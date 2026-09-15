import os
from copy import deepcopy
from pathlib import Path
import unittest
import uuid


os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
# Skip ~2s of procedural audio synthesis; no test asserts on sound output.
os.environ.setdefault("MERIDIAN_FAST_AUDIO", "1")

from meridian import Game
from meridian.common import pygame


class ContinueResumeTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.previous_save_path = os.environ.get("MERIDIAN_SAVE_PATH")
        save_root = Path(
            os.environ.get("MERIDIAN_TEST_SAVE_ROOT", Path.cwd())
        )
        self.save_path = save_root / (
            f".meridian-continue-test-{uuid.uuid4().hex}.json"
        )
        os.environ["MERIDIAN_SAVE_PATH"] = str(self.save_path)
        self.game = Game()

    def tearDown(self):
        self.game.audio.stop()
        pygame.quit()
        if self.previous_save_path is None:
            os.environ.pop("MERIDIAN_SAVE_PATH", None)
        else:
            os.environ["MERIDIAN_SAVE_PATH"] = self.previous_save_path
        for path in (
            self.save_path,
            self.save_path.with_suffix(self.save_path.suffix + ".bak"),
            self.save_path.with_suffix(self.save_path.suffix + ".tmp"),
        ):
            path.unlink(missing_ok=True)

    def _finish_transition(self):
        for _ in range(100):
            if not self.game.transition_active:
                return
            self.game._update_transition()
        self.fail("Transition did not finish")

    @staticmethod
    def _click_action(handler, buttons, action):
        button = next(button for button in buttons if button["action"] == action)
        position = button["rect"].center
        handler(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position))
        handler(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=position))

    def test_tetris_escape_continue_restores_exact_run(self):
        game = self.game
        game._start_tetris_game()
        game.tetris_grid[-1][0] = "I"
        game.tetris_grid[-1][1] = "T"
        game.tetris_current = {"kind": "L", "x": 5, "y": 7, "rotation": 2}
        game.tetris_next = "S"
        game.tetris_hold = "O"
        game.tetris_can_hold = False
        game.tetris_bag = ["Z", "J"]
        game.tetris_score = 800
        game.tetris_lines = 4
        game.tetris_level = 2
        game.tetris_fall_tick = 17
        game.tetris_lock_tick = 9
        expected = deepcopy(game._capture_tetris_run_state())

        game._handle_tetris_playing_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        )

        progress = game.save_data["progress"]["tetris"]
        self.assertTrue(progress["run_active"])
        self.assertEqual(progress["run_state"], expected)

        self._finish_transition()
        self.assertEqual(game.state, game.TETRIS_MENU)
        self._click_action(
            game._handle_tetris_menu_event,
            game._get_tetris_menu_buttons(),
            "continue",
        )

        self.assertEqual(game.state, game.TETRIS_PLAYING)
        self.assertEqual(game._capture_tetris_run_state(), expected)

    def test_mines_escape_continue_restores_exact_run(self):
        game = self.game
        game._start_mines_game()
        game._reveal_mines_cell(4, 4)
        flag_cell = next(
            (r, c)
            for r in range(game.mines_size)
            for c in range(game.mines_size)
            if not game.mines_revealed[r][c]
        )
        game._toggle_mines_flag(*flag_cell)
        game.mines_elapsed_ms = 12345
        game.mines_resume_elapsed = 12345
        expected = deepcopy(game._capture_mines_run_state())

        game._handle_mines_playing_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        )

        progress = game.save_data["progress"]["mines"]
        self.assertTrue(progress["run_active"])
        self.assertEqual(progress["run_state"], expected)

        self._finish_transition()
        self.assertEqual(game.state, game.MINES_MENU)
        self._click_action(
            game._handle_mines_menu_event,
            game._get_mines_menu_buttons(),
            "continue",
        )

        self.assertEqual(game.state, game.MINES_PLAYING)
        self.assertEqual(game._capture_mines_run_state(), expected)


if __name__ == "__main__":
    unittest.main()
