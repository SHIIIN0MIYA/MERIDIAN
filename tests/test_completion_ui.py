from unittest.mock import patch

import pygame

from meridian import Game
from meridian.completion import WORLD_IDS


def make_game():
    pygame.init()
    return Game()


def test_profile_exposes_eight_equal_world_cards():
    game = make_game()
    cards = game._completion_world_cards()
    assert [card["game_id"] for card in cards] == list(WORLD_IDS)
    assert all(set(card) >= {"total", "achievement", "objectives", "lore"} for card in cards)


def test_completion_lore_unlocks_thresholds_once_and_not_in_dev_mode():
    game = make_game()
    with patch("meridian.system.global_completion", return_value=50):
        assert game._unlock_completion_lore() == ["resonance_25", "resonance_50"]
        assert game._unlock_completion_lore() == []
    game.dev_mode = True
    with patch("meridian.system.global_completion", return_value=100):
        assert game._unlock_completion_lore() == []


def test_completion_profile_and_resonant_desktop_draw_without_error():
    game = make_game()
    game.profile_tab = "completion"
    game._draw_profile()
    with patch("meridian.shell_desktop.global_completion", return_value=99):
        assert game._completion_desktop_variant() == "normal"
    with patch("meridian.shell_desktop.global_completion", return_value=100):
        assert game._completion_desktop_variant() == "resonant"
