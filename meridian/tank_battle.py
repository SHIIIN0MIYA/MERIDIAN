"""Pygame presentation and two-player controls for Tank Duel."""

from __future__ import annotations

import math
import random

from .arcade_common import (
    arcade_button,
    draw_arcade_button,
    draw_arcade_frame,
    draw_pause_overlay,
    handle_arcade_buttons,
)
from .common import C, WINDOW_H, WINDOW_W, pygame, render_pixel_text
from .tank_engine import (
    ARENA_COLS,
    ARENA_ROWS,
    EngineEvent,
    ItemType,
    MatchPhase,
    PlayerCommand,
    TankBattleEngine,
    Terrain,
)


TANK_PALETTE = {
    "bg": C.TANK_BG,
    "panel": C.TANK_PANEL,
    "panel_dark": C.TANK_PANEL_DARK,
    "accent": C.TANK_ACCENT,
    "accent_light": C.TANK_ACCENT_LIGHT,
    "text": C.TANK_TEXT,
    "hover": (42, 67, 65),
}

_SOUNDS = {
    "shot": "tank_shot",
    "bullet_clash": "tank_clash",
    "brick_hit": "tank_brick",
    "tank_hit": "tank_hit",
    "tank_destroyed": "tank_explosion",
    "pickup": "tank_pickup",
    "item_used": "tank_item",
    "sudden_death": "tank_alarm",
}

