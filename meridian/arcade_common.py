"""Shared presentation helpers for the second-page arcade games."""

from .common import *
from .localization import get_chinese_font, is_chinese
from . import lore as _lore
from .ui_components import anchored_blit, draw_pixel_panel, fit_pixel_text


def arcade_button(rect, label, action, selected=False):
    return {"rect": pygame.Rect(rect), "label": label, "action": action, "selected": selected}


def draw_arcade_button(game, button, palette, hovered=False, pressed=False):
    rect = button["rect"].copy()
    if hovered:
        rect = rect.inflate(8, 6)
    if pressed:
        rect.y += 4
    pygame.draw.rect(game.screen, C.OUTLINE, rect.move(5, 5))
    fill = palette["hover"] if hovered or button.get("selected") else palette["panel_dark"]
    draw_pixel_panel(
        game.screen,
        rect,
        {"outline": C.OUTLINE, "panel": fill},
        border=2.5,
    )
    pygame.draw.rect(game.screen, palette["accent"], rect.inflate(-12, -12), 2)
    text = fit_pixel_text(
        game.font_btn,
        button["label"],
        palette["text"],
        rect.width - 20,
        preferred_scale=2,
    )
    anchored_blit(game.screen, text, rect, "center")


def handle_arcade_buttons(game, event, buttons, pressed_attr, actions):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for button in buttons:
            if button["rect"].collidepoint(event.pos):
                setattr(game, pressed_attr, button["action"])
                return True
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        pressed = getattr(game, pressed_attr)
        for button in buttons:
            if button["rect"].collidepoint(event.pos) and pressed == button["action"]:
                setattr(game, pressed_attr, None)
                action = actions.get(button["action"])
                if action:
                    action()
                return True
        setattr(game, pressed_attr, None)
    return False


def draw_arcade_frame(game, title, subtitle, palette):
    game.screen.fill(palette["bg"])
    outer = pygame.Rect(32, 28, WINDOW_W - 64, WINDOW_H - 56)
    draw_pixel_panel(
        game.screen,
        outer,
        {"outline": C.OUTLINE, "panel": palette["panel"]},
        border=5,
    )
    pygame.draw.rect(game.screen, palette["accent"], outer.inflate(-22, -22), 2)
    heading = fit_pixel_text(
        game.font_menu_title,
        title,
        palette["accent_light"],
        outer.width - 48,
        preferred_scale=3,
    )
    sub = fit_pixel_text(
        game.font_small,
        subtitle,
        palette["text"],
        outer.width - 48,
        preferred_scale=2,
    )
    heading_row = pygame.Rect(outer.x, outer.y + 24, outer.width, heading.get_height())
    anchored_blit(game.screen, heading, heading_row, "center")
    subtitle_y = outer.y + (100 if is_chinese() else 106)
    subtitle_row = pygame.Rect(outer.x, subtitle_y, outer.width, sub.get_height())
    anchored_blit(game.screen, sub, subtitle_row, "center")
    return outer


