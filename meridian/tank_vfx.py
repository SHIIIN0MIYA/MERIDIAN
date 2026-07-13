"""Deterministic event-driven visual feedback for Tank Duel."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import random

from .common import C, pygame


@dataclass
class TankVfxState:
    flashes: list[dict] = field(default_factory=list)
    trails: list[dict] = field(default_factory=list)
    particles: list[dict] = field(default_factory=list)
    rings: list[dict] = field(default_factory=list)
    score_popups: list[dict] = field(default_factory=list)
    respawn_scans: list[dict] = field(default_factory=list)
    item_effects: list[dict] = field(default_factory=list)


ITEM_EFFECT_KINDS = {
    "repair": "repair_cross", "shield": "shield_hex", "speed": "overdrive_trail",
    "mine": "mine_pulse", "emp": "emp_scan", "piercing": "piercing_glint",
    "smoke": "smoke_bloom", "warp": "warp_split",
}


def consume_engine_events(state: TankVfxState, events, effect_level="full", seed=0) -> None:
    rng = random.Random(seed)
    density = {"full": 12, "reduced": 5, "off": 0}.get(effect_level, 12)
    for event in events:
        x = float(event.data.get("x", 0.0)); y = float(event.data.get("y", 0.0))
        if event.kind == "shot" and effect_level != "off":
            state.flashes.append({"x": x, "y": y, "life": 110})
            state.trails.append({"x": x, "y": y, "life": 180})
        elif event.kind in {"tank_hit", "mine_triggered", "shield_blocked"}:
            if effect_level != "off":
                state.rings.append({"x": x, "y": y, "life": 260, "kind": event.kind})
        elif event.kind == "tank_destroyed":
            for index in range(density):
                angle = (index / max(1, density)) * math.tau + rng.uniform(-.12, .12)
                state.particles.append({"x": x, "y": y, "vx": math.cos(angle)*.004,
                    "vy": math.sin(angle)*.004, "life": 520})
            state.score_popups.append({"x": x, "y": y, "life": 900, "text": "+1"})
        elif event.kind == "respawn":
            state.respawn_scans.append({"x": x, "y": y, "life": 1200})
        elif event.kind == "item_used":
            item = str(event.data.get("item", ""))
            state.item_effects.append({"x": x, "y": y, "life": 650,
                "kind": ITEM_EFFECT_KINDS.get(item, "item")})


def update_vfx(state: TankVfxState, dt_ms: int) -> None:
    dt = max(0, int(dt_ms))
    for collection in (state.flashes, state.trails, state.particles, state.rings,
                       state.score_popups, state.respawn_scans, state.item_effects):
        for effect in collection:
            effect["life"] -= dt
            effect["x"] += effect.get("vx", 0) * dt
            effect["y"] += effect.get("vy", 0) * dt
        collection[:] = [effect for effect in collection if effect["life"] > 0]


def draw_tank_vfx(game, arena, tile, state: TankVfxState) -> None:
    def point(effect):
        return game._world_point(arena, tile, effect["x"], effect["y"])
    for trail in state.trails:
        x, y = point(trail); pygame.draw.line(game.screen, (255, 220, 110), (x-8, y), (x+8, y), 2)
    for scan in state.respawn_scans:
        x, y = point(scan); pygame.draw.rect(game.screen, C.TANK_ACCENT_LIGHT, (x-14, y-18, 28, 36), 2)
    for effect in state.item_effects:
        x, y = point(effect); radius = 8 + (effect["life"] % 10)
        pygame.draw.circle(game.screen, C.TANK_ACCENT_LIGHT, (x, y), radius, 2)
    for ring in state.rings:
        x, y = point(ring); pygame.draw.circle(game.screen, C.TANK_ACCENT, (x, y), 13, 3)
    for particle in state.particles:
        x, y = point(particle); pygame.draw.rect(game.screen, C.TANK_ACCENT_LIGHT, (x-2, y-2, 4, 4))
    for flash in state.flashes:
        x, y = point(flash); pygame.draw.circle(game.screen, (255, 235, 145), (x, y), 7)
    for popup in state.score_popups:
        x, y = point(popup); text = game.font_status.render(popup["text"], False, C.TANK_ACCENT_LIGHT)
        game.screen.blit(text, (x-text.get_width()//2, y-22))


__all__ = ["ITEM_EFFECT_KINDS", "TankVfxState", "consume_engine_events", "draw_tank_vfx", "update_vfx"]
