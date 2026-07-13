import unittest
from unittest.mock import patch


import MERIDIAN as legacy
from meridian import Board, Game
from meridian.common import WINDOW_H, WINDOW_W, pygame


class ArchitectureSmokeTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_legacy_entry_point_exports_game_and_board(self):
        self.assertIs(legacy.Game, Game)
        self.assertIs(legacy.Board, Board)

    def test_gomoku_board_still_places_wins_and_undoes(self):
        board = Board(15)
        moves = [
            (7, 3),
            (0, 0),
            (7, 4),
            (0, 1),
            (7, 5),
            (0, 2),
            (7, 6),
            (0, 3),
            (7, 7),
        ]

        self.assertTrue(all(board.place_stone(r, c) for r, c in moves))
        self.assertEqual(board.winner, 1)
        self.assertEqual(len(board.win_stones), 5)
        self.assertTrue(board.undo())
        self.assertEqual(board.winner, 0)

    def test_each_game_starts_in_its_original_playing_state(self):
        game = Game()

        starters = [
            (game._start_new_game, game.PLAYING),
            (game._start_snake_game, game.SNAKE_PLAYING),
            (game._start_breakout_game, game.BREAKOUT_PLAYING),
            (game._start_2048_game, game.G2048_PLAYING),
            (game._start_mines_game, game.MINES_PLAYING),
            (game._start_tetris_game, game.TETRIS_PLAYING),
        ]

        for start, expected_state in starters:
            start()
            self.assertEqual(game.state, expected_state)
        game._start_air_level()
        self.assertEqual(game.state, game.AIR_BRIEF)
        game._begin_air_combat()
        self.assertEqual(game.state, game.AIR_PLAYING)

    def test_2048_line_compression_is_unchanged(self):
        game = Game()

        self.assertEqual(
            game._compress_2048_line([2, 0, 2, 2])[0],
            [4, 2, 0, 0],
        )
        self.assertEqual(
            game._compress_2048_line([2, 2, 2, 2])[0],
            [4, 4, 0, 0],
        )

    def test_mines_first_click_safe_area_is_preserved(self):
        game = Game()
        game.mines_size = 9
        game.mines_count = 10
        game._start_mines_game()
        game._generate_mines_board(4, 4)

        mine_count = sum(
            value == -1 for row in game.mines_grid for value in row
        )
        safe_area = all(
            game.mines_grid[r][c] != -1
            for r in range(3, 6)
            for c in range(3, 6)
        )

        self.assertEqual(mine_count, 10)
        self.assertTrue(safe_area)

    def test_primary_screens_draw_without_errors(self):
        game = Game()
        game.transition_active = False
        states = [
            game.BOOT,
            game.DESKTOP,
            game.MENU,
            game.SETTINGS,
            game.SNAKE_MENU,
            game.SNAKE_SETTINGS,
            game.BREAKOUT_MENU,
            game.BREAKOUT_SETTINGS,
            game.G2048_MENU,
            game.MINES_MENU,
            game.MINES_SETTINGS,
            game.SYSTEM_READY,
            game.TETRIS_MENU,
            game.AIR_MENU,
            game.AIR_BRIEF,
            game.AIR_ARCHIVE,
            game.AIR_SUPPLY,
            game.SHUTDOWN,
            game.SYSTEM_SETTINGS,
            game.PROFILE,
            game.ACHIEVEMENT_WALL,
        ]

        for state in states:
            game.state = state
            game.draw()

    def test_audio_manager_accepts_keyboard_and_mouse_input(self):
        game = Game()
        game.audio.handle_input_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        )
        game.audio.handle_input_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))
        )

    def test_audio_tracks_and_volume_control_are_available(self):
        game = Game()
        expected_tracks = {
            "desktop", "gomoku", "snake", "breakout", "2048", "mines",
            "tetris", "air", "tank_menu", "tank_normal", "tank_final",
            "tank_sprint", "tank_sudden",
        }
        self.assertEqual(set(game.audio.tracks), expected_tracks)

        game.audio.sync_state(game.DESKTOP)
        self.assertEqual(game.audio.current_track, "desktop")
        game.audio.sync_state(game.SNAKE_PLAYING)
        self.assertEqual(game.audio.current_track, "snake")

        game.audio.set_music_volume(-1)
        self.assertEqual(game.audio.music_volume, 0.0)
        game.audio.set_music_volume(2)
        self.assertEqual(game.audio.music_volume, 1.0)
        game.audio.set_master_volume(-1)
        self.assertEqual(game.audio.master_volume, 0.0)
        game.audio.set_master_volume(2)
        self.assertEqual(game.audio.master_volume, 1.0)

    def test_loaded_master_volume_reaches_audio_manager(self):
        game = Game()
        game.save_data["settings"]["master_volume"] = 0.35

        game._apply_loaded_data()

        self.assertEqual(game.master_volume, 0.35)
        self.assertEqual(game.audio.master_volume, 0.35)

    def test_tank_music_layers_effects_and_phase_switching_are_available(self):
        from meridian.audio import TANK_DUEL_MOTIF, TANK_TRACK_SPECS, THEME_MELODY

        game = Game()
        self.assertEqual(
            TANK_TRACK_SPECS,
            {
                "tank_menu": 0.24,
                "tank_normal": 0.18,
                "tank_final": 0.15,
                "tank_sprint": 0.125,
                "tank_sudden": 0.105,
            },
        )
        self.assertLessEqual(set(TANK_TRACK_SPECS), set(game.audio.tracks))
        self.assertNotEqual(tuple(THEME_MELODY), TANK_DUEL_MOTIF)
        self.assertEqual(len(TANK_DUEL_MOTIF), 14)
        self.assertLessEqual(
            {
                "tank_shot", "tank_clash", "tank_brick", "tank_hit",
                "tank_explosion", "tank_pickup", "tank_item", "tank_alarm",
            },
            set(game.audio.effects),
        )
        game.audio.set_tank_phase("sprint")
        game.audio.sync_state(game.TANK_PLAYING)
        self.assertEqual(game.audio.current_track, "tank_sprint")
        self.assertEqual(game.audio.crossfade_duration_ms, 700)

    def test_tank_uses_dedicated_crossfire_transition(self):
        game = Game()
        game.state = game.DESKTOP
        game._start_transition(game.TANK_MENU, "tank_crossfire", 48)
        self.assertTrue(game.transition_active)
        self.assertEqual(game.transition_type, "tank_crossfire")
        game._draw_transition_overlay()

    def test_tank_pause_scales_music_and_resume_fades_for_300_ms(self):
        game = Game()
        game._start_tank_battle()
        game._handle_tank_playing_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)
        )
        self.assertEqual(game.audio.scene_volume_scale, 0.6)
        game._handle_tank_playing_event(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)
        )
        self.assertEqual(game.audio.scene_volume_scale_target, 1.0)
        self.assertEqual(game.audio.scene_volume_fade_duration_ms, 300)

    def test_audio_crossfade_and_power_sounds_are_available(self):
        game = Game()
        self.assertIn("power_on", game.audio.effects)
        self.assertIn("power_off", game.audio.effects)
        self.assertEqual(len(game.audio.music_channels), 2)

        game.audio.sync_state(game.DESKTOP)
        first_channel = game.audio.active_music_index
        game.audio.sync_state(game.SNAKE_PLAYING)
        self.assertNotEqual(game.audio.active_music_index, first_channel)
        self.assertIsNotNone(game.audio.previous_music_index)

        game.audio.crossfade_started_at -= game.audio.crossfade_duration_ms
        game.audio.sync_state(game.SNAKE_PLAYING)
        self.assertIsNone(game.audio.previous_music_index)

    def test_desktop_has_seven_games_and_two_system_apps(self):
        game = Game()
        enabled_actions = {
            item["action"]
            for page in game.desktop_pages
            for item in page
            if item.get("enabled")
        }
        self.assertEqual(
            enabled_actions,
            {
                "open_gomoku", "open_snake", "open_breakout", "open_2048",
                "open_mines", "open_tetris", "open_air",
                "open_tank",
                "open_system_settings", "open_profile", "open_achievement_wall",
                "open_lore",
            },
        )
        self.assertEqual(
            [item["action"] for item in game.desktop_pages[1]],
            ["open_air", "open_tank",
             "open_system_settings", "open_profile", "open_achievement_wall",
             "open_lore"],
        )

    def test_tank_desktop_icon_and_dispatch_are_registered(self):
        game = Game()
        actions = {item["action"] for page in game.desktop_pages for item in page}
        self.assertIn("open_tank", actions)
        for state in (game.TANK_MENU, game.TANK_CONTROLS, game.TANK_PLAYING, game.TANK_END):
            self.assertIn(state, game._EVENT_DISPATCH)
            self.assertIn(state, game._UPDATE_DISPATCH)
            self.assertIn(state, game._DRAW_DISPATCH)

    def test_chinese_tank_desktop_title_uses_two_x_primary_label(self):
        from meridian.localization import set_language

        game = Game()
        button = next(
            button for button in game._get_desktop_icon_buttons_for_page(1)
            if button["action"] == "open_tank"
        )
        set_language("zh_hans")
        try:
            module = __import__("meridian.shell_desktop", fromlist=["render_pixel_text"])
            with patch(
                "meridian.shell_desktop.render_pixel_text", wraps=module.render_pixel_text
            ) as render:
                game._draw_desktop_icon_button(button)
            title_call = next(
                call for call in render.call_args_list if call.args[1] == "坦克对决"
            )
            self.assertEqual(title_call.kwargs["scale"], 2)
            self.assertFalse(
                any(call.args[1] == "本地双人对战" for call in render.call_args_list)
            )
        finally:
            set_language("en")

    def test_returning_from_tank_clears_transient_input(self):
        game = Game()
        game.state = game.TANK_PLAYING
        game._tank_held = {pygame.K_w: 1}
        game._tank_item_pulses = {"red": True, "blue": True}

        game._go_desktop()

        self.assertEqual(game._tank_held, {})
        self.assertEqual(game._tank_item_pulses, {"red": False, "blue": False})

    def test_tank_match_statistics_are_accumulated_once(self):
        from meridian.tank_engine import EngineEvent
        from meridian.persistence import default_statistics

        game = Game()
        game.save_data["statistics"]["tank"] = default_statistics()["tank"]
        global_completed_before = game.save_data["statistics"]["global"]["games_completed"]
        game._start_tank_battle()
        game._handle_tank_engine_events([
            *[EngineEvent("shot", "red") for _ in range(10)],
            *[EngineEvent("tank_hit", "blue", {"attacker": "red"}) for _ in range(5)],
            EngineEvent("brick_hit", "red"),
            EngineEvent("item_used", "red", {"item": "shield"}),
            EngineEvent("mine_triggered", "blue", {"owner": "red"}),
            EngineEvent("match_ended", "red"),
            EngineEvent("match_ended", "red"),
        ])
        stats = game.save_data["statistics"]["tank"]
        self.assertEqual(stats["shots_fired"], 10)
        self.assertEqual(stats["hits"], 5)
        self.assertEqual(stats["bricks_destroyed"], 1)
        self.assertEqual(stats["shield_uses"], 1)
        self.assertEqual(stats["mine_hits"], 1)
        self.assertEqual(stats["matches_completed"], 1)
        self.assertEqual(stats["wins"], 1)
        self.assertEqual(stats["accurate_matches"], 1)
        self.assertEqual(
            game.save_data["statistics"]["global"]["games_completed"],
            global_completed_before + 1,
        )

    def test_profile_statistics_include_tank_duel(self):
        game = Game()
        sections = game._profile_statistics_sections()
        title, values = next(section for section in sections if "TANK DUEL" in section[0])
        self.assertIn("TANK DUEL", title)
        self.assertEqual([label for label, _ in values], ["MATCHES", "WINS", "KILLS", "ACCURACY"])

    def test_tank_accuracy_requires_ten_shots_and_half_hits(self):
        from meridian.tank_engine import EngineEvent

        for shots, hits in ((9, 9), (10, 4)):
            game = Game()
            game._start_tank_battle()
            game._handle_tank_engine_events([
                *[EngineEvent("shot", "red") for _ in range(shots)],
                *[EngineEvent("tank_hit", "blue", {"attacker": "red"}) for _ in range(hits)],
                EngineEvent("match_ended", "red"),
            ])
            self.assertEqual(game.save_data["statistics"]["tank"].get("accurate_matches", 0), 0)

    def test_password_keypad_does_not_cover_bottom_hint(self):
        game = Game()
        screen_rect = pygame.Rect(70, 70, WINDOW_W - 140, WINDOW_H - 140).inflate(-36, -36)
        hint = pygame.Rect(screen_rect.x, screen_rect.bottom - 28, screen_rect.width, 20)
        self.assertTrue(all(not button["rect"].colliderect(hint) for button in game.password_buttons))

    def test_password_0506_enables_session_developer_mode(self):
        game = Game()
        game.state = game.PASSWORD
        for digit in "0506":
            event = pygame.event.Event(
                pygame.KEYDOWN, {"key": getattr(pygame, f"K_{digit}"), "unicode": digit}
            )
            game._handle_password_event(event)
        game._update_password()
        self.assertTrue(game.dev_mode)
        self.assertEqual(game.transition_target_state, game.DESKTOP)

    def test_developer_panel_uses_f10_and_draws_on_any_page(self):
        game = Game()
        game._enable_developer_mode()
        handled = game._handle_developer_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_F10})
        )
        self.assertTrue(handled)
        self.assertTrue(game.dev_panel_open)
        game.state = game.DESKTOP
        game._draw_desktop()
        game._draw_developer_overlay()

    def test_breakout_end_buttons_restart_and_return_to_menu(self):
        game = Game()
        game.state = game.BREAKOUT_END
        restart, menu = game._get_breakout_end_buttons()

        game._handle_breakout_end_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=restart["rect"].center)
        )
        game._handle_breakout_end_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=restart["rect"].center)
        )
        self.assertEqual(game.state, game.BREAKOUT_PLAYING)

        game.state = game.BREAKOUT_END
        game._handle_breakout_end_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=menu["rect"].center)
        )
        game._handle_breakout_end_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=menu["rect"].center)
        )
        self.assertTrue(game.transition_active)
        self.assertEqual(game.transition_target_state, game.BREAKOUT_MENU)

    def test_boot_completes_at_system_ready_before_password(self):
        game = Game()
        game.state = game.BOOT
        game.boot_phase = "loading"
        game.boot_progress_frame = 600
        game._update_boot()
        self.assertEqual(game.state, game.SYSTEM_READY)

        button = game._get_system_ready_button()
        game._handle_system_ready_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=button.center)
        )
        game._handle_system_ready_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=button.center)
        )
        self.assertTrue(game.transition_active)
        self.assertEqual(game.transition_target_state, game.PASSWORD)

    def test_system_ready_can_switch_language(self):
        game = Game()
        game.state = game.SYSTEM_READY
        game.language = "en"
        game._handle_system_ready_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT})
        )
        self.assertEqual(game.language, "zh_hans")
        game._draw_system_ready_screen()

    def test_desktop_escape_requires_shutdown_confirmation(self):
        game = Game()
        game.state = game.DESKTOP
        game._handle_desktop_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertTrue(game.shutdown_confirm_open)
        self.assertEqual(game.state, game.DESKTOP)

        game._handle_desktop_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertFalse(game.shutdown_confirm_open)
        self.assertEqual(game.state, game.DESKTOP)

        game.shutdown_confirm_open = True
        shutdown = game._get_shutdown_confirm_buttons()[1]
        game._handle_desktop_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=shutdown["rect"].center)
        )
        game._handle_desktop_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=shutdown["rect"].center)
        )
        self.assertEqual(game.state, game.SHUTDOWN)

    def test_system_pages_return_to_desktop_with_fade_transition(self):
        with patch("meridian.persistence.SaveManager.save", return_value=None):
            game = Game()
        for state in (game.SYSTEM_SETTINGS, game.PROFILE, game.LORE_READER):
            game.state = state
            game._desktop_return_effect = "tetris_drop"
            game._go_desktop()
            self.assertEqual(game.transition_target_state, game.DESKTOP)
            self.assertEqual(game.transition_type, "fade")
            game.transition_active = False
            game.transition_target_state = None

    def test_chinese_mines_best_statistics_titles_are_localized(self):
        with patch("meridian.persistence.SaveManager.save", return_value=None):
            game = Game()
        game.language = "zh_hans"
        from meridian.localization import set_language
        set_language("zh_hans")

        titles = [title for title, _ in game._profile_statistics_sections()]

        self.assertIn("扫雷最佳 9 x 9", titles)
        self.assertIn("扫雷最佳 16 x 16", titles)
        self.assertNotIn("MINES BEST 9 x 9", titles)
        self.assertNotIn("MINES BEST 16 x 16", titles)

    def test_tetris_hold_is_limited_to_once_per_piece(self):
        game = Game()
        game._start_tetris_game()
        first = game.tetris_current["kind"]
        game._hold_tetris_piece()
        held = game.tetris_hold
        current = game.tetris_current["kind"]
        game._hold_tetris_piece()
        self.assertEqual(first, held)
        self.assertEqual(current, game.tetris_current["kind"])
        self.assertFalse(game.tetris_can_hold)

    def test_tetris_line_clear_scoring_and_level(self):
        game = Game()
        game._start_tetris_game()
        game.tetris_lines = 9
        game._clear_tetris_lines([21])
        self.assertEqual(game.tetris_lines, 10)
        self.assertEqual(game.tetris_level, 2)
        self.assertEqual(game.tetris_score, 200)
        self.assertTrue(all(cell is None for cell in game.tetris_grid[0]))

    def test_tetris_hard_drop_locks_and_spawns_next_piece(self):
        game = Game()
        game._start_tetris_game()
        original = game.tetris_current
        game._hard_drop_tetris_piece()
        self.assertIsNot(game.tetris_current, original)
        self.assertGreater(game.tetris_score, 0)
        self.assertTrue(any(cell is not None for row in game.tetris_grid for cell in row))

    def test_tetris_menu_preview_does_not_mutate_game_grid(self):
        game = Game()
        game._start_tetris_game()
        grid_before = [row[:] for row in game.tetris_grid]
        game.state = game.TETRIS_MENU
        for _ in range(80):
            game._update_tetris_preview()
        self.assertEqual(game.tetris_grid, grid_before)

    def test_tetris_preview_gameover_resets_after_reaching_top(self):
        game = Game()
        game.tetris_preview_grid = [[None for _ in range(10)] for _ in range(20)]
        game.tetris_preview_grid[1][4] = "J"
        game.tetris_preview_piece = {"kind": "O", "x": 3, "y": -1, "rotation": 0}
        game.tetris_preview_tick = 6
        game._update_tetris_preview()
        self.assertTrue(game.tetris_preview_gameover)

        for _ in range(120):
            game._update_tetris_preview()
        self.assertFalse(game.tetris_preview_gameover)
        self.assertIsNotNone(game.tetris_preview_piece)

    def test_tetris_game_over_and_mouse_pause_controls(self):
        game = Game()
        game._start_tetris_game()
        pause = game._get_tetris_play_buttons()[0]
        game._handle_tetris_playing_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pause["rect"].center)
        )
        game._handle_tetris_playing_event(
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pause["rect"].center)
        )
        self.assertTrue(game.tetris_paused)

        game.tetris_paused = False
        game.tetris_grid[0] = ["I"] * 10
        game.tetris_grid[1] = ["I"] * 10
        game._spawn_tetris_piece()
        self.assertEqual(game.state, game.TETRIS_END)


if __name__ == "__main__":
    unittest.main()
