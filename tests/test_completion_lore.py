"""Completion-linked Lore synchronization, registration, and UI gates."""

from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import patch
import uuid

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from meridian import Game, lore
from meridian.common import pygame
from meridian.completion import (
    WORLD_IDS,
    global_completion,
    lore_condition_met,
    world_completion,
)
from meridian.localization import set_language
from meridian.persistence import SaveManager, default_data
from meridian.system import ACHIEVEMENTS, SystemMixin


class LoreHarness(SystemMixin):
    LORE_READER = "lore_reader"
    LORE_STORY = "lore_story"

    def __init__(self):
        self.save_data = default_data()
        self.achievement_notifications = []
        self.dev_mode = False
        self.save_calls = 0
        self.state = self.LORE_READER
        self._init_lore_reader()

    def _save_now(self):
        self.save_calls += 1


def _max_out_completion_facts(data):
    for game_stats in data["statistics"].values():
        for key, value in list(game_stats.items()):
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                game_stats[key] = 100_000
    data["statistics"]["mines"]["wins_by_mode"] = {
        "9x10": 1,
        "16x40": 1,
    }
    data["achievements"] = {
        definition[0]: {"unlocked_at": "2026-01-01T00:00:00"}
        for definition in ACHIEVEMENTS
    }


class LoreConditionTests(unittest.TestCase):
    def test_stat_achievement_always_and_completion_conditions(self):
        data = default_data()
        data["statistics"]["snake"]["best_score"] = 40
        data["achievements"]["air_campaign"] = {"unlocked_at": "now"}
        self.assertTrue(lore_condition_met("always", data))
        self.assertTrue(lore_condition_met("stat:snake:best_score:40", data))
        self.assertFalse(lore_condition_met("stat:snake:best_score:41", data))
        self.assertTrue(lore_condition_met("achievement:air_campaign", data))
        self.assertFalse(lore_condition_met("achievement:missing", data))
        self.assertTrue(lore_condition_met(
            "completion:50", data, completion_percent=50,
        ))
        self.assertFalse(lore_condition_met(
            "completion:50", data, completion_percent=49,
        ))

    def test_gomoku_wins_aggregate_both_colors(self):
        data = default_data()
        data["statistics"]["gomoku"]["black_wins"] = 4
        data["statistics"]["gomoku"]["white_wins"] = 6
        self.assertTrue(lore_condition_met("stat:gomoku:wins:10", data))

    def test_malformed_conditions_and_values_fail_closed(self):
        data = default_data()
        data["statistics"]["gomoku"]["black_wins"] = "broken"
        for condition in (
            None,
            "",
            "unknown:thing",
            "stat:snake:best_score",
            "stat:snake:best_score:not-a-number",
            "stat:gomoku:wins:10",
            "completion:not-a-number",
        ):
            self.assertFalse(lore_condition_met(condition, data), condition)
        data["statistics"]["mines"]["wins_by_mode"] = "broken"
        self.assertFalse(lore_condition_met("completion:1", data))


class LoreSynchronizationTests(unittest.TestCase):
    def test_sync_backfills_saved_facts_without_marking_entries_read(self):
        game = LoreHarness()
        game.save_data["statistics"]["global"]["launches"] = 5
        game.save_data["statistics"]["snake"]["best_score"] = 40
        game.save_data["achievements"]["air_campaign"] = {"unlocked_at": "now"}
        game.save_data["lore"]["unlocked_entries"] = ["unknown_old_id"]

        new_ids = game._sync_lore_progress(notify_completion=False)

        unlocked = game.save_data["lore"]["unlocked_entries"]
        self.assertIn("unknown_old_id", unlocked)
        self.assertIn("meridian_nexus", unlocked)
        self.assertIn("snake_ouroboros", unlocked)
        self.assertIn("air_meridian_link", unlocked)
        self.assertEqual(game.save_data["lore"]["read_entries"], [])
        self.assertEqual(game.achievement_notifications, [])
        self.assertEqual(game.save_calls, 1)
        self.assertTrue(set(new_ids).issubset(set(unlocked)))

    def test_sync_is_monotonic_and_idempotent(self):
        game = LoreHarness()
        first = game._sync_lore_progress()
        first_snapshot = list(game.save_data["lore"]["unlocked_entries"])
        saves_after_first = game.save_calls
        second = game._sync_lore_progress()
        self.assertTrue(first)
        self.assertEqual(second, [])
        self.assertEqual(game.save_data["lore"]["unlocked_entries"], first_snapshot)
        self.assertEqual(game.save_calls, saves_after_first)

    def test_developer_mode_does_not_mutate_or_save(self):
        game = LoreHarness()
        game.dev_mode = True
        before = list(game.save_data["lore"]["unlocked_entries"])
        self.assertEqual(game._sync_lore_progress(), [])
        self.assertEqual(game.save_data["lore"]["unlocked_entries"], before)
        self.assertEqual(game.save_calls, 0)

    def test_sync_repairs_a_malformed_lore_container(self):
        game = LoreHarness()
        game.save_data["lore"] = "broken"
        game._sync_lore_progress()
        self.assertIsInstance(game.save_data["lore"], dict)
        self.assertIn("meridian_origin", game.save_data["lore"]["unlocked_entries"])

    def test_sync_fails_closed_for_malformed_nested_save_values(self):
        game = LoreHarness()
        game.save_data["statistics"]["mines"]["wins_by_mode"] = "broken"
        game.save_data["statistics"]["tank"] = "broken"
        game.save_data["achievements"] = {None: {}}
        game.save_data["lore"]["unlocked_entries"] = [{"broken": True}]

        game._sync_lore_progress(notify_completion=False)

        self.assertIsInstance(global_completion(game.save_data), int)

    def test_invalid_and_completion_conditions_do_not_reduce_world_lore_credit(self):
        world = lore.get_world("gomoku")
        extra_entries = [
            {"id": "invalid-condition", "unlock": "stat:broken"},
            {"id": "circular-condition", "unlock": "completion:100"},
        ]
        world["lore_entries"].extend(extra_entries)
        try:
            data = default_data()
            data["lore"]["unlocked_entries"] = ["gomoku_first_god"]
            self.assertEqual(world_completion("gomoku", data).lore, 100)
        finally:
            del world["lore_entries"][-len(extra_entries):]


class LoreStartupIntegrationTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.previous_save_path = os.environ.get("MERIDIAN_SAVE_PATH")
        save_root = Path(os.environ.get("MERIDIAN_TEST_SAVE_ROOT", Path.cwd()))
        self.save_path = save_root / f".meridian-lore-test-{uuid.uuid4().hex}.json"
        os.environ["MERIDIAN_SAVE_PATH"] = str(self.save_path)

    def tearDown(self):
        set_language("en")
        pygame.quit()
        if self.previous_save_path is None:
            os.environ.pop("MERIDIAN_SAVE_PATH", None)
        else:
            os.environ["MERIDIAN_SAVE_PATH"] = self.previous_save_path
        for path in (
            self.save_path,
            self.save_path.with_suffix(".json.bak"),
            self.save_path.with_suffix(".json.tmp"),
        ):
            path.unlink(missing_ok=True)

    def test_launch_is_counted_before_silent_backfill_and_reader_draws_bilingually(self):
        data = default_data()
        data["lore"]["unlocked_entries"] = ["unknown_old_id"]
        _max_out_completion_facts(data)
        data["statistics"]["global"]["launches"] = 4
        SaveManager(self.save_path).save(data)

        game = Game()
        try:
            unlocked = game.save_data["lore"]["unlocked_entries"]
            self.assertEqual(game.save_data["statistics"]["global"]["launches"], 5)
            self.assertIn("meridian_nexus", unlocked)
            self.assertIn("resonance_100", unlocked)
            self.assertIn("unknown_old_id", unlocked)
            self.assertEqual(game.achievement_notifications, [])

            game.state = game.LORE_READER
            for language in ("en", "zh_hans"):
                game.language = language
                set_language(language)
                game._draw_lore_reader()
        finally:
            game.audio.stop()

    def test_reapplying_erased_progress_clears_pending_tank_resume(self):
        game = Game()
        try:
            game._pending_run_states["tank"] = {"stale": True}
            game.tank_restore_notice = "STALE NOTICE"
            game.save_data = game.save_manager.erase_progress(game.save_data)

            game._apply_loaded_data()

            self.assertNotIn("tank", game._pending_run_states)
            self.assertIsNone(game.tank_restore_notice)
        finally:
            game.audio.stop()

    def test_all_confirmed_facts_reach_global_100_and_final_resonance(self):
        game = LoreHarness()
        _max_out_completion_facts(game.save_data)

        game._sync_lore_progress()

        for game_id in WORLD_IDS:
            score = world_completion(game_id, game.save_data)
            self.assertEqual(score.achievement, 100, game_id)
            self.assertEqual(score.objectives, 100, game_id)
            self.assertEqual(score.lore, 100, game_id)
            self.assertEqual(score.total, 100, game_id)
        self.assertEqual(global_completion(game.save_data), 100)
        self.assertIn(
            "resonance_100",
            game.save_data["lore"]["unlocked_entries"],
        )
        self.assertEqual(len(game.achievement_notifications), 4)

    def test_silent_startup_style_backfill_queues_no_resonance_notifications(self):
        game = LoreHarness()
        _max_out_completion_facts(game.save_data)
        game._sync_lore_progress(notify_completion=False, persist=False)
        self.assertIn("resonance_100", game.save_data["lore"]["unlocked_entries"])
        self.assertEqual(game.achievement_notifications, [])
        self.assertEqual(game.save_calls, 0)


