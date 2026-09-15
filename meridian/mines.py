from .common import *


class MinesMixin:
    def _init_mines(self):
        self.mines_size = DEFAULT_MINES_SIZE
        self.mines_count = DEFAULT_MINES_COUNT
        self.mines_grid = [[0 for _ in range(self.mines_size)] for _ in range(self.mines_size)]
        self.mines_revealed = [[False for _ in range(self.mines_size)] for _ in range(self.mines_size)]
        self.mines_flags = [[False for _ in range(self.mines_size)] for _ in range(self.mines_size)]
        self.mines_started = False
        self.mines_game_over = False
        self.mines_win = False
        self.mines_revealed_count = 0
        self.mines_flags_count = 0
        self.mines_pressed_action = None
        self.mines_elapsed_ms = 0
        # Timer model: mines_elapsed_ms is authoritative and is the only timer
        # value persisted.  The live segment adds (now - mines_timer_base);
        # pygame.time.get_ticks() restarts near zero in a new process, so a
        # saved tick value can never be used as a start point.
        self.mines_timer_base = 0
        self.mines_resume_elapsed = 0
        self.mines_best_times = {(9, 10): None, (9, 15): None, (9, 20): None, (16, 40): None, (16, 50): None, (16, 60): None}
        self.mines_last_click_cell = None
        self.mines_last_click_ticks = 0
        self.mines_reveal_anims = []
        self.mines_flag_anims = []
        self.mines_particles = []
        self.mines_shake = 0
        self.mines_end_panel_frame = 0
        self.mines_death_anim_active = False
        self.mines_death_phase = "none"
        self.mines_death_frame = 0
        self.mines_exploded_cell = None
        self.mines_death_fade_alpha = 0
        self.mines_last_open_cell = None
        self.mines_hint_cell = None
        self.mines_hint_flash_frame = 0
        self.mines_hint_cooldown = 0

    def _get_mines_gap(self):
        return 4 if self.mines_size <= 9 else 2

    def _get_mines_cell_size(self):
        gap = self._get_mines_gap()
        return (MINES_BOARD_PX - gap * (self.mines_size + 1)) // self.mines_size

    def _get_mines_menu_buttons(self):
        cx = WINDOW_W // 2; btn_w = 220; btn_h = 50; gap = 22; start_y = 345
        buttons = []
        if self.save_data["progress"]["mines"]["run_active"]:
            buttons.append({"rect": pygame.Rect(cx - btn_w // 2, start_y, btn_w, btn_h), "label": "CONTINUE", "action": "continue", "selected": False})
            start_y += btn_h + gap
        buttons.extend([{"rect": pygame.Rect(cx - btn_w // 2, start_y, btn_w, btn_h), "label": "START", "action": "mines_start", "selected": False},
                {"rect": pygame.Rect(cx - btn_w // 2, start_y + btn_h + gap, btn_w, btn_h), "label": "SETTINGS", "action": "settings", "selected": False},
                {"rect": pygame.Rect(cx - btn_w // 2, start_y + (btn_h + gap) * 2, btn_w, btn_h), "label": "DESKTOP", "action": "desktop", "selected": False}])
        return buttons

    def _get_mines_end_buttons(self):
        btn_w = 210; btn_h = 44; gap = 14
        pw, ph = 560, 420
        panel = pygame.Rect(WINDOW_W // 2 - pw // 2, WINDOW_H // 2 - ph // 2, pw, ph)
        x = panel.centerx - btn_w // 2; start_y = panel.y + 236
        return [{"rect": pygame.Rect(x, start_y, btn_w, btn_h), "label": "PLAY AGAIN", "action": "again", "selected": False},
                {"rect": pygame.Rect(x, start_y + btn_h + gap, btn_w, btn_h), "label": "MENU", "action": "menu", "selected": False},
                {"rect": pygame.Rect(x, start_y + (btn_h + gap) * 2, btn_w, btn_h), "label": "DESKTOP", "action": "desktop", "selected": False}]

    def _get_mines_settings_buttons(self):
        btns = []; pw = 980; ph = 590
        panel = pygame.Rect(WINDOW_W // 2 - pw // 2, WINDOW_H // 2 - ph // 2, pw, ph)
        bw = 150; bh = 48; gap = 24
        si = [("9 x 9", "mines_size_9"), ("16 x 16", "mines_size_16")]
        tw = len(si) * bw + (len(si) - 1) * gap; sx = panel.centerx - tw // 2; y = panel.y + 205
        for i, (lb, ac) in enumerate(si):
            btns.append({"rect": pygame.Rect(sx + i * (bw + gap), y, bw, bh), "label": lb, "action": ac, "selected": self.mines_size == int(ac.split("_")[-1])})
        ci = MINES_COUNT_CHOICES.get(self.mines_size, [self.mines_count])
        cbw = 130; tw = len(ci) * cbw + (len(ci) - 1) * gap; sx = panel.centerx - tw // 2; y = panel.y + 350
        for i, cnt in enumerate(ci):
            btns.append({"rect": pygame.Rect(sx + i * (cbw + gap), y, cbw, bh), "label": str(cnt), "action": f"mines_count_{cnt}", "selected": self.mines_count == cnt})
        btns.append({"rect": pygame.Rect(panel.centerx - 110, panel.bottom - 82, 220, 52), "label": "BACK", "action": "back", "selected": False})
        return btns

    def _draw_mines_button(self, btn, hovered=False, pressed=False):
        rect = btn["rect"].copy(); selected = btn.get("selected", False)
        if hovered: rect = rect.inflate(10, 8)
        if pressed: rect.y += 4
        shade = 6 if hovered else 4; pygame.draw.rect(self.screen, C.OUTLINE, rect.move(shade, shade))
        if selected: fill, inner, tc = C.MINES_ACCENT, C.MINES_ACCENT_LIGHT, C.OUTLINE
        elif hovered: fill, inner, tc = C.MINES_PANEL, C.MINES_ACCENT_LIGHT, C.MINES_TEXT
        else: fill, inner, tc = C.MINES_PANEL_DARK, C.MINES_ACCENT, C.MINES_TEXT
        pygame.draw.rect(self.screen, C.OUTLINE, rect); pygame.draw.rect(self.screen, fill, rect.inflate(-5, -5))
        pygame.draw.rect(self.screen, inner, rect.inflate(-12, -12), 2)
        if hovered: pygame.draw.rect(self.screen, C.MINES_ACCENT_LIGHT, (rect.x + 10, rect.y + 8, rect.width - 20, 4))
        label = render_pixel_text(self.font_btn, btn["label"], tc, scale=2)
        if label.get_width() > rect.width - 24: label = render_pixel_text(self.font_btn, btn["label"], tc, scale=1)
        self.screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    def _start_mines_game(self, restore_state=None, track=True):
        if restore_state:
            self.mines_grid = restore_state["grid"]
            self.mines_revealed = restore_state["revealed"]
            self.mines_flags = restore_state["flags"]
            self.mines_started = restore_state["started"]
            self.mines_elapsed_ms = int(restore_state.get("elapsed_ms", 0))
            self.mines_resume_elapsed = self.mines_elapsed_ms
            self.mines_timer_base = pygame.time.get_ticks()
            self.mines_game_over = False; self.mines_win = False
            self.mines_revealed_count = restore_state.get("revealed_count", 0)
            self.mines_flags_count = restore_state.get("flags_count", 0)
            self.mines_pressed_action = None
            self.mines_last_click_cell = None; self.mines_last_click_ticks = 0
            self.mines_reveal_anims.clear(); self.mines_flag_anims.clear(); self.mines_particles.clear()
            self.mines_shake = 0; self.mines_end_panel_frame = 0
            self.mines_death_anim_active = False; self.mines_death_phase = "none"; self.mines_death_frame = 0
            self.mines_exploded_cell = None; self.mines_death_fade_alpha = 0; self.mines_last_open_cell = None
            self.mines_hint_cell = None; self.mines_hint_flash_frame = 0; self.mines_hint_cooldown = 0
            self.state = self.MINES_PLAYING
            self.mines_stats_completed = False
            return
        self.mines_grid = [[0]*self.mines_size for _ in range(self.mines_size)]
        self.mines_revealed = [[False]*self.mines_size for _ in range(self.mines_size)]
        self.mines_flags = [[False]*self.mines_size for _ in range(self.mines_size)]
        self.mines_started = False; self.mines_game_over = False; self.mines_win = False
        self.mines_revealed_count = 0; self.mines_flags_count = 0; self.mines_pressed_action = None
        self.mines_elapsed_ms = 0; self.mines_resume_elapsed = 0
        self.mines_timer_base = pygame.time.get_ticks()
        self.mines_last_click_cell = None; self.mines_last_click_ticks = 0
        self.mines_reveal_anims.clear(); self.mines_flag_anims.clear(); self.mines_particles.clear()
        self.mines_shake = 0; self.mines_end_panel_frame = 0
        self.mines_death_anim_active = False; self.mines_death_phase = "none"; self.mines_death_frame = 0
        self.mines_exploded_cell = None; self.mines_death_fade_alpha = 0; self.mines_last_open_cell = None
        self.mines_hint_cell = None; self.mines_hint_flash_frame = 0; self.mines_hint_cooldown = 0
        self.state = self.MINES_PLAYING
        self.mines_stats_completed = False
        if track:
            self._record_stat("mines", "games_started")
        self._clear_run_state("mines")

    def _mines_elapsed_now(self):
        """Current elapsed play time, correct across a process restart.

        ``pygame.time.get_ticks()`` is only meaningful within one process, so
        the saved ``mines_elapsed_ms`` is carried forward as
        ``mines_resume_elapsed`` and the live segment adds the delta since the
        current ``mines_timer_base``.  Computed in one place so the HUD, the
        save file and the best-time record can never disagree.
        """
        if not self.mines_started or self.mines_game_over or self.mines_win:
            return self.mines_elapsed_ms
        return self.mines_resume_elapsed + (pygame.time.get_ticks() - self.mines_timer_base)

    def _capture_mines_run_state(self):
        # mines_elapsed_ms is kept fresh by _update_mines_visual_effects while
        # the board is live, so it is persisted as-is; recomputing here would
        # make the stored value depend on when the capture ran.
        return {
            "grid": self.mines_grid,
            "revealed": self.mines_revealed,
            "flags": self.mines_flags,
            "started": self.mines_started,
            "elapsed_ms": self.mines_elapsed_ms,
            "revealed_count": self.mines_revealed_count,
            "flags_count": self.mines_flags_count,
        }

    def _generate_mines_board(self, safe_r, safe_c):
        positions = [(r, c) for r in range(self.mines_size) for c in range(self.mines_size) if not (abs(r - safe_r) <= 1 and abs(c - safe_c) <= 1)]
        random.shuffle(positions)
        real = min(self.mines_count, len(positions))
        for i in range(real): r, c = positions[i]; self.mines_grid[r][c] = -1
        for r in range(self.mines_size):
            for c in range(self.mines_size):
                if self.mines_grid[r][c] == -1: continue
                cnt = sum(1 for dr in [-1,0,1] for dc in [-1,0,1] if not (dr==0 and dc==0) and 0<=r+dr<self.mines_size and 0<=c+dc<self.mines_size and self.mines_grid[r+dr][c+dc]==-1)
                self.mines_grid[r][c] = cnt
        self.mines_started = True
        self.mines_elapsed_ms = 0
        self.mines_resume_elapsed = 0
        self.mines_timer_base = pygame.time.get_ticks()

    def _get_mines_cell_rect(self, r, c, ox=0, oy=0):
        gap = self._get_mines_gap(); cell = self._get_mines_cell_size()
        x = (MINES_X + ox) + gap + c * (cell + gap); y = (MINES_Y + oy) + gap + r * (cell + gap)
        return pygame.Rect(x, y, cell, cell)

    def _mines_pos_to_cell(self, pos):
        mx, my = pos
        if not (MINES_X <= mx <= MINES_X + MINES_BOARD_PX and MINES_Y <= my <= MINES_Y + MINES_BOARD_PX): return None, None
        for r in range(self.mines_size):
            for c in range(self.mines_size):
                if self._get_mines_cell_rect(r, c).collidepoint(pos): return r, c
        return None, None

    def _reveal_mines_cell(self, r, c):
        if self.mines_game_over or self.mines_win: return
        if not (0 <= r < self.mines_size and 0 <= c < self.mines_size): return
        if self.mines_revealed[r][c] or self.mines_flags[r][c]: return
        if not self.mines_started: self._generate_mines_board(r, c)
        if self.mines_grid[r][c] == -1:
            if getattr(self, "dev_invincible", False):
                self.audio.play("error", 0.35)
                return
            self.audio.play("mines_pulse")
            self.mines_revealed[r][c] = True; self.mines_game_over = True; self.mines_win = False
            if not self.mines_stats_completed:
                self.mines_stats_completed = True
                self._record_stat("mines", "losses")
                self._record_stat("mines", "games_completed")
            self._clear_run_state("mines")
            self.mines_exploded_cell = (r, c)
            self.mines_death_anim_active = True; self.mines_death_phase = "flash"; self.mines_death_frame = 0
            self.mines_shake = MINES_SHAKE_FRAMES
            return
        self.mines_last_open_cell = (r, c)
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if not (0 <= cr < self.mines_size and 0 <= cc < self.mines_size): continue
            if self.mines_revealed[cr][cc] or self.mines_flags[cr][cc]: continue
            self.mines_revealed[cr][cc] = True; self.mines_revealed_count += 1
            self._record_stat("mines", "cells_revealed")
            self.mines_reveal_anims.append({"r": cr, "c": cc, "frame": 0, "max_frames": MINES_REVEAL_POP_FRAMES})
            if self.mines_grid[cr][cc] == 0:
                for dr in [-1,0,1]:
                    for dc in [-1,0,1]:
                        if not (dr==0 and dc==0): stack.append((cr+dr, cc+dc))
        self._check_mines_win()

    def _toggle_mines_flag(self, r, c):
        if self.mines_game_over or self.mines_win: return
        if not (0 <= r < self.mines_size and 0 <= c < self.mines_size): return
        if self.mines_revealed[r][c]: return
        self.mines_flags[r][c] = not self.mines_flags[r][c]
        if self.mines_flags[r][c]:
            self.mines_flags_count += 1; self._spawn_mines_flag_particles(r, c)
            self._record_stat("mines", "flags_placed")
        else: self.mines_flags_count -= 1
        self.mines_flag_anims.append({"r": r, "c": c, "frame": 0, "max_frames": MINES_FLAG_POP_FRAMES})

    def _reveal_all_mines(self):
        for r in range(self.mines_size):
            for c in range(self.mines_size):
                if self.mines_grid[r][c] == -1: self.mines_revealed[r][c] = True

    def _check_mines_win(self):
        if self.mines_revealed_count >= self.mines_size * self.mines_size - self.mines_count:
            self.mines_win = True; self.mines_game_over = False; self.mines_end_panel_frame = 0
            if self.mines_started:
                self.mines_elapsed_ms = self._mines_elapsed_now()
                key = (self.mines_size, self.mines_count)
                old = self.mines_best_times.get(key)
                # A negative elapsed can only come from a corrupt save; never
                # let it become an unbreakable "best time".
                if self.mines_elapsed_ms >= 0 and (old is None or self.mines_elapsed_ms < old):
                    self.mines_best_times[key] = self.mines_elapsed_ms
            self.state = self.MINES_END
            if not self.mines_stats_completed:
                self.mines_stats_completed = True
                self._record_stat("mines", "wins")
                self._record_stat("mines", "games_completed")
                mode = f"{self.mines_size}x{self.mines_count}"
                modes = self.save_data["statistics"]["mines"]["wins_by_mode"]
                modes[mode] = modes.get(mode, 0) + 1
                self._check_achievements()
            self._clear_run_state("mines")

    def _spawn_mines_flag_particles(self, r, c):
        rect = self._get_mines_cell_rect(r, c)
        for _ in range(MINES_FLAG_PARTICLE_COUNT):
            life = random.randint(12, 22)
            self.mines_particles.append({"x": rect.centerx, "y": rect.centery, "vx": random.uniform(-1.5, 1.5), "vy": random.uniform(-2.0, 0.5), "life": life, "max_life": life, "color": C.MINES_FLAG, "size": random.randint(2, 4)})

    def _spawn_mines_explosion(self, r, c):
        rect = self._get_mines_cell_rect(r, c); colors = [C.MINES_FLAG, C.MINES_ACCENT_LIGHT, C.MINES_MINE_RED, C.OUTLINE]
        for _ in range(MINES_EXPLOSION_PARTICLE_COUNT):
            life = random.randint(18, 34); speed = random.uniform(1.8, 4.6); angle = random.uniform(0, math.tau)
            self.mines_particles.append({"x": rect.centerx, "y": rect.centery, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed, "life": life, "max_life": life, "color": random.choice(colors), "size": random.randint(3, 7)})

    def _count_flags_around_mines_cell(self, r, c):
        return sum(1 for dr in [-1,0,1] for dc in [-1,0,1] if not (dr==0 and dc==0) and 0<=r+dr<self.mines_size and 0<=c+dc<self.mines_size and self.mines_flags[r+dr][c+dc])

    def _chord_mines_cell(self, r, c):
        if self.mines_game_over or self.mines_win: return
        if not (0 <= r < self.mines_size and 0 <= c < self.mines_size): return
        if not self.mines_revealed[r][c]: return
        v = self.mines_grid[r][c]
        if v <= 0: return
        if self._count_flags_around_mines_cell(r, c) != v: self.mines_shake = 8; return
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr==0 and dc==0: continue
                nr, nc = r+dr, c+dc
                if 0<=nr<self.mines_size and 0<=nc<self.mines_size and not self.mines_flags[nr][nc] and not self.mines_revealed[nr][nc]:
                    self._reveal_mines_cell(nr, nc)

    def _format_mines_time(self, ms):
        if ms is None: return "--:--"
        s = max(0, ms // 1000); return f"{s//60:02d}:{s%60:02d}"

    def _handle_mines_menu_event(self, event):
        if self.prologue_active:
            self._handle_prologue_event(event)
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self._go_desktop()
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]: self._start_mines_game()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_mines_menu_buttons():
                if b["rect"].collidepoint(event.pos): self.mines_pressed_action = b["action"]; return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_mines_menu_buttons():
                if b["rect"].collidepoint(event.pos) and self.mines_pressed_action == b["action"]:
                    a = b["action"]
                    if a == "continue": self._start_mines_game(restore_state=self.save_data["progress"]["mines"]["run_state"])
                    elif a == "mines_start": self._start_mines_game()
                    elif a == "settings": self.state = self.MINES_SETTINGS
                    elif a == "desktop": self._go_desktop()
                    self.mines_pressed_action = None; return
            self.mines_pressed_action = None

    def _handle_mines_playing_event(self, event):
        if self.mines_death_anim_active: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._save_now()
                self._start_transition(self.MINES_MENU, "fade")
                self.mines_pressed_action = None
                return
            if event.key == pygame.K_r: self._start_mines_game(); return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hb = self._get_mines_hint_button()
            if hb["rect"].collidepoint(event.pos): self.mines_pressed_action = "hint"; return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.mines_pressed_action == "hint":
                hb = self._get_mines_hint_button()
                if hb["rect"].collidepoint(event.pos): self._use_mines_hint()
                self.mines_pressed_action = None; return
        if event.type == pygame.MOUSEBUTTONDOWN:
            r, c = self._mines_pos_to_cell(event.pos)
            if r is None: return
            if event.button == 1:
                now = pygame.time.get_ticks(); same = self.mines_last_click_cell == (r, c)
                is_double = same and (now - self.mines_last_click_ticks <= 320)
                self.mines_last_click_cell = (r, c); self.mines_last_click_ticks = now
                if is_double and self.mines_revealed[r][c] and self.mines_grid[r][c] > 0: self._chord_mines_cell(r, c)
                else: self._reveal_mines_cell(r, c)
            elif event.button == 3: self._toggle_mines_flag(r, c)

    def _handle_mines_end_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: self._start_mines_game()
            elif event.key == pygame.K_ESCAPE: self.state = self.MINES_MENU; self.mines_pressed_action = None; return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_mines_end_buttons():
                if b["rect"].collidepoint(event.pos): self.mines_pressed_action = b["action"]; return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_mines_end_buttons():
                if b["rect"].collidepoint(event.pos) and self.mines_pressed_action == b["action"]:
                    a = b["action"]
                    if a == "again": self._start_mines_game()
                    elif a == "menu": self.state = self.MINES_MENU
                    elif a == "desktop": self._go_desktop()
                    self.mines_pressed_action = None; return
            self.mines_pressed_action = None

    def _handle_mines_settings_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = self.MINES_MENU; self.mines_pressed_action = None; return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_mines_settings_buttons():
                if b["rect"].collidepoint(event.pos): self.mines_pressed_action = b["action"]; return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_mines_settings_buttons():
                if b["rect"].collidepoint(event.pos) and self.mines_pressed_action == b["action"]:
                    a = b["action"]
                    if a == "back": self._start_transition(self.MINES_MENU, "fade")
                    elif a.startswith("mines_size_"):
                        self.mines_size = int(a.split("_")[-1])
                        self.mines_count = MINES_COUNT_CHOICES[self.mines_size][0]
                        self._start_mines_game(track=False); self.state = self.MINES_SETTINGS
                    elif a.startswith("mines_count_"):
                        self.mines_count = int(a.split("_")[-1])
                        self._start_mines_game(track=False); self.state = self.MINES_SETTINGS
                    self.mines_pressed_action = None; return
            self.mines_pressed_action = None

    def _update_mines_visual_effects(self):
        if self.mines_started and not self.mines_game_over and not self.mines_win:
            self.mines_elapsed_ms = self._mines_elapsed_now()
        self._update_mines_death_animation()
        for lst in [self.mines_reveal_anims, self.mines_flag_anims]:
            for a in lst[:]: a["frame"] += 1
            lst[:] = [a for a in lst if a["frame"] < a["max_frames"]]
        for p in self.mines_particles[:]:
            p["x"] += p["vx"]; p["y"] += p["vy"]
            p["vx"] *= 0.975; p["vy"] *= 0.975
            p["vy"] += 0.10; p["life"] -= 1
            if p["life"] <= 0: self.mines_particles.remove(p)
        if self.mines_shake > 0: self.mines_shake -= 1
        if self.mines_hint_flash_frame > 0: self.mines_hint_flash_frame -= 1
        else: self.mines_hint_cell = None
        if self.mines_hint_cooldown > 0: self.mines_hint_cooldown -= 1
        if self.state == self.MINES_END and self.mines_end_panel_frame < MINES_END_POP_FRAMES: self.mines_end_panel_frame += 1

    def _update_mines_death_animation(self):
        if not self.mines_death_anim_active: return
        self.mines_death_frame += 1
        if self.mines_death_phase == "flash":
            t = self.mines_death_frame / max(1, MINES_DEATH_FLASH_FRAMES)
            self.mines_shake = max(self.mines_shake, 2 + int(t * 6))
            if self.mines_exploded_cell is not None and self.mines_death_frame % 5 == 0:
                self._spawn_mines_warning_sparks(*self.mines_exploded_cell, 8)
            if self.mines_death_frame >= MINES_DEATH_FLASH_FRAMES:
                self.mines_death_phase = "explode"; self.mines_death_frame = 0
                self.audio.play("mines_explosion")
                if self.mines_exploded_cell is not None:
                    self._spawn_mines_big_explosion(*self.mines_exploded_cell)
        elif self.mines_death_phase == "explode":
            t = self.mines_death_frame / max(1, MINES_DEATH_EXPLOSION_FRAMES)
            self.mines_shake = max(self.mines_shake, max(3, int(14 * (1 - t))))
            if self.mines_death_frame == 22 and self.mines_exploded_cell is not None:
                self._spawn_mines_ring_explosion(*self.mines_exploded_cell)
            if self.mines_death_frame == 48 and self.mines_exploded_cell is not None:
                self._spawn_mines_embers(*self.mines_exploded_cell)
            if self.mines_exploded_cell is not None and self.mines_death_frame % 7 == 0:
                self._spawn_mines_warning_sparks(*self.mines_exploded_cell, 5)
            if self.mines_death_frame >= MINES_DEATH_EXPLOSION_FRAMES:
                self.mines_death_phase = "reveal"; self.mines_death_frame = 0; self._reveal_all_mines()
        elif self.mines_death_phase == "reveal":
            self.mines_shake = max(self.mines_shake, 2)
            if self.mines_death_frame >= MINES_DEATH_REVEAL_DELAY:
                self.mines_death_phase = "fade"; self.mines_death_frame = 0; self.mines_death_fade_alpha = 0
        elif self.mines_death_phase == "fade":
            t = self.mines_death_frame / max(1, MINES_DEATH_FADE_FRAMES)
            self.mines_death_fade_alpha = min(190, int(190 * t))
            if self.mines_death_frame >= MINES_DEATH_FADE_FRAMES:
                self.mines_death_anim_active = False; self.mines_death_phase = "none"
                self.mines_death_frame = 0; self.mines_death_fade_alpha = 0
                self.mines_end_panel_frame = 0
                self.audio.play_gameover("mines")
                self.state = self.MINES_END

    def _spawn_mines_warning_sparks(self, r, c, count=8):
        rect = self._get_mines_cell_rect(r, c)
        colors = [C.MINES_FLAG, C.MINES_ACCENT_LIGHT, C.MINES_MINE_RED]
        for _ in range(count):
            life = random.randint(16, 30); angle = random.uniform(0, math.tau); speed = random.uniform(0.8, 2.8)
            self.mines_particles.append({"x": rect.centerx+random.randint(-8,8), "y": rect.centery+random.randint(-8,8), "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed-0.8, "life": life, "max_life": life, "color": random.choice(colors), "size": random.randint(2,5)})

    def _spawn_mines_big_explosion(self, r, c):
        rect = self._get_mines_cell_rect(r, c)
        colors = [C.MINES_FLAG, C.MINES_ACCENT_LIGHT, C.MINES_MINE_RED, C.MINES_TEXT, C.OUTLINE]
        for _ in range(MINES_BIG_EXPLOSION_PARTICLES):
            life = random.randint(32, 68); speed = random.uniform(2.5, 8.5); angle = random.uniform(0, math.tau)
            self.mines_particles.append({"x": rect.centerx, "y": rect.centery, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed, "life": life, "max_life": life, "color": random.choice(colors), "size": random.randint(3,10)})
        for _ in range(36):
            life = random.randint(20, 38); speed = random.uniform(6.0, 11.0); angle = random.uniform(0, math.tau)
            self.mines_particles.append({"x": rect.centerx, "y": rect.centery, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed, "life": life, "max_life": life, "color": C.MINES_ACCENT_LIGHT, "size": random.randint(2,5)})

    def _spawn_mines_ring_explosion(self, r, c):
        rect = self._get_mines_cell_rect(r, c)
        colors = [C.MINES_ACCENT_LIGHT, C.MINES_FLAG, C.MINES_TEXT]
        for i in range(MINES_RING_EXPLOSION_PARTICLES):
            life = random.randint(34, 64); angle = (math.tau / MINES_RING_EXPLOSION_PARTICLES) * i + random.uniform(-0.08, 0.08); speed = random.uniform(3.8, 7.2)
            self.mines_particles.append({"x": rect.centerx, "y": rect.centery, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed, "life": life, "max_life": life, "color": random.choice(colors), "size": random.randint(3,7)})

    def _spawn_mines_embers(self, r, c):
        rect = self._get_mines_cell_rect(r, c)
        colors = [C.MINES_ACCENT_LIGHT, C.MINES_FLAG, C.MINES_MINE_RED]
        for _ in range(MINES_EMBER_PARTICLES):
            life = random.randint(55, 100); angle = random.uniform(-math.pi, 0); speed = random.uniform(0.8, 3.4)
            self.mines_particles.append({"x": rect.centerx+random.randint(-40,40), "y": rect.centery+random.randint(-30,30), "vx": math.cos(angle)*speed*0.7, "vy": math.sin(angle)*speed-random.uniform(0.6,1.6), "life": life, "max_life": life, "color": random.choice(colors), "size": random.randint(2,6)})

    def _use_mines_hint(self):
        if self.mines_game_over or self.mines_win or self.mines_death_anim_active: return
        if self.mines_hint_cooldown > 0: self.mines_shake = 6; return
        if not self.mines_started: self.mines_shake = 8; return
        base = self.mines_last_open_cell if self.mines_last_open_cell else (self.mines_size//2, self.mines_size//2)
        cand = [(abs(r-base[0])+abs(c-base[1]), r, c) for r in range(self.mines_size) for c in range(self.mines_size) if self.mines_grid[r][c]==-1 and not self.mines_flags[r][c] and not self.mines_revealed[r][c]]
        if not cand: self.mines_shake = 8; return
        cand.sort(); _, r, c = cand[0]
        self.mines_hint_cell = (r, c); self.mines_hint_flash_frame = MINES_HINT_FLASH_FRAMES; self.mines_hint_cooldown = MINES_HINT_BUTTON_COOLDOWN
        self._spawn_mines_hint_particles(r, c)

    def _spawn_mines_hint_particles(self, r, c):
        rect = self._get_mines_cell_rect(r, c)
        for _ in range(18):
            life = random.randint(18, 32); angle = random.uniform(0, math.tau); speed = random.uniform(0.8, 2.2)
            self.mines_particles.append({"x": rect.centerx, "y": rect.centery, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed, "life": life, "max_life": life, "color": C.MINES_ACCENT_LIGHT, "size": random.randint(2,5)})

    def _get_mines_hint_button(self):
        rect = pygame.Rect(RIGHT_BAR_X, RIGHT_BAR_Y, RIGHT_BAR_W, RIGHT_BAR_H)
        btn_w = 180; btn_h = 40
        return {"rect": pygame.Rect(rect.centerx - btn_w // 2, rect.y + 410, btn_w, btn_h), "label": "HINT", "action": "hint", "selected": False}

    def _draw_mines_flag(self, rect):
        s = rect.width / 52
        pw = max(2, int(5*s)); ph = max(12, int(28*s))
        px = rect.centerx - int(4*s); py = rect.centery - int(14*s)
        pygame.draw.rect(self.screen, C.OUTLINE, (px, py, pw, ph))
        pygame.draw.polygon(self.screen, C.MINES_FLAG, [(px+pw, py), (px+int(28*s), py+int(8*s)), (px+pw, py+int(16*s))])
        pygame.draw.rect(self.screen, C.OUTLINE, (px-int(8*s), py+ph, max(10,int(22*s)), max(2,int(5*s))))

    def _draw_mines_mine(self, rect, exploded=False, flashing=False):
        cx, cy = rect.center
        if flashing:
            color = C.MINES_MINE_RED if (self.anim_tick // 5) % 2 == 0 else C.MINES_ACCENT_LIGHT
            glow_col = C.MINES_ACCENT_LIGHT if (self.anim_tick // 5) % 2 == 0 else C.MINES_FLAG
            glow = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*glow_col, 120), glow.get_rect(), 4)
            self.screen.blit(glow, (rect.x - 10, rect.y - 10))
        else:
            color = C.MINES_MINE_RED if exploded else C.MINES_MINE
        s = rect.width / 52; body = max(10, int(24*s)); inner = max(7, int(18*s))
        ray = max(8, int(18*s)); thick = max(1, int(3*s))
        pygame.draw.rect(self.screen, C.OUTLINE, (cx-body//2, cy-body//2, body, body))
        pygame.draw.rect(self.screen, color, (cx-inner//2, cy-inner//2, inner, inner))
        pygame.draw.line(self.screen, C.OUTLINE, (cx-ray, cy), (cx+ray, cy), thick)
        pygame.draw.line(self.screen, C.OUTLINE, (cx, cy-ray), (cx, cy+ray), thick)
        pygame.draw.line(self.screen, C.OUTLINE, (cx-ray+4, cy-ray+4), (cx+ray-4, cy+ray-4), max(1, thick-1))
        pygame.draw.line(self.screen, C.OUTLINE, (cx+ray-4, cy-ray+4), (cx-ray+4, cy+ray-4), max(1, thick-1))

    def _draw_mines_left_title_panel(self):
        rect = pygame.Rect(LEFT_BAR_X, LEFT_BAR_Y, LEFT_BAR_W, LEFT_BAR_H)
        pygame.draw.rect(self.screen, C.MINES_PANEL, rect); pygame.draw.rect(self.screen, C.OUTLINE, rect, 4)
        pygame.draw.rect(self.screen, C.MINES_ACCENT, rect.inflate(-8, -8), 2)
        logo = render_vertical_pixel_text(self.font_menu_title, "MINES", C.MINES_ACCENT_LIGHT, scale=3, gap=14)
        shadow = render_vertical_pixel_text(self.font_menu_title, "MINES", C.OUTLINE, scale=3, gap=14)
        lx, ly = rect.centerx - logo.get_width() // 2, rect.centery - logo.get_height() // 2
        self.screen.blit(shadow, (lx + 3, ly + 3)); self.screen.blit(logo, (lx, ly))

    def _draw_mines_status_panel(self):
        rect = pygame.Rect(RIGHT_BAR_X, RIGHT_BAR_Y, RIGHT_BAR_W, RIGHT_BAR_H)
        pygame.draw.rect(self.screen, C.MINES_PANEL, rect); pygame.draw.rect(self.screen, C.OUTLINE, rect, 4)
        pygame.draw.rect(self.screen, C.MINES_ACCENT, rect.inflate(-8, -8), 2)
        title = render_pixel_text(self.font_status, "STATUS", C.MINES_ACCENT_LIGHT, scale=2)
        self.screen.blit(title, (rect.centerx - title.get_width() // 2, rect.y + 28))
        ml = max(0, self.mines_count - self.mines_flags_count); bk = (self.mines_size, self.mines_count)
        best_ms = self.mines_best_times.get(bk)
        labels = [("MINES", str(ml)), ("FLAGS", str(self.mines_flags_count)), ("TIME", self._format_mines_time(self.mines_elapsed_ms)), ("BEST", self._format_mines_time(best_ms))]
        y = rect.y + 78
        for name, value in labels:
            ns = render_pixel_text(self.font_status, name, C.MINES_TEXT, scale=2)
            vs = render_pixel_text(self.font_status, value, C.MINES_ACCENT_LIGHT, scale=3)
            self.screen.blit(ns, (rect.centerx - ns.get_width() // 2, y)); self.screen.blit(vs, (rect.centerx - vs.get_width() // 2, y + 28)); y += 74
        mode = render_pixel_text(self.font_small, f"{self.mines_size}x{self.mines_size} / {self.mines_count}", C.MINES_ACCENT_LIGHT, scale=2)
        self.screen.blit(mode, (rect.centerx - mode.get_width() // 2, rect.y + 374))
        hint_btn = self._get_mines_hint_button(); mp2 = self._logical_mouse_pos()
        self._draw_mines_button(hint_btn, hint_btn["rect"].collidepoint(mp2), self.mines_pressed_action == "hint")
        hints = ["LEFT: Open", "RIGHT: Flag", "DOUBLE: Auto", "R: Restart  ESC: Menu"]
        hy = hint_btn["rect"].bottom + 12
        for i, text in enumerate(hints):
            h = render_pixel_text(self.font_small, text, C.MINES_TEXT, scale=2); self.screen.blit(h, (rect.centerx - h.get_width() // 2, hy + i * 24))

    def _draw_mines_game(self):
        self.screen.fill(C.MINES_BG)
        outer = pygame.Rect(28, 28, WINDOW_W - 56, WINDOW_H - 56)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5); pygame.draw.rect(self.screen, C.MINES_ACCENT, outer.inflate(-8, -8), 2)
        self._draw_mines_left_title_panel(); self._draw_mines_status_panel()
        sx = 0; sy = 0
        if self.mines_shake > 0: strength = max(1, self.mines_shake // 3); sx = random.randint(-strength, strength); sy = random.randint(-strength, strength)
        br = pygame.Rect(MINES_X + sx, MINES_Y + sy, MINES_BOARD_PX, MINES_BOARD_PX)
        pygame.draw.rect(self.screen, C.OUTLINE, br.inflate(14, 14)); pygame.draw.rect(self.screen, C.MINES_BOARD, br)
        mp = self._logical_mouse_pos(); hr, hc = self._mines_pos_to_cell(mp)
        rl = {(a["r"], a["c"]): a for a in self.mines_reveal_anims}; fl = {(a["r"], a["c"]): a for a in self.mines_flag_anims}
        for r in range(self.mines_size):
            for c in range(self.mines_size):
                rect = self._get_mines_cell_rect(r, c, sx, sy)
                o = self.mines_revealed[r][c]; f = self.mines_flags[r][c]
                fill = C.MINES_CELL_OPEN if o else (C.MINES_CELL_HOVER if (hr == r and hc == c) else C.MINES_CELL_CLOSED)
                sf = 1.0
                if (r, c) in rl: a = rl[(r, c)]; t = a["frame"] / max(1, a["max_frames"]); sf = min(1.12, 0.3 + 0.85 * ease_out_back(min(1.0, t)))
                if (r, c) in fl: a = fl[(r, c)]; t = a["frame"] / max(1, a["max_frames"]); sf = 1.0 + 0.14 * math.sin(t * math.pi)
                dr = rect
                if sf != 1.0: nw = int(rect.width * sf); nh = int(rect.height * sf); dr = pygame.Rect(rect.centerx - nw // 2, rect.centery - nh // 2, nw, nh)
                pygame.draw.rect(self.screen, C.OUTLINE, dr); pygame.draw.rect(self.screen, fill, dr.inflate(-4, -4))
                if o:
                    v = self.mines_grid[r][c]
                    if v == -1:
                        flashing = (self.mines_death_anim_active and self.mines_death_phase == "flash" and self.mines_exploded_cell == (r, c))
                        exploded = (self.mines_exploded_cell == (r, c) or self.mines_game_over)
                        self._draw_mines_mine(dr, exploded=exploded, flashing=flashing)
                    elif v > 0:
                        nc = C.MINES_ACCENT_LIGHT if v < 3 else C.MINES_FLAG
                        ns = 3 if self.mines_size <= 9 else 2
                        txt = render_pixel_text(self.font_status, str(v), nc, scale=ns)
                        self.screen.blit(txt, (dr.centerx - txt.get_width() // 2, dr.centery - txt.get_height() // 2))
                elif f: self._draw_mines_flag(dr)
                if self.mines_hint_cell == (r, c) and self.mines_hint_flash_frame > 0:
                    if (self.anim_tick // 6) % 2 == 0:
                        pygame.draw.rect(self.screen, C.MINES_ACCENT_LIGHT, dr.inflate(6, 6), 4)
                        pygame.draw.rect(self.screen, C.MINES_FLAG, dr.inflate(12, 12), 2)
                    qs = 3 if self.mines_size <= 9 else 2
                    q = render_pixel_text(self.font_status, "?", C.MINES_ACCENT_LIGHT, scale=qs)
                    self.screen.blit(q, (dr.centerx - q.get_width()//2, dr.centery - q.get_height()//2))
        # death wave
        if self.mines_death_anim_active and self.mines_exploded_cell is not None:
            rr, cc = self.mines_exploded_cell; wre = self._get_mines_cell_rect(rr, cc, sx, sy)
            if self.mines_death_phase == "flash":
                t = self.mines_death_frame / max(1, MINES_DEATH_FLASH_FRAMES)
                for i in range(3):
                    lt = (t + i * 0.18) % 1.0; rad = int(18 + lt * 120); a = int(170 * (1 - lt))
                    wv = pygame.Surface((rad*2+8, rad*2+8), pygame.SRCALPHA)
                    pygame.draw.rect(wv, (*C.MINES_FLAG, a), wv.get_rect(), 4)
                    pygame.draw.rect(wv, (*C.MINES_ACCENT_LIGHT, a // 2), wv.get_rect().inflate(-12, -12), 2)
                    self.screen.blit(wv, (wre.centerx - wv.get_width()//2, wre.centery - wv.get_height()//2))
            elif self.mines_death_phase == "explode":
                t = self.mines_death_frame / max(1, MINES_DEATH_EXPLOSION_FRAMES)
                for i in range(2):
                    lt = min(1.0, max(0.0, t - i * 0.18)); rad = int(45 + lt * 230); a = int(190 * (1 - lt))
                    bl = pygame.Surface((rad*2+10, rad*2+10), pygame.SRCALPHA)
                    pygame.draw.rect(bl, (*C.MINES_ACCENT_LIGHT, a), bl.get_rect(), 6)
                    pygame.draw.rect(bl, (*C.MINES_FLAG, a // 2), bl.get_rect().inflate(-18, -18), 3)
                    self.screen.blit(bl, (wre.centerx - bl.get_width()//2, wre.centery - bl.get_height()//2))
                if self.mines_death_frame < 18:
                    fa = int(150 * (1 - self.mines_death_frame / 18))
                    flash = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
                    flash.fill((*C.MINES_ACCENT_LIGHT, fa)); self.screen.blit(flash, (0, 0))
        for p in self.mines_particles:
            lr = p["life"] / max(1, p["max_life"]); alpha = max(0, min(255, int(255 * lr)))
            size = max(1, int(p["size"] * (0.45 + lr)))
            x = int(p["x"] - size // 2 + sx); y = int(p["y"] - size // 2 + sy)
            gs = size + 8; glow = pygame.Surface((gs, gs), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*p["color"], max(0, alpha // 3)), glow.get_rect())
            self.screen.blit(glow, (x - 4, y - 4))
            surf = pygame.Surface((size, size), pygame.SRCALPHA); surf.fill((*p["color"], alpha))
            self.screen.blit(surf, (x, y))
            if size >= 4:
                cs = max(1, size // 2); core = pygame.Surface((cs, cs), pygame.SRCALPHA)
                core.fill((*C.MINES_ACCENT_LIGHT, min(255, alpha + 40)))
                self.screen.blit(core, (x + size // 4, y + size // 4))

        # death fade to end screen
        if self.mines_death_anim_active and self.mines_death_phase == "fade":
            ov = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, self.mines_death_fade_alpha)); self.screen.blit(ov, (0, 0))
            txt = render_pixel_text(self.font_menu_title, "BOOM...", C.MINES_ACCENT_LIGHT, scale=3)
            sd = render_pixel_text(self.font_menu_title, "BOOM...", C.OUTLINE, scale=3)
            a2 = min(255, self.mines_death_fade_alpha + 40)
            for s, (xxo, yyo) in [(sd, (3, 3)), (txt, (0, 0))]:
                t = pygame.Surface((s.get_width(), s.get_height()), pygame.SRCALPHA); t.blit(s, (0, 0)); t.set_alpha(a2)
                self.screen.blit(t, (WINDOW_W//2 - s.get_width()//2 + xxo, WINDOW_H//2 - s.get_height()//2 + yyo))

    def _draw_mines_menu(self):
        if self._check_and_show_prologue("mines"):
            self._draw_prologue_screen()
            return

        self.screen.fill(C.MINES_BG)
        outer = pygame.Rect(90, 54, WINDOW_W - 180, WINDOW_H - 108)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5); pygame.draw.rect(self.screen, C.MINES_PANEL, outer.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.MINES_ACCENT, outer.inflate(-22, -22), 2)
        title = render_pixel_text(self.font_menu_title, "MINES", C.MINES_ACCENT_LIGHT, scale=6)
        shadow = render_pixel_text(self.font_menu_title, "MINES", C.OUTLINE, scale=6)
        tx = outer.centerx - title.get_width() // 2
        ty = outer.y + (98 if is_chinese() else 120) + int(math.sin(self.anim_tick * 0.04) * 4)
        self.screen.blit(shadow, (tx + 4, ty + 4)); self.screen.blit(title, (tx, ty))
        subtitle_text = "翻开安全格并标记地雷" if is_chinese() else "OPEN SAFE CELLS AND FLAG MINES"
        sub = render_pixel_text(self.font_small, subtitle_text, C.MINES_TEXT, scale=2)
        self.screen.blit(sub, (outer.centerx - sub.get_width() // 2, ty + title.get_height() + 18))
        mp = self._logical_mouse_pos()
        for b in self._get_mines_menu_buttons():
            self._draw_mines_button(b, b["rect"].collidepoint(mp), self.mines_pressed_action == b["action"])

    def _draw_mines_end(self):
        self._draw_mines_game()
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA); overlay.fill((0, 0, 0, 165)); self.screen.blit(overlay, (0, 0))
        pw, ph = 560, 420
        t = min(1.0, self.mines_end_panel_frame / max(1, MINES_END_POP_FRAMES)); pop = ease_out_back(t)
        dw, dh = int(pw * pop), int(ph * pop)
        panel = pygame.Rect(WINDOW_W // 2 - dw // 2, WINDOW_H // 2 - dh // 2, dw, dh)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5); pygame.draw.rect(self.screen, C.MINES_PANEL, panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.MINES_ACCENT, panel.inflate(-24, -24), 2)
        tt = "YOU WIN" if self.mines_win else "BOOM"; tc = C.MINES_ACCENT_LIGHT if self.mines_win else C.MINES_FLAG
        title = render_pixel_text(self.font_menu_title, tt, tc, scale=4); shadow = render_pixel_text(self.font_menu_title, tt, C.OUTLINE, scale=4)
        self.screen.blit(shadow, (panel.centerx - title.get_width() // 2 + 3, panel.y + 48 + 3))
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 48))
        time_text = self._format_mines_time(self.mines_elapsed_ms)
        info = render_pixel_text(self.font_status, f"TIME {time_text}", C.MINES_TEXT, scale=3)
        self.screen.blit(info, (panel.centerx - info.get_width() // 2, panel.y + 145))
        open_info = render_pixel_text(self.font_status, f"OPEN {self.mines_revealed_count}", C.MINES_ACCENT_LIGHT, scale=2)
        self.screen.blit(open_info, (panel.centerx - open_info.get_width() // 2, panel.y + 190))
        mp = self._logical_mouse_pos()
        for b in self._get_mines_end_buttons():
            self._draw_mines_button(b, b["rect"].collidepoint(mp), self.mines_pressed_action == b["action"])

    def _draw_mines_settings_page(self):
        self.screen.fill(C.MINES_BG)
        pw = 980; ph = 590; panel = pygame.Rect(WINDOW_W // 2 - pw // 2, WINDOW_H // 2 - ph // 2, pw, ph)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5); pygame.draw.rect(self.screen, C.MINES_PANEL, panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, C.MINES_ACCENT, panel.inflate(-24, -24), 2)
        title = render_pixel_text(self.font_menu_title, "MINES SETTINGS", C.MINES_ACCENT_LIGHT, scale=3)
        shadow = render_pixel_text(self.font_menu_title, "MINES SETTINGS", C.OUTLINE, scale=3)
        tx = panel.centerx - title.get_width() // 2; ty = panel.y + 48
        self.screen.blit(shadow, (tx + 3, ty + 3)); self.screen.blit(title, (tx, ty))
        ly = panel.y + 122
        pygame.draw.line(self.screen, C.MINES_ACCENT, (panel.x + 70, ly), (panel.right - 70, ly), 3)
        pygame.draw.line(self.screen, C.OUTLINE, (panel.x + 70, ly + 5), (panel.right - 70, ly + 5), 2)
        sl = render_pixel_text(self.font_status, "BOARD SIZE", C.MINES_TEXT, scale=2)
        self.screen.blit(sl, (panel.centerx - sl.get_width() // 2, panel.y + 165))
        cl = render_pixel_text(self.font_status, "MINES COUNT", C.MINES_TEXT, scale=2)
        self.screen.blit(cl, (panel.centerx - cl.get_width() // 2, panel.y + 310))
        note = render_pixel_text(self.font_small, "Settings apply immediately to the next new board", C.MINES_ACCENT_LIGHT, scale=2)
        self.screen.blit(note, (panel.centerx - note.get_width() // 2, panel.y + 458))
        mp = self._logical_mouse_pos()
        for b in self._get_mines_settings_buttons():
            self._draw_mines_button(b, b["rect"].collidepoint(mp), self.mines_pressed_action == b["action"])
