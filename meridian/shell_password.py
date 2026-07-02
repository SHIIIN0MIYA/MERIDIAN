from .common import *
from .developer import DEV_PASSWORD


class PasswordMixin:
    def _init_password(self):
        self.password_input = []
        self.password_target = PASSWORD_TARGET
        self.password_max_length = PASSWORD_MAX_LENGTH
        self.password_error = False
        self.password_error_frame = 0
        self.password_pressed_action = None
        self.password_buttons = self._build_password_buttons()

    def _build_password_buttons(self):
        screen_rect = pygame.Rect(0, 0, WINDOW_W, WINDOW_H)
        btn_w, btn_h = 72, 44
        gap_x, gap_y = 18, 10
        cols, rows = 3, 4
        total_w = cols * btn_w + (cols - 1) * gap_x
        total_h = rows * btn_h + (rows - 1) * gap_y
        start_x = screen_rect.centerx - total_w // 2
        start_y = screen_rect.centery + 10

        layout = [
            ("1", 0, 0), ("2", 1, 0), ("3", 2, 0),
            ("4", 0, 1), ("5", 1, 1), ("6", 2, 1),
            ("7", 0, 2), ("8", 1, 2), ("9", 2, 2),
            ("0", 1, 3),
        ]
        buttons = []
        for label, col, row in layout:
            x = start_x + col * (btn_w + gap_x)
            y = start_y + row * (btn_h + gap_y)
            buttons.append({"label": label, "rect": pygame.Rect(x, y, btn_w, btn_h)})
        # DEL button in bottom-right corner
        del_x = start_x + 2 * (btn_w + gap_x)
        del_y = start_y + 3 * (btn_h + gap_y)
        del_w, del_h = 58, 44
        buttons.append({"label": "DEL", "rect": pygame.Rect(del_x, del_y, del_w, del_h)})
        return buttons

    def _handle_password_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_shutdown()
            elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                if self.password_input and not self.password_error:
                    self.password_input.pop()
                    self.password_pressed_action = "DEL"
                    self.audio.play("button_click", 0.6)
            elif not self.password_error:
                digit = event.unicode if event.unicode.isdigit() else ""
                if digit and len(self.password_input) < self.password_max_length:
                    self.password_input.append(digit)
                    self.password_pressed_action = digit
                    self.audio.play("button_click", 0.6)
            return

        if self.password_error:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self.password_buttons:
                if b["rect"].collidepoint(event.pos):
                    if b["label"] == "DEL":
                        if self.password_input:
                            self.password_input.pop()
                        self.password_pressed_action = "DEL"
                    else:
                        self.password_input.append(b["label"])
                        self.password_pressed_action = b["label"]
                    self.audio.play("button_click", 0.6)
                    break

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.password_pressed_action = None

    def _update_password(self):
        if self.password_error:
            self.password_error_frame += 1
            if self.password_error_frame >= PASSWORD_ERROR_SHAKE_FRAMES:
                self.password_error = False
                self.password_error_frame = 0
                self.password_pressed_action = None
            return

        if len(self.password_input) >= self.password_max_length:
            if self.password_input == DEV_PASSWORD:
                self._enable_developer_mode()
                self.audio.play("achievement", 0.75)
                self._start_transition(self.DESKTOP, "fade")
            elif self.password_input == self.password_target:
                self.audio.play("button_click", 0.6)
                self._start_transition(self.DESKTOP, "fade")
            else:
                self.password_error = True
                self.password_error_frame = 0
                self.password_input = []
                self.password_pressed_action = None
                self.audio.play("error", 0.8)

    def _draw_password_screen(self):
        self.screen.fill(C.PASSWORD_BG)

        outer = pygame.Rect(70, 70, WINDOW_W - 140, WINDOW_H - 140)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5)
        pygame.draw.rect(self.screen, C.DESK_ACCENT, outer.inflate(-10, -10), 2)

        screen_rect = outer.inflate(-36, -36)

        for i in range(screen_rect.height):
            t = i / max(1, screen_rect.height - 1)
            r = int(C.DESK_BG_TOP[0] * (1 - t) + C.DESK_BG_BOTTOM[0] * t)
            g = int(C.DESK_BG_TOP[1] * (1 - t) + C.DESK_BG_BOTTOM[1] * t)
            b = int(C.DESK_BG_TOP[2] * (1 - t) + C.DESK_BG_BOTTOM[2] * t)
            pygame.draw.line(self.screen, (r, g, b), (screen_rect.x, screen_rect.y + i), (screen_rect.right, screen_rect.y + i))

        for i in range(24):
            x = screen_rect.x + (i * 97 + 31) % screen_rect.width
            y = screen_rect.y + (i * 53 + 47) % screen_rect.height
            pulse = 0.5 + 0.5 * abs(math.sin(self.anim_tick * 0.03 + i))
            col = (int(C.DESK_ACCENT[0] * pulse), int(C.DESK_ACCENT[1] * pulse), int(C.DESK_ACCENT[2] * pulse))
            pygame.draw.rect(self.screen, col, (x, y, 3, 3))

        title = render_pixel_text(self.font_status, "NEXUS AUTHENTICATION", C.DESK_ACCENT_LIGHT, scale=3)
        self.screen.blit(title, (screen_rect.centerx - title.get_width() // 2, screen_rect.y + 48))

        digit_w, digit_h = 50, 60
        total_digit_w = self.password_max_length * digit_w + (self.password_max_length - 1) * 14
        base_x = screen_rect.centerx - total_digit_w // 2
        base_y = screen_rect.y + 176

        error_flash_on = (self.password_error_frame // PASSWORD_ERROR_FLASH_INTERVAL) % 2 == 0 if self.password_error else True

        for idx in range(self.password_max_length):
            rx = base_x + idx * (digit_w + 14)
            ry = base_y

            if self.password_error:
                shake_offset = int(math.sin(self.anim_tick * 0.6) * 5)
                rx += shake_offset

            rect = pygame.Rect(rx, ry, digit_w, digit_h)

            if self.password_error and not error_flash_on:
                border_color = (max(0, min(255, C.PASSWORD_DIGIT_ERROR[0])),
                                max(0, min(255, C.PASSWORD_DIGIT_ERROR[1] // 2)),
                                max(0, min(255, C.PASSWORD_DIGIT_ERROR[2] // 2)))
            elif self.password_error:
                border_color = C.PASSWORD_DIGIT_ERROR
            else:
                border_color = C.PASSWORD_BTN_BORDER

            pygame.draw.rect(self.screen, C.OUTLINE, rect, 3)
            pygame.draw.rect(self.screen, border_color, rect.inflate(-6, -6), 2)

            if idx < len(self.password_input):
                digit_color = C.PASSWORD_DIGIT_ERROR if self.password_error else C.PASSWORD_DIGIT
                txt = render_pixel_text(self.font_status, self.password_input[idx], digit_color, scale=3)
                self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        if self.password_error:
            error_text = render_pixel_text(self.font_small, "RESONANCE MISMATCH", C.PASSWORD_ERROR_TEXT, scale=2)
            self.screen.blit(error_text, (screen_rect.centerx - error_text.get_width() // 2, base_y + digit_h + 18))

        mouse_pos = self._logical_mouse_pos()
        for b in self.password_buttons:
            rect = b["rect"].copy()
            label = b["label"]
            hovered = rect.collidepoint(mouse_pos)
            pressed = self.password_pressed_action == label

            is_del = (label == "DEL")

            if hovered:
                rect = rect.inflate(8, 8)

            if pressed:
                rect.y += 4

            if hovered:
                shadow_col = C.PASSWORD_ERROR_TEXT if is_del else C.OUTLINE
                pygame.draw.rect(self.screen, shadow_col, rect.move(4, 4))

            border_col_out = C.PASSWORD_ERROR_TEXT if is_del else C.OUTLINE
            pygame.draw.rect(self.screen, border_col_out, rect)

            if is_del:
                fill = (70, 40, 50) if pressed else (50, 32, 45)
                if hovered: fill = (90, 52, 60)
                border_in = (210, 80, 80) if hovered else (160, 65, 70)
            else:
                fill = C.PASSWORD_BTN_HOVER if hovered else C.PASSWORD_BTN
                border_in = C.DESK_ACCENT_LIGHT if hovered else C.PASSWORD_BTN_BORDER
            pygame.draw.rect(self.screen, fill, rect.inflate(-5, -5))
            pygame.draw.rect(self.screen, border_in, rect.inflate(-10, -10), 2)

            if is_del:
                # Pixel-art backspace arrow: ←
                cx = rect.centerx
                cy = rect.centery
                arrow = [
                    (8, 0), (6, 0), (4, 0), (2, 0), (0, 0), (-2, 0), (-4, 0), (-6, 0), (-8, 0),
                    (6, -1), (4, -1), (2, -1), (0, -1), (-2, -1), (-4, -1), (-6, -1),
                    (4, -2), (2, -2), (0, -2), (-2, -2), (-4, -2),
                    (2, -3), (0, -3), (-2, -3),
                    (0, -4),
                    (8, 1), (6, 1), (4, 1), (2, 1), (0, 1), (-2, 1), (-4, 1), (-6, 1),
                    (6, 2), (4, 2), (2, 2), (0, 2), (-2, 2), (-4, 2),
                    (4, 3), (2, 3), (0, 3), (-2, 3),
                    (2, 4),
                ]
                arrow_color = (255, 140, 140) if hovered else (200, 100, 110)
                if pressed: arrow_color = C.GOLD_LIGHT
                for dx, dy in arrow:
                    pygame.draw.rect(self.screen, arrow_color,
                                     (cx + dx * 2, cy + dy * 2, 2, 2))
            else:
                txt = render_pixel_text(self.font_status, label, C.DESK_TEXT if not pressed else C.DESK_ACCENT_LIGHT, scale=2)
                self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        hint = render_pixel_text(self.font_small, "ESC: Shutdown", C.DESK_MUTED, scale=2)
        self.screen.blit(hint, (screen_rect.centerx - hint.get_width() // 2, screen_rect.bottom - hint.get_height() - 8))
