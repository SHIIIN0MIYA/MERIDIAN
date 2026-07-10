import unittest

from meridian.localization import (
    ZH, contains_chinese, set_language, translate,
    _format_dynamic, register_game_translations,
)


class LocalizationTests(unittest.TestCase):
    def test_translate_returns_original_when_english(self):
        set_language("en")
        self.assertEqual(translate("START"), "START")
        self.assertEqual(translate("NONEXISTENT_KEY"), "NONEXISTENT_KEY")

    def test_translate_returns_chinese_when_available(self):
        set_language("zh_hans")
        self.assertEqual(translate("START"), "开始")
        self.assertEqual(translate("NEW GAME"), "新游戏")

    def test_dynamic_format_maps_patterns(self):
        set_language("zh_hans")
        self.assertEqual(_format_dynamic("SCORE 100"), "得分 100")
        self.assertEqual(_format_dynamic("BEST 50"), "最高 50")
        self.assertEqual(_format_dynamic("CHAPTER 3"), "章节 3")

    def test_contains_chinese_detects_cjk(self):
        self.assertTrue(contains_chinese("你好"))
        self.assertTrue(contains_chinese("Hello 世界"))
        self.assertFalse(contains_chinese("Hello World"))

    def test_register_game_translations_adds_entries(self):
        initial_size = len(ZH)
        register_game_translations("test_game", {"TEST KEY": "测试键"})
        self.assertIn("TEST KEY", ZH)
        self.assertEqual(ZH["TEST KEY"], "测试键")
        # Cleanup
        del ZH["TEST KEY"]
        self.assertEqual(len(ZH), initial_size)


if __name__ == "__main__":
    unittest.main()
