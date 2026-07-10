from .common import *


class SnakeMixin:
    def _init_snake(self):
        self.snake = []
        self.snake_dir = (1, 0)
        self.snake_next_dir = (1, 0)
        self.snake_food = (0, 0)
        self.snake_score = 0
        self.snake_best = 0
        self.snake_move_timer = 0
        self.snake_game_over = False
        self.snake_pressed_action = None
        self.snake_speed_mode = "normal"
        self.snake_skin = "green"
        self.snake_body_color = C.SNAKE_BODY
        self.snake_head_color = C.SNAKE_HEAD
        self.snake_base_interval = SNAKE_MOVE_INTERVAL_FRAMES
        self.snake_particles = []
        self.snake_dead = False
        self.snake_shake_duration = 0
        self.snake_shake_x = 0
        self.snake_shake_y = 0
        self.snake_score_jump = 0
        self.snake_score_jump_frame = 0
        self.snake_cell_size = SNAKE_CELL_SIZE

    def _get_snake_menu_buttons(self):
        cx = WINDOW_W // 2
        btn_w = 210
        btn_h = 48
        gap = 20
        start_y = 330

        has_saved = self.save_data.get("progress", {}).get("snake", {}).get("run_active", False)

        buttons = []
        if has_saved:
            buttons.append({
                "rect": pygame.Rect(cx - btn_w // 2, start_y, btn_w, btn_h),
                "label": "CONTINUE",
                "action": "continue",
                "selected": False,
            })
            start_y += btn_h + gap

        buttons.extend([
            {
                "rect": pygame.Rect(cx - btn_w // 2, start_y, btn_w, btn_h),
                "label": "START",
                "action": "snake_start",
                "selected": False,
            },
            {
                "rect": pygame.Rect(cx - btn_w // 2, start_y + btn_h + gap, btn_w, btn_h),
                "label": "SETTINGS",
                "action": "settings",
                "selected": False,
            },
            {
                "rect": pygame.Rect(cx - btn_w // 2, start_y + (btn_h + gap) * 2, btn_w, btn_h),
                "label": "DESKTOP",
                "action": "desktop",
                "selected": False,
            },
        ])

        return buttons

    def _handle_snake_menu_event(self, event):
        if self.prologue_active:
            self._handle_prologue_event(event)
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._go_desktop()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self._start_snake_game()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_snake_menu_buttons():
                if b["rect"].collidepoint(event.pos):
                    self.snake_pressed_action = b["action"]
                    return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_snake_menu_buttons():
                if b["rect"].collidepoint(event.pos) and self.snake_pressed_action == b["action"]:
                    action = b["action"]

                    if action == "snake_start":
                        self._start_snake_game()
                    elif action == "continue":
                        state = self._pending_run_states.pop("snake", None)
                        self._start_snake_game(restore_state=state)
                        self.state = self.SNAKE_PLAYING
                    elif action == "settings":
                        self.state = self.SNAKE_SETTINGS
                    elif action == "desktop":
                        self._go_desktop()

                    self.snake_pressed_action = None
                    return

            self.snake_pressed_action = None

    def _set_snake_direction(self, new_dir):
        """Set snake direction using snake_next_dir for reverse check."""
        if not self.snake:
            return

        cur_dx, cur_dy = self.snake_next_dir
        new_dx, new_dy = new_dir

        if cur_dx + new_dx == 0 and cur_dy + new_dy == 0:
            return

        if self.snake_next_dir != new_dir:
            self.audio.play("snake_turn", 0.65)
        self.snake_next_dir = new_dir

    def _handle_snake_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = self.SNAKE_MENU
                self.snake_pressed_action = None
                return

            if event.key == pygame.K_r:
                self._start_snake_game()
                return

            if event.key in [pygame.K_UP, pygame.K_w]:
                self._set_snake_direction((0, -1))

            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self._set_snake_direction((0, 1))

            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                self._set_snake_direction((-1, 0))

            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self._set_snake_direction((1, 0))

    def _handle_snake_end_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._start_snake_game()
            elif event.key == pygame.K_ESCAPE:
                self.state = self.SNAKE_MENU
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_snake_end_buttons():
                if b["rect"].collidepoint(event.pos):
                    self.snake_pressed_action = b["action"]
                    return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_snake_end_buttons():
                if b["rect"].collidepoint(event.pos) and self.snake_pressed_action == b["action"]:
                    action = b["action"]

                    if action == "again":
                        self._start_snake_game()
                    elif action == "menu":
                        self.state = self.SNAKE_MENU
                    elif action == "desktop":
                        self._go_desktop()

                    self.snake_pressed_action = None
                    return

            self.snake_pressed_action = None

    def _get_snake_settings_buttons(self):
        cx = WINDOW_W // 2
        btns = []

        # SPEED 鎸夐挳
        speed_btn_w = 150
        speed_btn_h = 48
        speed_gap = 24
        speed_y = 315

        speed_items = [
            ("Slow", "snake_speed_slow"),
            ("Normal", "snake_speed_normal"),
            ("Fast", "snake_speed_fast"),
        ]

        total_speed_w = len(speed_items) * speed_btn_w + (len(speed_items) - 1) * speed_gap
        start_x = cx - total_speed_w // 2

        for i, (label, action) in enumerate(speed_items):
            btns.append({
                "rect": pygame.Rect(
                    start_x + i * (speed_btn_w + speed_gap),
                    speed_y,
                    speed_btn_w,
                    speed_btn_h
                ),
                "label": label.upper(),
                "action": action,
                "selected": self.snake_speed_mode == label.lower(),
            })

        # COLOR 鎸夐挳
        color_btn_w = 150
        color_btn_h = 48
        color_gap = 24
        color_y = 455

        color_items = [
            ("GREEN", "snake_color_green"),
            ("LIME", "snake_color_lime"),
            ("RED", "snake_color_red"),
        ]

        total_color_w = len(color_items) * color_btn_w + (len(color_items) - 1) * color_gap
        start_x = cx - total_color_w // 2

        for i, (label, action) in enumerate(color_items):
            btns.append({
                "rect": pygame.Rect(
                    start_x + i * (color_btn_w + color_gap),
                    color_y,
                    color_btn_w,
                    color_btn_h
                ),
                "label": label,
                "action": action,
                "selected": self.snake_skin == label.lower(),
            })

        # BACK 鎸夐挳
        back_w = 220
        back_h = 52
        back_y = 585

        btns.append({
            "rect": pygame.Rect(cx - back_w // 2, back_y, back_w, back_h),
            "label": "BACK",
            "action": "back",
            "selected": False,
        })

        return btns

    def _handle_snake_settings_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = self.SNAKE_MENU
                self.snake_pressed_action = None
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_snake_settings_buttons():
                if b["rect"].collidepoint(event.pos):
                    self.snake_pressed_action = b["action"]
                    return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_snake_settings_buttons():
                if b["rect"].collidepoint(event.pos) and self.snake_pressed_action == b["action"]:
                    action = b["action"]

                    if action == "back":
                        self._start_transition(self.SNAKE_MENU, "fade")

                    elif action.startswith("snake_speed_"):
                        mode = action.replace("snake_speed_", "")
                        self.snake_speed_mode = mode

                        if mode == "slow":
                            self.snake_base_interval = 11
                        elif mode == "normal":
                            self.snake_base_interval = 8
                        elif mode == "fast":
                            self.snake_base_interval = 6

                    elif action.startswith("snake_color_"):
                        skin = action.replace("snake_color_", "")
                        self.snake_skin = skin

                        if skin == "green":
                            self.snake_body_color = C.SNAKE_BODY
                            self.snake_head_color = C.SNAKE_HEAD
                        elif skin == "lime":
                            self.snake_body_color = C.SNAKE_LIME_BODY
                            self.snake_head_color = C.SNAKE_LIME_HEAD
                        elif skin == "red":
                            self.snake_body_color = C.SNAKE_RED_BODY
                            self.snake_head_color = C.SNAKE_RED_HEAD

                    self.snake_pressed_action = None
                    return

            self.snake_pressed_action = None

    def _draw_snake_settings_page(self):
        self.screen.fill(C.SNAKE_BG)

        # 涓婚潰鏉?
        panel_w = 980
        panel_h = 600
        panel = pygame.Rect(
            WINDOW_W // 2 - panel_w // 2,
            WINDOW_H // 2 - panel_h // 2,
            panel_w,
            panel_h
        )

        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, C.SNAKE_PANEL, panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.SNAKE_ACCENT, panel.inflate(-24, -24), 2)

        # 鍥涜瑁呴グ
        corner_size = 18
        for cx, cy in [
            (panel.x, panel.y),
            (panel.right - corner_size, panel.y),
            (panel.x, panel.bottom - corner_size),
            (panel.right - corner_size, panel.bottom - corner_size),
        ]:
            pygame.draw.rect(self.screen, C.OUTLINE, (cx, cy, corner_size, corner_size))
            pygame.draw.rect(self.screen, C.SNAKE_ACCENT, (cx + 4, cy + 4, corner_size - 8, corner_size - 8))

        # 鏍囬
        title = render_pixel_text(self.font_menu_title, "SNAKE SETTINGS", C.SNAKE_ACCENT_LIGHT, scale=3)

        if title.get_width() > panel.width - 120:
            title = render_pixel_text(self.font_menu_title, "SETTINGS", C.SNAKE_ACCENT_LIGHT, scale=3)

        shadow = render_pixel_text(
            self.font_menu_title,
            "SNAKE SETTINGS" if title.get_width() <= panel.width - 120 else "SETTINGS",
            C.OUTLINE,
            scale=3
        )

        title_x = panel.centerx - title.get_width() // 2
        title_y = panel.y + 52

        self.screen.blit(shadow, (title_x + 3, title_y + 3))
        self.screen.blit(title, (title_x, title_y))

        # 鍒嗛殧绾?
        line_y = panel.y + 132
        pygame.draw.line(self.screen, C.SNAKE_ACCENT, (panel.x + 70, line_y), (panel.right - 70, line_y), 3)
        pygame.draw.line(self.screen, C.OUTLINE, (panel.x + 70, line_y + 5), (panel.right - 70, line_y + 5), 2)

        # SPEED 鍖哄煙
        speed_label = render_pixel_text(self.font_status, "SPEED", C.SNAKE_TEXT, scale=2)
        self.screen.blit(speed_label, (panel.centerx - speed_label.get_width() // 2, panel.y + 185))
        speed_note = render_pixel_text(self.font_small, "Adjust snake movement speed", C.SNAKE_ACCENT, scale=2)
        self.screen.blit(speed_note, (panel.centerx - speed_note.get_width() // 2, panel.y + 214))

        # COLOR 鍖哄煙
        color_label = render_pixel_text(self.font_status, "SKIN COLOR", C.SNAKE_TEXT, scale=2)
        self.screen.blit(color_label, (panel.centerx - color_label.get_width() // 2, panel.y + 335))

        # 鎸夐挳
        mouse_pos = self._logical_mouse_pos()
        for b in self._get_snake_settings_buttons():
            hovered = b["rect"].collidepoint(mouse_pos)
            pressed = self.snake_pressed_action == b["action"]
            self._draw_snake_button(b, hovered, pressed)

    def _get_snake_end_buttons(self):
        btn_w = 210
        btn_h = 44
        gap = 14

        # 鍜?_draw_snake_end() 淇濇寔涓€鑷寸殑闈㈡澘灏哄
        panel_w = 560
        panel_h = 430
        panel = pygame.Rect(
            WINDOW_W // 2 - panel_w // 2,
            WINDOW_H // 2 - panel_h // 2,
            panel_w,
            panel_h
        )

        # 淇锛氭寜閽笉瑕佸啀鍐欐鍒?440锛岃€屾槸鐩稿闈㈡澘鍐呴儴瀹氫綅
        start_y = panel.y + 250
        x = panel.centerx - btn_w // 2

        return [
            {
                "rect": pygame.Rect(x, start_y, btn_w, btn_h),
                "label": "PLAY AGAIN",
                "action": "again",
                "selected": False,
            },
            {
                "rect": pygame.Rect(x, start_y + btn_h + gap, btn_w, btn_h),
                "label": "MENU",
                "action": "menu",
                "selected": False,
            },
            {
                "rect": pygame.Rect(x, start_y + (btn_h + gap) * 2, btn_w, btn_h),
                "label": "DESKTOP",
                "action": "desktop",
                "selected": False,
            },
        ]

    def _start_snake_game(self, restore_state=None):
        mid = SNAKE_GRID_COUNT // 2
        if restore_state:
            self.snake = restore_state["body"]
            self.snake_dir = tuple(restore_state["dir"])
            self.snake_next_dir = tuple(restore_state["next_dir"])
            self.snake_food = tuple(restore_state["food"]) if restore_state.get("food") else (0, 0)
            self.snake_score = restore_state["score"]
            self.snake_move_timer = restore_state.get("move_timer", 0)
        else:
            self.snake = [(mid, mid-2), (mid, mid-1), (mid, mid)]
            self.snake_dir = (1, 0)
            self.snake_next_dir = (1, 0)
            self.snake_food = (0, 0)
            self.snake_score = 0
            self.snake_move_timer = 0
        self.snake_game_over = False
        self.snake_dead = False
        self.snake_particles.clear()
        self.snake_score_jump = 0
        self.snake_score_jump_frame = 0

        self._spawn_snake_food()

        self.state = self.SNAKE_PLAYING
        self._record_stat("snake", "games_started")
        self._clear_run_state("snake")

    def _capture_snake_run_state(self):
        return {
            "body": self.snake[:],
            "dir": self.snake_dir,
            "next_dir": self.snake_next_dir,
            "food": self.snake_food,
            "score": self.snake_score,
            "move_timer": self.snake_move_timer,
        }

    def _spawn_snake_food(self):
        empty = []

        snake_set = set(self.snake)

        for r in range(SNAKE_GRID_COUNT):
            for c in range(SNAKE_GRID_COUNT):
                if (r, c) not in snake_set:
                    empty.append((r, c))

        if empty:
            self.snake_food = random.choice(empty)
        else:
            self.snake_food = None

    def _update_snake(self):
        if self.state != self.SNAKE_PLAYING:
            return

        self.snake_move_timer += 1

        if self.snake_move_timer < self._get_snake_current_interval():
            return

        self.snake_move_timer = 0

        self.snake_dir = self.snake_next_dir

        head_r, head_c = self.snake[-1]
        dc, dr = self.snake_dir

        new_head = (head_r + dr, head_c + dc)
        if getattr(self, "dev_invincible", False):
            new_head = (
                new_head[0] % SNAKE_GRID_COUNT,
                new_head[1] % SNAKE_GRID_COUNT,
            )
            if new_head in self.snake:
                self.snake.remove(new_head)

        # 鎾炲
        if not (0 <= new_head[0] < SNAKE_GRID_COUNT and 0 <= new_head[1] < SNAKE_GRID_COUNT):
            self._end_snake_game()
            return

        # 鎾炶嚜宸?
        if new_head in self.snake:
            self._end_snake_game()
            return

        self.snake.append(new_head)

        # 鍚冨埌椋熺墿
        if self.snake_food is not None and new_head == self.snake_food:
            self.audio.play("snake_eat")
            self.snake_score += 1
            self._record_stat("snake", "food_eaten")
            self._record_stat("snake", "best_score", self.snake_score, mode="max")
            if self.snake_speed_mode == "fast":
                self._record_stat("snake", "best_fast_score", self.snake_score, mode="max")
            self.snake_best = max(self.snake_best, self.snake_score)
            self.snake_score_jump = 6
            self.snake_score_jump_frame = 8
            # 椋熺墿绮掑瓙
            fx = SNAKE_X + self.snake_food[1] * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
            fy = SNAKE_Y + self.snake_food[0] * SNAKE_CELL_SIZE + SNAKE_CELL_SIZE // 2
            self._spawn_snake_particles(fx, fy)
            self._spawn_snake_food()
            # 闅惧害闅忓垎鏁版彁鍗囩敱 _get_snake_current_interval() 璁＄畻
            # 杩欓噷涓嶈鐩存帴淇敼 snake_base_interval锛屽惁鍒欎細鐮村潖璁剧疆椤甸€夋嫨
        else:
            self.snake.pop(0)

    def _get_snake_current_interval(self):
        """Current move interval. Speed increases with score but setting is preserved."""
        bonus = self.snake_score // 5
        return max(4, self.snake_base_interval - bonus)

    def _update_snake_visual_effects(self):
        # SNAKE 姝讳骸鎶栧睆
        if self.snake_shake_duration > 0:
            self.snake_shake_duration -= 1
            intensity = max(1, self.snake_shake_duration // 4)
            self.snake_shake_x = random.randint(-intensity, intensity)
            self.snake_shake_y = random.randint(-intensity, intensity)
        else:
            self.snake_shake_x = 0
            self.snake_shake_y = 0

        # 椋熺墿绮掑瓙
        for p in self.snake_particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1

            if p["life"] <= 0:
                self.snake_particles.remove(p)

    def _spawn_snake_particles(self, x, y):
        for _ in range(10):
            vx = random.uniform(-2.5, 2.5)
            vy = random.uniform(-2.5, 2.5)
            self.snake_particles.append({
                "x": x, "y": y,
                "vx": vx, "vy": vy,
                "life": random.randint(18, 28),
                "max_life": 28,
                "color": self.snake_body_color,
            })

    def _end_snake_game(self):
        self.audio.play_gameover("snake")
        self.snake_game_over = True
        self.snake_dead = True
        self.snake_best = max(self.snake_best, self.snake_score)
        self._record_stat("snake", "deaths")
        self._record_stat("snake", "games_completed")
        self._record_stat("snake", "best_score", self.snake_score, mode="max")

        # SNAKE 涓撶敤姝讳骸鎶栧睆
        self.snake_shake_duration = 18
        self.snake_shake_x = 0
        self.snake_shake_y = 0

        self.state = self.SNAKE_END
        self._clear_run_state("snake")

    def _draw_snake_left_title_panel(self):
        rect = pygame.Rect(LEFT_BAR_X, LEFT_BAR_Y, LEFT_BAR_W, LEFT_BAR_H)

        pygame.draw.rect(self.screen, C.SNAKE_PANEL, rect)
        pygame.draw.rect(self.screen, C.OUTLINE, rect, 4)
        pygame.draw.rect(self.screen, C.SNAKE_ACCENT, rect.inflate(-8, -8), 2)

        logo = render_vertical_pixel_text(
            self.font_menu_title,
            "SNAKE",
            C.SNAKE_ACCENT_LIGHT,
            scale=3,
            gap=12
        )

        shadow = render_vertical_pixel_text(
            self.font_menu_title,
            "SNAKE",
            C.OUTLINE,
            scale=3,
            gap=12
        )

        lx = rect.centerx - logo.get_width() // 2
        ly = rect.centery - logo.get_height() // 2

        self.screen.blit(shadow, (lx + 3, ly + 3))
        self.screen.blit(logo, (lx, ly))

    def _draw_snake_status_panel(self):
        rect = pygame.Rect(RIGHT_BAR_X, RIGHT_BAR_Y, RIGHT_BAR_W, RIGHT_BAR_H)

        pygame.draw.rect(self.screen, C.SNAKE_PANEL, rect)
        pygame.draw.rect(self.screen, C.OUTLINE, rect, 4)
        pygame.draw.rect(self.screen, C.SNAKE_ACCENT, rect.inflate(-8, -8), 2)

        title = render_pixel_text(self.font_status, "STATUS", C.SNAKE_ACCENT_LIGHT, scale=2)
        self.screen.blit(title, (rect.centerx - title.get_width() // 2, rect.y + 42))

        score_title = render_pixel_text(self.font_status, "SCORE", C.SNAKE_TEXT, scale=2)
        score = render_pixel_text(self.font_status, str(self.snake_score), C.SNAKE_ACCENT_LIGHT, scale=4)

        base_score_y = rect.y + 158
        if self.snake_score_jump_frame > 0:
            offset = int(math.sin((8 - self.snake_score_jump_frame) / 8 * math.pi) * self.snake_score_jump)
            self.snake_score_jump_frame -= 1
        else:
            offset = 0
        score_y = int(base_score_y - offset)

        self.screen.blit(score_title, (rect.centerx - score_title.get_width() // 2, rect.y + 120))
        self.screen.blit(score, (rect.centerx - score.get_width() // 2, score_y))

        best_title = render_pixel_text(self.font_status, "BEST", C.SNAKE_TEXT, scale=2)
        best = render_pixel_text(self.font_status, str(self.snake_best), C.SNAKE_ACCENT_LIGHT, scale=3)

        self.screen.blit(best_title, (rect.centerx - best_title.get_width() // 2, rect.y + 260))
        self.screen.blit(best, (rect.centerx - best.get_width() // 2, rect.y + 294))

        speed_text = f"SPD {self._get_snake_current_interval()}"
        speed = render_pixel_text(self.font_status, speed_text, C.SNAKE_TEXT, scale=2)
        self.screen.blit(speed, (rect.centerx - speed.get_width() // 2, rect.y + 350))

        hint1 = render_pixel_text(self.font_small, "WASD / ARROWS", C.SNAKE_TEXT, scale=2)
        hint2 = render_pixel_text(self.font_small, "R: Restart", C.SNAKE_TEXT, scale=2)
        hint3 = render_pixel_text(self.font_small, "ESC: Menu", C.SNAKE_TEXT, scale=2)

        self.screen.blit(hint1, (rect.centerx - hint1.get_width() // 2, rect.y + 425))
        self.screen.blit(hint2, (rect.centerx - hint2.get_width() // 2, rect.y + 459))
        self.screen.blit(hint3, (rect.centerx - hint3.get_width() // 2, rect.y + 493))

    def _draw_snake_game(self):
        self.screen.fill(C.SNAKE_BG)

        sx = self.snake_shake_x
        sy = self.snake_shake_y

        outer = pygame.Rect(28 + sx, 28 + sy, WINDOW_W - 56, WINDOW_H - 56)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5)
        pygame.draw.rect(self.screen, C.SNAKE_ACCENT, outer.inflate(-8, -8), 2)

        self._draw_snake_left_title_panel()
        self._draw_snake_status_panel()

        board_rect = pygame.Rect(
            SNAKE_X + sx,
            SNAKE_Y + sy,
            SNAKE_BOARD_PX,
            SNAKE_BOARD_PX
        )

        pygame.draw.rect(self.screen, C.OUTLINE, board_rect.inflate(14, 14))
        pygame.draw.rect(self.screen, C.SNAKE_PANEL_DARK, board_rect)

        cell = SNAKE_CELL_SIZE

        # 缃戞牸
        for i in range(SNAKE_GRID_COUNT + 1):
            x = board_rect.x + i * cell
            y = board_rect.y + i * cell
            pygame.draw.line(self.screen, C.SNAKE_GRID_DARK, (x, board_rect.y), (x, board_rect.bottom), 1)
            pygame.draw.line(self.screen, C.SNAKE_GRID_DARK, (board_rect.x, y), (board_rect.right, y), 1)

        # 椋熺墿
        if self.snake_food is not None:
            fr, fc = self.snake_food
            fx = board_rect.x + fc * cell
            fy = board_rect.y + fr * cell
            pygame.draw.rect(self.screen, C.OUTLINE, (fx + 3, fy + 3, cell - 6, cell - 6))
            pygame.draw.rect(self.screen, C.SNAKE_FOOD, (fx + 5, fy + 5, cell - 10, cell - 10))
            pygame.draw.rect(self.screen, C.SNAKE_FOOD_LIGHT, (fx + 8, fy + 8, 5, 5))

        # 铔?
        for idx, (r, c) in enumerate(self.snake):
            x = board_rect.x + c * cell
            y = board_rect.y + r * cell

            is_head = idx == len(self.snake) - 1
            col = self.snake_head_color if is_head else self.snake_body_color

            pygame.draw.rect(self.screen, C.OUTLINE, (x + 2, y + 2, cell - 4, cell - 4))
            pygame.draw.rect(self.screen, col, (x + 4, y + 4, cell - 8, cell - 8))

            if is_head:
                eye_size = 3
                dc, dr = self.snake_next_dir
                cx_body = x + cell // 2
                cy_body = y + cell // 2
                offset = 4
                if dr == 0 and dc == 1:  # right
                    eyes = [(cx_body + offset, cy_body - offset), (cx_body + offset, cy_body + offset)]
                elif dr == 0 and dc == -1:  # left
                    eyes = [(cx_body - offset, cy_body - offset), (cx_body - offset, cy_body + offset)]
                elif dr == 1 and dc == 0:  # down
                    eyes = [(cx_body - offset, cy_body + offset), (cx_body + offset, cy_body + offset)]
                else:  # up
                    eyes = [(cx_body - offset, cy_body - offset), (cx_body + offset, cy_body - offset)]
                for ex, ey in eyes:
                    pygame.draw.rect(self.screen, C.OUTLINE, (ex - 1, ey - 1, eye_size, eye_size))

        # 椋熺墿绮掑瓙锛氬彧缁樺埗锛屼笉鍦?draw 閲屾洿鏂?
        for p in self.snake_particles:
            alpha = max(0, int(255 * p["life"] / p["max_life"]))
            size = max(1, int(4 * p["life"] / p["max_life"]))
            color = (*p["color"], alpha)

            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill(color)

            self.screen.blit(
                s,
                (
                    int(p["x"] - size // 2 + sx),
                    int(p["y"] - size // 2 + sy)
                )
            )

    def _draw_snake_menu(self):
        if self._check_and_show_prologue("snake"):
            self._draw_prologue_screen()
            return

        self.screen.fill(C.SNAKE_BG)

        outer = pygame.Rect(90, 54, WINDOW_W - 180, WINDOW_H - 108)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5)
        pygame.draw.rect(self.screen, C.SNAKE_PANEL, outer.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.SNAKE_ACCENT, outer.inflate(-22, -22), 2)

        title = render_pixel_text(self.font_menu_title, "SNAKE", C.SNAKE_ACCENT_LIGHT, scale=5)
        shadow = render_pixel_text(self.font_menu_title, "SNAKE", C.OUTLINE, scale=5)

        tx = outer.centerx - title.get_width() // 2
        ty = outer.y + 120

        self.screen.blit(shadow, (tx + 4, ty + 4))
        self.screen.blit(title, (tx, ty))

        subtitle_text = "复古像素街机" if is_chinese() else "RETRO PIXEL ARCADE"
        subtitle = render_pixel_text(self.font_small, subtitle_text, C.SNAKE_TEXT, scale=2)
        self.screen.blit(subtitle, (outer.centerx - subtitle.get_width() // 2, ty + title.get_height() + 18))

        mouse_pos = self._logical_mouse_pos()

        for b in self._get_snake_menu_buttons():
            hovered = b["rect"].collidepoint(mouse_pos)
            self._draw_snake_button(b, hovered, self.snake_pressed_action == b["action"])

    def _draw_snake_button(self, button, hovered=False, pressed=False):
        rect = button["rect"].copy()
        selected = button.get("selected", False)

        # 鍔ㄦ晥锛氭偓鍋滄斁澶э紝鎸変笅涓嬫矇
        if hovered:
            rect = rect.inflate(10, 8)

        if pressed:
            rect.y += 4

        # 闃村奖
        shadow_offset = 6 if hovered else 4
        pygame.draw.rect(self.screen, C.OUTLINE, rect.move(shadow_offset, shadow_offset))

        # 涓讳綋棰滆壊
        if selected:
            fill = C.SNAKE_ACCENT
            inner = C.SNAKE_ACCENT_LIGHT
            text_col = C.OUTLINE
        elif hovered:
            fill = C.SNAKE_PANEL
            inner = C.SNAKE_ACCENT_LIGHT
            text_col = C.SNAKE_TEXT
        else:
            fill = C.SNAKE_PANEL_DARK
            inner = C.SNAKE_ACCENT
            text_col = C.SNAKE_TEXT

        pygame.draw.rect(self.screen, C.OUTLINE, rect)
        pygame.draw.rect(self.screen, fill, rect.inflate(-5, -5))

        # 鍐呮弿杈?
        pygame.draw.rect(self.screen, inner, rect.inflate(-12, -12), 2)

        # 鎮仠楂樺厜鏉?
        if hovered:
            shine_rect = pygame.Rect(rect.x + 10, rect.y + 8, rect.width - 20, 4)
            pygame.draw.rect(self.screen, C.SNAKE_ACCENT_LIGHT, shine_rect)

        # 閫変腑鐘舵€佺殑灏忚鏍?
        if selected:
            mark = pygame.Rect(rect.right - 18, rect.y + 8, 8, 8)
            pygame.draw.rect(self.screen, C.OUTLINE, mark)
            pygame.draw.rect(self.screen, C.SNAKE_TEXT, mark.inflate(-2, -2))

        # 鏂囨湰
        label = render_pixel_text(self.font_btn, button["label"], text_col, scale=2)

        if label.get_width() > rect.width - 24:
            label = render_pixel_text(self.font_btn, button["label"], text_col, scale=1)

        lx = rect.centerx - label.get_width() // 2
        ly = rect.centery - label.get_height() // 2

        # 鎮仠鏃舵枃瀛楄交寰笂娴?
        if hovered and not pressed:
            ly -= 1

        self.screen.blit(label, (lx, ly))

    def _draw_snake_end(self):
        # 鍏堢敾璐悆铔囨父鎴忕敾闈綔涓鸿儗鏅?
        self._draw_snake_game()

        # 鍗婇€忔槑閬僵
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        self.screen.blit(overlay, (0, 0))

        # 灞呬腑缁撴潫闈㈡澘
        panel_w = 560
        panel_h = 430
        panel = pygame.Rect(
            WINDOW_W // 2 - panel_w // 2,
            WINDOW_H // 2 - panel_h // 2,
            panel_w,
            panel_h
        )

        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, C.SNAKE_PANEL, panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.SNAKE_ACCENT, panel.inflate(-24, -24), 2)

        # 鏍囬
        title = render_pixel_text(self.font_menu_title, "GAME OVER", C.SNAKE_FOOD_LIGHT, scale=3)
        self.screen.blit(
            title,
            (
                panel.centerx - title.get_width() // 2,
                panel.y + 42
            )
        )

        # 鍒嗘暟
        score = render_pixel_text(self.font_status, f"SCORE {self.snake_score}", C.SNAKE_TEXT, scale=3)
        best = render_pixel_text(self.font_status, f"BEST {self.snake_best}", C.SNAKE_ACCENT_LIGHT, scale=3)

        self.screen.blit(
            score,
            (
                panel.centerx - score.get_width() // 2,
                panel.y + 128
            )
        )

        self.screen.blit(
            best,
            (
                panel.centerx - best.get_width() // 2,
                panel.y + 182
            )
        )

        # 鎸夐挳
        mouse_pos = self._logical_mouse_pos()

        for b in self._get_snake_end_buttons():
            hovered = b["rect"].collidepoint(mouse_pos)
            self._draw_snake_button(
                b,
                hovered,
                self.snake_pressed_action == b["action"]
            )
