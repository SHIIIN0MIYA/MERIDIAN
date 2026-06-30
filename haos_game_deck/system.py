"""Unified settings, profile, statistics, achievements, and persistence UI."""

import datetime as dt
import json

from .common import *
from .persistence import SaveManager, default_data, default_settings
from .localization import set_language


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
}


class SystemMixin:
    def _init_system(self, save_path=None):
        self.save_manager = SaveManager(save_path)
        self.save_data = self.save_manager.load()
        self.system_pressed_action = None
        self.system_dialog = None
        self.profile_tab = "achievements"
        self.profile_scroll = 0
        self.achievement_notifications = []
        self._last_persisted_snapshot = ""
        self._last_save_check = pygame.time.get_ticks()
        self._last_usage_tick = pygame.time.get_ticks()
        self._display_offset = (0, 0)
        self._display_scale = 1.0
        self._apply_loaded_data()
        self.save_data["statistics"]["global"]["launches"] += 1
        self._save_now()

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
        self.mines_size = int(settings["mines_size"])
        self.mines_count = int(settings["mines_count"])
        self._apply_snake_preferences()
        self._apply_breakout_preferences()
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
        return data

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
        for definition in ACHIEVEMENTS:
            achievement_id, title = definition[0], definition[1]
            progress, target = self._achievement_progress(definition)
            if progress >= target and achievement_id not in unlocked:
                unlocked[achievement_id] = {"unlocked_at": dt.datetime.now().isoformat(timespec="seconds")}
                self.achievement_notifications.append({"title": title, "frame": 0})
                self.audio.play("achievement", 0.85)
                newly_unlocked = True
        if newly_unlocked:
            self._save_now()

    def _update_achievement_notifications(self):
        if not self.achievement_notifications:
            return
        self.achievement_notifications[0]["frame"] += 1
        if self.achievement_notifications[0]["frame"] >= 240:
            self.achievement_notifications.pop(0)

    def _draw_achievement_notification(self):
        if not self.achievement_notifications:
            return
        item = self.achievement_notifications[0]
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
        y = int(-panel_h - 14 + (panel_h + 30) * ease_out_back(t))
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
        }
        return values.get(action, "")

    def _handle_system_settings_event(self, event):
        if self.system_dialog:
            self._handle_system_dialog_event(event)
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_desktop()
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
            self._go_desktop()
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
                self._go_desktop()
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
                        self._go_desktop()
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

    def _draw_statistics_list(self):
        stats = self.save_data["statistics"]
        sections = [
            ("GLOBAL", [
                ("LAUNCHES", stats["global"]["launches"]),
                ("PLAY TIME", self._format_duration(stats["global"]["play_time_ms"])),
                ("GAMES STARTED", stats["global"]["games_started"]),
                ("GAMES COMPLETE", stats["global"]["games_completed"]),
            ]),
            (f"GOMOKU  PLAY {self._format_duration(stats['gomoku']['play_time_ms'])}", [("GAMES", stats["gomoku"]["games_completed"]), ("BLACK WINS", stats["gomoku"]["black_wins"]), ("WHITE WINS", stats["gomoku"]["white_wins"]), ("UNDOS", stats["gomoku"]["undos"])]),
            (f"SNAKE  PLAY {self._format_duration(stats['snake']['play_time_ms'])}", [("GAMES", stats["snake"]["games_started"]), ("BEST", stats["snake"]["best_score"]), ("FOOD", stats["snake"]["food_eaten"]), ("DEATHS", stats["snake"]["deaths"])]),
            (f"BREAKOUT  PLAY {self._format_duration(stats['breakout']['play_time_ms'])}", [("BEST", stats["breakout"]["best_score"]), ("LEVEL", stats["breakout"]["highest_level"]), ("BRICKS", stats["breakout"]["bricks_broken"]), ("CLEARS", stats["breakout"]["levels_cleared"])]),
            (f"2048  PLAY {self._format_duration(stats['2048']['play_time_ms'])}", [("BEST", stats["2048"]["best_score"]), ("TOP TILE", stats["2048"]["highest_tile"]), ("MOVES", stats["2048"]["moves"]), ("MERGES", stats["2048"]["merges"])]),
            (f"MINES  PLAY {self._format_duration(stats['mines']['play_time_ms'])}", [("WINS", stats["mines"]["wins"]), ("LOSSES", stats["mines"]["losses"]), ("OPENED", stats["mines"]["cells_revealed"]), ("FLAGS", stats["mines"]["flags_placed"])]),
            ("MINES BEST 9 x 9", [
                (str(count), self._format_mines_time(self.mines_best_times.get((9, count))))
                for count in MINES_COUNT_CHOICES[9]
            ]),
            ("MINES BEST 16 x 16", [
                (str(count), self._format_mines_time(self.mines_best_times.get((16, count))))
                for count in MINES_COUNT_CHOICES[16]
            ]),
            (f"TETRIS  PLAY {self._format_duration(stats['tetris']['play_time_ms'])}", [("BEST", stats["tetris"]["best_score"]), ("LEVEL", stats["tetris"]["highest_level"]), ("LINES", stats["tetris"]["lines_cleared"]), ("TETRISES", stats["tetris"]["tetrises"])]),
            (f"AIR RAID  PLAY {self._format_duration(stats['air']['play_time_ms'])}", [("BEST", stats["air"]["best_score"]), ("MISSION", stats["air"]["highest_level"]), ("KILLS", stats["air"]["enemies_destroyed"]), ("S RANKS", stats["air"]["s_ranks"])]),
        ]
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
