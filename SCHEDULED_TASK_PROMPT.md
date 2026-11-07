Hourly run of the Canada job monitor: the second, independent copy that runs on Claude cloud. The GitHub Actions monitor in whtitefall/python-scripts is a separate system: never modify, trigger or touch that repository, its workflows or its settings.

Do exactly these steps and nothing else. Do not edit any code, do not open pull requests, do not push anything yourself, and do not touch any branch except through the runner below.

1. Fresh checkout of the state branch:
   rm -rf /tmp/jm-checkout /tmp/jm-work && git clone --quiet --single-branch --branch canada-job-monitor https://github.com/whtitefall/algo.git /tmp/jm-checkout

2. Run one cycle of the original job_monitor.py with a Bash timeout of 600000 ms (it normally takes 3 to 6 minutes; if it is moved to the background, wait for it to finish):
   python3 /tmp/jm-checkout/runner/jm_runner.py cycle
   The runner itself commits and pushes the updated state to branch canada-job-monitor of whtitefall/algo. That push is authorized; no other push is.

3. Act on the cycle's exit code:
   - 0: finished. Nothing to send (or another run holds the lease).
   - 10: job_monitor.py produced an email that is held for delivery. Read /tmp/jm-work/outbox/email.json and the body file it names. Send exactly ONE email with the Gmail connector's send_message tool: to = the "to" list, subject = the "subject" value exactly, body = the exact contents of the body file as plain text, unchanged, nothing added or removed. Then run one of:
       python3 /tmp/jm-checkout/runner/jm_runner.py finalize --sent <the message id Gmail returned>
       python3 /tmp/jm-checkout/runner/jm_runner.py finalize --failed "<short error text>"   (only if the send failed)
     Never send the email more than once, and never send any email unless the cycle exit code was 10.
   - 3: the state branch moved during the run. Send nothing.
   - 1 or 2: send nothing; include the printed error in your report.

4. End with a short report: the cycle exit code, the RUN line the runner printed, whether an email was sent (with the Gmail message id), and the finalize result.
