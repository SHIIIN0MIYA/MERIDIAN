"""Single entry point for the test-suite environment.

``conftest.py`` is imported by pytest *before* any test module, which makes this
the only place that can guarantee the environment is prepared before ``meridian``
(and therefore ``pygame``) is imported.  Previously the same five-line preamble
was copy-pasted into ``_game_fixture.py``, ``test_achievements.py``,
``test_completion_lore.py``, ``test_registration.py`` and
``test_tetris_mines_continue.py``; anything that imported ``meridian`` without it
paid for it with real SDL drivers and ~2s of procedural audio synthesis.

Two things happen here:

1. **Environment** (module import time, via ``os.environ.setdefault``) — headless
   SDL drivers and fast audio.  ``setdefault`` rather than assignment so a CI
   runner that already exports these (or a developer debugging with a real
   window) keeps its own value.
2. **Importability from any working directory** — the repository root is put on
   ``sys.path`` so ``pytest D:\\path\\to\\repo\\tests`` works even when the
   current directory is not the repository root.
3. **Save isolation** (autouse fixture, below) — every test gets its own
   ``tmp_path``-backed save location.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ── 1. Environment, before anything imports meridian/pygame ──────────────────
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
# Skip ~2s of procedural audio synthesis; no test asserts on sound output.
os.environ.setdefault("MERIDIAN_FAST_AUDIO", "1")

# ── 2. Make ``meridian`` importable from any working directory (V-12) ────────
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402  (kept after the environment setup on purpose)


@pytest.fixture(autouse=True)
def _isolate_save_location(tmp_path, monkeypatch):
    """Redirect both save-location variables into this test's ``tmp_path``.

    Without this the suite writes outside the sandbox:

    * ``MERIDIAN_TEST_SAVE_ROOT`` is read by several test modules as
      ``Path(os.environ.get("MERIDIAN_TEST_SAVE_ROOT", Path.cwd()))``, so with
      the variable unset the per-test save files land in the repository root.
      Those files are ``.meridian-*-test-<uuid>.json`` plus the ``.bak``/``.bak2``
      generations the save manager rotates, which is exactly how
      ``.meridian-continue-test-*.json.bak2`` ended up polluting the repo root.
    * ``MERIDIAN_SAVE_PATH`` is what ``SaveManager`` prefers; without it the
      manager falls back to the user's *real* save under ``%APPDATA%\\MERIDIAN``
      and a test would mutate a player's progress.

    ``monkeypatch.setenv`` restores the previous value at teardown, so tests that
    override either variable themselves (``GameSaveTestCase``) still work.
    """
    save_root = tmp_path / "save_root"
    save_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("MERIDIAN_TEST_SAVE_ROOT", str(save_root))
    monkeypatch.setenv("MERIDIAN_SAVE_PATH", str(save_root / "save.json"))
    yield save_root
