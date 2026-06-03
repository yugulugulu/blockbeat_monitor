# 本文件测试统计、重点内容排序和日报输出格式。

import sys
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from scripts.metrics import select_important_items, summarize_metrics
from scripts.report import render_report


class MetricsReportTests(unittest.TestCase):
    def sample_row(self, item_id, group_id, group_name, source_type, title, published_at, abstract="", content=""):
        return {
            "id": item_id,
            "group_id": group_id,
            "group_name": group_name,
            "source_type": source_type,
            "title": title,
            "abstract": abstract,
            "content": content,
            "url": "https://example.com/%s" % item_id,
            "published_at": published_at,
        }

    def test_summarize_mentions_and_previous_period(self):
        current = [
            self.sample_row("1", "avenir_group", "Avenir Group舆情相关", "newsflash_24h", "Avenir", "2026-06-02T10:00:00+08:00"),
            self.sample_row("1", "li_lin", "李林相关", "newsflash_24h", "李林", "2026-06-02T10:00:00+08:00"),
        ]
        previous = [
            self.sample_row("2", "avenir_group", "Avenir Group舆情相关", "article_24h", "Avenir old", "2026-06-01T10:00:00+08:00")
        ]
        summaries = summarize_metrics(current, previous)
        avenir = next(item for item in summaries if item["group_id"] == "avenir_group")
        self.assertEqual(avenir["mention_count"], 1)
        self.assertEqual(avenir["previous_mention_count"], 1)
        self.assertEqual(avenir["delta"], 0)

    def test_summarize_dedupes_same_content_across_endpoints(self):
        current = [
            self.sample_row("1", "binance_us_stocks", "币安上美股专项监测", "newsflash_24h", "Same title", "2026-06-02T10:00:00+08:00"),
            self.sample_row("2", "binance_us_stocks", "币安上美股专项监测", "newsflash_important", "Same title", "2026-06-02T10:00:00+08:00"),
        ]
        current[0]["url"] = "https://example.com/same"
        current[1]["url"] = "https://example.com/same"
        summaries = summarize_metrics(current, [])
        binance = next(item for item in summaries if item["group_id"] == "binance_us_stocks")
        self.assertEqual(binance["mention_count"], 1)
        self.assertEqual(len(binance["items"]), 1)
        self.assertEqual(binance["items"][0]["source_type"], "newsflash_important")

    def test_important_sorting_prefers_important_source_and_multi_group(self):
        rows = [
            self.sample_row("normal", "avenir_group", "Avenir Group舆情相关", "newsflash_24h", "Avenir 普通", "2026-06-02T12:00:00+08:00"),
            self.sample_row("important", "avenir_group", "Avenir Group舆情相关", "newsflash_important", "Avenir 重要", "2026-06-02T11:00:00+08:00"),
            self.sample_row("multi", "avenir_group", "Avenir Group舆情相关", "article_important", "Avenir 和 李林", "2026-06-02T10:00:00+08:00"),
            self.sample_row("multi", "li_lin", "李林相关", "article_important", "Avenir 和 李林", "2026-06-02T10:00:00+08:00"),
        ]
        selected = select_important_items(rows)
        self.assertEqual(selected[0]["id"], "multi")
        self.assertEqual(selected[1]["id"], "important")

    def test_important_items_dedupes_same_content_across_endpoints(self):
        rows = [
            self.sample_row("a1", "binance_us_stocks", "币安上美股专项监测", "newsflash_24h", "Same", "2026-06-02T12:00:00+08:00"),
            self.sample_row("a2", "binance_us_stocks", "币安上美股专项监测", "newsflash_important", "Same", "2026-06-02T12:00:00+08:00"),
        ]
        rows[0]["url"] = "https://example.com/same"
        rows[1]["url"] = "https://example.com/same"
        selected = select_important_items(rows)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["source_type"], "newsflash_important")

    def test_report_does_not_include_unconfirmed_metrics(self):
        now = datetime(2026, 6, 3, 10, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        summaries = [
            {
                "group_id": "avenir_group",
                "group_name": "Avenir Group舆情相关",
                "mention_count": 1,
                "previous_mention_count": 0,
                "delta": 1,
                "items": [self.sample_row("1", "avenir_group", "Avenir Group舆情相关", "newsflash_24h", "Avenir 新闻", "2026-06-02T10:00:00+08:00")],
            },
            {"group_id": "li_lin", "group_name": "李林相关", "mention_count": 0, "previous_mention_count": 0, "delta": 0, "items": []},
            {"group_id": "binance_us_stocks", "group_name": "币安上美股专项监测", "mention_count": 0, "previous_mention_count": 0, "delta": 0, "items": []},
            {"group_id": "crypto_exchange_us_stocks", "group_name": "加密平台美股交易舆情", "mention_count": 0, "previous_mention_count": 0, "delta": 0, "items": []},
            {"group_id": "crypto_stock_connect", "group_name": "币股互通市场舆情", "mention_count": 0, "previous_mention_count": 0, "delta": 0, "items": []},
        ]
        report = render_report(now, now, summaries, [])
        self.assertIn("总提及", report)
        for forbidden in ("曝光", "转发", "阅读"):
            self.assertNotIn(forbidden, report)


if __name__ == "__main__":
    unittest.main()
