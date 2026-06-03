# 本文件测试 5 组关键词的 OR/AND 匹配逻辑。

import unittest

from scripts.keywords import KEYWORD_GROUPS, match_group, match_groups


class KeywordTests(unittest.TestCase):
    def group(self, group_id):
        return next(group for group in KEYWORD_GROUPS if group.id == group_id)

    def test_or_group_matches_avenir(self):
        self.assertTrue(match_group("未来资本发布新动态", self.group("avenir_group")))
        self.assertTrue(match_group("Avenir Group news", self.group("avenir_group")))

    def test_li_lin_aliases(self):
        self.assertTrue(match_group("Founder of Huobi Li Lin appears in report", self.group("li_lin")))
        self.assertTrue(match_group("火币创始人李林相关消息", self.group("li_lin")))

    def test_and_group_requires_all_parts(self):
        group = self.group("binance_us_stocks")
        self.assertTrue(match_group("Binance will offer tokenized stocks", group))
        self.assertFalse(match_group("Binance market update only", group))

    def test_multiple_groups_can_match(self):
        matches = match_groups("币安交易所推进美股和股票代币，一个账户提升资金效率")
        self.assertGreaterEqual(len(matches), 2)


if __name__ == "__main__":
    unittest.main()