_PLAYER_KEYS = {
    "red": {"left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "down": pygame.K_s},
    "blue": {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "up": pygame.K_UP, "down": pygame.K_DOWN},
}
_ITEM_KEYS = {pygame.K_f: "red", pygame.K_RETURN: "blue", pygame.K_KP_ENTER: "blue"}


class TankBattleMixin:
    """Rendering-only integration layer; app routing is deliberately external."""

    def _init_tank_battle(self):
        self.tank_engine = TankBattleEngine()
        self.tank_pressed_action = None
        self.tank_paused = False
        self.tank_particles = []
        self.tank_shake_frames = 0
        self.tank_shake_x = self.tank_shake_y = 0
        self._tank_key_clock = 0
        self._tank_held = {}
        self._tank_item_pulses = {"red": False, "blue": False}

    def _tank_buttons(self, page):
        if page == "menu":
            return [
                arcade_button((520, 350, 240, 52), "START DUEL", "start"),
                arcade_button((520, 424, 240, 52), "CONTROLS", "controls"),
                arcade_button((520, 498, 240, 52), "DESKTOP", "desktop"),
            ]
        return [
            arcade_button((410, 550, 210, 52), "REMATCH", "start"),
            arcade_button((660, 550, 210, 52), "MENU", "menu"),
        ]

    def _start_tank_battle(self):
        self.tank_engine = TankBattleEngine()
        self.tank_paused = False
        self._tank_held.clear()
        self._tank_item_pulses = {"red": False, "blue": False}
        self.state = getattr(self, "TANK_PLAYING", "tank_playing")

    def _handle_tank_menu_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_desktop()
            return
        actions = {
            "start": self._start_tank_battle,
            "controls": lambda: setattr(self, "state", getattr(self, "TANK_CONTROLS", "tank_controls")),
            "desktop": self._go_desktop,
        }
        handle_arcade_buttons(self, event, self._tank_buttons("menu"), "tank_pressed_action", actions)

    def _handle_tank_controls_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.state = getattr(self, "TANK_MENU", "tank_menu")

    def _handle_tank_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = getattr(self, "TANK_MENU", "tank_menu")
                return
            if event.key == pygame.K_p:
                self.tank_paused = not self.tank_paused
                self.tank_engine.paused = self.tank_paused
                return
            if event.key in _ITEM_KEYS and not self._tank_held.get(event.key):
                self._tank_item_pulses[_ITEM_KEYS[event.key]] = True
            if event.key not in self._tank_held:
                self._tank_key_clock += 1
                self._tank_held[event.key] = self._tank_key_clock
        elif event.type == pygame.KEYUP:
            self._tank_held.pop(event.key, None)

    def _handle_tank_end_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._start_tank_battle()
            elif event.key == pygame.K_ESCAPE:
                self.state = getattr(self, "TANK_MENU", "tank_menu")
            return
        actions = {
            "start": self._start_tank_battle,
            "menu": lambda: setattr(self, "state", getattr(self, "TANK_MENU", "tank_menu")),
        }
        handle_arcade_buttons(self, event, self._tank_buttons("end"), "tank_pressed_action", actions)

    def _tank_axis(self, negative, positive):
        candidates = [(self._tank_held[key], value) for key, value in ((negative, -1), (positive, 1)) if key in self._tank_held]
        return max(candidates, default=(0, 0))[1]

    def _tank_command(self, player_id):
        keys = _PLAYER_KEYS[player_id]
        use_item = self._tank_item_pulses[player_id]
        self._tank_item_pulses[player_id] = False
        return PlayerCommand(
            self._tank_axis(keys["left"], keys["right"]),
            self._tank_axis(keys["up"], keys["down"]),
            use_item,
        )

    def _update_tank_battle(self, dt_ms=16):
        if self.tank_paused:
            return
        commands = {player: self._tank_command(player) for player in ("red", "blue")}
        events = self.tank_engine.update(max(0, int(dt_ms)), commands)
        self._handle_tank_engine_events(events)
        if self.tank_engine.phase is MatchPhase.ENDED:
            self.state = getattr(self, "TANK_END", "tank_end")
        if self.tank_shake_frames:
            self.tank_shake_frames -= 1
            self.tank_shake_x = random.randint(-3, 3)
            self.tank_shake_y = random.randint(-3, 3)
        else:
            self.tank_shake_x = self.tank_shake_y = 0
        for particle in self.tank_particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 1
        self.tank_particles[:] = [p for p in self.tank_particles if p["life"] > 0]

    def _handle_tank_engine_events(self, events):
        for event in events:
            sound = _SOUNDS.get(event.kind)
            if sound:
                self.audio.play(sound)
            if event.kind in {"tank_hit", "tank_destroyed", "mine_triggered"}:
                self.tank_shake_frames = max(self.tank_shake_frames, 8)
            if event.kind in _SOUNDS:
                tank = self.tank_engine.tanks.get(event.player_id or "red")
                if tank:
                    for index in range(6):
                        angle = index * math.tau / 6
                        self.tank_particles.append({"x": tank.x, "y": tank.y, "vx": math.cos(angle) * .05, "vy": math.sin(angle) * .05, "life": 14})

    def _capture_tank_run_state(self):
        return self.tank_engine.to_dict()

    def _restore_tank_run_state(self, snapshot):
        self.tank_engine = TankBattleEngine.from_dict(snapshot)
        self.tank_paused = self.tank_engine.paused
        self._tank_held.clear()
        self._tank_item_pulses = {"red": False, "blue": False}

    def _draw_tank_menu(self):
        outer = draw_arcade_frame(self, "TANK DUEL", "LOCAL TWO-PLAYER ARENA", TANK_PALETTE)
        self._draw_tank_emblem(outer.centerx, 245)
        mouse = self._logical_mouse_pos()
        for button in self._tank_buttons("menu"):
            draw_arcade_button(self, button, TANK_PALETTE, button["rect"].collidepoint(mouse), self.tank_pressed_action == button["action"])

    def _draw_tank_controls(self):
        draw_arcade_frame(self, "CONTROLS", "TWO CREWS / ONE KEYBOARD", TANK_PALETTE)
        lines = ["RED: W A S D    ITEM: F", "BLUE: ARROW KEYS    ITEM: ENTER", "MOVE IN 8 DIRECTIONS", "P: PAUSE    ESC: MENU"]
        panel = pygame.Rect(280, 190, 720, 350)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, C.TANK_PANEL_DARK, panel.inflate(-10, -10))
        for index, line in enumerate(lines):
            text = render_pixel_text(self.font_status, line, C.TANK_TEXT, scale=2)
            self.screen.blit(text, (panel.centerx - text.get_width() // 2, 245 + index * 62))

    def _draw_tank_playing(self):
        self.screen.fill(C.TANK_BG)
        self._draw_tank_hud()
        arena = pygame.Rect(40 + self.tank_shake_x, 112 + self.tank_shake_y, 1200, 540)
        tile = min(arena.width // ARENA_COLS, arena.height // ARENA_ROWS)
        arena.size = (tile * ARENA_COLS, tile * ARENA_ROWS)
        arena.centerx = WINDOW_W // 2 + self.tank_shake_x
        pygame.draw.rect(self.screen, C.OUTLINE, arena.inflate(8, 8))
        pygame.draw.rect(self.screen, C.TANK_GROUND, arena)
        grasses = []
        for y, row in enumerate(self.tank_engine.arena.rows):
            for x, cell in enumerate(row):
                rect = pygame.Rect(arena.x + x * tile, arena.y + y * tile, tile, tile)
                pygame.draw.rect(self.screen, C.TANK_GRID, rect, 1)
                if cell == Terrain.BRICK.value:
                    self._draw_brick(rect)
                elif cell == Terrain.STEEL.value:
                    self._draw_steel(rect)
                elif cell == Terrain.GRASS.value:
                    grasses.append(rect)
        if self.tank_engine.pickup:
            self._draw_pickup(arena, tile)
        for mine in self.tank_engine.mines:
            px, py = self._world_point(arena, tile, mine.x, mine.y)
            pygame.draw.rect(self.screen, C.OUTLINE, (px - 5, py - 5, 10, 10))
            pygame.draw.rect(self.screen, C.TANK_ACCENT, (px - 3, py - 3, 6, 6))
        for bullet in self.tank_engine.bullets:
            px, py = self._world_point(arena, tile, bullet.x, bullet.y)
            pygame.draw.rect(self.screen, C.TANK_ACCENT_LIGHT, (px - 3, py - 3, 6, 6))
        for player_id, tank in self.tank_engine.tanks.items():
            self._draw_tank_entity(arena, tile, player_id, tank)
        for particle in self.tank_particles:
            px, py = self._world_point(arena, tile, particle["x"], particle["y"])
            pygame.draw.rect(self.screen, C.TANK_ACCENT_LIGHT, (px - 2, py - 2, 4, 4))
        # Grass is intentionally the final arena layer so tanks can hide beneath it.
        for rect in grasses:
            pygame.draw.rect(self.screen, C.TANK_GRASS, rect)
            pygame.draw.rect(self.screen, (83, 146, 70), (rect.x + 4, rect.y + 4, rect.width - 8, 4))
        if self.tank_paused:
            draw_pause_overlay(self, TANK_PALETTE)

    def _draw_tank_end(self):
        self._draw_tank_playing()
        shade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        shade.fill(C.OVERLAY_END)
        self.screen.blit(shade, (0, 0))
        panel = pygame.Rect(330, 190, 620, 430)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, C.TANK_PANEL, panel.inflate(-10, -10))
        winner = self.tank_engine.winner
        title = "DRAW" if winner is None else f"{winner.upper()} WINS"
        text = render_pixel_text(self.font_menu_title, title, C.TANK_ACCENT_LIGHT, scale=4)
        self.screen.blit(text, (panel.centerx - text.get_width() // 2, 255))
        score = render_pixel_text(self.font_status, f"RED {self.tank_engine.score['red']}  :  {self.tank_engine.score['blue']} BLUE", C.TANK_TEXT, scale=3)
        self.screen.blit(score, (panel.centerx - score.get_width() // 2, 365))
        mouse = self._logical_mouse_pos()
        for button in self._tank_buttons("end"):
            draw_arcade_button(self, button, TANK_PALETTE, button["rect"].collidepoint(mouse), self.tank_pressed_action == button["action"])

    def _draw_tank_hud(self):
        pygame.draw.rect(self.screen, C.TANK_PANEL, (40, 28, 1200, 66))
        pygame.draw.rect(self.screen, C.OUTLINE, (40, 28, 1200, 66), 4)
        red = self.tank_engine.tanks["red"]
        blue = self.tank_engine.tanks["blue"]
        remain = max(0, self.tank_engine.remaining_ms // 1000)
        labels = [
            (f"RED  HP {red.hp}  {self._item_label(red.held_item)}", 70, C.TANK_RED_LIGHT),
            (f"{remain // 60:02d}:{remain % 60:02d}   {self.tank_engine.score['red']} : {self.tank_engine.score['blue']}", 515, C.TANK_ACCENT_LIGHT),
            (f"{self._item_label(blue.held_item)}  HP {blue.hp}  BLUE", 920, C.TANK_BLUE_LIGHT),
        ]
        for label, x, color in labels:
            self.screen.blit(render_pixel_text(self.font_status, label, color, scale=2), (x, 49))

    @staticmethod
    def _item_label(item):
        return "ITEM --" if item is None else f"ITEM {item.value.upper()}"

    @staticmethod
    def _world_point(arena, tile, x, y):
        return int(arena.x + x * tile), int(arena.y + y * tile)

    def _draw_brick(self, rect):
        pygame.draw.rect(self.screen, C.TANK_BRICK, rect)
        pygame.draw.rect(self.screen, C.OUTLINE, rect, 2)
        pygame.draw.line(self.screen, C.TANK_ACCENT, rect.midleft, rect.midright, 2)

    def _draw_steel(self, rect):
        pygame.draw.rect(self.screen, C.TANK_STEEL, rect)
        pygame.draw.rect(self.screen, C.OUTLINE, rect, 2)
        pygame.draw.rect(self.screen, (190, 205, 199), rect.inflate(-10, -10), 2)

    def _draw_pickup(self, arena, tile):
        pickup = self.tank_engine.pickup
        px, py = self._world_point(arena, tile, pickup.x, pickup.y)
        pygame.draw.rect(self.screen, C.OUTLINE, (px - 10, py - 10, 20, 20))
        pygame.draw.rect(self.screen, C.TANK_ACCENT_LIGHT, (px - 7, py - 7, 14, 14))

    def _draw_tank_entity(self, arena, tile, player_id, tank):
        px, py = self._world_point(arena, tile, tank.x, tank.y)
        color = C.TANK_RED if player_id == "red" else C.TANK_BLUE
        light = C.TANK_RED_LIGHT if player_id == "red" else C.TANK_BLUE_LIGHT
        size = max(14, int(tile * .66))
        body = pygame.Rect(px - size // 2, py - size // 2, size, size)
        pygame.draw.rect(self.screen, C.OUTLINE, body.inflate(4, 4))
        pygame.draw.rect(self.screen, color, body)
        # Red uses horizontal turret marks, blue vertical marks.
        if player_id == "red":
            pygame.draw.line(self.screen, light, (body.x + 4, body.centery), (body.right - 4, body.centery), 3)
        else:
            pygame.draw.line(self.screen, light, (body.centerx, body.y + 4), (body.centerx, body.bottom - 4), 3)
        end = (px + tank.facing_x * size // 2, py + tank.facing_y * size // 2)
        pygame.draw.line(self.screen, C.OUTLINE, (px, py), end, 5)
        pygame.draw.line(self.screen, light, (px, py), end, 2)

    def _draw_tank_emblem(self, x, y):
        pygame.draw.rect(self.screen, C.TANK_RED, (x - 82, y - 20, 64, 40))
        pygame.draw.rect(self.screen, C.TANK_BLUE, (x + 18, y - 20, 64, 40))
        pygame.draw.line(self.screen, C.TANK_ACCENT_LIGHT, (x - 18, y - 34), (x + 18, y + 34), 5)
