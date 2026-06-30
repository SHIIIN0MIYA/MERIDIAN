from .common import *


class Game2048Mixin:
    def _get_2048_menu_buttons(self):
        cx = WINDOW_W // 2; btn_w = 220; btn_h = 50; gap = 22; start_y = 365
        return [
            {"rect": pygame.Rect(cx - btn_w // 2, start_y, btn_w, btn_h), "label": "START", "action": "g2048_start", "selected": False},
            {"rect": pygame.Rect(cx - btn_w // 2, start_y + btn_h + gap, btn_w, btn_h), "label": "DESKTOP", "action": "desktop", "selected": False},
        ]

    def _get_2048_end_buttons(self):
        btn_w = 210; btn_h = 44; gap = 14
        panel_w = 560; panel_h = 430
        panel = pygame.Rect(WINDOW_W // 2 - panel_w // 2, WINDOW_H // 2 - panel_h // 2, panel_w, panel_h)
        x = panel.centerx - btn_w // 2; start_y = panel.y + 244
        buttons = [
            {"rect": pygame.Rect(x, start_y, btn_w, btn_h), "label": "PLAY AGAIN", "action": "again", "selected": False},
            {"rect": pygame.Rect(x, start_y + btn_h + gap, btn_w, btn_h), "label": "MENU", "action": "menu", "selected": False},
            {"rect": pygame.Rect(x, start_y + (btn_h + gap) * 2, btn_w, btn_h), "label": "DESKTOP", "action": "desktop", "selected": False},
        ]
        if self.g2048_won and not self.g2048_game_over:
            buttons.insert(1, {"rect": pygame.Rect(x, start_y + btn_h + gap, btn_w, btn_h), "label": "CONTINUE", "action": "continue", "selected": False})
            for i, b in enumerate(buttons): b["rect"].y = start_y + i * (btn_h + gap)
        return buttons

    def _draw_2048_button(self, button, hovered=False, pressed=False):
        rect = button["rect"].copy(); selected = button.get("selected", False)
        if hovered: rect = rect.inflate(10, 8)
        if pressed: rect.y += 4
        shade = 6 if hovered else 4
        pygame.draw.rect(self.screen, C.OUTLINE, rect.move(shade, shade))
        if selected: fill, inner, tc = C.G2048_ACCENT, C.G2048_ACCENT_LIGHT, C.OUTLINE
        elif hovered: fill, inner, tc = C.G2048_PANEL, C.G2048_ACCENT_LIGHT, C.G2048_TEXT
        else: fill, inner, tc = C.G2048_PANEL_DARK, C.G2048_ACCENT, C.G2048_TEXT
        pygame.draw.rect(self.screen, C.OUTLINE, rect); pygame.draw.rect(self.screen, fill, rect.inflate(-5, -5))
        pygame.draw.rect(self.screen, inner, rect.inflate(-12, -12), 2)
        if hovered: pygame.draw.rect(self.screen, C.G2048_ACCENT_LIGHT, (rect.x + 10, rect.y + 8, rect.width - 20, 4))
        label = render_pixel_text(self.font_btn, button["label"], tc, scale=2)
        if label.get_width() > rect.width - 24: label = render_pixel_text(self.font_btn, button["label"], tc, scale=1)
        lx, ly = rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2
        if hovered and not pressed: ly -= 1
        self.screen.blit(label, (lx, ly))

    def _get_2048_tile_color(self, value):
        table = {2: C.G2048_TILE_2, 4: C.G2048_TILE_4, 8: C.G2048_TILE_8, 16: C.G2048_TILE_16, 32: C.G2048_TILE_32,
                 64: C.G2048_TILE_64, 128: C.G2048_TILE_128, 256: C.G2048_TILE_256, 512: C.G2048_TILE_512,
                 1024: C.G2048_TILE_1024, 2048: C.G2048_TILE_2048}
        return table.get(value, C.G2048_TILE_2048)

    def _get_2048_cell_rect(self, r, c, board_offset_x=0, board_offset_y=0):
        """返回 2048 棋盘中某个格子的矩形区域。board_offset 用于无效移动抖动。"""
        board_rect = pygame.Rect(G2048_X + board_offset_x, G2048_Y + board_offset_y, G2048_BOARD_PX, G2048_BOARD_PX)
        x = board_rect.x + G2048_GAP + c * (G2048_CELL + G2048_GAP)
        y = board_rect.y + G2048_GAP + r * (G2048_CELL + G2048_GAP)
        return pygame.Rect(x, y, G2048_CELL, G2048_CELL)

    def _spawn_2048_particles(self, r, c, value, count=14):
        """2048 方块合并时生成像素粒子。"""
        cell_rect = self._get_2048_cell_rect(r, c)
        color = self._get_2048_tile_color(value)
        for _ in range(count):
            life = random.randint(G2048_PARTICLE_LIFE_MIN, G2048_PARTICLE_LIFE_MAX)
            self.g2048_particles.append({
                "x": cell_rect.centerx, "y": cell_rect.centery,
                "vx": random.uniform(-2.2, 2.2), "vy": random.uniform(-2.4, 1.2),
                "life": life, "max_life": life, "color": color, "size": random.randint(3, 6),
            })

    def _build_2048_slide_anims(self, old_grid, new_grid, direction):
        """根据移动前后棋盘生成 2048 方块滑行动画。"""
        self.g2048_slide_anims.clear()
        if direction in ["left", "right"]:
            for r in range(G2048_SIZE):
                oc = [(c, old_grid[r][c]) for c in range(G2048_SIZE) if old_grid[r][c] != 0]
                nc = [(c, new_grid[r][c]) for c in range(G2048_SIZE) if new_grid[r][c] != 0]
                if direction == "right": oc = list(reversed(oc)); nc = list(reversed(nc))
                for i in range(min(len(oc), len(nc))):
                    if oc[i][0] != nc[i][0]:
                        self.g2048_slide_anims.append({"from_r": r, "from_c": oc[i][0], "to_r": r, "to_c": nc[i][0],
                                                         "value": oc[i][1], "frame": 0, "max_frames": G2048_SLIDE_FRAMES})
        else:
            for c in range(G2048_SIZE):
                oc = [(r, old_grid[r][c]) for r in range(G2048_SIZE) if old_grid[r][c] != 0]
                nc = [(r, new_grid[r][c]) for r in range(G2048_SIZE) if new_grid[r][c] != 0]
                if direction == "down": oc = list(reversed(oc)); nc = list(reversed(nc))
                for i in range(min(len(oc), len(nc))):
                    if oc[i][0] != nc[i][0]:
                        self.g2048_slide_anims.append({"from_r": oc[i][0], "from_c": c, "to_r": nc[i][0], "to_c": c,
                                                         "value": oc[i][1], "frame": 0, "max_frames": G2048_SLIDE_FRAMES})

    def _start_2048_game(self):
        self.g2048_grid = [[0]*G2048_SIZE for _ in range(G2048_SIZE)]
        self.g2048_score = 0; self.g2048_moves = 0; self.g2048_won = False; self.g2048_game_over = False
        self.g2048_spawn_anims.clear(); self.g2048_merge_anims.clear(); self.g2048_slide_anims.clear()
        self.g2048_score_floaters.clear(); self.g2048_particles.clear()
        self.g2048_invalid_shake = 0; self.g2048_invalid_shake_dir = "x"
        self.g2048_end_panel_frame = 0; self.g2048_win_flash_frame = 0; self.g2048_pressed_action = None
        self._spawn_2048_tile(); self._spawn_2048_tile()
        self.state = self.G2048_PLAYING
        self.g2048_stats_completed = False
        self._record_stat("2048", "games_started")

    def _spawn_2048_tile(self):
        empty = [(r, c) for r in range(G2048_SIZE) for c in range(G2048_SIZE) if self.g2048_grid[r][c] == 0]
        if not empty: return False
        r, c = random.choice(empty); value = 4 if random.random() < 0.10 else 2
        self.g2048_grid[r][c] = value
        self.g2048_spawn_anims.append({"r": r, "c": c, "frame": 0, "max_frames": G2048_POP_FRAMES})
        return True

    def _compress_2048_line(self, line):
        nums = [v for v in line if v != 0]; result = []; gained = 0; merge_indices = []; i = 0
        while i < len(nums):
            if i + 1 < len(nums) and nums[i] == nums[i + 1]:
                merged = nums[i] * 2; result.append(merged); gained += merged; merge_indices.append(len(result) - 1); i += 2
            else: result.append(nums[i]); i += 1
        while len(result) < G2048_SIZE: result.append(0)
        return result, gained, merge_indices

    def _move_2048(self, direction):
        old_grid = [row[:] for row in self.g2048_grid]; total_gain = 0; all_merge_cells = []
        if direction in ["left", "right", "up", "down"]:
            for idx in range(G2048_SIZE):
                if direction == "left": line = self.g2048_grid[idx]; rev = False
                elif direction == "right": line = list(reversed(self.g2048_grid[idx])); rev = True
                elif direction == "up": line = [self.g2048_grid[r][idx] for r in range(G2048_SIZE)]; rev = False
                else: line = [self.g2048_grid[r][idx] for r in range(G2048_SIZE)]; line = list(reversed(line)); rev = True
                new_line, gain, merge_indices = self._compress_2048_line(line)
                if rev: new_line = list(reversed(new_line))
                total_gain += gain
                if direction in ["left", "right"]: self.g2048_grid[idx] = new_line
                else:
                    for r in range(G2048_SIZE): self.g2048_grid[r][idx] = new_line[r]
                for mi in merge_indices:
                    if direction == "left": all_merge_cells.append((idx, mi, new_line[mi]))
                    elif direction == "right": all_merge_cells.append((idx, G2048_SIZE - 1 - mi, new_line[G2048_SIZE - 1 - mi]))
                    elif direction == "up": all_merge_cells.append((mi, idx, new_line[mi]))
                    else: all_merge_cells.append((G2048_SIZE - 1 - mi, idx, new_line[mi]))
        if self.g2048_grid == old_grid:
            self.g2048_invalid_shake = G2048_INVALID_SHAKE_FRAMES
            self.g2048_invalid_shake_dir = "x" if direction in ["left", "right"] else "y"
            return False
        self.audio.play("2048_slide")
        self.g2048_moves += 1
        self._record_stat("2048", "moves")
        self._build_2048_slide_anims(old_grid, self.g2048_grid, direction)
        if total_gain > 0:
            self.g2048_score += total_gain; self.g2048_best = max(self.g2048_best, self.g2048_score)
            self.g2048_score_floaters.append({"text": f"+{total_gain}", "frame": 0, "max_frames": 42, "x_offset": random.randint(-12, 12)})
        for r, c, value in all_merge_cells:
            self._record_stat("2048", "merges")
            self._record_stat("2048", "highest_tile", value, mode="max")
            self.g2048_merge_anims.append({"r": r, "c": c, "value": value, "frame": 0, "max_frames": G2048_MERGE_FRAMES})
            self._spawn_2048_particles(r, c, value, 16)
            if value >= 2048 and not self.g2048_won:
                self.g2048_won = True; self.g2048_win_flash_frame = G2048_WIN_FLASH_FRAMES
                self.g2048_end_panel_frame = 0; self.state = self.G2048_END
                self._record_stat("2048", "wins")
                if not self.g2048_stats_completed:
                    self.g2048_stats_completed = True
                    self._record_stat("2048", "games_completed")
        self._spawn_2048_tile()
        if self._is_2048_game_over():
            self.g2048_game_over = True
            self.g2048_end_panel_frame = 0
            self.audio.play_gameover("2048")
            self.state = self.G2048_END
            if not self.g2048_stats_completed:
                self.g2048_stats_completed = True
                self._record_stat("2048", "games_completed")
        self._record_stat("2048", "best_score", self.g2048_score, mode="max")
        return True

    def _is_2048_game_over(self):
        for r in range(G2048_SIZE):
            for c in range(G2048_SIZE):
                if self.g2048_grid[r][c] == 0: return False
                if c + 1 < G2048_SIZE and self.g2048_grid[r][c] == self.g2048_grid[r][c + 1]: return False
                if r + 1 < G2048_SIZE and self.g2048_grid[r][c] == self.g2048_grid[r + 1][c]: return False
        return True

    def _handle_2048_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self._go_desktop()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]: self._start_2048_game()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_2048_menu_buttons():
                if b["rect"].collidepoint(event.pos): self.g2048_pressed_action = b["action"]; return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_2048_menu_buttons():
                if b["rect"].collidepoint(event.pos) and self.g2048_pressed_action == b["action"]:
                    a = b["action"]
                    if a == "g2048_start": self._start_2048_game()
                    elif a == "desktop": self._go_desktop()
                    self.g2048_pressed_action = None; return
            self.g2048_pressed_action = None

    def _handle_2048_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self._start_transition(self.G2048_MENU, "fade"); self.g2048_pressed_action = None; return
            if event.key == pygame.K_r: self._start_2048_game(); return
            if event.key in [pygame.K_LEFT, pygame.K_a]: self._move_2048("left")
            elif event.key in [pygame.K_RIGHT, pygame.K_d]: self._move_2048("right")
            elif event.key in [pygame.K_UP, pygame.K_w]: self._move_2048("up")
            elif event.key in [pygame.K_DOWN, pygame.K_s]: self._move_2048("down")

    def _handle_2048_end_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: self._start_2048_game()
            elif event.key == pygame.K_ESCAPE: self.state = self.G2048_MENU; self.g2048_pressed_action = None
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE] and self.g2048_won and not self.g2048_game_over: self.state = self.G2048_PLAYING
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_2048_end_buttons():
                if b["rect"].collidepoint(event.pos): self.g2048_pressed_action = b["action"]; return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_2048_end_buttons():
                if b["rect"].collidepoint(event.pos) and self.g2048_pressed_action == b["action"]:
                    a = b["action"]
                    if a == "again": self._start_2048_game()
                    elif a == "continue": self.g2048_end_panel_frame = 0; self.g2048_pressed_action = None; self.state = self.G2048_PLAYING
                    elif a == "menu": self.state = self.G2048_MENU
                    elif a == "desktop": self._go_desktop()
                    self.g2048_pressed_action = None; return
            self.g2048_pressed_action = None

    def _update_2048_visual_effects(self):
        # 新方块弹出
        for anim in self.g2048_spawn_anims[:]: anim["frame"] += 1
        self.g2048_spawn_anims = [a for a in self.g2048_spawn_anims if a["frame"] < a["max_frames"]]
        # 合并弹跳
        for anim in self.g2048_merge_anims[:]: anim["frame"] += 1
        self.g2048_merge_anims = [a for a in self.g2048_merge_anims if a["frame"] < a["max_frames"]]
        # 滑行动画
        for anim in self.g2048_slide_anims[:]: anim["frame"] += 1
        self.g2048_slide_anims = [a for a in self.g2048_slide_anims if a["frame"] < a["max_frames"]]
        # 分数飘字
        for f in self.g2048_score_floaters[:]: f["frame"] += 1
        self.g2048_score_floaters = [f for f in self.g2048_score_floaters if f["frame"] < f["max_frames"]]
        # 粒子
        self._update_2048_particles()
        # 无效移动抖动
        if self.g2048_invalid_shake > 0: self.g2048_invalid_shake -= 1
        # 胜利闪光
        if self.g2048_win_flash_frame > 0: self.g2048_win_flash_frame -= 1
        # 结束页弹出
        if self.state == self.G2048_END and self.g2048_end_panel_frame < G2048_END_POP_FRAMES: self.g2048_end_panel_frame += 1

    def _update_2048_particles(self):
        for p in self.g2048_particles[:]:
            p["x"] += p["vx"]; p["y"] += p["vy"]; p["vy"] += 0.08; p["life"] -= 1
            if p["life"] <= 0: self.g2048_particles.remove(p)

    def _draw_2048_left_title_panel(self):
        rect = pygame.Rect(LEFT_BAR_X, LEFT_BAR_Y, LEFT_BAR_W, LEFT_BAR_H)
        pygame.draw.rect(self.screen, C.G2048_PANEL, rect); pygame.draw.rect(self.screen, C.OUTLINE, rect, 4)
        pygame.draw.rect(self.screen, C.G2048_ACCENT, rect.inflate(-8, -8), 2)
        logo = render_vertical_pixel_text(self.font_menu_title, "2048", C.G2048_ACCENT_LIGHT, scale=4, gap=18)
        shadow = render_vertical_pixel_text(self.font_menu_title, "2048", C.OUTLINE, scale=4, gap=18)
        lx, ly = rect.centerx - logo.get_width() // 2, rect.centery - logo.get_height() // 2
        self.screen.blit(shadow, (lx + 3, ly + 3)); self.screen.blit(logo, (lx, ly))

    def _draw_2048_status_panel(self):
        rect = pygame.Rect(RIGHT_BAR_X, RIGHT_BAR_Y, RIGHT_BAR_W, RIGHT_BAR_H)
        pygame.draw.rect(self.screen, C.G2048_PANEL, rect); pygame.draw.rect(self.screen, C.OUTLINE, rect, 4)
        pygame.draw.rect(self.screen, C.G2048_ACCENT, rect.inflate(-8, -8), 2)
        title = render_pixel_text(self.font_status, "STATUS", C.G2048_ACCENT_LIGHT, scale=2)
        self.screen.blit(title, (rect.centerx - title.get_width() // 2, rect.y + 42))
        sl = render_pixel_text(self.font_status, "SCORE", C.G2048_TEXT, scale=2)
        sv = render_pixel_text(self.font_status, str(self.g2048_score), C.G2048_ACCENT_LIGHT, scale=4)
        self.screen.blit(sl, (rect.centerx - sl.get_width() // 2, rect.y + 112))
        self.screen.blit(sv, (rect.centerx - sv.get_width() // 2, rect.y + 148))
        bl2 = render_pixel_text(self.font_status, "BEST", C.G2048_TEXT, scale=2)
        bv = render_pixel_text(self.font_status, str(self.g2048_best), C.G2048_ACCENT_LIGHT, scale=3)
        self.screen.blit(bl2, (rect.centerx - bl2.get_width() // 2, rect.y + 245))
        self.screen.blit(bv, (rect.centerx - bv.get_width() // 2, rect.y + 278))
        ml = render_pixel_text(self.font_status, "MOVES", C.G2048_TEXT, scale=2)
        mv = render_pixel_text(self.font_status, str(self.g2048_moves), C.G2048_ACCENT_LIGHT, scale=3)
        self.screen.blit(ml, (rect.centerx - ml.get_width() // 2, rect.y + 350))
        self.screen.blit(mv, (rect.centerx - mv.get_width() // 2, rect.y + 383))
        for i, t in enumerate(["WASD / ARROWS", "R: Restart", "ESC: Menu"]):
            h = render_pixel_text(self.font_small, t, C.G2048_TEXT, scale=1 if is_chinese() else 2)
            self.screen.blit(h, (rect.centerx - h.get_width() // 2, rect.y + (450 if is_chinese() else 446) + i * (20 if is_chinese() else 26)))

    def _draw_2048_game(self):
        self.screen.fill(C.G2048_BG)
        outer = pygame.Rect(28, 28, WINDOW_W - 56, WINDOW_H - 56)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5); pygame.draw.rect(self.screen, C.G2048_ACCENT, outer.inflate(-8, -8), 2)
        self._draw_2048_left_title_panel(); self._draw_2048_status_panel()

        # 无效移动抖动
        sx = 0; sy = 0
        if self.g2048_invalid_shake > 0:
            strength = max(1, self.g2048_invalid_shake // 3)
            if self.g2048_invalid_shake_dir == "x": sx = random.randint(-strength, strength)
            else: sy = random.randint(-strength, strength)

        br = pygame.Rect(G2048_X + sx, G2048_Y + sy, G2048_BOARD_PX, G2048_BOARD_PX)
        pygame.draw.rect(self.screen, C.OUTLINE, br.inflate(14, 14)); pygame.draw.rect(self.screen, C.G2048_BOARD, br)

        # 空格背景
        for r in range(G2048_SIZE):
            for c in range(G2048_SIZE):
                cr = self._get_2048_cell_rect(r, c, sx, sy)
                pygame.draw.rect(self.screen, C.OUTLINE, cr); pygame.draw.rect(self.screen, C.G2048_CELL_EMPTY, cr.inflate(-5, -5))

        pop_lk = {(a["r"], a["c"]): a for a in self.g2048_spawn_anims}
        merge_lk = {(a["r"], a["c"]): a for a in self.g2048_merge_anims}
        sliding_targets = {(a["to_r"], a["to_c"]) for a in self.g2048_slide_anims}

        # 普通 tile
        for r in range(G2048_SIZE):
            for c in range(G2048_SIZE):
                v = self.g2048_grid[r][c]
                if v == 0: continue
                if (r, c) in sliding_targets: continue
                sf = 1.0
                if (r, c) in pop_lk:
                    a = pop_lk[(r, c)]; t = a["frame"] / max(1, a["max_frames"])
                    sf = 0.15 + 0.95 * ease_out_back(min(1.0, t)); sf = min(sf, 1.15)
                if (r, c) in merge_lk:
                    a = merge_lk[(r, c)]; t = a["frame"] / max(1, a["max_frames"])
                    sf = 1.0 + 0.22 * math.sin(t * math.pi)
                cr = self._get_2048_cell_rect(r, c, sx, sy)
                if sf != 1.0:
                    nw = int(cr.width * sf); nh = int(cr.height * sf)
                    cr = pygame.Rect(cr.centerx - nw // 2, cr.centery - nh // 2, nw, nh)
                color = self._get_2048_tile_color(v)
                pygame.draw.rect(self.screen, C.OUTLINE, cr); pygame.draw.rect(self.screen, color, cr.inflate(-5, -5))
                tc = C.OUTLINE if v <= 8 else C.G2048_TEXT
                sc = 4 if v < 100 else (3 if v < 1000 else 2)
                txt = render_pixel_text(self.font_menu_title, str(v), tc, scale=sc)
                self.screen.blit(txt, (cr.centerx - txt.get_width() // 2, cr.centery - txt.get_height() // 2))
                # 合并闪光框
                if (r, c) in merge_lk:
                    a = merge_lk[(r, c)]; t = a["frame"] / max(1, a["max_frames"]); alpha = int(180 * (1 - t))
                    glow = pygame.Surface((cr.width + 16, cr.height + 16), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (*C.G2048_ACCENT_LIGHT, alpha), glow.get_rect(), 4)
                    self.screen.blit(glow, (cr.x - 8, cr.y - 8))

        # 滑动 tile
        for anim in self.g2048_slide_anims:
            t = anim["frame"] / max(1, anim["max_frames"])
            t = 1 - (1 - t) * (1 - t)
            fr = self._get_2048_cell_rect(anim["from_r"], anim["from_c"], sx, sy)
            tr2 = self._get_2048_cell_rect(anim["to_r"], anim["to_c"], sx, sy)
            xx = fr.x + (tr2.x - fr.x) * t; yy = fr.y + (tr2.y - fr.y) * t
            cr = pygame.Rect(int(xx), int(yy), G2048_CELL, G2048_CELL)
            color = self._get_2048_tile_color(anim["value"])
            ts = pygame.Surface((cr.width, cr.height), pygame.SRCALPHA)
            pygame.draw.rect(ts, C.OUTLINE, (0, 0, cr.width, cr.height))
            pygame.draw.rect(ts, color, (5, 5, cr.width - 10, cr.height - 10))
            ts.set_alpha(230)
            self.screen.blit(ts, cr.topleft)

        # 粒子
        for p in self.g2048_particles:
            alpha = max(0, min(255, int(255 * p["life"] / max(1, p["max_life"]))))
            size = max(1, int(p["size"] * p["life"] / max(1, p["max_life"])))
            surf = pygame.Surface((size, size), pygame.SRCALPHA); surf.fill((*p["color"], alpha))
            self.screen.blit(surf, (int(p["x"] - size // 2 + sx), int(p["y"] - size // 2 + sy)))

        # 分数飘字
        for floater in self.g2048_score_floaters:
            t = floater["frame"] / max(1, floater["max_frames"]); alpha = max(0, int(255 * (1 - t)))
            yf = RIGHT_BAR_Y + 190 - int(t * 52)
            xf = RIGHT_BAR_X + RIGHT_BAR_W // 2 + floater.get("x_offset", 0)
            sc2 = 3 if t < 0.55 else 2
            txt = render_pixel_text(self.font_status, floater["text"], C.G2048_ACCENT_LIGHT, scale=sc2)
            tmp = pygame.Surface((txt.get_width(), txt.get_height()), pygame.SRCALPHA); tmp.blit(txt, (0, 0)); tmp.set_alpha(alpha)
            self.screen.blit(tmp, (xf - txt.get_width() // 2, yf))

        # 胜利闪光
        if self.g2048_win_flash_frame > 0:
            t = self.g2048_win_flash_frame / G2048_WIN_FLASH_FRAMES; alpha = int(130 * t)
            flash = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            flash.fill((*C.G2048_ACCENT_LIGHT, alpha)); self.screen.blit(flash, (0, 0))

    def _draw_2048_menu(self):
        self.screen.fill(C.G2048_BG)
        outer = pygame.Rect(90, 54, WINDOW_W - 180, WINDOW_H - 108)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5); pygame.draw.rect(self.screen, C.G2048_PANEL, outer.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.G2048_ACCENT, outer.inflate(-22, -22), 2)
        title_offset = int(math.sin(self.anim_tick * 0.04) * 4)
        title = render_pixel_text(self.font_menu_title, "2048", C.G2048_ACCENT_LIGHT, scale=7)
        shadow = render_pixel_text(self.font_menu_title, "2048", C.OUTLINE, scale=7)
        tx, ty = (
            outer.centerx - title.get_width() // 2,
            outer.y + (96 if is_chinese() else 120) + title_offset,
        )
        self.screen.blit(shadow, (tx + 4, ty + 4)); self.screen.blit(title, (tx, ty))
        subtitle_text = "数字合成 · 合并方块，挑战 2048" if is_chinese() else "MERGE TILES TO REACH 2048"
        subtitle = render_pixel_text(self.font_small, subtitle_text, C.G2048_TEXT, scale=2)
        self.screen.blit(subtitle, (outer.centerx - subtitle.get_width() // 2, ty + title.get_height() + 18))
        mp = self._logical_mouse_pos()
        for b in self._get_2048_menu_buttons():
            self._draw_2048_button(b, b["rect"].collidepoint(mp), self.g2048_pressed_action == b["action"])

    def _draw_2048_end(self):
        self._draw_2048_game()
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA); overlay.fill((0, 0, 0, 130)); self.screen.blit(overlay, (0, 0))
        pw, ph = 560, 430
        t = min(1.0, self.g2048_end_panel_frame / max(1, G2048_END_POP_FRAMES)); pop = ease_out_back(t)
        dw, dh = int(pw * pop), int(ph * pop)
        panel = pygame.Rect(WINDOW_W // 2 - dw // 2, WINDOW_H // 2 - dh // 2, dw, dh)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5); pygame.draw.rect(self.screen, C.G2048_PANEL, panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.G2048_ACCENT, panel.inflate(-24, -24), 2)
        title_text = "YOU WIN" if (self.g2048_won and not self.g2048_game_over) else "GAME OVER"
        title_col = C.G2048_ACCENT_LIGHT if (self.g2048_won and not self.g2048_game_over) else C.G2048_TILE_32
        pulse = 1.0 + 0.04 * math.sin(self.anim_tick * 0.15)
        title = render_pixel_text(self.font_menu_title, title_text, title_col, scale=3)
        tw = int(title.get_width() * pulse); th = int(title.get_height() * pulse)
        title = pygame.transform.scale(title, (tw, th))
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 50))
        score = render_pixel_text(self.font_status, f"SCORE {self.g2048_score}", C.G2048_TEXT, scale=3)
        best = render_pixel_text(self.font_status, f"BEST {self.g2048_best}", C.G2048_ACCENT_LIGHT, scale=3)
        self.screen.blit(score, (panel.centerx - score.get_width() // 2, panel.y + 130))
        self.screen.blit(best, (panel.centerx - best.get_width() // 2, panel.y + 185))
        mp = self._logical_mouse_pos()
        for b in self._get_2048_end_buttons():
            self._draw_2048_button(b, b["rect"].collidepoint(mp), self.g2048_pressed_action == b["action"])
