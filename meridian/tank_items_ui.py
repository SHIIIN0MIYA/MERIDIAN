"""Pixel icons and readable status for Tank Duel tactical items."""

from __future__ import annotations

from dataclasses import dataclass

from .common import pygame
from .tank_engine import ItemType


@dataclass(frozen=True)
class ItemStatus:
    item: ItemType | None
    active: bool = False
    remaining_ms: int = 0
    count: int = 0


def item_status(engine, player_id: str) -> ItemStatus:
    tank = engine.tanks[player_id]
    item = tank.held_item
    if item is ItemType.SHIELD:
        return ItemStatus(item, tank.shield_until_ms > engine.elapsed_ms,
                          max(0, tank.shield_until_ms - engine.elapsed_ms))
    if item is ItemType.SPEED:
        return ItemStatus(item, tank.speed_until_ms > engine.elapsed_ms,
                          max(0, tank.speed_until_ms - engine.elapsed_ms))
    if item is ItemType.EMP:
        return ItemStatus(item, tank.fire_locked_until_ms > engine.elapsed_ms,
                          max(0, tank.fire_locked_until_ms - engine.elapsed_ms))
    if item is ItemType.PIERCING:
        return ItemStatus(item, tank.piercing_shots > 0, count=tank.piercing_shots)
    return ItemStatus(item)


def draw_item_icon(surface, item: ItemType, rect, palette, active: bool = False) -> None:
    """Draw one of eight distinct code-defined pixel icons."""
    box = pygame.Rect(rect)
    color = palette.get("active") if active else palette.get("accent")
    color = color or (128, 232, 224)
    dark = palette.get("dark", (8, 18, 22))
    outline = palette.get("outline", (3, 5, 7))
    pygame.draw.rect(surface, outline, box)
    inner = box.inflate(-4, -4)
    pygame.draw.rect(surface, dark, inner)
    cx, cy = box.center
    scale = max(1, min(box.width, box.height) // 12)
    def line(points, width=2):
        pygame.draw.lines(surface, color, False, points, max(1, width * scale))
    if item is ItemType.REPAIR:
        pygame.draw.rect(surface, color, (cx - scale, cy - 4*scale, 2*scale, 8*scale))
        pygame.draw.rect(surface, color, (cx - 4*scale, cy - scale, 8*scale, 2*scale))
    elif item is ItemType.SHIELD:
        pygame.draw.polygon(surface, color, [(cx, cy-5*scale), (cx+4*scale, cy-3*scale),
            (cx+3*scale, cy+3*scale), (cx, cy+5*scale), (cx-3*scale, cy+3*scale), (cx-4*scale, cy-3*scale)], 2*scale)
    elif item is ItemType.SPEED:
        line([(cx-5*scale, cy-2*scale), (cx, cy-2*scale), (cx-2*scale, cy+2*scale), (cx+5*scale, cy+2*scale)])
        line([(cx, cy-5*scale), (cx+4*scale, cy), (cx, cy+5*scale)])
    elif item is ItemType.MINE:
        pygame.draw.circle(surface, color, (cx, cy), 4*scale, 2*scale)
        for dx, dy in ((0,-1),(1,0),(0,1),(-1,0)):
            line([(cx+dx*4*scale, cy+dy*4*scale), (cx+dx*6*scale, cy+dy*6*scale)], 1)
    elif item is ItemType.EMP:
        for radius in (2, 5):
            pygame.draw.arc(surface, color, (cx-radius*scale, cy-radius*scale, radius*2*scale, radius*2*scale), .35, 2.8, scale)
        pygame.draw.rect(surface, color, (cx-1*scale, cy-1*scale, 2*scale, 2*scale))
    elif item is ItemType.PIERCING:
        pygame.draw.polygon(surface, color, [(cx+6*scale, cy), (cx, cy-3*scale), (cx, cy-1*scale), (cx-6*scale, cy-1*scale), (cx-6*scale, cy+1*scale), (cx, cy+1*scale), (cx, cy+3*scale)])
    elif item is ItemType.SMOKE:
        for dx, dy, radius in ((-3,1,3),(0,-2,4),(3,1,3)):
            pygame.draw.circle(surface, color, (cx+dx*scale, cy+dy*scale), radius*scale, scale)
    else:  # WARP
        pygame.draw.rect(surface, color, (cx-5*scale, cy-5*scale, 3*scale, 10*scale), scale)
        pygame.draw.rect(surface, color, (cx+2*scale, cy-5*scale, 3*scale, 10*scale), scale)
        line([(cx-2*scale, cy), (cx+2*scale, cy)])


__all__ = ["ItemStatus", "draw_item_icon", "item_status"]
