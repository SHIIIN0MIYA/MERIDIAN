import unittest

import pygame

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

    def test_tank_english_and_chinese_copy_is_complete(self):
        required = {
            "TANK DUEL": "坦克对决",
            "IRON ARENA": "钢铁斗场",
            "SUDDEN DEATH": "骤死决胜",
            "REPAIR KIT": "维修包",
            "SHIELD": "护盾",
            "OVERDRIVE": "超速驱动",
            "MINE": "地雷",
            "MATCHES COMPLETED": "已完成对局",
            "RESTORE FAILED — STARTING A NEW MATCH": "恢复失败——将开始新对局",
        }
        set_language("zh_hans")
        for english, chinese in required.items():
            self.assertEqual(translate(english), chinese)
        achievement_keys = {
            "FIRST CLASH", "Complete one Tank Duel match",
            "FIRST VICTORY", "Win one Tank Duel match",
            "SHARPSHOOTER", "Hit at least half of 10 or more shots",
            "DEMOLITION CREW", "Destroy 100 brick walls",
            "ARSENAL MASTER", "Use all four item types",
            "IRON WILL", "Score a kill while at one health",
            "SUDDEN VICTOR", "Win in sudden death",
            "MINE EXPERT", "Hit enemies with 20 mines",
            "SHIELD WALL", "Block 25 hits with shields",
            "OVERDRIVE ACE", "Score two kills during one overdrive",
            "TURNAROUND", "Win after falling behind",
            "ARENA LEGEND", "Complete 50 Tank Duel matches",
        }
        self.assertTrue(achievement_keys <= ZH.keys())

    def test_tank_copy_renders_in_both_languages_with_initialized_font_cache(self):
        from meridian.common import render_pixel_text
        from meridian.localization import _font_cache, get_chinese_font

        pygame.font.init()
        _font_cache.clear()
        latin_font = pygame.font.Font(None, 16)
        get_chinese_font(12)
        for language in ("en", "zh_hans"):
            set_language(language)
            surface = render_pixel_text(latin_font, "TANK DUEL", (255, 255, 255), scale=2)
            self.assertGreater(surface.get_width(), 0)
            self.assertGreater(surface.get_height(), 0)

    def test_font_cache_is_rebuilt_after_font_subsystem_restart(self):
        from meridian.localization import clear_font_cache, get_chinese_font

        try:
            pygame.font.init()
            clear_font_cache()
            font1 = get_chinese_font(12)
            font1.render("中文", False, (255, 255, 255))
            pygame.font.quit()
            pygame.font.init()
            font2 = get_chinese_font(12)
            font2.render("中文", False, (255, 255, 255))
            self.assertIsNot(font2, font1)
        finally:
            pygame.font.init()
            clear_font_cache()
            set_language("en")

    def test_font_cache_is_rebuilt_after_pygame_restart(self):
        from meridian.localization import clear_font_cache, get_chinese_font

        try:
            pygame.init()
            clear_font_cache()
            font1 = get_chinese_font(12)
            font1.render("中文", False, (255, 255, 255))
            pygame.quit()
            pygame.init()
            font2 = get_chinese_font(12)
            font2.render("中文", False, (255, 255, 255))
            self.assertIsNot(font2, font1)
        finally:
            pygame.init()
            clear_font_cache()
            set_language("en")


if __name__ == "__main__":
    unittest.main()
