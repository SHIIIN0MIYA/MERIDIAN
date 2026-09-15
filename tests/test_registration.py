from __future__ import annotations

import os
from pathlib import Path
import uuid

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
# Skip ~2s of procedural audio synthesis; no test asserts on sound output.
os.environ.setdefault("MERIDIAN_FAST_AUDIO", "1")

import pytest

from meridian import app, localization, shell_desktop
from meridian.app import Game
from meridian.common import pygame
from meridian.shell_desktop import DesktopMixin


class DesktopHarness(DesktopMixin):
    MENU = "menu"
    SNAKE_MENU = "snake_menu"
    BREAKOUT_MENU = "breakout_menu"
    G2048_MENU = "g2048_menu"
    MINES_MENU = "mines_menu"
    TETRIS_MENU = "tetris_menu"
    AIR_MENU = "air_menu"
    TANK_MENU = "tank_menu"
    SYSTEM_SETTINGS = "system_settings"
    PROFILE = "profile"
    ACHIEVEMENT_WALL = "achievement_wall"
    LORE_READER = "lore_reader"

    def __init__(self):
        self.transitions = []
        self._desktop_return_effect = "fade"
        self._init_desktop()

    def _start_transition(self, target, effect, frames=32):
        self.transitions.append((target, effect, frames))


@pytest.fixture(autouse=True)
def isolate_registration_globals():
    states = list(app._GAME_STATE_REGISTRY)
    initializers = list(app._GAME_INITIALIZER_REGISTRY)
    icons = [icon.copy() for icon in shell_desktop.DESKTOP_ICON_REGISTRY]
    translations = dict(localization.ZH)
    owners = dict(localization._TRANSLATION_OWNERS)

    app._GAME_STATE_REGISTRY.clear()
    app._GAME_INITIALIZER_REGISTRY.clear()
    shell_desktop.DESKTOP_ICON_REGISTRY.clear()
    yield

    app._GAME_STATE_REGISTRY[:] = states
    app._GAME_INITIALIZER_REGISTRY[:] = initializers
    shell_desktop.DESKTOP_ICON_REGISTRY[:] = icons
    localization.ZH.clear()
    localization.ZH.update(translations)
    localization._TRANSLATION_OWNERS.clear()
    localization._TRANSLATION_OWNERS.update(owners)


@pytest.fixture(autouse=True)
def pygame_runtime():
    pygame.init()
    yield
    pygame.quit()


def test_builtin_icons_are_instance_local_and_extensions_default_to_page_three():
    shell_desktop.register_desktop_icon(
        "PLUGIN", "open_plugin", target_state="PLUGIN_MENU"
    )

    desktop = DesktopHarness()

    assert [len(page) for page in desktop.desktop_pages] == [6, 6, 1]
    assert sum(len(page) for page in desktop.desktop_pages[:2]) == 12
    assert desktop.desktop_pages[2][0]["action"] == "open_plugin"
    assert len(shell_desktop.DESKTOP_ICON_REGISTRY) == 1


def test_desktop_registration_rejects_invalid_pages_routes_actions_and_capacity():
    def callback(game):
        return None

    with pytest.raises(ValueError, match="negative"):
        shell_desktop.register_desktop_icon(
            "BAD", "bad_page", page=-1, on_activate=callback
        )
    with pytest.raises(ValueError, match="exactly one"):
        shell_desktop.register_desktop_icon("NO ROUTE", "no_route")
    with pytest.raises(ValueError, match="exactly one"):
        shell_desktop.register_desktop_icon(
            "TWO ROUTES", "two_routes", target_state="MENU", on_activate=callback
        )
    with pytest.raises(ValueError, match="already registered"):
        shell_desktop.register_desktop_icon(
            "CORE", "open_gomoku", on_activate=callback
        )
    with pytest.raises(ValueError, match="6 icons"):
        shell_desktop.register_desktop_icon(
            "FULL", "page_zero_full", page=0, on_activate=callback
        )

    for index in range(6):
        shell_desktop.register_desktop_icon(
            f"PLUGIN {index}", f"plugin_{index}", on_activate=callback
        )
    with pytest.raises(ValueError, match="6 icons"):
        shell_desktop.register_desktop_icon(
            "OVERFLOW", "plugin_overflow", on_activate=callback
        )
    with pytest.raises(ValueError, match="already registered"):
        shell_desktop.register_desktop_icon(
            "DUPLICATE", "plugin_0", page=3, on_activate=callback
        )


def test_desktop_uses_target_and_callback_routes_and_blocks_disabled_mouse_input():
    callbacks = []
    shell_desktop.register_desktop_icon(
        "TARGET",
        "open_target",
        target_state="PLUGIN_MENU",
        transition_effect="scan",
        transition_frames=41,
        return_effect="plugin_return",
    )
    shell_desktop.register_desktop_icon(
        "CALLBACK",
        "run_callback",
        on_activate=lambda game: callbacks.append(game),
    )
    shell_desktop.register_desktop_icon(
        "DISABLED",
        "disabled_callback",
        enabled=False,
        on_activate=lambda game: callbacks.append("disabled"),
    )
    desktop = DesktopHarness()

    target, callback, disabled = desktop.desktop_pages[2]
    assert desktop._activate_desktop_button(target)
    assert desktop.transitions == [("PLUGIN_MENU", "scan", 41)]
    assert desktop._desktop_return_effect == "plugin_return"
    assert desktop._activate_desktop_button(callback)
    assert callbacks == [desktop]
    assert desktop._desktop_return_effect == "fade"
    assert not desktop._activate_desktop_button(disabled)

    desktop.desktop_page = 2
    disabled_button = desktop._get_desktop_icon_buttons()[2]
    for event_type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
        desktop._handle_desktop_event(pygame.event.Event(
            event_type,
            {"button": 1, "pos": disabled_button["rect"].center},
        ))
    assert callbacks == [desktop]
    assert desktop.desktop_pressed_action is None


