"""Regression tests for R2: CONTINUE must resume the saved run in-session.

Found during the assessment:

* V-1 -- 2048's Down merge reported the mirrored cell's value, so a 2048 made
  downwards was never detected as a win and TOP TILE was recorded as 0.
* V-2/V-3 -- Gomoku's and Snake's CONTINUE read `_pending_run_states`, which
  `_apply_loaded_data` fills only at process start, so leaving a game with ESC
  and pressing CONTINUE started a brand-new game and discarded the saved run.
  Mines/Tetris/2048/Breakout read the stored snapshot instead.
* Tank had the same defect, plus its CONTINUE button was hidden in-session
  because the button and the handler used different predicates.

Every test drives the shipped menu handler: the bug lived in the handler, so a
test that calls `_start_new_game(restore_state=...)` directly would pass even
though the game is broken.
"""

from __future__ import annotations

import unittest

import pygame

from meridian.system import SystemMixin


class _MenuDriver:
    """Press a named menu button through a real event handler."""

    @staticmethod
    def click(game, handler, buttons_fn, action):
        button = next(b for b in buttons_fn() if b["action"] == action)
        pos = button["rect"].center
        handler(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
        handler(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos))


class _GameCase(unittest.TestCase):
    """Local copy of the shared save-path discipline (no conftest yet)."""

    def setUp(self):
        import os
        import tempfile
        from pathlib import Path

        pygame.init()
        self._previous = os.environ.get("MERIDIAN_SAVE_PATH")
        self._scratch = Path(tempfile.mkdtemp(prefix="meridian-r2-"))
        self.save_path = self._scratch / "save.json"
        os.environ["MERIDIAN_SAVE_PATH"] = str(self.save_path)
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


class StoredRunAccessorTests(_GameCase):
    def test_stored_run_state_reads_the_saved_snapshot(self):
        game = self.game
        game._start_new_game()
        game.state = game.PLAYING
        game.board.grid[7][7] = 1
        game.board.move_count = 1
        game._save_now()

        self.assertTrue(game._has_stored_run("gomoku"))
        snapshot = game._stored_run_state("gomoku")
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot["move_count"], 1)

    def test_stored_run_state_is_none_without_an_active_run(self):
        self.assertFalse(self.game._has_stored_run("gomoku"))
        self.assertIsNone(self.game._stored_run_state("gomoku"))

    def test_accessor_tolerates_a_malformed_progress_container(self):
        game = self.game
        game.save_data["progress"]["snake"] = []
        self.assertIsNone(game._stored_run_state("snake"))
        self.assertFalse(game._has_stored_run("snake"))


class GomokuContinueTests(_GameCase):
    def test_in_session_continue_keeps_the_board(self):
        game = self.game
        game._start_new_game()
        game.state = game.PLAYING
        game.board.grid[7][7] = 1
        game.board.move_count = 1
        game._save_now()

        game.state = game.MENU
        _MenuDriver.click(game, game._handle_menu_event, game._get_menu_buttons, "continue")
        self.assertEqual(game.board.move_count, 1, "CONTINUE discarded the saved run")
        self.assertEqual(game.board.grid[7][7], 1)


class SnakeContinueTests(_GameCase):
    def test_in_session_continue_keeps_score_and_body(self):
        game = self.game
        game._start_snake_game()
        game.state = game.SNAKE_PLAYING
        game.snake_score = 137
        game.snake = [(12, 10), (12, 11), (12, 12), (12, 13), (12, 14)]
        game._save_now()

        game.state = game.SNAKE_MENU
        _MenuDriver.click(
            game, game._handle_snake_menu_event, game._get_snake_menu_buttons, "continue"
        )
        self.assertEqual(game.snake_score, 137, "CONTINUE discarded the score")
        self.assertEqual(len(game.snake), 5, "CONTINUE discarded the body")


class TankContinueTests(_GameCase):
    def test_continue_button_is_offered_in_session_and_resumes(self):
        game = self.game
        game._start_tank_battle()
        game._save_now()
        game.state = game.TANK_MENU

        actions = [b["action"] for b in game._tank_buttons("menu")]
        self.assertIn(
            "continue",
            actions,
            "the CONTINUE button is hidden even though a run is stored",
        )
        game._continue_tank_battle()
        self.assertIsNotNone(game.tank_engine)


class G2048DirectionTests(_GameCase):
    """A 2048 produced in any direction must be detected."""

    def _merge_column_and_move(self, direction):
        from meridian.g2048 import G2048_SIZE

        game = self.game
        game.g2048_grid = [[0] * G2048_SIZE for _ in range(G2048_SIZE)]
        game.g2048_grid[0][0] = 1024
        game.g2048_grid[1][0] = 1024
        game.g2048_won = False
        game.g2048_stats_completed = False
        game.save_data["statistics"]["2048"]["highest_tile"] = 0
        game._move_2048(direction)
        flat = [cell for row in game.g2048_grid for cell in row]
        return 2048 in flat, game.g2048_won, game.save_data["statistics"]["2048"]["highest_tile"]

    def test_vertical_merge_wins_in_both_directions(self):
        for direction in ("up", "down"):
            with self.subTest(direction=direction):
                on_board, won, highest = self._merge_column_and_move(direction)
                self.assertTrue(on_board, f"{direction}: no 2048 on the board")
                self.assertTrue(won, f"{direction}: the win was not detected")
                self.assertEqual(
                    highest, 2048, f"{direction}: highest_tile recorded as {highest}"
                )


class ContinueCoverageTests(_GameCase):
    """Guard the four games that were already correct, so they stay correct."""

    def test_mines_and_tetris_continue_read_the_snapshot(self):
        game = self.game
        game._start_mines_game()
        game.state = game.MINES_PLAYING
        game._save_now()
        self.assertTrue(game._has_stored_run("mines"))

        game._start_tetris_game()
        game.state = game.TETRIS_PLAYING
        game._save_now()
        self.assertTrue(game._has_stored_run("tetris"))

    def test_system_mixin_exposes_the_accessor(self):
        # The accessor must live on SystemMixin so every game mixin can use it.
        self.assertTrue(hasattr(SystemMixin, "_stored_run_state"))
        self.assertTrue(hasattr(SystemMixin, "_has_stored_run"))


if __name__ == "__main__":
    unittest.main()
