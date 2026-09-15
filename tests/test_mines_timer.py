"""Regression tests for the Minesweeper timer (remediation R-02).

The timer used to be an absolute ``pygame.time.get_ticks()`` value persisted in
the save file.  ``get_ticks()`` restarts near zero in a new process, so a
restored run computed ``now - saved_tick`` and produced a large negative
elapsed time — which the win path then wrote into the best-time table as an
unbreakable record.
"""

from __future__ import annotations

from _game_fixture import GameSaveTestCase


class MinesTimerTests(GameSaveTestCase):
    def _started_run(self):
        """Start a real game and return its captured run state."""
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)      # generates the board and starts the clock
        self.assertTrue(game.mines_started, "the timer should be running")
        return game._capture_mines_run_state()

    def _mode_key(self):
        return (self.game.mines_size, self.game.mines_count)

    def _reveal_all_safe_cells(self):
        """Satisfy the real win condition: every non-mine cell revealed."""
        game = self.game
        game.mines_revealed_count = 0
        for r in range(game.mines_size):
            for c in range(game.mines_size):
                if game.mines_grid[r][c] == -1:
                    continue
                game.mines_revealed[r][c] = True
                game.mines_revealed_count += 1
        game._check_mines_win()

    # ── the cross-process defect ─────────────────────────────────────────

    def test_legacy_absolute_tick_restore_does_not_produce_a_negative_clock(self):
        """A save written by the old code carried an absolute tick."""
        state = self._started_run()
        state["elapsed_ms"] = 5000
        state["start_ticks"] = 900_000     # a tick value from the previous process

        game = self.game
        game._start_mines_game(restore_state=state)
        game._update_mines_visual_effects()

        self.assertGreaterEqual(
            game.mines_elapsed_ms, 5000,
            "the restored run must resume from the saved elapsed time",
        )

    def test_captured_state_no_longer_persists_an_absolute_tick(self):
        self.assertNotIn("start_ticks", self._started_run())

    def test_elapsed_time_keeps_advancing_after_a_restore(self):
        state = self._started_run()
        state["elapsed_ms"] = 5000

        game = self.game
        game._start_mines_game(restore_state=state)
        first = game._mines_elapsed_now()
        game.mines_timer_base -= 250       # pretend 250 ms of play happened
        self.assertGreater(game._mines_elapsed_now(), first)

    def test_elapsed_time_survives_a_save_restart(self):
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)
        game.mines_elapsed_ms = 4321

        self.assert_run_state_survives_restart("mines")

        game._start_mines_game(restore_state=self.pending_run_state("mines"))
        self.assertEqual(game.mines_elapsed_ms, 4321)

    # ── the bogus best-time record ───────────────────────────────────────

    def test_negative_elapsed_never_becomes_a_best_time(self):
        state = self._started_run()
        state["elapsed_ms"] = -5000
        state["start_ticks"] = 900_000

        game = self.game
        game._start_mines_game(restore_state=state)
        self._reveal_all_safe_cells()

        self.assertTrue(game.mines_win)
        self.assertIsNone(
            game.mines_best_times.get(self._mode_key()),
            "a negative elapsed must never be recorded as a best time",
        )
        self.assertLess(game.mines_elapsed_ms, 0)

    def test_a_genuine_fast_win_is_still_recorded(self):
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)
        self._reveal_all_safe_cells()

        self.assertTrue(game.mines_win)
        recorded = game.mines_best_times.get(self._mode_key())
        self.assertIsNotNone(recorded)
        self.assertGreaterEqual(recorded, 0)

    def test_the_clock_freezes_once_the_game_ends(self):
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)
        self._reveal_all_safe_cells()
        frozen = game.mines_elapsed_ms

        game.mines_timer_base -= 5000      # five seconds of wall clock pass

        game._update_mines_visual_effects()
        self.assertEqual(game.mines_elapsed_ms, frozen)
