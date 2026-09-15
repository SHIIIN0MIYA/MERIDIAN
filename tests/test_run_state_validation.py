"""Tests for run-state validation (remediation R-04).

Two layers:

* ``Validate*`` classes are pure unit tests over ``runstate.validate`` — fast,
  no ``Game`` needed, and they cover the malformed-input matrix.
* ``LoadLoop*`` / ``SettingChange*`` classes drive the real restore path in
  ``_apply_loaded_data`` and the settings page.
"""

from __future__ import annotations

import json
import unittest

from _game_fixture import GameSaveTestCase

from meridian.runstate import RunStateVerdict, validate


# ---------------------------------------------------------------------------
# Gomoku
# ---------------------------------------------------------------------------

def _gomoku_state(size=15, stones=((7, 7, 1), (7, 8, 2), (8, 8, 1)), **overrides):
    grid = [[0] * size for _ in range(size)]
    history = []
    for row, col, player in stones:
        grid[row][col] = player
        history.append([row, col, player])
    state = {
        "format": 1, "board_count": size, "grid": grid,
        "move_history": history, "move_count": len(history),
        "current_player": 2, "winner": 0, "last_move": [8, 8],
        "win_stones": [],
    }
    state.update(overrides)
    return state


class ValidateGomokuTests(unittest.TestCase):
    def test_a_healthy_state_is_resumable(self):
        self.assertIs(validate("gomoku", _gomoku_state()), RunStateVerdict.RESUMABLE)

    def test_a_pre_format_snapshot_is_rejected(self):
        state = _gomoku_state()
        del state["format"]
        self.assertIs(validate("gomoku", state), RunStateVerdict.REJECTED)

    def test_a_size_mismatch_is_rejected(self):
        """The reproducible defect: a 19x19 grid declared as 15x15."""
        state = _gomoku_state()
        state["grid"] = [[0] * 19 for _ in range(19)]
        self.assertIs(validate("gomoku", state), RunStateVerdict.REJECTED)

    def test_a_ragged_grid_is_rejected(self):
        state = _gomoku_state()
        state["grid"][3] = [0] * 5
        self.assertIs(validate("gomoku", state), RunStateVerdict.REJECTED)

    def test_a_wrong_cell_type_is_rejected(self):
        state = _gomoku_state()
        state["grid"][0][0] = "x"
        self.assertIs(validate("gomoku", state), RunStateVerdict.REJECTED)

    def test_a_bool_is_not_accepted_as_a_cell(self):
        state = _gomoku_state()
        state["grid"][0][0] = True
        self.assertIs(validate("gomoku", state), RunStateVerdict.REJECTED)

    def test_a_move_count_mismatch_is_rejected(self):
        state = _gomoku_state()
        state["move_count"] = 99
        self.assertIs(validate("gomoku", state), RunStateVerdict.REJECTED)

    def test_history_disagreeing_with_the_grid_is_rejected(self):
        state = _gomoku_state()
        state["grid"][7][7] = 0        # the recorded stone is not there
        self.assertIs(validate("gomoku", state), RunStateVerdict.REJECTED)

    def test_an_out_of_range_move_is_rejected(self):
        state = _gomoku_state()
        state["move_history"] = [[99, 0, 1]]
        state["move_count"] = 1
        self.assertIs(validate("gomoku", state), RunStateVerdict.REJECTED)

    def test_a_finished_game_is_completed(self):
        self.assertIs(
            validate("gomoku", _gomoku_state(winner=1)),
            RunStateVerdict.COMPLETED,
        )
        self.assertIs(
            validate("gomoku", _gomoku_state(winner=-1)),
            RunStateVerdict.COMPLETED,
        )

    def test_an_untouched_board_is_completed_not_rejected(self):
        """Nothing to continue — clear it quietly rather than warn."""
        state = _gomoku_state(stones=())
        self.assertIs(validate("gomoku", state), RunStateVerdict.COMPLETED)

    def test_list_and_tuple_moves_are_both_accepted(self):
        """JSON turns stored tuples into lists."""
        state = _gomoku_state()
        state["move_history"] = [tuple(entry) for entry in state["move_history"]]
        self.assertIs(validate("gomoku", state), RunStateVerdict.RESUMABLE)


