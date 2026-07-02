from .common import *


PIECE_SHAPES = {
    "I": (
        ((0, 1), (1, 1), (2, 1), (3, 1)),
        ((2, 0), (2, 1), (2, 2), (2, 3)),
        ((0, 2), (1, 2), (2, 2), (3, 2)),
        ((1, 0), (1, 1), (1, 2), (1, 3)),
    ),
    "O": (((1, 0), (2, 0), (1, 1), (2, 1)),) * 4,
    "T": (
        ((1, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (2, 1), (1, 2)),
        ((0, 1), (1, 1), (2, 1), (1, 2)),
        ((1, 0), (0, 1), (1, 1), (1, 2)),
    ),
    "S": (
        ((1, 0), (2, 0), (0, 1), (1, 1)),
        ((1, 0), (1, 1), (2, 1), (2, 2)),
        ((1, 1), (2, 1), (0, 2), (1, 2)),
        ((0, 0), (0, 1), (1, 1), (1, 2)),
    ),
    "Z": (
        ((0, 0), (1, 0), (1, 1), (2, 1)),
        ((2, 0), (1, 1), (2, 1), (1, 2)),
        ((0, 1), (1, 1), (1, 2), (2, 2)),
        ((1, 0), (0, 1), (1, 1), (0, 2)),
    ),
    "J": (
        ((0, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (2, 0), (1, 1), (1, 2)),
        ((0, 1), (1, 1), (2, 1), (2, 2)),
        ((1, 0), (1, 1), (0, 2), (1, 2)),
    ),
    "L": (
        ((2, 0), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (1, 2), (2, 2)),
        ((0, 1), (1, 1), (2, 1), (0, 2)),
        ((0, 0), (1, 0), (1, 1), (1, 2)),
    ),
}

PIECE_COLORS = {
    "I": C.TETRIS_I,
    "O": C.TETRIS_O,
    "T": C.TETRIS_T,
    "S": C.TETRIS_S,
    "Z": C.TETRIS_Z,
    "J": C.TETRIS_J,
    "L": C.TETRIS_L,
}


class TetrisMixin:
    def _init_tetris_state(self):
        self.tetris_grid = [[None for _ in range(TETRIS_COLS)] for _ in range(TETRIS_ROWS)]
        self.tetris_current = None
        self.tetris_next = None
        self.tetris_hold = None
        self.tetris_can_hold = True
        self.tetris_bag = []
        self.tetris_score = 0
        self.tetris_lines = 0
        self.tetris_level = 1
        self.tetris_fall_tick = 0
        self.tetris_lock_tick = 0
        self.tetris_paused = False
        self.tetris_pressed_action = None
        self.tetris_end_frame = 0
        self.tetris_particles = []
        self.tetris_clear_flash = []
        self.tetris_repeat = {}
        self.tetris_preview_grid = [[None for _ in range(10)] for _ in range(20)]
        self.tetris_preview_piece = None
        self.tetris_preview_tick = 0
        self.tetris_preview_rng = random.Random(425)
        self.tetris_preview_gameover = False
        self.tetris_preview_gameover_frame = 0
        self._reset_tetris_preview()

    def _new_tetris_piece(self, kind):
        return {"kind": kind, "x": 3, "y": 0, "rotation": 0}

    def _take_tetris_bag_piece(self):
        if not self.tetris_bag:
            self.tetris_bag = list(PIECE_SHAPES)
            random.shuffle(self.tetris_bag)
        return self.tetris_bag.pop()

    def _start_tetris_game(self, restore_state=None):
        if restore_state:
            self.tetris_grid = [[None if cell is None else cell for cell in row] for row in restore_state["grid"]]
            self.tetris_bag = restore_state["bag"][:]
            self.tetris_next = restore_state["next"]
            self.tetris_hold = restore_state["hold"]
            self.tetris_can_hold = restore_state["can_hold"]
            self.tetris_current = restore_state["current"].copy() if restore_state["current"] else None
            self.tetris_score = restore_state["score"]
            self.tetris_lines = restore_state["lines"]
            self.tetris_level = restore_state["level"]
            self.tetris_fall_tick = restore_state["fall_tick"]
            self.tetris_lock_tick = restore_state["lock_tick"]
        else:
            self.tetris_grid = [[None for _ in range(TETRIS_COLS)] for _ in range(TETRIS_ROWS)]
            self.tetris_bag = []
            self.tetris_next = self._take_tetris_bag_piece()
            self.tetris_hold = None
            self.tetris_can_hold = True
            self.tetris_score = 0
            self.tetris_lines = 0
            self.tetris_level = 1
            self.tetris_fall_tick = 0
            self.tetris_lock_tick = 0
            self._spawn_tetris_piece()
        self.tetris_paused = False
        self.tetris_pressed_action = None
        self.tetris_end_frame = 0
        self.tetris_particles = []
        self.tetris_clear_flash = []
        self.tetris_repeat = {}
        self.state = self.TETRIS_PLAYING
        self.tetris_stats_completed = False
        self._record_stat("tetris", "games_started")
        self._clear_run_state("tetris")

    def _capture_tetris_run_state(self):
        grid_data = []
        for row in self.tetris_grid:
            grid_data.append([cell if cell is None else str(cell) for cell in row])
        return {
            "grid": grid_data,
            "bag": self.tetris_bag[:],
            "next": self.tetris_next,
            "hold": self.tetris_hold,
            "can_hold": self.tetris_can_hold,
            "current": self.tetris_current.copy() if self.tetris_current else None,
            "score": self.tetris_score,
            "lines": self.tetris_lines,
            "level": self.tetris_level,
            "fall_tick": self.tetris_fall_tick,
            "lock_tick": self.tetris_lock_tick,
        }

    def _finish_tetris_game(self):
        self.tetris_end_frame = 0
        self.audio.play_gameover("tetris")
        self.state = self.TETRIS_END
        self._clear_run_state("tetris")
        if not getattr(self, "tetris_stats_completed", False):
            self.tetris_stats_completed = True
            self._record_stat("tetris", "games_completed")
            self._record_stat("tetris", "best_score", self.tetris_score, mode="max")
            self._record_stat("tetris", "highest_level", self.tetris_level, mode="max")
            self._record_stat("tetris", "best_lines", self.tetris_lines, mode="max")
            self.tetris_best = max(getattr(self, "tetris_best", 0), self.tetris_score)
            self.tetris_best_level = max(getattr(self, "tetris_best_level", 1), self.tetris_level)

    def _spawn_tetris_piece(self):
        kind = self.tetris_next or self._take_tetris_bag_piece()
        self.tetris_next = self._take_tetris_bag_piece()
        self.tetris_current = self._new_tetris_piece(kind)
        self.tetris_can_hold = True
        self.tetris_lock_tick = 0
        if self._tetris_collides(self.tetris_current):
            self._finish_tetris_game()

    def _tetris_cells(self, piece, x=None, y=None, rotation=None):
        px = piece["x"] if x is None else x
        py = piece["y"] if y is None else y
        rot = piece["rotation"] if rotation is None else rotation
        return [(px + dx, py + dy) for dx, dy in PIECE_SHAPES[piece["kind"]][rot % 4]]

    def _tetris_collides(self, piece, x=None, y=None, rotation=None):
        for col, row in self._tetris_cells(piece, x, y, rotation):
            if col < 0 or col >= TETRIS_COLS or row >= TETRIS_ROWS:
                return True
            if row >= 0 and self.tetris_grid[row][col] is not None:
                return True
        return False

    def _move_tetris_piece(self, dx, dy, sound=True):
        piece = self.tetris_current
        if piece is None or self._tetris_collides(piece, piece["x"] + dx, piece["y"] + dy):
            return False
        piece["x"] += dx
        piece["y"] += dy
        if dx and sound:
            self.audio.play("tetris_move", 0.45)
        self.tetris_lock_tick = 0
        return True

    def _rotate_tetris_piece(self, direction=1):
        piece = self.tetris_current
        if piece is None:
            return False
        target = (piece["rotation"] + direction) % 4
        for kick_x, kick_y in ((0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)):
            if not self._tetris_collides(piece, piece["x"] + kick_x, piece["y"] + kick_y, target):
                piece["x"] += kick_x
                piece["y"] += kick_y
                piece["rotation"] = target
                self.tetris_lock_tick = 0
                self.audio.play("tetris_rotate", 0.55)
                return True
        return False

    def _hard_drop_tetris_piece(self):
        distance = 0
        while self._move_tetris_piece(0, 1, sound=False):
            distance += 1
        self.tetris_score += distance * 2
        self.audio.play("tetris_drop", 0.7)
        self._lock_tetris_piece()

    def _hold_tetris_piece(self):
        if not self.tetris_can_hold or self.tetris_current is None:
            return
        current_kind = self.tetris_current["kind"]
        if self.tetris_hold is None:
            self.tetris_hold = current_kind
            self._spawn_tetris_piece()
        else:
            swap = self.tetris_hold
            self.tetris_hold = current_kind
            self.tetris_current = self._new_tetris_piece(swap)
            if self._tetris_collides(self.tetris_current):
                self._finish_tetris_game()
        self.tetris_can_hold = False
        self.audio.play("tetris_hold", 0.55)

    def _lock_tetris_piece(self):
        piece = self.tetris_current
        if piece is None:
            return
        color = PIECE_COLORS[piece["kind"]]
        for col, row in self._tetris_cells(piece):
            if row < 0:
                self._finish_tetris_game()
                return
            self.tetris_grid[row][col] = piece["kind"]
            self._spawn_tetris_particles(col, row, color, 3)
        cleared = [row for row in range(TETRIS_ROWS) if all(self.tetris_grid[row])]
        if cleared:
            self._clear_tetris_lines(cleared)
        self._record_stat("tetris", "pieces_locked")
        self._spawn_tetris_piece()

    def _clear_tetris_lines(self, rows):
        count = len(rows)
        for row in rows:
            self.tetris_clear_flash.append({"row": row, "life": 18})
        remaining = [row for index, row in enumerate(self.tetris_grid) if index not in rows]
        self.tetris_grid = [[None for _ in range(TETRIS_COLS)] for _ in rows] + remaining
        self.tetris_lines += count
        self.tetris_level = 1 + self.tetris_lines // 10
        self.tetris_score += (0, 100, 300, 500, 800)[count] * self.tetris_level
        self._record_stat("tetris", "lines_cleared", count)
        self._record_stat("tetris", "best_lines", self.tetris_lines, mode="max")
        self._record_stat("tetris", "highest_level", self.tetris_level, mode="max")
        self._record_stat("tetris", "best_score", self.tetris_score, mode="max")
        if count == 4:
            self._record_stat("tetris", "tetrises")
        self.audio.play(f"tetris_clear{count}", 0.8)

    def _tetris_ghost_y(self):
        if self.tetris_current is None:
            return 0
        y = self.tetris_current["y"]
        while not self._tetris_collides(self.tetris_current, y=y + 1):
            y += 1
        return y

    def _tetris_fall_interval(self):
        return max(4, 48 - (self.tetris_level - 1) * 4)

    def _spawn_tetris_particles(self, col, row, color, count):
        x = TETRIS_BOARD_X + col * TETRIS_CELL + TETRIS_CELL // 2
        y = TETRIS_BOARD_Y + (row - TETRIS_HIDDEN_ROWS) * TETRIS_CELL + TETRIS_CELL // 2
        for _ in range(count):
            self.tetris_particles.append({
                "x": x, "y": y, "vx": random.uniform(-1.8, 1.8),
                "vy": random.uniform(-2.4, -0.4), "life": random.randint(12, 24), "color": color,
            })

    def _get_tetris_menu_buttons(self):
        buttons = []
        y = 350
        has_saved = self.save_data.get("progress", {}).get("tetris", {}).get("run_active", False)
        if has_saved:
            buttons.append({"rect": pygame.Rect(820, y, 260, 54), "label": "CONTINUE", "action": "continue"})
            y += 76
        buttons.append({"rect": pygame.Rect(820, y, 260, 54), "label": "START", "action": "start"})
        y += 76
        buttons.append({"rect": pygame.Rect(820, y, 260, 54), "label": "DESKTOP", "action": "desktop"})
        return buttons

    def _get_tetris_end_buttons(self):
        return [
            {"rect": pygame.Rect(WINDOW_W // 2 - 218, WINDOW_H // 2 + 98, 200, 52), "label": "RESTART", "action": "restart"},
            {"rect": pygame.Rect(WINDOW_W // 2 + 18, WINDOW_H // 2 + 98, 200, 52), "label": "MENU", "action": "menu"},
        ]

    def _get_tetris_play_buttons(self):
        return [
            {"rect": pygame.Rect(102, 542, 112, 42), "label": "RESUME" if self.tetris_paused else "PAUSE", "action": "pause"},
            {"rect": pygame.Rect(230, 542, 112, 42), "label": "MENU", "action": "menu"},
        ]

    def _handle_tetris_menu_event(self, event):
        if self.prologue_active:
            self._handle_prologue_event(event)
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_desktop()
            return
        self._handle_tetris_buttons(event, self._get_tetris_menu_buttons(), {
            "continue": lambda: self._start_tetris_game(restore_state=self._pending_run_states.pop("tetris", None)),
            "start": self._start_tetris_game,
            "desktop": self._go_desktop,
        })

    def _handle_tetris_end_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._start_tetris_game()
            elif event.key == pygame.K_ESCAPE:
                self._start_transition(self.TETRIS_MENU, "fade")
            return
        self._handle_tetris_buttons(event, self._get_tetris_end_buttons(), {
            "restart": self._start_tetris_game,
            "menu": lambda: self._start_transition(self.TETRIS_MENU, "fade"),
        })

    def _handle_tetris_buttons(self, event, buttons, actions):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in buttons:
                if button["rect"].collidepoint(event.pos):
                    self.tetris_pressed_action = button["action"]
                    return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for button in buttons:
                if button["rect"].collidepoint(event.pos) and self.tetris_pressed_action == button["action"]:
                    self.tetris_pressed_action = None
                    actions[button["action"]]()
                    return
            self.tetris_pressed_action = None

    def _handle_tetris_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_transition(self.TETRIS_MENU, "fade")
            elif event.key == pygame.K_r:
                self._start_tetris_game()
            elif event.key == pygame.K_p:
                self.tetris_paused = not self.tetris_paused
            elif not self.tetris_paused:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self._move_tetris_piece(-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self._move_tetris_piece(1, 0)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self._rotate_tetris_piece(1)
                elif event.key == pygame.K_z:
                    self._rotate_tetris_piece(-1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if self._move_tetris_piece(0, 1, sound=False):
                        self.tetris_score += 1
                elif event.key == pygame.K_SPACE:
                    self._hard_drop_tetris_piece()
                elif event.key == pygame.K_c:
                    self._hold_tetris_piece()
            return
        self._handle_tetris_buttons(event, self._get_tetris_play_buttons(), {
            "pause": self._toggle_tetris_pause,
            "menu": lambda: self._start_transition(self.TETRIS_MENU, "fade"),
        })

    def _toggle_tetris_pause(self):
        self.tetris_paused = not self.tetris_paused

    def _update_tetris(self):
        if self.tetris_paused or self.tetris_current is None:
            return
        keys = pygame.key.get_pressed()
        for key, dx in ((pygame.K_LEFT, -1), (pygame.K_a, -1), (pygame.K_RIGHT, 1), (pygame.K_d, 1)):
            if keys[key]:
                count = self.tetris_repeat.get(key, 0) + 1
                self.tetris_repeat[key] = count
                if count > 10 and count % 3 == 0:
                    self._move_tetris_piece(dx, 0, sound=False)
            else:
                self.tetris_repeat[key] = 0
        self.tetris_fall_tick += 1
        soft_drop = keys[pygame.K_DOWN] or keys[pygame.K_s]
        interval = 2 if soft_drop else self._tetris_fall_interval()
        if self.tetris_fall_tick >= interval:
            self.tetris_fall_tick = 0
            if self._move_tetris_piece(0, 1, sound=False):
                if soft_drop:
                    self.tetris_score += 1
            else:
                self.tetris_lock_tick += interval
                if self.tetris_lock_tick >= 24:
                    self._lock_tetris_piece()
        self._update_tetris_effects()

    def _update_tetris_effects(self):
        for particle in self.tetris_particles[:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.12
            particle["life"] -= 1
            if particle["life"] <= 0:
                self.tetris_particles.remove(particle)
        for flash in self.tetris_clear_flash[:]:
            flash["life"] -= 1
            if flash["life"] <= 0:
                self.tetris_clear_flash.remove(flash)

    def _update_tetris_end(self):
        self.tetris_end_frame = min(TETRIS_END_POP_FRAMES, self.tetris_end_frame + 1)
        self._update_tetris_effects()

    def _reset_tetris_preview(self):
        self.tetris_preview_grid = [[None for _ in range(10)] for _ in range(20)]
        self.tetris_preview_gameover = False
        self.tetris_preview_gameover_frame = 0
        for row in range(14, 20):
            for col in range(10):
                if self.tetris_preview_rng.random() < 0.58 and not (row == 14 and 3 <= col <= 6):
                    self.tetris_preview_grid[row][col] = self.tetris_preview_rng.choice(tuple(PIECE_SHAPES))
        self.tetris_preview_piece = {
            "kind": self.tetris_preview_rng.choice(tuple(PIECE_SHAPES)),
            "x": self.tetris_preview_rng.randint(1, 5),
            "y": -2,
            "rotation": 0,
        }

    def _preview_collides(self, piece, x=None, y=None, rotation=None):
        px = piece["x"] if x is None else x
        py = piece["y"] if y is None else y
        rot = piece["rotation"] if rotation is None else rotation
        for dx, dy in PIECE_SHAPES[piece["kind"]][rot % 4]:
            col, row = px + dx, py + dy
            if col < 0 or col >= 10 or row >= 20:
                return True
            if row >= 0 and self.tetris_preview_grid[row][col]:
                return True
        return False

    def _update_tetris_preview(self):
        self.tetris_preview_tick += 1
        if self.tetris_preview_gameover:
            self.tetris_preview_gameover_frame += 1
            if self.tetris_preview_gameover_frame >= 120:
                self._reset_tetris_preview()
            return
        piece = self.tetris_preview_piece
        if self.tetris_preview_tick % 22 == 0:
            direction = self.tetris_preview_rng.choice((-1, 0, 1))
            if not self._preview_collides(piece, x=piece["x"] + direction):
                piece["x"] += direction
            if self.tetris_preview_rng.random() < 0.45:
                rotation = (piece["rotation"] + 1) % 4
                if not self._preview_collides(piece, rotation=rotation):
                    piece["rotation"] = rotation
        if self.tetris_preview_tick % 7 == 0:
            if not self._preview_collides(piece, y=piece["y"] + 1):
                piece["y"] += 1
            else:
                locked_above_top = any(
                    piece["y"] + dy < 0
                    for _, dy in PIECE_SHAPES[piece["kind"]][piece["rotation"]]
                )
                for dx, dy in PIECE_SHAPES[piece["kind"]][piece["rotation"]]:
                    col, row = piece["x"] + dx, piece["y"] + dy
                    if 0 <= row < 20:
                        self.tetris_preview_grid[row][col] = piece["kind"]
                if locked_above_top or any(self.tetris_preview_grid[row][col] for row in range(2) for col in range(10)):
                    self.tetris_preview_gameover = True
                    self.tetris_preview_gameover_frame = 0
                    self.tetris_preview_piece = None
                    return
                full = [row for row in range(20) if all(self.tetris_preview_grid[row])]
                self.tetris_preview_grid = [[None] * 10 for _ in full] + [
                    row for index, row in enumerate(self.tetris_preview_grid) if index not in full
                ]
                self.tetris_preview_piece = {
                    "kind": self.tetris_preview_rng.choice(tuple(PIECE_SHAPES)),
                    "x": self.tetris_preview_rng.randint(1, 5),
                    "y": -2,
                    "rotation": 0,
                }

    def _draw_tetris_background(self):
        self.screen.fill(C.TETRIS_BG)
        for y in range(0, WINDOW_H, 8):
            shade = 4 if (y // 8) % 2 else 0
            color = tuple(min(255, value + shade) for value in C.TETRIS_BG)
            pygame.draw.rect(self.screen, color, (0, y, WINDOW_W, 8))
        for index in range(34):
            x = (index * 83 + 41) % WINDOW_W
            y = (index * 47 + 29) % WINDOW_H
            pygame.draw.rect(self.screen, C.TETRIS_GRID, (x, y, 3, 3))

    def _draw_tetris_panel(self, rect):
        pygame.draw.rect(self.screen, C.OUTLINE, rect, 5)
        pygame.draw.rect(self.screen, C.TETRIS_PANEL_DARK, rect.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.TETRIS_ACCENT, rect.inflate(-22, -22), 2)

    def _draw_tetris_button(self, button, hovered=False, pressed=False):
        rect = button["rect"].copy()
        if hovered:
            rect = rect.inflate(10, 8)
        if pressed:
            rect.y += 4
        if hovered:
            pygame.draw.rect(self.screen, C.OUTLINE, rect.move(5, 5))
        pygame.draw.rect(self.screen, C.OUTLINE, rect)
        pygame.draw.rect(self.screen, C.TETRIS_PANEL if hovered else C.TETRIS_PANEL_DARK, rect.inflate(-5, -5))
        pygame.draw.rect(self.screen, C.TETRIS_ACCENT_LIGHT if hovered else C.TETRIS_ACCENT, rect.inflate(-12, -12), 2)
        label = render_pixel_text(self.font_btn, button["label"], C.TETRIS_TEXT, scale=2)
        self.screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    def _draw_tetris_block(self, x, y, color, size=TETRIS_CELL, ghost=False, surface=None):
        target = surface or self.screen
        rect = pygame.Rect(x, y, size, size)
        if ghost:
            pygame.draw.rect(target, C.TETRIS_GHOST, rect.inflate(-3, -3), 2)
            return
        pygame.draw.rect(target, C.OUTLINE, rect)
        pygame.draw.rect(target, color, rect.inflate(-3, -3))
        light = tuple(min(255, value + 38) for value in color)
        dark = tuple(max(0, value - 42) for value in color)
        pygame.draw.rect(target, light, (rect.x + 4, rect.y + 4, rect.width - 8, 3))
        pygame.draw.rect(target, dark, (rect.x + 4, rect.bottom - 7, rect.width - 8, 3))

    def _draw_tetris_menu(self):
        if self._check_and_show_prologue("tetris"):
            self._draw_prologue_screen()
            return

        self._draw_tetris_background()
        panel = pygame.Rect(100, 54, WINDOW_W - 200, WINDOW_H - 108)
        self._draw_tetris_panel(panel)
        title = render_pixel_text(self.font_menu_title, "TETRIS", C.TETRIS_ACCENT_LIGHT, scale=5)
        subtitle_text = "俄罗斯方块 · 经典落块街机" if is_chinese() else "FALLING BLOCK ARCADE"
        subtitle = render_pixel_text(self.font_small, subtitle_text, C.TETRIS_TEXT, scale=2)
        self.screen.blit(title, (panel.x + 90, panel.y + 68))
        self.screen.blit(subtitle, (panel.x + 94, panel.y + 164))
        preview = pygame.Surface((330, 380), pygame.SRCALPHA)
        preview.fill((*C.TETRIS_BOARD, 205))
        cell = 18
        ox, oy = 75, 10
        for row in range(20):
            for col in range(10):
                kind = self.tetris_preview_grid[row][col]
                if kind:
                    self._draw_tetris_block(ox + col * cell, oy + row * cell, PIECE_COLORS[kind], cell, surface=preview)
        piece = self.tetris_preview_piece
        if piece:
            for dx, dy in PIECE_SHAPES[piece["kind"]][piece["rotation"]]:
                row, col = piece["y"] + dy, piece["x"] + dx
                if row >= 0:
                    self._draw_tetris_block(ox + col * cell, oy + row * cell, PIECE_COLORS[piece["kind"]], cell, surface=preview)
        if self.tetris_preview_gameover:
            progress = min(1.0, self.tetris_preview_gameover_frame / 24)
            overlay = pygame.Surface(preview.get_size(), pygame.SRCALPHA)
            overlay.fill((18, 8, 12, int(165 * progress)))
            preview.blit(overlay, (0, 0))
            gameover = render_pixel_text(self.font_small, "GAME OVER", C.TETRIS_ACCENT_LIGHT, scale=2)
            gameover.set_alpha(int(255 * progress))
            preview.blit(
                gameover,
                (
                    preview.get_width() // 2 - gameover.get_width() // 2,
                    preview.get_height() // 2 - gameover.get_height() // 2,
                ),
            )
        preview.set_alpha(175)
        softened = pygame.transform.smoothscale(preview, (165, 190))
        softened = pygame.transform.smoothscale(softened, preview.get_size())
        self.screen.blit(softened, (panel.x + 70, panel.y + 190))
        controls = ["ARROWS / WASD  MOVE", "UP / W  ROTATE", "SPACE  HARD DROP", "C  HOLD", "P  PAUSE"]
        for index, line in enumerate(controls):
            text = render_pixel_text(self.font_small, line, C.TETRIS_MUTED, scale=2)
            self.screen.blit(text, (780, 190 + index * 34))
        mouse_pos = self._logical_mouse_pos()
        for button in self._get_tetris_menu_buttons():
            self._draw_tetris_button(
                button,
                button["rect"].collidepoint(mouse_pos),
                self.tetris_pressed_action == button["action"],
            )

    def _draw_tetris_game(self):
        self._draw_tetris_background()
        outer = pygame.Rect(48, 34, WINDOW_W - 96, WINDOW_H - 68)
        self._draw_tetris_panel(outer)
        board = pygame.Rect(TETRIS_BOARD_X, TETRIS_BOARD_Y, TETRIS_BOARD_W, TETRIS_BOARD_H)
        pygame.draw.rect(self.screen, C.OUTLINE, board.inflate(12, 12))
        pygame.draw.rect(self.screen, C.TETRIS_BOARD, board)
        for row in range(TETRIS_VISIBLE_ROWS):
            for col in range(TETRIS_COLS):
                rect = pygame.Rect(TETRIS_BOARD_X + col * TETRIS_CELL, TETRIS_BOARD_Y + row * TETRIS_CELL, TETRIS_CELL, TETRIS_CELL)
                pygame.draw.rect(self.screen, C.TETRIS_GRID, rect, 1)
                kind = self.tetris_grid[row + TETRIS_HIDDEN_ROWS][col]
                if kind:
                    self._draw_tetris_block(rect.x, rect.y, PIECE_COLORS[kind])
        if self.tetris_current:
            ghost_y = self._tetris_ghost_y()
            for col, row in self._tetris_cells(self.tetris_current, y=ghost_y):
                visible_row = row - TETRIS_HIDDEN_ROWS
                if visible_row >= 0:
                    self._draw_tetris_block(TETRIS_BOARD_X + col * TETRIS_CELL, TETRIS_BOARD_Y + visible_row * TETRIS_CELL, C.TETRIS_GHOST, ghost=True)
            for col, row in self._tetris_cells(self.tetris_current):
                visible_row = row - TETRIS_HIDDEN_ROWS
                if visible_row >= 0:
                    self._draw_tetris_block(TETRIS_BOARD_X + col * TETRIS_CELL, TETRIS_BOARD_Y + visible_row * TETRIS_CELL, PIECE_COLORS[self.tetris_current["kind"]])
        for flash in self.tetris_clear_flash:
            visible_row = flash["row"] - TETRIS_HIDDEN_ROWS
            if visible_row >= 0:
                alpha = int(210 * flash["life"] / 18)
                surface = pygame.Surface((TETRIS_BOARD_W, TETRIS_CELL), pygame.SRCALPHA)
                surface.fill((*C.TETRIS_ACCENT_LIGHT, alpha))
                self.screen.blit(surface, (TETRIS_BOARD_X, TETRIS_BOARD_Y + visible_row * TETRIS_CELL))
        for particle in self.tetris_particles:
            pygame.draw.rect(self.screen, particle["color"], (int(particle["x"]), int(particle["y"]), 4, 4))
        self._draw_tetris_game_sidebars()
        if self.tetris_paused:
            shade = pygame.Surface((TETRIS_BOARD_W, TETRIS_BOARD_H), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 175))
            self.screen.blit(shade, board)
            text = render_pixel_text(self.font_menu_title, "PAUSED", C.TETRIS_ACCENT_LIGHT, scale=3)
            self.screen.blit(text, (board.centerx - text.get_width() // 2, board.centery - text.get_height() // 2))

    def _draw_tetris_game_sidebars(self):
        left = pygame.Rect(78, 108, 290, 500)
        right = pygame.Rect(722, 108, 480, 500)
        self._draw_tetris_panel(left)
        self._draw_tetris_panel(right)
        title = render_pixel_text(self.font_menu_title, "TETRIS", C.TETRIS_ACCENT_LIGHT, scale=3)
        self.screen.blit(title, (left.centerx - title.get_width() // 2, left.y + 46))
        values = (("SCORE", self.tetris_score), ("LINES", self.tetris_lines), ("LEVEL", self.tetris_level))
        for index, (label, value) in enumerate(values):
            label_s = render_pixel_text(self.font_small, label, C.TETRIS_MUTED, scale=2)
            value_s = render_pixel_text(self.font_status, str(value), C.TETRIS_TEXT, scale=3)
            y = left.y + 150 + index * 92
            self.screen.blit(label_s, (left.centerx - label_s.get_width() // 2, y))
            self.screen.blit(value_s, (left.centerx - value_s.get_width() // 2, y + 30))
        mouse_pos = self._logical_mouse_pos()
        for button in self._get_tetris_play_buttons():
            self._draw_tetris_button(
                button,
                button["rect"].collidepoint(mouse_pos),
                self.tetris_pressed_action == button["action"],
            )
        self._draw_tetris_piece_card(right.x + 36, right.y + 48, "NEXT", self.tetris_next)
        self._draw_tetris_piece_card(right.x + 264, right.y + 48, "HOLD", self.tetris_hold)
        controls = ["MOVE  ARROWS / WASD", "ROTATE  UP / W / Z", "DROP  SPACE", "HOLD  C", "PAUSE  P", "RESTART  R", "MENU  ESC"]
        for index, line in enumerate(controls):
            text = render_pixel_text(self.font_small, line, C.TETRIS_MUTED, scale=2)
            self.screen.blit(text, (right.x + 46, right.y + 245 + index * 31))

    def _draw_tetris_piece_card(self, x, y, label, kind):
        rect = pygame.Rect(x, y, 180, 150)
        pygame.draw.rect(self.screen, C.OUTLINE, rect)
        pygame.draw.rect(self.screen, C.TETRIS_BOARD, rect.inflate(-5, -5))
        pygame.draw.rect(self.screen, C.TETRIS_ACCENT, rect.inflate(-12, -12), 1)
        text = render_pixel_text(self.font_small, label, C.TETRIS_ACCENT_LIGHT, scale=2)
        self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.y + 15))
        if not kind:
            return
        cells = PIECE_SHAPES[kind][0]
        min_x = min(x for x, _ in cells)
        max_x = max(x for x, _ in cells)
        min_y = min(y for _, y in cells)
        max_y = max(y for _, y in cells)
        size = 22
        width = (max_x - min_x + 1) * size
        height = (max_y - min_y + 1) * size
        ox = rect.centerx - width // 2 - min_x * size
        oy = rect.y + 90 - height // 2 - min_y * size
        for dx, dy in cells:
            self._draw_tetris_block(ox + dx * size, oy + dy * size, PIECE_COLORS[kind], size)

    def _draw_tetris_end(self):
        self._draw_tetris_game()
        shade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 170))
        self.screen.blit(shade, (0, 0))
        t = min(1.0, self.tetris_end_frame / max(1, TETRIS_END_POP_FRAMES))
        scale = max(0.01, min(1.08, ease_out_back(t)))
        target = pygame.Rect(WINDOW_W // 2 - 310, WINDOW_H // 2 - 190, 620, 380)
        panel = pygame.Rect(0, 0, int(target.width * scale), int(target.height * scale))
        panel.center = target.center
        self._draw_tetris_panel(panel)
        if t < 0.42:
            return
        title = render_pixel_text(self.font_menu_title, "GAME OVER", C.TETRIS_ACCENT_LIGHT, scale=3)
        score = render_pixel_text(self.font_status, f"SCORE {self.tetris_score}", C.TETRIS_TEXT, scale=3)
        stats = render_pixel_text(self.font_small, f"LINES {self.tetris_lines}   LEVEL {self.tetris_level}", C.TETRIS_MUTED, scale=2)
        self.screen.blit(title, (target.centerx - title.get_width() // 2, target.y + 54))
        self.screen.blit(score, (target.centerx - score.get_width() // 2, target.y + 132))
        self.screen.blit(stats, (target.centerx - stats.get_width() // 2, target.y + 188))
        mouse_pos = self._logical_mouse_pos()
        for button in self._get_tetris_end_buttons():
            self._draw_tetris_button(
                button,
                button["rect"].collidepoint(mouse_pos),
                self.tetris_pressed_action == button["action"],
            )
