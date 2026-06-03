# 本文件测试 API 响应标准化、SQLite 初始化、去重入库和匹配关系写入。

import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from scripts.blockbeats_client import normalize_item
from scripts.db import connect, fetch_matched_items, init_db, store_items


class DbClientTests(unittest.TestCase):
    def test_normalize_item_tolerates_missing_optional_fields(self):
        now = datetime(2026, 6, 3, 10, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        item = normalize_item({"title": "Avenir Group 新闻", "url": "https://example.com/a"}, "newsflash_24h", now)
        self.assertEqual(item["title"], "Avenir Group 新闻")
        self.assertEqual(item["abstract"], "")
        self.assertEqual(item["content"], "")
        self.assertIn("Avenir Group", item["raw_json"])

    def test_init_db_and_store_items_dedupes_matches(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "monitor.sqlite"
            conn = init_db(db_path)
            now = "2026-06-03T10:00:00+08:00"
            item = {
                "source": "blockbeats",
                "source_type": "newsflash_24h",
                "title": "Avenir Group 和 李林相关消息",
                "abstract": "",
                "content": "火币创始人李林相关",
                "url": "https://example.com/1",
                "published_at": "2026-06-03T09:00:00+08:00",
                "raw_json": json.dumps({"title": "Avenir Group 和 李林相关消息"}, ensure_ascii=False),
            }
            first = store_items(conn, [item], now)
            second = store_items(conn, [item], now)
            rows = fetch_matched_items(conn, "2026-06-03T00:00:00+08:00", "2026-06-04T00:00:00+08:00")
            self.assertEqual(first["stored"], 1)
            self.assertEqual(second["stored"], 1)
            self.assertEqual(len({row["id"] for row in rows}), 1)
            self.assertEqual({row["group_id"] for row in rows}, {"avenir_group", "li_lin"})
            source_rows = conn.execute("select item_id, source_type from item_sources").fetchall()
            self.assertEqual(len(source_rows), 1)
            conn.close()

    def test_canonicalizes_same_content_across_source_types(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "monitor.sqlite"
            conn = init_db(db_path)
            now = "2026-06-03T10:00:00+08:00"
            base = {
                "source": "blockbeats",
                "title": "Tradfi Summer来临！Binance已上线69个TradFi合约品种，多数日成交额超百万",
                "abstract": "",
                "content": "Binance 美股相关内容",
                "url": "https://m.theblockbeats.info/flash/349215",
                "published_at": "2026-06-03T15:25:33+08:00",
            }
            newsflash = dict(base, source_type="newsflash_24h", raw_json=json.dumps({"source_type": "newsflash_24h"}, ensure_ascii=False))
            important = dict(base, source_type="newsflash_important", raw_json=json.dumps({"source_type": "newsflash_important"}, ensure_ascii=False))
            result = store_items(conn, [newsflash, important], now)
            self.assertEqual(result["stored"], 1)
            self.assertEqual(result["source_variants"], 2)
            source_items = conn.execute("select id, source_type, url from source_items").fetchall()
            self.assertEqual(len(source_items), 1)
            self.assertEqual(source_items[0]["source_type"], "newsflash_important")
            variants = conn.execute("select source_type from item_sources order by source_type").fetchall()
            self.assertEqual([row["source_type"] for row in variants], ["newsflash_24h", "newsflash_important"])
            conn.close()

    def test_init_db_migration_is_idempotent_for_item_sources(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "monitor.sqlite"
            conn = init_db(db_path)
            now = "2026-06-03T10:00:00+08:00"
            base = {
                "source": "blockbeats",
                "title": "T",
                "abstract": "",
                "content": "C",
                "url": "https://example.com/same",
                "published_at": "2026-06-03T15:25:33+08:00",
            }
            store_items(conn, [
                dict(base, source_type="newsflash_24h", raw_json=json.dumps({"source_type": "newsflash_24h"}, ensure_ascii=False)),
                dict(base, source_type="newsflash_important", raw_json=json.dumps({"source_type": "newsflash_important"}, ensure_ascii=False)),
            ], now)
            conn.close()

            conn = init_db(db_path)
            variants = conn.execute("select source_type from item_sources order by source_type").fetchall()
            self.assertEqual([row["source_type"] for row in variants], ["newsflash_24h", "newsflash_important"])
            conn.close()


if __name__ == "__main__":
    unittest.main()
