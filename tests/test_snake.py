import unittest

import pygame

from meridian import Game
from meridian.common import SNAKE_GRID_COUNT


class SnakeLogicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not pygame.get_init():
            pygame.init()

    @classmethod
    def tearDownClass(cls):
        pass  # Don't quit pygame; other tests may need it

    def setUp(self):
        self.game = Game()
        self.game._start_snake_game()
        mid = SNAKE_GRID_COUNT // 2
        self.head_row = mid
        self.head_col = mid

    def test_snake_starts_with_three_segments(self):
        self.assertEqual(len(self.game.snake), 3)
        self.assertEqual(self.game.snake[-1], (self.head_row, self.head_col))

    def test_direction_change_prevents_reverse(self):
        # Initial direction is right: (1, 0) as (dc, dr)
        # Attempt to go left: (-1, 0) — should be rejected
        self.game._set_snake_direction((-1, 0))
        self.assertEqual(self.game.snake_next_dir, (1, 0))

        # Up should work: (0, -1)
        self.game._set_snake_direction((0, -1))
        self.assertEqual(self.game.snake_next_dir, (0, -1))

    def test_food_spawns_on_empty_cell(self):
        self.game._spawn_snake_food()
        food = self.game.snake_food
        self.assertIsNotNone(food)
        self.assertNotIn(food, self.game.snake)
        r, c = food
        self.assertTrue(0 <= r < SNAKE_GRID_COUNT)
        self.assertTrue(0 <= c < SNAKE_GRID_COUNT)

    def test_score_increments_on_food_eaten(self):
        self.assertEqual(self.game.snake_score, 0)
        # Place food directly in front of snake head
        dc, dr = self.game.snake_dir
        food_r = self.head_row + dr
        food_c = self.head_col + dc
        self.game.snake_food = (food_r, food_c)
        # Force move tick
        self.game.snake_move_timer = self.game._get_snake_current_interval()
        self.game._update_snake()
        self.assertEqual(self.game.snake_score, 1)
        self.assertGreater(len(self.game.snake), 3)


if __name__ == "__main__":
    unittest.main()
