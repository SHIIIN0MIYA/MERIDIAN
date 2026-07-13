"""Deterministic scene factory shared by the bilingual visual suite."""

from __future__ import annotations

import random
from collections.abc import Callable

import pygame

from meridian.app import Game
from meridian.localization import set_language
from meridian.tank_engine import (
    BulletState,
    ItemType,
    MatchPhase,
    SmokeState,
)


SCENE_NAMES: tuple[str, ...] = (
    "desktop_page_1", "desktop_page_2", "system_settings",
    "profile_statistics", "achievement_wall", "lore_list",
    "tank_menu", "tank_controls", "tank_playing", "tank_paused",
    "tank_sudden_death", "tank_end",
)

_VISUAL_RANDOM_SEED = 330


def _scene_desktop_page_1(game: Game) -> None:
    game.state = game.DESKTOP
    game.desktop_page = 0


def _scene_desktop_page_2(game: Game) -> None:
    game.state = game.DESKTOP
    game.desktop_page = 1


def _scene_system_settings(game: Game) -> None:
    game.state = game.SYSTEM_SETTINGS
    if hasattr(game.audio, "master_volume"):
        game.audio.master_volume = 0.8
    game.audio.set_music_volume(0.4)
    game.audio.set_sfx_volume(0.65)
    game.animation_level = "full"


def _scene_profile_statistics(game: Game) -> None:
    game.state = game.PROFILE
    game.profile_tab = "statistics"
    game.profile_scroll = 0


def _scene_achievement_wall(game: Game) -> None:
    game.state = game.ACHIEVEMENT_WALL
    game.achievement_wall_page = 0
    game.achievement_wall_detail_index = None
    unlocked_at = "2033-03-30T12:34:00"
    game.save_data["achievements"] = {
        achievement_id: {"unlocked_at": unlocked_at}
        for achievement_id in (
            "gomoku_first_game", "snake_5", "tank_first_clash",
        )
    }


def _scene_lore_list(game: Game) -> None:
    game.state = game.LORE_READER
    game.lore_category_index = 0
    game.lore_entry_index = 0
    game.lore_scroll = 0
    game.lore_reading_entry_id = None


def _scene_tank_menu(game: Game) -> None:
    game.state = game.TANK_MENU
    game.tank_pressed_action = None


def _scene_tank_controls(game: Game) -> None:
    game.state = game.TANK_CONTROLS
    game.tank_pressed_action = None


def _fixed_tank_match(game: Game) -> None:
    engine = game.tank_engine
    engine.phase = MatchPhase.REGULATION
    engine.elapsed_ms = 108_000
    engine.remaining_ms = 72_000
    engine.score.update(red=2, blue=1)
    engine.winner = None
    engine.paused = False
    engine.tanks["red"].hp = 2
    engine.tanks["red"].held_item = ItemType.PIERCING
    engine.tanks["blue"].hp = 1
    engine.tanks["blue"].held_item = ItemType.SMOKE
    engine.bullets = [BulletState("red", 9.5, 5.5, 1.0, 0.0, True)]
    engine.smokes = [SmokeState("blue", 18.5, 8.5, 90_000)]
    game.tank_paused = False


def _scene_tank_playing(game: Game) -> None:
    game.state = game.TANK_PLAYING
    _fixed_tank_match(game)


def _scene_tank_paused(game: Game) -> None:
    game.state = game.TANK_PLAYING
    _fixed_tank_match(game)
    game.tank_paused = True
    game.tank_engine.paused = True


def _scene_tank_sudden_death(game: Game) -> None:
    game.state = game.TANK_PLAYING
    _fixed_tank_match(game)
    game.tank_engine.phase = MatchPhase.SUDDEN_DEATH
    game.tank_engine.remaining_ms = 0
    game.tank_engine.score.update(red=3, blue=3)
    game.tank_engine.tanks["red"].hp = 1
    game.tank_engine.tanks["blue"].hp = 1
    game._tank_in_sudden_death = True


def _scene_tank_end(game: Game) -> None:
    game.state = game.TANK_END
    _fixed_tank_match(game)
    game.tank_engine.phase = MatchPhase.ENDED
    game.tank_engine.remaining_ms = 0
    game.tank_engine.score.update(red=4, blue=3)
    game.tank_engine.winner = "red"
    game.tank_engine.tanks["red"].hp = 2
    game.tank_engine.tanks["blue"].hp = 0


SCENE_BUILDERS: dict[str, Callable[[Game], None]] = {
    "desktop_page_1": _scene_desktop_page_1,
    "desktop_page_2": _scene_desktop_page_2,
    "system_settings": _scene_system_settings,
    "profile_statistics": _scene_profile_statistics,
    "achievement_wall": _scene_achievement_wall,
    "lore_list": _scene_lore_list,
    "tank_menu": _scene_tank_menu,
    "tank_controls": _scene_tank_controls,
    "tank_playing": _scene_tank_playing,
    "tank_paused": _scene_tank_paused,
    "tank_sudden_death": _scene_tank_sudden_death,
    "tank_end": _scene_tank_end,
}


def build_scene(name: str, language: str) -> Game:
    random.seed(_VISUAL_RANDOM_SEED)
    set_language(language)
    game = Game()
    game.language = language
    set_language(language)
    game.anim_tick = 120
    game.transition_active = False
    game.desktop_particles.clear()
    game.screen_shake_enabled = False
    game._get_desktop_time_text = lambda: "12:34"
    game._get_battery_text = lambda: "BAT 88%"
    game._last_clock_minute = -1
    configure = SCENE_BUILDERS[name]
    configure(game)
    return game


def render_scene(name: str, language: str) -> pygame.Surface:
    game = build_scene(name, language)
    game.draw()
    return game.screen.copy()
