"""Regression tests for run-state value semantics (remediation R-03).

Run-state snapshots used to hold live references: the mines capture returned
``self.mines_grid`` itself, and the gomoku/air restore paths assigned the stored
objects straight into live game state.  Playing therefore mutated the in-memory
save data.

Note on severity: no user-visible failure could be reproduced from this before
the fix, because escaping a game rewrites the snapshot and clearing a run state
detaches it.  The tests below pin the invariant itself — a snapshot must be a
value — which is also what makes the R-04 validation layer meaningful.
"""

from __future__ import annotations

import copy

from _game_fixture import GameSaveTestCase


class MinesSnapshotValueTests(GameSaveTestCase):
    def _started_mines(self):
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)
        return game

    def test_capture_is_not_an_alias_of_the_live_board(self):
        game = self._started_mines()
        snapshot = game._capture_mines_run_state()
        before = copy.deepcopy(snapshot)

        game.mines_revealed[0][0] = not game.mines_revealed[0][0]
        game.mines_flags[1][1] = not game.mines_flags[1][1]
        game.mines_grid[2][2] = 42

        self.assertEqual(snapshot, before, "playing must not mutate the snapshot")

    def test_restore_is_not_an_alias_of_the_stored_snapshot(self):
        game = self._started_mines()
        state = game._capture_mines_run_state()
        stored_before = copy.deepcopy(state)

        game._start_mines_game(restore_state=state)
        game.mines_revealed[0][0] = not game.mines_revealed[0][0]
        game.mines_grid[3][3] = 7

        self.assertEqual(
            state, stored_before,
            "playing a restored game must not mutate the snapshot it came from",
        )

    def test_a_restored_game_plays_independently_of_the_snapshot(self):
        game = self._started_mines()
        state = game._capture_mines_run_state()
        # Pick a cell the flood fill definitely did not open, so the assertion
        # does not depend on where the mines happened to land.
        r, c = next(
            (r, c)
            for r in range(game.mines_size)
            for c in range(game.mines_size)
            if not game.mines_revealed[r][c]
        )

        game._start_mines_game(restore_state=state)
        game.mines_revealed[r][c] = True

        self.assertFalse(
            state["revealed"][r][c],
            "playing a restored game must not write through to the snapshot",
        )


class GomokuSnapshotValueTests(GameSaveTestCase):
    def test_restore_is_not_an_alias_of_the_stored_snapshot(self):
        game = self.start_gomoku()
        game.board.place_stone(7, 7)
        state = game._capture_gomoku_run_state()
        stored_before = copy.deepcopy(state)

        game._start_new_game(restore_state=state)
        game.board.place_stone(0, 0)

        self.assertEqual(
            state, stored_before,
            "playing a restored game must not mutate the snapshot it came from",
        )

    def test_capture_is_not_an_alias_of_the_live_board(self):
        game = self.start_gomoku()
        game.board.place_stone(7, 7)
        snapshot = game._capture_gomoku_run_state()
        before = copy.deepcopy(snapshot)

        game.board.place_stone(8, 8)
        game.board.win_stones.append((99, 99))

        self.assertEqual(snapshot, before, "playing must not mutate the snapshot")


class AirSnapshotValueTests(GameSaveTestCase):
    def test_capture_is_not_an_alias_of_live_combat_state(self):
        game = self.game
        game.air_player = {"x": 100.0, "y": 200.0}
        game.air_enemies = [{"x": 1.0, "hp": 3}]
        game.air_bullets = [{"x": 5.0}]
        game.air_loadout = {"cannon": 2, "spread": 0, "laser": 0, "active": "cannon"}

        snapshot = game._capture_air_run_state()
        before = copy.deepcopy(snapshot)

        game.air_player["x"] = 999.0
        game.air_enemies[0]["hp"] = 0
        game.air_bullets.append({"x": 6.0})
        game.air_loadout["cannon"] = 5

        self.assertEqual(snapshot, before, "playing must not mutate the snapshot")
