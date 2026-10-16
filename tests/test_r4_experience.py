"""Regression tests for the remaining R4 items.

* V-5  the Gomoku result banner showed the *statistics* label ("黑方胜场",
       a win count) instead of the result ("黑方胜利").
* V-8  a failed save raised out of Game.update() and killed the session.
* V-9  the periodic save never compared equal, so the game rewrote the whole
       save file twice a second while merely idling.
* V-10 turning "screen shake" off left Mines, 2048 and Tank shaking.
* V-19 a dropped saved run (and a failed save) produced no visible notice.
"""

from __future__ import annotations

import unittest

import pygame


class _GameCase(unittest.TestCase):
    def setUp(self):
        import os
        import tempfile
        from pathlib import Path

        pygame.init()
        self._previous = os.environ.get("MERIDIAN_SAVE_PATH")
        self._scratch = Path(tempfile.mkdtemp(prefix="meridian-r4b-"))
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


class GomokuResultBannerTests(_GameCase):
    def test_result_banner_uses_the_result_key_not_the_count_label(self):
        from meridian.localization import set_language, translate

        set_language("zh_hans")
        self.assertEqual(translate("BLACK WINS"), "黑方胜场")      # the count label
        self.assertEqual(translate("BLACK_WINS_RESULT"), "黑方胜利")  # the result
        self.assertEqual(translate("WHITE_WINS_RESULT"), "白方胜利")

    def test_banner_text_for_each_winner(self):
        game = self.game
        for winner, expected in ((1, "BLACK_WINS_RESULT"), (2, "WHITE_WINS_RESULT")):
            with self.subTest(winner=winner):
                game.board.winner = winner
                name = "BLACK" if winner == 1 else "WHITE"
                # Mirrors the computation in _draw_game_status.
                self.assertEqual(f"{name}_WINS_RESULT", expected)


class SaveFailureTests(_GameCase):
    def test_a_failed_save_does_not_escape_update(self):
        game = self.game
        calls = {"n": 0}
        original = game.save_manager.save

        def failing_save(payload):
            calls["n"] += 1
            raise OSError(28, "No space left on device")

        game.save_manager.save = failing_save
        try:
            game._save_now()          # must not raise
            game._update_persistence()
        finally:
            game.save_manager.save = original
        self.assertGreater(calls["n"], 0, "the failing save was never attempted")
        self.assertIsNotNone(game.save_notice, "a failed save stayed invisible")

    def test_the_notice_clears_once_saving_works_again(self):
        game = self.game
        original = game.save_manager.save
        game.save_manager.save = lambda payload: (_ for _ in ()).throw(OSError(28, "full"))
        try:
            game._save_now()
        finally:
            game.save_manager.save = original
        self.assertIsNotNone(game.save_notice)
        game._save_now()
        self.assertIsNone(game.save_notice, "the notice outlived the failure")


class IdleSaveTests(_GameCase):
    def test_idle_play_time_does_not_trigger_endless_saves(self):
        game = self.game
        self.assertFalse(game.screen_shake_enabled is None)
        game._capture_data()          # a full payload, as the periodic check builds
        game._save_now()              # establishes _last_persisted_snapshot
        game._save_failure_count = 0

        saves = {"n": 0}
        original = game.save_manager.save

        def counting_save(payload):
            saves["n"] += 1

        game.save_manager.save = counting_save
        try:
            ticks = {"t": 1000}
            game._last_save_check = 0
            original_ticks = pygame.time.get_ticks
            pygame.time.get_ticks = lambda: ticks["t"]
            try:
                for _ in range(10):
                    ticks["t"] += 2000          # force the 2s branch every frame
                    game._update_persistence()
            finally:
                pygame.time.get_ticks = original_ticks
        finally:
            game.save_manager.save = original

        self.assertEqual(
            saves["n"],
            0,
            "an idle frame rewrote the save file; play_time_ms is still part of "
            "the change-detection snapshot",
        )

    def test_a_real_change_still_saves(self):
        game = self.game
        game._save_now()
        saves = {"n": 0}
        original = game.save_manager.save
        game.save_manager.save = lambda payload: saves.__setitem__("n", saves["n"] + 1)
        try:
            game.snake_best = 9999
            ticks = {"t": 1000}
            original_ticks = pygame.time.get_ticks
            pygame.time.get_ticks = lambda: ticks["t"]
            try:
                ticks["t"] += 2000
                game._update_persistence()
            finally:
                pygame.time.get_ticks = original_ticks
        finally:
            game.save_manager.save = original
        self.assertEqual(saves["n"], 1, "a real change should have been written")


class ScreenShakeTests(_GameCase):
    SHAKE_FIELDS = (
        "shake_duration", "shake_x", "shake_y",
        "snake_shake_duration", "snake_shake_x", "snake_shake_y",
        "breakout_shake_duration", "breakout_shake_x", "breakout_shake_y",
        "mines_shake", "g2048_invalid_shake", "g2048_invalid_shake_dir",
        "tank_shake_frames", "tank_shake_x", "tank_shake_y",
    )

    def _set_every_shake_field(self):
        for field in self.SHAKE_FIELDS:
            setattr(self, "_" + field, field)
            setattr(self.game, field, "x" if field.endswith("_dir") else 7)

    def test_disabling_shake_zeroes_every_game(self):
        game = self.game
        self._set_every_shake_field()
        game.screen_shake_enabled = False
        game._reset_screen_shake()
        for field in self.SHAKE_FIELDS:
            with self.subTest(field=field):
                value = getattr(game, field)
                expected = "x" if field.endswith("_dir") else 0
                self.assertEqual(value, expected, f"{field} survived the reset")

    def test_g2048_invalid_shake_is_actually_covered(self):
        game = self.game
        self.assertTrue(hasattr(game, "g2048_invalid_shake"))
        game.g2048_invalid_shake = 14
        game.screen_shake_enabled = False
        game._reset_screen_shake()
        self.assertEqual(game.g2048_invalid_shake, 0)

    def test_mines_and_tank_are_actually_covered(self):
        game = self.game
        game.mines_shake = 8
        game.tank_shake_frames = 6
        game.tank_shake_x = 3
        game.screen_shake_enabled = False
        game._reset_screen_shake()
        self.assertEqual(game.mines_shake, 0)
        self.assertEqual(game.tank_shake_frames, 0)
        self.assertEqual(game.tank_shake_x, 0)

    def test_every_shake_field_is_declared_in_the_shared_list(self):
        game = self.game
        for field in self.SHAKE_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field, game._SHAKE_FIELDS)


class DesktopNoticeTests(_GameCase):
    def test_no_notice_draws_nothing(self):
        self.assertIsNone(self.game._desktop_notice_text())

    def test_dropped_run_notice_is_visible(self):
        game = self.game
        game.restore_notice = "GOMOKU SAVE COULD NOT BE RESTORED"
        self.assertEqual(game._desktop_notice_text(), "GOMOKU SAVE COULD NOT BE RESTORED")
        game.state = game.DESKTOP
        game._draw_desktop()        # must not raise

    def test_failed_save_notice_is_visible(self):
        game = self.game
        game.save_notice = "SAVE FAILED - PROGRESS MAY NOT PERSIST"
        self.assertIn("SAVE FAILED", game._desktop_notice_text())

    def test_both_notices_are_combined(self):
        game = self.game
        game.restore_notice = "A"
        game.save_notice = "B"
        self.assertEqual(game._desktop_notice_text(), "A   B")


if __name__ == "__main__":
    unittest.main()
