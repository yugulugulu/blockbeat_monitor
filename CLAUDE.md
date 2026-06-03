<!-- 本文件用于告诉 Claude Code 如何把本仓库当作项目级 slash command 和普通项目一起使用。 -->

# BlockBeats Monitor For Claude Code

这个仓库的核心能力在 `scripts/` 目录里，是一个普通 Python 项目。同时，这个仓库现在也提供 Claude Code 的项目级 slash command，用户可以直接通过 `/blockbeats-monitor` 调用。

## 项目目标

- 抓取 BlockBeats 24h 快讯、24h 文章、重要快讯、重要文章
- 按 5 组关键词归类
- 存入本地 SQLite
- 生成 Markdown 日报
- 推送 Telegram

## Claude Code 使用原则

- 把这个仓库当作普通代码仓库使用，不依赖 OpenClaw 的安装或触发机制。
- 优先使用项目级 slash command：`/blockbeats-monitor`。
- 优先运行 `scripts/blockbeats_monitor.py` 里的 CLI 命令。
- 不要把真实的 `config.toml`、`data/` 目录或数据库文件提交到 Git。
- 当用户要求“定时每天发日报”时，Claude Code 负责提供命令和调度建议；真正定时执行要靠外部调度器，例如 `cron`。

## 必看文件

- `.claude/commands/blockbeats-monitor.md`：Claude Code slash command 定义
- `scripts/blockbeats_monitor.py`：主入口 CLI
- `scripts/blockbeats_client.py`：BlockBeats API 抓取
- `scripts/db.py`：SQLite 入库与 canonical 去重
- `scripts/metrics.py`：提及次数、上一周期对比、重点舆情
- `scripts/report.py`：日报渲染
- `scripts/telegram.py`：Telegram 推送
- `config.example.toml`：配置示例

## Claude Code Slash Command

本仓库提供项目级 slash command：

```text
/blockbeats-monitor
```

常见调用方式：

```text
/blockbeats-monitor init-db
/blockbeats-monitor ingest
/blockbeats-monitor report
/blockbeats-monitor report --output report.md
/blockbeats-monitor send-telegram --text-file report.md
/blockbeats-monitor run-daily
```

命令文件位置：

```text
.claude/commands/blockbeats-monitor.md
```

Claude Code 会把文件名 `blockbeats-monitor.md` 注册成 `/blockbeats-monitor`。如果新建完命令后当前会话里看不到，通常需要重新打开该仓库会话。

## 对应 CLI 命令

初始化数据库：

```bash
python3 scripts/blockbeats_monitor.py --config config.toml init-db
```

抓取最新内容：

```bash
python3 scripts/blockbeats_monitor.py --config config.toml ingest
```

生成日报：

```bash
python3 scripts/blockbeats_monitor.py --config config.toml report
```

生成日报并写入文件：

```bash
python3 scripts/blockbeats_monitor.py --config config.toml report --output report.md
```

推送现成日报文件到 Telegram：

```bash
python3 scripts/blockbeats_monitor.py --config config.toml send-telegram --text-file report.md
```

执行完整日报流程：

```bash
python3 scripts/blockbeats_monitor.py --config config.toml run-daily
```

## Claude Code 对用户的说法

如果用户说：

`请帮我每天上午 11:00 生成一份 BlockBeats 舆情日报`

Claude Code 应理解为：

- 使用 `run-daily` 作为主命令
- 提醒用户这需要外部调度器
- 或者直接帮用户生成 `cron` 配置

对应命令：

```bash
python3 /absolute/path/to/blockbeat_monitor/scripts/blockbeats_monitor.py --config /absolute/path/to/blockbeat_monitor/config.toml run-daily
```

## 最小兼容结论

这个仓库已经具备 Claude Code 可用的最小条件：

- 有明确 CLI 入口
- 有配置样例
- 有可直接运行的脚本
- 没有强依赖 OpenClaw runtime

因此 Claude Code 使用这个项目时，重点是：

- 对用户暴露 `/blockbeats-monitor`
- 底层执行 `scripts/blockbeats_monitor.py`
