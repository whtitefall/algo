# Canada Job Monitor：Claude 云端独立运行副本

这个分支（`canada-job-monitor`，与 algo 仓库的其他内容无关）是招聘监控的**第二套、独立**系统：每小时在 Claude Code 云端执行一次原始的
[`whtitefall/python-scripts`](https://github.com/whtitefall/python-scripts) 里的 `job-monitor/job_monitor.py`。

GitHub Actions 上的原系统保持原样，本分支不修改、不触发、不读取它的仓库设置、Secrets 或 Actions 缓存。两套系统各自维护状态、各自发信。

## 每小时发生什么

1. Claude 定时任务（America/Toronto，每小时一次）启动一个全新的云会话，会话按 [`SCHEDULED_TASK_PROMPT.md`](SCHEDULED_TASK_PROMPT.md) 执行。
2. 会话克隆本分支，运行 `python3 runner/jm_runner.py cycle`。运行器做这些事：
   - 浅克隆 python-scripts 的固定提交 `652aa62`，核对 `job_monitor.py`、`companies.json`、`requirements.txt` 的 Git blob 哈希（见 `runner/pinned_source.json`）。上游以后有改动也不会自动跟进，需要人工审阅后更新固定提交。
   - 建 venv，安装 `requirements.txt`。
   - 生成 `companies.json` 的**运行时副本**，只改三项：`ai_filter.enabled=false`、`smtp_host=127.0.0.1`、`smtp_port=<本机中继端口>`。原文件不动。
   - 用原命令行执行原脚本：`python job_monitor.py --config <运行时副本> --state <状态副本> --once`。不加 `--send-initial-snapshot`。
3. 原脚本有新职位要通知时，会照常用 `smtplib.SMTP_SSL` 登录并发信，只是对端换成了本机中继（`runner/held_smtp_relay.py`）。中继收下完整邮件，回复临时失败 `451`。原脚本因此和平时“Gmail 连不上”时的处理完全一样：职位保留在 `pending_notifications`，保存状态，退出码 1。
4. 运行器把状态提交并推送到本分支，同时写一个租约 `state/lease.json`（45 分钟），然后把截下来的邮件（收件人、主题、正文都是原脚本生成的）交给会话。
5. 会话用 **Gmail 连接器**（你的 Gmail 账号）发出这封邮件，再运行 `finalize`：
   - `--sent <Gmail 消息 ID>`：执行和原脚本“发送成功”分支完全相同的状态变化：pending 里的职位 ID 并入 `seen_job_ids`，`pending_notifications` 清空。
   - `--failed <原因>`：什么也不改，职位继续留在 pending，下一小时由原脚本重发（原有的待重试行为）。

## 与原 GitHub 系统的差别（已获你同意）

| 项目 | GitHub 原系统 | 本副本 |
|---|---|---|
| 代码 | `job_monitor.py` | 同一文件，字节一致，按哈希核对 |
| 发信 | Gmail SMTP `smtp.gmail.com:465` | Claude 云只放行 443 端口的 HTTPS，SMTP 不可达。改为：本机中继截获，再由 Gmail 连接器发出。邮件内容不变 |
| AI 过滤 | 已开启但未配置，实际回退为硬规则 | 关闭，只用硬规则 |
| 初始状态 | GitHub Actions 缓存里的生产状态 | 独立的新基线（首次运行把当时可见的职位记为已见，不发信） |
| 调度 | cron `2-59/5 * * * *` | 每小时一次，America/Toronto |
| 邮件主题里的时间 | 运行器所在时区（UTC） | `TZ=America/Toronto` |
| 状态存储 | Actions 缓存 | 本分支 `state/` 目录，每次运行一个提交 |

两套系统同时运行，同一个新职位通常会收到两封通知（GitHub 一封、本副本一封）。

## 文件

- `runner/jm_runner.py`：运行器，子命令 `cycle`、`finalize`、`status`
- `runner/held_smtp_relay.py`：本机 SMTPS 中继（只监听 127.0.0.1，每次运行随机端口、随机口令、临时自签证书）
- `runner/pinned_source.json`：固定的上游提交和文件哈希
- `runner/test_jm_runner.py`：测试，驱动真实的 `job_monitor.py`（不联网抓取）覆盖暂存、发出、失败重试、去重、过期租约、并发推送冲突等情况
- `state/job_monitor_state.json`：原脚本自己的状态文件，由原脚本写入，运行器只做字节复制；`finalize --sent` 按原脚本相同的格式写回
- `state/last_run.json`：最近一次运行的回执（结果、耗时、数据源告警、计数、邮件状态）
- `state/runs.jsonl`：运行历史（保留最近 3000 条）
- `state/last_run.log`：最近一次原脚本的完整日志
- `state/lease.json`：只在邮件等待 Gmail 发送时存在

## 退出码

`cycle`：0 完成；10 有邮件待发，发完要 `finalize`；1 原脚本失败（回执已提交）；2 启动检查拒绝（什么都没改）；3 分支在运行期间被别的运行更新了（这时不要发信）。

## 常用操作

查看状态（任意 Claude 会话或本地）：

```bash
git clone --single-branch --branch canada-job-monitor https://github.com/whtitefall/algo.git /tmp/jm-checkout
```

```bash
python3 /tmp/jm-checkout/runner/jm_runner.py status
```

- **暂停或恢复**：在 [claude.ai/code/routines](https://claude.ai/code/routines) 找到定时任务 “Canada job monitor (hourly)”，关闭或打开它。
- **手动跑一次**：在同一页面点 **Run now**。租约和推送冲突检查可以防止重复发信。
- **跑测试**：

```bash
cd /tmp/jm-checkout/runner && python3 -m unittest -v test_jm_runner
```

- **跟进上游新提交**：先审阅 `652aa62..新提交` 中 `job-monitor/` 的差异，再更新 `runner/pinned_source.json` 的 `commit` 和三个 blob 哈希。

## 安全边界与已知限制

- 不存放任何密码或 App Password。中继口令每次运行随机生成，只在本机使用。
- 本分支所在的 algo 仓库是**公开**的。`state/` 里是公开职位的 ID、标题、链接和运行日志，不含密钥；收件邮箱本来就写在公开的 `companies.json` 里。
- 每次运行都是一个完整的 Claude 云会话，计入你的 Claude 套餐用量（每天约 24 次）。
- 邮件正文由会话里的 Claude 按文件原样传给 Gmail 连接器，而不是程序直接投递。
- Gmail 连接器授权失效时发送会失败；职位会留在 pending，等授权恢复后重发。
- 某个数据源在建基线时抓取失败（比如 Microsoft 429），之后恢复时，它最近 48 小时内的职位会被当作新职位通知一次。这是原脚本本来的行为。
