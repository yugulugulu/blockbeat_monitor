---
description: 运行 BlockBeats 舆情监控命令，支持 init-db、ingest、report、send-telegram、run-daily
argument-hint: [init-db|ingest|report|send-telegram|run-daily] [可选参数]
allowed-tools: Bash(python3 scripts/blockbeats_monitor.py:*), Bash(test:*), Bash(ls:*), Bash(pwd:*), Bash(cp:*), Read, Glob
---

<!-- 本文件用于把仓库暴露为 Claude Code 的项目级 slash command，用户可通过 /blockbeats-monitor 直接调用。 -->

# BlockBeats Monitor Slash Command

你正在这个仓库内执行 BlockBeats 舆情监控命令。命令入口固定为：

```bash
python3 scripts/blockbeats_monitor.py --config config.toml ...
```

## 使用规则

- 如果用户没有提供参数，先告诉用户支持的命令，并给出最常见示例，不要盲目执行。
- 如果仓库根目录不存在 `config.toml`，先提示用户从 `config.example.toml` 复制并填写真实配置，再继续。
- 优先直接执行用户请求的子命令，不要改写成无关流程。
- 如果用户要求“生成并推送日报”，使用 `run-daily`。
- 如果用户要求“只抓数据”，使用 `ingest`。
- 如果用户要求“只生成日报但不推送”，使用 `report`，必要时允许透传额外参数，例如 `--output report.md`。
- 如果用户要求“推送已有日报文件”，使用 `send-telegram --text-file <path>`。
- 执行后用简洁中文汇报：实际运行了什么命令、结果如何、是否生成文件、是否已推送 Telegram。

## 子命令映射

- `/blockbeats-monitor init-db`
- `/blockbeats-monitor ingest`
- `/blockbeats-monitor report`
- `/blockbeats-monitor report --output report.md`
- `/blockbeats-monitor send-telegram --text-file report.md`
- `/blockbeats-monitor run-daily`

## 当前任务

读取用户传入的参数：`$ARGUMENTS`

按以下流程执行：

1. 先确认 `config.toml` 是否存在。
2. 根据 `$ARGUMENTS` 选择对应的 `python3 scripts/blockbeats_monitor.py --config config.toml ...` 命令。
3. 运行命令。
4. 将关键结果用中文反馈给用户。
