from __future__ import annotations

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
from .tank_battle import TankBattleMixin
from .system import SystemMixin
from .developer import DeveloperMixin

# ── Dynamic Game State Registry ──────────────────────────────
# New games register their states here without modifying app.py.
# Each entry: (state_attr_name, event_handler, update_methods, draw_handler)
_GAME_STATE_REGISTRY: list[tuple[str, str | None, list[str] | None, str | None]] = []


def _register_game_states(state_name: str, event_handler: str | None,
                         update_methods: list[str] | None,
                         draw_handler: str | None) -> None:
    """Register dispatch entries for a new game.

    Args:
        state_name: The state string constant (e.g. "pacman_menu")
        event_handler: Method name string for event handling
        update_methods: List of method name strings for update (empty list = no update)
        draw_handler: Method name string for draw
    """
    _GAME_STATE_REGISTRY.append((state_name, event_handler, update_methods, draw_handler))


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
    TankBattleMixin,
    DeveloperMixin,
    SystemMixin,
):
    BOOT = "boot"

    def _build_dispatch(self):
        s = self

        # ── Event Dispatch ──────────────────────────────────────
        self._EVENT_DISPATCH = {
            s.BOOT: None, s.SHUTDOWN: None,
            s.SYSTEM_READY: "_handle_system_ready_event",
            s.PASSWORD: "_handle_password_event",
            s.DESKTOP: "_handle_desktop_event",
            s.MENU: "_handle_menu_event", s.PLAYING: "_handle_game_event",
            s.END: "_handle_end_event", s.SETTINGS: "_handle_settings_event",
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
            s.AIR_SKINS: "_handle_air_skins_event",
            s.AIR_STORY: "_handle_air_story_event",
            s.SYSTEM_SETTINGS: "_handle_system_settings_event",
            s.PROFILE: "_handle_profile_event",
            s.ACHIEVEMENT_WALL: "_handle_achievement_wall_event",
            s.LORE_READER: "_handle_lore_reader_event",
            s.LORE_STORY: "_handle_lore_story_event",
        }
        # Air Raid states that share the same event handler
        for state in (s.AIR_MENU, s.AIR_SELECT, s.AIR_CONTROLS, s.AIR_BRIEF,
                       s.AIR_ARCHIVE, s.AIR_SUPPLY, s.AIR_PLAYING, s.AIR_END):
            self._EVENT_DISPATCH[state] = "_handle_air_event"
        self._EVENT_DISPATCH.update({
            s.TANK_MENU: "_handle_tank_menu_event",
            s.TANK_CONTROLS: "_handle_tank_controls_event",
            s.TANK_PLAYING: "_handle_tank_playing_event",
            s.TANK_END: "_handle_tank_end_event",
        })

        # ── Update Dispatch ─────────────────────────────────────
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
        }
        for state in (s.AIR_MENU, s.AIR_SELECT, s.AIR_CONTROLS, s.AIR_BRIEF,
                       s.AIR_ARCHIVE, s.AIR_SUPPLY, s.AIR_PLAYING, s.AIR_END):
            self._UPDATE_DISPATCH[state] = (True, ["_update_air_raid"])
        for state in (s.TANK_MENU, s.TANK_CONTROLS, s.TANK_END):
            self._UPDATE_DISPATCH[state] = (True, [])
        self._UPDATE_DISPATCH[s.TANK_PLAYING] = (True, ["_update_tank_battle"])

        # ── Draw Dispatch ───────────────────────────────────────
        self._DRAW_DISPATCH = {
            s.BOOT: "_draw_boot_screen",
            s.SYSTEM_READY: "_draw_system_ready_screen",
            s.PASSWORD: "_draw_password_screen",
            s.DESKTOP: "_draw_desktop",
            s.MENU: "_draw_menu", s.PLAYING: "_draw_game",
            s.END: "_draw_end_page", s.SETTINGS: "_draw_settings_page",
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
            s.AIR_SKINS: "_draw_air_skins",
            s.AIR_STORY: "_draw_air_story",
            s.SYSTEM_SETTINGS: "_draw_system_settings",
            s.PROFILE: "_draw_profile",
            s.ACHIEVEMENT_WALL: "_draw_achievement_wall",
            s.LORE_READER: "_draw_lore_reader",
            s.LORE_STORY: "_draw_lore_story",
            s.SHUTDOWN: "_draw_shutdown_screen",
        }
        for state in (s.AIR_MENU, s.AIR_SELECT, s.AIR_CONTROLS, s.AIR_BRIEF,
                       s.AIR_ARCHIVE, s.AIR_SUPPLY, s.AIR_PLAYING, s.AIR_END):
            self._DRAW_DISPATCH[state] = "_draw_air_raid"
        self._DRAW_DISPATCH.update({
            s.TANK_MENU: "_draw_tank_menu",
            s.TANK_CONTROLS: "_draw_tank_controls",
            s.TANK_PLAYING: "_draw_tank_playing",
            s.TANK_END: "_draw_tank_end",
        })

        # Merge dynamically registered game states from external modules
        for state_name, evt, upd, drw in _GAME_STATE_REGISTRY:
            state_attr = getattr(s, state_name, state_name)
            if evt is not None:
                self._EVENT_DISPATCH[state_attr] = evt
            if upd is not None:
                self._UPDATE_DISPATCH[state_attr] = (True, list(upd))
            if drw is not None:
                self._DRAW_DISPATCH[state_attr] = drw
    SYSTEM_READY = "system_ready"
    PASSWORD = "password"
    DESKTOP = "desktop"
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
    AIR_SKINS = "air_skins"
    AIR_STORY = "air_story"
    TANK_MENU = "tank_menu"
    TANK_CONTROLS = "tank_controls"
    TANK_PLAYING = "tank_playing"
    TANK_END = "tank_end"
    SYSTEM_SETTINGS = "system_settings"
    PROFILE = "profile"
    ACHIEVEMENT_WALL = "achievement_wall"
    LORE_READER = "lore_reader"
    LORE_STORY = "lore_story"
    SHUTDOWN = "shutdown"

    def __init__(self) -> None:
        # === 核心基础设施 ===
        self.display_surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.screen = pygame.Surface((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("MERIDIAN")
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio = AudioManager()
        self.state = self.BOOT
        self.anim_tick = 0

        # 字体
        self.font_title = pygame.font.Font(None, 28)
        self.font_menu_title = pygame.font.Font(None, 32)
        self.font_status = pygame.font.Font(None, 18)
        self.font_btn = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 14)

        # === Mixin 初始化 ===
        # SystemMixin 必须最后调用，因为 _apply_loaded_data() 会覆盖持久化状态
        self._init_transition()
        self._init_boot()
        self._init_desktop()
        self._init_password()
        self._init_prologue()
        self._init_gomoku()
        self._init_snake()
        self._init_breakout()
        self._init_2048()
        self._init_mines()
        self._init_tetris_state()
        self._init_air_raid()
        self._init_tank_battle()
        self._init_developer()
        self._init_system()          # ← 最后调用，覆盖已加载的持久化数据
        self._build_dispatch()

    def handle_events(self) -> None:
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

    def update(self) -> None:
        self.anim_tick += 1
        self._update_persistence()
        self.audio.sync_state(self.state)
        self._update_transition()
        self._update_desktop_slide()
        if self.dev_panel_open:
            return

        if self.desktop_esc_lock_frames > 0:
            self.desktop_esc_lock_frames -= 1

        entry = self._UPDATE_DISPATCH.get(self.state)
        if entry is not None:
            should_return, methods = entry
            for method_name in methods:
                getattr(self, method_name)()
            if should_return:
                return

        self._update_drop_animations()
        self._update_magnetic_preview()
        self._update_ripples()
        self._update_invalid_marks()
        self._update_undo_animations()
        self._update_win_line()
        self._update_win_stone_flash()
        self._update_delayed_end_page()
        self._update_end_page_animation()
        self._update_particles()
        self._update_screen_shake()
        self._update_win_overlay()

    # ── Animation Subsystems ────────────────────────────────────

    def _update_drop_animations(self) -> None:
        for anim in self.animations[:]:
            anim["frame"] += 1
            if anim["frame"] >= anim["max_frames"]:
                self.animations.remove(anim)

    def _update_magnetic_preview(self) -> None:
        if not self.preview_active:
            return
        dx = self.preview_target_x - self.preview_x
        dy = self.preview_target_y - self.preview_y
        self.preview_x += dx * MAGNET_PULL
        self.preview_y += dy * MAGNET_PULL
        if abs(dx) < 0.6 and abs(dy) < 0.6:
            self.preview_x = self.preview_target_x
            self.preview_y = self.preview_target_y

    def _update_ripples(self) -> None:
        for ripple in self.ripples[:]:
            ripple["frame"] += 1
            if ripple["frame"] >= ripple["max_frames"]:
                self.ripples.remove(ripple)

    def _update_invalid_marks(self) -> None:
        for mark in self.invalid_marks[:]:
            mark["frame"] += 1
            if mark["frame"] >= mark["max_frames"]:
                self.invalid_marks.remove(mark)

    def _update_undo_animations(self) -> None:
        for undo_anim in self.undo_animations[:]:
            undo_anim["frame"] += 1
            if undo_anim["frame"] >= undo_anim["max_frames"]:
                self.undo_animations.remove(undo_anim)

    def _update_win_line(self) -> None:
        if self.win_line_active:
            self.win_line_frame += 1
            if self.win_line_frame > WIN_LINE_MAX_FRAMES:
                self.win_line_frame = WIN_LINE_MAX_FRAMES

    def _update_win_stone_flash(self) -> None:
        if not self.win_stone_flash_active:
            return
        self.win_stone_flash_frame += 1
        ordered = self._get_ordered_win_stones()
        current_index = min(len(ordered) - 1, self.win_stone_flash_frame // WIN_STONE_FLASH_STEP) if ordered else -1
        if current_index > self.win_particle_burst_index and 0 <= current_index < len(ordered):
            self.win_particle_burst_index = current_index
            rr, cc = ordered[current_index]
            self._spawn_win_stone_burst(rr, cc)
        if self.win_stone_flash_frame >= WIN_STONE_FLASH_MAX_FRAMES:
            self.win_stone_flash_frame = WIN_STONE_FLASH_MAX_FRAMES

    def _update_delayed_end_page(self) -> None:
        if self.board.winner != 0 and self.end_page_delay > 0:
            self.end_page_delay -= 1
            if self.end_page_delay <= 0 and hasattr(self, "END"):
                self.state = self.END
                self.end_panel_anim_frame = 0
                self.end_text_flash_tick = 0
                self.end_overlay_alpha = 0

    def _update_end_page_animation(self) -> None:
        if self.state != self.END:
            return
        if self.end_panel_anim_frame < END_PANEL_POP_FRAMES:
            self.end_panel_anim_frame += 1
        self.end_text_flash_tick += 1
        if self.end_overlay_alpha < 205:
            self.end_overlay_alpha = min(205, self.end_overlay_alpha + 10)

    def _update_particles(self) -> None:
        for p in self.particles[:]:
            if not p.update():
                self.particles.remove(p)

    def _update_screen_shake(self) -> None:
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

    def _update_win_overlay(self) -> None:
        if self.board.winner != 0 and self.win_alpha < 160:
            self.win_alpha = min(160, self.win_alpha + 4)

    def draw(self) -> None:
        handler = self._DRAW_DISPATCH.get(self.state)
        if handler is not None:
            getattr(self, handler)()
        self._draw_achievement_notification()
        self._draw_developer_overlay()
        self._draw_transition_overlay()
        self._present_frame()

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(max(1, int(60 * self.dev_game_speed)))
        self._save_now()
        self.audio.stop()
        pygame.quit()
        sys.exit()
