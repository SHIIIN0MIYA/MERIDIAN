# Tetris and Mines Continue Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the exact active Tetris and Mines run when the player presses `ESC` and then chooses `CONTINUE`.

**Architecture:** Keep the existing per-game persistence model. Capture each run synchronously while its gameplay state is still active, then make Tetris read the same saved run that controls its `CONTINUE` button; Mines keeps its existing restore source.

**Tech Stack:** Python 3.12, pygame 2.x, standard-library `unittest`

## Global Constraints

- Limit production changes to `meridian/tetris.py` and `meridian/mines.py`.
- Do not change the persistence schema or unrelated game behavior.
- Use isolated temporary saves; never read or write the player's normal save.
- Do not create a Git commit unless the user separately requests one.

---

### Task 1: Add Resume Regression Coverage

**Files:**
- Create: `tests/test_tetris_mines_continue.py`
- Test: `tests/test_tetris_mines_continue.py`

**Interfaces:**
- Consumes: `Game._handle_tetris_playing_event`, `Game._handle_tetris_menu_event`, `Game._handle_mines_playing_event`, `Game._handle_mines_menu_event`
- Produces: two regression tests covering the full `ESC -> menu -> CONTINUE` behavior

- [ ] **Step 1: Write the failing tests**

Create an isolated `unittest.TestCase` that starts each game, assigns observable run state,
sends a `pygame.KEYDOWN` event for `ESC`, completes the transition, clicks the actual
`CONTINUE` menu button with mouse down/up events, and compares `_capture_*_run_state()` before
and after.

- [ ] **Step 2: Run the tests to verify RED**

Run:

```powershell
python -m unittest discover -s tests -p test_tetris_mines_continue.py -v
```

Expected: both tests fail. Tetris resets its score/grid because the restore source is `None`;
Mines has no synchronously captured active run after `ESC`.

---

### Task 2: Repair Tetris Continue

**Files:**
- Modify: `meridian/tetris.py:309-355`
- Test: `tests/test_tetris_mines_continue.py`

**Interfaces:**
- Consumes: `SystemMixin._save_now()` and `save_data["progress"]["tetris"]["run_state"]`
- Produces: exact same-session Tetris restoration through the existing `_start_tetris_game(restore_state=...)` interface

- [ ] **Step 1: Save before leaving gameplay**

Inside the Tetris `ESC` branch, call `_save_now()` before `_start_transition(...)` while the
state is still `TETRIS_PLAYING`.

- [ ] **Step 2: Use the visible button's save source**

Change the menu action to:

```python
"continue": lambda: self._start_tetris_game(
    restore_state=self.save_data["progress"]["tetris"]["run_state"]
),
```

- [ ] **Step 3: Run the Tetris regression test to verify GREEN**

Run:

```powershell
python -m unittest discover -s tests -p test_tetris_mines_continue.py -k tetris_escape_continue -v
```

Expected: PASS.

---

### Task 3: Synchronize Mines on ESC

**Files:**
- Modify: `meridian/mines.py:294-301`
- Test: `tests/test_tetris_mines_continue.py`

**Interfaces:**
- Consumes: `SystemMixin._save_now()` and the existing Mines `save_data` restore path
- Produces: a consistent Mines snapshot before the menu becomes active

- [ ] **Step 1: Save before leaving gameplay**

Inside the Mines `ESC` branch, call `_save_now()` before `_start_transition(...)` while the state
is still `MINES_PLAYING`.

- [ ] **Step 2: Run both regression tests to verify GREEN**

Run:

```powershell
python -m unittest discover -s tests -p test_tetris_mines_continue.py -v
```

Expected: 2 tests pass.

---

### Task 4: Record the Incident in the Tetris Diary

**Files:**
- Modify: `Development_Log/Developer_Diary/Part_08_Tetris.md`

**Interfaces:**
- Consumes: the reproduced failure and verified fix from Tasks 1-3
- Produces: a first-person, linear account inside record 97 without renumbering later entries

- [ ] **Step 1: Add the real playtest sequence**

Describe starting a Tetris run, pressing `ESC`, selecting `CONTINUE`, and receiving a fresh
board instead of the active run.

- [ ] **Step 2: Add root cause and repair details**

Explain the two different Tetris state sources, synchronous save before leaving, the related
Mines snapshot issue, and the state fields covered by the final regression test.

---

### Task 5: Final Verification

**Files:**
- Verify: `meridian/tetris.py`
- Verify: `meridian/mines.py`
- Verify: `tests/test_tetris_mines_continue.py`
- Verify: `Development_Log/Developer_Diary/Part_08_Tetris.md`

**Interfaces:**
- Consumes: all prior task outputs
- Produces: verified code and documentation changes ready for user review

- [ ] **Step 1: Run targeted tests**

```powershell
python -m unittest discover -s tests -p test_tetris_mines_continue.py -v
```

Expected: 2 tests pass.

- [ ] **Step 2: Run repository checks**

```powershell
python tools/check_release.py
python -m compileall -q MERIDIAN.py meridian tests/test_tetris_mines_continue.py
```

Expected: release check exits 0 and compilation exits 0.

- [ ] **Step 3: Review the diff and workspace status**

```powershell
git diff --check
git diff -- meridian/tetris.py meridian/mines.py Development_Log/Developer_Diary/Part_08_Tetris.md tests/test_tetris_mines_continue.py
git status --short
```

Expected: no whitespace errors; only intended production, test, plan/spec, and development-log
files are changed or added.
