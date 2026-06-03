# 本文件测试 TOML 配置加载和默认值回退。

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from scripts.config import get_blockbeats_api_key, get_db_path, get_lang, get_telegram_config, load_config, set_config


class ConfigTests(unittest.TestCase):
    def tearDown(self):
        set_config({})

    def test_loads_toml_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"
            config_path.write_text(
                """
[blockbeats]
api_key = "toml-key"
lang = "en"

[storage]
db_path = "custom.sqlite"

[telegram]
bot_token = "bot-token"
chat_id = "chat-id"
""",
                encoding="utf-8",
            )
            set_config(load_config(config_path))
            self.assertEqual(get_blockbeats_api_key(), "toml-key")
            self.assertEqual(get_lang(), "en")
            self.assertEqual(str(get_db_path()), "custom.sqlite")
            self.assertEqual(get_telegram_config(), ("bot-token", "chat-id"))

    def test_cli_db_path_overrides_toml_db_path(self):
        set_config({"storage": {"db_path": "toml.sqlite"}})
        self.assertEqual(str(get_db_path("cli.sqlite")), "cli.sqlite")


if __name__ == "__main__":
    unittest.main()
