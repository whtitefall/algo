Hourly run of the Canada job monitor: the second, independent copy that runs on Claude cloud. The GitHub Actions monitor in whtitefall/python-scripts is a separate system: never modify, trigger or touch that repository, its workflows or its settings.

Do exactly these steps and nothing else. Do not edit any code, do not open pull requests, do not push anything yourself, and do not touch any branch except through the runner below.

1. Fresh checkout of the state branch:
   rm -rf /tmp/jm-checkout /tmp/jm-work && git clone --quiet --single-branch --branch canada-job-monitor https://github.com/whtitefall/algo.git /tmp/jm-checkout

2. Run one cycle of the original job_monitor.py with a Bash timeout of 600000 ms (it normally takes 3 to 6 minutes; if it is moved to the background, wait for it to finish):
   python3 /tmp/jm-checkout/runner/jm_runner.py cycle
   The runner itself commits and pushes the updated state to branch canada-job-monitor of whtitefall/algo. That push is authorized; no other push is.

3. Act on the cycle's exit code:
   - 0: finished. Nothing to send (or another run holds the lease). No push notification.
   - 10: job_monitor.py produced an email that is held for delivery. Read /tmp/jm-work/outbox/email.json and the body file it names. Send exactly ONE email with the Gmail connector's send_message tool: to = the "to" list, subject = the "subject" value exactly, body = the exact contents of the body file as plain text, unchanged, nothing added or removed. Then run one of:
       python3 /tmp/jm-checkout/runner/jm_runner.py finalize --sent <the message id Gmail returned>
       python3 /tmp/jm-checkout/runner/jm_runner.py finalize --failed "<short error text>"   (only if the send failed)
     If no Gmail send_message tool exists in this session, do not look for another way to send: run finalize --failed "Gmail connector not attached to the scheduled task" and say so in the report.
     Never send the email more than once, and never send any email unless the cycle exit code was 10.
     Then send ONE push notification with the PushNotification tool. After a successful send, its message is exactly the contents of the push file named in email.json. If the send failed, its message is "Canada Job Alert 邮件发送失败，职位已保留，下一小时重试：" followed by a short error, under 200 characters in total.
   - 3: the git push failed (another run moved the branch, or this session has no push access to whtitefall/algo). Send no email; quote the git error in the report; send ONE push notification: "Canada Job Monitor：状态保存失败（git push 被拒，退出码 3），请打开本次运行查看".
   - 1 or 2: send no email; include the printed error in your report; send ONE push notification: "Canada Job Monitor：运行出错（退出码 <code>），请打开本次运行查看".

4. End with a short report: the cycle exit code, the RUN line the runner printed, whether an email was sent (with the Gmail message id), the finalize result, and the push notification you sent (if any).

Send no push notifications other than the ones above. Expected, not problems, and never a reason to notify: the WARNING "Monitoring delayed: about 60 minutes since the previous check (target 5.0 minutes)" (job_monitor.py's own 5-minute target; this copy runs hourly), and occasional HTTP 429/403/404 from individual job sites.