def test_callable_and_string_state_handlers_build_and_invoke(monkeypatch):
    calls = []

    def event_handler(game, event):
        calls.append(("event", game, event))

    def update_handler(game):
        calls.append(("update", game))

    def draw_method(self):
        calls.append(("draw", self))

    monkeypatch.setattr(Game, "_draw_plugin", draw_method, raising=False)
    app.register_game_state(
        "plugin_state",
        event_handler,
        [update_handler],
        "_draw_plugin",
    )
    game = object.__new__(Game)
    game._build_dispatch()

    marker = object()
    game._invoke_dispatch_handler(game._EVENT_DISPATCH["plugin_state"], marker)
    game._invoke_dispatch_handler(game._UPDATE_DISPATCH["plugin_state"][1][0])
    game._invoke_dispatch_handler(game._DRAW_DISPATCH["plugin_state"])

    assert calls == [
        ("event", game, marker),
        ("update", game),
        ("draw", game),
    ]


def test_state_registration_rejects_core_duplicates_and_missing_methods():
    with pytest.raises(ValueError, match="core game state"):
        app.register_game_state("DESKTOP", None, [], None)

    app.register_game_state("plugin_state", None, [], None)
    with pytest.raises(ValueError, match="already registered"):
        app.register_game_state("plugin_state", None, [], None)

    app._GAME_STATE_REGISTRY.clear()
    app.register_game_state("broken_state", "_missing_plugin_handler", [], None)
    with pytest.raises(AttributeError, match="_missing_plugin_handler"):
        object.__new__(Game)._build_dispatch()

    app._GAME_STATE_REGISTRY.clear()
    with pytest.raises(TypeError, match="update_methods entries"):
        app.register_game_state("none_update", None, [None], None)


def test_legacy_state_wrapper_and_new_registrations_only_affect_later_instances():
    earlier = object.__new__(Game)
    earlier._build_dispatch()

    app._register_game_states("later_state", None, [], None)
    later = object.__new__(Game)
    later._build_dispatch()

    assert "later_state" not in earlier._UPDATE_DISPATCH
    assert "later_state" in later._UPDATE_DISPATCH


def test_initializer_runs_after_system_loading_and_before_dispatch(monkeypatch):
    save_root = Path(os.environ.get("MERIDIAN_TEST_SAVE_ROOT", Path.cwd()))
    save_path = save_root / f".meridian-registration-test-{uuid.uuid4().hex}.json"
    monkeypatch.setenv("MERIDIAN_SAVE_PATH", str(save_path))
    observations = []

    def initialize(game):
        observations.append((
            hasattr(game, "save_data"),
            hasattr(game, "_EVENT_DISPATCH"),
        ))
        game.PLUGIN_MENU = "plugin_menu"

    app.register_game_initializer(initialize)
    app.register_game_state("PLUGIN_MENU", None, [], None)
    game = Game()
    try:
        assert observations == [(True, False)]
        assert "plugin_menu" in game._UPDATE_DISPATCH
    finally:
        game.audio.stop()
        for path in (
            save_path,
            save_path.with_suffix(save_path.suffix + ".bak"),
            save_path.with_suffix(save_path.suffix + ".tmp"),
        ):
            path.unlink(missing_ok=True)


def test_translation_registration_tracks_ownership_and_requires_explicit_replace():
    localization.register_game_translations("alpha", {"PLUGIN PLAY": "插件开始"})
    localization.register_game_translations("alpha", {"PLUGIN PLAY": "开始插件"})

    with pytest.raises(ValueError, match="owned by"):
        localization.register_game_translations(
            "beta", {"PLUGIN PLAY": "其他开始"}
        )
    assert localization.ZH["PLUGIN PLAY"] == "开始插件"
    assert localization._TRANSLATION_OWNERS["PLUGIN PLAY"] == "alpha"

    localization.register_game_translations(
        "beta", {"PLUGIN PLAY": "其他开始"}, replace=True
    )
    assert localization.ZH["PLUGIN PLAY"] == "其他开始"
    assert localization._TRANSLATION_OWNERS["PLUGIN PLAY"] == "beta"


def test_translation_conflicts_are_atomic_and_core_keys_are_protected():
    core_key = next(iter(localization.ZH))
    core_value = localization.ZH[core_key]

    with pytest.raises(ValueError, match="reserved"):
        localization.register_game_translations(
            "__core__", {core_key: "覆盖"}
        )
    with pytest.raises(ValueError, match="owned by"):
        localization.register_game_translations(
            "plugin", {"NEW PLUGIN KEY": "新值", core_key: "覆盖"}
        )

    assert "NEW PLUGIN KEY" not in localization.ZH
    assert localization.ZH[core_key] == core_value
