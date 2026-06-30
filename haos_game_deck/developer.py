"""Session-only developer tools shared by every game."""

import pygame

from .common import C, WINDOW_H, WINDOW_W, render_pixel_text


DEV_PASSWORD = ["0", "5", "0", "6"]


class DeveloperMixin:
    def _init_developer(self):
        self.dev_mode = False
        self.dev_panel_open = False
        self.dev_menu_index = 0
        self.dev_invincible = False
        self.dev_freeze_enemies = False
        self.dev_show_hitboxes = False
        self.dev_game_speed = 1.0
        self.dev_enemy_speed = 1.0

    def _enable_developer_mode(self):
        self.dev_mode = True
        self.dev_panel_open = False
        self.dev_menu_index = 0
        self.achievement_notifications.clear()

    def _dev_actions(self):
        return [
            ("CLOSE PANEL", "close"),
            (f"INVINCIBLE  {'ON' if self.dev_invincible else 'OFF'}", "invincible"),
            (f"ENEMY FIRE  {'FROZEN' if self.dev_freeze_enemies else 'ACTIVE'}", "freeze"),
            (f"GAME SPEED  x{self.dev_game_speed:g}", "game_speed"),
            (f"ENEMY SPEED x{self.dev_enemy_speed:g}", "enemy_speed"),
            (f"HITBOXES  {'ON' if self.dev_show_hitboxes else 'OFF'}", "hitboxes"),
            ("UNLOCK TEST CONTENT", "unlock"),
            ("FORCE CLEAR / WIN", "win"),
            ("FORCE FAIL", "fail"),
            ("TEST ACHIEVEMENT BANNER", "achievement"),
            ("AIR: PREVIOUS STAGE", "air_prev"),
            ("AIR: NEXT STAGE", "air_next"),
            ("AIR: NEXT BOSS PHASE", "air_phase"),
            ("AIR: MAX WEAPONS", "air_weapons"),
            ("AIR: MISSILE READY", "air_missile"),
            ("AIR: STORY MESSAGE", "air_story"),
            ("AIR: S-RANK RESULT", "air_result"),
        ]

    def _handle_developer_event(self, event):
        if not self.dev_mode or event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_F10:
            self.dev_panel_open = not self.dev_panel_open
            return True
        if not self.dev_panel_open:
            return False
        actions = self._dev_actions()
        if event.key in (pygame.K_ESCAPE,):
            self.dev_panel_open = False
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.dev_menu_index = (self.dev_menu_index - 1) % len(actions)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.dev_menu_index = (self.dev_menu_index + 1) % len(actions)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_LEFT, pygame.K_RIGHT):
            direction = -1 if event.key == pygame.K_LEFT else 1
            self._activate_developer_action(actions[self.dev_menu_index][1], direction)
        return True

    def _activate_developer_action(self, action, direction=1):
        if action == "close":
            self.dev_panel_open = False
        elif action == "invincible":
            self.dev_invincible = not self.dev_invincible
        elif action == "freeze":
            self.dev_freeze_enemies = not self.dev_freeze_enemies
        elif action == "hitboxes":
            self.dev_show_hitboxes = not self.dev_show_hitboxes
        elif action == "game_speed":
            values = (0.5, 1.0, 2.0)
            index = values.index(self.dev_game_speed)
            self.dev_game_speed = values[(index + direction) % len(values)]
        elif action == "enemy_speed":
            values = (0.5, 0.75, 1.0, 1.25)
            index = values.index(self.dev_enemy_speed)
            self.dev_enemy_speed = values[(index + direction) % len(values)]
        elif action == "unlock":
            progress = self.save_data.get("progress", {})
            air = progress.get("air")
            if air is not None:
                air["unlocked"] = 16
                air["archive_unlocked"] = 8
                air["challenge_unlocked"] = True
        elif action == "win":
            self._dev_force_result(True)
        elif action == "fail":
            self._dev_force_result(False)
        elif action == "achievement":
            self.achievement_notifications.append(
                {"title": "DEV TEST // ACHIEVEMENT", "frame": 0}
            )
            self.audio.play("achievement", 0.75)
        elif action.startswith("air_"):
            self._activate_air_developer_action(action)

    def _activate_air_developer_action(self, action):
        air_states = {
            self.AIR_MENU, self.AIR_SELECT, self.AIR_CONTROLS, self.AIR_BRIEF,
            self.AIR_ARCHIVE, self.AIR_SUPPLY, self.AIR_PLAYING, self.AIR_END,
        }
        if self.state not in air_states:
            return
        if action in ("air_prev", "air_next"):
            step = -1 if action == "air_prev" else 1
            level = (getattr(self, "air_level", 0) + step) % 16
            mode = "challenge" if getattr(self, "air_mode", "standard") == "challenge" else "standard"
            self._start_air_level(level, mode=mode)
        elif action == "air_phase" and self.state == self.AIR_PLAYING:
            bosses = [enemy for enemy in self.air_enemies if enemy.get("boss")]
            if bosses:
                boss = bosses[0]
                next_phase = min(3, self.air_boss_phase + 1)
                ratio = 0.66 if next_phase == 2 else 0.33
                boss["hp"] = max(1, int(boss["max_hp"] * ratio))
                self.air_boss_phase = next_phase
                boss["pattern"] = boss["patterns"][next_phase - 1]
                self.air_boss_phase_flash = 100
        elif action == "air_weapons":
            self.air_loadout.update({"cannon": 5, "spread": 5, "laser": 5})
        elif action == "air_missile":
            self.air_missile_charge = 100
            self.air_missile_ready = True
        elif action == "air_story":
            self._show_air_story("DEV LINK: STORY AND COMMS DISPLAY TEST.", 240)
        elif action == "air_result":
            self.air_score = max(self.air_score, 50000)
            self.air_destroyed = max(1, self.air_spawned)
            self.air_mission_value = self.air_mission_target
            self.air_health = 5
            self._finish_air(True)

    def _dev_force_result(self, won):
        if self.state == self.AIR_PLAYING:
            self._finish_air(won)
        elif self.state == self.PLAYING:
            self.board.winner = 1 if won else 2
            self._on_win()
        elif self.state == self.SNAKE_PLAYING:
            if won:
                self.snake_score = max(self.snake_score, 40)
            self._end_snake_game()
        elif self.state == self.BREAKOUT_PLAYING:
            if won:
                for brick in self.breakout_bricks:
                    brick["alive"] = False
            else:
                self.breakout_lives = 0
                self.state = self.BREAKOUT_END
        elif self.state == self.G2048_PLAYING:
            self.g2048_won = won
            self.g2048_game_over = not won
            self.state = self.G2048_END
        elif self.state == self.MINES_PLAYING:
            if won:
                for row in range(self.mines_size):
                    for col in range(self.mines_size):
                        if self.mines_grid[row][col] != -1:
                            self.mines_revealed[row][col] = True
                self.mines_revealed_count = self.mines_size * self.mines_size - self.mines_count
                self._check_mines_win()
            else:
                self.mines_game_over = True
                self.mines_win = False
                self.state = self.MINES_END
        elif self.state == self.TETRIS_PLAYING:
            if won:
                self.tetris_score = max(self.tetris_score, 10000)
                self.tetris_lines = max(self.tetris_lines, 20)
                self.tetris_level = max(self.tetris_level, 5)
            self._finish_tetris_game()

    def _draw_developer_overlay(self):
        if not self.dev_mode:
            return
        watermark = render_pixel_text(
            self.font_small, "DEV MODE // PROGRESS DISABLED", (255, 105, 125), scale=2
        )
        diagnostics = f"FPS {self.clock.get_fps():04.1f}"
        if self.state == self.AIR_PLAYING:
            diagnostics += f"  THREAT {self.air_threat:.2f}  STAGE {self.air_level + 1:02d}"
        diagnostic_text = render_pixel_text(
            self.font_small, diagnostics, (255, 185, 200), scale=1
        )
        badge = pygame.Surface(
            (
                max(watermark.get_width(), diagnostic_text.get_width()) + 20,
                watermark.get_height() + diagnostic_text.get_height() + 18,
            ),
            pygame.SRCALPHA,
        )
        badge.fill((20, 5, 12, 210))
        badge.blit(watermark, (10, 6))
        badge.blit(
            diagnostic_text,
            (badge.get_width() - diagnostic_text.get_width() - 10, watermark.get_height() + 10),
        )
        self.screen.blit(badge, (WINDOW_W - badge.get_width() - 12, 10))
        if self.dev_show_hitboxes:
            self._draw_developer_hitboxes()
        if not self.dev_panel_open:
            hint = render_pixel_text(self.font_small, "F10 DEV PANEL", (255, 170, 185), scale=1)
            self.screen.blit(hint, (WINDOW_W - hint.get_width() - 18, 45))
            return

        shade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 165))
        self.screen.blit(shade, (0, 0))
        panel = pygame.Rect(205, 55, 870, 610)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 6)
        pygame.draw.rect(self.screen, (17, 28, 48), panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, (255, 95, 125), panel.inflate(-22, -22), 2)
        title = render_pixel_text(self.font_status, "DEVELOPER CONTROL", (255, 185, 200), scale=3)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, 82))
        subtitle = render_pixel_text(
            self.font_small, "SESSION ONLY // SAVE, RECORDS, STATS AND ACHIEVEMENTS DISABLED",
            (135, 205, 225), scale=1,
        )
        self.screen.blit(subtitle, (panel.centerx - subtitle.get_width() // 2, 132))

        actions = self._dev_actions()
        for index, (label, _) in enumerate(actions):
            col, row = index // 9, index % 9
            rect = pygame.Rect(245 + col * 415, 170 + row * 49, 375, 38)
            selected = index == self.dev_menu_index
            pygame.draw.rect(self.screen, (7, 15, 28), rect)
            pygame.draw.rect(
                self.screen, (255, 105, 135) if selected else (45, 125, 155), rect, 2
            )
            text = render_pixel_text(
                self.font_small, label,
                (255, 225, 230) if selected else (180, 210, 220), scale=1,
            )
            self.screen.blit(text, (rect.x + 12, rect.centery - text.get_height() // 2))
        footer = render_pixel_text(
            self.font_small, "UP/DOWN SELECT   LEFT/RIGHT CHANGE   ENTER ACTIVATE   F10/ESC CLOSE",
            (120, 180, 200), scale=1,
        )
        self.screen.blit(footer, (panel.centerx - footer.get_width() // 2, 632))

    def _draw_developer_hitboxes(self):
        if self.state != self.AIR_PLAYING:
            return
        pygame.draw.circle(
            self.screen, (100, 255, 150),
            (int(self.air_player["x"]), int(self.air_player["y"])),
            int(self.air_player.get("r", 5)), 1,
        )
        for enemy in self.air_enemies:
            pygame.draw.circle(
                self.screen, (255, 220, 80),
                (int(enemy["x"]), int(enemy["y"])), int(enemy["r"]), 1,
            )
            hp = render_pixel_text(
                self.font_small, f"{max(0, int(enemy['hp']))}/{int(enemy['max_hp'])}",
                (255, 230, 120), scale=1,
            )
            self.screen.blit(
                hp,
                (int(enemy["x"]) - hp.get_width() // 2, int(enemy["y"] - enemy["r"] - 15)),
            )
        for bullet in self.air_enemy_bullets:
            pygame.draw.circle(
                self.screen, (255, 90, 150),
                (int(bullet["x"]), int(bullet["y"])), int(bullet["r"]), 1,
            )
