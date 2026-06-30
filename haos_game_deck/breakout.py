from .common import *


class BreakoutMixin:
    def _get_breakout_end_buttons(self):
        btn_w, btn_h, gap = 190, 50, 24
        total_w = btn_w * 2 + gap
        start_x = WINDOW_W // 2 - total_w // 2
        y = WINDOW_H // 2 + 92
        return [
            {"rect": pygame.Rect(start_x, y, btn_w, btn_h), "label": "RESTART", "action": "restart", "selected": False},
            {"rect": pygame.Rect(start_x + btn_w + gap, y, btn_w, btn_h), "label": "MENU", "action": "menu", "selected": False},
        ]

    def _get_breakout_menu_buttons(self):
        cx = WINDOW_W // 2
        btn_w = 220
        btn_h = 50
        gap = 22
        start_y = 380
        return [
            {"rect": pygame.Rect(cx - btn_w // 2, start_y, btn_w, btn_h), "label": "START", "action": "breakout_start", "selected": False},
            {"rect": pygame.Rect(cx - btn_w // 2, start_y + btn_h + gap, btn_w, btn_h), "label": "SETTINGS", "action": "settings", "selected": False},
            {"rect": pygame.Rect(cx - btn_w // 2, start_y + (btn_h + gap) * 2, btn_w, btn_h), "label": "DESKTOP", "action": "desktop", "selected": False},
        ]

    def _handle_breakout_menu_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_desktop()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_breakout_menu_buttons():
                if b["rect"].collidepoint(event.pos): self.breakout_pressed_action = b["action"]; return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_breakout_menu_buttons():
                if b["rect"].collidepoint(event.pos) and self.breakout_pressed_action == b["action"]:
                    a = b["action"]
                    if a == "breakout_start": self._start_breakout_game()
                    elif a == "settings": self.state = self.BREAKOUT_SETTINGS
                    elif a == "desktop": self._go_desktop()
                    self.breakout_pressed_action = None; return
            self.breakout_pressed_action = None

    def _handle_breakout_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self._start_transition(self.BREAKOUT_MENU, "fade"); return
            if event.key == pygame.K_r: self._start_breakout_game(); return

    def _handle_breakout_end_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: self._start_breakout_game()
            elif event.key == pygame.K_ESCAPE: self._start_transition(self.BREAKOUT_MENU, "fade")
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_breakout_end_buttons():
                if b["rect"].collidepoint(event.pos):
                    self.breakout_pressed_action = b["action"]
                    return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_breakout_end_buttons():
                if b["rect"].collidepoint(event.pos) and self.breakout_pressed_action == b["action"]:
                    if b["action"] == "restart":
                        self._start_breakout_game()
                    elif b["action"] == "menu":
                        self._start_transition(self.BREAKOUT_MENU, "fade")
                    self.breakout_pressed_action = None
                    return
            self.breakout_pressed_action = None

    def _handle_breakout_settings_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = self.BREAKOUT_MENU; self.breakout_pressed_action = None; return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_breakout_settings_buttons():
                if b["rect"].collidepoint(event.pos): self.breakout_pressed_action = b["action"]; return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_breakout_settings_buttons():
                if b["rect"].collidepoint(event.pos) and self.breakout_pressed_action == b["action"]:
                    action = b["action"]
                    if action == "back": self._start_transition(self.BREAKOUT_MENU, "fade")
                    elif action.startswith("breakout_control_"): self.breakout_control_mode = action.replace("breakout_control_", "")
                    elif action.startswith("breakout_diff_"): self.breakout_difficulty = action.replace("breakout_diff_", ""); self._apply_breakout_difficulty()
                    elif action.startswith("breakout_ball_"):
                        skin = action.replace("breakout_ball_", "")
                        self.breakout_ball_skin = skin
                        self.breakout_ball_color = {"yellow": C.BREAKOUT_BALL_YELLOW, "cyan": C.BREAKOUT_BALL_CYAN, "pink": C.BREAKOUT_BALL_PINK}.get(skin, C.BREAKOUT_BALL_YELLOW)
                        if self.breakout_ball is not None: self.breakout_ball["color"] = self.breakout_ball_color
                    elif action.startswith("breakout_brick_"):
                        skin = action.replace("breakout_brick_", "")
                        self.breakout_brick_skin = skin
                        self.breakout_brick_color = {"purple": C.BREAKOUT_BRICK_PURPLE, "orange": C.BREAKOUT_BRICK_ORANGE, "blue": C.BREAKOUT_BRICK_BLUE}.get(skin, C.BREAKOUT_BRICK_PURPLE)
                    elif action.startswith("breakout_paddle_"):
                        skin = action.replace("breakout_paddle_", "")
                        self.breakout_paddle_skin = skin
                        self.breakout_paddle_color = {"orange": C.BREAKOUT_PADDLE_ORANGE, "cyan": C.BREAKOUT_PADDLE_CYAN, "pink": C.BREAKOUT_PADDLE_PINK}.get(skin, C.BREAKOUT_PADDLE_ORANGE)
                    self.breakout_pressed_action = None; return
            self.breakout_pressed_action = None

    def _apply_breakout_difficulty(self):
        if self.breakout_difficulty == "easy": self.breakout_ball_speed = 4.5; self.breakout_paddle_width = 158; self.breakout_paddle_speed = 8
        elif self.breakout_difficulty == "normal": self.breakout_ball_speed = 5.2; self.breakout_paddle_width = 126; self.breakout_paddle_speed = 9
        elif self.breakout_difficulty == "hard": self.breakout_ball_speed = 6.3; self.breakout_paddle_width = 96; self.breakout_paddle_speed = 10
        if self.breakout_paddle is not None:
            cx = self.breakout_paddle["x"] + self.breakout_paddle["width"] / 2
            self.breakout_paddle["width"] = self.breakout_paddle_width
            self.breakout_paddle["x"] = cx - self.breakout_paddle_width / 2

    def _start_breakout_game(self):
        self._apply_breakout_difficulty()
        self.breakout_score = 0; self.breakout_lives = 3; self.breakout_level = 1
        self.breakout_particles.clear(); self.breakout_score_jump_frame = 0
        self.breakout_shake_duration = 0; self.breakout_shake_x = 0; self.breakout_shake_y = 0
        self.breakout_end_panel_frame = 0; self.breakout_pressed_action = None
        self.breakout_bricks = self._generate_breakout_bricks()
        self.breakout_paddle = {"x": BOARD_X + BOARD_PX // 2 - self.breakout_paddle_width // 2, "y": BOARD_Y + BOARD_PX - 36, "width": self.breakout_paddle_width, "height": 16}
        self._reset_breakout_ball()
        self.state = self.BREAKOUT_PLAYING
        self.breakout_level_start_lives = self.breakout_lives
        self._record_stat("breakout", "games_started")

    def _reset_breakout_ball(self):
        s = self.breakout_ball_speed + (self.breakout_level - 1) * 0.35
        self.breakout_ball = {"x": BOARD_X + BOARD_PX // 2, "y": BOARD_Y + BOARD_PX - 70, "vx": random.choice([-1, 1]) * s * 0.55, "vy": -s, "radius": 8, "color": self.breakout_ball_color}
        self._normalize_breakout_ball_speed()

    def _generate_breakout_bricks(self):
        bricks = []
        rows, cols, gap = 5, 8, 6
        brick_w = (BOARD_PX - gap * (cols + 1)) // cols
        brick_h = 26
        sx = BOARD_X + gap
        sy = BOARD_Y + 34
        for r in range(rows):
            for c in range(cols):
                bricks.append({"x": sx + c * (brick_w + gap), "y": sy + r * (brick_h + gap), "w": brick_w, "h": brick_h, "alive": True, "row": r, "col": c})
        return bricks

    def _normalize_breakout_ball_speed(self):
        ball = self.breakout_ball
        if ball is None: return
        speed = math.sqrt(ball["vx"]**2 + ball["vy"]**2)
        if speed <= 0: ball["vx"] = self.breakout_ball_speed; ball["vy"] = -self.breakout_ball_speed; return
        target = self.breakout_ball_speed + (self.breakout_level - 1) * 0.35
        scale = target / speed
        ball["vx"] *= scale; ball["vy"] *= scale
        min_vy = 2.4
        if abs(ball["vy"]) < min_vy:
            ball["vy"] = -min_vy if ball["vy"] < 0 else min_vy
            vx_sign = 1 if ball["vx"] >= 0 else -1
            ball["vx"] = vx_sign * math.sqrt(max(1, target**2 - ball["vy"]**2))

    def _circle_rect_collision(self, cx, cy, radius, rect):
        closest_x = max(rect.left, min(cx, rect.right))
        closest_y = max(rect.top, min(cy, rect.bottom))
        return (cx - closest_x)**2 + (cy - closest_y)**2 <= radius**2

    def _handle_breakout_paddle_collision(self):
        ball = self.breakout_ball; pad = self.breakout_paddle
        if ball is None or pad is None: return
        paddle_rect = pygame.Rect(int(pad["x"]), int(pad["y"]), int(pad["width"]), int(pad["height"]))
        if ball["vy"] <= 0: return
        if not self._circle_rect_collision(ball["x"], ball["y"], ball["radius"], paddle_rect): return
        ball["y"] = paddle_rect.top - ball["radius"] - 1
        impact = max(-1.0, min(1.0, (ball["x"] - paddle_rect.centerx) / (paddle_rect.width / 2)))
        angle = impact * math.radians(65)
        speed = self.breakout_ball_speed + (self.breakout_level - 1) * 0.35
        ball["vx"] = math.sin(angle) * speed
        ball["vy"] = -math.cos(angle) * speed
        self.audio.play("breakout_paddle")
        self.breakout_shake_duration = 5
        self._spawn_breakout_particles(ball["x"], ball["y"], self.breakout_paddle_color, 8)

    def _handle_breakout_brick_collision(self):
        ball = self.breakout_ball
        if ball is None: return
        for brick in self.breakout_bricks:
            if not brick.get("alive", True): continue
            rect = pygame.Rect(int(brick["x"]), int(brick["y"]), int(brick["w"]), int(brick["h"]))
            if not self._circle_rect_collision(ball["x"], ball["y"], ball["radius"], rect): continue
            brick["alive"] = False
            self.audio.play("breakout_brick")
            self.breakout_score += 10; self.breakout_score_jump_frame = 14
            self._record_stat("breakout", "bricks_broken")
            self._record_stat("breakout", "best_score", self.breakout_score, mode="max")
            ol = abs((ball["x"] + ball["radius"]) - rect.left)
            or_ = abs(rect.right - (ball["x"] - ball["radius"]))
            ot = abs((ball["y"] + ball["radius"]) - rect.top)
            ob = abs(rect.bottom - (ball["y"] - ball["radius"]))
            min_o = min(ol, or_, ot, ob)
            if min_o in [ol, or_]: ball["vx"] *= -1
            else: ball["vy"] *= -1
            self._normalize_breakout_ball_speed()
            self._spawn_breakout_particles(rect.centerx, rect.centery, self.breakout_brick_color, 14)
            break

    def _update_breakout_paddle_control(self):
        if self.breakout_paddle is None: return
        bl, br = BOARD_X, BOARD_X + BOARD_PX
        if self.breakout_control_mode == "keyboard":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.breakout_paddle["x"] -= self.breakout_paddle_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.breakout_paddle["x"] += self.breakout_paddle_speed
        elif self.breakout_control_mode == "mouse":
            mx = self._logical_mouse_pos()[0]
            self.breakout_paddle["x"] = mx - self.breakout_paddle["width"] / 2
        self.breakout_paddle["x"] = max(bl, min(br - self.breakout_paddle["width"], self.breakout_paddle["x"]))

    def _update_breakout(self):
        if self.breakout_ball is None or self.breakout_paddle is None: return
        self._update_breakout_paddle_control()
        ball = self.breakout_ball
        ball["x"] += ball["vx"]; ball["y"] += ball["vy"]
        bl, br = BOARD_X, BOARD_X + BOARD_PX
        bt, bb = BOARD_Y, BOARD_Y + BOARD_PX
        if ball["x"] - ball["radius"] <= bl:
            ball["x"] = bl + ball["radius"]; ball["vx"] = abs(ball["vx"])
            self.audio.play("breakout_wall", 0.7)
            self._spawn_breakout_particles(ball["x"], ball["y"], ball["color"], 5)
        elif ball["x"] + ball["radius"] >= br:
            ball["x"] = br - ball["radius"]; ball["vx"] = -abs(ball["vx"])
            self.audio.play("breakout_wall", 0.7)
            self._spawn_breakout_particles(ball["x"], ball["y"], ball["color"], 5)
        if ball["y"] - ball["radius"] <= bt:
            ball["y"] = bt + ball["radius"]; ball["vy"] = abs(ball["vy"])
            self.audio.play("breakout_wall", 0.7)
            self._spawn_breakout_particles(ball["x"], ball["y"], ball["color"], 5)
        self._handle_breakout_paddle_collision()
        self._handle_breakout_brick_collision()
        self._normalize_breakout_ball_speed()
        if ball["y"] - ball["radius"] > bb:
            if getattr(self, "dev_invincible", False):
                self._reset_breakout_ball()
                return
            self.breakout_lives -= 1
            self._record_stat("breakout", "lives_lost")
            if self.breakout_lives <= 0:
                self.breakout_best = max(self.breakout_best, self.breakout_score)
                self.audio.play_gameover("breakout")
                self.breakout_end_panel_frame = 0
                self.breakout_pressed_action = None
                self.state = self.BREAKOUT_END
                self._record_stat("breakout", "games_completed")
                self._record_stat("breakout", "best_score", self.breakout_score, mode="max")
                self._record_stat("breakout", "highest_level", self.breakout_level, mode="max")
                return
            self._reset_breakout_ball()
        if self.breakout_bricks and all(not b.get("alive", True) for b in self.breakout_bricks):
            self._record_stat("breakout", "levels_cleared")
            if self.breakout_difficulty == "hard":
                self._record_stat("breakout", "hard_levels_cleared")
            if self.breakout_lives == self.breakout_level_start_lives:
                self._record_stat("breakout", "perfect_levels")
            self.breakout_level += 1
            self._record_stat("breakout", "highest_level", self.breakout_level, mode="max")
            self.breakout_level_start_lives = self.breakout_lives
            self.breakout_bricks = self._generate_breakout_bricks(); self._reset_breakout_ball()

    def _spawn_breakout_particles(self, x, y, color, count=10):
        if isinstance(color, str):
            color = getattr(C, f"BREAKOUT_BALL_{color.upper()}", C.BREAKOUT_BALL_YELLOW)
        for _ in range(count):
            self.breakout_particles.append({"x": x, "y": y, "vx": random.uniform(-2.4, 2.4), "vy": random.uniform(-2.4, 1.4), "life": random.randint(14, 28), "max_life": random.randint(18, 30), "color": color})

    def _update_breakout_visual_effects(self):
        if self.state == self.BREAKOUT_END and self.breakout_end_panel_frame < BREAKOUT_END_POP_FRAMES:
            self.breakout_end_panel_frame += 1
        for p in self.breakout_particles[:]:
            p["x"] += p["vx"]; p["y"] += p["vy"]; p["vy"] += 0.05; p["life"] -= 1
            if p["life"] <= 0: self.breakout_particles.remove(p)
        if self.breakout_score_jump_frame > 0: self.breakout_score_jump_frame -= 1
        if self.breakout_shake_duration > 0:
            self.breakout_shake_duration -= 1
            intensity = max(1, self.breakout_shake_duration // 2)
            self.breakout_shake_x = random.randint(-intensity, intensity)
            self.breakout_shake_y = random.randint(-intensity, intensity)
        else: self.breakout_shake_x = 0; self.breakout_shake_y = 0

    def _draw_breakout(self):
        self.screen.fill(C.BREAKOUT_BG)
        sx, sy = self.breakout_shake_x, self.breakout_shake_y
        outer = pygame.Rect(28 + sx, 28 + sy, WINDOW_W - 56, WINDOW_H - 56)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5)
        pygame.draw.rect(self.screen, C.BREAKOUT_ACCENT, outer.inflate(-8, -8), 2)
        self._draw_breakout_left_panel()
        self._draw_breakout_status_panel()
        board_rect = pygame.Rect(BOARD_X + sx, BOARD_Y + sy, BOARD_PX, BOARD_PX)
        pygame.draw.rect(self.screen, C.OUTLINE, board_rect.inflate(6, 6), 3)
        pygame.draw.rect(self.screen, C.BREAKOUT_PANEL_DARK, board_rect)
        for brick in self.breakout_bricks:
            if brick["alive"]:
                bx, by = int(brick["x"] + sx), int(brick["y"] + sy)
                pygame.draw.rect(self.screen, C.OUTLINE, (bx, by, brick["w"], brick["h"]))
                pygame.draw.rect(self.screen, self.breakout_brick_color, (bx + 2, by + 2, brick["w"] - 4, brick["h"] - 4))
        pad = self.breakout_paddle
        if pad is not None:
            pr = pygame.Rect(int(pad["x"] + sx), int(pad["y"] + sy), int(pad["width"]), int(pad["height"]))
            pygame.draw.rect(self.screen, C.OUTLINE, pr)
            pygame.draw.rect(self.screen, self.breakout_paddle_color, pr.inflate(-4, -4))
            pygame.draw.rect(self.screen, C.BREAKOUT_ACCENT_LIGHT, (pr.x + 8, pr.y + 4, pr.width - 16, 3))
        ball = self.breakout_ball
        if ball is not None:
            br = pygame.Rect(int(ball["x"] - ball["radius"] + sx), int(ball["y"] - ball["radius"] + sy), ball["radius"] * 2, ball["radius"] * 2)
            pygame.draw.rect(self.screen, C.OUTLINE, br)
            pygame.draw.rect(self.screen, ball["color"], br.inflate(-3, -3))
            pygame.draw.rect(self.screen, C.BREAKOUT_ACCENT_LIGHT, (br.x + 4, br.y + 4, 4, 4))
        for p in self.breakout_particles:
            alpha = max(0, min(255, int(255 * p["life"] / p["max_life"])))
            s = pygame.Surface((4, 4), pygame.SRCALPHA); s.fill((*p["color"], alpha))
            self.screen.blit(s, (int(p["x"] + sx), int(p["y"] + sy)))

    def _draw_breakout_left_panel(self):
        rect = pygame.Rect(LEFT_BAR_X, LEFT_BAR_Y, LEFT_BAR_W, LEFT_BAR_H)
        pygame.draw.rect(self.screen, C.BREAKOUT_PANEL, rect)
        pygame.draw.rect(self.screen, C.OUTLINE, rect, 4)
        pygame.draw.rect(self.screen, C.BREAKOUT_ACCENT, rect.inflate(-8, -8), 2)
        logo = render_vertical_pixel_text(self.font_menu_title, "BRKOUT", C.BREAKOUT_ACCENT_LIGHT, scale=3, gap=10)
        shadow = render_vertical_pixel_text(self.font_menu_title, "BRKOUT", C.OUTLINE, scale=3, gap=10)
        lx, ly = rect.centerx - logo.get_width() // 2, rect.centery - logo.get_height() // 2
        self.screen.blit(shadow, (lx + 3, ly + 3)); self.screen.blit(logo, (lx, ly))

    def _draw_breakout_status_panel(self):
        rect = pygame.Rect(RIGHT_BAR_X, RIGHT_BAR_Y, RIGHT_BAR_W, RIGHT_BAR_H)
        pygame.draw.rect(self.screen, C.BREAKOUT_PANEL, rect)
        pygame.draw.rect(self.screen, C.OUTLINE, rect, 4)
        pygame.draw.rect(self.screen, C.BREAKOUT_ACCENT, rect.inflate(-8, -8), 2)
        title = render_pixel_text(self.font_status, "STATUS", C.BREAKOUT_ACCENT_LIGHT, scale=2)
        self.screen.blit(title, (rect.centerx - title.get_width() // 2, rect.y + 42))
        score_lbl = render_pixel_text(self.font_status, "SCORE", C.BREAKOUT_TEXT, scale=2)
        jump = 0
        if self.breakout_score_jump_frame > 0:
            jump = int(math.sin(self.breakout_score_jump_frame / 14 * math.pi) * 8)
        score = render_pixel_text(self.font_status, str(self.breakout_score), C.BREAKOUT_ACCENT_LIGHT, scale=4)
        self.screen.blit(score_lbl, (rect.centerx - score_lbl.get_width() // 2, rect.y + 120))
        self.screen.blit(score, (rect.centerx - score.get_width() // 2, rect.y + 158 - jump))
        lives_lbl = render_pixel_text(self.font_status, "LIVES", C.BREAKOUT_TEXT, scale=2)
        lives = render_pixel_text(self.font_status, str(self.breakout_lives), C.BREAKOUT_ACCENT_LIGHT, scale=3)
        self.screen.blit(lives_lbl, (rect.centerx - lives_lbl.get_width() // 2, rect.y + 260))
        self.screen.blit(lives, (rect.centerx - lives.get_width() // 2, rect.y + 294))
        best_lbl = render_pixel_text(self.font_status, "BEST", C.BREAKOUT_TEXT, scale=2)
        best = render_pixel_text(self.font_status, str(self.breakout_best), C.BREAKOUT_ACCENT_LIGHT, scale=3)
        self.screen.blit(best_lbl, (rect.centerx - best_lbl.get_width() // 2, rect.y + 370))
        self.screen.blit(best, (rect.centerx - best.get_width() // 2, rect.y + 404))
        hint_text = "A/D Move  R Restart" if self.breakout_control_mode == "keyboard" else "MOUSE MOVE  R Restart"
        hint = render_pixel_text(self.font_small, hint_text, C.BREAKOUT_MUTED, scale=2)
        self.screen.blit(hint, (rect.centerx - hint.get_width() // 2, rect.y + 490))

    def _draw_breakout_menu(self):
        self.screen.fill(C.BREAKOUT_BG)
        outer = pygame.Rect(90, 54, WINDOW_W - 180, WINDOW_H - 108)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5)
        pygame.draw.rect(self.screen, C.BREAKOUT_PANEL, outer.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.BREAKOUT_ACCENT, outer.inflate(-22, -22), 2)
        title = render_pixel_text(self.font_menu_title, "BREAKOUT", C.BREAKOUT_ACCENT_LIGHT, scale=5)
        shadow = render_pixel_text(self.font_menu_title, "BREAKOUT", C.OUTLINE, scale=5)
        tx, ty = outer.centerx - title.get_width() // 2, outer.y + 120
        self.screen.blit(shadow, (tx + 4, ty + 4)); self.screen.blit(title, (tx, ty))
        subtitle_text = "打砖块 · 复古像素街机" if is_chinese() else "RETRO PIXEL ARCADE"
        subtitle = render_pixel_text(self.font_small, subtitle_text, C.BREAKOUT_TEXT, scale=2)
        self.screen.blit(subtitle, (outer.centerx - subtitle.get_width() // 2, ty + title.get_height() + 12))
        mp = self._logical_mouse_pos()
        for b in self._get_breakout_menu_buttons():
            self._draw_breakout_button(b, b["rect"].collidepoint(mp), self.breakout_pressed_action == b["action"])

    def _draw_breakout_button(self, btn, hovered=False, pressed=False):
        rect = btn["rect"].copy(); selected = btn.get("selected", False)
        if hovered: rect = rect.inflate(10, 8)
        if pressed: rect.y += 4
        shade = 6 if hovered else 4
        pygame.draw.rect(self.screen, C.OUTLINE, rect.move(shade, shade))
        if selected: fill, inner, tc = C.BREAKOUT_ACCENT, C.BREAKOUT_ACCENT_LIGHT, C.OUTLINE
        elif hovered: fill, inner, tc = C.BREAKOUT_PANEL, C.BREAKOUT_ACCENT_LIGHT, C.BREAKOUT_TEXT
        else: fill, inner, tc = C.BREAKOUT_PANEL_DARK, C.BREAKOUT_ACCENT, C.BREAKOUT_TEXT
        pygame.draw.rect(self.screen, C.OUTLINE, rect)
        pygame.draw.rect(self.screen, fill, rect.inflate(-5, -5))
        pygame.draw.rect(self.screen, inner, rect.inflate(-12, -12), 2)
        if hovered: pygame.draw.rect(self.screen, C.BREAKOUT_ACCENT_LIGHT, (rect.x + 10, rect.y + 8, rect.width - 20, 4))
        if selected:
            mark = pygame.Rect(rect.right - 18, rect.y + 8, 8, 8)
            pygame.draw.rect(self.screen, C.OUTLINE, mark); pygame.draw.rect(self.screen, C.BREAKOUT_TEXT, mark.inflate(-2, -2))
        label = render_pixel_text(self.font_btn, btn["label"], tc, scale=2)
        if label.get_width() > rect.width - 24: label = render_pixel_text(self.font_btn, btn["label"], tc, scale=1)
        lx, ly = rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2
        if hovered and not pressed: ly -= 1
        self.screen.blit(label, (lx, ly))

    def _draw_breakout_end(self):
        self._draw_breakout()
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA); overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        t = min(1.0, self.breakout_end_panel_frame / max(1, BREAKOUT_END_POP_FRAMES))
        pop = max(0.0, min(1.08, ease_out_back(t)))
        target_panel = pygame.Rect(WINDOW_W // 2 - 290, WINDOW_H // 2 - 180, 580, 360)
        panel = pygame.Rect(0, 0, max(1, int(target_panel.width * pop)), max(1, int(target_panel.height * pop)))
        panel.center = target_panel.center
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        if panel.width > 20 and panel.height > 20:
            pygame.draw.rect(self.screen, C.BREAKOUT_PANEL, panel.inflate(-10, -10))
        if panel.width > 48 and panel.height > 48:
            pygame.draw.rect(self.screen, C.BREAKOUT_ACCENT, panel.inflate(-24, -24), 2)
        if t < 0.45:
            return
        title = render_pixel_text(self.font_menu_title, "GAME OVER", C.BREAKOUT_ACCENT_LIGHT, scale=3)
        self.screen.blit(title, (target_panel.centerx - title.get_width() // 2, target_panel.y + 44))
        score = render_pixel_text(self.font_status, f"SCORE {self.breakout_score}", C.BREAKOUT_TEXT, scale=3)
        self.screen.blit(score, (target_panel.centerx - score.get_width() // 2, target_panel.y + 126))
        hint = render_pixel_text(self.font_status, "R: Restart  ESC: Menu", C.BREAKOUT_MUTED, scale=2)
        self.screen.blit(hint, (target_panel.centerx - hint.get_width() // 2, target_panel.y + 190))
        mouse_pos = self._logical_mouse_pos()
        for b in self._get_breakout_end_buttons():
            hovered = b["rect"].collidepoint(mouse_pos)
            pressed = hovered and self.breakout_pressed_action == b["action"]
            self._draw_breakout_button(b, hovered, pressed)

    def _get_breakout_settings_buttons(self):
        btns = []

        panel_w = min(WINDOW_W - 80, 1080)
        panel_h = min(WINDOW_H - 80, 650)
        panel = pygame.Rect(
            WINDOW_W // 2 - panel_w // 2,
            WINDOW_H // 2 - panel_h // 2,
            panel_w,
            panel_h
        )

        # 缁熶竴甯冨眬鍙傛暟
        row_y = panel.y + 188
        row_gap = 78
        btn_h = 42
        btn_gap = 22

        # 鎸夐挳鍖哄煙浠庤繖閲屽紑濮嬶紝宸﹁竟鐣欑粰鏍囬
        buttons_x = panel.x + 405

        def add_row(items, y, selected_getter):
            count = len(items)

            if count == 2:
                btn_w = 150
            else:
                btn_w = 122

            for i, (label, action) in enumerate(items):
                value = action.split("_")[-1]

                btns.append({
                    "rect": pygame.Rect(
                        int(buttons_x + i * (btn_w + btn_gap)),
                        int(y),
                        int(btn_w),
                        int(btn_h)
                    ),
                    "label": label,
                    "action": action,
                    "selected": selected_getter(value),
                })

        # CONTROL
        add_row(
            [("KEYBOARD", "breakout_control_keyboard"), ("MOUSE", "breakout_control_mouse")],
            row_y,
            lambda value: self.breakout_control_mode == value
        )

        # DIFFICULTY
        add_row(
            [("EASY", "breakout_diff_easy"), ("NORMAL", "breakout_diff_normal"), ("HARD", "breakout_diff_hard")],
            row_y + row_gap,
            lambda value: self.breakout_difficulty == value
        )

        # BALL COLOR
        add_row(
            [("YELLOW", "breakout_ball_yellow"), ("CYAN", "breakout_ball_cyan"), ("PINK", "breakout_ball_pink")],
            row_y + row_gap * 2,
            lambda value: self.breakout_ball_skin == value
        )

        # BRICK COLOR
        add_row(
            [("PURPLE", "breakout_brick_purple"), ("ORANGE", "breakout_brick_orange"), ("BLUE", "breakout_brick_blue")],
            row_y + row_gap * 3,
            lambda value: self.breakout_brick_skin == value
        )

        # PADDLE COLOR
        add_row(
            [("ORANGE", "breakout_paddle_orange"), ("CYAN", "breakout_paddle_cyan"), ("PINK", "breakout_paddle_pink")],
            row_y + row_gap * 4,
            lambda value: self.breakout_paddle_skin == value
        )

        # BACK 鎸夐挳
        back_w = 220
        back_h = 48
        btns.append({
            "rect": pygame.Rect(panel.centerx - back_w // 2, panel.bottom - 72, back_w, back_h),
            "label": "BACK",
            "action": "back",
            "selected": False
        })

        return btns

    def _draw_breakout_settings(self):
        self.screen.fill(C.BREAKOUT_BG)

        panel_w = min(WINDOW_W - 80, 1080)
        panel_h = min(WINDOW_H - 80, 650)
        panel = pygame.Rect(
            WINDOW_W // 2 - panel_w // 2,
            WINDOW_H // 2 - panel_h // 2,
            panel_w,
            panel_h
        )

        # 涓婚潰鏉?
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, C.BREAKOUT_PANEL, panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.BREAKOUT_ACCENT, panel.inflate(-24, -24), 2)

        # 鍥涜瑁呴グ
        cs = 18
        for cx, cy in [
            (panel.x, panel.y),
            (panel.right - cs, panel.y),
            (panel.x, panel.bottom - cs),
            (panel.right - cs, panel.bottom - cs),
        ]:
            pygame.draw.rect(self.screen, C.OUTLINE, (cx, cy, cs, cs))
            pygame.draw.rect(self.screen, C.BREAKOUT_ACCENT, (cx + 4, cy + 4, cs - 8, cs - 8))

        # 鏍囬
        title_text = "BREAKOUT SETTINGS"
        title = render_pixel_text(self.font_menu_title, title_text, C.BREAKOUT_ACCENT_LIGHT, scale=3)
        shadow = render_pixel_text(self.font_menu_title, title_text, C.OUTLINE, scale=3)

        tx = panel.centerx - title.get_width() // 2
        ty = panel.y + 38

        self.screen.blit(shadow, (tx + 3, ty + 3))
        self.screen.blit(title, (tx, ty))

        # 鏍囬涓嬪垝绾?
        line_y = panel.y + 112
        pygame.draw.line(self.screen, C.BREAKOUT_ACCENT, (panel.x + 70, line_y), (panel.right - 70, line_y), 3)
        pygame.draw.line(self.screen, C.OUTLINE, (panel.x + 70, line_y + 5), (panel.right - 70, line_y + 5), 2)

        # 璁剧疆椤硅甯冨眬
        row_y = panel.y + 188
        row_gap = 78

        label_x = panel.x + 165
        label_w = 210

        rows = [
            ("CONTROL", row_y),
            ("DIFFICULTY", row_y + row_gap),
            ("BALL COLOR", row_y + row_gap * 2),
            ("BRICK COLOR", row_y + row_gap * 3),
            ("PADDLE COLOR", row_y + row_gap * 4),
        ]

        for label, y in rows:
            # 姣忎竴琛岀殑娣℃贰鑳屾櫙妗嗭紝璁╂帓鐗堟洿绋冲畾
            row_rect = pygame.Rect(panel.x + 70, y - 10, panel_w - 140, 60)
            pygame.draw.rect(self.screen, C.BREAKOUT_PANEL_DARK, row_rect)
            pygame.draw.rect(self.screen, C.BREAKOUT_ACCENT, row_rect, 1)

            label_surf = render_pixel_text(self.font_status, label, C.BREAKOUT_TEXT, scale=2)
            lx = label_x + (label_w - label_surf.get_width()) // 2
            ly = y + 10
            self.screen.blit(label_surf, (lx, ly))

        # 缁樺埗鎸夐挳
        mp = self._logical_mouse_pos()

        for b in self._get_breakout_settings_buttons():
            self._draw_breakout_button(
                b,
                b["rect"].collidepoint(mp),
                self.breakout_pressed_action == b["action"]
            )
