"""Tests for the relay and the runner, driving the REAL job_monitor.py.

The original monitor runs against a config with no sources, so nothing is
fetched from the internet; its pending-notification, email-failure and dedup
code paths run unchanged against the local relay.

  JM_ORIGINAL_SRC  checkout of whtitefall/python-scripts at the pinned commit
                   (default: fetched into a temporary directory)
  JM_TEST_PYTHON   interpreter with `requests` installed (default: a new venv)

Run from this directory:  python3 -m unittest -v test_jm_runner
"""
from __future__ import annotations

import io
import json
import os
import secrets
import shutil
import smtplib
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

import jm_runner
from held_smtp_relay import HOLD_REPLY, HeldSmtpRelay

HERE = Path(__file__).resolve().parent
PIN = json.loads((HERE / "pinned_source.json").read_text())
_CACHE = Path(tempfile.mkdtemp(prefix="jm-test-cache-"))


def original_source() -> Path:
    if os.environ.get("JM_ORIGINAL_SRC"):
        return Path(os.environ["JM_ORIGINAL_SRC"])
    return jm_runner.ensure_source(_CACHE, PIN)


def test_python() -> Path:
    if os.environ.get("JM_TEST_PYTHON"):
        return Path(os.environ["JM_TEST_PYTHON"])
    src = original_source()
    return jm_runner.ensure_venv(_CACHE, src / "job-monitor" / "requirements.txt")[0]


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def job(uid: str, hours_old: float = 1.0, title: str = "Software Engineer") -> dict:
    when = datetime.now(timezone.utc) - timedelta(hours=hours_old)
    return {"unique_id": uid, "source": "Test", "company": "TestCo", "title": title,
            "location": "Toronto, ON, Canada", "url": f"https://example.com/jobs/{uid}",
            "updated_at": when.replace(microsecond=0).isoformat()}


class RelayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.token = secrets.token_urlsafe(16)
        self.relay = HeldSmtpRelay(self.tmp, self.token).start()

    def tearDown(self):
        self.relay.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_smtp_ssl_client_is_held_and_message_captured(self):
        msg = EmailMessage()
        msg["From"] = "sender@example.com"
        msg["To"] = "rcpt@example.com"
        msg["Subject"] = "[Canada Job Alert] 1 new openings (2026-11-07 10:00:00)"
        body = "发现新的加拿大科技岗位：\n\n.leading dot line\n1. TestCo | Software Engineer\n   链接: https://example.com/x"
        msg.set_content(body)
        # Same client calls as job_monitor.send_email(), default SSL context included.
        with self.assertRaises(smtplib.SMTPDataError) as ctx:
            with smtplib.SMTP_SSL("127.0.0.1", self.relay.port, timeout=30) as server:
                server.login("sender@example.com", self.token)
                server.send_message(msg)
        self.assertEqual(ctx.exception.smtp_code, 451)
        self.assertIn(b"Held by local relay", ctx.exception.smtp_error)
        report = self.relay.stop()
        self.assertEqual(len(report.messages), 1)
        captured = report.messages[0]
        self.assertEqual(captured.rcpt_to, ["rcpt@example.com"])
        parsed = jm_runner.parse_captured(captured.data)
        self.assertEqual(str(parsed["Subject"]), msg["Subject"])
        self.assertEqual(parsed.get_body(("plain",)).get_content().rstrip("\n"), body)
        self.assertEqual(report.errors, [])

    def test_wrong_password_is_rejected(self):
        with self.assertRaises(smtplib.SMTPAuthenticationError):
            with smtplib.SMTP_SSL("127.0.0.1", self.relay.port, timeout=30) as server:
                server.login("x", "wrong")
        # smtplib.login() tries every advertised mechanism (PLAIN, then LOGIN) before giving up.
        self.assertGreaterEqual(self.relay.stop().auth_failures, 1)
        self.assertEqual(HOLD_REPLY[:3], b"451")


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.python = test_python()
        cls.original = original_source()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="jm-runner-test-"))
        # Source: the real job_monitor.py; the config keeps everything but fetches nothing.
        self.src = self.tmp / "src"
        (self.src / "job-monitor").mkdir(parents=True)
        for name in ("job_monitor.py", "requirements.txt"):
            shutil.copy(self.original / "job-monitor" / name, self.src / "job-monitor" / name)
        config = json.loads((self.original / "job-monitor" / "companies.json").read_text())
        config["sources"] = {}
        (self.src / "job-monitor" / "companies.json").write_text(json.dumps(config, indent=2))
        # A bare "origin" and a clone that plays the role of the state-branch checkout.
        self.origin = self.tmp / "origin.git"
        git(self.tmp, "init", "--quiet", "--bare", str(self.origin))
        self.checkout = self.clone("checkout", initial=True)
        self.workdir = self.tmp / "work"
        self.recipient = config["recipient_email"]

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def clone(self, name: str, initial: bool = False) -> Path:
        path = self.tmp / name
        if initial:
            path.mkdir()
            git(path, "init", "--quiet", "-b", jm_runner.DEFAULT_BRANCH)
            git(path, "remote", "add", "origin", str(self.origin))
            (path / "runner").mkdir()
            pin = {"repository": str(self.tmp / "no-such-upstream"), "commit": "test",
                   "files": {f"job-monitor/{n}": jm_runner.blob_sha((self.src / "job-monitor" / n).read_bytes())
                             for n in ("job_monitor.py", "companies.json", "requirements.txt")}}
            (path / "runner" / "pinned_source.json").write_text(json.dumps(pin))
            (path / "state").mkdir()
            (path / "state" / ".keep").write_text("")
            git(path, "add", "-A")
            git(path, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "--quiet", "-m", "init")
            git(path, "push", "--quiet", "origin", f"HEAD:refs/heads/{jm_runner.DEFAULT_BRANCH}")
        else:
            git(self.tmp, "clone", "--quiet", "--branch", jm_runner.DEFAULT_BRANCH, str(self.origin), str(path))
        git(path, "config", "user.name", "t")
        git(path, "config", "user.email", "t@example.com")
        return path

    def runner(self, *args: str, checkout: Path | None = None, push: bool = True, workdir: Path | None = None):
        argv = ["--workdir", str(workdir or self.workdir), "--checkout", str(checkout or self.checkout)]
        if not push:
            argv.append("--no-push")
        argv += list(args)
        if args and args[0] == "cycle":
            argv += ["--source-dir", str(self.src), "--python", str(self.python)]
        out = io.StringIO()
        with redirect_stdout(out):
            code = jm_runner.main(argv)
        return code, out.getvalue()

    def state(self, checkout: Path | None = None) -> dict:
        return json.loads(((checkout or self.checkout) / "state" / "job_monitor_state.json").read_text())

    def write_state(self, pending: list[dict], seen: list[str] | None = None) -> None:
        state = {"initialized": True, "seen_job_ids": seen or [], "pending_notifications": pending,
                 "ai_rejected_job_ids": [], "last_check_at": None}
        (self.checkout / "state" / "job_monitor_state.json").write_text(json.dumps(state))
        git(self.checkout, "add", "-A")
        git(self.checkout, "commit", "--quiet", "-m", "seed state")
        git(self.checkout, "push", "--quiet", "origin", f"HEAD:refs/heads/{jm_runner.DEFAULT_BRANCH}")

    def remote_head(self) -> str:
        return git(self.checkout, "ls-remote", "origin", f"refs/heads/{jm_runner.DEFAULT_BRANCH}").split()[0]

    # ------------------------------------------------------------- baseline

    def test_missing_state_needs_explicit_baseline_flag(self):
        head = self.remote_head()
        code, out = self.runner("cycle")
        self.assertEqual(code, jm_runner.EXIT_PREFLIGHT, out)
        self.assertEqual(self.remote_head(), head)
        code, out = self.runner("cycle", "--allow-new-baseline")
        self.assertEqual(code, jm_runner.EXIT_OK, out)
        state = self.state()
        self.assertTrue(state["initialized"])
        self.assertEqual(state["pending_notifications"], [])
        receipt = json.loads((self.checkout / "state" / "last_run.json").read_text())
        self.assertTrue(receipt["baseline_created"])
        self.assertIn("Initialized baseline", (self.checkout / "state" / "last_run.log").read_text())
        self.assertEqual(self.remote_head(), git(self.checkout, "rev-parse", "HEAD"))

    def test_unreadable_state_is_refused_not_rebuilt(self):
        (self.checkout / "state" / "job_monitor_state.json").write_text("{not json")
        code, out = self.runner("cycle", push=False)
        self.assertEqual(code, jm_runner.EXIT_PREFLIGHT, out)
        self.assertEqual((self.checkout / "state" / "job_monitor_state.json").read_text(), "{not json")

    def test_modified_monitor_is_refused(self):
        self.write_state([])
        with (self.src / "job-monitor" / "job_monitor.py").open("a") as handle:
            handle.write("\n# changed\n")
        code, out = self.runner("cycle")
        self.assertEqual(code, jm_runner.EXIT_PREFLIGHT, out)
        self.assertIn("does not match pinned blob", out)

    # ---------------------------------------------------- held email paths

    def test_held_email_then_sent_marks_seen_and_dedups(self):
        self.write_state([job("t:1")], seen=["old:1"])
        code, out = self.runner("cycle")
        self.assertEqual(code, jm_runner.EXIT_SEND_EMAIL, out)
        outbox = json.loads((self.workdir / "outbox" / "email.json").read_text())
        self.assertEqual(outbox["to"], [self.recipient])
        self.assertTrue(outbox["subject"].startswith("[Canada Job Alert] 1 new openings"))
        body = (self.workdir / "outbox" / "body.txt").read_text()
        self.assertIn("https://example.com/jobs/t:1", body)
        self.assertTrue(body.startswith("发现新的加拿大科技岗位："), body[:40])
        self.assertNotIn("\r", body)
        self.assertEqual([j["unique_id"] for j in self.state()["pending_notifications"]], ["t:1"])
        self.assertTrue((self.checkout / "state" / "lease.json").exists())
        self.assertEqual(self.remote_head(), git(self.checkout, "rev-parse", "HEAD"))

        # A second cycle while the email is held does nothing.
        head = self.remote_head()
        code, out = self.runner("cycle", workdir=self.tmp / "other-work")
        self.assertEqual(code, jm_runner.EXIT_OK)
        self.assertIn("LEASE ACTIVE", out)
        self.assertEqual(self.remote_head(), head)

        code, out = self.runner("finalize", "--sent", "gmail-123")
        self.assertEqual(code, jm_runner.EXIT_OK, out)
        state = self.state()
        self.assertEqual(state["pending_notifications"], [])
        self.assertEqual(state["seen_job_ids"], ["old:1", "t:1"])
        self.assertFalse((self.checkout / "state" / "lease.json").exists())
        receipt = json.loads((self.checkout / "state" / "last_run.json").read_text())
        self.assertEqual(receipt["email"]["status"], "sent")
        self.assertEqual(receipt["email"]["gmail_message_id"], "gmail-123")

        code, out = self.runner("finalize", "--sent", "again")
        self.assertEqual(code, jm_runner.EXIT_PREFLIGHT, out)

        code, out = self.runner("cycle")
        self.assertEqual(code, jm_runner.EXIT_OK, out)
        self.assertIn("No new jobs this cycle", (self.checkout / "state" / "last_run.log").read_text())
        self.assertFalse((self.workdir / "outbox").exists())

    def test_failed_send_keeps_pending_and_next_cycle_retries(self):
        self.write_state([job("t:2")])
        self.assertEqual(self.runner("cycle")[0], jm_runner.EXIT_SEND_EMAIL)
        code, out = self.runner("finalize", "--failed", "Gmail connector error")
        self.assertEqual(code, jm_runner.EXIT_OK, out)
        self.assertEqual([j["unique_id"] for j in self.state()["pending_notifications"]], ["t:2"])
        self.assertFalse((self.checkout / "state" / "lease.json").exists())
        code, out = self.runner("cycle")
        self.assertEqual(code, jm_runner.EXIT_SEND_EMAIL, out)
        self.assertIn("t:2", (self.workdir / "outbox" / "body.txt").read_text())

    def test_expired_lease_does_not_block_and_jobs_are_resent(self):
        self.write_state([job("t:3")])
        self.assertEqual(self.runner("cycle")[0], jm_runner.EXIT_SEND_EMAIL)
        lease_path = self.checkout / "state" / "lease.json"
        lease = json.loads(lease_path.read_text())
        lease["expires_at"] = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        lease_path.write_text(json.dumps(lease))
        git(self.checkout, "commit", "--quiet", "-am", "expire lease")
        git(self.checkout, "push", "--quiet", "origin", f"HEAD:refs/heads/{jm_runner.DEFAULT_BRANCH}")
        code, out = self.runner("cycle")
        self.assertEqual(code, jm_runner.EXIT_SEND_EMAIL, out)
        receipt = json.loads((self.checkout / "state" / "last_run.json").read_text())
        self.assertEqual(receipt["stale_lease_run_id"], lease["run_id"])

    def test_stale_pending_job_is_dropped_by_original_age_filter(self):
        self.write_state([job("t:old", hours_old=24 * 5)])
        code, out = self.runner("cycle")
        self.assertEqual(code, jm_runner.EXIT_OK, out)
        state = self.state()
        self.assertEqual(state["pending_notifications"], [])
        self.assertIn("t:old", state["seen_job_ids"])

    # ------------------------------------------------- concurrent updates

    def test_finalize_refuses_when_branch_moved(self):
        self.write_state([job("t:4")])
        self.assertEqual(self.runner("cycle")[0], jm_runner.EXIT_SEND_EMAIL)
        other = self.clone("other")
        (other / "state" / "note.txt").write_text("someone else")
        git(other, "add", "-A")
        git(other, "commit", "--quiet", "-m", "other run")
        git(other, "push", "--quiet", "origin", f"HEAD:refs/heads/{jm_runner.DEFAULT_BRANCH}")
        code, out = self.runner("finalize", "--sent", "gmail-x")
        self.assertEqual(code, jm_runner.EXIT_BRANCH_MOVED, out)
        self.assertEqual([j["unique_id"] for j in self.state()["pending_notifications"]], ["t:4"])

    def test_cycle_does_not_offer_email_when_push_is_rejected(self):
        self.write_state([job("t:5")])
        other = self.clone("other")
        # Simulate another run finishing while this one is running: patch the push target.
        original_push = jm_runner.push

        def racing_push(layout, branch):
            (other / "state" / "note.txt").write_text("race")
            git(other, "add", "-A")
            git(other, "commit", "--quiet", "-m", "other run")
            git(other, "push", "--quiet", "origin", f"HEAD:refs/heads/{branch}")
            return original_push(layout, branch)

        jm_runner.push = racing_push
        try:
            code, out = self.runner("cycle")
        finally:
            jm_runner.push = original_push
        self.assertEqual(code, jm_runner.EXIT_BRANCH_MOVED, out)
        self.assertFalse((self.workdir / "outbox").exists())
        code, out = self.runner("finalize", "--sent", "gmail-y")
        self.assertNotEqual(code, jm_runner.EXIT_OK, out)


if __name__ == "__main__":
    unittest.main()
