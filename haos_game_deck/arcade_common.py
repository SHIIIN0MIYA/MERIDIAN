"""Shared presentation helpers for the second-page arcade games."""

from .common import *


def arcade_button(rect, label, action, selected=False):
    return {"rect": pygame.Rect(rect), "label": label, "action": action, "selected": selected}


def draw_arcade_button(game, button, palette, hovered=False, pressed=False):
    rect = button["rect"].copy()
    if hovered:
        rect = rect.inflate(8, 6)
    if pressed:
        rect.y += 4
    pygame.draw.rect(game.screen, C.OUTLINE, rect.move(5, 5))
    pygame.draw.rect(game.screen, C.OUTLINE, rect)
    fill = palette["hover"] if hovered or button.get("selected") else palette["panel_dark"]
    pygame.draw.rect(game.screen, fill, rect.inflate(-5, -5))
    pygame.draw.rect(game.screen, palette["accent"], rect.inflate(-12, -12), 2)
    text = render_pixel_text(game.font_btn, button["label"], palette["text"], scale=2)
    if text.get_width() > rect.width - 20:
        text = render_pixel_text(game.font_small, button["label"], palette["text"], scale=1)
    game.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))


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
    pygame.draw.rect(game.screen, C.OUTLINE, outer, 5)
    pygame.draw.rect(game.screen, palette["panel"], outer.inflate(-10, -10))
    pygame.draw.rect(game.screen, palette["accent"], outer.inflate(-22, -22), 2)
    heading = render_pixel_text(game.font_menu_title, title, palette["accent_light"], scale=3)
    sub = render_pixel_text(game.font_small, subtitle, palette["text"], scale=2)
    game.screen.blit(heading, (outer.centerx - heading.get_width() // 2, outer.y + 24))
    subtitle_y = outer.y + (100 if is_chinese() else 106)
    game.screen.blit(sub, (outer.centerx - sub.get_width() // 2, subtitle_y))
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
    shade.fill((0, 0, 0, 175))
    game.screen.blit(shade, (0, 0))
    panel = pygame.Rect(WINDOW_W // 2 - 230, WINDOW_H // 2 - 90, 460, 180)
    pygame.draw.rect(game.screen, C.OUTLINE, panel, 5)
    pygame.draw.rect(game.screen, palette["panel"], panel.inflate(-10, -10))
    text = render_pixel_text(game.font_menu_title, "PAUSED", palette["accent_light"], scale=3)
    hint = render_pixel_text(game.font_small, "P TO RESUME   ESC FOR MENU", palette["text"], scale=2)
    game.screen.blit(text, (panel.centerx - text.get_width() // 2, panel.y + 38))
    game.screen.blit(hint, (panel.centerx - hint.get_width() // 2, panel.y + 108))


class ArcadeHubMixin:
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
        shade.fill((0, 0, 0, 205))
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