# ---------------------------------------------------------------------------
# Minesweeper
# ---------------------------------------------------------------------------

def _mines_state(size=9, count=10, **overrides):
    grid = [[0] * size for _ in range(size)]
    placed = 0
    for row in range(size):
        for col in range(size):
            if placed < count:
                grid[row][col] = -1
                placed += 1
    state = {
        "format": 1, "size": size, "mines_count": count, "grid": grid,
        "revealed": [[False] * size for _ in range(size)],
        "flags": [[False] * size for _ in range(size)],
        "started": True, "elapsed_ms": 0,
        "revealed_count": 0, "flags_count": 0,
    }
    state.update(overrides)
    return state


class ValidateMinesTests(unittest.TestCase):
    def test_a_healthy_state_is_resumable(self):
        self.assertIs(validate("mines", _mines_state()), RunStateVerdict.RESUMABLE)

    def test_a_size_mismatch_is_rejected(self):
        """The reproducible crash: a 16x16 grid declared as 9x9."""
        state = _mines_state(size=9)
        state["grid"] = [[0] * 16 for _ in range(16)]
        self.assertIs(validate("mines", state), RunStateVerdict.REJECTED)

    def test_a_revealed_grid_of_the_wrong_shape_is_rejected(self):
        state = _mines_state()
        state["revealed"] = [[False] * 4 for _ in range(4)]
        self.assertIs(validate("mines", state), RunStateVerdict.REJECTED)

    def test_a_flags_grid_of_the_wrong_shape_is_rejected(self):
        state = _mines_state()
        del state["flags"]
        self.assertIs(validate("mines", state), RunStateVerdict.REJECTED)

    def test_a_non_boolean_revealed_cell_is_rejected(self):
        state = _mines_state()
        state["revealed"][0][0] = 1
        self.assertIs(validate("mines", state), RunStateVerdict.REJECTED)

    def test_a_mine_count_mismatch_is_rejected(self):
        state = _mines_state(count=10)
        state["mines_count"] = 3
        self.assertIs(validate("mines", state), RunStateVerdict.REJECTED)

    def test_an_uncovered_mine_is_completed(self):
        state = _mines_state()
        state["revealed"][0][0] = True      # (0,0) is a mine in this fixture
        self.assertIs(validate("mines", state), RunStateVerdict.COMPLETED)

    def test_all_safe_cells_revealed_is_completed(self):
        state = _mines_state(size=6, count=4)
        for row in range(6):
            for col in range(6):
                if state["grid"][row][col] != -1:
                    state["revealed"][row][col] = True
        self.assertIs(validate("mines", state), RunStateVerdict.COMPLETED)


# ---------------------------------------------------------------------------
# Robustness
# ---------------------------------------------------------------------------

class ValidateRobustnessTests(unittest.TestCase):
    def test_junk_never_raises(self):
        junk = (None, [], "x", 5, 3.5, {"grid": "x"}, {"format": 1},
                {"format": 1, "board_count": "15"},
                {"format": 1, "board_count": 15, "grid": None},
                {"format": 1, "size": 9, "mines_count": 10, "grid": [[None]]})
        for game_id in ("gomoku", "mines", "snake", "tetris", "air", "tank"):
            for value in junk:
                with self.subTest(game_id=game_id, value=repr(value)[:24]):
                    self.assertIsInstance(validate(game_id, value), RunStateVerdict)

    def test_other_games_accept_a_snapshot_with_the_expected_keys(self):
        self.assertIs(
            validate("snake", {"body": [], "dir": [1, 0], "next_dir": [1, 0],
                              "food": None, "score": 0, "move_timer": 0}),
            RunStateVerdict.RESUMABLE,
        )

    def test_other_games_reject_a_snapshot_missing_a_required_key(self):
        self.assertIs(
            validate("snake", {"body": [], "score": 0}),
            RunStateVerdict.REJECTED,
        )

    def test_tank_is_left_to_its_own_validator(self):
        self.assertIs(validate("tank", {"anything": 1}), RunStateVerdict.RESUMABLE)


