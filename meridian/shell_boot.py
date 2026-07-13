from .common import *
from .localization import is_chinese, set_language


class BootMixin:
    def _init_boot(self):
        self.boot_frame = 0
        self.boot_visible_chars = 0
        self.boot_next_char_delay = BOOT_TYPE_BASE_DELAY
        self.boot_phase = "fade"
        self.boot_fade_alpha = 0
        self.boot_progress_frame = 0
        self.boot_progress_value = 0.0
        self.system_ready_pressed = False
        self.shutdown_frame = 0
        self.shutdown_visible_chars = len(SHUTDOWN_TEXT)
        self.shutdown_phase = "show"
        self.shutdown_delete_timer = 0
        self.shutdown_fade_alpha = 0

    def _localized_boot_text(self):
        if is_chinese():
            return "MERIDIAN — \u6b63\u5728\u5efa\u7acb\u8fde\u63a5..."
        return BOOT_TEXT_MERIDIAN

    def _localized_shutdown_text(self):
        if is_chinese():
            return "\u6b63\u5728\u5173\u95ed\u8fde\u63a5\u2026\u2026\u8bf8\u754c\u91cd\u5f52\u6c89\u7720\u3002"
        return SHUTDOWN_TEXT_MERIDIAN

    def _get_boot_type_delay(self, next_char_index):
        """
        寮€鏈烘墦瀛楄嚜鐒跺仠椤裤€?        杩欐鏁翠綋鏀炬參涓€鐐癸紝璁╄緭鍏ユ洿浠庡銆?        """
        boot_text = self._localized_boot_text()
        if next_char_index <= 0 or next_char_index > len(boot_text):
            return BOOT_TYPE_BASE_DELAY
        ch = boot_text[next_char_index - 1]
        typed = boot_text[:next_char_index]

        if ch == " ":
            return random.randint(10, 16)

        if ch == "'":
            return random.randint(8, 12)

        if typed in ["WELCOME ", "WELCOME TO ", "WELCOME TO HAO'S "]:
            return random.randint(22, 34)

        return random.randint(5, 9)

    def _update_boot(self):
        self.boot_frame += 1

        if self.boot_phase == "fade":
            self.boot_fade_alpha += 255 / BOOT_FADE_IN_FRAMES

            if self.boot_fade_alpha >= 255:
                self.boot_fade_alpha = 255
                self.boot_phase = "typing"
                self.boot_frame = 0
                self.boot_next_char_delay = BOOT_TYPE_BASE_DELAY

        elif self.boot_phase == "typing":
            self.boot_next_char_delay -= 1

            if self.boot_next_char_delay <= 0:
                if self.boot_visible_chars < len(self._localized_boot_text()):
                    self.boot_visible_chars += 1
                    self.boot_next_char_delay = self._get_boot_type_delay(self.boot_visible_chars)
                else:
                    self.boot_phase = "enter"
                    self.boot_frame = 0

        elif self.boot_phase == "enter":
            if self.boot_frame >= BOOT_ENTER_PAUSE_FRAMES:
                self.boot_phase = "loading"
                self.boot_frame = 0
                self.boot_progress_frame = 0
                self.boot_progress_value = 0.0

        elif self.boot_phase == "loading":
            self.boot_progress_frame += 1
            f = self.boot_progress_frame
            total = BOOT_PROGRESS_TOTAL_FRAMES

            if f <= 90:
                p = f / 90
                self.boot_progress_value = 0.12 * p

            elif f <= 150:
                self.boot_progress_value = 0.12

            elif f <= 300:
                p = (f - 150) / 150
                self.boot_progress_value = 0.12 + (0.41 - 0.12) * p

            elif f <= 345:
                self.boot_progress_value = 0.41

            elif f <= 480:
                p = (f - 345) / 135
                self.boot_progress_value = 0.41 + (0.73 - 0.41) * p

            elif f <= 525:
                self.boot_progress_value = 0.73

            elif f <= total:
                p = (f - 525) / (total - 525)
                self.boot_progress_value = 0.73 + (1.00 - 0.73) * p

            else:
                self.boot_progress_value = 1.0

            if self.boot_progress_frame >= total:
                self.boot_progress_value = 1.0
                self.boot_phase = "done"
                self.state = self.SYSTEM_READY

    def _get_system_ready_button(self):
        return pygame.Rect(WINDOW_W // 2 - 150, WINDOW_H // 2 + 160, 300, 60)

    def _get_system_ready_language_buttons(self):
        return [
            {
                "rect": pygame.Rect(WINDOW_W // 2 - 235, WINDOW_H // 2 + 88, 220, 48),
                "label": "ENGLISH", "language": "en",
            },
            {
                "rect": pygame.Rect(WINDOW_W // 2 + 15, WINDOW_H // 2 + 88, 220, 48),
                "label": "\u7b80\u4f53\u4e2d\u6587", "language": "zh_hans",
            },
        ]

    def _handle_system_ready_event(self, event):
        button = self._get_system_ready_button()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                self.language = "zh_hans" if self.language == "en" else "en"
                set_language(self.language)
                self._save_now()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.system_ready_pressed = False
                self._start_transition(self.PASSWORD, "system_unlock", frames=44)
            elif event.key == pygame.K_ESCAPE:
                self._start_shutdown()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for language_button in self._get_system_ready_language_buttons():
                if language_button["rect"].collidepoint(event.pos):
                    self.language = language_button["language"]
                    set_language(self.language)
                    self._save_now()
                    return
            if button.collidepoint(event.pos):
                self.system_ready_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if button.collidepoint(event.pos) and self.system_ready_pressed:
                self.system_ready_pressed = False
                self._start_transition(self.PASSWORD, "system_unlock", frames=44)
            else:
                self.system_ready_pressed = False

    def _start_shutdown(self):
        if hasattr(self, "save_manager"):
            self._save_now()
        self.audio.begin_shutdown()
        self.state = self.SHUTDOWN

        self.shutdown_frame = 0
        self.shutdown_visible_chars = len(self._localized_shutdown_text())
        self.shutdown_phase = "show"
        self.shutdown_delete_timer = 0
        self.shutdown_fade_alpha = 0

        self.desktop_pressed_action = None
        self.pressed_button_action = None
        self.shutdown_confirm_open = False
        self.shutdown_confirm_pressed = None

    def _update_shutdown(self):
        self.shutdown_frame += 1

        if self.shutdown_phase == "show":
            if self.shutdown_frame >= 45:
                self.shutdown_phase = "deleting"
                self.shutdown_frame = 0
                self.shutdown_delete_timer = 0

        elif self.shutdown_phase == "deleting":
            self.shutdown_delete_timer += 1

            if self.shutdown_delete_timer >= SHUTDOWN_DELETE_DELAY:
                self.shutdown_delete_timer = 0

                if self.shutdown_visible_chars > 0:
                    self.shutdown_visible_chars -= 1
                else:
                    self.shutdown_phase = "fade"
                    self.shutdown_frame = 0

        elif self.shutdown_phase == "fade":
            t = min(1.0, self.shutdown_frame / SHUTDOWN_FADE_FRAMES)
            self.shutdown_fade_alpha = int(255 * t)

            if self.shutdown_frame >= SHUTDOWN_FADE_FRAMES:
                self.running = False

    def _draw_boot_screen(self):
        self.screen.fill(C.DESK_PANEL_DARK)

        outer = pygame.Rect(70, 70, WINDOW_W - 140, WINDOW_H - 140)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5)
        pygame.draw.rect(self.screen, C.DESK_ACCENT, outer.inflate(-10, -10), 2)

        screen_rect = outer.inflate(-36, -36)
        pygame.draw.rect(self.screen, C.DESK_BG_TOP, screen_rect)

        for i in range(28):
            x = screen_rect.x + (i * 97 + 31) % screen_rect.width
            y = screen_rect.y + (i * 53 + 47) % screen_rect.height
            pulse = 0.5 + 0.5 * abs(math.sin(self.anim_tick * 0.03 + i))
            col = (
                int(C.DESK_ACCENT[0] * pulse),
                int(C.DESK_ACCENT[1] * pulse),
                int(C.DESK_ACCENT[2] * pulse),
            )
            pygame.draw.rect(self.screen, col, (x, y, 3, 3))

        draw_restrained_meteors(self.screen, screen_rect, self.anim_tick, max_meteors=2, alpha_scale=0.9)

        shown = self._localized_boot_text()[:self.boot_visible_chars]
        text = render_pixel_text(self.font_status, shown, C.DESK_TEXT, scale=3)

        cursor_visible = (self.anim_tick // 18) % 2 == 0
        show_cursor = self.boot_phase in ["typing", "enter"]

        cursor_w = 10
        cursor_h = max(26, text.get_height())

        total_w = text.get_width() + (cursor_w + 8 if cursor_visible and show_cursor else 0)
        x = screen_rect.centerx - total_w // 2
        y = screen_rect.centery - text.get_height() // 2 - 48

        self.screen.blit(text, (x, y))

        if cursor_visible and show_cursor:
            cx = x + text.get_width() + 8
            cy = y + 2
            pygame.draw.rect(self.screen, C.DESK_ACCENT_LIGHT, (cx, cy, cursor_w, cursor_h))

        if self.boot_phase == "enter":
            tip = render_pixel_text(self.font_small, "PRESSING ENTER...", C.DESK_ACCENT_LIGHT, scale=2)
            self.screen.blit(
                tip,
                (
                    screen_rect.centerx - tip.get_width() // 2,
                    y + text.get_height() + 26
                )
            )

        if self.boot_phase in ["loading", "done"]:
            # Rotate status messages during progress phases
            if self.boot_progress_frame <= 90:
                status_index = 0
            elif self.boot_progress_frame <= 300:
                status_index = 1
            elif self.boot_progress_frame <= 480:
                status_index = 2
            else:
                status_index = 3
            status_text = BOOT_STATUS_MESSAGES[min(status_index, len(BOOT_STATUS_MESSAGES) - 1)]
            label = render_pixel_text(self.font_small, status_text, C.DESK_ACCENT_LIGHT, scale=2)
            label_x = screen_rect.centerx - label.get_width() // 2
            label_y = y + text.get_height() + 24
            self.screen.blit(label, (label_x, label_y))

            bar_w = 520
            bar_h = 22
            bar_x = screen_rect.centerx - bar_w // 2
            bar_y = label_y + 38

            pygame.draw.rect(self.screen, C.OUTLINE, (bar_x, bar_y, bar_w, bar_h), 3)
            pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, (bar_x + 3, bar_y + 3, bar_w - 6, bar_h - 6))

            inner_w = bar_w - 10
            fill_w = int(inner_w * max(0.0, min(1.0, self.boot_progress_value)))
            if fill_w > 0:
                pygame.draw.rect(self.screen, C.DESK_ACCENT, (bar_x + 5, bar_y + 5, fill_w, bar_h - 10))

                if fill_w > 8:
                    pygame.draw.rect(self.screen, C.DESK_ACCENT_LIGHT, (bar_x + 5, bar_y + 5, fill_w, 4))

            percent = int(self.boot_progress_value * 100)
            percent_txt = render_pixel_text(self.font_small, f"{percent}%", C.DESK_TEXT, scale=2)
            self.screen.blit(
                percent_txt,
                (
                    screen_rect.centerx - percent_txt.get_width() // 2,
                    bar_y + 34
                )
            )

        fade_alpha = max(0, int(255 - self.boot_fade_alpha))
        if fade_alpha > 0:
            overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, fade_alpha))
            self.screen.blit(overlay, (0, 0))

    def _draw_shutdown_screen(self):
        self._draw_desktop()

        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)

        if self.shutdown_phase in ["show", "deleting"]:
            overlay.fill((0, 0, 0, 150))
        else:
            overlay.fill((0, 0, 0, max(150, self.shutdown_fade_alpha)))

        self.screen.blit(overlay, (0, 0))

        box_w = 760
        box_h = 220
        box = pygame.Rect(
            WINDOW_W // 2 - box_w // 2,
            WINDOW_H // 2 - box_h // 2,
            box_w,
            box_h
        )

        pygame.draw.rect(self.screen, C.OUTLINE, box, 5)
        pygame.draw.rect(self.screen, C.DESK_PANEL_DARK, box.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.DESK_ACCENT, box.inflate(-22, -22), 2)

        shown = self._localized_shutdown_text()[:self.shutdown_visible_chars]

        text = render_pixel_text(self.font_status, shown, C.DESK_TEXT, scale=3)
        x = box.centerx - text.get_width() // 2
        y = box.centery - text.get_height() // 2 - 8

        self.screen.blit(text, (x, y))

        if self.shutdown_phase == "deleting":
            if (self.anim_tick // 12) % 2 == 0:
                cursor_x = x + text.get_width() + 8
                cursor_y = y + 2
                pygame.draw.rect(self.screen, C.DESK_ACCENT_LIGHT, (cursor_x, cursor_y, 10, text.get_height()))

        if self.shutdown_phase == "fade":
            fade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            fade.fill((0, 0, 0, self.shutdown_fade_alpha))
            self.screen.blit(fade, (0, 0))

    def _draw_system_ready_screen(self):
        self.screen.fill(C.DESK_PANEL_DARK)
        outer = pygame.Rect(70, 70, WINDOW_W - 140, WINDOW_H - 140)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5)
        pygame.draw.rect(self.screen, C.DESK_ACCENT, outer.inflate(-10, -10), 2)
        inner = outer.inflate(-36, -36)
        for y in range(inner.height):
            t = y / max(1, inner.height - 1)
            color = tuple(int(C.DESK_BG_TOP[i] * (1 - t) + C.DESK_BG_BOTTOM[i] * t) for i in range(3))
            pygame.draw.line(self.screen, color, (inner.x, inner.y + y), (inner.right, inner.y + y))
        pulse = 0.65 + 0.35 * math.sin(self.anim_tick * 0.06)
        ring_color = tuple(int(v * pulse) for v in C.DESK_ACCENT_LIGHT)
        for index in range(3):
            rect = pygame.Rect(0, 0, 110 + index * 34, 110 + index * 34)
            rect.center = (inner.centerx, inner.centery - 102)
            pygame.draw.rect(self.screen, ring_color, rect, 2)
        pygame.draw.rect(self.screen, C.DESK_ACCENT_LIGHT, (inner.centerx - 8, inner.centery - 110, 16, 16))
        title = render_pixel_text(self.font_menu_title, "SYSTEM READY", C.DESK_ACCENT_LIGHT, scale=4)
        subtitle = render_pixel_text(self.font_small, SYSTEM_READY_SUBTITLE, C.DESK_TEXT, scale=2)
        title_y = inner.centery - 74
        self.screen.blit(title, (inner.centerx - title.get_width() // 2, title_y))
        sub_y = title_y + title.get_height() + 12
        self.screen.blit(subtitle, (inner.centerx - subtitle.get_width() // 2, sub_y))
        language_title = render_pixel_text(
            self.font_small, "LANGUAGE", C.DESK_MUTED, scale=2
        )
        self.screen.blit(
            language_title,
            (inner.centerx - language_title.get_width() // 2, inner.centery + 58),
        )
        mouse = self._logical_mouse_pos()
        for language_button in self._get_system_ready_language_buttons():
            language_rect = language_button["rect"].copy()
            selected = self.language == language_button["language"]
            hovered_language = language_rect.collidepoint(mouse)
            if hovered_language:
                language_rect = language_rect.inflate(6, 4)
            pygame.draw.rect(self.screen, C.OUTLINE, language_rect)
            pygame.draw.rect(
                self.screen,
                C.DESK_ICON_HOVER if selected or hovered_language else C.DESK_PANEL_DARK,
                language_rect.inflate(-5, -5),
            )
            pygame.draw.rect(
                self.screen,
                C.GOLD_LIGHT if selected else C.DESK_ACCENT,
                language_rect.inflate(-11, -11),
                2,
            )
            language_text = render_pixel_text(
                self.font_btn, language_button["label"], C.DESK_TEXT, scale=2
            )
            self.screen.blit(
                language_text,
                (
                    language_rect.centerx - language_text.get_width() // 2,
                    language_rect.centery - language_text.get_height() // 2,
                ),
            )
        button = self._get_system_ready_button().copy()
        hovered = button.collidepoint(self._logical_mouse_pos())
        if hovered:
            button = button.inflate(10, 8)
        if self.system_ready_pressed:
            button.y += 4
        if hovered:
            pygame.draw.rect(self.screen, C.OUTLINE, button.move(5, 5))
        pygame.draw.rect(self.screen, C.OUTLINE, button)
        pygame.draw.rect(self.screen, C.DESK_ICON_HOVER if hovered else C.DESK_ICON, button.inflate(-5, -5))
        pygame.draw.rect(self.screen, C.DESK_ACCENT_LIGHT, button.inflate(-12, -12), 2)
        text = render_pixel_text(self.font_btn, "ENTER SYSTEM", C.DESK_TEXT, scale=2)
        self.screen.blit(text, (button.centerx - text.get_width() // 2, button.centery - text.get_height() // 2))
        hint = render_pixel_text(self.font_small, "ENTER / CLICK TO CONTINUE", C.DESK_MUTED, scale=2)
        self.screen.blit(hint, (inner.centerx - hint.get_width() // 2, button.bottom + 12))


