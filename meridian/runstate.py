"""Validation for stored run states.

Run states are untrusted input: they are read from disk, may come from an older
build, and a rejected state must degrade to "no saved run" rather than crash a
game or load a board of the wrong size.

Scope note: strict dimension checks are applied where a mismatch can actually
occur — Gomoku (board size is a setting) and Minesweeper (same).  The other
games have fixed board geometry, so they only get a shape check: rejecting their
snapshots would discard valid runs without buying any safety.
"""

from __future__ import annotations

from enum import Enum


RUN_STATE_FORMAT = 1

# Games whose snapshot must carry the current format marker and an explicit size.
DIMENSION_CHECKED_GAMES = ("gomoku", "mines")


class RunStateVerdict(Enum):
    RESUMABLE = "resumable"   # valid and unfinished
    COMPLETED = "completed"   # valid but the run already ended; should be cleared
    REJECTED = "rejected"     # malformed or from another format; must not be used


def _is_int(value, *, exclude_bool=True):
    if exclude_bool and isinstance(value, bool):
        return False
    return isinstance(value, int)


def _is_square_grid(value, size, allowed_values, *, bools=False):
    """A ``size`` x ``size`` list of lists holding allowed cell values."""
    if not isinstance(value, list) or len(value) != size:
        return False
    for row in value:
        if not isinstance(row, list) or len(row) != size:
            return False
        for cell in row:
            if bools:
                if not isinstance(cell, bool):
                    return False
            elif not _is_int(cell) or cell not in allowed_values:
                return False
    return True


def _validate_gomoku(state) -> RunStateVerdict:
    """Verify the board is square, sized as declared, and consistently filled."""
    size = state.get("board_count")
    if not _is_int(size) or size < 5:
        return RunStateVerdict.REJECTED
    grid = state.get("grid")
    if not _is_square_grid(grid, size, {0, 1, 2}):
        return RunStateVerdict.REJECTED

    history = state.get("move_history")
    if not isinstance(history, list) or state.get("move_count") != len(history):
        return RunStateVerdict.REJECTED
    for entry in history:
        if not isinstance(entry, (list, tuple)) or len(entry) != 3:
            return RunStateVerdict.REJECTED
        row, col, player = entry
        if not (_is_int(row) and _is_int(col) and _is_int(player)):
            return RunStateVerdict.REJECTED
        if not (0 <= row < size and 0 <= col < size) or player not in (1, 2):
            return RunStateVerdict.REJECTED
        if grid[row][col] == 0:
            return RunStateVerdict.REJECTED      # history disagrees with the grid

    if not history:
        # An untouched board has nothing to continue; clear it quietly rather
        # than offering a "continue" that resumes nothing.
        return RunStateVerdict.COMPLETED
    if state.get("current_player") not in (1, 2):
        return RunStateVerdict.REJECTED
    winner = state.get("winner")
    if winner not in (-1, 0, 1, 2):
        return RunStateVerdict.REJECTED
    if winner != 0:
        return RunStateVerdict.COMPLETED
    return RunStateVerdict.RESUMABLE


def _validate_mines(state) -> RunStateVerdict:
    """Verify the three boards share one size and that size matches the setting.

    A mismatch here is the reproducible crash: ``_reveal_mines_cell`` iterates
    ``range(self.mines_size)`` over the restored grid.
    """
    size = state.get("size")
    count = state.get("mines_count")
    if not _is_int(size) or size < 2 or not _is_int(count) or count < 1:
        return RunStateVerdict.REJECTED

    grid = state.get("grid")
    if not _is_square_grid(grid, size, set(range(-1, 9))):
        return RunStateVerdict.REJECTED
    if not _is_square_grid(state.get("revealed"), size, None, bools=True):
        return RunStateVerdict.REJECTED
    if not _is_square_grid(state.get("flags"), size, None, bools=True):
        return RunStateVerdict.REJECTED

    mines = sum(cell == -1 for row in grid for cell in row)
    if mines != count:
        return RunStateVerdict.REJECTED

    safe_cells = size * size - mines
    revealed_safe = sum(
        1
        for r in range(size)
        for c in range(size)
        if grid[r][c] != -1 and state["revealed"][r][c]
    )
    for r in range(size):
        for c in range(size):
            if grid[r][c] == -1 and state["revealed"][r][c]:
                return RunStateVerdict.COMPLETED   # a mine was uncovered
    if revealed_safe == safe_cells:
        return RunStateVerdict.COMPLETED
    return RunStateVerdict.RESUMABLE


# Keys each restore path indexes directly with ``[...]``; a snapshot missing one
# would raise KeyError while being unpacked.  Tank is deliberately absent: it
# validates its own snapshot through TankSnapshotError in _restore_tank_run_state.
_REQUIRED_KEYS = {
    "snake": ("body", "dir", "next_dir", "food", "score", "move_timer"),
    "breakout": ("bricks", "ball", "paddle", "score", "lives", "level"),
    "2048": ("grid", "score", "moves"),
    "tetris": ("grid", "bag", "next", "hold", "can_hold", "current", "score",
               "lines", "level", "fall_tick", "lock_tick"),
    "air": ("player", "enemies", "bullets", "score", "health", "missile_charge",
            "loadout"),
}


def _validate_shape_only(game_id, state) -> RunStateVerdict:
    """Accept snapshots whose restore path can unpack them, reject the rest."""
    required = _REQUIRED_KEYS.get(game_id)
    if required is None:
        return RunStateVerdict.RESUMABLE
    if not isinstance(state, dict):
        return RunStateVerdict.REJECTED
    if all(key in state for key in required):
        return RunStateVerdict.RESUMABLE
    return RunStateVerdict.REJECTED


def validate(game_id: str, state, *, expected_size=None,
             expected_count=None) -> RunStateVerdict:
    """Classify a stored run state.  Never raises on malformed input.

    ``expected_size`` / ``expected_count`` are the *current settings*.  A
    snapshot must agree with them: restoring a 9x9 board into a 16x16 mode is
    the reproducible crash (``_reveal_mines_cell`` indexes the grid with the
    setting's size), and restoring a 19x19 grid into a 15x15 board silently
    hangs the extra rows off the board.  Checking only internal consistency is
    not enough, because the setting can change between sessions.
    """
    if not isinstance(state, dict):
        return RunStateVerdict.REJECTED
    try:
        if game_id in DIMENSION_CHECKED_GAMES:
            if state.get("format") != RUN_STATE_FORMAT:
                # Pre-format snapshots cannot be checked for size, and loading
                # one into a differently sized board is the failure we guard.
                return RunStateVerdict.REJECTED
            if expected_size is not None and state.get("size", state.get("board_count")) != expected_size:
                return RunStateVerdict.REJECTED
            if expected_count is not None and state.get("mines_count") != expected_count:
                return RunStateVerdict.REJECTED
            if game_id == "gomoku":
                return _validate_gomoku(state)
            return _validate_mines(state)
        return _validate_shape_only(game_id, state)
    except (KeyError, TypeError, ValueError, IndexError):
        return RunStateVerdict.REJECTED


__all__ = [
    "DIMENSION_CHECKED_GAMES", "RUN_STATE_FORMAT", "RunStateVerdict", "validate",
]
