"""Regression tests for R4: D2 (air restore leak) and D3 (breakout perfect level).

D2 -- `_air_restore_state` was cleared only where it was consumed, so abandoning
a CONTINUE on the brief page left it armed.  The next NEW CAMPAIGN / LEVEL
SELECT / BOSS RUSH then silently resumed the old run's score, health and enemy
list.  Worse, a snapshot taken between waves legitimately has an empty enemy
list, so restoring it into a boss stage satisfied
`if boss and not enemies: _finish_air(True)` on the very first frame -- a free
MISSION CLEAR on every boss stage.

D3 -- `_start_breakout_game` overwrote `breakout_level_start_lives` with the
restored lives, so a level cleared after losing a life still counted as
"perfect" if it was resumed through CONTINUE, re-earning the achievement.
"""

from __future__ import annotations

import unittest

import pygame

from meridian.arcade_levels import AIR_LEVELS


class _GameCase(unittest.TestCase):
    def setUp(self):
        import os
        import tempfile
        from pathlib import Path

        pygame.init()
        self._previous = os.environ.get("MERIDIAN_SAVE_PATH")
        self._scratch = Path(tempfile.mkdtemp(prefix="meridian-r4-"))
        os.environ["MERIDIAN_SAVE_PATH"] = str(self._scratch / "save.json")
        from meridian.app import Game

        self.game = Game()

    def tearDown(self):
        import os
        import shutil

        self.game.audio.stop()
        pygame.quit()
        if self._previous is None:
            os.environ.pop("MERIDIAN_SAVE_PATH", None)
        else:
            os.environ["MERIDIAN_SAVE_PATH"] = self._previous
        shutil.rmtree(self._scratch, ignore_errors=True)


class AirRestoreLeakTests(_GameCase):
    def test_new_campaign_clears_a_stale_restore_state(self):
        game = self.game
        game._air_restore_state = {"level": 4, "score": 4242, "health": 2,
                                   "enemies": [], "player": {}, "bullets": [],
                                   "missile_charge": 0, "loadout": {}}
        game._start_air_campaign("standard")
        self.assertIsNone(
            game._air_restore_state,
            "a stale snapshot survived NEW CAMPAIGN and will pollute the level",
        )

    def test_level_select_clears_a_stale_restore_state(self):
        game = self.game
        game._air_restore_state = {"level": 4, "score": 777, "health": 2,
                                   "enemies": [], "player": {}, "bullets": [],
                                   "missile_charge": 0, "loadout": {}}
        game._start_air_level(0)
        self.assertIsNone(game._air_restore_state)

    def test_boss_rush_clears_a_stale_restore_state(self):
        game = self.game
        game._air_restore_state = {"level": 4, "score": 1, "health": 2,
                                   "enemies": [], "player": {}, "bullets": [],
                                   "missile_charge": 0, "loadout": {}}
        game._start_air_boss_rush()
        self.assertIsNone(game._air_restore_state)


class FreeBossClearTests(_GameCase):
    """An empty enemy list on a boss stage must not read as "boss defeated"."""

    def _boss_level_index(self):
        return next(i for i, cfg in enumerate(AIR_LEVELS) if cfg["boss"])

    def test_boss_stage_is_not_won_before_the_boss_has_spawned(self):
        game = self.game
        game.air_mode = "standard"
        game.air_level = self._boss_level_index()
        game.air_enemies = []
        game.air_bullets = []
        game.air_enemy_bullets = []
        game.air_powerups = []
        game.air_missiles = []
        game.air_player = {"x": 100.0, "y": 100.0, "vx": 0.0, "vy": 0.0,
                           "r": 5, "cool": 0, "shield": 0, "invuln": 0,
                           "hit_flash": 0, "muzzle": 0}
        game._air_boss_spawned = False
        game.state = game.AIR_PLAYING
        game._update_air_raid()
        self.assertNotEqual(
            game.state,
            game.AIR_END,
            "a boss stage with no enemies was won without a boss ever spawning",
        )

    def test_a_real_boss_spawn_arms_the_win_condition(self):
        game = self.game
        game.air_mode = "standard"
        game.air_level = self._boss_level_index()
        game._prepare_air_level(game.air_level, preserve_loadout=True)
        game._begin_air_combat()
        self.assertTrue(
            game._air_boss_spawned,
            "spawning the boss should arm the win check",
        )
        self.assertTrue(game.air_enemies, "the boss was not spawned")


class BreakoutPerfectLevelTests(_GameCase):
    def test_losing_a_life_then_resuming_does_not_earn_a_perfect_level(self):
        game = self.game
        game._start_breakout_game()
        game.breakout_lives = 2          # one life lost on this level
        snapshot = game._capture_breakout_run_state()
        self.assertEqual(snapshot["level_start_lives"], 3)

        # Restore the way CONTINUE does.
        game._start_breakout_game(restore_state=snapshot)
        self.assertEqual(
            game.breakout_level_start_lives,
            3,
            "the restored level forgot the lives it began with",
        )

        for brick in game.breakout_bricks:
            brick["alive"] = False
        before = game.save_data["statistics"]["breakout"].get("perfect_levels", 0)
        game._update_breakout()
        after = game.save_data["statistics"]["breakout"].get("perfect_levels", 0)
        self.assertEqual(after, before, "a life was lost yet the level counted as perfect")

    def test_a_genuinely_perfect_level_still_counts(self):
        game = self.game
        game._start_breakout_game()
        for brick in game.breakout_bricks:
            brick["alive"] = False
        before = game.save_data["statistics"]["breakout"].get("perfect_levels", 0)
        game._update_breakout()
        after = game.save_data["statistics"]["breakout"].get("perfect_levels", 0)
        self.assertEqual(after, before + 1, "a clean clear should count as perfect")


class OldBreakoutBehaviourTests(_GameCase):
    """Prove the D3 fix is load-bearing by restoring the old assignment."""

    def test_old_assignment_grants_a_false_perfect_level(self):
        game = self.game
        game._start_breakout_game()
        game.breakout_lives = 2
        snapshot = game._capture_breakout_run_state()

        game._start_breakout_game(restore_state=snapshot)
        game.breakout_level_start_lives = game.breakout_lives   # pre-R4 behaviour
        for brick in game.breakout_bricks:
            brick["alive"] = False
        before = game.save_data["statistics"]["breakout"].get("perfect_levels", 0)
        game._update_breakout()
        after = game.save_data["statistics"]["breakout"].get("perfect_levels", 0)
        self.assertEqual(
            after,
            before + 1,
            "with the old assignment the level should wrongly count as perfect",
        )


if __name__ == "__main__":
    unittest.main()
