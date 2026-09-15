"""Regression tests for the Gomoku win-counter drift (remediation R-01).

``statistics.gomoku`` drives achievements and completion, while the instance
attributes (``black_wins`` / ``white_wins`` / ``draws``) are what the UI reads.
They used to be updated in two separate places, and ``_do_undo`` rolled back
only the display side — so a single undo left a win counted twice in
achievement progress and once on screen, permanently.
"""

from __future__ import annotations

from _game_fixture import GameSaveTestCase

from meridian.system import ACHIEVEMENTS


def _definition(achievement_id):
    for definition in ACHIEVEMENTS:
        if definition[0] == achievement_id:
            return definition
    raise KeyError(achievement_id)


class GomokuWinCounterTests(GameSaveTestCase):
    def _place(self, cells):
        """Place an alternating sequence of (row, col); every stone must land.

        ``Board.place_stone`` returns False on an occupied cell and silently
        stops alternating, so asserting here keeps the fixtures honest.
        """
        for row, col in cells:
            self.assertTrue(
                self.game.board.place_stone(row, col),
                f"stone rejected at {(row, col)}",
            )

    def _play_black_win(self):
        """Play a genuine black five-in-a-row and run the win accounting."""
        game = self.start_gomoku()
        self._place([(0, 0), (1, 0), (0, 1), (1, 1), (0, 2),
                     (1, 2), (0, 3), (1, 3), (0, 4)])
        self.assertEqual(game.board.winner, 1)
        game._on_win()
        return game

    def _statistics(self):
        return self.game.save_data["statistics"]["gomoku"]

    # ── the counter split ────────────────────────────────────────────────

    def test_win_records_one_count_on_both_sides(self):
        self._play_black_win()
        self.assertEqual(self.game.black_wins, 1)
        self.assertEqual(self._statistics()["black_wins"], 1)

    def test_undo_rolls_back_display_and_statistics_together(self):
        self._play_black_win()
        self.game._do_undo()

        self.assertEqual(self.game.black_wins, 0)
        self.assertEqual(self._statistics()["black_wins"], 0)

    def test_win_undo_win_keeps_the_two_sides_equal(self):
        """The original defect: after undo, a second win double-counted."""
        self._play_black_win()
        self.game._do_undo()
        self._play_black_win()

        self.assertEqual(self.game.black_wins, self._statistics()["black_wins"])
        self.assertEqual(self.game.black_wins, 1)

    def test_white_win_counter_stays_equal_and_rolls_back(self):
        game = self.start_gomoku()
        # Black is scattered so it never lines up; white takes all of row 1.
        self._place([(0, 0), (1, 0), (0, 2), (1, 1), (0, 4),
                     (1, 2), (2, 0), (1, 3), (2, 2), (1, 4)])
        self.assertEqual(game.board.winner, 2)

        game._on_win()
        self.assertEqual(game.white_wins, 1)
        self.assertEqual(self._statistics()["white_wins"], 1)

        game._do_undo()
        self.assertEqual(game.white_wins, 0)
        self.assertEqual(self._statistics()["white_wins"], 0)

    def test_draw_counter_stays_equal_and_rolls_back(self):
        game = self.start_gomoku()
        game.board.place_stone(0, 0)      # a real move, so undo has something to pop
        game.board.winner = -1            # force the drawn outcome
        game._on_win()

        self.assertEqual(game.draws, 1)
        self.assertEqual(self._statistics()["draws"], 1)

        game._do_undo()
        self.assertEqual(game.draws, 0)
        self.assertEqual(self._statistics()["draws"], 0)

    def test_counters_never_go_negative_on_repeated_undo(self):
        self._play_black_win()
        self.game._do_undo()
        self.game._do_undo()            # second undo has nothing to roll back

        self.assertEqual(self.game.black_wins, 0)
        self.assertEqual(self._statistics()["black_wins"], 0)

    # ── the source of truth ──────────────────────────────────────────────

    def test_counters_load_from_statistics_not_records(self):
        self.game.save_data["statistics"]["gomoku"]["black_wins"] = 7
        self.game.save_data["records"]["gomoku"]["black_wins"] = 99
        self.game._apply_loaded_data()

        self.assertEqual(self.game.black_wins, 7)

    def test_counters_survive_a_restart(self):
        self._play_black_win()
        self.save_and_restart()

        self.assertEqual(self.game.black_wins, 1)
        self.assertEqual(self._statistics()["black_wins"], 1)

    def test_records_mirror_is_still_written_for_save_shape(self):
        self._play_black_win()
        self.game._save_now()

        mirror = self.game.save_data["records"]["gomoku"]
        self.assertEqual(mirror["black_wins"], 1)

    # ── achievement semantics (decision D1 = A) ──────────────────────────

    def test_undo_keeps_the_unlocked_achievement_but_lowers_progress(self):
        self._play_black_win()
        self.assertIn("gomoku_first_win", self.game.save_data["achievements"])

        self.game._do_undo()

        self.assertIn(
            "gomoku_first_win", self.game.save_data["achievements"],
            "an unlocked achievement must not be recalled by an undo",
        )
        progress, target = self.game._achievement_progress(
            _definition("gomoku_first_win")
        )
        self.assertEqual(target, 1)
        self.assertEqual(progress, 0, "the progress value should roll back")

    def test_redo_after_undo_does_not_unlock_twice(self):
        self._play_black_win()
        first = self.game.save_data["achievements"]["gomoku_first_win"]

        self.game._do_undo()
        self._play_black_win()

        self.assertEqual(
            self.game.save_data["achievements"]["gomoku_first_win"], first,
            "re-winning must not rewrite the original unlock timestamp",
        )
