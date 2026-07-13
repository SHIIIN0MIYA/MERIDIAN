import unittest

from meridian import Game


class MinesLogicTests(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.mines_size = 9
        self.game.mines_count = 10
        self.game._start_mines_game()

    def test_board_not_generated_until_first_click(self):
        self.assertFalse(self.game.mines_started)

    def test_board_generation_creates_safe_zone(self):
        self.game._reveal_mines_cell(4, 4)
        self.assertTrue(self.game.mines_started)
        # The 3x3 safe zone around (4,4) should contain no mines
        for r in range(3, 6):
            for c in range(3, 6):
                self.assertNotEqual(self.game.mines_grid[r][c], -1)

    def test_mine_count_is_correct(self):
        self.game._reveal_mines_cell(4, 4)
        mine_count = sum(
            1 for row in self.game.mines_grid for cell in row if cell == -1
        )
        self.assertEqual(mine_count, self.game.mines_count)

    def test_flag_toggle_changes_count(self):
        self.game._reveal_mines_cell(4, 4)
        self.assertEqual(self.game.mines_flags_count, 0)
        # Find an unrevealed non-mine cell
        for r in range(9):
            for c in range(9):
                if not self.game.mines_revealed[r][c] and self.game.mines_grid[r][c] != -1:
                    self.game._toggle_mines_flag(r, c)
                    self.assertEqual(self.game.mines_flags_count, 1)
                    self.assertTrue(self.game.mines_flags[r][c])
                    self.game._toggle_mines_flag(r, c)
                    self.assertEqual(self.game.mines_flags_count, 0)
                    self.assertFalse(self.game.mines_flags[r][c])
                    return
        self.fail("No flaggable cell found")


if __name__ == "__main__":
    unittest.main()
