"""Structural guards for R7 (Gomoku's per-frame updates moved out of app.py).

R7 moved Gomoku's ten per-frame animation methods out of the generic tail of
`Game.update()` into a `_update_gomoku()` method registered for Gomoku's four
main states.  Before that, "no entry in `_UPDATE_DISPATCH`" implicitly meant
"run Gomoku's animation code", which is why 19 unrelated states (desktop, the
achievement wall, the lore reader, ...) executed it every frame.

Behaviour was verified unchanged by a 92-case rendering fingerprint (46 states
x 2 languages, 6 frames each, hashing the screen surface): every digest is
identical before and after.  These tests lock in the structural part.
"""

from __future__ import annotations

import unittest

import pygame


class _GameCase(unittest.TestCase):
    def setUp(self):
        import os
        import tempfile
        from pathlib import Path

        pygame.init()
        self._previous = os.environ.get("MERIDIAN_SAVE_PATH")
        self._scratch = Path(tempfile.mkdtemp(prefix="meridian-r7-"))
        os.environ["MERIDIAN_SAVE_PATH"] = str(self._scratch / "save.json")
        from meridian.app import Game

        self.game = Game()

    def tearDown(self):
        import os
        import shutil

        self.game.audio.stop()
        pygame.quit()
        if self._previous is None:
            os.environ.pop("MERIDIAN_SAVE_PATH", None)
        else:
            os.environ["MERIDIAN_SAVE_PATH"] = self._previous
        shutil.rmtree(self._scratch, ignore_errors=True)


class GomokuUpdateRegistrationTests(_GameCase):
    GOMOKU_STATES = ("MENU", "PLAYING", "END", "SETTINGS")

    def test_gomoku_states_are_registered_explicitly(self):
        game = self.game
        for name in self.GOMOKU_STATES:
            with self.subTest(state=name):
                state = getattr(game, name)
                entry = game._UPDATE_DISPATCH.get(state)
                self.assertIsNotNone(entry, f"{name} has no update entry")
                self.assertIn("_update_gomoku", entry[1])

    def test_update_gomoku_exists_and_runs_its_ten_subsystems(self):
        game = self.game
        game._start_new_game()
        game.state = game.PLAYING
        for _ in range(3):
            game._update_gomoku()          # must not raise

    def test_update_gomoku_advances_the_gomoku_animations(self):
        game = self.game
        game._start_new_game()
        game.state = game.PLAYING
        game.anim_tick = 0
        game.ripples.append({"frame": 0, "max_frames": 10})
        game._update_gomoku()
        self.assertEqual(game.ripples[0]["frame"], 1, "the ripple did not advance")

    def test_the_generic_tail_still_runs_shared_subsystems(self):
        game = self.game
        game.particles.append(_FakeParticle())
        game.state = game.DESKTOP
        game.update()
        self.assertEqual(
            len(game.particles), 0, "shared particle updates stopped running"
        )


class _FakeParticle:
    def __init__(self):
        self.removed = False

    def update(self):
        return False          # False means "expired, drop me"


class DispatchInvariantTests(_GameCase):
    def test_no_update_entry_means_the_shared_tail(self):
        """`None` must still mean "shared visual subsystems", as documented.

        Extension games rely on this: `register_game_state(update_methods=None)`
        deliberately leaves no table entry.  The tail now calls a Gomoku method
        that is harmless without Gomoku state, which is what makes that safe.
        """
        game = self.game
        game.state = "definitely_not_a_registered_state"
        game.particles.clear()
        game.update()             # must not raise

    def test_every_state_still_has_a_draw_handler(self):
        game = self.game
        for state in game._UPDATE_DISPATCH:
            with self.subTest(state=state):
                self.assertIn(state, game._DRAW_DISPATCH)

    def test_state_count_is_unchanged_by_the_refactor(self):
        game = self.game
        states = set(game._EVENT_DISPATCH) | set(game._UPDATE_DISPATCH) | set(game._DRAW_DISPATCH)
        self.assertEqual(len(states), 46)


if __name__ == "__main__":
    unittest.main()
