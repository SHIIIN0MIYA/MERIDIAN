import unittest

from meridian.lore import get_all_worlds, collect_lore_translations, get_world


class LoreTests(unittest.TestCase):
    def test_seven_worlds_are_registered(self):
        worlds = get_all_worlds()
        expected_ids = {"gomoku", "snake", "breakout", "2048", "mines", "tetris", "air", "tank"}
        actual_ids = {w["game_id"] for w in worlds}
        self.assertEqual(actual_ids, expected_ids)

    def test_each_world_has_required_fields(self):
        required = ("game_id", "world_name_en", "world_name_zh",
                     "prologue_en", "prologue_zh",
                     "menu_flavor_en", "menu_flavor_zh")
        for world in get_all_worlds():
            for key in required:
                self.assertIn(key, world,
                              f"Missing '{key}' in world '{world.get('game_id', '?')}'")

    def test_collect_lore_translations_has_world_names(self):
        translations = collect_lore_translations()
        self.assertGreater(len(translations), 10)
        for world in get_all_worlds():
            key = f"world_{world['game_id']}_name"
            self.assertIn(key, translations,
                          f"Missing translation key '{key}'")

    def test_iron_arena_world_and_unlockable_lore_are_registered(self):
        world = get_world("tank")
        self.assertEqual(world["world_name_en"], "IRON ARENA")
        self.assertEqual(world["world_name_zh"], "钢铁斗场")
        self.assertEqual(world["prologue_en"], [
            "THE IRON ARENA ACCEPTS TWO SIGNALS.",
            "RED AND BLUE WAKE BENEATH THE SAME SKY.",
            "NO SPAWN IS SAFE FOREVER.",
            "ONLY THE LAST SCORE SURVIVES THE BELL.",
        ])
        entries = {entry["id"]: entry for entry in world["lore_entries"]}
        self.assertEqual(entries["arena_origin"]["unlock"], "stat:tank:matches_completed:1")
        self.assertEqual(entries["moving_spawn"]["unlock"], "stat:tank:matches_completed:10")


if __name__ == "__main__":
    unittest.main()