class LoreReaderGateTests(unittest.TestCase):
    def setUp(self):
        self.game = LoreHarness()
        self.entry = lore.get_lore_entry("resonance_25")

    def test_locked_completion_entry_uses_hidden_title(self):
        self.assertFalse(self.game._is_lore_unlocked(self.entry))
        self.assertEqual(self.game._lore_entry_title(self.entry), "???")

    def test_direct_and_keyboard_open_use_the_same_gate(self):
        self.assertFalse(self.game._start_lore_reading(self.entry))
        self.assertEqual(self.game.state, self.game.LORE_READER)

        self.game.lore_category_index = 0
        self.game.lore_entry_index = 3
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        self.game._handle_lore_reader_event(event)
        self.assertEqual(self.game.state, self.game.LORE_READER)
        self.assertIsNone(self.game.lore_reading_entry_id)

    def test_mouse_cannot_bypass_locked_completion_entry(self):
        self.game.lore_category_index = 0
        self.game.lore_entry_index = 3
        self.game.lore_scroll = 3
        self.game._lore_reader_layout = lambda: {
            "panel": pygame.Rect(30, 30, 1220, 660),
            "tab_rects": [],
            "list_y": 100,
            "entry_h": 40,
            "entry_gap": 8,
            "visible_entries": 4,
        }
        pos = (100, 110)
        self.game._handle_lore_reader_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)
        )
        self.game._handle_lore_reader_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos)
        )
        self.assertEqual(self.game.state, self.game.LORE_READER)
        self.assertIsNone(self.game.lore_reading_entry_id)
        self.assertEqual(self.game.save_data["lore"]["read_entries"], [])

        self.game.save_data["lore"]["unlocked_entries"].append("resonance_25")
        self.game._handle_lore_reader_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)
        )
        self.game._handle_lore_reader_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos)
        )
        self.assertEqual(self.game.state, self.game.LORE_STORY)
        self.assertEqual(self.game.lore_reading_entry_id, "resonance_25")
        self.assertIn("resonance_25", self.game.save_data["lore"]["read_entries"])


class LoreRegistrationTests(unittest.TestCase):
    def test_duplicate_world_and_lore_ids_are_rejected_without_partial_write(self):
        with self.assertRaisesRegex(ValueError, "Duplicate game world"):
            lore.register_game_world(
                "gomoku",
                world_name_en="Duplicate", world_name_zh="重复",
                world_summary_en="Duplicate", world_summary_zh="重复",
                prologue_en=[], prologue_zh=[],
                menu_flavor_en="Duplicate", menu_flavor_zh="重复",
            )

        game_id = f"duplicate-test-{uuid.uuid4().hex}"
        with self.assertRaisesRegex(ValueError, "Duplicate lore entry id"):
            lore.register_game_world(
                game_id,
                world_name_en="Duplicate", world_name_zh="重复",
                world_summary_en="Duplicate", world_summary_zh="重复",
                prologue_en=[], prologue_zh=[],
                menu_flavor_en="Duplicate", menu_flavor_zh="重复",
                lore_entries=[{
                    "id": "meridian_origin",
                    "title_en": "Duplicate", "title_zh": "重复",
                    "content_en": [], "content_zh": [],
                }],
            )
        self.assertIsNone(lore.get_world(game_id))

    def test_register_lore_entry_accepts_unlock_and_rejects_duplicate_id(self):
        entry_id = f"test-entry-{uuid.uuid4().hex}"
        world = lore.get_world("gomoku")
        try:
            lore.register_lore_entry(
                "gomoku", entry_id,
                title_en="Test", title_zh="测试",
                content_en=["Test"], content_zh=["测试"],
                unlock="stat:gomoku:wins:99",
            )
            self.assertEqual(lore.get_lore_entry(entry_id)["unlock"], "stat:gomoku:wins:99")
            with self.assertRaisesRegex(ValueError, "Duplicate lore entry id"):
                lore.register_device_lore(
                    entry_id,
                    title_en="Duplicate", title_zh="重复",
                    content_en=[], content_zh=[],
                )
        finally:
            world["lore_entries"][:] = [
                entry for entry in world["lore_entries"] if entry["id"] != entry_id
            ]
            lore._lore_by_id.pop(entry_id, None)

    def test_dynamic_category_uses_registered_bilingual_world_names(self):
        game_id = f"dynamic-{uuid.uuid4().hex}"
        lore.register_game_world(
            game_id,
            world_name_en="DYNAMIC WORLD", world_name_zh="动态世界",
            world_summary_en="Summary", world_summary_zh="简介",
            prologue_en=[], prologue_zh=[],
            menu_flavor_en="Flavor", menu_flavor_zh="风味",
            desktop_subtitle_en="DYNAMIC DESKTOP",
        )
        try:
            game = LoreHarness()
            with patch("meridian.system.is_chinese", return_value=False):
                self.assertEqual(
                    game._lore_category_label(game_id, f"lore_category_{game_id}"),
                    "DYNAMIC DESKTOP",
                )
            with patch("meridian.system.is_chinese", return_value=True):
                self.assertEqual(
                    game._lore_category_label(game_id, f"lore_category_{game_id}"),
                    "动态世界",
                )
        finally:
            lore._world_registry.pop(game_id, None)


if __name__ == "__main__":
    unittest.main()
