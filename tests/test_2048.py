import unittest

from meridian import Game


class Game2048LogicTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game._start_2048_game()

    def test_board_starts_with_two_tiles(self):
        non_zero = sum(
            1 for row in self.game.g2048_grid for cell in row if cell != 0
        )
        self.assertEqual(non_zero, 2)

    def test_left_compress_merges_equal_tiles(self):
        result, score, merges = self.game._compress_2048_line([2, 0, 2, 2])
        self.assertEqual(result, [4, 2, 0, 0])
        self.assertEqual(score, 4)
        self.assertTrue(len(merges) >= 1)

    def test_game_over_detects_no_moves(self):
        # Fill board with alternating values so no merges are possible
        self.game.g2048_grid = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]
        self.assertTrue(self.game._is_2048_game_over())


if __name__ == "__main__":
    unittest.main()
