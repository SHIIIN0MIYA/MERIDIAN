import os
from pathlib import Path
import tempfile

import pygame
import pytest

from meridian import Game
from meridian import system, tank_battle
from meridian.ui_components import draw_pixel_panel


SCREEN = pygame.Rect(0, 0, 1280, 720)


@pytest.fixture
def game():
    pygame.init()
    test_root = Path.cwd() / "tests" / ".tmp"
    test_root.mkdir(exist_ok=True)
    temp = tempfile.TemporaryDirectory(dir=test_root)
    previous = os.environ.get("MERIDIAN_SAVE_PATH")
    os.environ["MERIDIAN_SAVE_PATH"] = str(Path(temp.name) / "ui-layout.json")
    instance = Game()
    yield instance
    if previous is None:
        os.environ.pop("MERIDIAN_SAVE_PATH", None)
    else:
        os.environ["MERIDIAN_SAVE_PATH"] = previous
    temp.cleanup()


def assert_protected_group(rects):
    assert rects
    assert all(SCREEN.contains(rect) for rect in rects)
    for index, left in enumerate(rects):
        for right in rects[index + 1:]:
            assert not left.colliderect(right), f"protected rects overlap: {left} / {right}"


def test_settings_profile_achievement_and_lore_layouts_are_protected(game):
    layouts = game._protected_system_layouts()

    assert set(layouts) == {
        "settings_buttons",
        "profile_buttons",
        "achievement_badges",
        "achievement_navigation",
        "lore_tabs",
        "lore_entries",
    }
    for rects in layouts.values():
        assert_protected_group(rects)


def test_tank_menu_pause_and_end_layouts_are_protected(game):
    layouts = game._protected_tank_layouts()

    assert set(layouts) == {
        "menu_buttons",
        "pause_content",
        "end_cards",
        "end_buttons",
    }
    for rects in layouts.values():
        assert_protected_group(rects)


def test_draw_pixel_panel_requires_integer_pixel_border():
    surface = pygame.Surface((40, 40))
    palette = {"outline": (1, 2, 3), "panel": (4, 5, 6)}

    with pytest.raises(TypeError, match="integer"):
        draw_pixel_panel(surface, (2, 2, 30, 30), palette, border=2.5)


def test_protected_system_and_tank_drawers_delegate_shared_primitives(game, monkeypatch):
    calls = {"system_panel": 0, "tank_panel": 0, "text": 0, "anchor": 0}

    original_panel = draw_pixel_panel
    original_text = system.fit_pixel_text
    original_anchor = system.anchored_blit

    def system_panel(*args, **kwargs):
        calls["system_panel"] += 1
        return original_panel(*args, **kwargs)

    def tank_panel(*args, **kwargs):
        calls["tank_panel"] += 1
        return original_panel(*args, **kwargs)

    def shared_text(*args, **kwargs):
        calls["text"] += 1
        return original_text(*args, **kwargs)

    def shared_anchor(*args, **kwargs):
        calls["anchor"] += 1
        return original_anchor(*args, **kwargs)

    monkeypatch.setattr(system, "draw_pixel_panel", system_panel)
    monkeypatch.setattr(system, "fit_pixel_text", shared_text)
    monkeypatch.setattr(system, "anchored_blit", shared_anchor)
    monkeypatch.setattr(tank_battle, "draw_pixel_panel", tank_panel)

    game._draw_system_settings()
    game._draw_profile()
    game._draw_achievement_wall()
    game._draw_lore_reader()
    game._draw_tank_menu()
    game._draw_tank_controls()
    game._draw_tank_end()

    assert calls["system_panel"] >= 8
    assert calls["tank_panel"] >= 8
    assert calls["text"] >= 4
    assert calls["anchor"] >= 4
