import pygame
import tests.visual_scenes as visual_scenes

from meridian.localization import get_language
from meridian.tank_engine import BulletState, ItemType, MatchPhase, SmokeState
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


def test_shell_visual_states_are_explicitly_fixed():
    page_1 = build_scene("desktop_page_1", "en")
    page_2 = build_scene("desktop_page_2", "zh_hans")
    assert (page_1.state, page_1.desktop_page) == (page_1.DESKTOP, 0)
    assert (page_2.state, page_2.desktop_page) == (page_2.DESKTOP, 1)

    settings = build_scene("system_settings", "en")
    assert settings.state == settings.SYSTEM_SETTINGS
    assert settings.audio.music_volume == 0.4
    assert settings.audio.sfx_volume == 0.65
    if hasattr(settings.audio, "master_volume"):
        assert settings.audio.master_volume == 0.8
    assert settings.animation_level == "full"

    profile = build_scene("profile_statistics", "en")
    assert (profile.state, profile.profile_tab, profile.profile_scroll) == (
        profile.PROFILE, "statistics", 0,
    )

    achievements = build_scene("achievement_wall", "zh_hans")
    assert achievements.state == achievements.ACHIEVEMENT_WALL
    assert achievements.achievement_wall_page == 0
    assert set(achievements.save_data["achievements"]) == {
        "gomoku_first_game", "snake_5", "tank_first_clash",
    }

    lore = build_scene("lore_list", "zh_hans")
    assert (lore.state, lore.lore_category_index) == (lore.LORE_READER, 0)
    assert (lore.lore_entry_index, lore.lore_scroll) == (0, 0)


def test_tank_menu_and_controls_visual_states_are_fixed():
    menu = build_scene("tank_menu", "en")
    controls = build_scene("tank_controls", "zh_hans")

    assert (menu.state, menu.tank_pressed_action) == (menu.TANK_MENU, None)
    assert (controls.state, controls.tank_pressed_action) == (
        controls.TANK_CONTROLS, None,
    )


def test_tank_playing_visual_state_is_not_a_random_default():
    playing = build_scene("tank_playing", "en")
    engine = playing.tank_engine

    assert playing.state == playing.TANK_PLAYING
    assert engine.phase is MatchPhase.REGULATION
    assert engine.score == {"red": 2, "blue": 1}
    assert engine.remaining_ms == 72_000
    assert engine.tanks["red"].hp == 2
    assert engine.tanks["red"].held_item is ItemType.PIERCING
    assert engine.tanks["blue"].hp == 1
    assert engine.tanks["blue"].held_item is ItemType.SMOKE
    assert engine.bullets == [BulletState("red", 9.5, 5.5, 1.0, 0.0, True)]
    assert engine.smokes == [SmokeState("blue", 18.5, 8.5, 90_000)]
    assert playing.tank_paused is False
    assert engine.paused is False


def test_tank_paused_visual_state_freezes_the_fixed_match():
    paused = build_scene("tank_paused", "zh_hans")

    assert paused.state == paused.TANK_PLAYING
    assert paused.tank_engine.score == {"red": 2, "blue": 1}
    assert paused.tank_paused is True
    assert paused.tank_engine.paused is True


def test_tank_sudden_death_visual_state_is_explicit():
    sudden = build_scene("tank_sudden_death", "zh_hans")

    assert sudden.state == sudden.TANK_PLAYING
    assert sudden.tank_engine.phase is MatchPhase.SUDDEN_DEATH
    assert sudden.tank_engine.remaining_ms == 0
    assert sudden.tank_engine.score == {"red": 3, "blue": 3}
    assert sudden.tank_engine.tanks["red"].hp == 1
    assert sudden.tank_engine.tanks["blue"].hp == 1
    assert sudden._tank_in_sudden_death is True


def test_tank_end_visual_state_has_fixed_result_data():
    ended = build_scene("tank_end", "en")

    assert ended.state == ended.TANK_END
    assert ended.tank_engine.phase is MatchPhase.ENDED
    assert ended.tank_engine.remaining_ms == 0
    assert ended.tank_engine.score == {"red": 4, "blue": 3}
    assert ended.tank_engine.winner == "red"
    assert ended.tank_engine.tanks["red"].hp == 2
    assert ended.tank_engine.tanks["blue"].hp == 0
