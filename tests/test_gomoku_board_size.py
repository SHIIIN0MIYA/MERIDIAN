"""Regression tests for the 19x19 board achievement (remediation R-05).

``_on_win`` used to judge the board from ``self.board_size``, which is the
*preference* that applies to the next game.  It can be changed from the settings
page mid-game without the board being rebuilt, so winning a 15x15 game after
switching the preference to 19 wrongly granted ``gomoku_19_win``.
"""

from __future__ import annotations

from _game_fixture import GameSaveTestCase


class GomokuWinsOn19Tests(GameSaveTestCase):
    def _statistics(self):
        return self.game.save_data["statistics"]["gomoku"]

    def _play_black_win_on_the_loaded_board(self):
        """Five in a row along the top row of whatever board is loaded."""
        game = self.game
        for col in range(5):
            self.assertTrue(
                game.board.place_stone(0, col), f"stone rejected at {(0, col)}"
            )
            if col < 4:
                self.assertTrue(game.board.place_stone(1, col))
        self.assertEqual(game.board.winner, 1)
        game._on_win()

    def test_mid_game_size_change_does_not_grant_the_achievement(self):
        game = self.game
        game._start_new_game()
        self.assertEqual(game.board.board_count, 15)

        game.board_size = 19        # the preference changes; the board does not

        self._play_black_win_on_the_loaded_board()

        self.assertEqual(game.board.board_count, 15)
        self.assertEqual(
            self._statistics()["wins_on_19"], 0,
            "a 15x15 win must not count towards the 19x19 statistic",
        )
        self.assertNotIn("gomoku_19_win", game.save_data["achievements"])

    def test_a_genuine_19_board_win_still_grants_the_achievement(self):
        game = self.game
        game.board_size = 19
        game._start_new_game()
        self.assertEqual(game.board.board_count, 19)

        self._play_black_win_on_the_loaded_board()

        self.assertEqual(self._statistics()["wins_on_19"], 1)
        self.assertIn("gomoku_19_win", game.save_data["achievements"])

    def test_a_13_board_win_does_not_grant_the_achievement(self):
        game = self.game
        game.board_size = 13
        game._start_new_game()
        self.assertEqual(game.board.board_count, 13)

        self._play_black_win_on_the_loaded_board()

        self.assertEqual(self._statistics()["wins_on_19"], 0)
