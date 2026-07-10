from .common import *


class TransitionMixin:
    def _init_transition(self):
        self.transition_active = False
        self.transition_type = "fade"
        self.transition_target_state = None
        self.transition_frame = 0
        self.transition_max_frames = 24
        self.transition_phase = "out"
        self.transition_alpha = 0
        self.current_game_id = "gomoku"
        self.current_game_name = "GOMOKU"
        self._desktop_return_effect = "fade"

    def _select_game(self, game_id):
        """Switch current game for the future game hub."""
        for game in GAME_LIBRARY:
            if game["id"] == game_id:
                self.current_game_id = game["id"]
                self.current_game_name = game["name"]

                if game_id == "gomoku":
                    self.board_size = game.get("default_board_size", DEFAULT_SIZE)
                    self.board = Board(self.board_size)
                    self._rebuild_stone_assets()

                self.state = self.MENU
                return

    def _start_transition(self, target_state, transition_type="fade", frames=32):
        if self.transition_active or target_state == self.state: return
        if getattr(self, "animation_level", "full") == "reduced":
            frames = max(8, frames // 2)
        elif getattr(self, "animation_level", "full") == "off":
            frames = 6
        self.transition_active = True; self.transition_type = transition_type
        self.transition_target_state = target_state; self.transition_frame = 0
        self.transition_max_frames = max(6, frames); self.transition_phase = "out"; self.transition_alpha = 0

    def _update_transition(self):
        if not self.transition_active: return
        self.transition_frame += 1
        half = max(1, self.transition_max_frames // 2)
        if self.transition_phase == "out":
            t = min(1.0, self.transition_frame / half); self.transition_alpha = int(255 * t)
            if self.transition_frame >= half:
                if self.transition_target_state is not None: self.state = self.transition_target_state
                self.transition_phase = "in"; self.transition_frame = 0
        elif self.transition_phase == "in":
            t = min(1.0, self.transition_frame / half); self.transition_alpha = int(255 * (1.0 - t))
            if self.transition_frame >= half:
                self.transition_active = False; self.transition_target_state = None
                self.transition_frame = 0; self.transition_alpha = 0; self.transition_phase = "out"

    def _draw_transition_overlay(self):
        if not self.transition_active: return
        if self.transition_type == "fade": self._draw_transition_fade()
        elif self.transition_type == "gomoku_grid": self._draw_transition_gomoku_grid()
        elif self.transition_type == "snake_scan": self._draw_transition_snake_scan()
        elif self.transition_type == "g2048_tiles": self._draw_transition_2048_tiles()
        elif self.transition_type == "breakout_bricks": self._draw_transition_breakout_bricks()
        elif self.transition_type == "mines_radar": self._draw_transition_mines_radar()
        elif self.transition_type == "tetris_drop": self._draw_transition_tetris_drop()
        elif self.transition_type == "air_sweep":
            self._draw_transition_arcade()
        elif self.transition_type == "system_unlock": self._draw_transition_system_unlock()
        else: self._draw_transition_fade()

    def _draw_transition_fade(self):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.transition_alpha)); self.screen.blit(overlay, (0, 0))

    def _draw_transition_arcade(self):
        half = max(1, self.transition_max_frames // 2)
        t = min(1.0, self.transition_frame / half)
        if self.transition_phase == "in":
            t = 1.0 - t

        # Dark overlay
        shade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        shade.fill((4, 11, 26, int(200 * t)))
        self.screen.blit(shade, (0, 0))

        # Expanding radar rings from center
        cx, cy = WINDOW_W // 2, WINDOW_H // 2
        max_radius = int(math.hypot(WINDOW_W, WINDOW_H) * 0.6)
        for ring in range(3):
            delay = ring * 0.12
            ring_t = min(1.0, max(0.0, (t - delay) / (1.0 - delay)))
            radius = int(max_radius * ring_t)
            alpha = int(140 * ring_t)
            if alpha > 0:
                pygame.draw.circle(self.screen, (55, 180, 225, alpha), (cx, cy), radius, 2)

        # Bullet curtain — horizontal streams from both sides
        rng = random.Random(91)
        bullet_t = min(1.0, t * 1.3)
        for row in range(24):
            y = 30 + row * 29 + rng.randint(-4, 4)
            for col in range(22):
                base_x = col * 58 + rng.randint(-8, 8)
                offset = rng.randint(0, 58)
                x = (base_x + offset + int(bullet_t * 700)) % (WINDOW_W + 80) - 40
                if 20 < x < WINDOW_W - 20:
                    alpha = int(180 * bullet_t * rng.uniform(0.5, 1.0))
                    color = (255, 218, 92, alpha) if rng.random() < 0.6 else (120, 245, 215, alpha)
                    pygame.draw.rect(self.screen, color, (x, y, 4, 4))
                    pygame.draw.rect(self.screen, (255, 255, 255, alpha // 3), (x + 1, y + 1, 2, 2))

    def _draw_transition_system_unlock(self):
        half = max(1, self.transition_max_frames // 2)
        t = min(1.0, self.transition_frame / half)
        if self.transition_phase == "in":
            t = 1.0 - t
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((*C.DESK_PANEL_DARK, int(210 * t)))
        self.screen.blit(overlay, (0, 0))
        for index in range(12):
            width = int(WINDOW_W * max(0.0, min(1.0, t - index * 0.035)))
            y = WINDOW_H // 2 - 132 + index * 24
            pygame.draw.rect(self.screen, C.DESK_ACCENT, (WINDOW_W // 2 - width // 2, y, width, 3))
        ring = int(180 * t)
        if ring > 0:
            pygame.draw.rect(
                self.screen,
                C.DESK_ACCENT_LIGHT,
                (WINDOW_W // 2 - ring, WINDOW_H // 2 - ring // 2, ring * 2, ring),
                3,
            )

    def _draw_transition_tetris_drop(self):
        half = max(1, self.transition_max_frames // 2)
        t = min(1.0, self.transition_frame / half)
        if self.transition_phase == "in":
            t = 1.0 - t
        shade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        shade.fill((*C.TETRIS_BG, int(175 * t)))
        self.screen.blit(shade, (0, 0))
        colors = [C.TETRIS_I, C.TETRIS_O, C.TETRIS_T, C.TETRIS_S, C.TETRIS_Z, C.TETRIS_J, C.TETRIS_L]
        rng = random.Random(425)
        for index in range(42):
            delay = (index % 9) * 0.035
            local = max(0.0, min(1.0, (t - delay) / 0.7))
            if local <= 0:
                continue
            size = 30
            x = rng.randrange(-20, WINDOW_W)
            target_y = rng.randrange(WINDOW_H // 3, WINDOW_H + 60)
            y = int(-100 - (index % 5) * 35 + (target_y + 160) * (1 - (1 - local) ** 3))
            angle = int(local * 3) % 4
            offsets = [(0, 0), (1, 0), (0, 1), (1, 1)] if index % 3 == 0 else [(0, 0), (1, 0), (2, 0), (2, 1)]
            for ox, oy in offsets:
                px = x + (oy if angle % 2 else ox) * size
                py = y + (ox if angle % 2 else oy) * size
                rect = pygame.Rect(px, py, size, size)
                pygame.draw.rect(self.screen, C.OUTLINE, rect)
                pygame.draw.rect(self.screen, colors[index % len(colors)], rect.inflate(-4, -4))

    def _draw_transition_gomoku_grid(self):
        cols = 16; rows = 9; cw = math.ceil(WINDOW_W / cols); ch = math.ceil(WINDOW_H / rows)
        half = max(1, self.transition_max_frames // 2)
        t = min(1.0, self.transition_frame / half) if self.transition_phase == "out" else 1.0 - min(1.0, self.transition_frame / half)
        md = cols + rows - 2
        for r in range(rows):
            for c in range(cols):
                d = (r + c) / md * 0.45; lt = max(0.0, min(1.0, (t - d) / 0.55))
                if lt <= 0: continue
                ss = max(0.0, min(1.15, ease_out_back(lt))); w = int(cw * ss); h = int(ch * ss)
                x = c * cw + cw // 2 - w // 2; y = r * ch + ch // 2 - h // 2
                rect = pygame.Rect(x, y, w + 2, h + 2)
                color = C.BOARD if (r + c) % 2 == 0 else C.BOARD_EDGE
                pygame.draw.rect(self.screen, C.OUTLINE, rect); pygame.draw.rect(self.screen, color, rect.inflate(-4, -4))

    def _draw_transition_snake_scan(self):
        half = max(1, self.transition_max_frames // 2)
        t = min(1.0, self.transition_frame / half) if self.transition_phase == "out" else 1.0 - min(1.0, self.transition_frame / half)
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(135 * t))); self.screen.blit(overlay, (0, 0))
        cell = 28; cols = WINDOW_W // cell + 4; rows = WINDOW_H // cell + 4
        path = []
        for r in range(rows):
            if r % 2 == 0:
                for c in range(cols): path.append((r, c))
            else:
                for c in range(cols - 1, -1, -1): path.append((r, c))
        rc = int(len(path) * t); sl = int(18 + 46 * t)
        si = max(0, rc - sl); snake_body = path[si:rc]
        fc = max(0, rc - sl // 2); filled = path[:fc]
        for r, c in filled:
            x = c * cell - cell; y = r * cell - cell
            if x > WINDOW_W or y > WINDOW_H: continue
            pygame.draw.rect(self.screen, C.SNAKE_PANEL_DARK, (x, y, cell, cell))
            pygame.draw.rect(self.screen, C.SNAKE_GRID_DARK, (x + 2, y + 2, cell - 4, cell - 4), 1)
        for i, (r, c) in enumerate(snake_body):
            x = c * cell - cell; y = r * cell - cell
            if x > WINDOW_W or y > WINDOW_H: continue
            ratio = i / max(1, len(snake_body) - 1)
            col = C.SNAKE_HEAD if ratio > 0.82 else (C.SNAKE_BODY if ratio > 0.55 else C.SNAKE_SHADOW)
            rect = pygame.Rect(x, y, cell, cell)
            pygame.draw.rect(self.screen, C.OUTLINE, rect); pygame.draw.rect(self.screen, col, rect.inflate(-4, -4))
            if i % 3 == 0: pygame.draw.rect(self.screen, C.SNAKE_ACCENT_LIGHT, (rect.x + 6, rect.y + 6, max(3, cell // 4), max(3, cell // 4)))
        if snake_body:
            hr, hc = snake_body[-1]; hx = hc * cell - cell; hy = hr * cell - cell
            head_rect = pygame.Rect(hx, hy, cell, cell)
            pygame.draw.rect(self.screen, C.OUTLINE, head_rect.inflate(6, 6))
            pygame.draw.rect(self.screen, C.SNAKE_HEAD, head_rect.inflate(1, 1))
            e_off = 5 if hr % 2 == 0 else -5
            for ey in [-6, 6]: pygame.draw.rect(self.screen, C.OUTLINE, (head_rect.centerx + e_off - 2, head_rect.centery + ey - 2, 4, 4))
        if t > 0.78:
            ft = (t - 0.78) / 0.22; fa = int(210 * ft)
            fo = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            fo.fill((*C.SNAKE_PANEL_DARK, fa)); self.screen.blit(fo, (0, 0))
            ga = int(120 * ft); gs = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            for x in range(0, WINDOW_W, cell): pygame.draw.line(gs, (*C.SNAKE_GRID, ga), (x, 0), (x, WINDOW_H), 1)
            for y in range(0, WINDOW_H, cell): pygame.draw.line(gs, (*C.SNAKE_GRID_DARK, ga), (0, y), (WINDOW_W, y), 1)
            self.screen.blit(gs, (0, 0))

    def _draw_transition_2048_tiles(self):
        tile = 80; cols = math.ceil(WINDOW_W / tile); rows = math.ceil(WINDOW_H / tile)
        half = max(1, self.transition_max_frames // 2)
        t = min(1.0, self.transition_frame / half) if self.transition_phase == "out" else 1.0 - min(1.0, self.transition_frame / half)
        cr = rows / 2; cc = cols / 2; md = math.sqrt(cr ** 2 + cc ** 2)
        colors = [C.G2048_TILE_2, C.G2048_TILE_4, C.G2048_TILE_8, C.G2048_TILE_16, C.G2048_TILE_32, C.G2048_TILE_64]
        for r in range(rows):
            for c in range(cols):
                dist = math.sqrt((r - cr) ** 2 + (c - cc) ** 2)
                d = (dist / md) * 0.42; lt = max(0.0, min(1.0, (t - d) / 0.58))
                if lt <= 0: continue
                ss = max(0.0, min(1.1, ease_out_back(lt))); w = int(tile * ss); h = int(tile * ss)
                x = c * tile + tile // 2 - w // 2; y = r * tile + tile // 2 - h // 2
                rect = pygame.Rect(x, y, w, h)
                pygame.draw.rect(self.screen, C.OUTLINE, rect)
                pygame.draw.rect(self.screen, colors[(r + c) % len(colors)], rect.inflate(-6, -6))

    def _draw_transition_breakout_bricks(self):
        bw = 86; bh = 34; gap = 6
        cols = math.ceil(WINDOW_W / (bw + gap)) + 2; rows = math.ceil(WINDOW_H / (bh + gap)) + 2
        half = max(1, self.transition_max_frames // 2)
        t = min(1.0, self.transition_frame / half) if self.transition_phase == "out" else 1.0 - min(1.0, self.transition_frame / half)
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(115 * t))); self.screen.blit(overlay, (0, 0))
        colors = [C.BREAKOUT_BRICK_PURPLE, C.BREAKOUT_BRICK_ORANGE, C.BREAKOUT_BRICK_BLUE, C.BREAKOUT_ACCENT, C.BREAKOUT_ACCENT_LIGHT]
        md = rows + cols - 2
        for r in range(rows):
            for c in range(cols):
                d = (r * 0.75 + c * 0.18) / md * 0.42; lt = max(0.0, min(1.0, (t - d) / 0.58))
                if lt <= 0: continue
                drop = max(0.0, min(1.15, ease_out_back(lt)))
                x = c * (bw + gap) - bw // 2; y = int(-120 + ((r * (bh + gap) - bh // 2) + 120) * drop)
                rect = pygame.Rect(x, y, bw, bh); col = colors[(r + c) % len(colors)]
                pygame.draw.rect(self.screen, C.OUTLINE, rect); pygame.draw.rect(self.screen, col, rect.inflate(-4, -4))
                pygame.draw.line(self.screen, C.BREAKOUT_ACCENT_LIGHT, (rect.x + 8, rect.y + 7), (rect.right - 8, rect.y + 7), 2)
        if t > 0.18:
            bt = min(1.0, (t - 0.18) / 0.82); bx = int(WINDOW_W * bt); by = int(WINDOW_H * 0.35 + math.sin(bt * math.tau * 2.5) * 120)
            pygame.draw.circle(self.screen, C.OUTLINE, (bx, by), 18); pygame.draw.circle(self.screen, C.BREAKOUT_BALL_YELLOW, (bx, by), 14)
            pygame.draw.circle(self.screen, C.BREAKOUT_ACCENT_LIGHT, (bx - 5, by - 5), 4)

    def _draw_transition_mines_radar(self):
        half = max(1, self.transition_max_frames // 2)
        t = min(1.0, self.transition_frame / half) if self.transition_phase == "out" else 1.0 - min(1.0, self.transition_frame / half)
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((*C.MINES_PANEL_DARK, int(190 * t))); self.screen.blit(overlay, (0, 0))
        smoke = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA); rng = random.Random(2026)
        for i in range(int(90 * t)):
            x = rng.randint(-80, WINDOW_W + 40); y = rng.randint(-60, WINDOW_H + 40)
            drift = int(math.sin(self.anim_tick * 0.03 + i) * 18)
            size = rng.randint(28, 86); alpha = rng.randint(18, 48)
            color = C.MINES_PANEL if i % 2 == 0 else C.MINES_BOARD
            pygame.draw.rect(smoke, (*color, alpha), (x + drift, y, size, size // 2))
        self.screen.blit(smoke, (0, 0))
        cx = WINDOW_W // 2; cy = WINDOW_H // 2
        mr = int(math.sqrt(WINDOW_W ** 2 + WINDOW_H ** 2) * 0.58); rad = int(mr * t)
        for i in range(4):
            rr = int(rad * (0.35 + i * 0.22))
            if rr <= 0: continue
            alpha = max(0, int(150 * t * (1 - i * 0.16)))
            ring = pygame.Surface((rr * 2 + 8, rr * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*C.MINES_ACCENT_LIGHT, alpha), (ring.get_width() // 2, ring.get_height() // 2), rr, 3)
            self.screen.blit(ring, (cx - ring.get_width() // 2, cy - ring.get_height() // 2))
        sa = self.anim_tick * 0.08; sl = mr
        for i in range(18):
            a = sa - i * 0.035; alpha = int(150 * t * (1 - i / 18))
            ex = cx + math.cos(a) * sl * t; ey = cy + math.sin(a) * sl * t
            ls = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            pygame.draw.line(ls, (*C.MINES_ACCENT_LIGHT, alpha), (cx, cy), (int(ex), int(ey)), 3)
            self.screen.blit(ls, (0, 0))
        for idx, (px, py) in enumerate([(0.22, 0.28), (0.74, 0.24), (0.38, 0.46), (0.62, 0.55), (0.18, 0.70), (0.82, 0.76), (0.50, 0.82)]):
            at = max(0.0, min(1.0, (t - idx * 0.06) / 0.45))
            if at <= 0: continue
            x = int(WINDOW_W * px); y = int(WINDOW_H * py)
            blink = (self.anim_tick // 6 + idx) % 2 == 0
            col = C.MINES_MINE_RED if blink else C.MINES_ACCENT_LIGHT
            sz = int(10 + 14 * at)
            pygame.draw.rect(self.screen, C.OUTLINE, (x - sz // 2, y - sz // 2, sz, sz))
            pygame.draw.rect(self.screen, col, (x - sz // 2 + 3, y - sz // 2 + 3, sz - 6, sz - 6))
            if blink: pygame.draw.rect(self.screen, C.MINES_FLAG, (x - sz, y - sz, sz * 2, sz * 2), 2)

    def _go_desktop(self):
        """Return to desktop UI with the game's entry transition effect."""
        system_states = {
            getattr(self, "SYSTEM_SETTINGS", None),
            getattr(self, "PROFILE", None),
            getattr(self, "ACHIEVEMENT_WALL", None),
            getattr(self, "LORE_READER", None),
            getattr(self, "LORE_STORY", None),
        }
        transition_type = "fade" if self.state in system_states else self._desktop_return_effect
        self.animations.clear()
        self.particles.clear()
        self.ripples.clear()
        if hasattr(self, "invalid_marks"): self.invalid_marks.clear()
        if hasattr(self, "undo_animations"): self.undo_animations.clear()
        self.shake_duration = 0
        self.preview_active = False; self.preview_cell = None
        self.occupied_hover_pos = None
        self.pressed_button_action = None; self.desktop_pressed_action = None
        self.desktop_esc_lock_frames = 15
        self._start_transition(self.DESKTOP, transition_type)
