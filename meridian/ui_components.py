"""Shared pixel-art drawing and layout primitives."""

from __future__ import annotations

import pygame

from .common import render_pixel_text


def fit_pixel_text(
    font: pygame.font.Font,
    text: str,
    color: tuple[int, int, int],
    max_width: int,
    preferred_scale: int = 2,
) -> pygame.Surface:
    """Render text at the largest fitting integer pixel scale, then crop if needed."""
    max_width = int(max_width)
    if max_width < 1:
        raise ValueError("max_width must be positive")

    for scale in range(max(1, int(preferred_scale)), 0, -1):
        rendered = render_pixel_text(font, text, color, scale=scale)
        if rendered.get_width() <= max_width:
            return rendered

    return rendered.subsurface((0, 0, max_width, rendered.get_height())).copy()


def draw_pixel_panel(
    surface: pygame.Surface,
    rect: pygame.Rect | tuple[int, int, int, int],
    palette: dict[str, tuple[int, int, int]],
    border: int = 5,
) -> pygame.Rect:
    """Draw a square pixel panel using an integer-pixel inset border."""
    if isinstance(border, bool) or not isinstance(border, int):
        raise TypeError("border must be an integer pixel count")
    if border < 0:
        raise ValueError("border must not be negative")
    panel_rect = pygame.Rect(rect)
    pygame.draw.rect(surface, palette["outline"], panel_rect)
    inner = panel_rect.inflate(-2 * border, -2 * border)
    if inner.width > 0 and inner.height > 0:
        pygame.draw.rect(surface, palette["panel"], inner)
    return panel_rect


def anchored_blit(
    surface: pygame.Surface,
    image: pygame.Surface,
    rect: pygame.Rect | tuple[int, int, int, int],
    anchor: str,
) -> pygame.Rect:
    """Blit an image using a stable center, midleft, or midright anchor."""
    target = pygame.Rect(rect)
    if anchor not in {"center", "midleft", "midright"}:
        raise ValueError(f"unsupported anchor: {anchor}")

    placed = image.get_rect()
    setattr(placed, anchor, getattr(target, anchor))
    surface.blit(image, placed)
    return placed
