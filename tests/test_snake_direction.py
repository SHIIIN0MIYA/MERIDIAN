"""Regression tests for R3.2 (D1): a queued turn must not reverse the snake.

`_set_snake_direction` compared the requested direction against the *pending*
one, so a queue could hold a 180-degree reversal: pressing UP then LEFT inside
one move interval left `snake_next_dir == (-1, 0)` while the snake was still
travelling `(1, 0)`.  The next tick then drove the head into its own neck.

Both keys arrive in the same frame because `Game.handle_events` drains the whole
event queue before `update()` runs, so this needs no unusual input timing.

The frame gate matters for the reproduction: `_update_snake()` returns until
`snake_move_timer` reaches the current interval (8 frames at score 0), so the
test must drive enough frames for the move to actually happen.
"""

from __future__ import annotations

import unittest

import pygame

from meridian.common import SNAKE_MOVE_INTERVAL_FRAMES
from meridian.system import SystemMixin


class _SnakeCase(unittest.TestCase):
    def setUp(self):
        import os
        import tempfile
        from pathlib import Path

        pygame.init()
        self._previous = os.environ.get("MERIDIAN_SAVE_PATH")
        self._scratch = Path(tempfile.mkdtemp(prefix="meridian-snake-"))
        os.environ["MERIDIAN_SAVE_PATH"] = str(self._scratch / "save.json")
        from meridian.app import Game

        self.game = Game()
        self.game._start_snake_game()
        self.game.state = self.game.SNAKE_PLAYING

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

    def _key(self, key):
        return pygame.event.Event(pygame.KEYDOWN, key=key)

    def _advance_one_move(self):
        """Run exactly enough frames for one move (plus a little slack)."""
        for _ in range(SNAKE_MOVE_INTERVAL_FRAMES + 2):
            if self.game.state != self.game.SNAKE_PLAYING:
                break
            self.game._update_snake()

    def _is_dead(self) -> bool:
        return (
            self.game.state == self.game.SNAKE_END
            or bool(getattr(self.game, "snake_game_over", False))
            or bool(getattr(self.game, "game_over", False))
        )


class QueuedReversalTests(_SnakeCase):
    def _body_moving_right(self):
        """A three-segment snake travelling right, so the neck is at (12, 11)."""
        self.game.snake = [(12, 10), (12, 11), (12, 12)]
        self.game.snake_dir = (1, 0)
        self.game.snake_next_dir = (1, 0)

    def test_up_then_left_in_one_tick_does_not_kill_the_snake(self):
        self._body_moving_right()
        self.game._handle_snake_playing_event(self._key(pygame.K_UP))
        self.game._handle_snake_playing_event(self._key(pygame.K_LEFT))
        self._advance_one_move()
        self.assertFalse(
            self._is_dead(),
            "a queued UP+LEFT was accepted as a reversal and killed the snake",
        )

    def test_a_single_left_press_is_still_rejected(self):
        self._body_moving_right()
        self.game._handle_snake_playing_event(self._key(pygame.K_LEFT))
        self.assertEqual(self.game.snake_next_dir, (1, 0), "LEFT reversed the snake")

    def test_a_legal_perpendicular_turn_still_works(self):
        self._body_moving_right()
        self.game._handle_snake_playing_event(self._key(pygame.K_UP))
        self.assertEqual(self.game.snake_next_dir, (0, -1))
        self._advance_one_move()
        self.assertFalse(self._is_dead(), "a legal turn killed the snake")
        self.assertEqual(self.game.snake_dir, (0, -1), "the turn was not applied")

    def test_pressing_the_committed_direction_is_a_no_op(self):
        self._body_moving_right()
        self.game._handle_snake_playing_event(self._key(pygame.K_RIGHT))
        self.assertEqual(self.game.snake_next_dir, (1, 0))


class OldGuardTests(_SnakeCase):
    """Prove the new guard is load-bearing by restoring the old comparison."""

    def test_old_comparison_reproduces_the_death(self):
        game = self.game
        game.snake = [(12, 10), (12, 11), (12, 12)]
        game.snake_dir = (1, 0)
        game.snake_next_dir = (1, 0)

        def old_set_direction(new_dir):
            if not game.snake:
                return
            cur_dx, cur_dy = game.snake_next_dir      # the pre-R3.2 comparison
            new_dx, new_dy = new_dir
            if cur_dx + new_dx == 0 and cur_dy + new_dy == 0:
                return
            game.snake_next_dir = new_dir

        original = type(game)._set_snake_direction
        type(game)._set_snake_direction = lambda self, d: old_set_direction(d)
        try:
            game._handle_snake_playing_event(self._key(pygame.K_UP))
            game._handle_snake_playing_event(self._key(pygame.K_LEFT))
            self.assertEqual(
                game.snake_next_dir,
                (-1, 0),
                "the old guard should have accepted the reversal",
            )
            self._advance_one_move()
            self.assertTrue(
                self._is_dead(),
                "with the old guard the snake should die -- if it does not, "
                "this test no longer proves the fix is load-bearing",
            )
        finally:
            type(game)._set_snake_direction = original


class AccessorWiringTests(unittest.TestCase):
    def test_snake_uses_the_shared_run_state_accessor(self):
        # R2 moved CONTINUE onto SystemMixin._stored_run_state; keep it that way.
        self.assertTrue(hasattr(SystemMixin, "_stored_run_state"))


if __name__ == "__main__":
    unittest.main()
