import json
import os
from pathlib import Path
import tempfile
import unittest


from meridian import Game
from meridian.common import pygame
from meridian.persistence import SaveManager, default_data, default_statistics
from meridian.system import ACHIEVEMENTS


class SaveManagerTests(unittest.TestCase):
    def setUp(self):
        test_root = Path.cwd() / "tests" / ".tmp"
        test_root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=test_root)
        self.path = Path(self.temp.name) / "save.json"
        self.manager = SaveManager(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_first_load_and_unknown_fields(self):
        data = self.manager.load()
        self.assertEqual(data["schema_version"], 5)
        data["future_field"] = {"kept": True}
        self.manager.save(data)
        self.assertTrue(self.manager.load()["future_field"]["kept"])

    def test_atomic_save_creates_backup(self):
        first = default_data()
        first["records"]["snake"]["best_score"] = 5
        self.manager.save(first)
        second = default_data()
        second["records"]["snake"]["best_score"] = 10
        self.manager.save(second)
        self.assertTrue(self.manager.backup_path.exists())
        with self.manager.backup_path.open("r", encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["records"]["snake"]["best_score"], 5)

    def test_corrupt_primary_uses_backup_and_isolates_bad_file(self):
        data = default_data()
        data["records"]["2048"]["best_score"] = 2048
        self.manager.save(data)
        self.manager.save(data)
        self.path.write_text("{bad json", encoding="utf-8")
        loaded = self.manager.load()
        self.assertEqual(loaded["records"]["2048"]["best_score"], 2048)
        self.assertTrue(list(self.path.parent.glob("save.corrupt-*.json")))

    def test_reset_boundaries(self):
        data = default_data()
        data["settings"]["music_volume"] = 0.1
        data["records"]["snake"]["best_score"] = 20
        settings_reset = self.manager.reset_settings(data)
        self.assertEqual(settings_reset["settings"]["music_volume"], 0.55)
        self.assertEqual(settings_reset["records"]["snake"]["best_score"], 20)
        erased = self.manager.erase_progress(data)
        self.assertEqual(erased["settings"]["music_volume"], 0.1)
        self.assertEqual(erased["records"]["snake"]["best_score"], 0)

    def test_schema_three_resets_only_air_raid_data(self):
        old = default_data()
        old["schema_version"] = 2
        old["records"]["snake"]["best_score"] = 77
        old["statistics"]["snake"]["food_eaten"] = 55
        old["records"]["air"]["best_score"] = 99999
        old["statistics"]["air"]["enemies_destroyed"] = 400
        old["progress"]["air"]["unlocked"] = 16
        old["achievements"]["air_old"] = {"unlocked_at": "old"}
        old["achievements"]["snake_5"] = {"unlocked_at": "kept"}
        migrated = self.manager.migrate(old)
        self.assertEqual(migrated["schema_version"], 5)
        self.assertEqual(migrated["records"]["snake"]["best_score"], 77)
        self.assertEqual(migrated["statistics"]["snake"]["food_eaten"], 55)
        self.assertEqual(migrated["records"]["air"]["best_score"], 0)
        self.assertEqual(migrated["statistics"]["air"]["enemies_destroyed"], 0)
        self.assertEqual(migrated["progress"]["air"]["unlocked"], 1)
        self.assertNotIn("air_old", migrated["achievements"])
        self.assertIn("snake_5", migrated["achievements"])

    def test_schema_four_adds_tank_without_resetting_other_games(self):
        old = default_data()
        old["schema_version"] = 4
        old["statistics"].pop("tank", None)
        old["progress"].pop("tank", None)
        old["statistics"]["snake"]["best_score"] = 17

        migrated = self.manager.migrate(old)

        self.assertEqual(migrated["schema_version"], 5)
        self.assertEqual(migrated["statistics"]["snake"]["best_score"], 17)
        self.assertEqual(migrated["statistics"]["tank"], default_statistics()["tank"])
        self.assertEqual(migrated["progress"]["tank"], {"run_active": False, "run_state": None})


class RuntimePersistenceTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        test_root = Path.cwd() / "tests" / ".tmp"
        test_root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=test_root)
        self.path = str(Path(self.temp.name) / "runtime.json")
        self.previous_save_path = os.environ.get("MERIDIAN_SAVE_PATH")
        os.environ["MERIDIAN_SAVE_PATH"] = self.path

    def tearDown(self):
        if self.previous_save_path is None:
            os.environ.pop("MERIDIAN_SAVE_PATH", None)
        else:
            os.environ["MERIDIAN_SAVE_PATH"] = self.previous_save_path
        self.temp.cleanup()

    def test_settings_records_and_stats_reload(self):
        game = Game()
        game.audio.set_music_volume(0.2)
        game.snake_speed_mode = "fast"
        game.snake_best = 17
        game._record_stat("snake", "food_eaten", 12)
        game._save_now()

        restored = Game()
        self.assertAlmostEqual(restored.audio.music_volume, 0.2)
        self.assertEqual(restored.snake_speed_mode, "fast")
        self.assertEqual(restored.snake_best, 17)
        self.assertEqual(restored._stat("snake", "food_eaten"), 12)

    def test_language_setting_persists_and_applies(self):
        game = Game()
        game.language = "zh_hans"
        game._save_now()
        restored = Game()
        self.assertEqual(restored.language, "zh_hans")
        self.assertEqual(restored.save_data["settings"]["language"], "zh_hans")

    def test_achievement_unlocks_once(self):
        game = Game()
        game._record_stat("snake", "best_score", 5, mode="max")
        first_count = len(game.save_data["achievements"])
        first_notifications = len(game.achievement_notifications)
        game._record_stat("snake", "best_score", 8, mode="max")
        self.assertEqual(first_count, 1)
        self.assertEqual(len(game.save_data["achievements"]), 1)
        self.assertEqual(len(game.achievement_notifications), first_notifications)

    def test_developer_mode_blocks_stats_achievements_and_saves(self):
        game = Game()
        before_stats = repr(game.save_data["statistics"])
        before_achievements = repr(game.save_data["achievements"])
        before_snapshot = game._last_persisted_snapshot
        game._enable_developer_mode()
        game._record_stat("snake", "best_score", 999, mode="max")
        game._check_achievements()
        game._save_now()
        self.assertEqual(repr(game.save_data["statistics"]), before_stats)
        self.assertEqual(repr(game.save_data["achievements"]), before_achievements)
        self.assertEqual(game._last_persisted_snapshot, before_snapshot)

    def test_all_achievement_definitions_are_unique(self):
        self.assertEqual(len(ACHIEVEMENTS), 48)
        self.assertEqual(len({item[0] for item in ACHIEVEMENTS}), 48)

    def test_gomoku_completion_is_not_double_counted(self):
        game = Game()
        game._start_new_game()
        game.board.winner = 1
        game._on_win()
        game._on_win()
        self.assertEqual(game._stat("gomoku", "games_completed"), 1)
        self.assertEqual(game._stat("gomoku", "black_wins"), 1)

    def test_system_pages_draw_and_scaled_events_map(self):
        game = Game()
        game.state = game.SYSTEM_SETTINGS
        game.draw()
        game.state = game.PROFILE
        game.draw()
        game._display_scale = 2.0
        game._display_offset = (100, 50)
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(300, 250))
        mapped = game._map_event_to_logical(event)
        self.assertEqual(mapped.pos, (100, 100))

    def test_tank_playing_capture_is_persisted(self):
        game = Game()
        game._start_tank_battle()

        data = game._capture_data()

        self.assertTrue(data["progress"]["tank"]["run_active"])
        self.assertEqual(data["progress"]["tank"]["run_state"], game._capture_tank_run_state())

    def test_invalid_tank_snapshot_only_clears_tank_run(self):
        data = default_data()
        data["statistics"]["tank"]["games_completed"] = 9
        data["statistics"]["snake"]["best_score"] = 17
        data["progress"]["snake"] = {"run_active": True, "run_state": {"kept": True}}
        data["progress"]["tank"] = {"run_active": True, "run_state": {"bad": True}}
        SaveManager(self.path).save(data)

        game = Game()

        self.assertEqual(game.save_data["progress"]["tank"], {"run_active": False, "run_state": None})
        self.assertEqual(game.save_data["statistics"]["tank"]["games_completed"], 9)
        self.assertEqual(game.save_data["statistics"]["snake"]["best_score"], 17)
        self.assertEqual(game.save_data["progress"]["snake"]["run_state"], {"kept": True})
        self.assertEqual(game.tank_restore_notice, "TANK SAVE COULD NOT BE RESTORED")


if __name__ == "__main__":
    unittest.main()
