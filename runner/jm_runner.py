#!/usr/bin/env python3
"""Run the unchanged job_monitor.py once per scheduled Claude cloud session.

  cycle     one fetch/notify cycle of the original monitor; commits the new
            state to the state branch and, if job_monitor.py tried to send an
            email, leaves that email "held" for the Gmail connector
  finalize  after the Gmail connector call: --sent GMAIL_MESSAGE_ID applies the
            state change job_monitor.py makes after a successful send;
            --failed REASON keeps the jobs pending (original retry behaviour)
  status    summary of the state branch

Exit codes: 0 done, 10 a held email must be sent and finalized, 1 the monitor
failed (receipt committed), 2 preflight refused (nothing changed), 3 the state
branch moved or a push was rejected (do NOT send the held email).

See ../README.md for the design. Standard library only.
"""
from __future__ import annotations

import argparse
import email
import email.policy
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from held_smtp_relay import HeldSmtpRelay, RelayReport

RUNNER_DIR = Path(__file__).resolve().parent
DEFAULT_BRANCH = "canada-job-monitor"
DEFAULT_WORKDIR = Path(os.environ.get("JM_WORKDIR", "/tmp/jm-work"))
LEASE_MINUTES = 45
HISTORY_KEEP = 3000
MONITOR_TIMEOUT_SECONDS = 1500
SUBJECT_RE = re.compile(r"^\[Canada Job Alert\] (\d+) new openings")
JOB_FIELDS = frozenset({"unique_id", "source", "company", "title", "location", "url", "updated_at"})

EXIT_OK, EXIT_MONITOR_FAILED, EXIT_PREFLIGHT, EXIT_BRANCH_MOVED, EXIT_SEND_EMAIL = 0, 1, 2, 3, 10


class PreflightError(Exception):
    pass


class Layout:
    """Paths inside the checkout of the state branch."""

    def __init__(self, checkout: Path) -> None:
        self.checkout = checkout.resolve()
        self.state_dir = self.checkout / "state"
        self.state = self.state_dir / "job_monitor_state.json"
        self.lease = self.state_dir / "lease.json"
        self.last_run = self.state_dir / "last_run.json"
        self.history = self.state_dir / "runs.jsonl"
        self.log = self.state_dir / "last_run.log"
        self.pin = self.checkout / "runner" / "pinned_source.json"


# ---------------------------------------------------------------- helpers

def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(value: datetime) -> str:
    return value.isoformat()


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run(cmd, *, cwd=None, env=None, check=True, timeout=None) -> subprocess.CompletedProcess:
    proc = subprocess.run([str(c) for c in cmd], cwd=cwd, env=env, capture_output=True,
                          encoding="utf-8", errors="replace", timeout=timeout)
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(map(str, cmd))}\n"
                           f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    return proc


def git(layout_or_dir, *args, check=True) -> subprocess.CompletedProcess:
    cwd = layout_or_dir.checkout if isinstance(layout_or_dir, Layout) else layout_or_dir
    return run(["git", *args], cwd=cwd, check=check)


def git_out(layout_or_dir, *args) -> str:
    return git(layout_or_dir, *args).stdout.strip()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_state_like_original(path: Path, state: dict) -> None:
    # Same serialisation as job_monitor.save_state(): json.dump(state, f, ensure_ascii=False, indent=2)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
    tmp.replace(path)


def validate_state(state) -> None:
    if not isinstance(state, dict):
        raise PreflightError("state is not a JSON object")
    if state.get("initialized") is not True:
        raise PreflightError("state is not an initialized job_monitor state")
    for key in ("seen_job_ids", "pending_notifications"):
        if not isinstance(state.get(key), list):
            raise PreflightError(f"state field {key} is missing or not a list")
    if "ai_rejected_job_ids" in state and not isinstance(state["ai_rejected_job_ids"], list):
        raise PreflightError("state field ai_rejected_job_ids is not a list")


def load_valid_state(path: Path) -> dict:
    try:
        state = read_json(path)
    except (OSError, ValueError) as exc:
        # job_monitor.py would silently rebuild an unreadable state; refuse instead.
        raise PreflightError(f"cannot read {path.name}: {exc}") from None
    validate_state(state)
    return state


