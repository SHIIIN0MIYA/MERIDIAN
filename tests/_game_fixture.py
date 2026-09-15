"""Shared harness for tests that need a real ``Game`` and a throwaway save file.

Importing this module sets the dummy SDL drivers and disables procedural audio
synthesis, so it must be imported before ``meridian`` is used.  The user's real
save under ``%APPDATA%\\MERIDIAN`` is never touched: every test gets its own
temporary ``MERIDIAN_SAVE_PATH``.

Typical use::

    from _game_fixture import GameSaveTestCase

    class MyTests(GameSaveTestCase):
        def test_something(self):
            self.game._start_new_game()
            self.assert_run_state_survives_restart("gomoku")
"""

from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path
import unittest

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
# Skip ~2s of procedural audio synthesis; no test asserts on sound output.
os.environ.setdefault("MERIDIAN_FAST_AUDIO", "1")

from meridian import Game  # noqa: E402
from meridian.common import pygame  # noqa: E402


# Game ids that own a run state, mirroring the capture/restore convention in
# ``SystemMixin`` (`_capture_<game_id>_run_state`).
RUN_STATE_GAME_IDS = (
    "gomoku", "snake", "breakout", "2048", "mines", "tetris", "air", "tank",
)


def as_stored(value):
    """Apply the transformation the save file applies: tuples become lists.

    Run states are not JSON-stable — ``_capture_snake_run_state`` emits tuples
    while the save layer stores lists, and each game's restore path is what
    converts them back.  Comparisons therefore have to normalise the "before"
    side the same way the save layer would.
    """
    return json.loads(json.dumps(value))


class GameSaveTestCase(unittest.TestCase):
    """One ``Game`` instance and one temporary save file per test."""

    def setUp(self) -> None:
        pygame.init()
        self._previous_save_path = os.environ.get("MERIDIAN_SAVE_PATH")
        self.save_dir = Path(tempfile.mkdtemp(prefix="meridian-test-"))
        self.save_path = self.save_dir / "save.json"
        os.environ["MERIDIAN_SAVE_PATH"] = str(self.save_path)
        self.game = Game()

    def tearDown(self) -> None:
        self.game.audio.stop()
        pygame.quit()
        if self._previous_save_path is None:
            os.environ.pop("MERIDIAN_SAVE_PATH", None)
        else:
            os.environ["MERIDIAN_SAVE_PATH"] = self._previous_save_path
        for path in (
            self.save_path,
            self.save_path.with_suffix(".json.bak"),
            self.save_path.with_suffix(".json.tmp"),
        ):
            path.unlink(missing_ok=True)

    # ── run-state capture ────────────────────────────────────────────────

    def capture_run_state(self, game_id: str):
        """Return the game's own run-state snapshot (a plain dict)."""
        return getattr(self.game, f"_capture_{game_id}_run_state")()

    def stored_run_state(self, game_id: str):
        """Return the run state currently held in the in-memory save data."""
        return self.game.save_data["progress"][game_id]["run_state"]

    def progress(self, game_id: str) -> dict:
        return self.game.save_data["progress"][game_id]

    # ── save / restore roundtrip ─────────────────────────────────────────

    def save_and_restart(self) -> "Game":
        """Persist, then re-read exactly like a fresh launch would.

        Mirrors ``Game.__init__``: load from disk, replace the in-memory save
        data, clear the pending snapshots, and re-apply the loaded data (which
        repopulates ``_pending_run_states``).
        """
        game = self.game
        game._save_now()
        game.save_data = game.save_manager.load()
        game._pending_run_states.clear()
        game._apply_loaded_data()
        return game

    def pending_run_state(self, game_id: str):
        """The snapshot the restore path would offer as "Continue", if any."""
        return self.game._pending_run_states.get(game_id)

    def assert_run_state_survives_restart(self, game_id: str):
        """Assert a captured run state survives a save/restart roundtrip.

        The captured snapshot is normalised with :func:`as_stored` first, since
        the save layer converts tuples to lists.  Returns the stored snapshot.
        """
        before = as_stored(copy.deepcopy(self.capture_run_state(game_id)))
        self.save_and_restart()
        after = self.pending_run_state(game_id)
        self.assertIsNotNone(
            after, f"{game_id} run state was not offered for restore"
        )
        self.assertEqual(
            as_stored(after), before,
            f"{game_id} run state changed across a save/restart roundtrip",
        )
        return after


__all__ = ["GameSaveTestCase", "RUN_STATE_GAME_IDS", "as_stored"]
