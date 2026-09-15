# Tetris and Mines Continue Fix Design

## Problem

Two menu flows can lose the active run after leaving gameplay with `ESC`:

- Tetris shows `CONTINUE` from `save_data`, but the action restores from
  `_pending_run_states`. That cache is populated only while loading a save and is cleared when
  a game starts, so continuing during the same application session passes `None` and creates a
  new board.
- Mines restores from `save_data`, but `ESC` changes state without first capturing the current
  run. Periodic persistence can therefore leave scalar fields such as `started`, elapsed time,
  and counters older than the live grid and revealed-cell matrices.

## Scope

The fix is limited to Tetris and Mines. It does not introduce a shared navigation refactor or
change new-game, game-over, desktop, pause, scoring, or save-schema behavior.

## Design

### Tetris

While still in `TETRIS_PLAYING`, handling `ESC` will call `_save_now()` before starting the menu
transition. The menu's `continue` action will restore from
`save_data["progress"]["tetris"]["run_state"]`, the same source used to decide whether the
button is visible. `_start_tetris_game()` will continue to consume the restored run through the
existing `_clear_run_state("tetris")` behavior.

### Mines

While still in `MINES_PLAYING`, handling `ESC` will call `_save_now()` before starting the menu
transition. The existing `continue` action already reads the correct `save_data` entry, so no
second restore path is needed.

## Regression Tests

One isolated `unittest` module will use a temporary save file and the SDL dummy drivers.

- Tetris: set a non-empty grid, score, line count, level, current piece, next piece, hold piece,
  bag, and fall/lock counters; leave with `ESC`; activate the real menu `CONTINUE` button; assert
  that the captured run is restored exactly.
- Mines: generate a board, reveal cells, place a flag, set elapsed time, leave with `ESC`;
  activate the real menu `CONTINUE` button; assert that grid, revealed cells, flags, started
  state, elapsed time, and counters are restored exactly.

The tests must fail against the current implementation before production code changes and pass
after the minimal fixes.

## Development-History Update

The incident will be added inside record 97 of the Tetris development diary. It will describe
the observed `ESC -> CONTINUE -> new game` behavior, the mismatch between visibility and restore
state sources, the related Mines snapshot issue discovered during comparison, the fixes, and the
cross-game resume checks. No record numbers will change.