def counts(state) -> dict | None:
    if not isinstance(state, dict):
        return None
    return {
        "seen": len(state.get("seen_job_ids") or []),
        "pending": len(state.get("pending_notifications") or []),
        "ai_rejected": len(state.get("ai_rejected_job_ids") or []),
    }


def pending_ids(state: dict) -> list[str]:
    # job_monitor.index_pending_jobs() keeps only entries that build a JobPosting.
    return sorted({item["unique_id"] for item in state.get("pending_notifications") or []
                   if isinstance(item, dict) and set(item) == JOB_FIELDS})


def append_history(layout: Layout, entry: dict) -> None:
    lines = layout.history.read_text(encoding="utf-8").splitlines() if layout.history.exists() else []
    lines.append(json.dumps(entry, ensure_ascii=False, sort_keys=True))
    layout.history.write_text("\n".join(lines[-HISTORY_KEEP:]) + "\n", encoding="utf-8")


def commit(layout: Layout, message: str) -> bool:
    """Commit only state/ (anything else staged in the checkout is left alone)."""
    git(layout, "add", "--all", "state")
    if git(layout, "diff", "--cached", "--quiet", "--", "state", check=False).returncode == 0:
        return False
    identity = []
    if not git(layout, "config", "user.email", check=False).stdout.strip():
        identity = ["-c", "user.name=canada-job-monitor",
                    "-c", "user.email=canada-job-monitor@users.noreply.github.com"]
    git(layout, *identity, "commit", "--quiet", "-m", message, "--", "state")
    return True


def fetch_remote_head(layout: Layout, branch: str) -> str:
    git(layout, "fetch", "--quiet", "origin", f"+refs/heads/{branch}:refs/remotes/origin/{branch}")
    return git_out(layout, "rev-parse", f"refs/remotes/origin/{branch}")


def sync_with_remote(layout: Layout, branch: str) -> None:
    remote = fetch_remote_head(layout, branch)
    local = git_out(layout, "rev-parse", "HEAD")
    if local == remote:
        return
    if git(layout, "status", "--porcelain", check=False).stdout.strip():
        raise PreflightError("the state checkout has uncommitted changes; use a fresh clone")
    if git(layout, "merge-base", "--is-ancestor", local, remote, check=False).returncode != 0:
        raise PreflightError("the state checkout has commits that are not on origin; use a fresh clone")
    git(layout, "reset", "--quiet", "--hard", remote)


def push(layout: Layout, branch: str) -> bool:
    proc = git(layout, "push", "--quiet", "origin", f"HEAD:refs/heads/{branch}", check=False)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
    return proc.returncode == 0


# ------------------------------------------------- source, venv and config

def ensure_source(workdir: Path, pin: dict) -> Path:
    """Shallow checkout of the pinned commit; every pinned blob must match."""
    src = workdir / "src"
    if (src / ".git").exists() and git(src, "rev-parse", "HEAD", check=False).stdout.strip() != pin["commit"]:
        shutil.rmtree(src)
    if not (src / ".git").exists():
        shutil.rmtree(src, ignore_errors=True)
        src.mkdir(parents=True)
        git(src, "init", "--quiet")
        git(src, "remote", "add", "origin", pin["repository"])
        git(src, "fetch", "--quiet", "--depth", "1", "origin", pin["commit"])
        git(src, "checkout", "--quiet", "--detach", "FETCH_HEAD")
    verify_pinned_files(src, pin)
    return src


def verify_pinned_files(src: Path, pin: dict) -> None:
    for rel, expected in pin["files"].items():
        on_disk = blob_sha((src / rel).read_bytes())
        if on_disk != expected:
            raise PreflightError(f"{rel} does not match pinned blob {expected} (found {on_disk})")


def upstream_head(pin: dict) -> str | None:
    proc = run(["git", "ls-remote", pin["repository"], "refs/heads/master"], check=False, timeout=60)
    return proc.stdout.split()[0] if proc.returncode == 0 and proc.stdout.strip() else None


def ensure_venv(workdir: Path, requirements: Path) -> tuple[Path, dict]:
    venv = workdir / "venv"
    python = venv / "bin" / "python"
    if not python.exists():
        run([sys.executable, "-m", "venv", venv])
    # cwd = job-monitor/: the repository root has an email.py that shadows the stdlib.
    run([python, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "-r", requirements.name],
        cwd=requirements.parent, timeout=900)
    return python, interpreter_versions(python, requirements.parent)


