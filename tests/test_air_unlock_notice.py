"""Regression tests for the Air Raid unlock announcement (remediation R-07).

``air_challenge_unlocked_notice`` was set once when the standard campaign was
completed and never cleared, so "CHALLENGE CAMPAIGN + BOSS RUSH UNLOCKED" was
drawn on every later end screen — including failed missions.

The tests deliberately avoid importing the new frame constant so they can run
against the pre-fix module and fail on behaviour rather than on an ImportError.
"""

from __future__ import annotations

from _game_fixture import GameSaveTestCase


# A generous bound: the announcement must expire well within this many frames.
NOTICE_BUDGET = 2000


class UnlockNoticeTests(GameSaveTestCase):
    def _complete_the_campaign(self):
        game = self.game
        game.air_mode = "standard"
        game.air_campaign_active = True
        game.air_level = 15            # the last level
        game._finish_air(True)
        return game

    def _drain_notice(self, game):
        """Update until the notice clears; return the frame count, or None."""
        for frame in range(1, NOTICE_BUDGET + 1):
            game._update_air_raid()
            if not game.air_challenge_unlocked_notice:
                return frame
        return None

    def _arm_notice(self, game, frames):
        game.air_challenge_unlocked_notice = True
        game.air_unlock_notice_frames = frames
        return game

    def test_completing_the_campaign_raises_the_notice(self):
        game = self._complete_the_campaign()

        self.assertTrue(game.air_challenge_unlocked_notice)
        self.assertGreater(getattr(game, "air_unlock_notice_frames", 0), 0)

    def test_the_notice_expires_on_its_own(self):
        game = self._complete_the_campaign()

        expired_after = self._drain_notice(game)

        self.assertIsNotNone(
            expired_after,
            "the announcement must not persist into later end screens",
        )
        self.assertGreater(expired_after, 0)

    def test_the_notice_is_visible_right_up_to_its_last_frame(self):
        game = self._complete_the_campaign()
        lifespan = self._drain_notice(game)
        self.assertIsNotNone(lifespan)

        self._arm_notice(game, lifespan)

        for _ in range(lifespan - 1):
            game._update_air_raid()
        self.assertTrue(game.air_challenge_unlocked_notice)

        game._update_air_raid()
        self.assertFalse(game.air_challenge_unlocked_notice)

    def test_a_later_failed_mission_does_not_resurrect_the_notice(self):
        """The reported symptom: the banner reappeared on losses."""
        game = self._complete_the_campaign()
        self.assertIsNotNone(self._drain_notice(game))

        game.air_level = 4
        game._finish_air(False)
        for _ in range(60):
            game._update_air_raid()

        self.assertFalse(game.air_challenge_unlocked_notice)

    def test_the_notice_starts_clear(self):
        self.assertFalse(self.game.air_challenge_unlocked_notice)

    def test_an_expiring_notice_does_not_disturb_the_air_menu(self):
        """The countdown runs before the menu's early return, not instead of it."""
        game = self._arm_notice(self.game, 1)
        game.state = game.AIR_MENU
        game.air_demo_scene_tick = 0

        game._update_air_raid()

        self.assertEqual(game.air_demo_scene_tick, 1)
        self.assertFalse(game.air_challenge_unlocked_notice)
