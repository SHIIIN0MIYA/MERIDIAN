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

    def test_old_save_gains_master_volume_without_changing_category_levels(self):
        old = default_data()
        old["settings"].pop("master_volume", None)
        old["settings"]["music_volume"] = 0.3
        old["settings"]["sfx_volume"] = 0.7

        migrated = self.manager.migrate(old)

        self.assertEqual(migrated["settings"]["master_volume"], 1.0)
        self.assertEqual(migrated["settings"]["music_volume"], 0.3)
        self.assertEqual(migrated["settings"]["sfx_volume"], 0.7)


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
        game.master_volume = 0.4
        game.audio.set_music_volume(0.2)
        game.snake_speed_mode = "fast"
        game.snake_best = 17
        game._record_stat("snake", "food_eaten", 12)
        game._save_now()

        restored = Game()
        self.assertAlmostEqual(restored.master_volume, 0.4)
        self.assertAlmostEqual(restored.audio.music_volume, 0.2)
        self.assertEqual(restored.snake_speed_mode, "fast")
        self.assertEqual(restored.snake_best, 17)
        self.assertEqual(restored._stat("snake", "food_eaten"), 12)

    def test_master_volume_is_clamped_when_loaded_and_captured(self):
        data = default_data()
        data["settings"]["master_volume"] = 2.0
        data["records"]["snake"]["best_score"] = 23
        self.manager = SaveManager(self.path)
        self.manager.save(data)

        game = Game()

        self.assertEqual(game.master_volume, 1.0)
        game.master_volume = -0.5
        captured = game._capture_data()
        self.assertEqual(captured["settings"]["master_volume"], 0.0)
        self.assertEqual(captured["records"]["snake"]["best_score"], 23)

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
        self.assertEqual(len(ACHIEVEMENTS), 60)
        self.assertEqual(len({item[0] for item in ACHIEVEMENTS}), 60)

    def test_tank_has_twelve_unique_achievements_with_fixed_progress(self):
        tank = [item for item in ACHIEVEMENTS if item[3] == "tank"]
        self.assertEqual(
            [(item[0], item[4], item[5]) for item in tank],
            [
                ("tank_first_clash", "matches_completed", 1),
                ("tank_first_victory", "wins", 1),
                ("tank_sharpshooter", "accurate_matches", 1),
                ("tank_demolition", "bricks_destroyed", 100),
                ("tank_arsenal_master", "item_variety", 8),
                ("tank_iron_will", "iron_will_kills", 1),
                ("tank_sudden_victor", "sudden_wins", 1),
                ("tank_mine_expert", "mine_hits", 20),
                ("tank_shield_wall", "shield_blocks", 25),
                ("tank_overdrive_ace", "overdrive_double_kills", 1),
                ("tank_turnaround", "comeback_wins", 1),
                ("tank_arena_legend", "matches_completed", 50),
            ],
        )

    def test_tank_compound_achievement_progress_and_unlock_once(self):
        game = Game()
        stats = game.save_data["statistics"]["tank"]
        stats.update({
            "repair_uses": 1, "shield_uses": 2, "speed_uses": 3, "mine_uses": 4,
            "emp_uses": 1, "piercing_uses": 1, "smoke_uses": 1, "warp_uses": 1,
        })
        arsenal = next(item for item in ACHIEVEMENTS if item[0] == "tank_arsenal_master")
        self.assertEqual(game._achievement_progress(arsenal), (8, 8))
        stats["matches_completed"] = 1
        game._check_achievements()
        game._check_achievements()
        self.assertEqual(list(game.save_data["achievements"]).count("tank_first_clash"), 1)

    def test_achievement_wall_pages_keep_global_indexes_and_lock_during_detail(self):
        game = Game()
        game.achievement_wall_page = 0
        self.assertEqual(len(game._get_achievement_wall_badges()), 48)
        game.achievement_wall_page = 1
        badges = game._get_achievement_wall_badges()
        self.assertEqual(len(badges), 12)
        self.assertEqual([badge["index"] for badge in badges], list(range(48, 60)))
        game.achievement_wall_detail_index = 48
        game._handle_achievement_wall_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
        self.assertEqual(game.achievement_wall_page, 1)
        game.achievement_wall_detail_index = None
        game._handle_achievement_wall_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
        self.assertEqual(game.achievement_wall_page, 0)

    def test_achievement_wall_mouse_paging_preserves_badge_size(self):
        game = Game()
        first_size = game._get_achievement_wall_badges()[0]["rect"].size
        _, next_rect = game._get_achievement_wall_page_rects()
        game._handle_achievement_wall_event(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=1, pos=next_rect.center,
        ))
        self.assertEqual(game.achievement_wall_page, 1)
        self.assertTrue(all(badge["rect"].size == first_size for badge in game._get_achievement_wall_badges()))
        prev_rect, _ = game._get_achievement_wall_page_rects()
        game._handle_achievement_wall_event(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=1, pos=prev_rect.center,
        ))
        self.assertEqual(game.achievement_wall_page, 0)

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

    def test_valid_tank_snapshot_continues_from_menu_and_is_consumed(self):
        source = Game()
        source._start_tank_battle()
        source.tank_engine.score["red"] = 4
        source.tank_engine.remaining_ms = 123456
        brick_row = next(index for index, value in enumerate(source.tank_engine.arena.rows) if "B" in value)
        row = source.tank_engine.arena.rows[brick_row]
        brick_col = row.index("B")
        source.tank_engine.arena.rows[brick_row] = row[:brick_col] + "." + row[brick_col + 1:]
        snapshot = source._capture_tank_run_state()
        data = default_data()
        data["progress"]["tank"] = {"run_active": True, "run_state": snapshot}
        SaveManager(self.path).save(data)

        game = Game()

        self.assertEqual(game._tank_buttons("menu")[0]["action"], "continue")
        game._tank_held = {pygame.K_w: 1}
        game._tank_item_pulses = {"red": True, "blue": True}
        game._continue_tank_battle()
        self.assertEqual(game.state, game.TANK_PLAYING)
        self.assertEqual(game.tank_engine.score["red"], 4)
        self.assertEqual(game.tank_engine.remaining_ms, 123456)
        self.assertEqual(game.tank_engine.arena.rows[brick_row][brick_col], ".")
        self.assertNotIn("tank", game._pending_run_states)
        self.assertEqual(game._tank_held, {})
        self.assertEqual(game._tank_item_pulses, {"red": False, "blue": False})


if __name__ == "__main__":
    unittest.main()
