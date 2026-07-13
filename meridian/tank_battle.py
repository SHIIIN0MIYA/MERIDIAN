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
from .localization import get_chinese_font, is_chinese, translate
from .tank_engine import (
    ARENA_COLS,
    ARENA_ROWS,
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
    "brick_impact": "tank_brick",
    "tank_hit": "tank_hit",
    "tank_destroyed": "tank_explosion",
    "pickup": "tank_pickup",
    "item_used": "tank_item",
    "sudden_death": "tank_alarm",
    "emp_blast": "tank_alarm",
    "tank_warped": "tank_item",
}
_SOUND_VOLUMES = {
    "tank_shot": 0.46,
    "tank_clash": 0.62,
    "tank_brick": 0.58,
    "tank_hit": 0.68,
    "tank_explosion": 0.76,
    "tank_pickup": 0.62,
    "tank_item": 0.66,
    "tank_alarm": 0.72,
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
        self.tank_restore_notice = None
        self._reset_tank_tracking()

    def _reset_tank_tracking(self):
        self._tank_match_stats_recorded = False
        self._tank_match_shots = 0
        self._tank_match_hits = 0
        self._tank_max_deficit = {"red": 0, "blue": 0}
        self._tank_player_shots = {"red": 0, "blue": 0}
        self._tank_player_hits = {"red": 0, "blue": 0}
        self._tank_player_items_used = {"red": 0, "blue": 0}
        self._tank_overdrive_kills = {"red": 0, "blue": 0}
        self._tank_in_sudden_death = False

    def _tank_buttons(self, page):
        if page == "menu":
            if "tank" in getattr(self, "_pending_run_states", {}):
                return [
                    arcade_button((520, 310, 240, 52), "CONTINUE", "continue"),
                    arcade_button((520, 374, 240, 52), "NEW MATCH", "start"),
                    arcade_button((520, 438, 240, 52), "CONTROLS", "controls"),
                    arcade_button((520, 502, 240, 52), "DESKTOP", "desktop"),
                ]
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
        getattr(self, "_pending_run_states", {}).pop("tank", None)
        self.tank_engine = TankBattleEngine()
        self.tank_paused = False
        self._tank_held.clear()
        self._tank_item_pulses = {"red": False, "blue": False}
        self._reset_tank_tracking()
        record = getattr(self, "_record_stat", None)
        if record:
            record("tank", "games_started")
        self.audio.set_tank_phase(self.tank_engine.music_phase)
        self.audio.set_scene_volume_scale(1.0, 300)
        target = getattr(self, "TANK_PLAYING", "tank_playing")
        if self.state == getattr(self, "TANK_MENU", "tank_menu"):
            self._start_transition(target, "tank_crossfire", 42)
        else:
            self.state = target

    def _continue_tank_battle(self):
        snapshot = getattr(self, "_pending_run_states", {}).pop("tank", None)
        if snapshot is not None:
            self._restore_tank_run_state(snapshot)
        self._tank_held.clear()
        self._tank_item_pulses = {"red": False, "blue": False}
        self.audio.set_tank_phase(self.tank_engine.music_phase)
        self.audio.set_scene_volume_scale(0.6 if self.tank_paused else 1.0, 300)
        target = getattr(self, "TANK_PLAYING", "tank_playing")
        if self.state == getattr(self, "TANK_MENU", "tank_menu"):
            self._start_transition(target, "tank_crossfire", 42)
        else:
            self.state = target

    def _handle_tank_menu_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_desktop()
            return
        actions = {
            "continue": self._continue_tank_battle,
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
                self.audio.set_scene_volume_scale(
                    0.6 if self.tank_paused else 1.0,
                    0 if self.tank_paused else 300,
                )
                return
            if self.tank_paused and event.key in _ITEM_KEYS:
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
            self._tank_item_pulses = {"red": False, "blue": False}
            return
        commands = {player: self._tank_command(player) for player in ("red", "blue")}
        events = self.tank_engine.update(max(0, int(dt_ms)), commands)
        self._handle_tank_engine_events(events)
        self.audio.set_tank_phase(self.tank_engine.music_phase)
        if self.tank_engine.phase is MatchPhase.ENDED:
            target = getattr(self, "TANK_END", "tank_end")
            self._start_transition(target, "tank_crossfire", 46)
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
            self._record_tank_engine_event(event)
            sound = _SOUNDS.get(event.kind)
            if sound:
                self.audio.play(sound, _SOUND_VOLUMES.get(sound, 0.7))
            if event.kind in {"tank_hit", "tank_destroyed", "mine_triggered"}:
                self.tank_shake_frames = max(self.tank_shake_frames, 8)
            if event.kind in _SOUNDS:
                tank = self.tank_engine.tanks.get(event.player_id or "red")
                if tank:
                    for index in range(6):
                        angle = index * math.tau / 6
                        self.tank_particles.append({"x": tank.x, "y": tank.y, "vx": math.cos(angle) * .05, "vy": math.sin(angle) * .05, "life": 14})

    def _record_tank_engine_event(self, event):
        record = getattr(self, "_record_stat", None)
        if not record:
            return
        if event.kind == "shot":
            self._tank_match_shots += 1
            self._tank_player_shots[event.player_id] += 1
            record("tank", "shots_fired")
        elif event.kind == "tank_hit":
            self._tank_match_hits += 1
            attacker = str(event.data.get("attacker", ""))
            if attacker in self._tank_player_hits:
                self._tank_player_hits[attacker] += 1
            record("tank", "hits")
        elif event.kind == "shield_blocked":
            record("tank", "shield_blocks")
        elif event.kind == "brick_hit":
            record("tank", "bricks_destroyed")
        elif event.kind == "pickup":
            record("tank", "items_picked_up")
        elif event.kind == "item_used":
            self._tank_player_items_used[event.player_id] += 1
            record("tank", "items_used")
            item = str(event.data.get("item", ""))
            if item in {"repair", "shield", "speed", "mine", "emp", "piercing", "smoke", "warp"}:
                record("tank", f"{item}_uses")
            if item == "speed":
                self._tank_overdrive_kills[event.player_id] = 0
        elif event.kind == "mine_triggered":
            record("tank", "mine_hits")
        elif event.kind == "sudden_death":
            self._tank_in_sudden_death = True
        elif event.kind == "tank_destroyed":
            attacker = str(event.data.get("attacker", ""))
            record("tank", "kills")
            tank = self.tank_engine.tanks.get(attacker)
            if tank and tank.hp == 1:
                record("tank", "iron_will_kills")
            if tank and tank.speed_until_ms > self.tank_engine.elapsed_ms:
                self._tank_overdrive_kills[attacker] += 1
                if self._tank_overdrive_kills[attacker] == 2:
                    record("tank", "overdrive_double_kills")
            for player in ("red", "blue"):
                enemy = "blue" if player == "red" else "red"
                deficit = self.tank_engine.score[enemy] - self.tank_engine.score[player]
                self._tank_max_deficit[player] = max(self._tank_max_deficit[player], deficit)
        elif event.kind == "match_ended" and not self._tank_match_stats_recorded:
            self._tank_match_stats_recorded = True
            winner = event.player_id
            record("tank", "matches_completed")
            record("tank", "games_completed")
            if winner in {"red", "blue"}:
                record("tank", "wins")
                record("tank", f"{winner}_wins")
                if self._tank_in_sudden_death:
                    record("tank", "sudden_wins")
                if self._tank_max_deficit[winner] >= 3:
                    record("tank", "comeback_wins")
            if self._tank_match_shots >= 10 and self._tank_match_hits * 2 >= self._tank_match_shots:
                record("tank", "accurate_matches")
            clear = getattr(self, "_clear_run_state", None)
            if clear:
                clear("tank")

    def _capture_tank_run_state(self):
        return {
            "engine": self.tank_engine.to_dict(),
            "tracking": {
                "match_stats_recorded": self._tank_match_stats_recorded,
                "match_shots": self._tank_match_shots,
                "match_hits": self._tank_match_hits,
                "max_deficit": dict(self._tank_max_deficit),
                "player_shots": dict(self._tank_player_shots),
                "player_hits": dict(self._tank_player_hits),
                "player_items_used": dict(self._tank_player_items_used),
                "overdrive_kills": dict(self._tank_overdrive_kills),
                "in_sudden_death": self._tank_in_sudden_death,
            },
        }

    def _restore_tank_run_state(self, snapshot):
        if isinstance(snapshot, dict) and "engine" in snapshot:
            engine_snapshot = snapshot["engine"]
            tracking = snapshot.get("tracking", {})
        else:
            engine_snapshot = snapshot
            tracking = {}
        self.tank_engine = TankBattleEngine.from_dict(engine_snapshot)
        self._reset_tank_tracking()
        if isinstance(tracking, dict):
            self._tank_match_stats_recorded = bool(tracking.get("match_stats_recorded", False))
            self._tank_match_shots = max(0, int(tracking.get("match_shots", 0)))
            self._tank_match_hits = max(0, int(tracking.get("match_hits", 0)))
            for key, attr in (
                ("max_deficit", "_tank_max_deficit"),
                ("player_shots", "_tank_player_shots"),
                ("player_hits", "_tank_player_hits"),
                ("player_items_used", "_tank_player_items_used"),
                ("overdrive_kills", "_tank_overdrive_kills"),
            ):
                values = tracking.get(key, {})
                if isinstance(values, dict):
                    setattr(self, attr, {
                        player: max(0, int(values.get(player, 0)))
                        for player in ("red", "blue")
                    })
            self._tank_in_sudden_death = bool(tracking.get("in_sudden_death", False))
        self.tank_paused = self.tank_engine.paused
        self._tank_held.clear()
        self._tank_item_pulses = {"red": False, "blue": False}

    def _draw_tank_menu(self):
        outer = draw_arcade_frame(self, "TANK DUEL", "LOCAL TWO-PLAYER ARENA", TANK_PALETTE)
        if is_chinese():
            # Force the bundled 12px CJK bitmap face and integer nearest scaling.
            title_font = get_chinese_font(12)
            raw = title_font.render(translate("TANK DUEL"), False, C.TANK_ACCENT_LIGHT)
            title = pygame.transform.scale(raw, (raw.get_width() * 4, raw.get_height() * 4))
            title_plate = pygame.Rect(outer.centerx - title.get_width() // 2 - 18,
                                      outer.y + 18, title.get_width() + 36, title.get_height() + 12)
            pygame.draw.rect(self.screen, C.TANK_PANEL, title_plate)
            pygame.draw.rect(self.screen, C.OUTLINE, title_plate, 3)
            self.screen.blit(title, (outer.centerx - title.get_width() // 2,
                                     title_plate.centery - title.get_height() // 2))
        arena_card = pygame.Rect(154, 164, 972, 142)
        pygame.draw.rect(self.screen, C.OUTLINE, arena_card, 5)
        pygame.draw.rect(self.screen, C.TANK_PANEL_DARK, arena_card.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.TANK_ACCENT, arena_card.inflate(-20, -20), 2)
        self._draw_tank_emblem(outer.centerx, 226)
        versus = render_pixel_text(self.font_menu_title, "VS", C.TANK_ACCENT_LIGHT, scale=3)
        self.screen.blit(versus, (outer.centerx - versus.get_width() // 2,
                                  arena_card.centery - versus.get_height() // 2))
        red_call = render_pixel_text(self.font_small, translate("RED"), C.TANK_RED_LIGHT, scale=2)
        blue_call = render_pixel_text(self.font_small, translate("BLUE"), C.TANK_BLUE_LIGHT, scale=2)
        self.screen.blit(red_call, (arena_card.x + 122, arena_card.bottom - 40))
        self.screen.blit(blue_call, (arena_card.right - 122 - blue_call.get_width(), arena_card.bottom - 40))
        rule = render_pixel_text(
            self.font_small, "03:00  /  3 HP  /  AUTO FIRE", C.TANK_TEXT, scale=2,
        )
        self.screen.blit(rule, (outer.centerx - rule.get_width() // 2, 315))
        mouse = self._logical_mouse_pos()
        for button in self._tank_buttons("menu"):
            draw_arcade_button(self, button, TANK_PALETTE, button["rect"].collidepoint(mouse), self.tank_pressed_action == button["action"])
        if self.tank_restore_notice:
            notice = render_pixel_text(
                self.font_status, self.tank_restore_notice, C.TANK_ACCENT_LIGHT, scale=2,
            )
            self.screen.blit(notice, (outer.centerx - notice.get_width() // 2, 580))

    def _draw_tank_controls(self):
        draw_arcade_frame(self, "CONTROLS", "TWO CREWS / ONE KEYBOARD", TANK_PALETTE)
        lines = ["RED: W A S D    ITEM: F", "BLUE: ARROW KEYS    ITEM: ENTER", "MOVE IN 8 DIRECTIONS", "P: PAUSE    ESC: MENU"]
        panel = pygame.Rect(220, 164, 840, 448)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, C.TANK_PANEL_DARK, panel.inflate(-10, -10))
        for index, line in enumerate(lines):
            text = render_pixel_text(self.font_status, line, C.TANK_TEXT, scale=2)
            self.screen.blit(text, (panel.centerx - text.get_width() // 2, 202 + index * 48))
        pygame.draw.line(self.screen, C.TANK_ACCENT,
                         (panel.x + 38, 398), (panel.right - 38, 398), 2)
        for index, item in enumerate(ItemType):
            col, row = index % 4, index // 4
            card = pygame.Rect(panel.x + 34 + col * 196, 420 + row * 72, 176, 50)
            pygame.draw.rect(self.screen, C.OUTLINE, card, 2)
            pygame.draw.rect(self.screen, C.TANK_PANEL, card.inflate(-4, -4))
            label_key = {"repair": "REPAIR KIT", "speed": "OVERDRIVE"}.get(
                item.value, item.value.upper()
            )
            label = render_pixel_text(
                self.font_small, translate(label_key), C.TANK_ACCENT_LIGHT, scale=2,
            )
            self.screen.blit(label, (card.centerx - label.get_width() // 2,
                                     card.centery - label.get_height() // 2))

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
        for smoke in self.tank_engine.smokes:
            px, py = self._world_point(arena, tile, smoke.x, smoke.y)
            cloud = pygame.Surface((tile * 4, tile * 4), pygame.SRCALPHA)
            rng = random.Random(f"{smoke.owner}:{int(smoke.x)}:{int(smoke.y)}")
            for _ in range(18):
                radius = rng.randint(max(8, tile // 3), max(10, tile * 2 // 3))
                cx = cloud.get_width() // 2 + rng.randint(-tile, tile)
                cy = cloud.get_height() // 2 + rng.randint(-tile, tile)
                pygame.draw.circle(cloud, (66, 78, 72, 205), (cx, cy), radius)
            pygame.draw.circle(cloud, (145, 160, 150, 85), cloud.get_rect().center,
                               int(tile * 1.45), 3)
            self.screen.blit(cloud, (px - cloud.get_width() // 2,
                                     py - cloud.get_height() // 2))
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
        panel = pygame.Rect(250, 132, 780, 516)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, C.TANK_PANEL, panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.TANK_ACCENT, panel.inflate(-22, -22), 2)
        pygame.draw.line(self.screen, C.TANK_ACCENT, (panel.x + 36, 334),
                         (panel.right - 36, 334), 2)
        winner = self.tank_engine.winner
        title = translate("DRAW" if winner is None else f"{winner.upper()} WINS")
        winner_color = (C.TANK_ACCENT_LIGHT if winner is None else
                        C.TANK_RED_LIGHT if winner == "red" else C.TANK_BLUE_LIGHT)
        text = render_pixel_text(self.font_menu_title, title, winner_color, scale=4)
        self.screen.blit(text, (panel.centerx - text.get_width() // 2, 178))
        score_label = (
            f"{translate('RED')} {self.tank_engine.score['red']}  :  "
            f"{self.tank_engine.score['blue']} {translate('BLUE')}"
        )
        score = render_pixel_text(self.font_status, score_label, C.TANK_TEXT, scale=3)
        self.screen.blit(score, (panel.centerx - score.get_width() // 2, 272))
        for index, player in enumerate(("red", "blue")):
            shots = self._tank_player_shots[player]
            accuracy = round(self._tank_player_hits[player] * 100 / shots) if shots else 0
            summary = (
                f"{translate(player.upper())}  {translate('ACCURACY')} {accuracy}%  "
                f"{translate('ITEMS USED')} {self._tank_player_items_used[player]}"
            )
            color = C.TANK_RED_LIGHT if player == "red" else C.TANK_BLUE_LIGHT
            card = pygame.Rect(panel.x + 54 + index * 348, 362, 324, 112)
            pygame.draw.rect(self.screen, C.OUTLINE, card, 3)
            pygame.draw.rect(self.screen, C.TANK_PANEL_DARK, card.inflate(-6, -6))
            pygame.draw.rect(self.screen, color, (card.x + 12, card.y + 14, 7, card.height - 28))
            line = render_pixel_text(self.font_small, summary, color, scale=2)
            self.screen.blit(line, (card.centerx - line.get_width() // 2 + 5,
                                    card.centery - line.get_height() // 2))
        mouse = self._logical_mouse_pos()
        for button in self._tank_buttons("end"):
            draw_arcade_button(self, button, TANK_PALETTE, button["rect"].collidepoint(mouse), self.tank_pressed_action == button["action"])

    def _draw_tank_hud(self):
        pygame.draw.rect(self.screen, C.TANK_PANEL, (40, 28, 1200, 66))
        pygame.draw.rect(self.screen, C.OUTLINE, (40, 28, 1200, 66), 4)
        red = self.tank_engine.tanks["red"]
        blue = self.tank_engine.tanks["blue"]
        remain = max(0, self.tank_engine.remaining_ms // 1000)
        red_name = render_pixel_text(self.font_status, translate("RED"), C.TANK_RED_LIGHT, scale=2)
        red_item = render_pixel_text(self.font_status, self._item_label(red.held_item), C.TANK_RED_LIGHT, scale=2)
        blue_name = render_pixel_text(self.font_status, translate("BLUE"), C.TANK_BLUE_LIGHT, scale=2)
        blue_item = render_pixel_text(self.font_status, self._item_label(blue.held_item), C.TANK_BLUE_LIGHT, scale=2)
        clock = render_pixel_text(
            self.font_status,
            f"{remain // 60:02d}:{remain % 60:02d}   {self.tank_engine.score['red']} : {self.tank_engine.score['blue']}",
            C.TANK_ACCENT_LIGHT,
            scale=2,
        )
        self.screen.blit(red_name, (70, 46))
        self._draw_life_cells(145, 48, red.hp, C.TANK_RED_LIGHT)
        self.screen.blit(red_item, (205, 46))
        self.screen.blit(clock, (WINDOW_W // 2 - clock.get_width() // 2, 46))
        # Right-anchor every blue element so Chinese and English widths cannot shift it.
        blue_right = 1210
        self.screen.blit(blue_name, (blue_right - blue_name.get_width(), 46))
        self._draw_life_cells(1080, 48, blue.hp, C.TANK_BLUE_LIGHT)
        self.screen.blit(blue_item, (1060 - blue_item.get_width(), 46))

    def _draw_life_cells(self, x, y, hp, color):
        for index in range(3):
            rect = pygame.Rect(x + index * 18, y, 14, 14)
            pygame.draw.rect(self.screen, color if index < hp else C.TANK_PANEL_DARK, rect)
            pygame.draw.rect(self.screen, C.OUTLINE, rect, 2)

    @staticmethod
    def _item_label(item):
        return translate("ITEM --" if item is None else f"ITEM {item.value.upper()}")

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
        item = pickup.item.value
        colors = {
            "repair": C.TANK_RED_LIGHT, "shield": C.TANK_BLUE_LIGHT,
            "speed": C.TANK_ACCENT_LIGHT, "mine": C.TANK_ACCENT,
            "emp": (180, 125, 255), "piercing": (255, 225, 105),
            "smoke": (145, 160, 150), "warp": (100, 245, 225),
        }
        color = colors.get(item, C.TANK_ACCENT_LIGHT)
        pygame.draw.rect(self.screen, color, (px - 7, py - 7, 14, 14))
        glyphs = {"repair": "+", "shield": "O", "speed": ">", "mine": "X",
                  "emp": "E", "piercing": "P", "smoke": "S", "warp": "W"}
        glyph = render_pixel_text(self.font_small, glyphs.get(item, "?"), C.OUTLINE, scale=1)
        self.screen.blit(glyph, (px - glyph.get_width() // 2, py - glyph.get_height() // 2))

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