# ---------------------------------------------------------------------------
# The real load path
# ---------------------------------------------------------------------------

class LoadLoopTests(GameSaveTestCase):
    def _corrupt_stored_run_state(self, game_id, mutate):
        """Save, mutate the run state on disk, then reload like a fresh launch."""
        game = self.game
        game._save_now()
        payload = json.loads(self.save_path.read_text(encoding="utf-8"))
        mutate(payload["progress"][game_id]["run_state"])
        self.save_path.write_text(json.dumps(payload), encoding="utf-8")

        game.save_data = game.save_manager.load()
        game._pending_run_states.clear()
        game._apply_loaded_data()
        return game

    def test_a_healthy_gomoku_run_still_restores(self):
        game = self.start_gomoku()
        game.board.place_stone(7, 7)

        self.assert_run_state_survives_restart("gomoku")
        self.assertIsNone(game.restore_notice)

    def test_a_healthy_mines_run_still_restores(self):
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)

        self.assert_run_state_survives_restart("mines")
        self.assertIsNone(game.restore_notice)

    def test_a_19_board_snapshot_in_a_15_game_is_rejected_not_misplaced(self):
        game = self.start_gomoku()
        game.board.place_stone(7, 7)

        def mutate(state):
            state["board_count"] = 19
            state["grid"] = [[0] * 19 for _ in range(19)]

        self._corrupt_stored_run_state("gomoku", mutate)

        self.assertIsNone(self.pending_run_state("gomoku"))
        self.assertFalse(self.progress("gomoku")["run_active"])
        self.assertIsNotNone(game.restore_notice)
        self.assertIn("GOMOKU", game.restore_notice)

    def test_a_ragged_mines_snapshot_is_rejected_without_raising(self):
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)

        self._corrupt_stored_run_state(
            "mines", lambda state: state["revealed"].pop()
        )

        self.assertIsNone(self.pending_run_state("mines"))
        self.assertFalse(self.progress("mines")["run_active"])
        self.assertIn("MINES", game.restore_notice)

    def test_a_mines_snapshot_from_another_size_is_rejected(self):
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)

        def mutate(state):
            state["size"] = 16
            state["grid"] = [[0] * 16 for _ in range(16)]

        self._corrupt_stored_run_state("mines", mutate)

        self.assertIsNone(self.pending_run_state("mines"))
        self.assertIn("MINES", game.restore_notice)

    def test_a_completed_run_is_cleared_without_a_notice(self):
        game = self.start_gomoku()
        game.board.place_stone(7, 7)

        self._corrupt_stored_run_state("gomoku", lambda state: state.update(winner=1))

        self.assertIsNone(self.pending_run_state("gomoku"))
        self.assertFalse(self.progress("gomoku")["run_active"])
        self.assertIsNone(
            game.restore_notice,
            "a finished run is normal, not an error worth reporting",
        )


class SettingChangeTests(GameSaveTestCase):
    def test_changing_the_gomoku_size_mid_game_drops_the_run(self):
        game = self.start_gomoku()
        game.board.place_stone(7, 7)
        game._save_now()
        self.assertTrue(self.progress("gomoku")["run_active"])

        game._activate_system_setting("cycle_gomoku")

        self.assertFalse(self.progress("gomoku")["run_active"])
        self.assertIsNone(self.progress("gomoku")["run_state"])
        self.assertNotEqual(game.board.board_count, game.board_size)

    def test_changing_the_gomoku_size_before_moving_still_resizes_the_board(self):
        game = self.start_gomoku()

        game._activate_system_setting("cycle_gomoku")

        self.assertEqual(game.board.board_count, game.board_size)

    def test_changing_the_mines_mode_drops_the_run(self):
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)
        game._save_now()
        self.assertTrue(self.progress("mines")["run_active"])

        game._activate_system_setting("cycle_mines")

        self.assertFalse(self.progress("mines")["run_active"])
        self.assertIsNone(self.progress("mines")["run_state"])


