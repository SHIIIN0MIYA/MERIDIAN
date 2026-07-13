"""Deterministic scene factory shared by the bilingual visual suite."""

from __future__ import annotations

import random
from collections.abc import Callable

import pygame

from meridian.app import Game
from meridian.localization import set_language
from meridian.tank_engine import MatchPhase


SCENE_NAMES: tuple[str, ...] = (
    "desktop_page_1", "desktop_page_2", "system_settings",
    "profile_statistics", "achievement_wall", "lore_list",
    "tank_menu", "tank_controls", "tank_playing", "tank_paused",
    "tank_sudden_death", "tank_end",
)

_VISUAL_RANDOM_SEED = 330


def _state(state_name: str, **attributes: object) -> Callable[[Game], None]:
    def configure(game: Game) -> None:
        game.state = getattr(game, state_name)
        for name, value in attributes.items():
            setattr(game, name, value)

    return configure


def _tank_sudden_death(game: Game) -> None:
    game.state = game.TANK_PLAYING
    game.tank_engine.phase = MatchPhase.SUDDEN_DEATH
    game.tank_engine.remaining_ms = 0
    game._tank_in_sudden_death = True


def _tank_end(game: Game) -> None:
    game.state = game.TANK_END
    game.tank_engine.phase = MatchPhase.ENDED
    game.tank_engine.remaining_ms = 0
    game.tank_engine.score.update(red=3, blue=2)
    game.tank_engine.winner = "red"


SCENE_BUILDERS: dict[str, Callable[[Game], None]] = {
    "desktop_page_1": _state("DESKTOP", desktop_page=0),
    "desktop_page_2": _state("DESKTOP", desktop_page=1),
    "system_settings": _state("SYSTEM_SETTINGS"),
    "profile_statistics": _state("PROFILE", profile_tab="statistics", profile_scroll=0),
    "achievement_wall": _state("ACHIEVEMENT_WALL", achievement_wall_page=0),
    "lore_list": _state("LORE_READER", lore_category_index=0, lore_entry_index=0, lore_scroll=0),
    "tank_menu": _state("TANK_MENU"),
    "tank_controls": _state("TANK_CONTROLS"),
    "tank_playing": _state("TANK_PLAYING"),
    "tank_paused": _state("TANK_PLAYING", tank_paused=True),
    "tank_sudden_death": _tank_sudden_death,
    "tank_end": _tank_end,
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
    configure = SCENE_BUILDERS[name]
    configure(game)
    return game


def render_scene(name: str, language: str) -> pygame.Surface:
    game = build_scene(name, language)
    game.draw()
    return game.screen.copy()