def interpreter_versions(python: Path, cwd: Path) -> dict:
    out = run([python, "-c", "import sys, requests; print(sys.version.split()[0]); print(requests.__version__)"],
              cwd=cwd).stdout.split()
    return {"python": out[0], "requests": out[1]}


def build_runtime_config(original: dict, relay_port: int) -> tuple[dict, list[str]]:
    config = json.loads(json.dumps(original))
    ai = config.get("ai_filter")
    if not isinstance(ai, dict):
        ai = config["ai_filter"] = {}
    ai["enabled"] = False
    config["smtp_host"] = "127.0.0.1"
    config["smtp_port"] = relay_port
    overrides = ["ai_filter.enabled=false", "smtp_host=127.0.0.1", f"smtp_port={relay_port} (held relay)"]
    return config, overrides


def monitor_env(token: str, sender: str) -> dict:
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("AI_FILTER_", "PYTHON")) and k not in ("SMTP_USER", "SMTP_PASSWORD")}
    env.update({"SMTP_USER": sender, "SMTP_PASSWORD": token, "TZ": "America/Toronto",
                "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"})
    return env


# ------------------------------------------------------------ one monitor run

def run_original_monitor(*, src: Path, python: Path, base_config: dict, state_path: Path,
                         workdir: Path, sender: str, timeout: int) -> dict:
    """Run job-monitor/job_monitor.py --once with a runtime config pointing at the relay."""
    token = secrets.token_urlsafe(24)
    relay = HeldSmtpRelay(workdir / "relay", token).start()
    timed_out = False
    try:
        config, overrides = build_runtime_config(base_config, relay.port)
        config_path = workdir / "runtime-companies.json"
        write_json(config_path, config)
        command = [str(python), "job_monitor.py", "--config", str(config_path),
                   "--state", str(state_path), "--once"]
        try:
            proc = subprocess.run(command, cwd=src / "job-monitor", env=monitor_env(token, sender),
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  encoding="utf-8", errors="replace", timeout=timeout)
            exit_code, log = proc.returncode, proc.stdout
        except subprocess.TimeoutExpired as exc:
            timed_out, exit_code = True, None
            raw = exc.stdout or ""
            log = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
    finally:
        report = relay.stop()
    shown = command[:]
    shown[0] = "python"
    return {"exit_code": exit_code, "timed_out": timed_out, "log": log.replace(token, "[relay-token]"),
            "relay": report, "config": config, "overrides": overrides,
            "command": " ".join(shown)}


def parse_captured(data: bytes) -> email.message.EmailMessage:
    # SMTP carries CRLF line ends; job_monitor.py built the body with "\n".
    return email.message_from_bytes(data.replace(b"\r\n", b"\n"), policy=email.policy.default)


def inspect_held_message(report: RelayReport, state_after: dict | None, config: dict,
                         exit_code, log: str) -> tuple[dict, list[str]]:
    captured = report.messages[0]
    message = parse_captured(captured.data)
    subject = str(message.get("Subject", ""))
    to = [address.addr_spec for address in message["To"].addresses] if message["To"] else []
    part = message.get_body(preferencelist=("plain",))
    body = part.get_content() if part is not None else ""
    match = SUBJECT_RE.match(subject)
    job_count = int(match.group(1)) if match else None
    recipient = str(config.get("recipient_email", "")).strip().lower()
    ids = pending_ids(state_after) if state_after else []
    problems = []
    if exit_code in (0, None):
        problems.append("job_monitor.py did not report the held email as a failed send")
    if "Held by local relay" not in log:
        problems.append("job_monitor.py log does not show the relay hold")
    if state_after is None:
        problems.append("no valid state was saved")
    elif job_count is None:
        problems.append(f"unexpected subject: {subject!r}")
    elif job_count != len(ids) or job_count != len(state_after.get("pending_notifications") or []):
        problems.append(f"subject lists {job_count} jobs but the state keeps {len(ids)} pending")
    if [r.lower() for r in captured.rcpt_to] != [recipient] or [t.lower() for t in to] != [recipient]:
        problems.append(f"unexpected recipients {captured.rcpt_to} / {to}")
    held = {
        "to": to, "subject": subject, "body": body, "job_count": job_count,
        "body_sha256": sha256_text(body), "pending_ids_sha256": sha256_text("\n".join(ids)),
        "message_sha256": hashlib.sha256(captured.data).hexdigest(),
    }
    return held, problems


