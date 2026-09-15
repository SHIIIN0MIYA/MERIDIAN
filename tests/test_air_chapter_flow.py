"""Regression tests for the Air Raid chapter/level mapping (remediation R-06).

``_prepare_air_level(level)`` derives a 0-based chapter index and used to park
*that* in ``_pending_brief_level`` when a chapter story interrupted the launch.
The story then resumed at ``AIR_LEVELS[chapter - 1]`` instead of the level it
interrupted: chapter 2 replayed chapter 1's boss, chapter 8 was thrown back
seven levels to chapter 4's boss, and only chapter 1 worked by coincidence
(its chapter index and first level index are both 0).

Chapter N owns level indices [2(N-1), 2(N-1)+1].
"""

from __future__ import annotations

from _game_fixture import GameSaveTestCase

from meridian.arcade_levels import AIR_CHAPTERS, AIR_LEVELS
from meridian.common import pygame

ENTER = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
ESCAPE = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)


def _first_level_of_chapter(chapter_num):
    return 2 * (chapter_num - 1)


class ChapterStoryMappingTests(GameSaveTestCase):
    def _enter_campaign_at(self, chapters_already_read, level):
        """Reproduce the save state when the player reaches ``level``."""
        game = self.game
        game._air_progress()["stories_read"] = list(range(1, chapters_already_read + 1))
        game.air_story_source = ""
        game._pending_brief_level = None
        game.air_campaign_active = True
        game.air_mode = "standard"
        game._prepare_air_level(level)
        return game

    def test_every_chapter_story_resumes_its_own_first_mission(self):
        for chapter_num in range(1, len(AIR_CHAPTERS) + 1):
            with self.subTest(chapter=chapter_num):
                expected = _first_level_of_chapter(chapter_num)
                game = self._enter_campaign_at(chapter_num - 1, expected)

                self.assertEqual(game.state, game.AIR_STORY)
                self.assertEqual(
                    game._pending_brief_level, expected,
                    "the story must remember the level it interrupted",
                )
                game._handle_air_story_event(ENTER)
                self.assertEqual(game.air_level, expected)
                self.assertEqual(game.state, game.AIR_BRIEF)

    def test_the_campaign_advance_path_never_skips_backwards(self):
        """The path a real campaign walks, via _advance_air_after_clear."""
        game = self.game
        game._air_progress()["stories_read"] = []
        game._pending_brief_level = None
        game.air_campaign_active = True
        game.air_mode = "standard"

        game._prepare_air_level(0)
        if game.state == game.AIR_STORY:
            game._handle_air_story_event(ENTER)

        for expected in range(1, len(AIR_LEVELS)):
            with self.subTest(level=expected):
                game.air_level = expected - 1
                game._advance_air_after_clear()
                if game.state == game.AIR_STORY:
                    game._handle_air_story_event(ENTER)
                self.assertEqual(
                    game.air_level, expected,
                    f"advancing from level {expected - 1} must reach {expected}",
                )

    def test_boss_rush_starts_on_a_boss_level(self):
        game = self.game
        game._air_progress()["stories_read"] = []
        game._pending_brief_level = None

        game._start_air_boss_rush()
        if game.state == game.AIR_STORY:
            game._handle_air_story_event(ENTER)

        self.assertEqual(game.air_level, 1)
        self.assertTrue(AIR_LEVELS[game.air_level]["boss"])
        self.assertEqual(game.state, game.AIR_BRIEF)

    def test_a_level_without_a_story_still_launches(self):
        """The gate must not fire twice for the same chapter."""
        game = self._enter_campaign_at(0, 0)
        game._handle_air_story_event(ENTER)          # chapter 1 story consumed

        game._prepare_air_level(1)                   # the chapter 1 boss

        self.assertEqual(game.state, game.AIR_BRIEF)
        self.assertEqual(game.air_level, 1)


class StoryArchiveTests(GameSaveTestCase):
    def _open_archive(self, completed=0):
        game = self.game
        game._air_progress()["completed"] = completed
        game._open_air_story_archive()
        return game

    def test_opening_the_archive_clears_a_stale_pending_level(self):
        game = self.game
        game._pending_brief_level = 5

        game._open_air_story_archive()

        self.assertIsNone(game._pending_brief_level)
        self.assertEqual(game.air_story_source, "archive_index")

    def test_enter_opens_the_highlighted_chapter(self):
        """This branch used to be unreachable: ENTER left the archive."""
        game = self._open_archive(completed=3)

        game.air_story_page = 1                      # chapter 1
        game._handle_air_story_event(ENTER)

        self.assertEqual(game.air_story_source, "chapter_1")
        self.assertEqual(game.air_story_page, 0)
        self.assertEqual(game.air_story_lines, list(_chapter_lines(1)))

    def test_enter_opens_the_prologue_at_index_zero(self):
        game = self._open_archive(completed=3)

        game.air_story_page = 0
        game._handle_air_story_event(ENTER)

        self.assertEqual(game.air_story_source, "prologue")

    def test_a_locked_chapter_cannot_be_opened(self):
        game = self._open_archive(completed=0)       # only chapter 1 readable

        game.air_story_page = 5
        game._handle_air_story_event(ENTER)

        self.assertEqual(
            game.air_story_source, "archive_index",
            "a locked chapter must leave the reader on the index",
        )

    def test_escape_leaves_the_archive(self):
        game = self._open_archive()

        game._handle_air_story_event(ESCAPE)

        self.assertEqual(game.state, game.AIR_MENU)

    def test_opening_a_chapter_does_not_launch_a_level(self):
        """Reading the archive must never start a mission."""
        game = self._open_archive(completed=8)
        game.air_level = 7

        game.air_story_page = 3
        game._handle_air_story_event(ENTER)
        game._handle_air_story_event(ENTER)          # now on a chapter page

        self.assertEqual(game.air_level, 7, "the archive must not change the level")


def _chapter_lines(chapter_num):
    from meridian.arcade_levels import AIR_CHAPTER_STORIES
    return AIR_CHAPTER_STORIES[chapter_num]
