from .common import *
from .audio import AudioManager
from .arcade_common import ArcadeHubMixin
from .air_raid import AirRaidMixin
from .breakout import BreakoutMixin
from .g2048 import Game2048Mixin
from .gomoku import GomokuMixin
from .mines import MinesMixin
from .shell import ShellMixin
from .snake import SnakeMixin
from .tetris import TetrisMixin
from .system import SystemMixin
from .developer import DeveloperMixin


class Game(
    ShellMixin,
    GomokuMixin,
    MinesMixin,
    Game2048Mixin,
    BreakoutMixin,
    SnakeMixin,
    TetrisMixin,
    ArcadeHubMixin,
    AirRaidMixin,
    DeveloperMixin,
    SystemMixin,
):
    BOOT = "boot"

    def _build_dispatch(self):
        s = self
        self._EVENT_DISPATCH = {
            s.BOOT: None,
            s.SYSTEM_READY: "_handle_system_ready_event",
            s.PASSWORD: "_handle_password_event",
            s.SHUTDOWN: None,
            s.DESKTOP: "_handle_desktop_event",
            s.MENU: "_handle_menu_event",
            s.PLAYING: "_handle_game_event",
            s.END: "_handle_end_event",
            s.SETTINGS: "_handle_settings_event",
            s.SNAKE_MENU: "_handle_snake_menu_event",
            s.SNAKE_PLAYING: "_handle_snake_playing_event",
            s.SNAKE_END: "_handle_snake_end_event",
            s.SNAKE_SETTINGS: "_handle_snake_settings_event",
            s.BREAKOUT_MENU: "_handle_breakout_menu_event",
            s.BREAKOUT_PLAYING: "_handle_breakout_playing_event",
            s.BREAKOUT_END: "_handle_breakout_end_event",
            s.BREAKOUT_SETTINGS: "_handle_breakout_settings_event",
            s.G2048_MENU: "_handle_2048_menu_event",
            s.G2048_PLAYING: "_handle_2048_playing_event",
            s.G2048_END: "_handle_2048_end_event",
            s.MINES_MENU: "_handle_mines_menu_event",
            s.MINES_PLAYING: "_handle_mines_playing_event",
            s.MINES_END: "_handle_mines_end_event",
            s.MINES_SETTINGS: "_handle_mines_settings_event",
            s.TETRIS_MENU: "_handle_tetris_menu_event",
            s.TETRIS_PLAYING: "_handle_tetris_playing_event",
            s.TETRIS_END: "_handle_tetris_end_event",
            s.AIR_MENU: "_handle_air_event",
            s.AIR_SELECT: "_handle_air_event",
            s.AIR_CONTROLS: "_handle_air_event",
            s.AIR_BRIEF: "_handle_air_event",
            s.AIR_ARCHIVE: "_handle_air_event",
            s.AIR_SUPPLY: "_handle_air_event",
            s.AIR_PLAYING: "_handle_air_event",
            s.AIR_END: "_handle_air_event",
            s.SYSTEM_SETTINGS: "_handle_system_settings_event",
            s.PROFILE: "_handle_profile_event",
        }
        self._UPDATE_DISPATCH = {
            s.BOOT: (True, ["_update_boot"]),
            s.SYSTEM_READY: (True, []),
            s.PASSWORD: (True, ["_update_password"]),
            s.SHUTDOWN: (True, ["_update_shutdown"]),
            s.SNAKE_PLAYING: (True, ["_update_snake", "_update_snake_visual_effects"]),
            s.SNAKE_END: (True, ["_update_snake_visual_effects"]),
            s.BREAKOUT_PLAYING: (True, ["_update_breakout", "_update_breakout_visual_effects"]),
            s.BREAKOUT_END: (True, ["_update_breakout_visual_effects"]),
            s.G2048_PLAYING: (True, ["_update_2048_visual_effects"]),
            s.G2048_END: (True, ["_update_2048_visual_effects"]),
            s.MINES_PLAYING: (True, ["_update_mines_visual_effects"]),
            s.MINES_END: (True, ["_update_mines_visual_effects"]),
            s.TETRIS_MENU: (True, ["_update_tetris_preview"]),
            s.TETRIS_PLAYING: (True, ["_update_tetris"]),
            s.TETRIS_END: (True, ["_update_tetris_end"]),
            s.AIR_MENU: (True, ["_update_air_raid"]),
            s.AIR_SELECT: (True, ["_update_air_raid"]),
            s.AIR_CONTROLS: (True, ["_update_air_raid"]),
            s.AIR_BRIEF: (True, ["_update_air_raid"]),
            s.AIR_ARCHIVE: (True, ["_update_air_raid"]),
            s.AIR_SUPPLY: (True, ["_update_air_raid"]),
            s.AIR_PLAYING: (True, ["_update_air_raid"]),
            s.AIR_END: (True, ["_update_air_raid"]),
        }
        self._DRAW_DISPATCH = {
            s.BOOT: "_draw_boot_screen",
            s.SYSTEM_READY: "_draw_system_ready_screen",
            s.PASSWORD: "_draw_password_screen",
            s.DESKTOP: "_draw_desktop",
            s.MENU: "_draw_menu",
            s.PLAYING: "_draw_game",
            s.END: "_draw_end_page",
            s.SETTINGS: "_draw_settings_page",
            s.SNAKE_MENU: "_draw_snake_menu",
            s.SNAKE_PLAYING: "_draw_snake_game",
            s.SNAKE_END: "_draw_snake_end",
            s.SNAKE_SETTINGS: "_draw_snake_settings_page",
            s.BREAKOUT_MENU: "_draw_breakout_menu",
            s.BREAKOUT_PLAYING: "_draw_breakout",
            s.BREAKOUT_END: "_draw_breakout_end",
            s.BREAKOUT_SETTINGS: "_draw_breakout_settings",
            s.G2048_MENU: "_draw_2048_menu",
            s.G2048_PLAYING: "_draw_2048_game",
            s.G2048_END: "_draw_2048_end",
            s.MINES_MENU: "_draw_mines_menu",
            s.MINES_PLAYING: "_draw_mines_game",
            s.MINES_END: "_draw_mines_end",
            s.MINES_SETTINGS: "_draw_mines_settings_page",
            s.TETRIS_MENU: "_draw_tetris_menu",
            s.TETRIS_PLAYING: "_draw_tetris_game",
            s.TETRIS_END: "_draw_tetris_end",
            s.AIR_MENU: "_draw_air_raid",
            s.AIR_SELECT: "_draw_air_raid",
            s.AIR_CONTROLS: "_draw_air_raid",
            s.AIR_BRIEF: "_draw_air_raid",
            s.AIR_ARCHIVE: "_draw_air_raid",
            s.AIR_SUPPLY: "_draw_air_raid",
            s.AIR_PLAYING: "_draw_air_raid",
            s.AIR_END: "_draw_air_raid",
            s.SYSTEM_SETTINGS: "_draw_system_settings",
            s.PROFILE: "_draw_profile",
            s.SHUTDOWN: "_draw_shutdown_screen",
        }
    SYSTEM_READY = "system_ready"
    PASSWORD = "password"
    DESKTOP = "desktop"
    HUB = "hub"
    MENU = "menu"
    PLAYING = "playing"
    END = "end"
    SETTINGS = "settings"
    SNAKE_MENU = "snake_menu"
    SNAKE_PLAYING = "snake_playing"
    SNAKE_END = "snake_end"
    SNAKE_SETTINGS = "snake_settings"
    BREAKOUT_MENU = "breakout_menu"
    BREAKOUT_PLAYING = "breakout_playing"
    BREAKOUT_END = "breakout_end"
    BREAKOUT_SETTINGS = "breakout_settings"
    G2048_MENU = "g2048_menu"
    G2048_PLAYING = "g2048_playing"
    G2048_END = "g2048_end"
    MINES_MENU = "mines_menu"
    MINES_PLAYING = "mines_playing"
    MINES_END = "mines_end"
    MINES_SETTINGS = "mines_settings"
    TETRIS_MENU = "tetris_menu"
    TETRIS_PLAYING = "tetris_playing"
    TETRIS_END = "tetris_end"
    AIR_MENU = "air_menu"
    AIR_SELECT = "air_select"
    AIR_CONTROLS = "air_controls"
    AIR_BRIEF = "air_brief"
    AIR_ARCHIVE = "air_archive"
    AIR_SUPPLY = "air_supply"
    AIR_PLAYING = "air_playing"
    AIR_END = "air_end"
    SYSTEM_SETTINGS = "system_settings"
    PROFILE = "profile"
    SHUTDOWN = "shutdown"

    def __init__(self):
        self.display_surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.screen = pygame.Surface((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("HAO'S GAME DECK")
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio = AudioManager()

        # Global page transition state
        self.transition_active = False
        self.transition_type = "fade"
        self.transition_target_state = None
        self.transition_frame = 0
        self.transition_max_frames = 24
        self.transition_phase = "out"
        self.transition_alpha = 0

        # 褰撳墠閫変腑鐨勫皬娓告垙锛屾湭鏉ュ皬娓告垙鍚堥泦浼氱敤鍒?
        self.current_game_id = "gomoku"
        self.current_game_name = "GOMOKU"

        # 鍚姩鍏堣繘鍏ュ紑鏈哄姩鐢伙紝鍔ㄧ敾缁撴潫鍚庡啀杩涘叆妗岄潰
        self.state = self.BOOT

        # 褰撳墠娓告垙閰嶇疆
        self.board_size = DEFAULT_SIZE
        self.board = Board(self.board_size)

        # ============================================================
        #  Desktop / handheld shell state
        # ============================================================

        # 鍚姩鏃堕棿锛岀敤浜庢闈㈢數閲忎粠 100% 缂撴參涓嬮檷鍒?0%
        self.app_start_ticks = pygame.time.get_ticks()

        # 妗岄潰鍥炬爣鎸変笅鐘舵€?
        self.desktop_pressed_action = None
        self.desktop_volume_open = False
        self.desktop_volume_dragging = False
        self.shutdown_confirm_open = False
        self.shutdown_confirm_pressed = None

        # 闃叉浠庢父鎴?/ 鑿滃崟杩斿洖妗岄潰鏃讹紝鍚屼竴娆?ESC 缁х画瑙﹀彂鍏虫満
        self.desktop_esc_lock_frames = 0

        # ============================================================
        #  Boot / Shutdown animation state
        # ============================================================

        # 寮€鏈哄姩鐢?
        self.boot_frame = 0
        self.boot_visible_chars = 0
        self.boot_next_char_delay = BOOT_TYPE_BASE_DELAY
        self.boot_phase = "fade"   # fade / typing / enter / loading / done
        self.boot_fade_alpha = 0
        self.boot_progress_frame = 0
        self.boot_progress_value = 0.0
        self.system_ready_pressed = False

        # ============================================================
        #  Password screen state
        # ============================================================
        self.password_input = []
        self.password_target = PASSWORD_TARGET
        self.password_max_length = PASSWORD_MAX_LENGTH
        self.password_error = False
        self.password_error_frame = 0
        self.password_pressed_action = None
        self.password_buttons = self._build_password_buttons()

        # 鍏虫満鍔ㄧ敾
        self.shutdown_frame = 0
        self.shutdown_visible_chars = len(SHUTDOWN_TEXT)
        self.shutdown_phase = "show"  # show / deleting / fade / done
        self.shutdown_delete_timer = 0
        self.shutdown_fade_alpha = 0

        # 妗岄潰鍥炬爣瀹氫箟
        self.desktop_page = 0

        # Desktop page slide animation
        self.desktop_slide_active = False
        self.desktop_slide_from_page = 0
        self.desktop_slide_to_page = 0
        self.desktop_slide_direction = 0
        self.desktop_slide_frame = 0
        self.desktop_slide_max_frames = 36

        self.desktop_pages = [
            [
                {"label": "GOMOKU", "action": "open_gomoku", "enabled": True},
                {"label": "SNAKE", "action": "open_snake", "enabled": True},
                {"label": "BREAKOUT", "action": "open_breakout", "enabled": True},
                {"label": "2048", "action": "open_2048", "enabled": True},
                {"label": "MINES", "action": "open_mines", "enabled": True},
                {"label": "TETRIS", "action": "open_tetris", "enabled": True},
            ],
            [
                {"label": "AIR RAID", "action": "open_air", "enabled": True},
                {"label": "SETTINGS", "action": "open_system_settings", "enabled": True},
                {"label": "PROFILE", "action": "open_profile", "enabled": True},
            ],
        ]

        # ============================================================
        #  Snake game state
        # ============================================================

        self.snake = []
        self.snake_dir = (1, 0)
        self.snake_next_dir = (1, 0)
        self.snake_food = (0, 0)
        self.snake_score = 0
        self.snake_best = 0
        self.snake_move_timer = 0
        self.snake_game_over = False
        self.snake_pressed_action = None

        # 璐悆铔囪缃?
        self.snake_speed_mode = "normal"
        self.snake_skin = "green"
        self.snake_body_color = C.SNAKE_BODY
        self.snake_head_color = C.SNAKE_HEAD
        self.snake_base_interval = SNAKE_MOVE_INTERVAL_FRAMES

        # 璐悆铔囩矑瀛愶紙鍚冮鐗╋級
        self.snake_particles = []

        # 姝讳骸鎶栧睆
        self.snake_dead = False
        self.snake_shake_duration = 0
        self.snake_shake_x = 0
        self.snake_shake_y = 0

        # 鍒嗘暟璺冲姩
        self.snake_score_jump = 0
        self.snake_score_jump_frame = 0

        # 褰撳墠鏍煎瓙澶у皬锛屽厛淇濈暀鎺ュ彛
        self.snake_cell_size = SNAKE_CELL_SIZE

        # ============================================================
        #  Breakout game state
        # ============================================================

        self.breakout_bricks = []
        self.breakout_ball = None
        self.breakout_paddle = None

        self.breakout_score = 0
        self.breakout_best = 0
        self.breakout_lives = 3
        self.breakout_level = 1

        self.breakout_particles = []
        self.breakout_score_jump_frame = 0
        self.breakout_shake_duration = 0
        self.breakout_shake_x = 0
        self.breakout_shake_y = 0
        self.breakout_pressed_action = None
        self.breakout_end_panel_frame = 0

        #  Breakout settings
        self.breakout_control_mode = "keyboard"
        self.breakout_difficulty = "normal"
        self.breakout_ball_skin = "yellow"
        self.breakout_brick_skin = "purple"
        self.breakout_paddle_skin = "orange"

        self.breakout_ball_color = C.BREAKOUT_BALL_YELLOW
        self.breakout_brick_color = C.BREAKOUT_BRICK_PURPLE
        self.breakout_paddle_color = C.BREAKOUT_PADDLE_ORANGE

        self.breakout_ball_speed = 5.2
        self.breakout_paddle_width = 126
        self.breakout_paddle_speed = 9

        # 2048 game state
        self.g2048_grid = [[0 for _ in range(G2048_SIZE)] for _ in range(G2048_SIZE)]
        self.g2048_score = 0
        self.g2048_best = 0
        self.g2048_moves = 0
        self.g2048_won = False
        self.g2048_game_over = False
        self.g2048_pressed_action = None
        self.g2048_spawn_anims = []
        self.g2048_merge_anims = []
        self.g2048_slide_anims = []
        self.g2048_score_floaters = []
        self.g2048_particles = []

        self.g2048_invalid_shake = 0
        self.g2048_invalid_shake_dir = "x"

        self.g2048_end_panel_frame = 0
        self.g2048_win_flash_frame = 0

        # Minesweeper game state
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
        self.mines_start_ticks = 0
        self.mines_elapsed_ms = 0
        self.mines_best_times = {(9, 10): None, (9, 15): None, (9, 20): None, (16, 40): None, (16, 50): None, (16, 60): None}
        self.mines_last_click_cell = None
        self.mines_last_click_ticks = 0
        self.mines_reveal_anims = []
        self.mines_flag_anims = []
        self.mines_particles = []
        self.mines_shake = 0
        self.mines_end_panel_frame = 0

        # death/hint
        self.mines_death_anim_active = False
        self.mines_death_phase = "none"   # none / flash / explode / reveal / fade
        self.mines_death_frame = 0
        self.mines_exploded_cell = None
        self.mines_death_fade_alpha = 0
        self.mines_last_open_cell = None
        self.mines_hint_cell = None
        self.mines_hint_flash_frame = 0
        self.mines_hint_cooldown = 0
        self.hover_pos = None

        self._init_tetris_state()
        self._init_air_raid()

        self.anim_tick = 0
        self.win_alpha = 0
        self.shake_duration = 0
        self.shake_x = 0
        self.shake_y = 0

        # ============================================================
        #  Animation states
        # ============================================================

        # 纾佸惛棰勮妫嬪瓙鐘舵€?
        self.preview_active = False
        self.preview_cell = None
        self.preview_x = 0.0
        self.preview_y = 0.0
        self.preview_target_x = 0.0
        self.preview_target_y = 0.0
        self.preview_player = 1

        # 钀藉瓙娉㈢汗鍒楄〃
        # 姣忛」鏍煎紡锛歿"r": r, "c": c, "frame": 0, "max_frames": RIPPLE_MAX_FRAMES}
        self.ripples = []

        # 闈炴硶钀藉瓙鍙嶉
        # 姣忛」鏍煎紡锛歿"r": r, "c": c, "frame": 0, "max_frames": INVALID_MARK_MAX_FRAMES}
        self.invalid_marks = []

        # 鎮仠鍦ㄥ凡鏈夋瀛愪笂鐨勪綅缃?
        self.occupied_hover_pos = None

        # 鎮旀鍔ㄧ敾
        # 姣忛」鏍煎紡锛歿"r": r, "c": c, "player": player, "frame": 0, "max_frames": UNDO_ANIM_MAX_FRAMES}
        self.undo_animations = []

        # 鑳滃埄杩炵嚎鍔ㄧ敾
        self.win_line_frame = 0
        self.win_line_active = False

        # 鑳滃埄妫嬪瓙渚濇闂儊
        self.win_stone_flash_frame = 0
        self.win_stone_flash_active = False

        # 渚濇鐖嗙矑瀛愮殑绱㈠紩锛屼繚璇佷簲棰楁瀛愭寜椤哄簭鍠峰彂
        self.win_particle_burst_index = -1

        # 鎸夐挳鐐瑰嚮鐘舵€?
        self.pressed_button_action = None

        # 鑳滃埄鍚庡欢杩熻繘鍏ョ粨鏉熼〉
        self.end_page_delay = 0

        # 缁撴潫椤靛叆鍦哄姩鐢?
        self.end_panel_anim_frame = 0
        self.end_text_flash_tick = 0
        self.end_overlay_alpha = 0

        # Animations: list of {type, r, c, player, frame, max_frames}
        self.animations = []
        # Particles
        self.particles = []
        # Score tracking
        self.black_wins = 0
        self.white_wins = 0
        self.draws = 0
        self._win_scored = False  # prevent double-counting on undo + re-win

        # Pre-render background
        self.wood_bg = create_wood_texture(WINDOW_W, WINDOW_H)

        # Fonts
        self.font_title = pygame.font.Font(None, 28)
        self.font_menu_title = pygame.font.Font(None, 32)
        self.font_status = pygame.font.Font(None, 18)
        self.font_btn = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 14)

        # ============================================================
        #  Menu hanging-logo settings
        # ============================================================
        self.menu_logo_text = "GOMOKU"

        # 淇锛氬師鏉?scale=4 澶ぇ锛屽叚涓悐鐗屾€诲搴︿細瓒呭嚭绐楀彛
        self.menu_logo_scale = 3

        # 姣忎釜鍚婄墝鐙珛鎽嗗姩鍙傛暟
        # 鎽嗗箙鎺у埗寰楁洿灏忥紝閬垮厤鍚婄墝鐢╁嚭杈圭晫
        self.menu_logo_phase = [0.00, 0.87, 1.76, 2.43, 3.39, 4.12]
        self.menu_logo_swing_amp = [4.8, 4.2, 5.0, 4.4, 4.7, 4.1]
        self.menu_logo_micro_amp = [0.22, 0.18, 0.24, 0.20, 0.22, 0.18]

        # 淇锛氱怀瀛愬彉鐭紝鍚婄墝鏁翠綋涓婄Щ锛屽噺灏戝崰鐢ㄧ┖闂?
        self.menu_logo_rope_len = [22, 21, 23, 22, 22, 21]

        # 淇锛氬悐鐗岄棿璺濈缉灏忥紝閬垮厤 GOMOKU 瓒呭嚭宸﹀彸杈圭晫
        self.menu_logo_gap = 6

        # 椤堕儴妯浣嶇疆
        self.menu_logo_beam_y = 92

        # 缂撳瓨灏侀潰鍚婄墝绱犳潗
        self.menu_logo_letters = []
        self._build_menu_logo_assets()

        # Stone assets (regenerated when board_size changes)
        self._rebuild_stone_assets()

        # Menu buttons
        self._build_menu_buttons()

        # End page buttons
        self.end_btns = []

        # Win overlay surface
        self.win_overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        self._init_developer()
        self._init_system()
        self._build_dispatch()

    def handle_events(self):
        for raw_event in pygame.event.get():
            event = self._map_event_to_logical(raw_event)
            if event.type == pygame.QUIT:
                if self.state != self.SHUTDOWN:
                    self._save_now()
                    self._start_shutdown()
                return

            # skip input during transition
            if self.transition_active: continue
            self.audio.handle_input_event(event)
            if self._handle_developer_event(event):
                continue

            handler = self._EVENT_DISPATCH.get(self.state)
            if handler is not None:
                getattr(self, handler)(event)

    def update(self):
        self.anim_tick += 1
        self._update_persistence()
        self.audio.sync_state(self.state)
        self._update_transition()
        self._update_desktop_slide()
        if self.dev_panel_open:
            return

        if self.desktop_esc_lock_frames > 0:
            self.desktop_esc_lock_frames -= 1

        # 寮€鏈哄姩鐢诲彧鏇存柊寮€鏈虹姸鎬侊紝涓嶆洿鏂版父鎴忛€昏緫
        entry = self._UPDATE_DISPATCH.get(self.state)
        if entry is not None:
            should_return, methods = entry
            for method_name in methods:
                getattr(self, method_name)()
            if should_return:
                return

        # Drop animations
        for anim in self.animations[:]:
            anim["frame"] += 1
            if anim["frame"] >= anim["max_frames"]:
                self.animations.remove(anim)

        # Magnetic hover preview
        if self.preview_active:
            dx = self.preview_target_x - self.preview_x
            dy = self.preview_target_y - self.preview_y

            self.preview_x += dx * MAGNET_PULL
            self.preview_y += dy * MAGNET_PULL

            # 闈炲父鎺ヨ繎浜ゅ弶鐐规椂鐩存帴鍚搁檮鍒颁腑蹇冿紝閬垮厤姘歌繙灏忔暟鎶栧姩
            if abs(dx) < 0.6 and abs(dy) < 0.6:
                self.preview_x = self.preview_target_x
                self.preview_y = self.preview_target_y

        # Ripples
        for ripple in self.ripples[:]:
            ripple["frame"] += 1
            if ripple["frame"] >= ripple["max_frames"]:
                self.ripples.remove(ripple)

        # Invalid move marks
        for mark in self.invalid_marks[:]:
            mark["frame"] += 1
            if mark["frame"] >= mark["max_frames"]:
                self.invalid_marks.remove(mark)

        # Undo animations
        for undo_anim in self.undo_animations[:]:
            undo_anim["frame"] += 1
            if undo_anim["frame"] >= undo_anim["max_frames"]:
                self.undo_animations.remove(undo_anim)

        # Win line animation
        if self.win_line_active:
            self.win_line_frame += 1
            if self.win_line_frame > WIN_LINE_MAX_FRAMES:
                self.win_line_frame = WIN_LINE_MAX_FRAMES

        # Win stone sequential flash
        if self.win_stone_flash_active:
            self.win_stone_flash_frame += 1

            ordered = self._get_ordered_win_stones()
            current_index = min(len(ordered) - 1, self.win_stone_flash_frame // WIN_STONE_FLASH_STEP) if ordered else -1

            # 姣忔帹杩涘埌涓嬩竴棰楄儨鍒╂瀛愶紝灏辫ˉ涓€娆″皬鍨嬬矑瀛愬柗鍙?
            if current_index > self.win_particle_burst_index and 0 <= current_index < len(ordered):
                self.win_particle_burst_index = current_index
                rr, cc = ordered[current_index]
                self._spawn_win_stone_burst(rr, cc)

            if self.win_stone_flash_frame >= WIN_STONE_FLASH_MAX_FRAMES:
                self.win_stone_flash_frame = WIN_STONE_FLASH_MAX_FRAMES

        # Delayed end page
        if self.board.winner != 0 and self.end_page_delay > 0:
            self.end_page_delay -= 1
            if self.end_page_delay <= 0 and hasattr(self, "END"):
                self.state = self.END
                self.end_panel_anim_frame = 0
                self.end_text_flash_tick = 0
                self.end_overlay_alpha = 0

        # End page animation
        if self.state == self.END:
            if self.end_panel_anim_frame < END_PANEL_POP_FRAMES:
                self.end_panel_anim_frame += 1

            self.end_text_flash_tick += 1

            if self.end_overlay_alpha < 205:
                self.end_overlay_alpha = min(205, self.end_overlay_alpha + 10)

        # Particles
        for p in self.particles[:]:
            if not p.update():
                self.particles.remove(p)

        # Screen shake
        if self.shake_duration > 0:
            self.shake_duration -= 1
            intensity = max(1, self.shake_duration // 2)
            self.shake_x = random.randint(-intensity, intensity)
            self.shake_y = random.randint(-intensity, intensity)
        else:
            self.shake_x = 0
            self.shake_y = 0
        if not self.screen_shake_enabled:
            self.shake_duration = 0
            self.shake_x = self.shake_y = 0
            self.snake_shake_duration = 0
            self.snake_shake_x = self.snake_shake_y = 0
            self.breakout_shake_duration = 0
            self.breakout_shake_x = self.breakout_shake_y = 0

        # Win overlay fade-in
        if self.board.winner != 0 and self.win_alpha < 160:
            self.win_alpha = min(160, self.win_alpha + 4)

    def draw(self):
        handler = self._DRAW_DISPATCH.get(self.state)
        if handler is not None:
            getattr(self, handler)()
        self._draw_achievement_notification()
        self._draw_developer_overlay()
        self._draw_transition_overlay()
        self._present_frame()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(max(1, int(60 * self.dev_game_speed)))
        self._save_now()
        self.audio.stop()
        pygame.quit()
        sys.exit()