# ------------------------------------------------------------------- commands

def cmd_cycle(args) -> int:
    layout = Layout(args.checkout)
    workdir = args.workdir
    workdir.mkdir(parents=True, exist_ok=True)
    for stale in ("run.json", "outbox"):
        target = workdir / stale
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    started, clock = utc_now(), time.monotonic()
    run_id = started.strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(2)
    try:
        if args.push:
            sync_with_remote(layout, args.branch)
        base_commit = git_out(layout, "rev-parse", "HEAD")
        lease = read_json(layout.lease) if layout.lease.exists() else None
        stale_lease = None
        if lease is not None:
            if utc_now() < datetime.fromisoformat(lease["expires_at"]):
                print(f"LEASE ACTIVE: run {lease.get('run_id')} holds an email awaiting Gmail delivery "
                      f"until {lease['expires_at']}. Nothing was done.")
                return EXIT_OK
            stale_lease = lease
        layout.state_dir.mkdir(exist_ok=True)
        if layout.state.exists():
            state_before = load_valid_state(layout.state)
        elif args.allow_new_baseline:
            state_before = None
        else:
            raise PreflightError("state/job_monitor_state.json is missing; a new baseline needs "
                                 "--allow-new-baseline (explicit user authorisation)")
        pin = read_json(layout.pin)
        src = args.source_dir.resolve() if args.source_dir else ensure_source(workdir, pin)
        verify_pinned_files(src, pin)
        if args.python:
            python = args.python
            versions = interpreter_versions(python, src / "job-monitor")
        else:
            python, versions = ensure_venv(workdir, src / "job-monitor" / "requirements.txt")
        base_config = read_json(src / "job-monitor" / "companies.json")
    except (PreflightError, RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"PREFLIGHT REFUSED: {exc}")
        return EXIT_PREFLIGHT

    work_state = workdir / "state.json"
    work_state.unlink(missing_ok=True)
    if state_before is not None:
        shutil.copyfile(layout.state, work_state)
    sender = args.sender or str(base_config.get("recipient_email", "")).strip()
    result = run_original_monitor(src=src, python=python, base_config=base_config, state_path=work_state,
                                  workdir=workdir, sender=sender, timeout=args.timeout)
    report: RelayReport = result["relay"]
    state_after, state_error = None, None
    if work_state.exists():
        try:
            state_after = load_valid_state(work_state)
        except PreflightError as exc:
            state_error = str(exc)

    held, problems = None, []
    if result["timed_out"]:
        outcome = "timeout"
    elif len(report.messages) > 1:
        outcome, problems = "relay_inconsistent", [f"{len(report.messages)} messages captured"]
    elif len(report.messages) == 1:
        held, problems = inspect_held_message(report, state_after, result["config"],
                                              result["exit_code"], result["log"])
        outcome = "held_for_gmail" if not problems else "relay_inconsistent"
    elif result["exit_code"] == 0:
        outcome = "ok"
    else:
        outcome = "monitor_failed"

    log = result["log"]
    state_committed = state_after is not None and not result["timed_out"]
    if state_committed:
        shutil.copyfile(work_state, layout.state)  # bytes exactly as job_monitor.py saved them
    layout.log.write_text(log, encoding="utf-8")
    final_counts = counts(state_after) if state_committed else counts(state_before)
    receipt = {
        "run_id": run_id,
        "started_at": iso(started),
        "finished_at": iso(utc_now()),
        "duration_seconds": round(time.monotonic() - clock, 1),
        "outcome": outcome,
        "problems": problems,
        "monitor_exit_code": result["exit_code"],
        "command": result["command"],
        "baseline_created": state_before is None and state_committed,
        "state_committed": state_committed,
        "state_error": state_error,
        "base_commit": base_commit,
        "source": {"repository": pin["repository"], "commit": pin["commit"],
                   "upstream_master": upstream_head(pin) if args.push else None},
        "runtime": versions,
        "config_overrides": result["overrides"],
        "counts_before": counts(state_before),
        "counts_after": final_counts,
        "email": ({"status": "held", "job_count": held["job_count"], "subject": held["subject"],
                   "body_sha256": held["body_sha256"]} if outcome == "held_for_gmail" else {"status": "none"}),
        "relay": {"connections": report.connections, "auth_failures": report.auth_failures,
                  "errors": report.errors, "messages": len(report.messages)},
        "source_warnings": [line for line in log.splitlines() if "| WARNING |" in line or "| ERROR |" in line][-40:],
        "stale_lease_run_id": stale_lease.get("run_id") if stale_lease else None,
    }
    if outcome == "held_for_gmail":
        write_json(layout.lease, {
            "run_id": run_id, "created_at": iso(started),
            "expires_at": iso(started + timedelta(minutes=LEASE_MINUTES)),
            "job_count": held["job_count"], "subject": held["subject"],
            "body_sha256": held["body_sha256"], "pending_ids_sha256": held["pending_ids_sha256"],
        })
    else:
        layout.lease.unlink(missing_ok=True)  # an expired lease: its jobs are still pending in the state
    write_json(layout.last_run, receipt)
    append_history(layout, {k: receipt[k] for k in ("run_id", "started_at", "duration_seconds", "outcome",
                                                     "monitor_exit_code", "counts_after", "email")})
    c = final_counts or {}
    commit(layout, f"monitor: {outcome} run={run_id} seen={c.get('seen')} pending={c.get('pending')}")
    commit_sha = git_out(layout, "rev-parse", "HEAD")
    pushed = push(layout, args.branch) if args.push else None
    run_meta = {"run_id": run_id, "outcome": outcome, "commit": commit_sha, "branch": args.branch,
                "pushed": pushed, "push_enabled": args.push, "checkout": str(layout.checkout)}
    write_json(workdir / "run.json", run_meta)

    print(f"RUN {run_id}: outcome={outcome} monitor_exit={result['exit_code']} "
          f"duration={receipt['duration_seconds']}s counts={final_counts} commit={commit_sha[:12]} pushed={pushed}")
    for line in receipt["source_warnings"]:
        print("  " + line)
    for problem in problems:
        print("  PROBLEM: " + problem)
    if args.push and not pushed:
        print("BRANCH MOVED / PUSH REJECTED: another run updated the state branch. Do NOT send any email; "
              "the next scheduled run starts from the newer state.")
        return EXIT_BRANCH_MOVED
    if outcome == "held_for_gmail":
        outbox = workdir / "outbox"
        outbox.mkdir()
        (outbox / "body.txt").write_text(held["body"], encoding="utf-8")
        write_json(outbox / "email.json", {"run_id": run_id, "to": held["to"], "subject": held["subject"],
                                           "body_file": str(outbox / "body.txt"),
                                           "body_sha256": held["body_sha256"], "job_count": held["job_count"]})
        print("HELD EMAIL - send it with the Gmail connector, then run finalize:")
        print(f"  to: {', '.join(held['to'])}")
        print(f"  subject: {held['subject']}")
        print(f"  body: the exact contents of {outbox / 'body.txt'}")
        return EXIT_SEND_EMAIL
    return EXIT_OK if outcome == "ok" else EXIT_MONITOR_FAILED


