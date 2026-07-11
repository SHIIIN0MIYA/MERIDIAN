"""Unified settings, profile, statistics, achievements, and persistence UI."""

import datetime as dt
import json

from .common import *
from .persistence import SaveManager
from .localization import set_language, get_chinese_font, is_chinese
from . import lore as _lore
from .tank_engine import TankSnapshotError


ACHIEVEMENTS = [
    ("gomoku_first_game", "FIRST STONES", "Complete one Gomoku game", "gomoku", "games_completed", 1),
    ("gomoku_first_win", "FIVE IN LINE", "Win one Gomoku game", "gomoku", "wins", 1),
    ("gomoku_both_sides", "TWO COLORS", "Win as Black and White", "gomoku", "both_sides", 1),
    ("gomoku_19_win", "GRAND BOARD", "Win on a 19 x 19 board", "gomoku", "wins_on_19", 1),
    ("gomoku_10_wins", "STONE MASTER", "Win 10 Gomoku games", "gomoku", "wins", 10),
    ("gomoku_50_games", "OLD RIVALS", "Complete 50 Gomoku games", "gomoku", "games_completed", 50),
    ("snake_5", "SMALL BITE", "Reach 5 points in Snake", "snake", "best_score", 5),
    ("snake_10", "HUNGRY", "Reach 10 points in Snake", "snake", "best_score", 10),
    ("snake_20", "LONG TRAIL", "Reach 20 points in Snake", "snake", "best_score", 20),
    ("snake_fast_30", "GREEN LIGHTNING", "Reach 30 on Fast speed", "snake", "best_fast_score", 30),
    ("snake_food_100", "FULL PANTRY", "Eat 100 food in total", "snake", "food_eaten", 100),
    ("snake_40", "ENDLESS COIL", "Reach 40 points in Snake", "snake", "best_score", 40),
    ("breakout_first_clear", "CLEAR SKIES", "Clear one Breakout level", "breakout", "levels_cleared", 1),
    ("breakout_level_3", "THIRD FLOOR", "Reach Breakout level 3", "breakout", "highest_level", 3),
    ("breakout_1000", "FOUR DIGITS", "Score 1000 in Breakout", "breakout", "best_score", 1000),
    ("breakout_hard", "HARD HITTER", "Clear a level on Hard", "breakout", "hard_levels_cleared", 1),
    ("breakout_perfect", "UNTOUCHABLE", "Clear a level without losing a life", "breakout", "perfect_levels", 1),
    ("breakout_500", "DEMOLITION", "Break 500 bricks in total", "breakout", "bricks_broken", 500),
    ("2048_128", "POWER OF SEVEN", "Create a 128 tile", "2048", "highest_tile", 128),
    ("2048_512", "HEAVY TILE", "Create a 512 tile", "2048", "highest_tile", 512),
    ("2048_2048", "THE NUMBER", "Create a 2048 tile", "2048", "highest_tile", 2048),
    ("2048_4096", "BEYOND", "Create a 4096 tile", "2048", "highest_tile", 4096),
    ("2048_score_10000", "FIVE DIGITS", "Score 10000 in one game", "2048", "best_score", 10000),
    ("2048_merges_1000", "FUSION ENGINE", "Complete 1000 merges", "2048", "merges", 1000),
    ("mines_first_win", "SAFE STEP", "Win one Mines game", "mines", "wins", 1),
    ("mines_9_10", "SCOUT", "Win 9 x 9 with 10 mines", "mines", "mode:9x10", 1),
    ("mines_9_20", "DENSE FIELD", "Win 9 x 9 with 20 mines", "mines", "mode:9x20", 1),
    ("mines_16_40", "WIDE FIELD", "Win 16 x 16 with 40 mines", "mines", "mode:16x40", 1),
    ("mines_16_60", "RED ZONE", "Win 16 x 16 with 60 mines", "mines", "mode:16x60", 1),
    ("mines_10_wins", "BOMB SQUAD", "Win 10 Mines games", "mines", "wins", 10),
    ("tetris_first_line", "FIRST FLOOR", "Clear one line", "tetris", "lines_cleared", 1),
    ("tetris_tetris", "FOUR AT ONCE", "Clear four lines at once", "tetris", "tetrises", 1),
    ("tetris_20_lines", "STACK CONTROL", "Clear 20 lines in one game", "tetris", "best_lines", 20),
    ("tetris_level_5", "FASTER FALL", "Reach Tetris level 5", "tetris", "highest_level", 5),
    ("tetris_10000", "BLOCK BANK", "Score 10000 in Tetris", "tetris", "best_score", 10000),
    ("tetris_200_lines", "CITY BUILDER", "Clear 200 lines in total", "tetris", "lines_cleared", 200),
    ("air_first_clear", "FIRST SORTIE", "Complete one Air Raid mission", "air", "levels_cleared", 1),
    ("air_first_boss", "COMMAND BREAKER", "Defeat one command frame", "air", "bosses_defeated", 1),
    ("air_cannon_five", "GUNLINE", "Upgrade Cannon to level 5", "air", "cannon_level", 5),
    ("air_spread_five", "WIDE SKY", "Upgrade Spread to level 5", "air", "spread_level", 5),
    ("air_laser_five", "LIGHT SPEAR", "Upgrade Laser to level 5", "air", "laser_level", 5),
    ("air_missile_eight", "EIGHT LOCKS", "Destroy 8 targets with one missile launch", "air", "best_missile_kills", 8),
    ("air_first_s", "PERFECT VECTOR", "Earn one S rating", "air", "s_ranks", 1),
    ("air_campaign", "LAST HORIZON", "Complete the standard campaign", "air", "campaigns_completed", 1),
    ("air_all_s", "WARDEN PRIME", "Earn S on all 16 standard missions", "air", "standard_all_s", 1),
    ("air_challenge_clear", "HARD SIGNAL", "Clear one challenge mission", "air", "challenge_clears", 1),
    ("air_challenge_campaign", "NO SAFE SKY", "Complete Challenge Campaign", "air", "challenge_campaigns_completed", 1),
    ("air_boss_rush", "EIGHT COMMANDS", "Complete Boss Rush", "air", "boss_rush_clears", 1),
]


GAME_STATES = {
    "playing": "gomoku",
    "snake_playing": "snake",
    "breakout_playing": "breakout",
    "g2048_playing": "2048",
    "mines_playing": "mines",
    "tetris_playing": "tetris",
    "air_playing": "air",
    "tank_playing": "tank",
}


