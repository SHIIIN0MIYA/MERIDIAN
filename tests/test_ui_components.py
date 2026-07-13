import pygame
import pytest

from meridian import arcade_common
from meridian.common import render_pixel_text
from meridian.ui_components import anchored_blit, draw_pixel_panel, fit_pixel_text


WHITE = (255, 255, 255)


@pytest.fixture(autouse=True)
def pygame_font():
    pygame.font.init()
    yield


@pytest.fixture
def font():
    return pygame.font.Font(None, 18)


def test_fit_pixel_text_keeps_preferred_integer_scale_when_it_fits(font):
    result = fit_pixel_text(font, "OK", WHITE, 200, preferred_scale=3)
    expected = render_pixel_text(font, "OK", WHITE, scale=3)

    assert result.get_size() == expected.get_size()


def test_fit_pixel_text_steps_down_to_an_integer_scale(font):
    scale_two = render_pixel_text(font, "PLAYER", WHITE, scale=2)
    result = fit_pixel_text(
        font,
        "PLAYER",
        WHITE,
        scale_two.get_width(),
        preferred_scale=3,
    )

    assert result.get_size() == scale_two.get_size()


def test_fit_pixel_text_never_exceeds_width(font):
    result = fit_pixel_text(
        font,
        "玩家档案统计页面",
        WHITE,
        90,
        preferred_scale=3,
    )
    scale_one = render_pixel_text(font, "玩家档案统计页面", WHITE, scale=1)

    assert result.get_width() <= 90
    assert result.get_height() == scale_one.get_height()


def test_draw_pixel_panel_returns_rect_and_uses_palette():
    screen = pygame.Surface((80, 60))
    box = pygame.Rect(10, 8, 50, 40)
    palette = {"outline": (11, 12, 13), "panel": (21, 22, 23)}

    drawn = draw_pixel_panel(screen, box, palette, border=5)

    assert drawn == box
    assert screen.get_at(box.topleft)[:3] == palette["outline"]
    assert screen.get_at(box.center)[:3] == palette["panel"]


@pytest.mark.parametrize(
    ("anchor", "attribute"),
    [("center", "center"), ("midleft", "midleft"), ("midright", "midright")],
)
def test_anchored_blit_places_supported_anchors(anchor, attribute):
    screen = pygame.Surface((100, 80))
    image = pygame.Surface((17, 9))
    box = pygame.Rect(20, 10, 60, 50)

    placed = anchored_blit(screen, image, box, anchor)

    assert getattr(placed, attribute) == getattr(box, attribute)


def test_right_anchor_is_stable_for_different_text_widths():
    screen = pygame.Surface((160, 80))
    short_image = pygame.Surface((20, 10))
    long_image = pygame.Surface((70, 10))
    box = pygame.Rect(20, 10, 110, 50)

    short = anchored_blit(screen, short_image, box, "midright")
    long = anchored_blit(screen, long_image, box, "midright")

    assert short.right == long.right == box.right


def test_anchored_blit_rejects_unknown_anchor():
    screen = pygame.Surface((40, 40))

    with pytest.raises(ValueError, match="anchor"):
        anchored_blit(screen, pygame.Surface((5, 5)), screen.get_rect(), "topright")


def test_arcade_drawers_delegate_shared_ui_primitives(monkeypatch, font):
    calls = {"panel": 0, "text": 0, "blit": 0}

    def record_panel(*args, **kwargs):
        calls["panel"] += 1
        return draw_pixel_panel(*args, **kwargs)

    def record_text(*args, **kwargs):
        calls["text"] += 1
        return fit_pixel_text(*args, **kwargs)

    def record_blit(*args, **kwargs):
        calls["blit"] += 1
        return anchored_blit(*args, **kwargs)

    monkeypatch.setattr(arcade_common, "draw_pixel_panel", record_panel)
    monkeypatch.setattr(arcade_common, "fit_pixel_text", record_text)
    monkeypatch.setattr(arcade_common, "anchored_blit", record_blit)

    game = type("ArcadeHarness", (), {})()
    game.screen = pygame.Surface((1280, 720))
    game.font_btn = font
    game.font_small = font
    game.font_menu_title = font
    palette = {
        "bg": (1, 2, 3),
        "panel": (4, 5, 6),
        "panel_dark": (7, 8, 9),
        "accent": (10, 11, 12),
        "accent_light": (13, 14, 15),
        "text": (16, 17, 18),
        "hover": (19, 20, 21),
    }

    arcade_common.draw_arcade_frame(game, "TITLE", "SUBTITLE", palette)
    arcade_common.draw_arcade_button(
        game,
        arcade_common.arcade_button((500, 300, 250, 48), "BUTTON", "action"),
        palette,
    )
    arcade_common.draw_pause_overlay(game, palette)

    assert calls["panel"] == 3
    assert calls["text"] == 5
    assert calls["blit"] == 5
