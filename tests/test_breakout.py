import unittest

from meridian import Game


class BreakoutLogicTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game._start_breakout_game()

    def test_breakout_starts_with_three_lives(self):
        self.assertEqual(self.game.breakout_lives, 3)
        self.assertEqual(self.game.breakout_score, 0)
        self.assertEqual(self.game.breakout_level, 1)

    def test_breakout_has_40_bricks(self):
        self.assertEqual(len(self.game.breakout_bricks), 40)
        self.assertTrue(all(b["alive"] for b in self.game.breakout_bricks))

    def test_ball_below_board_triggers_life_loss(self):
        board_bottom = self.game.breakout_ball["y"] + 600  # push ball far below
        self.game.breakout_ball["y"] = board_bottom
        initial_lives = self.game.breakout_lives
        self.game._update_breakout()
        self.assertEqual(self.game.breakout_lives, initial_lives - 1)


if __name__ == "__main__":
    unittest.main()
