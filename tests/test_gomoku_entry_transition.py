"""Regression tests for the Gomoku entry transition (remediation R-11).

``_start_new_game`` used to set ``self.state = self.PLAYING`` itself. The menu
callers then called ``_start_transition(PLAYING)``, which returns immediately
when the target already equals the current state — so starting or continuing a
game never faded at all, while the "resume" entry (which never calls
``_start_new_game``) did.

The end screen had the mirror problem: its R key restarted without a
transition while its "again" button restarted with one.
"""

from __future__ import annotations

from _game_fixture import GameSaveTestCase

from meridian.common import pygame


def _click(handler, buttons, action):
    button = next(b for b in buttons if b["action"] == action)
    position = button["rect"].center
    handler(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=position))
    handler(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=position))


class GomokuEntryTransitionTests(GameSaveTestCase):
    def _menu_entry(self, action):
        game = self.game
        game.state = game.MENU
        game.transition_active = False
        _click(game._handle_menu_event, game._get_menu_buttons(), action)
        return game

    def test_starting_from_the_menu_plays_a_transition(self):
        game = self._menu_entry("start")

        self.assertTrue(
            game.transition_active,
            "starting a game must fade, not cut straight to the board",
        )

    def test_the_state_does_not_switch_before_the_fade_completes(self):
        game = self._menu_entry("start")
        self.assertEqual(
            game.state, game.MENU,
            "the menu must stay on screen while the transition fades out",
        )

        self._finish_transition()

        self.assertEqual(game.state, game.PLAYING)

    def test_continuing_a_saved_game_plays_a_transition(self):
        game = self.start_gomoku()
        game.board.place_stone(7, 7)
        game._save_now()                      # marks the run active on disk
        self.assertTrue(self.progress("gomoku")["run_active"])
        game.state = game.MENU
        game.transition_active = False

        _click(game._handle_menu_event, game._get_menu_buttons(), "continue")

        self.assertTrue(game.transition_active)

    def test_resuming_plays_a_transition(self):
        """The entry that always worked — kept so the three stay aligned."""
        game = self.start_gomoku()
        game.board.place_stone(7, 7)
        game.state = game.MENU
        game.transition_active = False
        actions = {b["action"] for b in game._get_menu_buttons()}
        self.assertIn("resume", actions)

        _click(game._handle_menu_event, game._get_menu_buttons(), "resume")

        self.assertTrue(game.transition_active)

    def test_the_end_screen_key_and_button_restart_alike(self):
        """Both restart paths must behave the same; only one used to fade."""
        game = self.start_gomoku()
        game.state = game.END
        game.transition_active = False
        game._handle_end_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
        by_key = game.transition_active

        game2 = self.start_gomoku()
        game2.state = game2.END
        game2.transition_active = False
        _click(game2._handle_end_event, game2._get_end_buttons(), "again")
        by_button = game2.transition_active

        self.assertTrue(by_key, "the R key restart must fade like the button does")
        self.assertEqual(by_key, by_button)

    def test_an_in_game_restart_does_not_fade(self):
        """Already playing: a restart should be instant, as it was before."""
        game = self.start_gomoku()
        game.board.place_stone(7, 7)
        game.transition_active = False

        game._handle_game_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))

        self.assertFalse(game.transition_active)
        self.assertEqual(game.board.move_count, 0)

    def _finish_transition(self):
        for _ in range(200):
            if not self.game.transition_active:
                return
            self.game._update_transition()
        self.fail("the transition never completed")
