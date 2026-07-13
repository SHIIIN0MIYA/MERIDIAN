import pygame
import tests.visual_scenes as visual_scenes

from meridian.localization import get_language
from tests.visual_scenes import SCENE_NAMES, build_scene, render_scene


def test_visual_suite_has_exactly_twelve_named_scenes():
    assert SCENE_NAMES == (
        "desktop_page_1", "desktop_page_2", "system_settings",
        "profile_statistics", "achievement_wall", "lore_list",
        "tank_menu", "tank_controls", "tank_playing", "tank_paused",
        "tank_sudden_death", "tank_end",
    )


def test_each_scene_builds_with_frozen_visual_environment():
    for language in ("en", "zh_hans"):
        for name in SCENE_NAMES:
            game = build_scene(name, language)
            assert game.screen.get_size() == (1280, 720)
            assert game.anim_tick == 120
            assert game.transition_active is False
            assert game.desktop_particles == []
            assert game.screen_shake_enabled is False
            assert game._get_desktop_time_text() == "12:34"
            assert game._get_battery_text() == "BAT 88%"
            assert game.language == language
            assert get_language() == language


def test_render_scene_returns_a_detached_fixed_size_surface(monkeypatch):
    class FakeGame:
        def __init__(self):
            self.screen = pygame.Surface((1280, 720))
            self.screen.fill((10, 20, 30))

        def draw(self):
            pass

    game = FakeGame()
    monkeypatch.setattr(visual_scenes, "build_scene", lambda name, language: game)

    surface = render_scene("desktop_page_1", "zh_hans")

    assert isinstance(surface, pygame.Surface)
    assert surface.get_size() == (1280, 720)
    assert surface is not game.screen

    surface.set_at((0, 0), (200, 100, 50))
    assert game.screen.get_at((0, 0)) == pygame.Color(10, 20, 30, 255)