class SystemMixin:
    def _game_id_from_state(self, state=None):
        return GAME_STATES.get(state or self.state)

    def _init_system(self, save_path=None):
        self.save_manager = SaveManager(save_path)
        self.save_data = self.save_manager.load()
        self.system_pressed_action = None
        self.system_dialog = None
        self.profile_tab = "achievements"
        self.profile_scroll = 0
        self.achievement_notifications = []
        self.achievement_wall_pressed_index = None
        self.achievement_wall_detail_index = None
        self.achievement_wall_detail_frame = 0
        self.achievement_wall_detail_closing = False
        self._pending_run_states = {}
        self.tank_restore_notice = None
        self._last_persisted_snapshot = ""
        self._last_save_check = pygame.time.get_ticks()
        self._last_usage_tick = pygame.time.get_ticks()
        self._display_offset = (0, 0)
        self._display_scale = 1.0
        self._apply_loaded_data()
        self._init_lore_reader()
        self._auto_unlock_lore()
        self.save_data["statistics"]["global"]["launches"] += 1
        self._save_now()

    def _auto_unlock_lore(self):
        """Auto-unlock any 'always' lore entries that aren't yet tracked."""
        lore_data = self.save_data.setdefault("lore", {})
        unlocked = lore_data.setdefault("unlocked_entries", [])
        for entry in _lore.get_all_lore_entries():
            if entry.get("unlock") == "always" and entry["id"] not in unlocked:
                unlocked.append(entry["id"])

    def _apply_loaded_data(self):
        settings = self.save_data["settings"]
        self.language = settings.get("language", "en")
        set_language(self.language)
        self.audio.set_music_volume(settings["music_volume"])
        self.audio.set_sfx_volume(settings["sfx_volume"])
        self.audio.set_muted(settings["muted"])
        self.fullscreen = bool(settings["fullscreen"])
        self.animation_level = settings["animation_level"]
        self.screen_shake_enabled = bool(settings["screen_shake"])
        self.board_size = int(settings["gomoku_board_size"])
        self.board = Board(self.board_size)
        self.snake_speed_mode = settings["snake_speed"]
        self.snake_skin = settings["snake_skin"]
        self.breakout_control_mode = settings["breakout_control"]
        self.breakout_difficulty = settings["breakout_difficulty"]
        self.breakout_ball_skin = settings["breakout_ball_skin"]
        self.breakout_brick_skin = settings["breakout_brick_skin"]
        self.breakout_paddle_skin = settings["breakout_paddle_skin"]
        self.air_skin = settings.get("air_skin", "default")
        self.mines_size = int(settings["mines_size"])
        self.mines_count = int(settings["mines_count"])
        self._apply_snake_preferences()
        self._apply_breakout_preferences()
        self._apply_air_preferences()
        records = self.save_data["records"]
        self.black_wins = int(records["gomoku"]["black_wins"])
        self.white_wins = int(records["gomoku"]["white_wins"])
        self.draws = int(records["gomoku"]["draws"])
        self.snake_best = int(records["snake"]["best_score"])
        self.breakout_best = int(records["breakout"]["best_score"])
        self.g2048_best = int(records["2048"]["best_score"])
        self.tetris_best = int(records["tetris"]["best_score"])
        self.tetris_best_level = int(records["tetris"]["best_level"])
        self.mines_best_times = {}
        for size in MINES_SIZE_CHOICES:
            for count in MINES_COUNT_CHOICES[size]:
                key = f"{size}x{count}"
                self.mines_best_times[(size, count)] = records["mines"]["best_times"].get(key)
        self._rebuild_stone_assets()
        self._set_display_mode(self.fullscreen, persist=False)
        # Load pending run states for resume support
        for game_id in ("gomoku", "snake", "breakout", "2048", "mines", "tetris", "air", "tank"):
            progress = self.save_data.get("progress", {}).get(game_id, {})
            if progress.get("run_active") and progress.get("run_state") is not None:
                if game_id == "tank":
                    try:
                        self._restore_tank_run_state(progress["run_state"])
                    except TankSnapshotError:
                        progress["run_active"] = False
                        progress["run_state"] = None
                        self.tank_restore_notice = "TANK SAVE COULD NOT BE RESTORED"
                    else:
                        self._pending_run_states[game_id] = progress["run_state"]
                else:
                    self._pending_run_states[game_id] = progress["run_state"]

    def _apply_snake_preferences(self):
        self.snake_base_interval = {"slow": 11, "normal": 8, "fast": 6}.get(self.snake_speed_mode, 8)
        colors = {
            "green": (C.SNAKE_BODY, C.SNAKE_HEAD),
            "lime": ((150, 255, 90), (205, 255, 130)),
            "red": ((255, 95, 120), (255, 160, 170)),
        }
        self.snake_body_color, self.snake_head_color = colors.get(self.snake_skin, colors["green"])

    def _apply_breakout_preferences(self):
        self.breakout_ball_color = {
            "yellow": C.BREAKOUT_BALL_YELLOW, "cyan": C.BREAKOUT_BALL_CYAN,
            "pink": C.BREAKOUT_BALL_PINK,
        }.get(self.breakout_ball_skin, C.BREAKOUT_BALL_YELLOW)
        self.breakout_brick_color = {
            "purple": C.BREAKOUT_BRICK_PURPLE, "orange": C.BREAKOUT_BRICK_ORANGE,
            "blue": C.BREAKOUT_BRICK_BLUE,
        }.get(self.breakout_brick_skin, C.BREAKOUT_BRICK_PURPLE)
        self.breakout_paddle_color = {
            "orange": C.BREAKOUT_PADDLE_ORANGE, "cyan": C.BREAKOUT_PADDLE_CYAN,
            "pink": C.BREAKOUT_PADDLE_PINK,
        }.get(self.breakout_paddle_skin, C.BREAKOUT_PADDLE_ORANGE)
        self._apply_breakout_difficulty()

    def _apply_air_preferences(self):
        colors = {
            "default": (C.AIR_SKIN_DEFAULT_SHIP, C.AIR_SKIN_DEFAULT_ENGINE, C.AIR_SKIN_DEFAULT_SHIELD),
            "crimson": (C.AIR_SKIN_CRIMSON_SHIP, C.AIR_SKIN_CRIMSON_ENGINE, C.AIR_SKIN_CRIMSON_SHIELD),
            "azure": (C.AIR_SKIN_AZURE_SHIP, C.AIR_SKIN_AZURE_ENGINE, C.AIR_SKIN_AZURE_SHIELD),
            "gold": (C.AIR_SKIN_GOLD_SHIP, C.AIR_SKIN_GOLD_ENGINE, C.AIR_SKIN_GOLD_SHIELD),
        }
        ship, engine, shield = colors.get(self.air_skin, colors["default"])
        self.air_ship_color = ship
        self.air_engine_color = engine
        self.air_shield_color = shield

    def _capture_data(self):
        data = self.save_data
        data["settings"].update({
            "language": self.language,
            "music_volume": self.audio.music_volume,
            "sfx_volume": self.audio.sfx_volume,
            "muted": self.audio.muted,
            "fullscreen": self.fullscreen,
            "animation_level": self.animation_level,
            "screen_shake": self.screen_shake_enabled,
            "gomoku_board_size": self.board_size,
            "snake_speed": self.snake_speed_mode,
            "snake_skin": self.snake_skin,
            "breakout_control": self.breakout_control_mode,
            "breakout_difficulty": self.breakout_difficulty,
            "breakout_ball_skin": self.breakout_ball_skin,
            "breakout_brick_skin": self.breakout_brick_skin,
            "breakout_paddle_skin": self.breakout_paddle_skin,
            "air_skin": self.air_skin,
            "mines_size": self.mines_size,
            "mines_count": self.mines_count,
        })
        data["records"]["gomoku"].update({
            "black_wins": self.black_wins, "white_wins": self.white_wins, "draws": self.draws,
        })
        data["records"]["snake"]["best_score"] = max(self.snake_best, self._stat("snake", "best_score"))
        data["records"]["breakout"]["best_score"] = max(self.breakout_best, self._stat("breakout", "best_score"))
        data["records"]["2048"]["best_score"] = max(self.g2048_best, self._stat("2048", "best_score"))
        data["records"]["tetris"].update({
            "best_score": max(getattr(self, "tetris_best", 0), self._stat("tetris", "best_score")),
            "best_level": max(getattr(self, "tetris_best_level", 1), self._stat("tetris", "highest_level")),
        })
        air_progress = data["progress"]["air"]
        data["records"]["air"].update({
            "best_score": self._stat("air", "best_score"),
            "highest_level": self._stat("air", "highest_level"),
            "boss_rush_score": air_progress["boss_rush_best"]["score"],
            "boss_rush_health": air_progress["boss_rush_best"]["health"],
        })
        data["records"]["mines"]["best_times"] = {
            f"{size}x{count}": value
            for (size, count), value in self.mines_best_times.items()
        }
        # Capture in-progress game run state
        game_id = self._game_id_from_state()
        if game_id:
            capture_method = getattr(self, f"_capture_{game_id}_run_state", None)
            if capture_method:
                data["progress"][game_id]["run_state"] = capture_method()
                data["progress"][game_id]["run_active"] = True
        return data

    def _clear_run_state(self, game_id):
        progress = self.save_data["progress"].get(game_id, {})
        progress["run_active"] = False
        progress["run_state"] = None
        self._save_now()

    def _save_now(self):
        if getattr(self, "dev_mode", False):
            return
        payload = self._capture_data()
        self.save_manager.save(payload)
        self._last_persisted_snapshot = json.dumps(payload, sort_keys=True)
        self._last_save_check = pygame.time.get_ticks()

    def _update_persistence(self):
        now = pygame.time.get_ticks()
        delta = max(0, min(1000, now - self._last_usage_tick))
        self._last_usage_tick = now
        if getattr(self, "dev_mode", False):
            self._update_achievement_notifications()
            return
        stats = self.save_data["statistics"]
        stats["global"]["play_time_ms"] += delta
        game = GAME_STATES.get(self.state)
        if game:
            stats[game]["play_time_ms"] += delta
        if not self.screen_shake_enabled:
            self.shake_duration = 0
            self.shake_x = self.shake_y = 0
            self.snake_shake_duration = 0
            self.snake_shake_x = self.snake_shake_y = 0
            self.breakout_shake_duration = 0
            self.breakout_shake_x = self.breakout_shake_y = 0
        if now - self._last_save_check >= 2000:
            snapshot = json.dumps(self._capture_data(), sort_keys=True)
            if snapshot != self._last_persisted_snapshot:
                self._save_now()
            else:
                self._last_save_check = now
        self._update_achievement_notifications()

    def _stat(self, game, key):
        return self.save_data["statistics"][game].get(key, 0)

    def _record_stat(self, game, key, amount=1, mode="add"):
        if getattr(self, "dev_mode", False):
            return
        stats = self.save_data["statistics"]
        target = stats[game]
        if mode == "max":
            target[key] = max(target.get(key, 0), amount)
        else:
            target[key] = target.get(key, 0) + amount
        if key == "games_started":
            stats["global"]["games_started"] += amount
        elif key == "games_completed":
            stats["global"]["games_completed"] += amount
        self._check_achievements()

    def _achievement_progress(self, definition):
        _, _, _, game, key, target = definition
        stats = self.save_data["statistics"][game]
        if key == "wins":
            if game == "gomoku":
                value = stats["black_wins"] + stats["white_wins"]
            else:
                value = stats.get("wins", 0)
        elif key == "both_sides":
            value = int(stats["black_wins"] > 0 and stats["white_wins"] > 0)
        elif key.startswith("mode:"):
            value = stats.get("wins_by_mode", {}).get(key.split(":", 1)[1], 0)
        elif game == "air" and key == "standard_all_s":
            ratings = self.save_data["progress"]["air"]["ratings"]["standard"]
            value = int(
                len(ratings) >= 16
                and all(item.get("rank") == "S" for item in ratings.values())
            )
        else:
            value = stats.get(key, 0)
        return min(value, target), target

    def _check_achievements(self):
        if getattr(self, "dev_mode", False):
            return
        unlocked = self.save_data["achievements"]
        newly_unlocked = False
        play_sound = False
        for definition in ACHIEVEMENTS:
            achievement_id, title = definition[0], definition[1]
            progress, target = self._achievement_progress(definition)
            if progress >= target and achievement_id not in unlocked:
                unlocked[achievement_id] = {"unlocked_at": dt.datetime.now().isoformat(timespec="seconds")}
                self.achievement_notifications.append({"title": title, "frame": 0})
                newly_unlocked = True
                play_sound = True
                # Cap queue at 3
                while len(self.achievement_notifications) > 3:
                    self.achievement_notifications.pop(0)
        if play_sound:
            self.audio.play("achievement", 0.85)
        if newly_unlocked:
            self._save_now()

    def _update_achievement_notifications(self):
        for note in self.achievement_notifications[:]:
            note["frame"] += 1
            if note["frame"] >= 240:
                self.achievement_notifications.remove(note)

    def _draw_achievement_notification(self):
        if not self.achievement_notifications:
            return
        # Show up to 3 stacked notifications
        for idx, item in enumerate(self.achievement_notifications[:3]):
            frame = item["frame"]
            t = min(1.0, frame / 18)
            if frame > 205:
                t = max(0.0, (240 - frame) / 35)
            label = render_pixel_text(self.font_small, "ACHIEVEMENT UNLOCKED", C.DESK_MUTED, scale=1 if is_chinese() else 2)
            title = render_pixel_text(self.font_status, item["title"], C.GOLD_LIGHT, scale=2)
            panel_w = max(360, min(620, max(label.get_width(), title.get_width()) + 96))
            if title.get_width() > panel_w - 48:
                title = render_pixel_text(self.font_status, item["title"], C.GOLD_LIGHT, scale=1)
                panel_w = max(360, min(620, max(label.get_width(), title.get_width()) + 96))
            panel_h = 72 if is_chinese() else 66
            base_y = int(-panel_h - 14 + (panel_h + 30) * ease_out_back(t))
            offset_y = idx * (panel_h + 10)
            y = base_y + offset_y
            panel = pygame.Rect(WINDOW_W // 2 - panel_w // 2, y, panel_w, panel_h)
            pygame.draw.rect(self.screen, C.OUTLINE, panel, 4)
            pygame.draw.rect(self.screen, C.DESK_PANEL, panel.inflate(-8, -8))
            pygame.draw.rect(self.screen, C.GOLD, panel.inflate(-16, -16), 2)
            self.screen.blit(label, (panel.centerx - label.get_width() // 2, panel.y + 9))
            self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + (32 if is_chinese() else 36)))

    def _set_display_mode(self, fullscreen, persist=True):
        self.fullscreen = bool(fullscreen)
        if self.fullscreen:
            info = pygame.display.Info()
            size = (max(WINDOW_W, info.current_w), max(WINDOW_H, info.current_h))
            self.display_surface = pygame.display.set_mode(size, pygame.NOFRAME)
        else:
            self.display_surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        if not hasattr(self, "screen") or self.screen.get_size() != (WINDOW_W, WINDOW_H):
            self.screen = pygame.Surface((WINDOW_W, WINDOW_H))
        self._update_display_transform()
        if persist and hasattr(self, "save_data"):
            self._save_now()

    def _update_display_transform(self):
        dw, dh = self.display_surface.get_size()
        scale = min(dw / WINDOW_W, dh / WINDOW_H)
        self._display_scale = scale
        self._display_offset = (
            int((dw - WINDOW_W * scale) / 2),
            int((dh - WINDOW_H * scale) / 2),
        )

    def _logical_mouse_pos(self, pos=None):
        if pos is None:
            pos = pygame.mouse.get_pos()
        ox, oy = self._display_offset
        scale = max(0.001, self._display_scale)
        return (int((pos[0] - ox) / scale), int((pos[1] - oy) / scale))

    def _map_event_to_logical(self, event):
        if hasattr(event, "pos"):
            attrs = dict(event.dict)
            attrs["pos"] = self._logical_mouse_pos(event.pos)
            if "rel" in attrs:
                attrs["rel"] = (
                    int(attrs["rel"][0] / max(0.001, self._display_scale)),
                    int(attrs["rel"][1] / max(0.001, self._display_scale)),
                )
            return pygame.event.Event(event.type, attrs)
        return event

    def _present_frame(self):
        if self.display_surface is self.screen:
            pygame.display.flip()
            return
        self.display_surface.fill((0, 0, 0))
        scale = self._display_scale
        size = (int(WINDOW_W * scale), int(WINDOW_H * scale))
        frame = pygame.transform.scale(self.screen, size)
        self.display_surface.blit(frame, self._display_offset)
        pygame.display.flip()

    def _get_system_settings_buttons(self):
        buttons = []
        panel = pygame.Rect(50, 38, 1180, 644)
        x1, x2 = panel.x + 250, panel.x + 750
        rows = [158, 210, 262, 314, 366, 418, 470]
        buttons.extend([
            {"rect": pygame.Rect(x1, rows[0], 56, 38), "label": "-", "action": "music_down"},
            {"rect": pygame.Rect(x1 + 250, rows[0], 56, 38), "label": "+", "action": "music_up"},
            {"rect": pygame.Rect(x1, rows[1], 56, 38), "label": "-", "action": "sfx_down"},
            {"rect": pygame.Rect(x1 + 250, rows[1], 56, 38), "label": "+", "action": "sfx_up"},
            {"rect": pygame.Rect(x1, rows[2], 306, 38), "label": "MUTE", "action": "toggle_mute", "selected": self.audio.muted},
            {"rect": pygame.Rect(x1, rows[3], 306, 38), "label": "FULLSCREEN", "action": "toggle_fullscreen", "selected": self.fullscreen},
            {"rect": pygame.Rect(x1, rows[4], 306, 38), "label": self.animation_level.upper(), "action": "cycle_animation"},
            {"rect": pygame.Rect(x1, rows[5], 306, 38), "label": "SCREEN SHAKE", "action": "toggle_shake", "selected": self.screen_shake_enabled},
            {"rect": pygame.Rect(x1, rows[6], 306, 38), "label": "SIMPLIFIED CHINESE" if self.language == "zh_hans" else "ENGLISH", "action": "cycle_language"},
        ])
        game_rows = [
            ("BOARD", "cycle_gomoku"), ("SNAKE SPEED", "cycle_snake_speed"),
            ("SNAKE SKIN", "cycle_snake_skin"), ("BREAKOUT MODE", "cycle_breakout_control"),
            ("BREAKOUT LEVEL", "cycle_breakout_difficulty"), ("MINES BOARD", "cycle_mines"),
            ("AIR SKIN", "cycle_air_skin"),
        ]
        for index, (_, action) in enumerate(game_rows):
            buttons.append({"rect": pygame.Rect(x2, rows[index], 320, 38), "label": action, "action": action})
        buttons.extend([
            {"rect": pygame.Rect(panel.x + 110, panel.bottom - 70, 250, 44), "label": "DEFAULT SETTINGS", "action": "reset_settings"},
            {"rect": pygame.Rect(panel.centerx - 125, panel.bottom - 70, 250, 44), "label": "ERASE PROGRESS", "action": "erase_progress"},
            {"rect": pygame.Rect(panel.right - 360, panel.bottom - 70, 250, 44), "label": "BACK", "action": "back"},
        ])
        return buttons

    def _settings_value(self, action):
        values = {
            "cycle_gomoku": f"{self.board_size} x {self.board_size}",
            "cycle_snake_speed": self.snake_speed_mode.upper(),
            "cycle_snake_skin": self.snake_skin.upper(),
            "cycle_breakout_control": self.breakout_control_mode.upper(),
            "cycle_breakout_difficulty": self.breakout_difficulty.upper(),
            "cycle_mines": f"{self.mines_size} x {self.mines_size} / {self.mines_count}",
            "cycle_air_skin": self.air_skin.upper(),
        }
        return values.get(action, "")

    def _handle_system_settings_event(self, event):
        if self.system_dialog:
            self._handle_system_dialog_event(event)
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_system_desktop()
            return
        buttons = self._get_system_settings_buttons()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in buttons:
                if button["rect"].collidepoint(event.pos):
                    self.system_pressed_action = button["action"]
                    return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for button in buttons:
                if button["rect"].collidepoint(event.pos) and self.system_pressed_action == button["action"]:
                    self._activate_system_setting(button["action"])
                    break
            self.system_pressed_action = None

    def _activate_system_setting(self, action):
        if action == "back":
            self._go_system_desktop()
        elif action == "music_down":
            self.audio.set_music_volume(self.audio.music_volume - 0.1)
        elif action == "music_up":
            self.audio.set_music_volume(self.audio.music_volume + 0.1)
        elif action == "sfx_down":
            self.audio.set_sfx_volume(self.audio.sfx_volume - 0.1)
        elif action == "sfx_up":
            self.audio.set_sfx_volume(self.audio.sfx_volume + 0.1)
        elif action == "toggle_mute":
            self.audio.set_muted(not self.audio.muted)
        elif action == "toggle_fullscreen":
            self._set_display_mode(not self.fullscreen)
        elif action == "cycle_animation":
            levels = ["full", "reduced", "off"]
            self.animation_level = levels[(levels.index(self.animation_level) + 1) % len(levels)]
        elif action == "toggle_shake":
            self.screen_shake_enabled = not self.screen_shake_enabled
        elif action == "cycle_language":
            self.language = "en" if self.language == "zh_hans" else "zh_hans"
            set_language(self.language)
        elif action == "cycle_gomoku":
            choices = BOARD_SIZE_CHOICES
            self.board_size = choices[(choices.index(self.board_size) + 1) % len(choices)]
            if not self.board.has_moves() or self.board.winner:
                self.board = Board(self.board_size)
                self._rebuild_stone_assets()
        elif action == "cycle_snake_speed":
            values = ["slow", "normal", "fast"]
            self.snake_speed_mode = values[(values.index(self.snake_speed_mode) + 1) % len(values)]
            self._apply_snake_preferences()
        elif action == "cycle_snake_skin":
            values = ["green", "lime", "red"]
            self.snake_skin = values[(values.index(self.snake_skin) + 1) % len(values)]
            self._apply_snake_preferences()
        elif action == "cycle_air_skin":
            progress = self.save_data.get("progress", {}).get("air", {})
            unlocked = progress.get("skins_unlocked", ["default"])
            if self.air_skin not in unlocked:
                self.air_skin = unlocked[0]
            else:
                idx = unlocked.index(self.air_skin)
                self.air_skin = unlocked[(idx + 1) % len(unlocked)]
            self._apply_air_preferences()
        elif action == "cycle_breakout_control":
            self.breakout_control_mode = "mouse" if self.breakout_control_mode == "keyboard" else "keyboard"
        elif action == "cycle_breakout_difficulty":
            values = ["easy", "normal", "hard"]
            self.breakout_difficulty = values[(values.index(self.breakout_difficulty) + 1) % len(values)]
            self._apply_breakout_difficulty()
        elif action == "cycle_mines":
            modes = [(9, 10), (9, 15), (9, 20), (16, 40), (16, 50), (16, 60)]
            current = (self.mines_size, self.mines_count)
            self.mines_size, self.mines_count = modes[(modes.index(current) + 1) % len(modes)]
        elif action in ("reset_settings", "erase_progress"):
            self.system_dialog = action
        self._save_now()

    def _get_system_dialog_buttons(self):
        return [
            {"rect": pygame.Rect(WINDOW_W // 2 - 220, WINDOW_H // 2 + 64, 190, 46), "label": "CANCEL", "action": "cancel"},
            {"rect": pygame.Rect(WINDOW_W // 2 + 30, WINDOW_H // 2 + 64, 190, 46), "label": "CONFIRM", "action": "confirm"},
        ]

    def _handle_system_dialog_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.system_dialog = None
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self._get_system_dialog_buttons():
                if button["rect"].collidepoint(event.pos):
                    self.system_pressed_action = button["action"]
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for button in self._get_system_dialog_buttons():
                if button["rect"].collidepoint(event.pos) and self.system_pressed_action == button["action"]:
                    if button["action"] == "confirm":
                        if self.system_dialog == "reset_settings":
                            self.save_data = self.save_manager.reset_settings(self.save_data)
                        else:
                            self.save_data = self.save_manager.erase_progress(self.save_data)
                        self._apply_loaded_data()
                        self._save_now()
                    self.system_dialog = None
                    break
            self.system_pressed_action = None

    def _draw_system_button(self, button):
        rect = button["rect"].copy()
        mouse = self._logical_mouse_pos()
        hovered = rect.collidepoint(mouse)
        pressed = self.system_pressed_action == button["action"]
        if hovered:
            rect = rect.inflate(6, 4)
        if pressed:
            rect.y += 3
        pygame.draw.rect(self.screen, C.OUTLINE, rect.move(4, 4))
        pygame.draw.rect(self.screen, C.OUTLINE, rect)
        fill = C.DESK_ICON_HOVER if hovered or button.get("selected") else C.DESK_PANEL_DARK
        pygame.draw.rect(self.screen, fill, rect.inflate(-4, -4))
        pygame.draw.rect(self.screen, C.DESK_ACCENT_LIGHT, rect.inflate(-10, -10), 2)
        label = button["label"]
        if label.startswith("cycle_"):
            label = self._settings_value(label)
        text = render_pixel_text(self.font_small, label, C.DESK_TEXT, scale=2)
        if text.get_width() > rect.width - 18:
            text = render_pixel_text(self.font_small, label, C.DESK_TEXT, scale=1)
        self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

    def _draw_system_settings(self):
        self.screen.fill(C.DESK_BG_BOTTOM)
        panel = pygame.Rect(50, 38, 1180, 644)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, C.DESK_PANEL, panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.DESK_ACCENT, panel.inflate(-22, -22), 2)
        title = render_pixel_text(self.font_menu_title, "SYSTEM SETTINGS", C.DESK_ACCENT_LIGHT, scale=3)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 28))
        left = render_pixel_text(self.font_status, "SYSTEM", C.GOLD_LIGHT, scale=2)
        right = render_pixel_text(self.font_status, "GAME OPTIONS", C.GOLD_LIGHT, scale=2)
        self.screen.blit(left, (350 - left.get_width() // 2, 132))
        self.screen.blit(right, (930 - right.get_width() // 2, 132))
        labels = ["MUSIC", "SFX", "MASTER MUTE", "DISPLAY", "ANIMATION", "SHAKE", "LANGUAGE"]
        game_labels = ["GOMOKU BOARD", "SNAKE SPEED", "SNAKE SKIN", "BREAKOUT MODE", "BREAKOUT LEVEL", "MINES BOARD"]
        for index, y in enumerate([158, 210, 262, 314, 366, 418, 470]):
            label = render_pixel_text(self.font_small, labels[index], C.DESK_TEXT, scale=2)
            self.screen.blit(label, (92, y + 10))
            if index < len(game_labels):
                game_label = render_pixel_text(self.font_small, game_labels[index], C.DESK_TEXT, scale=2)
                self.screen.blit(game_label, (632, y + 10))
        for button in self._get_system_settings_buttons():
            self._draw_system_button(button)
        music = render_pixel_text(self.font_small, f"{int(self.audio.music_volume * 100):03d}%", C.GOLD_LIGHT, scale=2)
        sfx = render_pixel_text(self.font_small, f"{int(self.audio.sfx_volume * 100):03d}%", C.GOLD_LIGHT, scale=2)
        self.screen.blit(music, (405 - music.get_width() // 2, 168))
        self.screen.blit(sfx, (405 - sfx.get_width() // 2, 220))
        if self.system_dialog:
            self._draw_system_dialog()

    def _draw_system_dialog(self):
        shade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 185))
        self.screen.blit(shade, (0, 0))
        panel = pygame.Rect(WINDOW_W // 2 - 310, WINDOW_H // 2 - 140, 620, 280)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, C.DESK_PANEL, panel.inflate(-10, -10))
        title_text = "RESTORE DEFAULT SETTINGS?" if self.system_dialog == "reset_settings" else "ERASE ALL PROGRESS?"
        note_text = "GAME RECORDS WILL BE KEPT" if self.system_dialog == "reset_settings" else "RECORDS, STATS AND ACHIEVEMENTS WILL BE LOST"
        title = render_pixel_text(self.font_status, title_text, C.GOLD_LIGHT, scale=2)
        note = render_pixel_text(self.font_small, note_text, C.DESK_TEXT, scale=2)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 52))
        self.screen.blit(note, (panel.centerx - note.get_width() // 2, panel.y + 112))
        for button in self._get_system_dialog_buttons():
            self._draw_system_button(button)

    def _handle_profile_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._go_system_desktop()
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.profile_tab = "achievements"
                self.profile_scroll = 0
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.profile_tab = "statistics"
                self.profile_scroll = 0
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.profile_scroll = max(0, self.profile_scroll - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.profile_scroll += 1
            return
        if event.type == pygame.MOUSEWHEEL:
            self.profile_scroll = max(0, self.profile_scroll - event.y)
            return
        buttons = self._get_profile_buttons()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in buttons:
                if button["rect"].collidepoint(event.pos):
                    self.system_pressed_action = button["action"]
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for button in buttons:
                if button["rect"].collidepoint(event.pos) and self.system_pressed_action == button["action"]:
                    if button["action"] == "back":
                        self._go_system_desktop()
                    else:
                        self.profile_tab = button["action"]
                        self.profile_scroll = 0
                    break
            self.system_pressed_action = None

    def _get_profile_buttons(self):
        return [
            {"rect": pygame.Rect(90, 104, 250, 48), "label": "ACHIEVEMENTS", "action": "achievements", "selected": self.profile_tab == "achievements"},
            {"rect": pygame.Rect(360, 104, 250, 48), "label": "STATISTICS", "action": "statistics", "selected": self.profile_tab == "statistics"},
            {"rect": pygame.Rect(960, 104, 220, 48), "label": "BACK", "action": "back"},
        ]

    def _format_duration(self, value):
        seconds = max(0, int(value) // 1000)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _go_system_desktop(self):
        self._start_transition(self.DESKTOP, "fade", frames=28)

    def _draw_profile(self):
        self.screen.fill(C.DESK_BG_BOTTOM)
        outer = pygame.Rect(46, 34, 1188, 652)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5)
        pygame.draw.rect(self.screen, C.DESK_PANEL, outer.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.DESK_ACCENT, outer.inflate(-22, -22), 2)
        title = render_pixel_text(self.font_menu_title, "PLAYER PROFILE", C.DESK_ACCENT_LIGHT, scale=3)
        self.screen.blit(title, (outer.centerx - title.get_width() // 2, 42))
        for button in self._get_profile_buttons():
            self._draw_system_button(button)
        if self.profile_tab == "achievements":
            self._draw_achievement_list()
        else:
            self._draw_statistics_list()

    def _draw_achievement_list(self):
        unlocked = self.save_data["achievements"]
        completed = len(unlocked)
        summary = render_pixel_text(self.font_status, f"COMPLETE {completed} / {len(ACHIEVEMENTS)}   {completed * 100 // len(ACHIEVEMENTS)}%", C.GOLD_LIGHT, scale=2)
        self.screen.blit(summary, (WINDOW_W // 2 - summary.get_width() // 2, 164))
        visible = 5 if is_chinese() else 6
        max_scroll = max(0, len(ACHIEVEMENTS) - visible)
        self.profile_scroll = min(self.profile_scroll, max_scroll)
        for row, definition in enumerate(ACHIEVEMENTS[self.profile_scroll:self.profile_scroll + visible]):
            achievement_id, title, description = definition[:3]
            progress, target = self._achievement_progress(definition)
            y = (194 + row * 88) if is_chinese() else (198 + row * 74)
            rect = pygame.Rect(96, y, 1088, 78 if is_chinese() else 64)
            is_unlocked = achievement_id in unlocked
            pygame.draw.rect(self.screen, C.OUTLINE, rect)
            pygame.draw.rect(self.screen, C.DESK_ICON if is_unlocked else C.DESK_PANEL_DARK, rect.inflate(-4, -4))
            pygame.draw.rect(self.screen, C.GOLD if is_unlocked else C.DESK_MUTED, rect.inflate(-10, -10), 2)
            name = render_pixel_text(self.font_status, title, C.GOLD_LIGHT if is_unlocked else C.DESK_TEXT, scale=2)
            desc = render_pixel_text(
                self.font_small, description, C.DESK_TEXT, scale=1 if is_chinese() else 2
            )
            prog = render_pixel_text(self.font_small, f"{progress} / {target}", C.GOLD_LIGHT, scale=2)
            if is_unlocked:
                unlocked_at = unlocked[achievement_id].get("unlocked_at", "").replace("T", " ")
                prog = render_pixel_text(self.font_small, unlocked_at, C.GOLD_LIGHT, scale=1)
            self.screen.blit(name, (rect.x + 18, rect.y + (8 if is_chinese() else 7)))
            self.screen.blit(desc, (rect.x + 18, rect.y + (46 if is_chinese() else 37)))
            self.screen.blit(prog, (rect.right - prog.get_width() - 18, rect.y + (34 if is_chinese() else 23)))
        hint = render_pixel_text(
            self.font_small, "WHEEL / W S TO SCROLL", C.DESK_MUTED,
            scale=1 if is_chinese() else 2
        )
        self.screen.blit(hint, (WINDOW_W // 2 - hint.get_width() // 2, 650 if is_chinese() else 670))

    def _profile_statistics_sections(self):
        stats = self.save_data["statistics"]
        return [
            ("GLOBAL", [
                ("LAUNCHES", stats["global"]["launches"]),
                ("PLAY TIME", self._format_duration(stats["global"]["play_time_ms"])),
                ("GAMES STARTED", stats["global"]["games_started"]),
                ("GAMES COMPLETE", stats["global"]["games_completed"]),
            ]),
            (f"{translate('GOMOKU')}  PLAY {self._format_duration(stats['gomoku']['play_time_ms'])}", [("GAMES", stats["gomoku"]["games_completed"]), ("BLACK WINS", stats["gomoku"]["black_wins"]), ("WHITE WINS", stats["gomoku"]["white_wins"]), ("UNDOS", stats["gomoku"]["undos"])]),
            (f"{translate('SNAKE')}  PLAY {self._format_duration(stats['snake']['play_time_ms'])}", [("GAMES", stats["snake"]["games_started"]), ("BEST", stats["snake"]["best_score"]), ("FOOD", stats["snake"]["food_eaten"]), ("DEATHS", stats["snake"]["deaths"])]),
            (f"{translate('BREAKOUT')}  PLAY {self._format_duration(stats['breakout']['play_time_ms'])}", [("BEST", stats["breakout"]["best_score"]), ("LEVEL", stats["breakout"]["highest_level"]), ("BRICKS", stats["breakout"]["bricks_broken"]), ("CLEARS", stats["breakout"]["levels_cleared"])]),
            (f"{translate('2048')}  PLAY {self._format_duration(stats['2048']['play_time_ms'])}", [("BEST", stats["2048"]["best_score"]), ("TOP TILE", stats["2048"]["highest_tile"]), ("MOVES", stats["2048"]["moves"]), ("MERGES", stats["2048"]["merges"])]),
            (f"{translate('MINES')}  PLAY {self._format_duration(stats['mines']['play_time_ms'])}", [("WINS", stats["mines"]["wins"]), ("LOSSES", stats["mines"]["losses"]), ("OPENED", stats["mines"]["cells_revealed"]), ("FLAGS", stats["mines"]["flags_placed"])]),
            (translate("MINES BEST 9 x 9"), [
                (str(count), self._format_mines_time(self.mines_best_times.get((9, count))))
                for count in MINES_COUNT_CHOICES[9]
            ]),
            (translate("MINES BEST 16 x 16"), [
                (str(count), self._format_mines_time(self.mines_best_times.get((16, count))))
                for count in MINES_COUNT_CHOICES[16]
            ]),
            (f"{translate('TETRIS')}  PLAY {self._format_duration(stats['tetris']['play_time_ms'])}", [("BEST", stats["tetris"]["best_score"]), ("LEVEL", stats["tetris"]["highest_level"]), ("LINES", stats["tetris"]["lines_cleared"]), ("TETRISES", stats["tetris"]["tetrises"])]),
            (f"{translate('AIR RAID')}  PLAY {self._format_duration(stats['air']['play_time_ms'])}", [("BEST", stats["air"]["best_score"]), ("MISSION", stats["air"]["highest_level"]), ("KILLS", stats["air"]["enemies_destroyed"]), ("S RANKS", stats["air"]["s_ranks"])]),
        ]

    def _draw_statistics_list(self):
        sections = self._profile_statistics_sections()
        visible = 4
        self.profile_scroll = min(self.profile_scroll, len(sections) - visible)
        for row, (name, values) in enumerate(sections[self.profile_scroll:self.profile_scroll + visible]):
            y = 174 + row * 116
            rect = pygame.Rect(96, y, 1088, 102)
            pygame.draw.rect(self.screen, C.OUTLINE, rect)
            pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, rect.inflate(-4, -4))
            title = render_pixel_text(self.font_status, name, C.GOLD_LIGHT, scale=2)
            self.screen.blit(title, (rect.x + 18, rect.y + 12))
            for index, (label, value) in enumerate(values):
                x = rect.x + 24 + index * (1040 // max(1, len(values)))
                text = render_pixel_text(self.font_small, label, C.DESK_MUTED, scale=2)
                number = render_pixel_text(self.font_status, str(value), C.DESK_TEXT, scale=2)
                self.screen.blit(text, (x, rect.y + 45))
                self.screen.blit(number, (x, rect.y + 70))

    # ============================================================
    #  Achievement Wall
    # ============================================================

    def _get_achievement_wall_badges(self):
        """Return 48 badge dicts with rect, index, and definition."""
        panel_x = 90
        panel_y = 78
        panel_w = WINDOW_W - 180
        panel_h = WINDOW_H - 156
        cols = 8
        rows = 6
        gap = 8
        badge_w = (panel_w - gap * (cols + 1)) // cols
        badge_h = (panel_h - gap * (rows + 1) - 52) // rows
        start_x = panel_x + gap
        start_y = panel_y + 46

        badges = []
        for index, definition in enumerate(ACHIEVEMENTS):
            row = index // cols
            col = index % cols
            x = start_x + col * (badge_w + gap)
            y = start_y + row * (badge_h + gap)
            rect = pygame.Rect(x, y, badge_w, badge_h)
            badges.append({"rect": rect, "index": index, "definition": definition})
        return badges

    def _start_achievement_wall_close(self):
        """Begin close animation, capping frame so easing starts immediately."""
        self.achievement_wall_detail_frame = min(self.achievement_wall_detail_frame, 24)
        self.achievement_wall_detail_closing = True

    def _handle_achievement_wall_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.achievement_wall_detail_index is not None and not self.achievement_wall_detail_closing:
                self._start_achievement_wall_close()
            elif self.achievement_wall_detail_index is None:
                self._start_transition(self.DESKTOP, "fade", frames=28)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            badges = self._get_achievement_wall_badges()
            # Check X button first when detail is open
            if self.achievement_wall_detail_index is not None and not self.achievement_wall_detail_closing:
                close_rect = self._get_achievement_wall_close_rect(badges)
                if close_rect.collidepoint(event.pos):
                    self._start_achievement_wall_close()
                    return
                detail_rect = self._get_achievement_wall_detail_rect(badges)
                if not detail_rect.collidepoint(event.pos):
                    self._start_achievement_wall_close()
                    return
                return
            # Normal badge selection
            for badge in badges:
                if badge["rect"].collidepoint(event.pos):
                    self.achievement_wall_pressed_index = badge["index"]
                    return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.achievement_wall_pressed_index is not None:
                badges = self._get_achievement_wall_badges()
                for badge in badges:
                    if badge["rect"].collidepoint(event.pos) and badge["index"] == self.achievement_wall_pressed_index:
                        self.achievement_wall_detail_index = badge["index"]
                        self.achievement_wall_detail_frame = 0
                        self.achievement_wall_detail_closing = False
                        break
                self.achievement_wall_pressed_index = None

    def _get_achievement_wall_detail_rect(self, badges):
        panel_w = 540
        panel_h = 420
        cx = WINDOW_W // 2
        cy = WINDOW_H // 2
        return pygame.Rect(cx - panel_w // 2, cy - panel_h // 2, panel_w, panel_h)

    def _get_achievement_wall_close_rect(self, badges):
        """Close (X) button rect in the current detail panel coordinate."""
        detail_rect = self._get_achievement_wall_detail_rect(badges)
        close_btn_size = 34
        return pygame.Rect(
            detail_rect.right - close_btn_size - 4,
            detail_rect.y + 4,
            close_btn_size, close_btn_size,
        )

    def _achievement_wall_detail_t(self):
        """Ease-out-back progress: 0→1 for open, 1→0 for close."""
        max_frames = 24
        frame = min(self.achievement_wall_detail_frame, max_frames)
        t = frame / max_frames
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

    def _draw_achievement_badge_icon(self, rect, definition, unlocked):
        icon_size = 28
        ix = rect.x + (rect.width - icon_size) // 2
        iy = rect.y + 6
        icon_rect = pygame.Rect(ix, iy, icon_size, icon_size)
        aid = definition[0]
        seed = sum(ord(c) for c in aid)
        rng = random.Random(seed)

        dot = 4
        gap_px = 2
        cols = (icon_size - gap_px) // (dot + gap_px)
        rows = cols
        ox = ix + (icon_size - cols * (dot + gap_px) + gap_px) // 2
        oy = iy + (icon_size - rows * (dot + gap_px) + gap_px) // 2

        for row in range(rows):
            for col in range(cols):
                dx = ox + col * (dot + gap_px)
                dy = oy + row * (dot + gap_px)
                if unlocked:
                    val = rng.randint(0, 3)
                    if val == 0:
                        col_rgb = C.GOLD_LIGHT
                    elif val == 1:
                        col_rgb = C.DESK_ACCENT_LIGHT
                    elif val == 2:
                        col_rgb = C.GOLD
                    else:
                        col_rgb = C.DESK_ACCENT
                else:
                    val = rng.randint(0, 2)
                    if val == 0:
                        col_rgb = C.DESK_MUTED
                    else:
                        col_rgb = C.DESK_PANEL_DARK
                pygame.draw.rect(self.screen, col_rgb, (dx, dy, dot, dot))

        # Gold star in top-right corner for unlocked badges
        if unlocked:
            star_x = ix + icon_size - 7
            star_y = iy + 1
            for sx, sy in [(0, -2), (-1, -1), (0, -1), (1, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (0, 2)]:
                pygame.draw.rect(self.screen, C.GOLD_LIGHT, (star_x + sx * 2, star_y + sy * 2, 2, 2))

        return icon_rect

    def _draw_achievement_badge(self, badge, selected=False):
        rect = badge["rect"]
        definition = badge["definition"]
        aid, title, description, game_key, stat_key, target = definition
        unlocked_data = self.save_data["achievements"].get(aid)
        unlocked = unlocked_data is not None

        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos) and self.achievement_wall_detail_index is None

        draw_rect = rect.copy()
        border_color = C.OUTLINE
        fill_color = C.DESK_PANEL if selected else C.DESK_PANEL_DARK

        if hovered:
            draw_rect = draw_rect.inflate(6, 6)
            border_color = C.DESK_ACCENT_LIGHT
            fill_color = C.DESK_ICON_HOVER
            # Shadow
            shadow = draw_rect.move(3, 3)
            pygame.draw.rect(self.screen, C.OUTLINE, shadow)

        pygame.draw.rect(self.screen, border_color, draw_rect)
        pygame.draw.rect(self.screen, fill_color, draw_rect.inflate(-2, -2))

        # Adjust icon and text positions for hovered rect
        base_rect = draw_rect

        self._draw_achievement_badge_icon(base_rect, definition, unlocked)

        if unlocked:
            progress, target_val = self._achievement_progress(definition)
            progress = min(progress, target_val)
            bar_rect = pygame.Rect(base_rect.x + 8, base_rect.bottom - 16, base_rect.width - 16, 6)
            pygame.draw.rect(self.screen, C.DESK_PANEL, bar_rect)
            if target_val > 0:
                fill_w = int(bar_rect.width * progress / target_val)
                pygame.draw.rect(self.screen, C.GOLD, (bar_rect.x, bar_rect.y, fill_w, bar_rect.height))
                if fill_w > 2:
                    pygame.draw.rect(self.screen, C.GOLD_LIGHT, (bar_rect.x + 1, bar_rect.y + 1, fill_w - 2, 2))
            pygame.draw.rect(self.screen, C.OUTLINE, bar_rect, 1)

        display_title = translate(title) if unlocked else "???"
        title_short = display_title[:12] if len(display_title) > 12 else display_title
        txt_color = C.GOLD_LIGHT if hovered else (C.GOLD_LIGHT if unlocked else C.DESK_MUTED)
        txt = render_pixel_text(self.font_small, title_short, txt_color, scale=1)
        self.screen.blit(txt, (base_rect.x + (base_rect.width - txt.get_width()) // 2, base_rect.y + base_rect.height - 30))

    def _draw_achievement_wall(self):
        # Gradient background
        bg_rect = pygame.Rect(0, 0, WINDOW_W, WINDOW_H)
        for i in range(bg_rect.height):
            t = i / max(1, bg_rect.height - 1)
            r = int(C.DESK_BG_TOP[0] * (1 - t) + C.DESK_BG_BOTTOM[0] * t)
            g = int(C.DESK_BG_TOP[1] * (1 - t) + C.DESK_BG_BOTTOM[1] * t)
            b = int(C.DESK_BG_TOP[2] * (1 - t) + C.DESK_BG_BOTTOM[2] * t)
            pygame.draw.line(self.screen, (r, g, b), (bg_rect.x, bg_rect.y + i), (bg_rect.right, bg_rect.y + i))

        panel_rect = pygame.Rect(80, 62, WINDOW_W - 160, WINDOW_H - 124)
        # Three depth layers
        pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, panel_rect)
        pygame.draw.rect(self.screen, C.OUTLINE, panel_rect, 3)
        pygame.draw.rect(self.screen, C.DESK_ACCENT, panel_rect.inflate(-10, -10), 2)

        draw_restrained_meteors(self.screen, panel_rect, self.anim_tick, max_meteors=2, alpha_scale=0.75)

        # Title with shadow
        title_x = panel_rect.centerx
        title_y = panel_rect.y + 4
        title_text = "ACHIEVEMENT WALL"
        title_shadow = render_pixel_text(self.font_title, title_text, C.OUTLINE, scale=3)
        title_main = render_pixel_text(self.font_title, title_text, C.GOLD_LIGHT, scale=3)
        self.screen.blit(title_shadow, (title_x - title_shadow.get_width() // 2 + 3, title_y + 3))
        self.screen.blit(title_main, (title_x - title_main.get_width() // 2, title_y))

        # Gold separator line
        sep_y = panel_rect.y + 52
        sep_w = panel_rect.width - 40
        sep_x = panel_rect.x + 20
        pygame.draw.line(self.screen, C.GOLD_DARK, (sep_x, sep_y), (sep_x + sep_w, sep_y), 2)
        pygame.draw.line(self.screen, C.OUTLINE, (sep_x + 2, sep_y + 3), (sep_x + sep_w - 2, sep_y + 3), 1)

        badges = self._get_achievement_wall_badges()
        unlocked_count = sum(1 for b in badges if self.save_data["achievements"].get(b["definition"][0]))

        for badge in badges:
            selected = badge["index"] == self.achievement_wall_detail_index
            self._draw_achievement_badge(badge, selected=selected)

        # Footer status bar
        footer_rect = pygame.Rect(panel_rect.x + 10, panel_rect.bottom - 34, panel_rect.width - 20, 26)
        pygame.draw.rect(self.screen, C.OUTLINE, footer_rect)
        pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, footer_rect.inflate(-2, -2))
        pygame.draw.line(self.screen, C.DESK_ACCENT, (footer_rect.x + 1, footer_rect.y + 1), (footer_rect.right - 1, footer_rect.y + 1), 1)

        footer = render_pixel_text(self.font_small, f"UNLOCKED {unlocked_count} / 48", C.DESK_MUTED, scale=2)
        self.screen.blit(footer, (footer_rect.centerx - footer.get_width() // 2, footer_rect.centery - footer.get_height() // 2))

        esc_text = render_pixel_text(self.font_small, "ESC RETURN", C.DESK_MUTED, scale=1)
        self.screen.blit(esc_text, (footer_rect.right - esc_text.get_width() - 8, footer_rect.centery - esc_text.get_height() // 2))

        if self.achievement_wall_detail_index is not None and not self.achievement_wall_detail_closing:
            self.achievement_wall_detail_frame += 1
        if self.achievement_wall_detail_closing:
            self.achievement_wall_detail_frame -= 1

        if self.achievement_wall_detail_index is not None:
            self._draw_achievement_wall_detail(badges)

        if self.achievement_wall_detail_closing and self.achievement_wall_detail_frame <= 0:
            self.achievement_wall_detail_frame = 0
            self.achievement_wall_detail_index = None
            self.achievement_wall_detail_closing = False

    def _draw_achievement_wall_detail(self, badges):
        source_index = self.achievement_wall_detail_index
        source = badges[source_index]
        definition = source["definition"]
        aid, title, description, game_key, stat_key, target = definition

        unlocked_data = self.save_data["achievements"].get(aid)
        unlocked = unlocked_data is not None

        dest = self._get_achievement_wall_detail_rect(badges)
        t = self._achievement_wall_detail_t()
        frame = self.achievement_wall_detail_frame

        # Darken background
        dark_overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, int(160 * min(1.0, frame / 18.0))))
        self.screen.blit(dark_overlay, (0, 0))

        # Interpolate rect
        cur_x = int(source["rect"].x + (dest.x - source["rect"].x) * t)
        cur_y = int(source["rect"].y + (dest.y - source["rect"].y) * t)
        cur_w = int(source["rect"].width + (dest.width - source["rect"].width) * t)
        cur_h = int(source["rect"].height + (dest.height - source["rect"].height) * t)
        cur_rect = pygame.Rect(cur_x, cur_y, cur_w, cur_h)

        # Decorative border (Cuphead-style corners)
        draw_decorative_border(self.screen, cur_rect, C.OUTLINE, 4)
        # Three depth layers
        pygame.draw.rect(self.screen, C.DESK_PANEL, cur_rect.inflate(-8, -8))
        pygame.draw.rect(self.screen, C.DESK_ACCENT, cur_rect.inflate(-16, -16), 2)
        pygame.draw.rect(self.screen, C.GOLD_DARK, cur_rect.inflate(-22, -22), 1)

        # Draw icon (scales with rect)
        icon_size = int(28 + (40 - 28) * t)
        icon_rect = pygame.Rect(
            cur_rect.x + (cur_w - icon_size) // 2,
            cur_rect.y + int(8 + (16 - 8) * t),
            icon_size, icon_size,
        )
        self._draw_achievement_badge_icon(icon_rect, definition, unlocked)

        # Fade-in text content after reaching near-full size
        detail_t = max(0.0, min(1.0, t * 1.6 - 0.3))

        # Game label
        game_names = {
            "gomoku": "GOMOKU", "snake": "SNAKE", "breakout": "BREAKOUT",
            "2048": "2048", "mines": "MINES", "tetris": "TETRIS", "air": "AIR RAID",
        }
        game_label = game_names.get(game_key, game_key.upper())
        game_colors = {
            "gomoku": C.GOLD, "snake": C.SNAKE_ACCENT, "breakout": C.BREAKOUT_ACCENT,
            "2048": C.G2048_ACCENT, "mines": C.MINES_ACCENT, "tetris": C.TETRIS_ACCENT,
            "air": C.AIR_ACCENT,
        }
        game_color = game_colors.get(game_key, C.DESK_ACCENT)

        if detail_t > 0.01:
            # Game tag
            tag_surf = render_pixel_text(self.font_small, game_label, game_color, scale=1)
            tag_surf.set_alpha(int(255 * detail_t))
            self.screen.blit(tag_surf, (cur_rect.centerx - tag_surf.get_width() // 2, cur_rect.y + int(48 * t)))

            display_title = translate(title)
            title_surf = render_pixel_text(self.font_title, display_title, C.GOLD_LIGHT, scale=2)
            title_surf.set_alpha(int(255 * detail_t))
            self.screen.blit(title_surf, (cur_rect.centerx - title_surf.get_width() // 2, cur_rect.y + int(74 * t)))

            display_desc = translate(description)
            desc_surf = render_pixel_text(self.font_small, display_desc, C.DESK_TEXT, scale=1)
            desc_surf.set_alpha(int(255 * detail_t))
            self.screen.blit(desc_surf, (cur_rect.centerx - desc_surf.get_width() // 2, cur_rect.y + int(120 * t)))

            # Progress bar in detail
            bar_rect = pygame.Rect(cur_rect.x + 60, cur_rect.y + int(155 * t), cur_rect.width - 120, 10)
            if unlocked:
                progress, _ = self._achievement_progress(definition)
                progress = min(progress, target)
            else:
                progress = 0
            fill_w = int(bar_rect.width * progress / max(1, target))

            pygame.draw.rect(self.screen, C.OUTLINE, bar_rect)
            pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, bar_rect.inflate(-2, -2))
            if fill_w > 0:
                pygame.draw.rect(self.screen, C.GOLD, (bar_rect.x + 1, bar_rect.y + 1, fill_w - 2, bar_rect.height - 2))
                if fill_w > 4:
                    pygame.draw.rect(self.screen, C.GOLD_LIGHT, (bar_rect.x + 2, bar_rect.y + 2, fill_w - 4, 3))
            target_surf = render_pixel_text(self.font_small, f"{progress} / {target}", C.DESK_ACCENT_LIGHT, scale=1)
            target_surf.set_alpha(int(255 * detail_t))
            self.screen.blit(target_surf, (cur_rect.centerx - target_surf.get_width() // 2, bar_rect.bottom + 4))

            if unlocked:
                unlocked_at = unlocked_data.get("unlocked_at", "")
                unlocked_label = translate("UNLOCKED") if "UNLOCKED" else "UNLOCKED"
                date_text = f"{unlocked_label}: {unlocked_at}"
                date_surf = render_pixel_text(self.font_small, date_text, C.DESK_MUTED, scale=1)
                date_surf.set_alpha(int(255 * detail_t))
                self.screen.blit(date_surf, (cur_rect.centerx - date_surf.get_width() // 2, cur_rect.y + int(210 * t)))

        # Bottom hint bar
        footer_rect = pygame.Rect(cur_rect.x + 20, cur_rect.bottom - 26, cur_rect.width - 40, 18)
        if detail_t > 0.8:
            pygame.draw.rect(self.screen, C.OUTLINE, footer_rect)
            pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, footer_rect.inflate(-2, -2))
            hint = render_pixel_text(self.font_small, "CLICK OUTSIDE OR ESC TO CLOSE", C.DESK_MUTED, scale=1)
            hint.set_alpha(int(255 * detail_t))
            self.screen.blit(hint, (footer_rect.centerx - hint.get_width() // 2, footer_rect.centery - hint.get_height() // 2))

        # --- Close button (pixel-art X) in top-right corner ---
        close_btn_size = 34
        close_x = cur_rect.right - close_btn_size - 6
        close_y = cur_rect.y + 6
        close_rect = pygame.Rect(close_x, close_y, close_btn_size, close_btn_size)

        mouse_pos = pygame.mouse.get_pos()
        hovered = close_rect.collidepoint(mouse_pos)
        pressed = hovered and pygame.mouse.get_pressed()[0]

        close_color = C.GOLD_LIGHT if hovered else C.DESK_MUTED
        if pressed:
            close_color = C.GOLD

        pygame.draw.rect(self.screen, C.OUTLINE, close_rect)
        bg_c = C.DESK_PANEL_DARK if pressed else C.DESK_PANEL
        pygame.draw.rect(self.screen, bg_c, close_rect.inflate(-2, -2))

        # Pixel-art X (3x3 block pattern)
        px = close_rect.x + 8
        py = close_rect.y + 8
        xs = [
            (0, 0), (4, 0), (8, 0), (12, 0), (16, 0),
            (2, 2), (10, 2), (14, 2),
            (4, 4), (8, 4), (12, 4),
            (14, 6), (10, 6), (2, 6),
            (16, 8), (12, 8), (8, 8), (4, 8), (0, 8),
            (14, 10), (10, 10), (2, 10),
            (12, 12), (8, 12), (4, 12),
            (10, 14), (14, 14), (2, 14),
            (16, 16), (12, 16), (8, 16), (4, 16), (0, 16),
        ]
        for dx, dy in xs:
            pygame.draw.rect(self.screen, close_color, (px + dx, py + dy, 3, 3))

        # Actual click handling is in _handle_achievement_wall_event via _get_achievement_wall_close_rect

    # ── Lore Reader ───────────────────────────────────────────

    def _init_lore_reader(self):
        self.lore_category_index = 0
        self.lore_entry_index = 0
        self.lore_scroll = 0
        self.lore_reading_entry_id = None
        self.lore_reading_page = 0
        self.lore_pressed_action = None

    @property
    def _lore_categories(self):
        cats = [("__device__", "lore_category_device")]
        for world in _lore.get_all_worlds():
            cats.append((world["game_id"], f"lore_category_{world['game_id']}"))
        return cats

    def _get_lore_entries_for_category(self, cat_id):
        if cat_id == "__device__":
            return _lore.get_device_lore()
        world = _lore.get_world(cat_id)
        return world["lore_entries"] if world else []

    def _is_lore_unlocked(self, entry):
        # All lore is always available — this is a world archive, not a reward system.
        return True

    def _unlock_lore_entry(self, entry_id):
        lore_data = self.save_data.setdefault("lore", {})
        unlocked = lore_data.setdefault("unlocked_entries", [])
        if entry_id not in unlocked:
            unlocked.append(entry_id)
            self._save_now()

    def _lore_reader_layout(self):
        panel = pygame.Rect(30, 30, WINDOW_W - 60, WINDOW_H - 60)
        return {
            "panel": panel,
            "tab_w": 130,
            "tab_y": panel.y + 104,
            "list_y": panel.y + 156,
            "entry_h": 40,
            "entry_gap": 8,
            "visible_entries": 8,
        }

    def _lore_category_label(self, cat_id, cat_key):
        if is_chinese():
            return translate(cat_key)
        if cat_id == "__device__":
            return "MERIDIAN"
        world = _lore.get_world(cat_id)
        if world:
            return world.get("desktop_subtitle_en") or world.get("world_name_en") or cat_id.upper()
        return cat_id.upper()

    def _render_lore_fitted_text(self, font, text, color, max_width, scale=1):
        display_text = translate(text)
        surface = render_pixel_text(font, display_text, color, scale=scale)
        if surface.get_width() <= max_width:
            return surface
        if scale > 1:
            surface = render_pixel_text(font, display_text, color, scale=1)
            if surface.get_width() <= max_width:
                return surface
        while len(display_text) > 1:
            display_text = display_text[:-1]
            candidate = render_pixel_text(font, display_text + "...", color, scale=1)
            if candidate.get_width() <= max_width:
                return candidate
        return render_pixel_text(font, "...", color, scale=1)

    def _wrap_lore_line(self, font, line, max_width, scale=1):
        if render_pixel_text(font, line, C.LORE_TEXT, scale=scale).get_width() <= max_width:
            return [line]
        if is_chinese() or contains_chinese(line):
            wrapped = []
            current = ""
            for char in line:
                candidate = current + char
                if current and render_pixel_text(font, candidate, C.LORE_TEXT, scale=scale).get_width() > max_width:
                    wrapped.append(current)
                    current = char
                else:
                    current = candidate
            if current:
                wrapped.append(current)
            return wrapped

        wrapped = []
        current = ""
        for word in line.split():
            candidate = word if not current else current + " " + word
            if current and render_pixel_text(font, candidate, C.LORE_TEXT, scale=scale).get_width() > max_width:
                wrapped.append(current)
                current = word
            else:
                current = candidate
        if current:
            wrapped.append(current)
        return wrapped or [line]

    def _lore_story_wrapped_lines(self, entry, font, max_width):
        raw_lines = entry["content_zh"] if is_chinese() else entry["content_en"]
        wrapped = []
        for raw_line in raw_lines:
            wrapped.extend(self._wrap_lore_line(font, raw_line, max_width, scale=1))
            wrapped.append("")
        if wrapped and wrapped[-1] == "":
            wrapped.pop()
        return wrapped

    def _handle_lore_reader_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._go_system_desktop()
                return
            if event.key in (pygame.K_UP, pygame.K_w):
                self.lore_entry_index = max(0, self.lore_entry_index - 1)
                self.lore_scroll = self.lore_entry_index
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                entries = self._get_lore_entries_for_category(
                    self._lore_categories[self.lore_category_index][0])
                self.lore_entry_index = min(len(entries) - 1, self.lore_entry_index + 1) if entries else 0
                self.lore_scroll = self.lore_entry_index
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.lore_category_index = max(0, self.lore_category_index - 1)
                self.lore_entry_index = 0
                self.lore_scroll = 0
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                max_cat = len(self._lore_categories) - 1
                self.lore_category_index = min(max_cat, self.lore_category_index + 1)
                self.lore_entry_index = 0
                self.lore_scroll = 0
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                cat_id = self._lore_categories[self.lore_category_index][0]
                entries = self._get_lore_entries_for_category(cat_id)
                if entries and self.lore_entry_index < len(entries):
                    entry = entries[self.lore_entry_index]
                    if self._is_lore_unlocked(entry):
                        self._start_lore_reading(entry)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.lore_pressed_action = "click"
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.lore_pressed_action == "click":
                layout = self._lore_reader_layout()
                panel = layout["panel"]
                tab_w = layout["tab_w"]
                tab_y = layout["tab_y"]
                # Check category tabs
                for i, (cat_id, cat_key) in enumerate(self._lore_categories):
                    tx = panel.x + 26 + i * (tab_w + 8)
                    if tx + tab_w > panel.right - 10:
                        break
                    tab_rect = pygame.Rect(tx, tab_y, tab_w, 32)
                    if tab_rect.collidepoint(event.pos):
                        self.lore_category_index = i
                        self.lore_entry_index = 0
                        self.lore_scroll = 0
                        self.lore_pressed_action = None
                        return
                # Check entry list
                cat_id = self._lore_categories[self.lore_category_index][0]
                entries = self._get_lore_entries_for_category(cat_id)
                visible_start = self.lore_scroll
                list_y = layout["list_y"]
                step = layout["entry_h"] + layout["entry_gap"]
                for vi in range(min(layout["visible_entries"], len(entries) - visible_start)):
                    ei = visible_start + vi
                    ey = list_y + vi * step
                    entry_rect = pygame.Rect(panel.x + 26, ey, panel.width - 52, layout["entry_h"])
                    if entry_rect.collidepoint(event.pos) and ei < len(entries):
                        entry = entries[ei]
                        self.lore_entry_index = ei
                        self._start_lore_reading(entry)
                        self.lore_pressed_action = None
                        return
            self.lore_pressed_action = None

    def _start_lore_reading(self, entry):
        self.lore_reading_entry_id = entry["id"]
        self.lore_reading_page = 0
        # Mark as read
        lore_data = self.save_data.setdefault("lore", {})
        read = lore_data.setdefault("read_entries", [])
        if entry["id"] not in read:
            read.append(entry["id"])
            self._save_now()
        self.state = self.LORE_STORY

    def _handle_lore_story_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.state = self.LORE_READER
                return
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                entry = _lore.get_lore_entry(self.lore_reading_entry_id)
                if entry:
                    story_font = get_chinese_font(16)
                    panel = pygame.Rect(100, 50, WINDOW_W - 200, WINDOW_H - 100)
                    lines = self._lore_story_wrapped_lines(entry, story_font, panel.width - 100)
                    max_page = max(0, (len(lines) - 1) // 10)
                    self.lore_reading_page = min(self.lore_reading_page + 1, max_page)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.lore_reading_page = max(0, self.lore_reading_page - 1)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.state = self.LORE_READER

    def _draw_lore_reader(self):
        self.screen.fill(C.LORE_BG)
        # Gradient bg
        layout = self._lore_reader_layout()
        panel = layout["panel"]
        for y in range(panel.height):
            t = y / max(1, panel.height - 1)
            r = int(C.LORE_BG[0] * (1 - t) + C.DESK_BG_BOTTOM[0] * t)
            g = int(C.LORE_BG[1] * (1 - t) + C.DESK_BG_BOTTOM[1] * t)
            b = int(C.LORE_BG[2] * (1 - t) + C.DESK_BG_BOTTOM[2] * t)
            pygame.draw.line(self.screen, (r, g, b), (panel.x, panel.y + y), (panel.right, panel.y + y))
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 4)
        pygame.draw.rect(self.screen, C.LORE_ACCENT, panel.inflate(-8, -8), 2)

        # Title (with translation)
        title_text = "异界档案" if is_chinese() else "LORE ARCHIVE"
        title = self._render_lore_fitted_text(
            self.font_menu_title, title_text, C.LORE_TITLE, panel.width - 160, scale=3)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 14))

        # Subtitle / description
        desc_text = "MERIDIAN \u2014 \u4e03\u754c\u8bb0\u5f55" if is_chinese() else "MERIDIAN \u2014 CHRONICLES OF SEVEN WORLDS"
        desc = self._render_lore_fitted_text(self.font_small, desc_text, C.LORE_MUTED, panel.width - 240, scale=1)
        self.screen.blit(desc, (panel.centerx - desc.get_width() // 2, panel.y + 76))

        # Category tabs — moved down to avoid overlap
        tab_w = layout["tab_w"]
        cats = self._lore_categories
        tab_y = layout["tab_y"]
        for i, (cat_id, cat_key) in enumerate(cats):
            tx = panel.x + 26 + i * (tab_w + 8)
            if tx + tab_w > panel.right - 10:
                break
            tab_rect = pygame.Rect(tx, tab_y, tab_w, 32)
            selected = i == self.lore_category_index
            fill = C.LORE_PANEL if selected else C.LORE_PANEL_DARK
            border = C.LORE_TITLE if selected else C.LORE_MUTED
            pygame.draw.rect(self.screen, C.OUTLINE, tab_rect)
            pygame.draw.rect(self.screen, fill, tab_rect.inflate(-2, -2))
            pygame.draw.rect(self.screen, border, tab_rect.inflate(-6, -6), 1)
            cat_label = self._lore_category_label(cat_id, cat_key)
            cat_txt = self._render_lore_fitted_text(
                self.font_small, cat_label, C.LORE_TEXT if selected else C.LORE_MUTED,
                tab_rect.width - 16, scale=1)
            self.screen.blit(cat_txt, (tab_rect.centerx - cat_txt.get_width() // 2,
                                       tab_rect.centery - cat_txt.get_height() // 2))

        # Entry list
        cat_id, _ = cats[self.lore_category_index]
        entries = self._get_lore_entries_for_category(cat_id)
        visible_start = self.lore_scroll
        list_y = layout["list_y"]
        mouse_pos = self._logical_mouse_pos()
        step = layout["entry_h"] + layout["entry_gap"]

        for vi in range(min(layout["visible_entries"], len(entries) - visible_start)):
            if vi < 0:
                continue
            ei = visible_start + vi
            if ei >= len(entries):
                break
            entry = entries[ei]
            ey = list_y + vi * step
            entry_rect = pygame.Rect(panel.x + 26, ey, panel.width - 52, layout["entry_h"])
            unlocked = self._is_lore_unlocked(entry)
            hovered = entry_rect.collidepoint(mouse_pos)
            is_read = entry["id"] in self.save_data.get("lore", {}).get("read_entries", [])
            selected = ei == self.lore_entry_index

            fill = C.LORE_PANEL if (hovered or selected) else C.LORE_PANEL_DARK
            border = C.LORE_TITLE if selected else (C.LORE_ACCENT if hovered else C.LORE_MUTED)
            pygame.draw.rect(self.screen, C.OUTLINE, entry_rect)
            pygame.draw.rect(self.screen, fill, entry_rect.inflate(-2, -2))
            pygame.draw.rect(self.screen, border, entry_rect.inflate(-6, -6), 1)

            if unlocked:
                title_text = entry["title_zh"] if is_chinese() else entry["title_en"]
                col = C.LORE_TEXT if not is_read else C.LORE_ACCENT_LIGHT
            else:
                title_text = entry["title_zh"] if is_chinese() else entry["title_en"]
                col = C.LORE_TEXT

            et = self._render_lore_fitted_text(self.font_small, title_text, col, entry_rect.width - 58, scale=1)
            self.screen.blit(et, (entry_rect.x + 14, entry_rect.centery - et.get_height() // 2))

            # Read indicator
            if unlocked and is_read:
                dot_col = C.LORE_ACCENT_LIGHT
                pygame.draw.rect(self.screen, dot_col, (entry_rect.right - 24, entry_rect.centery - 3, 8, 6))

        # Hint
        hint_text = "ESC: \u8fd4\u56de   \u56de\u8f66: \u9605\u8bfb   A/D: \u5206\u7c7b" if is_chinese() else "ESC: DESKTOP   ENTER: READ   A/D: CATEGORY"
        hint = render_pixel_text(self.font_small, hint_text, C.LORE_MUTED, scale=1)
        self.screen.blit(hint, (panel.centerx - hint.get_width() // 2, panel.bottom - 28))

    def _draw_lore_story(self):
        entry = _lore.get_lore_entry(self.lore_reading_entry_id)
        if not entry:
            self.state = self.LORE_READER
            return

        self.screen.fill(C.LORE_BG)
        panel = pygame.Rect(100, 50, WINDOW_W - 200, WINDOW_H - 100)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 4)
        pygame.draw.rect(self.screen, C.LORE_PANEL, panel.inflate(-8, -8))
        pygame.draw.rect(self.screen, C.LORE_ACCENT, panel.inflate(-16, -16), 2)

        # Title
        title_text = entry["title_zh"] if is_chinese() else entry["title_en"]
        title = self._render_lore_fitted_text(
            self.font_menu_title, title_text, C.LORE_TITLE, panel.width - 120, scale=3)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 24))

        # Content
        story_font = get_chinese_font(16)
        lines = self._lore_story_wrapped_lines(entry, story_font, panel.width - 100)
        lines_per_page = 10
        start = self.lore_reading_page * lines_per_page
        page_lines = lines[start:start + lines_per_page]
        max_page = max(0, (len(lines) - 1) // lines_per_page)

        for li, line in enumerate(page_lines):
            y = panel.y + 92 + li * 36
            if not line:
                continue
            txt = render_pixel_text(story_font, line, C.LORE_TEXT, scale=1)
            self.screen.blit(txt, (panel.x + 50, y))

        # Page indicator
        if max_page > 0:
            pi_text = f"{self.lore_reading_page + 1} / {max_page + 1}"
            pi = render_pixel_text(self.font_small, pi_text, C.LORE_MUTED, scale=1)
            self.screen.blit(pi, (panel.centerx - pi.get_width() // 2, panel.bottom - 70))

        # Hint
        hint_text = "\u56de\u8f66 / \u70b9\u51fb\u8fd4\u56de   A/D: \u7ffb\u9875" if is_chinese() else "ENTER / CLICK TO RETURN   A/D: PAGE"
        hint = self._render_lore_fitted_text(self.font_small, hint_text, C.LORE_ACCENT_LIGHT, panel.width - 120, scale=2)
        self.screen.blit(hint, (panel.centerx - hint.get_width() // 2, panel.bottom - 44))
