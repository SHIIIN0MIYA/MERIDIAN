from .common import *
from .localization import is_chinese


# ── Desktop Icon Registry ────────────────────────────────────
# New games call register_desktop_icon() to appear on the desktop.
DESKTOP_ICON_REGISTRY = []


def register_desktop_icon(label, action, page=0, enabled=True,
                          subtitle_en=None, subtitle_zh=None):
    """Register a desktop icon for a new game or feature.

    Args:
        label: Icon label (uppercase, max 12 chars)
        action: Action string handled in _handle_desktop_event
        page: Which desktop page (0 or 1), 6 icons per page max
        enabled: Whether the icon is clickable
        subtitle_en/zh: Subtitle shown below the label
    """
    DESKTOP_ICON_REGISTRY.append({
        "label": label,
        "action": action,
        "enabled": enabled,
        "page": int(page),
        "subtitle_en": subtitle_en,
        "subtitle_zh": subtitle_zh,
    })


class DesktopMixin:
    def _init_desktop(self):
        self.app_start_ticks = pygame.time.get_ticks()
        self.desktop_pressed_action = None
        self.desktop_volume_open = False
        self.desktop_volume_dragging = False
        self.shutdown_confirm_open = False
        self.shutdown_confirm_pressed = None
        self.desktop_esc_lock_frames = 0
        self.desktop_page = 0
        self.desktop_particles = []
        self._last_mouse_pos = (0, 0)
        self._last_clock_minute = -1
        self.desktop_hour_fx_triggered = False
        self.desktop_hour_fx_frame = 0
        self.desktop_hour_fx_x = 0
        self.desktop_hour_fx_y = 0
        self.desktop_slide_active = False
        self.desktop_slide_from_page = 0
        self.desktop_slide_to_page = 0
        self.desktop_slide_direction = 0
        self.desktop_slide_frame = 0
        self.desktop_slide_max_frames = 36

        # Build pages from registry (if empty, use defaults)
        if not DESKTOP_ICON_REGISTRY:
            self._register_builtin_icons()
        self.desktop_pages = self._build_desktop_pages()

    def _register_builtin_icons(self):
        """Register all built-in desktop icons."""
        from . import lore as _lore
        # Page 0: six games
        for gid in ("gomoku", "snake", "breakout", "2048", "mines", "tetris"):
            world = _lore.get_world(gid)
            sub_en = world["desktop_subtitle_en"] if world else None
            sub_zh = world["desktop_subtitle_zh"] if world else None
            register_desktop_icon(
                gid.upper().replace("2048", "2048"),
                f"open_{gid}",
                page=0, enabled=True,
                subtitle_en=sub_en, subtitle_zh=sub_zh,
            )
        # Page 1: Air Raid + system icons + LORE
        air_world = _lore.get_world("air")
        register_desktop_icon(
            "AIR RAID", "open_air", page=1, enabled=True,
            subtitle_en=air_world["desktop_subtitle_en"] if air_world else "SHOOT 'EM UP",
            subtitle_zh=air_world["desktop_subtitle_zh"] if air_world else "弹幕射击",
        )
        register_desktop_icon("TANK DUEL", "open_tank", page=1, enabled=True,
                              subtitle_en="LOCAL TWO-PLAYER ARENA",
                              subtitle_zh="本地双人对战")
        register_desktop_icon("SETTINGS", "open_system_settings", page=1, enabled=True)
        register_desktop_icon("PROFILE", "open_profile", page=1, enabled=True)
        register_desktop_icon("WALL", "open_achievement_wall", page=1, enabled=True)
        register_desktop_icon("LORE", "open_lore", page=1, enabled=True,
                              subtitle_en="CHRONICLE", subtitle_zh="编年史")

    def _build_desktop_pages(self):
        """Build page list from registry. 6 icons per page max."""
        max_pages = max((icon["page"] for icon in DESKTOP_ICON_REGISTRY), default=0) + 1
        pages = [[] for _ in range(max_pages)]
        for icon in DESKTOP_ICON_REGISTRY:
            page = icon["page"]
            entry = {
                "label": icon["label"],
                "action": icon["action"],
                "enabled": icon["enabled"],
            }
            sub_en = icon.get("subtitle_en")
            sub_zh = icon.get("subtitle_zh")
            if sub_en or sub_zh:
                entry["subtitle_en"] = sub_en
                entry["subtitle_zh"] = sub_zh
            pages[page].append(entry)
        return pages

    def _get_desktop_volume_tab_rect(self):
        return pygame.Rect(
            DESKTOP_SCREEN_RECT.left + 8,
            DESKTOP_SCREEN_RECT.bottom - 78,
            34,
            34,
        )

    def _get_desktop_volume_panel_rect(self):
        tab = self._get_desktop_volume_tab_rect()
        return pygame.Rect(tab.right + 8, tab.y - 12, 214, 58)

    def _get_desktop_volume_slider_rect(self):
        panel = self._get_desktop_volume_panel_rect()
        return pygame.Rect(panel.x + 54, panel.centery - 4, 138, 8)

    def _set_desktop_volume_from_pos(self, pos):
        slider = self._get_desktop_volume_slider_rect()
        value = (pos[0] - slider.left) / max(1, slider.width)
        self.audio.set_music_volume(value)

    def _handle_desktop_volume_event(self, event):
        tab = self._get_desktop_volume_tab_rect()
        panel = self._get_desktop_volume_panel_rect()
        slider = self._get_desktop_volume_slider_rect()

        if event.type == pygame.MOUSEMOTION:
            if self.desktop_volume_dragging:
                self._set_desktop_volume_from_pos(event.pos)
                return True
            if tab.collidepoint(event.pos) or panel.collidepoint(event.pos):
                self.desktop_volume_open = True
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if tab.collidepoint(event.pos):
                self.desktop_volume_open = not self.desktop_volume_open
                return True
            if self.desktop_volume_open and slider.inflate(12, 18).collidepoint(event.pos):
                self.desktop_volume_dragging = True
                self._set_desktop_volume_from_pos(event.pos)
                return True
            if self.desktop_volume_open and not panel.collidepoint(event.pos):
                self.desktop_volume_open = False
            return False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.desktop_volume_dragging:
                self._set_desktop_volume_from_pos(event.pos)
                self.desktop_volume_dragging = False
                return True
        return False

    def _handle_desktop_event(self, event):
        if self.shutdown_confirm_open:
            buttons = self._get_shutdown_confirm_buttons()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.shutdown_confirm_open = False
                self.shutdown_confirm_pressed = None
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        self.shutdown_confirm_pressed = button["action"]
                        return
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos) and self.shutdown_confirm_pressed == button["action"]:
                        action = button["action"]
                        self.shutdown_confirm_pressed = None
                        if action == "cancel":
                            self.shutdown_confirm_open = False
                        else:
                            self._start_shutdown()
                        return
                self.shutdown_confirm_pressed = None
            return
        if self._handle_desktop_volume_event(event):
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.desktop_esc_lock_frames <= 0:
                    self.shutdown_confirm_open = True
                    self.shutdown_confirm_pressed = None
            return
        if self.desktop_slide_active: return
        all_btn = self._get_desktop_icon_buttons() + self._get_desktop_page_buttons()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in all_btn:
                if b["rect"].collidepoint(event.pos): self.desktop_pressed_action = b["action"]; return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in all_btn:
                if b["rect"].collidepoint(event.pos) and self.desktop_pressed_action == b["action"]:
                    action = b["action"]
                    if action == "open_gomoku": self._desktop_return_effect = "gomoku_grid"; self._start_transition(self.MENU, "gomoku_grid", frames=44)
                    elif action == "open_snake": self._desktop_return_effect = "snake_scan"; self._start_transition(self.SNAKE_MENU, "snake_scan", frames=50)
                    elif action == "open_breakout": self._desktop_return_effect = "breakout_bricks"; self._start_transition(self.BREAKOUT_MENU, "breakout_bricks", frames=48)
                    elif action == "open_2048": self._desktop_return_effect = "g2048_tiles"; self._start_transition(self.G2048_MENU, "g2048_tiles", frames=44)
                    elif action == "open_mines": self._desktop_return_effect = "mines_radar"; self._start_transition(self.MINES_MENU, "mines_radar", frames=50)
                    elif action == "open_tetris": self._desktop_return_effect = "tetris_drop"; self._start_transition(self.TETRIS_MENU, "tetris_drop", frames=58)
                    elif action == "open_air": self._desktop_return_effect = "air_sweep"; self._start_transition(self.AIR_MENU, "air_sweep", frames=46)
                    elif action == "open_tank": self._desktop_return_effect = "tank_crossfire"; self._start_transition(self.TANK_MENU, "tank_crossfire", frames=48)
                    elif action == "open_system_settings": self._start_transition(self.SYSTEM_SETTINGS, "fade", frames=28)
                    elif action == "open_profile": self._start_transition(self.PROFILE, "fade", frames=28)
                    elif action == "open_achievement_wall": self._start_transition(self.ACHIEVEMENT_WALL, "fade", frames=28)
                    elif action == "open_lore": self._start_transition(self.LORE_READER, "fade", frames=28)
                    elif action == "desktop_next_page" and b.get("enabled", True): self._start_desktop_page_slide(self.desktop_page + 1)
                    elif action == "desktop_prev_page" and b.get("enabled", True): self._start_desktop_page_slide(self.desktop_page - 1)
                    self.desktop_pressed_action = None; return
            self.desktop_pressed_action = None

    def _get_desktop_time_text(self):
        now = datetime.datetime.now()
        return now.strftime("%H:%M")

    def _get_battery_text(self):
        elapsed = pygame.time.get_ticks() - self.app_start_ticks
        ratio = max(0.0, 1.0 - elapsed / BATTERY_DRAIN_MS)
        battery = int(round(ratio * 100))
        return f"BAT {battery}%"

    def _get_current_desktop_icons(self):
        if not self.desktop_pages: return []
        return self.desktop_pages[self.desktop_page]

    def _get_desktop_page_buttons(self):
        rect = DESKTOP_SCREEN_RECT; buttons = []; bs = 42; by = rect.bottom - 52
        buttons.append({"rect": pygame.Rect(rect.right - bs - 18, by, bs, bs), "label": ">", "action": "desktop_next_page", "enabled": self.desktop_page < len(self.desktop_pages) - 1})
        buttons.append({"rect": pygame.Rect(rect.right - bs * 2 - 30, by, bs, bs), "label": "<", "action": "desktop_prev_page", "enabled": self.desktop_page > 0})
        return buttons

    def _start_desktop_page_slide(self, target_page):
        if self.desktop_slide_active: return
        if target_page < 0 or target_page >= len(self.desktop_pages): return
        if target_page == self.desktop_page: return
        self.desktop_slide_active = True
        self.desktop_slide_from_page = self.desktop_page; self.desktop_slide_to_page = target_page
        self.desktop_slide_direction = 1 if target_page > self.desktop_page else -1
        self.desktop_slide_frame = 0; self.desktop_pressed_action = None

    def _update_desktop_slide(self):
        if not self.desktop_slide_active: return
        self.desktop_slide_frame += 1
        if self.desktop_slide_frame >= self.desktop_slide_max_frames:
            self.desktop_page = self.desktop_slide_to_page
            self.desktop_slide_active = False; self.desktop_slide_frame = 0
            self.desktop_slide_direction = 0; self.desktop_pressed_action = None

    def _ease_in_out_cubic(self, t):
        t = max(0.0, min(1.0, t))
        if t < 0.5: return 4 * t * t * t
        return 1 - pow(-2 * t + 2, 3) / 2

    def _get_desktop_icon_buttons_for_page(self, page_index, offset_x=0, offset_y=0):
        rect = DESKTOP_SCREEN_RECT
        grid_cols = 3; grid_rows = 2; icon_size = DESKTOP_ICON_SIZE
        content_top = rect.y + DESKTOP_STATUS_H + 56; content_bottom = rect.bottom - 62
        content_h = content_bottom - content_top
        total_icon_w = grid_cols * icon_size; gap_x = (rect.width - total_icon_w) // (grid_cols + 1)
        total_icon_h = grid_rows * icon_size; gap_y = (content_h - total_icon_h) // (grid_rows + 1)
        buttons = []
        if page_index < 0 or page_index >= len(self.desktop_pages): return buttons
        icons = self.desktop_pages[page_index]
        for idx, item in enumerate(icons[:6]):
            col = idx % grid_cols; row = idx // grid_cols
            x = rect.x + gap_x + col * (icon_size + gap_x) + offset_x
            y = content_top + gap_y + row * (icon_size + gap_y) + offset_y
            buttons.append({"rect": pygame.Rect(x, y, icon_size, icon_size), "label": item["label"], "action": item["action"], "enabled": item["enabled"], "page_index": page_index, "icon_index": idx})
        return buttons

    def _get_desktop_icon_buttons(self):
        return self._get_desktop_icon_buttons_for_page(self.desktop_page)

    def _draw_handheld_shell(self):
        outer = HANDHELD_RECT

        # 澶栧３涓讳綋
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 6)
        pygame.draw.rect(self.screen, C.GOLD_DARK, outer.inflate(-8, -8), 4)

        shell_inner = outer.inflate(-18, -18)
        pygame.draw.rect(self.screen, (42, 19, 14), shell_inner)

        # 灞忓箷杈规
        screen_rect = DESKTOP_SCREEN_RECT
        pygame.draw.rect(self.screen, C.OUTLINE, screen_rect.inflate(14, 14), 4)
        pygame.draw.rect(self.screen, C.GOLD_DARK, screen_rect.inflate(6, 6), 2)

        # 鍥涜閲戝睘瑙掑潡
        corner_size = 16
        for cx, cy in [
            (screen_rect.x - 7, screen_rect.y - 7),
            (screen_rect.right - corner_size + 7, screen_rect.y - 7),
            (screen_rect.x - 7, screen_rect.bottom - corner_size + 7),
            (screen_rect.right - corner_size + 7, screen_rect.bottom - corner_size + 7),
        ]:
            pygame.draw.rect(self.screen, C.OUTLINE, (cx, cy, corner_size, corner_size))
            pygame.draw.rect(self.screen, C.GOLD_DARK, (cx + 3, cy + 3, corner_size - 6, corner_size - 6))
            pygame.draw.rect(self.screen, C.GOLD_LIGHT, (cx + 6, cy + 6, 4, 4))

    def _draw_desktop_wallpaper(self):
        rect = DESKTOP_SCREEN_RECT

        # 妗岄潰涓撶敤钃濈传娓愬彉鑳屾櫙锛屽拰浜斿瓙妫嬬殑鏈ㄨ川妫曡壊鍖哄垎寮€
        for i in range(rect.height):
            t = i / max(1, rect.height - 1)

            r = int(C.DESK_BG_TOP[0] * (1 - t) + C.DESK_BG_BOTTOM[0] * t)
            g = int(C.DESK_BG_TOP[1] * (1 - t) + C.DESK_BG_BOTTOM[1] * t)
            b = int(C.DESK_BG_TOP[2] * (1 - t) + C.DESK_BG_BOTTOM[2] * t)

            pygame.draw.line(self.screen, (r, g, b), (rect.x, rect.y + i), (rect.right, rect.y + i))

        # 鍍忕礌鏄熺偣 / 鐢靛瓙鍣偣
        dots = [
            (0.08, 0.18), (0.18, 0.32), (0.86, 0.18), (0.74, 0.34),
            (0.28, 0.58), (0.64, 0.62), (0.84, 0.76), (0.14, 0.80),
            (0.50, 0.12), (0.54, 0.86), (0.38, 0.24), (0.70, 0.50),
            (0.44, 0.72), (0.24, 0.14), (0.90, 0.52), (0.10, 0.58),
        ]

        for idx, (rx, ry) in enumerate(dots):
            x = rect.x + int(rect.width * rx)
            y = rect.y + int(rect.height * ry)

            pulse = 0.55 + 0.45 * abs(math.sin(self.anim_tick * 0.035 + idx))
            col = (
                int(C.DESK_ACCENT[0] * pulse),
                int(C.DESK_ACCENT[1] * pulse),
                int(C.DESK_ACCENT[2] * pulse),
            )

            pygame.draw.rect(self.screen, col, (x, y, 3, 3))

        draw_restrained_meteors(self.screen, rect, self.anim_tick, max_meteors=2, alpha_scale=0.75)

    def _draw_desktop_status_bar(self):
        rect = DESKTOP_SCREEN_RECT
        bar_rect = pygame.Rect(rect.x, rect.y, rect.width, DESKTOP_STATUS_H)

        pygame.draw.rect(self.screen, C.OUTLINE, bar_rect)
        pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, bar_rect.inflate(-4, -4))
        pygame.draw.line(self.screen, C.DESK_ACCENT, (bar_rect.x + 8, bar_rect.bottom - 3), (bar_rect.right - 8, bar_rect.bottom - 3), 2)

        left_text = self._get_desktop_time_text()
        center_text = DECK_TITLE
        right_text = self._get_battery_text()

        # Clock pulse during hour celebration
        clock_color = C.DESK_TEXT
        clock_scale = 2
        if 0 < self.desktop_hour_fx_frame <= 35:
            pulse = self.desktop_hour_fx_frame / 35.0
            clock_color = (
                int(C.DESK_TEXT[0] + (C.GOLD_LIGHT[0] - C.DESK_TEXT[0]) * pulse),
                int(C.DESK_TEXT[1] + (C.GOLD_LIGHT[1] - C.DESK_TEXT[1]) * pulse),
                int(C.DESK_TEXT[2] + (C.GOLD_LIGHT[2] - C.DESK_TEXT[2]) * pulse),
            )
            clock_scale = int(2 + pulse * 2)

        left = render_pixel_text(self.font_small, left_text, clock_color, scale=clock_scale)
        center = render_pixel_text(self.font_small, center_text, C.DESK_ACCENT_LIGHT, scale=2)
        right = render_pixel_text(self.font_small, right_text, C.DESK_TEXT, scale=2)

        self.screen.blit(left, (bar_rect.x + 10, bar_rect.y + (bar_rect.height - left.get_height()) // 2))
        self.screen.blit(center, (bar_rect.centerx - center.get_width() // 2, bar_rect.y + (bar_rect.height - center.get_height()) // 2))
        self.screen.blit(right, (bar_rect.right - right.get_width() - 10, bar_rect.y + (bar_rect.height - right.get_height()) // 2))

        # Hourly celebration animation (or dev-triggered)
        now = datetime.datetime.now()
        current_minute = now.minute
        triggered = self.desktop_hour_fx_triggered
        if (current_minute == 0 and self._last_clock_minute == 59) or triggered:
            if triggered:
                self.desktop_hour_fx_triggered = False
            burst_x = bar_rect.x + 10 + left.get_width() + 14
            burst_y = bar_rect.centery
            self.desktop_hour_fx_frame = 90
            self.desktop_hour_fx_x = burst_x
            self.desktop_hour_fx_y = burst_y
            # Ring-pattern particles
            for i in range(60):
                angle = i * math.pi * 2 / 60
                speed = random.uniform(2.0, 5.0)
                self.desktop_particles.append(Particle(
                    burst_x, burst_y,
                    C.GOLD if i % 3 == 0 else C.DESK_ACCENT_LIGHT,
                    math.cos(angle) * speed, math.sin(angle) * speed,
                    random.randint(30, 55),
                ))
            # Golden "star" sparkles — larger, longer life
            for _ in range(12):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(3.5, 7.0)
                self.desktop_particles.append(Particle(
                    burst_x + random.randint(-4, 4), burst_y + random.randint(-4, 4),
                    C.GOLD_LIGHT,
                    math.cos(angle) * speed, math.sin(angle) * speed,
                    random.randint(50, 70),
                ))
        self._last_clock_minute = current_minute

    def _draw_desktop_icon_button(self, button, hovered=False, pressed=False):
        rect = button["rect"].copy()
        label = button["label"]
        enabled = button["enabled"]

        if hovered:
            rect = rect.inflate(8, 8)

        if pressed:
            rect.y += 5

        # 闃村奖
        if hovered:
            pygame.draw.rect(self.screen, C.OUTLINE, rect.move(5, 5))

        # 澶栨
        pygame.draw.rect(self.screen, C.OUTLINE, rect)

        if enabled:
            fill = C.DESK_ICON_HOVER if hovered else C.DESK_ICON
        else:
            fill = C.DESK_ICON_SOON if not hovered else C.DESK_PANEL

        pygame.draw.rect(self.screen, fill, rect.inflate(-5, -5))

        # 楂樹寒鎻忚竟
        border_col = C.DESK_ACCENT_LIGHT if hovered else C.DESK_ACCENT
        pygame.draw.rect(self.screen, border_col, rect.inflate(-12, -12), 2)

        # 鍥炬爣鍐呴儴鍥炬鍖哄煙
        icon_box = pygame.Rect(
            rect.x + 24,
            rect.y + 18,
            rect.width - 48,
            rect.height - 52
        )

        pygame.draw.rect(self.screen, C.OUTLINE, icon_box, 2)

        if enabled:
            pygame.draw.rect(self.screen, C.DESK_ACCENT, icon_box.inflate(-4, -4))
        else:
            pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, icon_box.inflate(-4, -4))

        # GOMOKU 鍥炬爣鍐呭
        if button["action"] == "open_gomoku":
            board_icon = icon_box.inflate(-12, -12)
            pygame.draw.rect(self.screen, C.BOARD, board_icon)
            pygame.draw.rect(self.screen, C.OUTLINE, board_icon, 2)

            for i in range(1, 4):
                x = board_icon.x + i * board_icon.width // 4
                y = board_icon.y + i * board_icon.height // 4
                pygame.draw.line(self.screen, C.GRID, (x, board_icon.y + 4), (x, board_icon.bottom - 4), 1)
                pygame.draw.line(self.screen, C.GRID, (board_icon.x + 4, y), (board_icon.right - 4, y), 1)

            pygame.draw.rect(self.screen, C.BLACK_STONE, (board_icon.centerx - 12, board_icon.centery - 8, 10, 10))
            pygame.draw.rect(self.screen, C.WHITE_STONE, (board_icon.centerx + 4, board_icon.centery + 2, 10, 10))
            pygame.draw.rect(self.screen, C.OUTLINE, (board_icon.centerx + 4, board_icon.centery + 2, 10, 10), 1)

        elif button["action"] == "open_snake":
            snake_icon = icon_box.inflate(-12, -12)
            pygame.draw.rect(self.screen, C.SNAKE_PANEL_DARK, snake_icon)
            pygame.draw.rect(self.screen, C.OUTLINE, snake_icon, 2)

            cells = [
                (1, 2), (2, 2), (3, 2), (3, 1), (4, 1)
            ]

            cell = snake_icon.width // 6

            for idx, (cx, cy) in enumerate(cells):
                px = snake_icon.x + cx * cell
                py = snake_icon.y + cy * cell

                col = C.SNAKE_HEAD if idx == len(cells) - 1 else C.SNAKE_BODY
                pygame.draw.rect(self.screen, C.OUTLINE, (px, py, cell, cell))
                pygame.draw.rect(self.screen, col, (px + 2, py + 2, cell - 4, cell - 4))

            food_x = snake_icon.x + 1 * cell
            food_y = snake_icon.y + 4 * cell
            pygame.draw.rect(self.screen, C.OUTLINE, (food_x, food_y, cell, cell))
            pygame.draw.rect(self.screen, C.SNAKE_FOOD, (food_x + 3, food_y + 3, cell - 6, cell - 6))

        elif button["action"] == "open_breakout":
            br_icon = icon_box.inflate(-12, -12)
            pygame.draw.rect(self.screen, C.BG_DEEP_BLUE, br_icon)
            pygame.draw.rect(self.screen, C.OUTLINE, br_icon, 2)

            brick_w = br_icon.width // 5
            brick_h = 10
            for r in range(3):
                for n in range(5):
                    bx = br_icon.x + n * brick_w
                    by = br_icon.y + 4 + r * (brick_h + 3)
                    pygame.draw.rect(self.screen, C.OUTLINE, (bx, by, brick_w, brick_h))
                    pygame.draw.rect(self.screen, C.BRICK_PURPLE, (bx + 1, by + 1, brick_w - 2, brick_h - 2))

            pad_x = br_icon.x + br_icon.width // 4
            pad_y = br_icon.bottom - 16
            pygame.draw.rect(self.screen, C.BRICK_ORANGE, (pad_x, pad_y, br_icon.width // 2, 8))

            ball_x = br_icon.centerx
            ball_y = br_icon.centery + 6
            pygame.draw.circle(self.screen, C.YELLOW, (int(ball_x), int(ball_y)), 5)
            pygame.draw.circle(self.screen, C.OUTLINE, (int(ball_x), int(ball_y)), 5, 1)

        elif button["action"] == "open_2048":
            game_icon = icon_box.inflate(-12, -12)
            pygame.draw.rect(self.screen, C.G2048_PANEL_DARK, game_icon)
            pygame.draw.rect(self.screen, C.OUTLINE, game_icon, 2)
            mini_gap = 4
            mini_cell = (game_icon.width - mini_gap * 5) // 4
            nums = [[2, 0, 4, 0], [0, 8, 0, 16], [32, 0, 64, 0], [0, 128, 0, 0]]
            for rr in range(4):
                for cc in range(4):
                    x = game_icon.x + mini_gap + cc * (mini_cell + mini_gap)
                    y = game_icon.y + mini_gap + rr * (mini_cell + mini_gap)
                    val = nums[rr][cc]
                    col = C.G2048_CELL_EMPTY if val == 0 else self._get_2048_tile_color(val)
                    pygame.draw.rect(self.screen, C.OUTLINE, (x, y, mini_cell, mini_cell))
                    pygame.draw.rect(self.screen, col, (x + 1, y + 1, mini_cell - 2, mini_cell - 2))

        elif button["action"] == "open_mines":
            mine_icon = icon_box.inflate(-12, -12)
            pygame.draw.rect(self.screen, C.MINES_PANEL_DARK, mine_icon)
            pygame.draw.rect(self.screen, C.OUTLINE, mine_icon, 2)
            gg = 3; mc = (mine_icon.width - gg * 6) // 5
            for rr in range(5):
                for cc in range(5):
                    x = mine_icon.x + gg + cc * (mc + gg)
                    y = mine_icon.y + gg + rr * (mc + gg)
                    col = C.MINES_CELL_CLOSED
                    if (rr, cc) in [(1, 1), (2, 3), (3, 2)]: col = C.MINES_CELL_OPEN
                    pygame.draw.rect(self.screen, C.OUTLINE, (x, y, mc, mc))
                    pygame.draw.rect(self.screen, col, (x + 1, y + 1, mc - 2, mc - 2))
            fx = mine_icon.x + gg + 3 * (mc + gg); fy = mine_icon.y + gg + 1 * (mc + gg)
            pygame.draw.rect(self.screen, C.OUTLINE, (fx + 4, fy + 3, 3, mc - 5))
            pygame.draw.polygon(self.screen, C.MINES_FLAG, [(fx + 7, fy + 3), (fx + mc - 4, fy + 7), (fx + 7, fy + 11)])

        elif button["action"] == "open_tetris":
            block_icon = icon_box.inflate(-16, -16)
            pygame.draw.rect(self.screen, C.TETRIS_BOARD, block_icon)
            pygame.draw.rect(self.screen, C.OUTLINE, block_icon, 2)
            cell = max(6, (block_icon.width - 10) // 7)
            ox = block_icon.centerx - cell * 3
            oy = block_icon.centery - cell * 2 + 3
            pieces = [
                (0, 3, C.TETRIS_J), (1, 3, C.TETRIS_J), (2, 3, C.TETRIS_J),
                (2, 2, C.TETRIS_J), (3, 3, C.TETRIS_O), (4, 3, C.TETRIS_O),
                (3, 2, C.TETRIS_O), (4, 2, C.TETRIS_O), (4, 1, C.TETRIS_T),
                (5, 1, C.TETRIS_T), (6, 1, C.TETRIS_T), (5, 0, C.TETRIS_T),
            ]
            for px, py, color in pieces:
                block_rect = pygame.Rect(ox + px * cell, oy + py * cell, cell - 1, cell - 1)
                pygame.draw.rect(self.screen, C.OUTLINE, block_rect)
                pygame.draw.rect(self.screen, color, block_rect.inflate(-2, -2))

        elif button["action"] == "open_air":
            field = icon_box.inflate(-14, -14)
            pygame.draw.rect(self.screen, (5, 18, 34), field)
            pygame.draw.rect(self.screen, (65, 175, 230), field, 2)
            cx, cy = field.center
            pygame.draw.polygon(self.screen, (150, 235, 255),
                                [(cx, cy - 29), (cx - 24, cy + 25),
                                 (cx, cy + 14), (cx + 24, cy + 25)])
            pygame.draw.line(self.screen, (255, 205, 90), (cx - 8, cy - 35), (cx - 8, cy - 48), 3)
            pygame.draw.line(self.screen, (255, 205, 90), (cx + 8, cy - 35), (cx + 8, cy - 48), 3)

        elif button["action"] == "open_system_settings":
            gear = icon_box.inflate(-20, -20)
            pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, gear)
            pygame.draw.rect(self.screen, C.OUTLINE, gear, 2)
            pygame.draw.circle(self.screen, C.DESK_ACCENT_LIGHT, gear.center, 22, 7)
            pygame.draw.circle(self.screen, C.OUTLINE, gear.center, 7)
            for angle in range(0, 360, 45):
                dx = int(math.cos(math.radians(angle)) * 29)
                dy = int(math.sin(math.radians(angle)) * 29)
                pygame.draw.rect(self.screen, C.DESK_ACCENT, (gear.centerx + dx - 5, gear.centery + dy - 5, 10, 10))

        elif button["action"] == "open_profile":
            card = icon_box.inflate(-18, -18)
            pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, card)
            pygame.draw.rect(self.screen, C.OUTLINE, card, 2)
            pygame.draw.circle(self.screen, C.GOLD_LIGHT, (card.centerx, card.y + 24), 12)
            pygame.draw.rect(self.screen, C.DESK_ACCENT_LIGHT, (card.centerx - 22, card.y + 42, 44, 23))
            for row in range(3):
                pygame.draw.rect(self.screen, C.GOLD, (card.x + 12, card.y + 72 + row * 7, card.width - 24, 3))

        elif button["action"] == "open_achievement_wall":
            wall_icon = icon_box.inflate(-12, -12)
            pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, wall_icon)
            pygame.draw.rect(self.screen, C.OUTLINE, wall_icon, 2)
            cols = 8
            rows = 6
            margin = 6
            dot_gap = 2
            dot_w = (wall_icon.width - margin * 2 - dot_gap * (cols - 1)) // cols
            dot_h = (wall_icon.height - margin * 2 - dot_gap * (rows - 1)) // rows
            for r in range(rows):
                for c in range(cols):
                    dx = wall_icon.x + margin + c * (dot_w + dot_gap)
                    dy = wall_icon.y + margin + r * (dot_h + dot_gap)
                    unlocked = (r * cols + c) < 7
                    col = C.GOLD_LIGHT if unlocked else C.DESK_MUTED
                    if (r, c) == (2, 3):
                        col = C.DESK_ACCENT_LIGHT
                    pygame.draw.rect(self.screen, C.OUTLINE, (dx, dy, dot_w, dot_h))
                    pygame.draw.rect(self.screen, col, (dx + 1, dy + 1, dot_w - 2, dot_h - 2))

        elif button["action"] == "open_lore":
            # Pixel-art book icon
            book_icon = icon_box.inflate(-16, -16)
            bx, by = book_icon.x, book_icon.y
            bw, bh = book_icon.width, book_icon.height
            # Book cover
            pygame.draw.rect(self.screen, C.OUTLINE, book_icon)
            pygame.draw.rect(self.screen, C.LORE_PANEL_DARK, book_icon.inflate(-2, -2))
            # Spine
            spine_w = 6
            pygame.draw.rect(self.screen, C.LORE_ACCENT,
                             (bx + 6, by + 4, spine_w, bh - 8))
            # Pages (left and right)
            left_page = pygame.Rect(bx + 6 + spine_w + 4, by + 8,
                                    (bw - spine_w - 20) // 2, bh - 16)
            right_page = pygame.Rect(left_page.right + 4, by + 8,
                                     (bw - spine_w - 20) // 2, bh - 16)
            pygame.draw.rect(self.screen, C.LORE_PANEL, left_page)
            pygame.draw.rect(self.screen, C.LORE_PANEL, right_page)
            pygame.draw.rect(self.screen, C.LORE_MUTED, left_page, 1)
            pygame.draw.rect(self.screen, C.LORE_MUTED, right_page, 1)
            # Text lines on pages
            for li in range(3):
                ly = left_page.y + 6 + li * 8
                pygame.draw.rect(self.screen, C.LORE_MUTED,
                                 (left_page.x + 4, ly, left_page.width - 8, 2))
            for li in range(3):
                ly = right_page.y + 6 + li * 8
                pygame.draw.rect(self.screen, C.LORE_MUTED,
                                 (right_page.x + 4, ly, right_page.width - 8, 2))
            # Bookmark ribbon
            pygame.draw.rect(self.screen, C.LORE_TITLE,
                             (bx + bw - 18, by, 4, 18))

        else:
            # COMING SOON 鍥炬爣锛氬儚绱犻攣 / 鍗犱綅鍥炬
            lock_w = 34
            lock_h = 26
            lx = icon_box.centerx - lock_w // 2
            ly = icon_box.centery - lock_h // 2 + 6

            pygame.draw.rect(self.screen, C.OUTLINE, (lx, ly, lock_w, lock_h))
            pygame.draw.rect(self.screen, C.DESK_MUTED, (lx + 4, ly + 4, lock_w - 8, lock_h - 8))

            # 閿佹
            pygame.draw.rect(self.screen, C.OUTLINE, (icon_box.centerx - 14, ly - 16, 28, 18), 2)

        # 鏂囨湰鏍囩
        if label == "COMING SOON":
            text = "SOON"
        else:
            text = label

        txt_scale = 2 if len(text) <= 8 else 1
        text_col = C.DESK_TEXT if enabled else C.DESK_MUTED

        # Check for per-icon subtitle from registry
        icon_sub_en = button.get("subtitle_en")
        icon_sub_zh = button.get("subtitle_zh")
        has_icon_sub = bool(icon_sub_en or icon_sub_zh)
        if has_icon_sub:
            txt_scale = 1

        txt = render_pixel_text(self.font_small, text, text_col, scale=txt_scale)
        tx = rect.centerx - txt.get_width() // 2
        ty = rect.bottom - txt.get_height() - (24 if has_icon_sub else 8)

        self.screen.blit(txt, (tx, ty))
        if has_icon_sub:
            sub_text = icon_sub_zh if is_chinese() else icon_sub_en
            subtitle = render_pixel_text(
                self.font_small, sub_text, text_col, scale=1
            )
            self.screen.blit(
                subtitle,
                (rect.centerx - subtitle.get_width() // 2, rect.bottom - subtitle.get_height() - 7),
            )

    def _draw_desktop_page_button(self, button, hovered=False, pressed=False):
        rect = button["rect"].copy()
        enabled = button.get("enabled", True)
        if not enabled: hovered = False; pressed = False
        if hovered: rect = rect.inflate(6, 6)
        if pressed: rect.y += 4
        if hovered: pygame.draw.rect(self.screen, C.OUTLINE, rect.move(4, 4))
        pygame.draw.rect(self.screen, C.OUTLINE, rect); pygame.draw.rect(self.screen, C.DESK_PANEL, rect.inflate(-4, -4))
        pygame.draw.rect(self.screen, C.DESK_ACCENT, rect.inflate(-10, -10), 2)
        cx, cy = rect.center
        if button["action"] == "desktop_next_page": pts = [(cx - 6, cy - 10), (cx + 8, cy), (cx - 6, cy + 10)]
        else: pts = [(cx + 6, cy - 10), (cx - 8, cy), (cx + 6, cy + 10)]
        tc = C.DESK_ACCENT_LIGHT if enabled else C.DESK_MUTED
        pygame.draw.polygon(self.screen, tc, pts); pygame.draw.polygon(self.screen, C.OUTLINE, pts, 2)

    def _draw_desktop_page_icons(self, page_index, offset_x=0, slide_t=1.0, is_incoming=False):
        mouse_pos = self._logical_mouse_pos()

        buttons = self._get_desktop_icon_buttons_for_page(page_index, offset_x=offset_x)

        for b in buttons:
            idx = b.get("icon_index", 0)

            stagger = idx * 0.035

            if is_incoming:
                local_t = max(0.0, min(1.0, (slide_t - stagger) / 0.82))
            else:
                local_t = max(0.0, min(1.0, slide_t))

            lift = int(math.sin(local_t * math.pi) * 10)

            b = b.copy()
            b["rect"] = b["rect"].move(0, -lift)

            hovered = (
                not self.desktop_slide_active
                and b["rect"].collidepoint(mouse_pos)
                and b.get("enabled", True)
            )

            pressed = (
                not self.desktop_slide_active
                and self.desktop_pressed_action == b["action"]
            )

            if hovered and self.anim_tick % 6 == 0:
                icon_rect = b["rect"]
                self.desktop_particles.append(Particle(
                    icon_rect.x + random.randint(0, icon_rect.width),
                    icon_rect.y + random.randint(0, icon_rect.height),
                    C.GOLD_LIGHT,
                    random.uniform(-1.0, 1.0), random.uniform(-2.5, -0.5),
                    random.randint(8, 15),
                ))

            self._draw_desktop_icon_button(b, hovered=hovered, pressed=pressed)

    def _draw_desktop_page_dots(self):
        pc = len(self.desktop_pages)
        if pc <= 1: return
        dy = DESKTOP_SCREEN_RECT.bottom - 46; dg = 18; ds = 8
        tw = pc * ds + (pc - 1) * dg; sx2 = DESKTOP_SCREEN_RECT.centerx - tw // 2
        if self.desktop_slide_active:
            t = self.desktop_slide_frame / max(1, self.desktop_slide_max_frames)
            t = self._ease_in_out_cubic(t)
            af = self.desktop_slide_from_page + (self.desktop_slide_to_page - self.desktop_slide_from_page) * t
        else: af = float(self.desktop_page)
        for i in range(pc):
            x = sx2 + i * (ds + dg); dist = abs(af - i); active = max(0.0, 1.0 - dist)
            w = int(ds + active * 14); h = ds
            col = C.DESK_ACCENT_LIGHT if active > 0.5 else C.DESK_MUTED
            dr = pygame.Rect(x - int(active * 7), dy, w, h)
            pygame.draw.rect(self.screen, C.OUTLINE, dr.inflate(4, 4)); pygame.draw.rect(self.screen, col, dr)

    def _draw_desktop_volume_control(self):
        tab = self._get_desktop_volume_tab_rect()
        panel = self._get_desktop_volume_panel_rect()
        slider = self._get_desktop_volume_slider_rect()
        mouse_pos = self._logical_mouse_pos()
        visible = (
            self.desktop_volume_open
            or self.desktop_volume_dragging
            or tab.collidepoint(mouse_pos)
            or panel.collidepoint(mouse_pos)
        )

        if visible:
            pygame.draw.rect(self.screen, C.OUTLINE, panel)
            pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, panel.inflate(-4, -4))
            pygame.draw.rect(self.screen, C.DESK_ACCENT, panel.inflate(-10, -10), 2)

            label = render_pixel_text(self.font_small, "BGM", C.DESK_TEXT, scale=1)
            self.screen.blit(label, (panel.x + 16, panel.centery - label.get_height() // 2))

            pygame.draw.rect(self.screen, C.OUTLINE, slider.inflate(4, 4))
            pygame.draw.rect(self.screen, C.DESK_MUTED, slider)
            fill_w = int(slider.width * self.audio.music_volume)
            if fill_w > 0:
                pygame.draw.rect(
                    self.screen,
                    C.DESK_ACCENT_LIGHT,
                    (slider.x, slider.y, fill_w, slider.height),
                )
            knob_x = slider.x + fill_w
            pygame.draw.rect(self.screen, C.OUTLINE, (knob_x - 5, slider.centery - 10, 10, 20))
            pygame.draw.rect(self.screen, C.GOLD, (knob_x - 2, slider.centery - 7, 4, 14))

        pygame.draw.rect(self.screen, C.OUTLINE, tab)
        pygame.draw.rect(
            self.screen,
            C.DESK_ICON_HOVER if visible else C.DESK_PANEL_DARK,
            tab.inflate(-4, -4),
        )
        cx, cy = tab.center
        pygame.draw.rect(self.screen, C.DESK_ACCENT_LIGHT, (cx - 9, cy - 4, 5, 8))
        pygame.draw.polygon(
            self.screen,
            C.DESK_ACCENT_LIGHT,
            [(cx - 4, cy - 4), (cx + 2, cy - 9), (cx + 2, cy + 9), (cx - 4, cy + 4)],
        )
        if self.audio.music_volume > 0.02:
            pygame.draw.arc(self.screen, C.DESK_ACCENT_LIGHT, (cx - 2, cy - 8, 15, 16), -0.8, 0.8, 2)

    def _draw_desktop(self):
        self._draw_stage_background()
        self._draw_handheld_shell()
        self._draw_desktop_wallpaper()
        self._draw_desktop_status_bar()
        screen_rect = DESKTOP_SCREEN_RECT; old_clip = self.screen.get_clip()
        self.screen.set_clip(screen_rect)
        if self.desktop_slide_active:
            rt = self.desktop_slide_frame / max(1, self.desktop_slide_max_frames)
            t = self._ease_in_out_cubic(rt)
            travel = screen_rect.width + 80; direction = self.desktop_slide_direction
            fo = int(-direction * travel * t); to = int(direction * travel * (1 - t))
            self._draw_desktop_page_icons(self.desktop_slide_from_page, offset_x=fo, slide_t=t, is_incoming=False)
            self._draw_desktop_page_icons(self.desktop_slide_to_page, offset_x=to, slide_t=t, is_incoming=True)
            la = int(90 * math.sin(rt * math.pi))
            if la > 0:
                sp = pygame.Surface((screen_rect.width, screen_rect.height), pygame.SRCALPHA)
                for i in range(10):
                    y = screen_rect.y + 90 + i * 42; x1 = screen_rect.x + 60 + i * 13; x2 = x1 + 120
                    pygame.draw.line(sp, (*C.DESK_ACCENT_LIGHT, la), (x1, y), (x2, y), 2)
                self.screen.blit(sp, (0, 0))
        else:
            self._draw_desktop_page_icons(self.desktop_page)
        self.screen.set_clip(old_clip)
        mp = self._logical_mouse_pos()
        # Mouse trail particles
        dx = mp[0] - self._last_mouse_pos[0]
        dy = mp[1] - self._last_mouse_pos[1]
        if abs(dx) > 3 or abs(dy) > 3:
            if self.anim_tick % 2 == 0:
                for _ in range(2):
                    self.desktop_particles.append(Particle(
                        mp[0] + random.randint(-4, 4), mp[1] + random.randint(-4, 4),
                        C.DESK_ACCENT_LIGHT,
                        random.uniform(-0.4, 0.4), random.uniform(-0.8, -0.1),
                        random.randint(12, 20),
                    ))
            self._last_mouse_pos = mp
        for b in self._get_desktop_page_buttons():
            h = (not self.desktop_slide_active and b["rect"].collidepoint(mp) and b.get("enabled", True))
            p = (not self.desktop_slide_active and self.desktop_pressed_action == b["action"])
            self._draw_desktop_page_button(b, hovered=h, pressed=p)
        self._draw_desktop_page_dots()
        self._draw_desktop_volume_control()
        hint = render_pixel_text(self.font_small, 'ESC to Quit', C.DESK_MUTED, scale=1 if is_chinese() else 2)
        hint_y = DESKTOP_SCREEN_RECT.bottom - hint.get_height() - 14
        self.screen.blit(hint, (DESKTOP_SCREEN_RECT.centerx - hint.get_width() // 2, hint_y))
        # Draw expanding rings for hour celebration
        if self.desktop_hour_fx_frame > 0:
            # Three expanding rings
            for ring_idx in range(3):
                ring_delay = ring_idx * 8
                ring_frame = self.desktop_hour_fx_frame - ring_delay
                if ring_frame <= 0:
                    continue
                radius = int((90 - ring_frame) * 3.5)
                alpha = int(180 * ring_frame / 90.0)
                ring_surf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (*C.GOLD, alpha), (radius + 2, radius + 2), radius, 2)
                if ring_idx == 0:
                    pygame.draw.circle(ring_surf, (*C.GOLD_LIGHT, alpha // 2), (radius + 2, radius + 2), radius - 4, 1)
                self.screen.blit(ring_surf, (self.desktop_hour_fx_x - radius - 2, self.desktop_hour_fx_y - radius - 2))
            self.desktop_hour_fx_frame -= 1

        # Update and draw desktop particles
        for p in self.desktop_particles[:]:
            if not p.update():
                self.desktop_particles.remove(p)
            else:
                p.draw(self.screen)
        if self.shutdown_confirm_open:
            self._draw_shutdown_confirm()

    def _get_shutdown_confirm_buttons(self):
        panel = pygame.Rect(WINDOW_W // 2 - 300, WINDOW_H // 2 - 145, 600, 290)
        return [
            {"rect": pygame.Rect(panel.x + 58, panel.bottom - 92, 220, 52), "label": "MISCLICKED~", "action": "cancel"},
            {"rect": pygame.Rect(panel.right - 278, panel.bottom - 92, 220, 52), "label": "SHUT DOWN", "action": "shutdown"},
        ]

    def _draw_shutdown_confirm(self):
        shade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 170))
        self.screen.blit(shade, (0, 0))
        panel = pygame.Rect(WINDOW_W // 2 - 300, WINDOW_H // 2 - 145, 600, 290)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, C.DESK_PANEL, panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.DESK_ACCENT, panel.inflate(-24, -24), 2)
        title = render_pixel_text(self.font_menu_title, "POWER OFF?", C.DESK_ACCENT_LIGHT, scale=3)
        message = render_pixel_text(self.font_small, "UNSAVED PROGRESS MAY BE LOST", C.DESK_TEXT, scale=2)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 48))
        self.screen.blit(message, (panel.centerx - message.get_width() // 2, panel.y + 116))
        mouse_pos = self._logical_mouse_pos()
        for button in self._get_shutdown_confirm_buttons():
            rect = button["rect"].copy()
            hovered = rect.collidepoint(mouse_pos)
            pressed = self.shutdown_confirm_pressed == button["action"]
            if hovered:
                rect = rect.inflate(8, 8)
            if pressed:
                rect.y += 4
            if hovered:
                pygame.draw.rect(self.screen, C.OUTLINE, rect.move(4, 4))
            pygame.draw.rect(self.screen, C.OUTLINE, rect)
            pygame.draw.rect(self.screen, C.DESK_ICON_HOVER if hovered else C.DESK_ICON, rect.inflate(-5, -5))
            pygame.draw.rect(self.screen, C.DESK_ACCENT_LIGHT, rect.inflate(-11, -11), 2)
            label = render_pixel_text(self.font_btn, button["label"], C.DESK_TEXT, scale=2)
            self.screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))



