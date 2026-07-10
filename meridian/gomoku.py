from .common import *


class GomokuMixin:
    def _init_gomoku(self):
        self.board_size = DEFAULT_SIZE
        self.board = Board(self.board_size)
        self.hover_pos = None
        self.win_alpha = 0
        self.shake_duration = 0
        self.shake_x = 0
        self.shake_y = 0
        self.preview_active = False
        self.preview_cell = None
        self.preview_x = 0.0
        self.preview_y = 0.0
        self.preview_target_x = 0.0
        self.preview_target_y = 0.0
        self.preview_player = 1
        self.ripples = []
        self.invalid_marks = []
        self.occupied_hover_pos = None
        self.undo_animations = []
        self.win_line_frame = 0
        self.win_line_active = False
        self.win_stone_flash_frame = 0
        self.win_stone_flash_active = False
        self.win_particle_burst_index = -1
        self.pressed_button_action = None
        self.end_page_delay = 0
        self.end_panel_anim_frame = 0
        self.end_text_flash_tick = 0
        self.end_overlay_alpha = 0
        self.animations = []
        self.particles = []
        self.black_wins = 0
        self.white_wins = 0
        self.draws = 0
        self._win_scored = False
        self.wood_bg = create_wood_texture(WINDOW_W, WINDOW_H)
        self.menu_logo_text = "GOMOKU"
        self.menu_logo_scale = 3
        self.menu_logo_phase = [0.00, 0.87, 1.76, 2.43, 3.39, 4.12]
        self.menu_logo_swing_amp = [4.8, 4.2, 5.0, 4.4, 4.7, 4.1]
        self.menu_logo_micro_amp = [0.22, 0.18, 0.24, 0.20, 0.22, 0.18]
        self.menu_logo_rope_len = [22, 21, 23, 22, 22, 21]
        self.menu_logo_gap = 6
        self.menu_logo_beam_y = 92
        self.menu_logo_letters = []
        self._build_menu_logo_assets()
        self._rebuild_stone_assets()
        self._build_menu_buttons()
        self.end_btns = []
        self.win_overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)

    def _rebuild_stone_assets(self):
        stone_sz = self.board.stone_size
        base = max(4, stone_sz // 4)
        black_small = create_pixel_stone(C.BLACK_STONE, C.BLACK_HL, C.BLACK_SH, base)
        white_small = create_pixel_stone(C.WHITE_STONE, C.WHITE_HL, C.WHITE_SH, base)
        self.stone_black_img = pygame.transform.scale(black_small, (stone_sz, stone_sz))
        self.stone_white_img = pygame.transform.scale(white_small, (stone_sz, stone_sz))
        self.hint_black = self._make_ghost(self.stone_black_img)
        self.hint_white = self._make_ghost(self.stone_white_img)

    def _build_menu_logo_assets(self):
        self.menu_logo_letters = []

        for ch in self.menu_logo_text:
            letter = render_pixel_text(self.font_menu_title, ch, C.GOLD_LIGHT, scale=self.menu_logo_scale)
            shadow = render_pixel_text(self.font_menu_title, ch, C.OUTLINE, scale=self.menu_logo_scale)

            # 淇锛氱缉灏忓悐鐗屽唴杈硅窛锛岃鏁翠綋瀹藉害鍙帶
            panel_pad_x = 10
            panel_pad_y = 9

            panel_w = max(48, letter.get_width() + panel_pad_x * 2)
            panel_h = max(56, letter.get_height() + panel_pad_y * 2 + 10)

            surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)

            # 鍚婄墝涓讳綋
            plaque_rect = pygame.Rect(4, 12, panel_w - 8, panel_h - 16)

            pygame.draw.rect(surf, C.OUTLINE, plaque_rect)
            pygame.draw.rect(surf, C.GOLD_DARK, plaque_rect.inflate(-4, -4))
            pygame.draw.rect(surf, C.RED, plaque_rect.inflate(-8, -8))
            pygame.draw.rect(surf, C.RED_LIGHT, plaque_rect.inflate(-12, -12), 1)

            # 椤堕儴閲戝睘鎸傜墖
            # 淇锛氭寕鐗囩洿鎺ュ睘浜庡悐鐗屾湰浣擄紝缁冲瓙浼氱‖杩炴帴鍒拌繖閲?
            cap_w = 16
            cap_h = 8
            cap_x = panel_w // 2 - cap_w // 2
            cap_y = 5
            cap_rect = pygame.Rect(cap_x, cap_y, cap_w, cap_h)

            pygame.draw.rect(surf, C.OUTLINE, cap_rect)
            pygame.draw.rect(surf, C.GOLD, cap_rect.inflate(-4, -3))

            # 鎸傜偣浣嶇疆锛氳繖鏄悗闈?纭繛鎺?鐨勫叧閿?
            hook_local_x = panel_w // 2
            hook_local_y = cap_y

            # 鎸傚瓟灏忕偣
            pygame.draw.rect(surf, C.OUTLINE, (hook_local_x - 1, cap_y + 3, 2, 2))

            # 宸﹀彸閾嗛拤
            pygame.draw.rect(surf, C.OUTLINE, (plaque_rect.x + 6, plaque_rect.y + 6, 4, 4))
            pygame.draw.rect(surf, C.OUTLINE, (plaque_rect.right - 10, plaque_rect.y + 6, 4, 4))
            pygame.draw.rect(surf, C.GOLD_LIGHT, (plaque_rect.x + 7, plaque_rect.y + 7, 2, 2))
            pygame.draw.rect(surf, C.GOLD_LIGHT, (plaque_rect.right - 9, plaque_rect.y + 7, 2, 2))

            # 瀛楁瘝
            lx = (panel_w - letter.get_width()) // 2
            ly = plaque_rect.y + (plaque_rect.height - letter.get_height()) // 2 + 2

            surf.blit(shadow, (lx + 2, ly + 2))
            surf.blit(letter, (lx, ly))

            self.menu_logo_letters.append({
                "char": ch,
                "surface": surf,
                "width": panel_w,
                "height": panel_h,
                "hook_local_x": hook_local_x,
                "hook_local_y": hook_local_y,
            })

    def _rotate_local_point(self, x, y, cx, cy, angle_deg):
        rad = math.radians(angle_deg)
        dx = x - cx
        dy = y - cy

        rx = dx * math.cos(rad) - dy * math.sin(rad)
        ry = dx * math.sin(rad) + dy * math.cos(rad)

        return cx + rx, cy + ry

    def _rotate_point_around(self, x, y, pivot_x, pivot_y, angle_deg):
        rad = math.radians(angle_deg)
        dx = x - pivot_x
        dy = y - pivot_y

        rx = dx * math.cos(rad) - dy * math.sin(rad)
        ry = dx * math.sin(rad) + dy * math.cos(rad)

        return pivot_x + rx, pivot_y + ry

    def _draw_menu_logo_beam(self, left_x, right_x, y):
        beam_rect = pygame.Rect(int(left_x), int(y - 5), int(right_x - left_x), 10)

        pygame.draw.rect(self.screen, C.OUTLINE, beam_rect)
        pygame.draw.rect(self.screen, C.GOLD_DARK, beam_rect.inflate(-4, -4))

        # 妯楂樺厜鍜屾殫绾?
        pygame.draw.line(
            self.screen,
            C.GOLD_LIGHT,
            (int(left_x + 4), int(y - 2)),
            (int(right_x - 4), int(y - 2)),
            1
        )
        pygame.draw.line(
            self.screen,
            C.BTN_BORDER,
            (int(left_x + 4), int(y + 2)),
            (int(right_x - 4), int(y + 2)),
            1
        )

        # 涓ょ鍥哄畾鍧?
        pygame.draw.rect(self.screen, C.OUTLINE, (int(left_x - 5), int(y - 8), 10, 16))
        pygame.draw.rect(self.screen, C.OUTLINE, (int(right_x - 5), int(y - 8), 10, 16))
        pygame.draw.rect(self.screen, C.GOLD, (int(left_x - 2), int(y - 5), 4, 10))
        pygame.draw.rect(self.screen, C.GOLD, (int(right_x - 2), int(y - 5), 4, 10))

    def _draw_menu_logo(self):
        if not self.menu_logo_letters:
            return

        gap = self.menu_logo_gap
        beam_y = self.menu_logo_beam_y

        total_w = sum(item["width"] for item in self.menu_logo_letters) + gap * (len(self.menu_logo_letters) - 1)

        # 淇锛氱‘淇濇暣涓?GOMOKU 涓嶄細瓒呭嚭鑿滃崟闈㈡澘杈圭晫
        max_logo_w = WINDOW_W - 120

        if total_w > max_logo_w:
            gap = 4
            total_w = sum(item["width"] for item in self.menu_logo_letters) + gap * (len(self.menu_logo_letters) - 1)

        start_x = (WINDOW_W - total_w) // 2

        # 璁＄畻姣忎釜鍚婄墝鐨勬Ы浣?
        slots = []
        x = start_x

        for item in self.menu_logo_letters:
            slots.append((x, item))
            x += item["width"] + gap

        beam_left = max(54, start_x - 10)
        beam_right = min(WINDOW_W - 54, start_x + total_w + 10)

        self._draw_menu_logo_beam(beam_left, beam_right, beam_y)

        for i, (slot_x, item) in enumerate(slots):
            surf = item["surface"]
            w = item["width"]
            h = item["height"]

            phase = self.menu_logo_phase[i % len(self.menu_logo_phase)]
            amp = self.menu_logo_swing_amp[i % len(self.menu_logo_swing_amp)]
            micro_amp = self.menu_logo_micro_amp[i % len(self.menu_logo_micro_amp)]
            rope_len = self.menu_logo_rope_len[i % len(self.menu_logo_rope_len)]

            # 鑷劧杞绘憜锛氬箙搴﹀皬銆侀€熷害鎱€佹瘡涓瓧姣嶄笉鍚屾
            main_swing = math.sin(self.anim_tick * 0.018 + phase) * amp
            secondary_swing = math.sin(self.anim_tick * 0.009 + phase * 1.7) * (amp * 0.14)
            micro_swing = math.sin(self.anim_tick * 0.041 + phase * 2.6) * micro_amp

            angle = main_swing + secondary_swing + micro_swing

            # 妯涓婄殑鍥哄畾鐐?
            anchor_x = slot_x + w / 2
            anchor_y = beam_y

            # 鍚婄墝鎸傜偣鐨勪笘鐣屼綅缃?
            # Move the hook along the rope arc so rope and plaque behave as
            # one pendulum instead of two disconnected animations.
            pendulum_rad = math.radians(angle)
            hook_x = anchor_x + math.sin(pendulum_rad) * rope_len
            hook_y = anchor_y + math.cos(pendulum_rad) * rope_len

            # 鏃嬭浆鍚婄墝
            rotated = pygame.transform.rotozoom(surf, -angle, 1.0)

            # ============================================================
            #  纭繛鎺ユ牳蹇冿細
            #  涓嶅啀璁╃嚎鍘昏拷鏃嬭浆鍚庣殑鐗屽瓙锛?
            #  鑰屾槸璁╂棆杞悗鐨勭墝瀛愭寕鐐规案杩滃榻?hook_x / hook_y銆?
            # ============================================================

            local_hook_x = item["hook_local_x"]
            local_hook_y = item["hook_local_y"]

            # 鍘熷浘涓紝鎸傜偣鐩稿浜庡浘鐗囦腑蹇冪殑鍋忕Щ
            dx = local_hook_x - w / 2
            dy = local_hook_y - h / 2

            rad = math.radians(-angle)

            # 鎸傜偣鍋忕Щ鏃嬭浆鍚庣殑鍊?
            rotated_dx = dx * math.cos(rad) - dy * math.sin(rad)
            rotated_dy = dx * math.sin(rad) + dy * math.cos(rad)

            # 鏃嬭浆鍚庡浘鐗囦腑蹇冨簲璇ュ湪鍝噷锛屾墠鑳借鎸傜偣绮剧‘钀藉湪 hook_x/hook_y
            center_x = hook_x - rotated_dx
            center_y = hook_y - rotated_dy

            rect = rotated.get_rect(center=(int(center_x), int(center_y)))

            # 鍚婄怀锛氫粠妯寤朵几鍒板悐鐗屾寕鐗囧唴閮?
            # 缁冲瓙澶氱敾 8px 绌垮叆鎸傜墖鍖猴紝鐒跺悗鍚婄墝鐩栧湪涓婇潰锛岃瑙変笂灏辨槸涓€浣?
            rope_overlap = 7
            rope_end_x = hook_x + math.sin(pendulum_rad) * rope_overlap
            rope_end_y = hook_y + math.cos(pendulum_rad) * rope_overlap

            pygame.draw.line(
                self.screen,
                C.OUTLINE,
                (int(anchor_x), int(anchor_y)),
                (int(rope_end_x), int(rope_end_y)),
                3
            )
            pygame.draw.line(
                self.screen,
                C.CREAM_DARK,
                (int(anchor_x), int(anchor_y)),
                (int(rope_end_x), int(rope_end_y)),
                1
            )

            # 妯鍥哄畾閽?
            pygame.draw.rect(
                self.screen,
                C.OUTLINE,
                (int(anchor_x - 2), int(anchor_y - 2), 4, 4)
            )
            pygame.draw.rect(
                self.screen,
                C.GOLD_LIGHT,
                (int(anchor_x - 1), int(anchor_y - 1), 2, 2)
            )

            # 鍚婄墝鐢诲湪缁冲瓙涓婂眰锛屾寕鐗囩洊浣忕怀澶达紝褰㈡垚纭繛鎺?
            self.screen.blit(rotated, rect.topleft)

    def _make_ghost(self, surf):
        g = surf.copy()
        g.set_alpha(90)
        return g

    def _build_menu_buttons(self):
        """Create button rects for the menu."""
        self.menu_btns = []  # list of {rect, label, action, selected}
        self.btn_selected_size = DEFAULT_SIZE

    def _get_menu_buttons(self):
        """Return current menu button definitions."""
        cx = WINDOW_W // 2
        btns = []

        btn_w, btn_h = 180, 46
        gap = 18

        # 淇锛氫富鑿滃崟涓嶅啀鏀炬鐩樺ぇ灏忛€夋嫨锛岄伩鍏嶆嫢鎸?
        start_y = 310

        has_saved = self.save_data.get("progress", {}).get("gomoku", {}).get("run_active", False)
        if has_saved:
            btns.append({
                "rect": pygame.Rect(cx - btn_w // 2, start_y, btn_w, btn_h),
                "label": "CONTINUE",
                "action": "continue",
                "selected": False,
            })
            start_y += btn_h + gap

        if self.board.has_moves() and self.board.winner == 0:
            main_label = "RESUME"
            main_action = "resume"
        else:
            main_label = "START"
            main_action = "start"

        btns.append({
            "rect": pygame.Rect(cx - btn_w // 2, start_y, btn_w, btn_h),
            "label": main_label,
            "action": main_action,
            "selected": False,
        })

        btns.append({
            "rect": pygame.Rect(cx - btn_w // 2, start_y + btn_h + gap, btn_w, btn_h),
            "label": "SETTINGS",
            "action": "settings",
            "selected": False,
        })

        return btns

    def _get_end_buttons(self):
        cx = WINDOW_W // 2

        btn_w = 180
        btn_h = 42
        gap = 12

        # 淇锛氭寜閽暣浣撲笅绉伙紝缁欐瘮鍒嗗拰鎻愮ず鐣欑┖闂?
        start_y = 500

        return [
            {
                "rect": pygame.Rect(cx - btn_w // 2, start_y, btn_w, btn_h),
                "label": "PLAY AGAIN",
                "action": "again",
                "selected": False,
            },
            {
                "rect": pygame.Rect(cx - btn_w // 2, start_y + btn_h + gap, btn_w, btn_h),
                "label": "MENU",
                "action": "menu",
                "selected": False,
            },
            {
                "rect": pygame.Rect(cx - btn_w // 2, start_y + (btn_h + gap) * 2, btn_w, btn_h),
                "label": "DESKTOP",
                "action": "quit",
                "selected": False,
            },
        ]

    def _get_settings_buttons(self):
        cx = WINDOW_W // 2
        btns = []

        # 妫嬬洏澶у皬鎸夐挳
        size_btn_w = 120
        size_btn_h = 44
        size_gap = 22

        total_w = len(BOARD_SIZE_CHOICES) * size_btn_w + (len(BOARD_SIZE_CHOICES) - 1) * size_gap
        start_x = cx - total_w // 2

        # 淇锛氭寜閽斁鍦?BOARD SIZE 鏍囬涓嬮潰锛屼笉鍐嶅帇浣忔枃瀛?
        size_y = 310

        for i, sz in enumerate(BOARD_SIZE_CHOICES):
            bx = start_x + i * (size_btn_w + size_gap)
            btns.append({
                "rect": pygame.Rect(bx, size_y, size_btn_w, size_btn_h),
                "label": f"{sz} x {sz}",
                "action": f"settings_size_{sz}",
                "selected": self.board_size == sz,
            })

        # BACK 鎸夐挳鏀惧埌搴曢儴鍖哄煙锛屽拰鎻愮ず鏂囧瓧鎷夊紑
        back_w = 200
        back_h = 48
        back_y = 520

        btns.append({
            "rect": pygame.Rect(cx - back_w // 2, back_y, back_w, back_h),
            "label": "BACK",
            "action": "back",
            "selected": False,
        })

        return btns

    def _handle_menu_event(self, event):
        if self.prologue_active:
            self._handle_prologue_event(event)
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_desktop()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            btns = self._get_menu_buttons()
            for b in btns:
                if b["rect"].collidepoint(event.pos):
                    self.pressed_button_action = b["action"]
                    return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            btns = self._get_menu_buttons()
            for b in btns:
                if b["rect"].collidepoint(event.pos) and self.pressed_button_action == b["action"]:
                    action = b["action"]

                    if action == "start":
                        self._start_new_game()
                        self._start_transition(self.PLAYING, "fade")
                    elif action == "continue":
                        state = self._pending_run_states.pop("gomoku", None)
                        self._start_new_game(restore_state=state)
                        self._start_transition(self.PLAYING, "fade")
                    elif action == "resume":
                        self._start_transition(self.PLAYING, "fade")
                    elif action == "settings":
                        self._start_transition(self.SETTINGS, "fade")

                    self.pressed_button_action = None
                    return

            self.pressed_button_action = None

    def _handle_game_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._update_hover(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.board.winner == 0:
                r, c = self._pos_to_cell(event.pos)

                if r is not None:
                    # 淇锛氱偣鍑诲凡鏈夋瀛愭椂锛屼笉鍐嶆棤鍙嶉锛岃€屾槸鍑虹幇闈炴硶钀藉瓙鎻愮ず
                    if not self.board.is_empty(r, c):
                        self._add_invalid_mark(r, c)
                        return

                    if self.board.place_stone(r, c):
                        self.audio.play("gomoku_place")
                        self._add_drop_animation(r, c, self.board.grid[r][c])
                        self._add_ripple(r, c)

                        # 钀藉瓙鍚庡綋鍓嶇帺瀹朵細鍒囨崲锛屾墍浠ュ埛鏂伴瑙堢帺瀹?
                        self.preview_player = self.board.current_player

                        if self.board.winner != 0:
                            self._on_win()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._start_new_game()
            elif event.key == pygame.K_u:
                self._do_undo()
            elif event.key == pygame.K_ESCAPE:
                self._go_desktop()

    def _handle_end_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_transition(self.MENU, "fade")
                self.animations.clear()
                self.particles.clear()
                self.ripples.clear()
                self.invalid_marks.clear()
                self.undo_animations.clear()
                self.shake_duration = 0
                self.occupied_hover_pos = None
                self.pressed_button_action = None
            elif event.key == pygame.K_r:
                self._start_new_game()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_end_buttons():
                if b["rect"].collidepoint(event.pos):
                    self.pressed_button_action = b["action"]
                    return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_end_buttons():
                if b["rect"].collidepoint(event.pos) and self.pressed_button_action == b["action"]:
                    action = b["action"]

                    if action == "again":
                        self._start_new_game()
                        self._start_transition(self.PLAYING, "fade")
                    elif action == "menu":
                        self._start_transition(self.MENU, "fade")
                        self.animations.clear()
                        self.particles.clear()
                        self.ripples.clear()
                        self.invalid_marks.clear()
                        self.undo_animations.clear()
                        self.shake_duration = 0
                        self.occupied_hover_pos = None
                        self.pressed_button_action = None
                    elif action == "quit":
                        # 鍥炲埌妗岄潰锛屼笉鍏抽棴绋嬪簭
                        self._go_desktop()

    def _handle_settings_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._start_transition(self.MENU, "fade")
                self.pressed_button_action = None
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self._get_settings_buttons():
                if b["rect"].collidepoint(event.pos):
                    self.pressed_button_action = b["action"]
                    return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for b in self._get_settings_buttons():
                if b["rect"].collidepoint(event.pos) and self.pressed_button_action == b["action"]:
                    action = b["action"]

                    if action == "back":
                        self._start_transition(self.MENU, "fade")

                    elif action.startswith("settings_size_"):
                        new_size = int(action.split("_")[-1])
                        self.board_size = new_size

                        # 娌℃湁杩涜涓殑妫嬪眬鏃讹紝绔嬪嵆鍚屾妫嬬洏瀵硅薄
                        if not self.board.has_moves() or self.board.winner != 0:
                            self.board = Board(self.board_size)
                            self._rebuild_stone_assets()

                    self.pressed_button_action = None
                    return

            self.pressed_button_action = None

    def _start_new_game(self, restore_state=None):
        self.board = Board(self.board_size)
        if restore_state:
            self.board.grid = restore_state["grid"]
            self.board.current_player = restore_state["current_player"]
            self.board.move_history = restore_state["move_history"]
            self.board.move_count = restore_state["move_count"]
            self.board.last_move = restore_state.get("last_move")
            self.board.winner = restore_state.get("winner", 0)
            self.board.win_stones = restore_state.get("win_stones", [])
        self._rebuild_stone_assets()
        self.state = self.PLAYING
        self.hover_pos = None
        self.animations.clear()
        self.particles.clear()
        self.ripples.clear()
        self.invalid_marks.clear()
        self.undo_animations.clear()

        self.shake_duration = 0
        self.win_alpha = 0
        self._win_scored = False
        self.gomoku_stats_completed = False
        self._record_stat("gomoku", "games_started")

        # 娓呯悊纾佸惛棰勮鐘舵€?
        self.preview_active = False
        self.preview_cell = None
        self.preview_x = 0.0
        self.preview_y = 0.0
        self.preview_target_x = 0.0
        self.preview_target_y = 0.0
        self.preview_player = self.board.current_player

        self.occupied_hover_pos = None

        # 娓呯悊鑳滃埄婕斿嚭
        self.win_line_frame = 0
        self.win_line_active = False
        self.win_stone_flash_frame = 0
        self.win_stone_flash_active = False
        self.win_particle_burst_index = -1

        # 娓呯悊鎸夐挳鐐瑰嚮鐘舵€?
        self.pressed_button_action = None

        # 娓呯悊缁撴潫椤靛姩鐢?
        self.end_page_delay = 0
        self.end_panel_anim_frame = 0
        self.end_text_flash_tick = 0
        self.end_overlay_alpha = 0
        self._clear_run_state("gomoku")

    def _capture_gomoku_run_state(self):
        return {
            "grid": [row[:] for row in self.board.grid],
            "current_player": self.board.current_player,
            "move_history": self.board.move_history[:],
            "move_count": self.board.move_count,
            "last_move": self.board.last_move,
            "winner": self.board.winner,
            "win_stones": self.board.win_stones[:],
        }

    def _do_undo(self):
        # Can't undo during animations
        if self.animations or self.undo_animations:
            return

        # 缁撴潫椤甸潰涓嶅厑璁告倲妫嬶紝閬垮厤鑳滃埄璁″垎鍜岀姸鎬佹贩涔?
        if self.state == self.END:
            return

        if not self.board.move_history:
            return

        was_win = self.board.winner

        # 鍏堟嬁鍒版渶鍚庝竴鎵嬩俊鎭紝鐢ㄤ簬鎾斁鍔ㄧ敾
        row, col, player = self.board.move_history[-1]

        if self.board.undo():
            self._record_stat("gomoku", "undos")
            # 鍒犻櫎妫嬪瓙鍚庯紝鐢?undo_animations 缁х画鎶婂畠鐢诲嚭鏉ワ紝
            # 杩欐牱瑙嗚涓婂氨鏄?鎶栧姩 0.3s 鍚庣缉灏忔贰鍑?
            self.undo_animations.append({
                "r": row,
                "c": col,
                "player": player,
                "frame": 0,
                "max_frames": UNDO_ANIM_MAX_FRAMES,
            })

            self.win_alpha = 0
            self.particles.clear()
            self.shake_duration = 0
            self.invalid_marks.clear()

            # 娓呯悊鑳滃埄婕斿嚭鐘舵€?
            self.win_line_frame = 0
            self.win_line_active = False
            self.win_stone_flash_frame = 0
            self.win_stone_flash_active = False
            self.win_particle_burst_index = -1
            self.end_page_delay = 0
            self.end_panel_anim_frame = 0
            self.end_text_flash_tick = 0
            self.end_overlay_alpha = 0

            if was_win != 0 and self._win_scored:
                if was_win == 1:
                    self.black_wins = max(0, self.black_wins - 1)
                elif was_win == 2:
                    self.white_wins = max(0, self.white_wins - 1)
                else:
                    self.draws = max(0, self.draws - 1)

                self._win_scored = False

    def _on_win(self):
        self.audio.play("gomoku_line")
        self.audio.play_gameover("gomoku")
        self._spawn_win_particles()
        self.shake_duration = 18

        # 鍚姩鑳滃埄杩炵嚎
        self.win_line_active = True
        self.win_line_frame = 0

        # 鍚姩鑳滃埄妫嬪瓙渚濇闂儊
        self.win_stone_flash_active = True
        self.win_stone_flash_frame = 0
        self.win_particle_burst_index = -1

        # 绛変簲杩炵嚎 + 渚濇闂儊澶ц嚧鎾畬锛屽啀杩涘叆缁撴潫椤?
        self.end_page_delay = max(WIN_LINE_MAX_FRAMES, WIN_STONE_FLASH_MAX_FRAMES) + 24

        # 娓呯┖缁撴潫椤靛姩鐢荤姸鎬侊紝纭繚姣忔鑳滃埄閮介噸鏂板脊鍑?
        self.end_panel_anim_frame = 0
        self.end_text_flash_tick = 0
        self.end_overlay_alpha = 0

        if not self._win_scored:
            if self.board.winner == 1:
                self.black_wins += 1
            elif self.board.winner == 2:
                self.white_wins += 1
            else:
                self.draws += 1

            self._win_scored = True
        if not getattr(self, "gomoku_stats_completed", False):
            self.gomoku_stats_completed = True
            self._record_stat("gomoku", "games_completed")
            if self.board.winner == 1:
                self._record_stat("gomoku", "black_wins")
            elif self.board.winner == 2:
                self._record_stat("gomoku", "white_wins")
            else:
                self._record_stat("gomoku", "draws")
            if self.board_size == 19 and self.board.winner in (1, 2):
                self._record_stat("gomoku", "wins_on_19")

    def _add_drop_animation(self, r, c, player):
        self.animations.append({
            "type": "drop",
            "r": r, "c": c, "player": player,
            "frame": 0, "max_frames": 14,
        })

    def _add_ripple(self, r, c):
        self.ripples.append({
            "r": r,
            "c": c,
            "frame": 0,
            "max_frames": RIPPLE_MAX_FRAMES,
        })

    def _add_invalid_mark(self, r, c):
        # 濡傛灉鍚屼竴涓綅缃凡缁忔湁闈炴硶鎻愮ず锛屽氨鍒锋柊瀹冿紝鑰屼笉鏄噸澶嶅爢鍙?
        for mark in self.invalid_marks:
            if mark["r"] == r and mark["c"] == c:
                mark["frame"] = 0
                return

        self.invalid_marks.append({
            "r": r,
            "c": c,
            "frame": 0,
            "max_frames": INVALID_MARK_MAX_FRAMES,
        })

    def _get_ordered_win_stones(self):
        stones = self.board.win_stones[:]
        if not stones:
            return []

        # 妯嚎锛氭寜鍒楁帓搴?
        if len({r for r, c in stones}) == 1:
            return sorted(stones, key=lambda p: p[1])

        # 绔栫嚎锛氭寜琛屾帓搴?
        if len({c for r, c in stones}) == 1:
            return sorted(stones, key=lambda p: p[0])

        # 姝ｆ枩绾挎垨鍙嶆枩绾匡細鎸夎鎺掑簭鍗冲彲寰楀埌浠庝竴绔埌鍙︿竴绔殑椤哄簭
        return sorted(stones, key=lambda p: p[0])

    def _emit_particle_burst(self, x, y, count, speed_min=1.6, speed_max=5.8, life_min=18, life_max=38):
        colors = [C.GOLD_LIGHT, C.GOLD, C.RED_LIGHT, C.CREAM, C.GOLD_DARK]

        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(speed_min, speed_max)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(1.0, 2.6)
            life = random.randint(life_min, life_max)
            self.particles.append(
                Particle(x, y, random.choice(colors), vx, vy, life)
            )

    def _spawn_win_particles(self):
        for r, c in self._get_ordered_win_stones():
            sx = BOARD_X + c * self.board.cell_size
            sy = BOARD_Y + r * self.board.cell_size
            self._emit_particle_burst(sx, sy, 18, speed_min=1.8, speed_max=6.2, life_min=18, life_max=42)

    def _spawn_win_stone_burst(self, r, c):
        sx = BOARD_X + c * self.board.cell_size
        sy = BOARD_Y + r * self.board.cell_size
        self._emit_particle_burst(sx, sy, 10, speed_min=1.2, speed_max=4.2, life_min=14, life_max=28)

    def _update_hover(self, mouse_pos):
        mx, my = mouse_pos
        cell = self.board.cell_size

        # 鎵惧埌绂婚紶鏍囨渶杩戠殑妫嬬洏浜ゅ弶鐐?
        c = round((mx - BOARD_X) / cell)
        r = round((my - BOARD_Y) / cell)

        if not (0 <= r < self.board.board_count and 0 <= c < self.board.board_count):
            self.hover_pos = None
            self.preview_active = False
            self.preview_cell = None
            return

        target_x = BOARD_X + c * cell
        target_y = BOARD_Y + r * cell

        dx = mx - target_x
        dy = my - target_y
        dist = math.sqrt(dx * dx + dy * dy)

        # 榧犳爣杩涘叆浜ゅ弶鐐归檮杩?
        if dist <= MAGNET_RADIUS and self.board.winner == 0:
            # 鍙惤瀛愪綅缃細姝ｅ父纾佸惛棰勮
            if self.board.is_empty(r, c):
                self.hover_pos = (r, c)
                self.occupied_hover_pos = None

                if not self.preview_active or self.preview_cell != (r, c):
                    self.preview_x = float(mx)
                    self.preview_y = float(my)
                    self.preview_cell = (r, c)

                self.preview_active = True
                self.preview_target_x = float(target_x)
                self.preview_target_y = float(target_y)
                self.preview_player = self.board.current_player

            # 宸叉湁妫嬪瓙浣嶇疆锛氫笉瑕佺獊鐒舵秷澶憋紝鏀逛负鏄剧ず涓嶅彲钀藉瓙鎻愮ず
            else:
                self.hover_pos = None
                self.occupied_hover_pos = (r, c)

                # 棰勮妫嬪瓙涓嶅啀缁х画绉诲姩锛屼絾涔熶笉闇€瑕佸弽澶嶅嚭鐜版秷澶?
                self.preview_active = False
                self.preview_cell = None

        else:
            self.hover_pos = None
            self.occupied_hover_pos = None
            self.preview_active = False
            self.preview_cell = None

    def _pos_to_cell(self, pos):
        mx, my = pos
        cell = self.board.cell_size

        c = round((mx - BOARD_X) / cell)
        r = round((my - BOARD_Y) / cell)

        if not (0 <= r < self.board.board_count and 0 <= c < self.board.board_count):
            return None, None

        ix = BOARD_X + c * cell
        iy = BOARD_Y + r * cell

        dx = mx - ix
        dy = my - iy
        dist = math.sqrt(dx * dx + dy * dy)

        # 淇锛氳惤瀛愯寖鍥村拰纾佸惛鑼冨洿缁熶竴
        if dist <= MAGNET_RADIUS:
            return r, c

        return None, None

    def _draw_stage_background(self):
        self.screen.fill(C.MENU_BG)

        bar_h = 50
        for y, flip in [(0, False), (WINDOW_H - bar_h, True)]:
            for i in range(bar_h):
                t = i / bar_h
                shade = int(20 + 20 * t) if flip else int(40 - 20 * t)
                c = (shade, 5, 3)
                pygame.draw.line(self.screen, c, (0, y + i), (WINDOW_W, y + i))

    def _draw_basic_panel(self, rect, border=4):
        pygame.draw.rect(self.screen, C.MENU_PANEL, rect)
        pygame.draw.rect(self.screen, C.OUTLINE, rect, border)
        pygame.draw.rect(self.screen, C.GOLD_DARK, rect.inflate(-8, -8), 2)

    def _draw_menu(self):
        # ── Prologue check ──
        if self._check_and_show_prologue("gomoku"):
            self._draw_prologue_screen()
            return

        self._draw_stage_background()

        # Center card panel for 16:9 layout
        panel_w = 700
        panel_h = 560
        panel_x = (WINDOW_W - panel_w) // 2
        panel_y = 80
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        self._draw_basic_panel(panel_rect, border=3)

        # Corner decorations
        for cx, cy in [(panel_rect.x, panel_rect.y),
                       (panel_rect.right - 18, panel_rect.y),
                       (panel_rect.x, panel_rect.bottom - 18),
                       (panel_rect.right - 18, panel_rect.bottom - 18)]:
            pygame.draw.rect(self.screen, C.OUTLINE, (cx, cy, 18, 18))
            pygame.draw.rect(self.screen, C.GOLD, (cx + 3, cy + 3, 12, 12))
            pygame.draw.rect(self.screen, C.GOLD_LIGHT, (cx + 5, cy + 5, 4, 4))

        # Title
        self._draw_menu_logo()
        if is_chinese():
            subtitle = render_pixel_text(
                self.font_small, "连成五子即可获胜", C.CREAM, scale=2
            )
            self.screen.blit(
                subtitle, (panel_rect.centerx - subtitle.get_width() // 2, 255)
            )

        # Buttons
        mouse_pos = self._logical_mouse_pos()
        btns = self._get_menu_buttons()
        for b in btns:
            hovered = b["rect"].collidepoint(mouse_pos)
            self._draw_menu_button(b, hovered)

        # Score display
        self._draw_menu_scores()

        # Bottom hint
        hint = render_pixel_text(self.font_small, "ESC to Quit", C.GOLD_DARK, scale=2)
        hx = (WINDOW_W - hint.get_width()) // 2
        self.screen.blit(hint, (hx, WINDOW_H - 40))

    def _draw_menu_button(self, btn, hovered):
        rect = btn["rect"].copy()
        action = btn.get("action")

        pressed = self.pressed_button_action == action

        # 鍔ㄦ晥锛氭偓鍋滄椂杞诲井鏀惧ぇ
        if hovered:
            rect = rect.inflate(8, 6)

        # 鍔ㄦ晥锛氭偓鍋滄椂杞诲井涓婁笅娴姩
        if hovered and not pressed:
            float_y = int(math.sin(self.anim_tick * 0.18) * 2)
            rect.y += float_y

        # 鍔ㄦ晥锛氱偣鍑绘椂涓嬪帇
        if pressed:
            rect.y += 4

        # Determine colors based on state
        if btn.get("selected", False):
            fill = C.BTN_SELECT
            border = C.OUTLINE
            text_col = C.OUTLINE
        elif hovered:
            fill = C.BTN_HOVER
            border = C.GOLD_LIGHT
            text_col = C.TEXT
        else:
            fill = C.BTN_NORMAL
            border = C.BTN_BORDER
            text_col = C.TEXT

        # Hover shadow
        if hovered:
            pygame.draw.rect(self.screen, C.OUTLINE, rect.move(4, 4))

        pygame.draw.rect(self.screen, border, rect)
        pygame.draw.rect(self.screen, fill, rect.inflate(-4, -4))

        if btn.get("selected", False):
            pygame.draw.rect(self.screen, C.GOLD_LIGHT, rect.inflate(-8, -8), 1)

        # Hover shine line
        if hovered:
            pygame.draw.line(
                self.screen,
                C.CREAM,
                (rect.x + 8, rect.y + 7),
                (rect.right - 8, rect.y + 7),
                2
            )

        # Label
        label = render_pixel_text(self.font_btn, btn["label"], text_col, scale=2)

        # 淇锛氭寜閽枃瀛楀鏋滃お瀹斤紝鑷姩闄嶄綆缂╂斁
        if label.get_width() > rect.width - 12:
            label = render_pixel_text(self.font_btn, btn["label"], text_col, scale=1)

        lx = rect.centerx - label.get_width() // 2
        ly = rect.centery - label.get_height() // 2

        # 鐐瑰嚮鏃舵枃瀛椾篃璺熺潃涓嬪帇涓€鐐?
        if pressed:
            ly += 1

        self.screen.blit(label, (lx, ly))

    def _draw_panel_title(self, text, y, scale=3):
        title = render_pixel_text(self.font_menu_title, text, C.GOLD_LIGHT, scale=scale)
        shadow = render_pixel_text(self.font_menu_title, text, C.OUTLINE, scale=scale)

        max_w = WINDOW_W - 100
        if title.get_width() > max_w:
            title = render_pixel_text(self.font_menu_title, text, C.GOLD_LIGHT, scale=2)
            shadow = render_pixel_text(self.font_menu_title, text, C.OUTLINE, scale=2)

        x = (WINDOW_W - title.get_width()) // 2

        self.screen.blit(shadow, (x + 3, y + 3))
        self.screen.blit(title, (x, y))

    def _draw_menu_scores(self):
        y = 510

        # Section label
        lbl = render_pixel_text(self.font_status, "SCORES", C.GOLD, scale=2)
        self.screen.blit(lbl, ((WINDOW_W - lbl.get_width()) // 2, y))
        y += 34

        # 淇锛氬師鏉ョ殑璁″垎妗嗗お灏忥紝鏁板瓧鍜屾枃瀛椾細閲嶅彔
        box_w, box_h = 118, 54
        gap = 18
        total_w = 3 * box_w + 2 * gap
        start_x = (WINDOW_W - total_w) // 2

        entries = [
            (self.black_wins, C.BLACK_STONE, "BLACK"),
            (self.white_wins, C.WHITE_STONE, "WHITE"),
            (self.draws, C.GOLD_DARK, "DRAW"),
        ]

        for i, (score, stone_col, label_text) in enumerate(entries):
            bx = start_x + i * (box_w + gap)
            rect = pygame.Rect(bx, y, box_w, box_h)

            pygame.draw.rect(self.screen, C.MENU_BG, rect)
            pygame.draw.rect(self.screen, C.OUTLINE, rect, 2)

            # Mini stone icon
            stone_rect = pygame.Rect(bx + 8, y + 7, 12, 12)
            pygame.draw.rect(self.screen, stone_col, stone_rect)
            pygame.draw.rect(self.screen, C.OUTLINE, stone_rect, 1)

            # Label
            # 淇锛氭爣绛炬斁鍒板乏涓嬭锛岄伩鍏嶅拰鏁板瓧閲嶅彔
            lbl = render_pixel_text(self.font_small, label_text, C.CREAM, scale=2)

            if lbl.get_width() > box_w - 16:
                lbl = render_pixel_text(self.font_small, label_text, C.CREAM, scale=1)

            self.screen.blit(lbl, (bx + 10, y + box_h - lbl.get_height() - 6))

            # Score number
            # 淇锛氭暟瀛楃缉鏀句粠 3 鏀规垚 2锛屽苟鏀惧埌鍙充晶
            num = render_pixel_text(self.font_menu_title, str(score), C.GOLD_LIGHT, scale=2)

            nx = bx + box_w - num.get_width() - 10
            ny = y + 6

            self.screen.blit(num, (nx, ny))

    def _draw_end_page(self):
        # 鍏堢敾妫嬬洏鑳屾櫙
        self._draw_game()

        # 鍗婇€忔槑鏆楄壊閬僵
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((20, 8, 4, 205))
        self.screen.blit(overlay, (0, 0))

        # ============================================================
        #  淇锛氱粨鏉熼〉闈㈡澘鍋氬ぇ锛岄噸鏂版帓鐗?
        # ============================================================
        panel_w = WINDOW_W - 92
        panel_h = 590
        panel_x = (WINDOW_W - panel_w) // 2
        panel_y = 78
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        pygame.draw.rect(self.screen, C.MENU_PANEL, panel_rect)
        pygame.draw.rect(self.screen, C.OUTLINE, panel_rect, 4)
        pygame.draw.rect(self.screen, C.GOLD_DARK, panel_rect.inflate(-8, -8), 2)

        # 鍥涜瑁呴グ
        corner_size = 20
        for cx, cy in [
            (panel_rect.x, panel_rect.y),
            (panel_rect.right - corner_size, panel_rect.y),
            (panel_rect.x, panel_rect.bottom - corner_size),
            (panel_rect.right - corner_size, panel_rect.bottom - corner_size),
        ]:
            pygame.draw.rect(self.screen, C.OUTLINE, (cx, cy, corner_size, corner_size))
            pygame.draw.rect(self.screen, C.GOLD, (cx + 4, cy + 4, corner_size - 8, corner_size - 8))
            pygame.draw.rect(self.screen, C.GOLD_LIGHT, (cx + 7, cy + 7, 5, 5))

        # ============================================================
        #  鏍囬鍜屽壇鏍囬
        # ============================================================
        if self.board.winner == -1:
            result_text = "DRAW"
            sub_text = "NO WINNER THIS ROUND"
        elif self.board.winner == 1:
            result_text = "BLACK_WINS_RESULT"
            sub_text = "BLACK TAKES THE ROUND"
        else:
            result_text = "WHITE_WINS_RESULT"
            sub_text = "WHITE TAKES THE ROUND"

        title = render_pixel_text(self.font_menu_title, result_text, C.GOLD_LIGHT, scale=3)
        shadow = render_pixel_text(self.font_menu_title, result_text, C.OUTLINE, scale=3)

        if title.get_width() > panel_rect.width - 80:
            title = render_pixel_text(self.font_menu_title, result_text, C.GOLD_LIGHT, scale=2)
            shadow = render_pixel_text(self.font_menu_title, result_text, C.OUTLINE, scale=2)

        title_x = panel_rect.centerx - title.get_width() // 2
        title_y = panel_rect.y + 42

        self.screen.blit(shadow, (title_x + 3, title_y + 3))
        self.screen.blit(title, (title_x, title_y))

        sub = render_pixel_text(self.font_status, sub_text, C.CREAM, scale=2)
        self.screen.blit(sub, (panel_rect.centerx - sub.get_width() // 2, panel_rect.y + 106))

        # 鍒嗛殧绾?
        line_y = panel_rect.y + 154
        pygame.draw.line(
            self.screen,
            C.GOLD_DARK,
            (panel_rect.x + 40, line_y),
            (panel_rect.right - 40, line_y),
            3
        )
        pygame.draw.line(
            self.screen,
            C.OUTLINE,
            (panel_rect.x + 40, line_y + 4),
            (panel_rect.right - 40, line_y + 4),
            2
        )

        # ============================================================
        #  鑳滆€呮瀛愬睍绀?
        # ============================================================
        showcase_box_w = 92
        showcase_box_h = 92
        showcase_box_x = panel_rect.centerx - showcase_box_w // 2
        showcase_box_y = panel_rect.y + 176

        pygame.draw.rect(
            self.screen,
            C.OUTLINE,
            (showcase_box_x, showcase_box_y, showcase_box_w, showcase_box_h),
            2
        )
        pygame.draw.rect(
            self.screen,
            C.GOLD_DARK,
            (showcase_box_x + 4, showcase_box_y + 4, showcase_box_w - 8, showcase_box_h - 8),
            2
        )

        bob = int(math.sin(self.anim_tick * 0.12) * 3)

        if self.board.winner == 1:
            big_sz = 70
            big = pygame.transform.scale(self.stone_black_img, (big_sz, big_sz))
            self.screen.blit(
                big,
                (
                    panel_rect.centerx - big_sz // 2,
                    showcase_box_y + (showcase_box_h - big_sz) // 2 + bob
                )
            )

        elif self.board.winner == 2:
            big_sz = 70
            big = pygame.transform.scale(self.stone_white_img, (big_sz, big_sz))
            self.screen.blit(
                big,
                (
                    panel_rect.centerx - big_sz // 2,
                    showcase_box_y + (showcase_box_h - big_sz) // 2 + bob
                )
            )

        else:
            big_sz = 56
            black_big = pygame.transform.scale(self.stone_black_img, (big_sz, big_sz))
            white_big = pygame.transform.scale(self.stone_white_img, (big_sz, big_sz))

            self.screen.blit(
                black_big,
                (
                    panel_rect.centerx - big_sz - 8,
                    showcase_box_y + (showcase_box_h - big_sz) // 2 + bob
                )
            )
            self.screen.blit(
                white_big,
                (
                    panel_rect.centerx + 8,
                    showcase_box_y + (showcase_box_h - big_sz) // 2 - bob
                )
            )

        # ============================================================
        #  鍒嗘暟鍖哄煙
        # ============================================================
        score_title_y = panel_rect.y + 300
        score_value_y = panel_rect.y + 338

        score_title = render_pixel_text(self.font_status, "SCORES", C.GOLD, scale=2)
        self.screen.blit(
            score_title,
            (panel_rect.centerx - score_title.get_width() // 2, score_title_y)
        )

        score_text = f"B:{self.black_wins}    W:{self.white_wins}    D:{self.draws}"
        score = render_pixel_text(self.font_status, score_text, C.CREAM, scale=2)

        if score.get_width() > panel_rect.width - 90:
            score = render_pixel_text(self.font_status, score_text, C.CREAM, scale=1)

        self.screen.blit(
            score,
            (panel_rect.centerx - score.get_width() // 2, score_value_y)
        )

        # ============================================================
        #  鎿嶄綔鎻愮ず
        # ============================================================
        # 淇锛氭彁绀哄崟鐙暀涓€琛岋紝骞朵笖鍜屾寜閽尯鎷夊紑璺濈
        hint_y = panel_rect.y + 382
        hint = render_pixel_text(self.font_small, "R: Restart    ESC: Menu", C.GOLD_DARK, scale=2)

        if hint.get_width() > panel_rect.width - 80:
            hint = render_pixel_text(self.font_small, "R: Restart    ESC: Menu", C.GOLD_DARK, scale=1)

        self.screen.blit(
            hint,
            (panel_rect.centerx - hint.get_width() // 2, hint_y)
        )

        # ============================================================
        #  鎸夐挳
        # ============================================================
        mouse_pos = self._logical_mouse_pos()
        for b in self._get_end_buttons():
            hovered = b["rect"].collidepoint(mouse_pos)
            self._draw_menu_button(b, hovered)

    def _draw_settings_page(self):
        self._draw_stage_background()

        # 妯睆璁剧疆椤典富闈㈡澘
        panel_w = 720
        panel_h = 500
        panel_x = (WINDOW_W - panel_w) // 2
        panel_y = (WINDOW_H - panel_h) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        self._draw_basic_panel(panel_rect, border=4)

        # ============================================================
        #  鏍囬
        # ============================================================
        title = render_pixel_text(self.font_menu_title, "SETTINGS", C.GOLD_LIGHT, scale=3)
        shadow = render_pixel_text(self.font_menu_title, "SETTINGS", C.OUTLINE, scale=3)

        title_x = panel_rect.centerx - title.get_width() // 2
        title_y = panel_rect.y + 42

        self.screen.blit(shadow, (title_x + 3, title_y + 3))
        self.screen.blit(title, (title_x, title_y))

        # 鍒嗛殧绾?
        line_y = panel_rect.y + 112
        pygame.draw.line(
            self.screen,
            C.GOLD_DARK,
            (panel_rect.x + 60, line_y),
            (panel_rect.right - 60, line_y),
            3
        )
        pygame.draw.line(
            self.screen,
            C.OUTLINE,
            (panel_rect.x + 60, line_y + 4),
            (panel_rect.right - 60, line_y + 4),
            2
        )

        # ============================================================
        #  BOARD SIZE
        # ============================================================
        board_label = render_pixel_text(self.font_status, "BOARD SIZE", C.GOLD, scale=2)
        board_label_x = panel_rect.centerx - board_label.get_width() // 2
        board_label_y = panel_rect.y + 166

        self.screen.blit(board_label, (board_label_x, board_label_y))

        # 妫嬬洏澶у皬鎸夐挳
        mouse_pos = self._logical_mouse_pos()
        for b in self._get_settings_buttons():
            hovered = b["rect"].collidepoint(mouse_pos)
            self._draw_menu_button(b, hovered)

        # ============================================================
        #  褰撳墠閫夋嫨
        # ============================================================
        current_text = f"Current: {self.board_size} x {self.board_size}"
        current = render_pixel_text(self.font_status, current_text, C.CREAM, scale=2)

        current_x = panel_rect.centerx - current.get_width() // 2
        current_y = panel_rect.y + 278

        self.screen.blit(current, (current_x, current_y))

        # ============================================================
        #  鎻愮ず鏂囧瓧
        # ============================================================
        note_text = "Changing size affects the next new game."
        note = render_pixel_text(self.font_small, note_text, C.GOLD_DARK, scale=2)

        if note.get_width() > panel_rect.width - 100:
            note = render_pixel_text(self.font_small, note_text, C.GOLD_DARK, scale=1)

        note_x = panel_rect.centerx - note.get_width() // 2
        note_y = panel_rect.y + 324

        self.screen.blit(note, (note_x, note_y))

    def _draw_ripples(self, sx, sy):
        cell = self.board.cell_size

        for ripple in self.ripples:
            r = ripple["r"]
            c = ripple["c"]
            frame = ripple["frame"]
            max_frames = ripple["max_frames"]

            t = frame / max_frames
            radius = int(4 + t * (cell * 0.58))
            alpha = max(0, int(180 * (1 - t)))

            cx = BOARD_X + sx + c * cell
            cy = BOARD_Y + sy + r * cell

            # 鍍忕礌椋庢尝绾癸細鐢ㄦ柟妗嗕唬鏇垮渾鍦?
            color = C.GOLD_LIGHT if frame % 4 < 2 else C.CREAM

            ripple_surf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.rect(
                ripple_surf,
                (*color, alpha),
                (2, 2, radius * 2, radius * 2),
                2
            )

            self.screen.blit(ripple_surf, (cx - radius - 2, cy - radius - 2))

    def _draw_invalid_marks(self, sx, sy):
        cell = self.board.cell_size

        for mark in self.invalid_marks:
            r = mark["r"]
            c = mark["c"]
            frame = mark["frame"]
            max_frames = mark["max_frames"]

            t = frame / max_frames
            alpha = max(0, int(230 * (1 - t)))

            cx = BOARD_X + sx + c * cell
            cy = BOARD_Y + sy + r * cell

            # 鍓嶅崐娈垫姈鍔ㄦ槑鏄撅紝鍚庡崐娈垫贰鍑?
            shake = 0
            if frame < 12:
                shake = int(math.sin(frame * 2.6) * 3)

            size = 13
            cross_surf = pygame.Surface((size * 2 + 8, size * 2 + 8), pygame.SRCALPHA)

            red = (*C.RED_LIGHT, alpha)
            outline = (*C.OUTLINE, alpha)

            # 澶栧眰榛戣壊鎻忚竟
            pygame.draw.line(cross_surf, outline, (4, 4), (size * 2 + 4, size * 2 + 4), 4)
            pygame.draw.line(cross_surf, outline, (size * 2 + 4, 4), (4, size * 2 + 4), 4)

            # 鍐呭眰绾㈠弶
            pygame.draw.line(cross_surf, red, (4, 4), (size * 2 + 4, size * 2 + 4), 2)
            pygame.draw.line(cross_surf, red, (size * 2 + 4, 4), (4, size * 2 + 4), 2)

            self.screen.blit(
                cross_surf,
                (
                    int(cx - size - 4 + shake),
                    int(cy - size - 4)
                )
            )

    def _draw_occupied_hover_hint(self, sx, sy):
        if not self.occupied_hover_pos:
            return

        if self.board.winner != 0:
            return

        r, c = self.occupied_hover_pos
        cell = self.board.cell_size

        cx = BOARD_X + sx + c * cell
        cy = BOARD_Y + sy + r * cell

        pulse = abs(math.sin(self.anim_tick * 0.12))
        size = 17 + int(pulse * 2)

        hint_surf = pygame.Surface((size * 2 + 6, size * 2 + 6), pygame.SRCALPHA)

        # 鐢ㄧ孩鑹茶鏍囨彁绀?杩欓噷涓嶈兘涓?锛屼絾涓嶈鍍忕偣鍑婚潪娉曢偅鏍峰己鐑?
        col = (*C.RED_LIGHT, OCCUPIED_HINT_ALPHA)

        # 鍥涗釜瑙掞紝涓嶈鏁村湀鍖呬綇锛岄伩鍏嶅お鎶㈢溂
        leg_len = 7

        # 宸︿笂
        pygame.draw.line(hint_surf, col, (3, 3), (3 + leg_len, 3), 2)
        pygame.draw.line(hint_surf, col, (3, 3), (3, 3 + leg_len), 2)

        # 鍙充笂
        pygame.draw.line(hint_surf, col, (size * 2 + 3, 3), (size * 2 + 3 - leg_len, 3), 2)
        pygame.draw.line(hint_surf, col, (size * 2 + 3, 3), (size * 2 + 3, 3 + leg_len), 2)

        # 宸︿笅
        pygame.draw.line(hint_surf, col, (3, size * 2 + 3), (3 + leg_len, size * 2 + 3), 2)
        pygame.draw.line(hint_surf, col, (3, size * 2 + 3), (3, size * 2 + 3 - leg_len), 2)

        # 鍙充笅
        pygame.draw.line(hint_surf, col, (size * 2 + 3, size * 2 + 3), (size * 2 + 3 - leg_len, size * 2 + 3), 2)
        pygame.draw.line(hint_surf, col, (size * 2 + 3, size * 2 + 3), (size * 2 + 3, size * 2 + 3 - leg_len), 2)

        self.screen.blit(
            hint_surf,
            (
                int(cx - size - 3),
                int(cy - size - 3)
            )
        )

    def _draw_undo_animations(self, sx, sy):
        cell = self.board.cell_size

        for anim in self.undo_animations:
            r = anim["r"]
            c = anim["c"]
            player = anim["player"]
            frame = anim["frame"]
            max_frames = anim["max_frames"]

            t = frame / max_frames

            # 鍓?60% 鎶栧姩锛屽悗 40% 缂╁皬娣″嚭
            shake_amp = max(0, int((1 - t) * 5))
            shake_x = int(math.sin(frame * 2.4) * shake_amp)
            shake_y = int(math.cos(frame * 2.1) * shake_amp)

            if t < 0.55:
                scale = 1.0
                alpha = 255
            else:
                local = (t - 0.55) / 0.45
                scale = max(0.05, 1.0 - local)
                alpha = max(0, int(255 * (1 - local)))

            base_img = self.stone_black_img if player == 1 else self.stone_white_img
            size = max(4, int(self.board.stone_size * scale))

            img = pygame.transform.scale(base_img, (size, size)).copy()
            img.set_alpha(alpha)

            cx = BOARD_X + sx + c * cell
            cy = BOARD_Y + sy + r * cell

            self.screen.blit(
                img,
                (
                    int(cx - size // 2 + shake_x),
                    int(cy - size // 2 + shake_y)
                )
            )

    def _draw_magnetic_preview(self, sx, sy):
        if not self.preview_active or self.preview_cell is None:
            return

        if self.board.winner != 0:
            return

        stone_half = self.board.stone_size // 2

        px = self.preview_x
        py = self.preview_y

        # 璁＄畻棰勮妫嬪瓙璺濈浜ゅ弶鐐逛腑蹇冭繕鏈夊杩?
        dx = self.preview_target_x - self.preview_x
        dy = self.preview_target_y - self.preview_y
        dist = math.sqrt(dx * dx + dy * dy)

        # 纾佸惛蹇埌涓績鏃讹紝鍒堕€犱竴鐐?纾侀搧鍚镐綇鍓嶇殑鎶栧姩"
        jitter_x = 0
        jitter_y = 0

        if 1.5 < dist < MAGNET_JITTER_RADIUS:
            strength = 1 - dist / MAGNET_JITTER_RADIUS
            jitter_amp = 2.8 * strength

            jitter_x = math.sin(self.anim_tick * 1.7) * jitter_amp
            jitter_y = math.cos(self.anim_tick * 2.1) * jitter_amp

        # 瓒婃帴杩戜腑蹇冿紝閫忔槑搴﹁秺楂橈紝鍍忔槸琚惛闄勬垚鍨?
        alpha = 80
        if dist < MAGNET_RADIUS:
            alpha = int(80 + (1 - min(dist / MAGNET_RADIUS, 1)) * 90)

        hint = self.hint_black if self.preview_player == 1 else self.hint_white
        hint = hint.copy()
        hint.set_alpha(alpha)

        draw_x = px + sx + jitter_x - stone_half
        draw_y = py + sy + jitter_y - stone_half

        self.screen.blit(hint, (draw_x, draw_y))

        # 鐩爣浜ゅ弶鐐逛笂鐨勫皬鍨嬬鍚告
        target_size = 10 + int(math.sin(self.anim_tick * 0.35) * 2)
        tx = self.preview_target_x + sx
        ty = self.preview_target_y + sy

        pygame.draw.rect(
            self.screen,
            C.GOLD_LIGHT,
            (
                int(tx - target_size // 2),
                int(ty - target_size // 2),
                target_size,
                target_size,
            ),
            1
        )

    def _draw_last_move_marker(self, sx, sy):
        if not self.board.last_move:
            return

        if self.board.winner != 0:
            return

        r, c = self.board.last_move
        cell = self.board.cell_size

        cx = BOARD_X + sx + c * cell
        cy = BOARD_Y + sy + r * cell

        # 浣庤皟鐗堟湰锛氬彧鏄剧ず妫嬪瓙涓績灏忛噾鐐?
        blink = abs(math.sin(self.anim_tick * 0.1))
        color = C.GOLD_LIGHT if blink > 0.5 else C.GOLD

        pygame.draw.rect(
            self.screen,
            C.OUTLINE,
            (int(cx - 4), int(cy - 4), 8, 8)
        )

        pygame.draw.rect(
            self.screen,
            color,
            (int(cx - 3), int(cy - 3), 6, 6)
        )

    def _draw_win_line(self, sx, sy):
        stones = self._get_ordered_win_stones()
        if not stones:
            return

        if not self.win_line_active:
            return

        start_r, start_c = stones[0]
        end_r, end_c = stones[-1]

        cell = self.board.cell_size

        x1 = BOARD_X + sx + start_c * cell
        y1 = BOARD_Y + sy + start_r * cell
        x2 = BOARD_X + sx + end_c * cell
        y2 = BOARD_Y + sy + end_r * cell

        t = min(1.0, self.win_line_frame / WIN_LINE_MAX_FRAMES)
        t = 1 - (1 - t) * (1 - t)  # ease out

        cur_x = x1 + (x2 - x1) * t
        cur_y = y1 + (y2 - y1) * t

        # 澶栧眰娣辫壊鎻忚竟
        pygame.draw.line(
            self.screen,
            C.OUTLINE,
            (x1, y1),
            (cur_x, cur_y),
            8
        )

        # 涓眰绾㈤噾鍏夊甫
        pygame.draw.line(
            self.screen,
            C.RED_LIGHT,
            (x1, y1),
            (cur_x, cur_y),
            5
        )

        # 鍐呭眰涓婚噾绾?
        pygame.draw.line(
            self.screen,
            C.GOLD_LIGHT,
            (x1, y1),
            (cur_x, cur_y),
            3
        )

        # 绾垮ご楂樺厜
        flash = 7 + int(math.sin(self.anim_tick * 0.35) * 2)
        pygame.draw.rect(
            self.screen,
            C.CREAM,
            (
                int(cur_x - flash // 2),
                int(cur_y - flash // 2),
                flash,
                flash,
            )
        )

    def _draw_win_stone_sequence(self, sx, sy):
        stones = self._get_ordered_win_stones()
        if not stones:
            return

        cell = self.board.cell_size

        # 濡傛灉杩樺湪鎾斁渚濇闂儊锛屽氨鎸夐『搴忎竴涓釜鐐逛寒锛?
        # 濡傛灉宸茬粡鎾畬锛屽氨淇濈暀鍏ㄩ儴妫嬪瓙鐨勮交寰懠鍚搁珮浜?
        for idx, (r, c) in enumerate(stones):
            cx = BOARD_X + sx + c * cell
            cy = BOARD_Y + sy + r * cell

            if self.win_stone_flash_active:
                start_frame = idx * WIN_STONE_FLASH_STEP
                if self.win_stone_flash_frame < start_frame:
                    continue
                local = self.win_stone_flash_frame - start_frame
            else:
                local = self.anim_tick

            pulse = abs(math.sin(local * 0.30))
            size = 8 + int(pulse * 4)

            outer_col = C.OUTLINE
            inner_col = C.CREAM if pulse > 0.55 else C.GOLD_LIGHT

            pygame.draw.rect(
                self.screen,
                outer_col,
                (cx - size - 1, cy - size - 1, (size + 1) * 2, (size + 1) * 2),
                1
            )

            pygame.draw.rect(
                self.screen,
                inner_col,
                (cx - size, cy - size, size * 2, size * 2),
                2
            )

            # 瑙掔偣鐏姳
            if pulse > 0.72:
                pygame.draw.rect(self.screen, C.RED_LIGHT, (cx + size - 2, cy - size, 3, 3))
                pygame.draw.rect(self.screen, C.CREAM, (cx - size - 1, cy + size - 1, 3, 3))

    def _draw_game(self):
        # Apply screen shake offset
        sx, sy = self.shake_x, self.shake_y

        # Background
        self.screen.blit(self.wood_bg, (0, 0))

        # Handheld outer screen frame
        outer = pygame.Rect(28, 28, WINDOW_W - 56, WINDOW_H - 56)
        pygame.draw.rect(self.screen, C.OUTLINE, outer, 5)
        pygame.draw.rect(self.screen, C.GOLD_DARK, outer.inflate(-8, -8), 2)

        cell = self.board.cell_size
        board_px = (self.board.board_count - 1) * cell

        # Decorative border
        border_rect = (BOARD_X + sx - 10, BOARD_Y + sy - 10, board_px + 20, board_px + 20)
        draw_decorative_border(self.screen, border_rect, C.OUTLINE, 3)
        pygame.draw.rect(self.screen, C.GOLD_DARK,
                         (border_rect[0] + 4, border_rect[1] + 4,
                          border_rect[2] - 8, border_rect[3] - 8), 2)

        # Board panel
        board_rect = (BOARD_X + sx - 2, BOARD_Y + sy - 2, board_px + 4, board_px + 4)
        pygame.draw.rect(self.screen, C.BOARD, board_rect)
        pygame.draw.rect(self.screen, C.BOARD_EDGE, board_rect, 2)

        # Grid lines
        n = self.board.board_count
        mid = n // 2
        for i in range(n):
            lw = 2 if i == mid else 1
            color = C.GRID_THICK if i == mid else C.GRID
            lx = BOARD_X + sx
            ly = BOARD_Y + sy + i * cell
            pygame.draw.line(self.screen, color, (lx, ly), (lx + board_px, ly), lw)
            vx = BOARD_X + sx + i * cell
            vy = BOARD_Y + sy
            pygame.draw.line(self.screen, color, (vx, vy), (vx, vy + board_px), lw)

        # Star points
        for r, c in self.board.star_points:
            px = BOARD_X + sx + c * cell
            py = BOARD_Y + sy + r * cell
            pygame.draw.rect(self.screen, C.STAR, (px - 3, py - 3, 6, 6))

        # Draw ripples under stones
        self._draw_ripples(sx, sy)

        # Collect drop animation info for lookup
        anim_stones = {}
        for anim in self.animations:
            if anim["type"] == "drop":
                key = (anim["r"], anim["c"])
                anim_stones[key] = anim

        # Draw stones (skip those that are animating their drop)
        stone_half = self.board.stone_size // 2
        for r in range(n):
            for c in range(n):
                stone_val = self.board.grid[r][c]
                if stone_val == 0:
                    continue
                if (r, c) in anim_stones:
                    continue  # drawn by animation below
                px = BOARD_X + sx + c * cell - stone_half
                py = BOARD_Y + sy + r * cell - stone_half
                img = self.stone_black_img if stone_val == 1 else self.stone_white_img
                self.screen.blit(img, (px, py))

        # Draw drop animations
        for anim in self.animations:
            if anim["type"] != "drop":
                continue
            r, c, player = anim["r"], anim["c"], anim["player"]
            progress = anim["frame"] / anim["max_frames"]
            # Ease-out bounce
            t = progress
            if t < 0.7:
                y_offset = -40 * (1 - (t / 0.7)) ** 2
            else:
                bounce = (t - 0.7) / 0.3
                y_offset = 6 * math.sin(bounce * math.pi * 2) * (1 - bounce)
            px = BOARD_X + sx + c * cell - stone_half
            py = BOARD_Y + sy + r * cell - stone_half + y_offset
            # Slight scale-in
            scale_factor = 0.85 + 0.15 * min(1, progress * 1.5)
            img = self.stone_black_img if player == 1 else self.stone_white_img
            if abs(scale_factor - 1.0) > 0.005:
                sz = int(self.board.stone_size * scale_factor)
                _scaled = pygame.transform.scale(img, (max(4, sz), max(4, sz)))
                self.screen.blit(_scaled, (px, py))
            else:
                self.screen.blit(img, (px, py))

        # Draw undo animations over board, where the removed stone used to be
        self._draw_undo_animations(sx, sy)

# Last move marker
        # Last move marker
        if not anim_stones:
            self._draw_last_move_marker(sx, sy)

        # Magnetic hover preview
        if not anim_stones:
            self._draw_magnetic_preview(sx, sy)

        # Occupied hover hint
        self._draw_occupied_hover_hint(sx, sy)

        # Invalid move cross feedback
        self._draw_invalid_marks(sx, sy)

        # Win stones sequential flash
        self._draw_win_stone_sequence(sx, sy)

        # Animated win line
        self._draw_win_line(sx, sy)

        # Particles (on top of stones)
        for p in self.particles:
            p.draw(self.screen, sx, sy)

        # Title banner
        self._draw_game_title_banner(sx)

        # Status bar
        self._draw_game_status(sx)

        # Win overlay
        # 淇锛氬彧鏈変粛鍦?PLAYING 鐘舵€佹椂鎵嶇敾妫嬬洏涓婄殑鑳滃埄閬僵锛?
        # 杩涘叆 END 鐘舵€佸悗锛岀敱 _draw_end_page() 璐熻矗缁樺埗缁撴潫椤甸潰銆?
        if self.state == self.PLAYING and self.board.winner != 0 and self.win_alpha > 0:
            self.win_overlay.fill((0, 0, 0, self.win_alpha))
            self.screen.blit(self.win_overlay, (0, 0))

    def _draw_game_title_banner(self, sx):
        # 妯睆鎺屾満甯冨眬锛氭爣棰樹笉鍐嶆斁椤堕儴妯箙锛岃€屾槸鏀惧乏渚х珫鍚戦潰鏉?
        self._draw_left_title_panel()

    def _draw_left_title_panel(self):
        rect = pygame.Rect(LEFT_BAR_X, LEFT_BAR_Y, LEFT_BAR_W, LEFT_BAR_H)

        pygame.draw.rect(self.screen, C.MENU_PANEL, rect)
        pygame.draw.rect(self.screen, C.OUTLINE, rect, 4)
        pygame.draw.rect(self.screen, C.GOLD_DARK, rect.inflate(-8, -8), 2)

        # 瑙掓爣
        corner_size = 18
        for cx, cy in [
            (rect.x, rect.y),
            (rect.right - corner_size, rect.y),
            (rect.x, rect.bottom - corner_size),
            (rect.right - corner_size, rect.bottom - corner_size),
        ]:
            pygame.draw.rect(self.screen, C.OUTLINE, (cx, cy, corner_size, corner_size))
            pygame.draw.rect(self.screen, C.GOLD, (cx + 4, cy + 4, corner_size - 8, corner_size - 8))
            pygame.draw.rect(self.screen, C.GOLD_LIGHT, (cx + 7, cy + 7, 4, 4))

        # 绔栨帓 GOMOKU
        logo = render_vertical_pixel_text(
            self.font_menu_title,
            "GOMOKU",
            C.GOLD_LIGHT,
            scale=3,
            gap=8
        )

        shadow = render_vertical_pixel_text(
            self.font_menu_title,
            "GOMOKU",
            C.OUTLINE,
            scale=3,
            gap=8
        )

        lx = rect.centerx - logo.get_width() // 2
        ly = rect.centery - logo.get_height() // 2

        self.screen.blit(shadow, (lx + 3, ly + 3))
        self.screen.blit(logo, (lx, ly))

        # 灏忚楗扮嚎
        pygame.draw.line(self.screen, C.GOLD_DARK, (rect.centerx, rect.y + 34), (rect.centerx, ly - 20), 3)
        pygame.draw.line(self.screen, C.GOLD_DARK, (rect.centerx, ly + logo.get_height() + 20), (rect.centerx, rect.bottom - 34), 3)

    def _draw_game_status(self, sx):
        # 缁撴潫椤佃儗鏅笉鏄剧ず娓告垙鐘舵€佹爮
        if self.state == self.END:
            return

        panel_rect = pygame.Rect(RIGHT_BAR_X, RIGHT_BAR_Y, RIGHT_BAR_W, RIGHT_BAR_H)

        pygame.draw.rect(self.screen, C.MENU_PANEL, panel_rect)
        pygame.draw.rect(self.screen, C.OUTLINE, panel_rect, 4)
        pygame.draw.rect(self.screen, C.GOLD_DARK, panel_rect.inflate(-8, -8), 2)

        # 瑙掓爣
        corner_size = 18
        for cx, cy in [
            (panel_rect.x, panel_rect.y),
            (panel_rect.right - corner_size, panel_rect.y),
            (panel_rect.x, panel_rect.bottom - corner_size),
            (panel_rect.right - corner_size, panel_rect.bottom - corner_size),
        ]:
            pygame.draw.rect(self.screen, C.OUTLINE, (cx, cy, corner_size, corner_size))
            pygame.draw.rect(self.screen, C.GOLD, (cx + 4, cy + 4, corner_size - 8, corner_size - 8))
            pygame.draw.rect(self.screen, C.GOLD_LIGHT, (cx + 7, cy + 7, 4, 4))

        # STATUS 鏍囬
        title = render_pixel_text(self.font_status, "STATUS", C.GOLD, scale=2)
        self.screen.blit(title, (panel_rect.centerx - title.get_width() // 2, panel_rect.y + 36))

        # 鍒嗛殧绾?
        line_y = panel_rect.y + 78
        pygame.draw.line(self.screen, C.GOLD_DARK, (panel_rect.x + 48, line_y), (panel_rect.right - 48, line_y), 3)
        pygame.draw.line(self.screen, C.OUTLINE, (panel_rect.x + 48, line_y + 4), (panel_rect.right - 48, line_y + 4), 2)

        # 褰撳墠鐘舵€?
        if self.board.winner == -1:
            main_status = "DRAW"
            sub_status = "NO WINNER"
        elif self.board.winner != 0:
            name = "BLACK" if self.board.winner == 1 else "WHITE"
            main_status = f"{name} WINS"
            sub_status = "ROUND OVER"
        else:
            name = "BLACK" if self.board.current_player == 1 else "WHITE"
            main_status = f"{name}'S TURN"
            sub_status = "PLACE A STONE"

        main = render_pixel_text(self.font_status, main_status, C.CREAM, scale=2)
        sub = render_pixel_text(self.font_small, sub_status, C.GOLD_DARK, scale=2)
        self.screen.blit(main, (panel_rect.centerx - main.get_width() // 2, panel_rect.y + 106))
        self.screen.blit(sub, (panel_rect.centerx - sub.get_width() // 2, panel_rect.y + 142))

        # 褰撳墠鐜╁妫嬪瓙
        if self.board.winner == 0:
            icon_size = 68
            icon = self.stone_black_img if self.board.current_player == 1 else self.stone_white_img
            icon = pygame.transform.scale(icon, (icon_size, icon_size))
            icon_box = pygame.Rect(panel_rect.centerx - 48, panel_rect.y + 180, 96, 96)
            pygame.draw.rect(self.screen, C.OUTLINE, icon_box, 2)
            pygame.draw.rect(self.screen, C.GOLD_DARK, icon_box.inflate(-6, -6), 2)
            self.screen.blit(icon, (icon_box.centerx - icon_size // 2, icon_box.centery - icon_size // 2))

        # 鍒嗘暟鍖哄煙
        score_line_y = panel_rect.y + 304
        pygame.draw.line(self.screen, C.GOLD_DARK, (panel_rect.x + 48, score_line_y), (panel_rect.right - 48, score_line_y), 3)
        pygame.draw.line(self.screen, C.OUTLINE, (panel_rect.x + 48, score_line_y + 4), (panel_rect.right - 48, score_line_y + 4), 2)

        score_title = render_pixel_text(self.font_status, "SCORES", C.GOLD, scale=2)
        self.screen.blit(score_title, (panel_rect.centerx - score_title.get_width() // 2, panel_rect.y + 332))

        score_text = f"B:{self.black_wins}    W:{self.white_wins}    D:{self.draws}"
        score = render_pixel_text(self.font_status, score_text, C.CREAM, scale=2)
        if score.get_width() > panel_rect.width - 80:
            score = render_pixel_text(self.font_status, score_text, C.CREAM, scale=1)
        self.screen.blit(score, (panel_rect.centerx - score.get_width() // 2, panel_rect.y + 370))

        # 鎿嶄綔鎻愮ず
        hint1 = render_pixel_text(self.font_small, "U: Undo    R: Restart", C.GOLD_DARK, scale=2)
        hint2 = render_pixel_text(self.font_small, "ESC: Menu", C.GOLD_DARK, scale=2)
        self.screen.blit(hint1, (panel_rect.centerx - hint1.get_width() // 2, panel_rect.y + 452))
        self.screen.blit(hint2, (panel_rect.centerx - hint2.get_width() // 2, panel_rect.y + 482))