def cmd_finalize(args) -> int:
    meta_path = args.workdir / "run.json"
    if not meta_path.exists():
        print("FINALIZE REFUSED: no run.json in the work directory")
        return EXIT_PREFLIGHT
    meta = read_json(meta_path)
    layout = Layout(Path(meta["checkout"]))
    if meta.get("outcome") != "held_for_gmail" or meta.get("finalized"):
        print(f"FINALIZE REFUSED: run {meta.get('run_id')} has outcome={meta.get('outcome')} "
              f"finalized={meta.get('finalized')}")
        return EXIT_PREFLIGHT
    if meta.get("push_enabled"):
        if not meta.get("pushed"):
            print("FINALIZE REFUSED: the held state was never pushed")
            return EXIT_BRANCH_MOVED
        remote = fetch_remote_head(layout, meta["branch"])
        local = git_out(layout, "rev-parse", "HEAD")
        if remote != meta["commit"] or local != meta["commit"]:
            print("FINALIZE REFUSED: the state branch moved since this cycle; the jobs stay pending and the "
                  "next cycle will send them again")
            return EXIT_BRANCH_MOVED
    lease = read_json(layout.lease) if layout.lease.exists() else None
    if not lease or lease.get("run_id") != meta["run_id"]:
        print("FINALIZE REFUSED: the lease does not belong to this run")
        return EXIT_PREFLIGHT
    try:
        state = load_valid_state(layout.state)
    except PreflightError as exc:
        print(f"FINALIZE REFUSED: {exc}")
        return EXIT_PREFLIGHT
    ids = pending_ids(state)
    if sha256_text("\n".join(ids)) != lease["pending_ids_sha256"]:
        print("FINALIZE REFUSED: pending jobs differ from the held email")
        return EXIT_PREFLIGHT
    now = utc_now()
    if args.sent:
        # Exactly what job_monitor.run_check_cycle does after send_email(...) returns True:
        #   seen_ids.update(job.unique_id for job in pending_jobs); pending_jobs = []
        seen = {str(x) for x in state.get("seen_job_ids") or []}
        seen.update(ids)
        state["seen_job_ids"] = sorted(seen)
        state["pending_notifications"] = []
        write_state_like_original(layout.state, state)
        email_result, event = {"status": "sent", "gmail_message_id": args.sent, "at": iso(now)}, "email_sent"
    else:
        # Same as send_email(...) returning False: the jobs stay pending and are retried next cycle.
        email_result, event = {"status": "send_failed", "reason": args.failed[:500], "at": iso(now)}, "email_send_failed"
    layout.lease.unlink()
    receipt = read_json(layout.last_run) if layout.last_run.exists() else {"run_id": meta["run_id"]}
    if receipt.get("run_id") == meta["run_id"]:
        receipt["email"] = {**receipt.get("email", {}), **email_result}
        receipt["counts_after_finalize"] = counts(state)
        write_json(layout.last_run, receipt)
    append_history(layout, {"run_id": meta["run_id"], "event": event, **email_result,
                            "counts_after": counts(state)})
    c = counts(state)
    commit(layout, f"monitor: {event} run={meta['run_id']} seen={c['seen']} pending={c['pending']}")
    meta["finalized"] = event
    if meta.get("push_enabled") and not push(layout, meta["branch"]):
        write_json(meta_path, meta)
        print("PUSH REJECTED after finalize: the state branch moved; the next cycle may send these jobs again")
        return EXIT_BRANCH_MOVED
    write_json(meta_path, meta)
    print(f"FINALIZED {meta['run_id']}: {event} counts={c}")
    return EXIT_OK


