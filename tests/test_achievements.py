"""Unit tests for the achievement evaluation system.

Covers: standard stat-threshold achievements, special composite keys
(both_sides, mode:…, standard_all_s, item_variety), idempotent unlock,
and notification cap behaviour.
"""

from __future__ import annotations

import os
from pathlib import Path
import unittest
import uuid

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
# Skip ~2s of procedural audio synthesis; no test asserts on sound output.
os.environ.setdefault("MERIDIAN_FAST_AUDIO", "1")

from meridian import Game
from meridian.common import pygame
from meridian.system import ACHIEVEMENTS


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _achievement_ids():
    return {definition[0] for definition in ACHIEVEMENTS}


def _find_achievement(achievement_id: str):
    for definition in ACHIEVEMENTS:
        if definition[0] == achievement_id:
            return definition
    raise KeyError(achievement_id)


class AchievementEvaluationTests(unittest.TestCase):
    """Tests that use the real Game state machine to verify achievement unlock."""

    def setUp(self):
        pygame.init()
        self.previous_save_path = os.environ.get("MERIDIAN_SAVE_PATH")
        save_root = Path(
            os.environ.get("MERIDIAN_TEST_SAVE_ROOT", Path.cwd())
        )
        self.save_path = save_root / (
            f".meridian-achievement-test-{uuid.uuid4().hex}.json"
        )
        os.environ["MERIDIAN_SAVE_PATH"] = str(self.save_path)
        self.game = Game()

    def tearDown(self):
        self.game.audio.stop()
        pygame.quit()
        if self.previous_save_path is None:
            os.environ.pop("MERIDIAN_SAVE_PATH", None)
        else:
            os.environ["MERIDIAN_SAVE_PATH"] = self.previous_save_path
        for path in (
            self.save_path,
            self.save_path.with_suffix(self.save_path.suffix + ".bak"),
            self.save_path.with_suffix(self.save_path.suffix + ".tmp"),
        ):
            path.unlink(missing_ok=True)

    def _set_stat(self, game: str, key: str, value: int):
        self.game.save_data["statistics"][game][key] = value

    def test_snake_score_5_unlocks_small_bite(self):
        self._set_stat("snake", "best_score", 5)
        self.game._check_achievements()
        self.assertIn("snake_5", self.game.save_data["achievements"])

    def test_snake_score_4_does_not_unlock(self):
        self._set_stat("snake", "best_score", 4)
        self.game._check_achievements()
        self.assertNotIn("snake_5", self.game.save_data["achievements"])

    def test_already_unlocked_achievement_stays_unlocked(self):
        self.game.save_data["achievements"]["snake_5"] = {
            "unlocked_at": "2025-06-01T12:00:00"
        }
        stamp = self.game.save_data["achievements"]["snake_5"]["unlocked_at"]
        self._set_stat("snake", "best_score", 99)
        self.game._check_achievements()
        self.assertEqual(
            self.game.save_data["achievements"]["snake_5"]["unlocked_at"], stamp
        )

    def test_gomoku_both_sides_unlocks(self):
        stats = self.game.save_data["statistics"]["gomoku"]
        stats["black_wins"] = 1
        stats["white_wins"] = 1
        self.game._check_achievements()
        self.assertIn("gomoku_both_sides", self.game.save_data["achievements"])

    def test_gomoku_both_sides_only_black_does_not_unlock(self):
        stats = self.game.save_data["statistics"]["gomoku"]
        stats["black_wins"] = 5
        stats["white_wins"] = 0
        self.game._check_achievements()
        self.assertNotIn("gomoku_both_sides", self.game.save_data["achievements"])

    def test_gomoku_wins_sum_both_colors(self):
        stats = self.game.save_data["statistics"]["gomoku"]
        stats["black_wins"] = 3
        stats["white_wins"] = 7
        self.game._check_achievements()
        self.assertIn("gomoku_10_wins", self.game.save_data["achievements"])

    def test_mines_mode_win_unlocks(self):
        stats = self.game.save_data["statistics"]["mines"]
        stats["wins_by_mode"] = {"9x10": 1}
        self.game._check_achievements()
        self.assertIn("mines_9_10", self.game.save_data["achievements"])

    def test_tank_item_variety_all_eight_unlocks(self):
        stats = self.game.save_data["statistics"]["tank"]
        for item in ("repair", "shield", "speed", "mine", "emp",
                     "piercing", "smoke", "warp"):
            stats[f"{item}_uses"] = 1
        self.game._check_achievements()
        self.assertIn("tank_arsenal_master", self.game.save_data["achievements"])

    def test_tank_item_variety_seven_does_not_unlock(self):
        stats = self.game.save_data["statistics"]["tank"]
        for item in ("repair", "shield", "speed", "mine", "emp",
                     "piercing", "smoke"):
            stats[f"{item}_uses"] = 1
        self.game._check_achievements()
        self.assertNotIn("tank_arsenal_master", self.game.save_data["achievements"])

    def test_multiple_achievements_can_unlock_simultaneously(self):
        stats = self.game.save_data["statistics"]["snake"]
        stats["best_score"] = 50
        stats["food_eaten"] = 200
        self.game._check_achievements()
        self.assertIn("snake_5", self.game.save_data["achievements"])
        self.assertIn("snake_10", self.game.save_data["achievements"])
        self.assertIn("snake_20", self.game.save_data["achievements"])
        self.assertIn("snake_40", self.game.save_data["achievements"])
        self.assertIn("snake_food_100", self.game.save_data["achievements"])

    def test_dev_mode_skips_achievement_check(self):
        self._set_stat("snake", "best_score", 999)
        self.game.dev_mode = True
        self.game._check_achievements()
        self.assertNotIn("snake_5", self.game.save_data["achievements"])

    def test_notification_capped_at_three(self):
        # Trigger many achievements at once
        stats = self.game.save_data["statistics"]["snake"]
        stats["best_score"] = 100
        stats["food_eaten"] = 200
        stats["best_fast_score"] = 50
        self.game._check_achievements()
        self.assertLessEqual(len(self.game.achievement_notifications), 3)

    def test_tetris_tetris_achievement(self):
        self._set_stat("tetris", "tetrises", 1)
        self.game._check_achievements()
        self.assertIn("tetris_tetris", self.game.save_data["achievements"])

    def test_breakout_first_clear(self):
        self._set_stat("breakout", "levels_cleared", 1)
        self.game._check_achievements()
        self.assertIn("breakout_first_clear", self.game.save_data["achievements"])

    def test_2048_tile_achievement(self):
        self._set_stat("2048", "highest_tile", 2048)
        self.game._check_achievements()
        self.assertIn("2048_2048", self.game.save_data["achievements"])

    def test_achievement_definition_count(self):
        """Guard: ensure all 60 achievement definitions are present."""
        self.assertEqual(len(ACHIEVEMENTS), 60)

    def test_all_achievement_ids_are_unique(self):
        ids = [d[0] for d in ACHIEVEMENTS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_air_standard_all_s_unlocks(self):
        """16 missions, all S rank."""
        ratings = self.game.save_data["progress"]["air"]["ratings"]["standard"]
        for i in range(1, 17):
            ratings[str(i)] = {"rank": "S"}
        self.game._check_achievements()
        self.assertIn("air_all_s", self.game.save_data["achievements"])

    def test_air_standard_all_s_fails_if_one_is_A(self):
        ratings = self.game.save_data["progress"]["air"]["ratings"]["standard"]
        for i in range(1, 17):
            ratings[str(i)] = {"rank": "S"}
        ratings["8"] = {"rank": "A"}
        self.game._check_achievements()
        self.assertNotIn("air_all_s", self.game.save_data["achievements"])

    def test_air_standard_all_s_fails_if_less_than_sixteen(self):
        ratings = self.game.save_data["progress"]["air"]["ratings"]["standard"]
        for i in range(1, 16):
            ratings[str(i)] = {"rank": "S"}
        self.game._check_achievements()
        self.assertNotIn("air_all_s", self.game.save_data["achievements"])

    def test_tank_sharpshooter(self):
        """accurate_matches: hit at least half of 10+ shots."""
        self._set_stat("tank", "accurate_matches", 1)
        self.game._check_achievements()
        self.assertIn("tank_sharpshooter", self.game.save_data["achievements"])

    def test_tank_first_clash(self):
        self._set_stat("tank", "matches_completed", 1)
        self.game._check_achievements()
        self.assertIn("tank_first_clash", self.game.save_data["achievements"])

    def test_tank_iron_will(self):
        self._set_stat("tank", "iron_will_kills", 1)
        self.game._check_achievements()
        self.assertIn("tank_iron_will", self.game.save_data["achievements"])

    def test_tank_arena_legend(self):
        self._set_stat("tank", "matches_completed", 50)
        self.game._check_achievements()
        self.assertIn("tank_arena_legend", self.game.save_data["achievements"])


if __name__ == "__main__":
    unittest.main()