def menu_buttons(include_mode=False):
    cx, y, w, h, gap = WINDOW_W // 2, 350, 250, 48, 16
    items = [("CONTINUE", "continue"), ("LEVEL SELECT", "select")]
    if include_mode:
        items.append(("ENDLESS", "endless"))
    items += [("CONTROLS", "controls"), ("DESKTOP", "desktop")]
    return [arcade_button((cx - w // 2, y + i * (h + gap), w, h), label, action)
            for i, (label, action) in enumerate(items)]


def level_select_buttons(count, unlocked, page):
    buttons = []
    start = page * 12
    for index in range(start, min(count, start + 12)):
        col, row = (index - start) % 6, (index - start) // 6
        rect = (130 + col * 174, 210 + row * 100, 140, 62)
        label = f"{index + 1:02d}" if index < unlocked else "LOCKED"
        buttons.append(arcade_button(rect, label, f"level:{index}", index < unlocked))
    buttons += [
        arcade_button((90, 620, 180, 44), "PREV", "prev"),
        arcade_button((WINDOW_W - 270, 620, 180, 44), "NEXT", "next"),
        arcade_button((WINDOW_W // 2 - 100, 620, 200, 44), "BACK", "back"),
    ]
    return buttons


def end_buttons():
    return [
        arcade_button((WINDOW_W // 2 - 220, 520, 200, 50), "RETRY", "retry"),
        arcade_button((WINDOW_W // 2 + 20, 520, 200, 50), "MENU", "menu"),
    ]


def draw_pause_overlay(game, palette):
    shade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    shade.fill(C.OVERLAY_PAUSE)
    game.screen.blit(shade, (0, 0))
    panel = pygame.Rect(WINDOW_W // 2 - 230, WINDOW_H // 2 - 90, 460, 180)
    draw_pixel_panel(
        game.screen,
        panel,
        {"outline": C.OUTLINE, "panel": palette["panel"]},
        border=5,
    )
    text = fit_pixel_text(
        game.font_menu_title,
        "PAUSED",
        palette["accent_light"],
        panel.width - 40,
        preferred_scale=3,
    )
    hint = fit_pixel_text(
        game.font_small,
        "P TO RESUME   ESC FOR MENU",
        palette["text"],
        panel.width - 40,
        preferred_scale=2,
    )
    title_row = pygame.Rect(panel.x, panel.y + 38, panel.width, text.get_height())
    hint_row = pygame.Rect(panel.x, panel.y + 108, panel.width, hint.get_height())
    anchored_blit(game.screen, text, title_row, "center")
    anchored_blit(game.screen, hint, hint_row, "center")


class ArcadeHubMixin:
    # ── Prologue System ──────────────────────────────────────

    def _init_prologue(self):
        self.prologue_active = False
        self.prologue_game_id = None
        self.prologue_lines = []
        self.prologue_title = ""
        self.prologue_page = 0
        self.prologue_dismiss_action = None  # callable to run on dismiss

    def _check_and_show_prologue(self, game_id):
        """Return True if a prologue is being shown (menu should skip rendering)."""
        if self.prologue_active:
            return True
        seen = self.save_data.get("lore", {}).get("prologues_seen", [])
        if game_id in seen:
            return False
        world = _lore.get_world(game_id)
        if world is None:
            return False
        lines = world["prologue_zh"] if is_chinese() else world["prologue_en"]
        self.prologue_active = True
        self.prologue_game_id = game_id
        self.prologue_lines = list(lines)
        self.prologue_title = world["world_name_zh"] if is_chinese() else world["world_name_en"]
        self.prologue_page = 0
        return True

    def _handle_prologue_event(self, event, on_dismiss=None):
        """Handle events while prologue is showing. CALLER must check prologue_active first."""
        if not self.prologue_active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self._dismiss_prologue(on_dismiss)
                return True
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                lines_per_page = 5
                max_page = max(0, (len(self.prologue_lines) - 1) // lines_per_page)
                self.prologue_page = min(self.prologue_page + 1, max_page)
                return True
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.prologue_page = max(0, self.prologue_page - 1)
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._dismiss_prologue(on_dismiss)
            return True
        return False

    def _dismiss_prologue(self, on_dismiss):
        self.prologue_active = False
        game_id = self.prologue_game_id
        self.prologue_game_id = None
        self.prologue_lines = []
        # Mark as seen
        lore_data = self.save_data.setdefault("lore", {})
        seen = lore_data.setdefault("prologues_seen", [])
        if game_id and game_id not in seen:
            seen.append(game_id)
        self._save_now()
        if on_dismiss:
            on_dismiss()

    def _draw_prologue_screen(self):
        """Draw the prologue overlay. Only call when prologue_active is True."""
        if not self.prologue_active:
            return

        # Darken background
        shade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 220))
        self.screen.blit(shade, (0, 0))

        # Panel
        panel = pygame.Rect(140, 60, WINDOW_W - 280, WINDOW_H - 120)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 4)
        pygame.draw.rect(self.screen, C.LORE_PANEL, panel.inflate(-8, -8))
        pygame.draw.rect(self.screen, C.LORE_ACCENT, panel.inflate(-16, -16), 2)

        # Title
        title_text = render_pixel_text(
            self.font_menu_title, self.prologue_title, C.LORE_TITLE, scale=3)
        self.screen.blit(
            title_text,
            (panel.centerx - title_text.get_width() // 2, panel.y + 28),
        )

        # Lines (paginated)
        lines_per_page = 5
        start = self.prologue_page * lines_per_page
        page_lines = self.prologue_lines[start:start + lines_per_page]
        max_page = max(0, (len(self.prologue_lines) - 1) // lines_per_page)

        story_font = get_chinese_font(16)
        for li, line in enumerate(page_lines):
            y = panel.y + 100 + li * 72
            txt = render_pixel_text(story_font, line, C.LORE_TEXT, scale=1)
            self.screen.blit(txt, (panel.x + 50, y))

        # Page indicator (if multi-page)
        if max_page > 0:
            page_indicator = f"{self.prologue_page + 1} / {max_page + 1}"
            pi = render_pixel_text(self.font_small, page_indicator, C.LORE_MUTED, scale=1)
            self.screen.blit(
                pi,
                (panel.centerx - pi.get_width() // 2, panel.bottom - 70),
            )

        # Hint
        hint_text = "ENTER / CLICK TO CONTINUE"
        hint = render_pixel_text(
            self.font_small, hint_text, C.LORE_ACCENT_LIGHT, scale=2)
        self.screen.blit(
            hint,
            (panel.centerx - hint.get_width() // 2, panel.bottom - 48),
        )

    # ── Existing methods ─────────────────────────────────────

    def _handle_level_select(self, event, game_key, count, start_level, menu_state):
        page_attr = f"{game_key}_select_page"
        pressed_attr = f"{game_key}_pressed"
        page = getattr(self, page_attr, 0)
        unlocked = self.save_data["progress"][game_key]["unlocked"]
        buttons = level_select_buttons(count, unlocked, page)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = menu_state
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                setattr(self, page_attr, max(0, page - 1))
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                setattr(self, page_attr, min((count - 1) // 12, page + 1))
            return

        def choose(action):
            if action == "back":
                self.state = menu_state
            elif action == "prev":
                setattr(self, page_attr, max(0, page - 1))
            elif action == "next":
                setattr(self, page_attr, min((count - 1) // 12, page + 1))
            elif action.startswith("level:"):
                index = int(action.split(":", 1)[1])
                if index < unlocked:
                    start_level(index)

        actions = {button["action"]: lambda action=button["action"]: choose(action)
                   for button in buttons}
        handle_arcade_buttons(self, event, buttons, pressed_attr, actions)

    def _draw_level_select(self, title, count, unlocked, palette, game_key=None):
        game_key = game_key or title.lower().split()[0]
        page = getattr(self, f"{game_key}_select_page", 0)
        pressed = getattr(self, f"{game_key}_pressed", None)
        draw_arcade_frame(self, title, f"UNLOCKED {unlocked:02d} / {count:02d}", palette)
        for button in level_select_buttons(count, unlocked, page):
            hovered = button["rect"].collidepoint(self._logical_mouse_pos())
            draw_arcade_button(self, button, palette, hovered, pressed == button["action"])

    def _draw_controls(self, lines, palette):
        panel = pygame.Rect(325, 175, 630, 360)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, palette["panel_dark"], panel.inflate(-10, -10))
        for index, line in enumerate(lines):
            text = render_pixel_text(self.font_small, line, palette["text"], scale=2)
            self.screen.blit(text, (panel.centerx - text.get_width() // 2, 225 + index * 58))
        hint = render_pixel_text(self.font_small, "ESC TO RETURN", palette["accent_light"], scale=2)
        self.screen.blit(hint, (panel.centerx - hint.get_width() // 2, 485))

    def _draw_simple_end(self, title, detail, palette, pressed=None):
        shade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        shade.fill(C.OVERLAY_END)
        self.screen.blit(shade, (0, 0))
        panel = pygame.Rect(335, 155, 610, 460)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 6)
        pygame.draw.rect(self.screen, palette["panel"], panel.inflate(-12, -12))
        pygame.draw.rect(self.screen, palette["accent"], panel.inflate(-28, -28), 2)
        heading = render_pixel_text(self.font_menu_title, title, palette["accent_light"], scale=3)
        summary = render_pixel_text(self.font_small, detail, palette["text"], scale=2)
        self.screen.blit(heading, (panel.centerx - heading.get_width() // 2, 235))
        self.screen.blit(summary, (panel.centerx - summary.get_width() // 2, 340))
        mouse = self._logical_mouse_pos()
        for button in end_buttons():
            draw_arcade_button(
                self,
                button,
                palette,
                button["rect"].collidepoint(mouse),
                pressed == button["action"],
            )
