"""Local SMTPS endpoint used in place of smtp.gmail.com:465.

job_monitor.py sends mail with smtplib.SMTP_SSL(host, port), login() and
send_message(). Claude cloud sessions cannot open SMTP connections to Gmail
(the egress proxy only carries HTTPS on port 443), so the runner points the
*runtime copy* of companies.json at this relay on 127.0.0.1.

The relay speaks real SMTP over TLS, records the complete message, and answers
DATA with a temporary failure (451). job_monitor.py then does exactly what it
does whenever Gmail is unreachable: it keeps the jobs in
``pending_notifications``, saves its state and exits non-zero. The runner hands
the captured message to the Gmail connector and, only after Gmail accepts it,
applies the same state change job_monitor.py applies after a successful send
(pending -> seen). If the Gmail send fails, nothing is changed and the original
retry-next-cycle behaviour applies.

Standard library only; certificates are made with the ``openssl`` CLI.
"""
from __future__ import annotations

import base64
import hmac
import re
import socket
import ssl
import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path

HOLD_REPLY = (
    b"451 4.3.0 Held by local relay for Gmail connector delivery; "
    b"jm_runner finalizes the state only after Gmail accepts it"
)
_ADDR = re.compile(rb"<([^>]*)>")


@dataclass
class CapturedMessage:
    mail_from: str
    rcpt_to: list[str]
    data: bytes  # RFC 5322 message as received (dot-unstuffed, CRLF line ends)
    auth_user: str


@dataclass
class RelayReport:
    messages: list[CapturedMessage] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    auth_failures: int = 0
    connections: int = 0


def _addr(arg: bytes) -> str:
    match = _ADDR.search(arg)
    return (match.group(1) if match else arg.split(b":", 1)[-1].strip()).decode("utf-8", "replace")


class HeldSmtpRelay:
    def __init__(self, workdir: Path, password: str) -> None:
        workdir.mkdir(parents=True, exist_ok=True)
        cert, key = workdir / "relay-cert.pem", workdir / "relay-key.pem"
        subprocess.run(
            ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", str(key),
             "-out", str(cert), "-days", "2", "-subj", "/CN=127.0.0.1"],
            check=True, capture_output=True,
        )
        self._ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self._ctx.load_cert_chain(str(cert), str(key))
        self._password = password.encode()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(8)
        self._sock.settimeout(0.5)
        self.port: int = self._sock.getsockname()[1]
        self.report = RelayReport()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._serve, name="held-smtp-relay", daemon=True)

    def start(self) -> "HeldSmtpRelay":
        self._thread.start()
        return self

    def stop(self) -> RelayReport:
        self._stop.set()
        self._thread.join(timeout=10)
        self._sock.close()
        return self.report

    def __enter__(self) -> "HeldSmtpRelay":
        return self.start()

    def __exit__(self, *exc) -> None:
        self.stop()

    def _serve(self) -> None:
        while not self._stop.is_set():
            try:
                conn, _ = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            self.report.connections += 1
            try:
                self._session(conn)
            except Exception as exc:  # recorded, never raised into the runner
                self.report.errors.append(f"{type(exc).__name__}: {exc}")
            finally:
                try:
                    conn.close()
                except OSError:
                    pass

    def _session(self, raw: socket.socket) -> None:
        raw.settimeout(120)
        with self._ctx.wrap_socket(raw, server_side=True) as tls, tls.makefile("rb") as reader:
            self._dialogue(tls, reader)

    def _dialogue(self, tls: ssl.SSLSocket, reader) -> None:
        def reply(*lines: bytes) -> None:
            tls.sendall(b"".join(line + b"\r\n" for line in lines))

        def read_line(limit: int = 65536) -> bytes:
            return reader.readline(limit)

        reply(b"220 127.0.0.1 ESMTP job-monitor held relay")
        authed = False
        auth_user = ""
        mail_from: str | None = None
        rcpts: list[str] = []
        while True:
            line = read_line()
            if not line:
                return
            cmd = line.rstrip(b"\r\n")
            verb, _, arg = cmd.partition(b" ")
            verb = verb.upper()
            arg = arg.strip()
            if verb == b"EHLO":
                reply(b"250-127.0.0.1", b"250-8BITMIME", b"250-SMTPUTF8",
                      b"250-ENHANCEDSTATUSCODES", b"250 AUTH PLAIN LOGIN")
            elif verb == b"HELO":
                reply(b"250 127.0.0.1")
            elif verb == b"AUTH":
                parts = arg.split()
                mech = parts[0].upper() if parts else b""
                try:
                    if mech == b"PLAIN":
                        if len(parts) > 1:
                            response = parts[1]
                        else:
                            reply(b"334 ")
                            response = read_line().strip()
                        _, user, password = base64.b64decode(response).split(b"\0", 2)
                    elif mech == b"LOGIN":
                        if len(parts) > 1:
                            user = base64.b64decode(parts[1])
                        else:
                            reply(b"334 VXNlcm5hbWU6")
                            user = base64.b64decode(read_line().strip())
                        reply(b"334 UGFzc3dvcmQ6")
                        password = base64.b64decode(read_line().strip())
                    else:
                        reply(b"504 5.5.4 Unsupported authentication mechanism")
                        continue
                except ValueError:  # includes binascii.Error
                    reply(b"501 5.5.2 Malformed AUTH response")
                    continue
                if hmac.compare_digest(password, self._password):
                    authed = True
                    auth_user = user.decode("utf-8", "replace")
                    reply(b"235 2.7.0 Accepted")
                else:
                    self.report.auth_failures += 1
                    reply(b"535 5.7.8 Authentication credentials invalid")
            elif verb == b"MAIL":
                if not authed:
                    reply(b"530 5.7.0 Authentication required")
                    continue
                mail_from, rcpts = _addr(arg), []
                reply(b"250 2.1.0 OK")
            elif verb == b"RCPT":
                if mail_from is None:
                    reply(b"503 5.5.1 MAIL first")
                    continue
                rcpts.append(_addr(arg))
                reply(b"250 2.1.5 OK")
            elif verb == b"DATA":
                if mail_from is None or not rcpts:
                    reply(b"503 5.5.1 RCPT first")
                    continue
                reply(b"354 Go ahead")
                chunks: list[bytes] = []
                while True:
                    data_line = read_line(1 << 20)
                    if not data_line:
                        return
                    if data_line in (b".\r\n", b".\n"):
                        break
                    if data_line.startswith(b"."):
                        data_line = data_line[1:]  # RFC 5321 section 4.5.2
                    chunks.append(data_line)
                self.report.messages.append(
                    CapturedMessage(mail_from, list(rcpts), b"".join(chunks), auth_user)
                )
                tls.sendall(HOLD_REPLY + b"\r\n")
                mail_from, rcpts = None, []
            elif verb == b"RSET":
                mail_from, rcpts = None, []
                reply(b"250 2.0.0 OK")
            elif verb == b"NOOP":
                reply(b"250 2.0.0 OK")
            elif verb == b"QUIT":
                reply(b"221 2.0.0 Bye")
                return
            else:
                reply(b"502 5.5.1 Command not implemented")
