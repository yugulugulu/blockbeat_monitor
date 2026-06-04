<!-- 本文件用于给 Claude Code 新手说明如何配置、生成日报，并把日报推送到 Telegram。 -->

# BlockBeats 舆情日报 Claude Code 使用说明

这是一个给 Claude Code 使用的 BlockBeats 舆情监控仓库。

它会做 3 件事：

1. 从 BlockBeats 抓取过去 24 小时的快讯、文章和重要内容
2. 按预设关键词分组统计舆情
3. 生成日报，或直接把日报推送到 Telegram 群

## 你最终会用到的命令

如果你只记 2 个命令，记这两个就够了：

生成日报：

```text
/blockbeats-monitor report --output report.md
```

生成日报并推送到 Telegram：

```text
/blockbeats-monitor run-daily
```

## 一、先准备什么

你需要准备 3 项信息：

1. BlockBeats Pro API Key
2. Telegram Bot Token
3. Telegram 群组或频道的 `chat_id`

## 二、先配置 `config.toml`

如果仓库里还没有 `config.toml`，先复制一份示例文件：

```bash
cp config.example.toml config.toml
```

然后打开 `config.toml`，填入你自己的配置：

```toml
[blockbeats]
api_key = "你的 BlockBeats Pro API Key"
lang = "cn"

[telegram]
bot_token = "你的 Telegram Bot Token"
chat_id = "你的 Telegram 群组或频道 ID"

[storage]
db_path = "data/blockbeats_monitor.sqlite"

[report]
timezone = "Asia/Shanghai"
```

这些字段的含义：

- `blockbeats.api_key`：用于抓取 BlockBeats 数据
- `blockbeats.lang`：请求语言，保持 `cn` 即可
- `telegram.bot_token`：用于发 Telegram 消息
- `telegram.chat_id`：消息要发到哪个群、频道或用户
- `storage.db_path`：本地 SQLite 数据库文件位置
- `report.timezone`：日报时间按哪个时区生成

## 三、在 Claude Code 里怎么调用

这个仓库已经提供了 Claude Code 的项目级命令：

```text
/blockbeats-monitor
```

你可以直接在 Claude Code 里输入下面这些命令。

常见命令：

```text
/blockbeats-monitor init-db
/blockbeats-monitor ingest
/blockbeats-monitor report
/blockbeats-monitor report --output report.md
/blockbeats-monitor send-telegram --text-file report.md
/blockbeats-monitor run-daily
```

如果当前会话里看不到 `/blockbeats-monitor`，通常只需要重新打开这个仓库的 Claude Code 会话。

## 四、推荐的新手使用顺序

第一次使用，按这个顺序最稳：

1. 初始化数据库
2. 抓取一次最新数据
3. 生成一份日报
4. 确认内容没问题后，再推送到 Telegram

对应命令如下。

### 1. 初始化数据库

```text
/blockbeats-monitor init-db
```

这一步会创建本地 SQLite 数据库和必要的数据表。

### 2. 抓取最新数据

```text
/blockbeats-monitor ingest
```

这一步会抓取以下 4 个 BlockBeats 端点的数据：

- `/v1/newsflash/24h`
- `/v1/article/24h`
- `/v1/newsflash/important`
- `/v1/article/important`

### 3. 生成日报

如果你只想在本地看日报内容，用这个命令：

```text
/blockbeats-monitor report --output report.md
```

执行后会在仓库目录里生成一个 `report.md` 文件。

日报包含这些内容：

- 总提及
- 关键词热度排名
- 每个关键词组的相关内容
- 昨日重点相关内容

### 4. 把已经生成的日报推送到 Telegram

如果你已经有 `report.md`，可以单独推送：

```text
/blockbeats-monitor send-telegram --text-file report.md
```

这适合你想先检查日报，再决定是否发群。

## 五、如果你想一步完成

如果你不想分步骤跑，直接用：

```text
/blockbeats-monitor run-daily
```

这个命令会一次性完成：

1. 初始化数据库
2. 抓取最新数据
3. 生成日报
4. 保存日报记录
5. 推送到 Telegram

这是最适合日常使用的命令。

## 六、两种最常见的用法

### 只生成日报，不推送

```text
/blockbeats-monitor report --output report.md
```

适合：

- 先人工检查日报内容
- 只想保存本地日报文件
- 不希望立即推送到群里

### 生成日报并推送到 Telegram

```text
/blockbeats-monitor run-daily
```

适合：

- 每天固定产出日报
- 直接发到 Telegram 群
- 不需要手动检查中间文件

## 七、如果你更习惯命令行

上面的 Claude Code 命令，底层实际执行的是 Python CLI。

例如：

```text
/blockbeats-monitor run-daily
```

等价于：

```bash
python3 scripts/blockbeats_monitor.py --config config.toml run-daily
```

再比如：

```text
/blockbeats-monitor report --output report.md
```

等价于：

```bash
python3 scripts/blockbeats_monitor.py --config config.toml report --output report.md
```

所以即使你不用 slash command，也可以直接跑这些 Python 命令。

## 八、遇到问题先检查什么

如果命令跑不通，优先检查这几项：

1. `config.toml` 是否存在
2. `blockbeats.api_key` 是否填写正确
3. `telegram.bot_token` 和 `telegram.chat_id` 是否填写正确
4. 当前 Claude Code 会话是否已经刷新，能否看到 `/blockbeats-monitor`
5. 本地是否有权限写入 `data/blockbeats_monitor.sqlite`

## 九、最短上手流程

如果你只想最快跑通一次，照着下面做：

```bash
cp config.example.toml config.toml
```

填好 `config.toml` 后，在 Claude Code 里依次运行：

```text
/blockbeats-monitor init-db
/blockbeats-monitor ingest
/blockbeats-monitor report --output report.md
```

如果确认日报内容没问题，再执行：

```text
/blockbeats-monitor run-daily
```

## 十、补充说明

- `report` 负责生成日报，但不会发 Telegram
- `send-telegram` 负责发送已有日报文件
- `run-daily` 是完整流程，既生成日报，也发送 Telegram

如果你只保留一个日常命令，保留这个：

```text
/blockbeats-monitor run-daily
```