def cmd_status(args) -> int:
    layout = Layout(args.checkout)
    if args.push:
        try:
            sync_with_remote(layout, args.branch)
        except (PreflightError, RuntimeError) as exc:
            print(f"(could not refresh from origin: {exc})")
    summary = {
        "branch_head": git_out(layout, "rev-parse", "HEAD"),
        "state_counts": counts(read_json(layout.state)) if layout.state.exists() else None,
        "lease": read_json(layout.lease) if layout.lease.exists() else None,
        "last_run": read_json(layout.last_run) if layout.last_run.exists() else None,
        "recent": [json.loads(line) for line in
                   (layout.history.read_text(encoding="utf-8").splitlines()[-24:] if layout.history.exists() else [])],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return EXIT_OK


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workdir", type=Path, default=DEFAULT_WORKDIR)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--checkout", type=Path, default=RUNNER_DIR.parent,
                        help="checkout of the state branch (default: the one containing this runner)")
    parser.add_argument("--no-push", dest="push", action="store_false",
                        help="local test mode: no fetch or push")
    sub = parser.add_subparsers(dest="command", required=True)
    cycle = sub.add_parser("cycle")
    cycle.add_argument("--allow-new-baseline", action="store_true",
                       help="only with explicit user authorisation: create the state if it is missing")
    cycle.add_argument("--timeout", type=int, default=MONITOR_TIMEOUT_SECONDS)
    cycle.add_argument("--sender", help="SMTP_USER given to job_monitor.py (From header only)")
    cycle.add_argument("--source-dir", type=Path, help="tests: use this checkout instead of fetching")
    cycle.add_argument("--python", type=Path, help="tests: interpreter with requests installed")
    finalize = sub.add_parser("finalize")
    group = finalize.add_mutually_exclusive_group(required=True)
    group.add_argument("--sent", metavar="GMAIL_MESSAGE_ID")
    group.add_argument("--failed", metavar="REASON")
    sub.add_parser("status")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    return {"cycle": cmd_cycle, "finalize": cmd_finalize, "status": cmd_status}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