# ---------------------------------------------------------------------------
# The snapshot must agree with the current settings
# ---------------------------------------------------------------------------

class ExpectedGeometryTests(unittest.TestCase):
    """Internal consistency alone is not enough: the setting can change."""

    def test_matching_settings_are_accepted(self):
        self.assertIs(
            validate("mines", _mines_state(size=9, count=10),
                     expected_size=9, expected_count=10),
            RunStateVerdict.RESUMABLE,
        )

    def test_a_smaller_boards_than_the_mode_is_rejected(self):
        self.assertIs(
            validate("mines", _mines_state(size=9, count=10),
                     expected_size=16, expected_count=40),
            RunStateVerdict.REJECTED,
        )

    def test_a_changed_mine_count_is_rejected(self):
        self.assertIs(
            validate("mines", _mines_state(size=9, count=10),
                     expected_size=9, expected_count=15),
            RunStateVerdict.REJECTED,
        )

    def test_a_gomoku_size_mismatch_is_rejected(self):
        self.assertIs(
            validate("gomoku", _gomoku_state(size=15), expected_size=19),
            RunStateVerdict.REJECTED,
        )

    def test_omitting_the_settings_skips_only_that_check(self):
        self.assertIs(
            validate("mines", _mines_state(size=9)),
            RunStateVerdict.RESUMABLE,
        )


class CrossSessionGeometryTests(GameSaveTestCase):
    """The reproducible crash: a run saved in one mode, resumed in another."""

    def _reload_with_settings(self, settings):
        game = self.game
        game._save_now()
        payload = json.loads(self.save_path.read_text(encoding="utf-8"))
        payload["settings"].update(settings)
        self.save_path.write_text(json.dumps(payload), encoding="utf-8")

        game.save_data = game.save_manager.load()
        game._pending_run_states.clear()
        game._apply_loaded_data()
        return game

    def test_the_reproducible_mines_crash_is_prevented(self):
        """A 9x9 run with the mode set to 16x16 used to raise IndexError.

        Old behaviour, reproduced end to end: the 9x9 board was accepted, and
        ``_reveal_mines_cell(14, 14)`` then raised
        ``IndexError: list index out of range`` because the grid was indexed
        with the setting's size.
        """
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)

        self._reload_with_settings({"mines_size": 16, "mines_count": 40})

        self.assertEqual(game.mines_size, 16)
        self.assertIsNone(
            self.pending_run_state("mines"),
            "the mismatched board must not be offered, or resuming it would crash",
        )
        self.assertFalse(self.progress("mines")["run_active"])
        self.assertIn("MINES", game.restore_notice)

    def test_a_mines_run_from_a_leaner_mode_is_rejected(self):
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)

        self._reload_with_settings({"mines_count": 15})

        self.assertIsNone(self.pending_run_state("mines"))

    def test_a_gomoku_run_from_another_board_size_is_rejected(self):
        game = self.start_gomoku()
        game.board.place_stone(7, 7)

        self._reload_with_settings({"gomoku_board_size": 19})

        self.assertIsNone(self.pending_run_state("gomoku"))
        self.assertIn("GOMOKU", game.restore_notice)

    def test_a_run_matching_the_settings_still_restores(self):
        game = self.start_gomoku()
        game.board.place_stone(7, 7)

        self._reload_with_settings({"gomoku_board_size": 15})

        self.assertIsNotNone(self.pending_run_state("gomoku"))
        self.assertIsNone(game.restore_notice)
