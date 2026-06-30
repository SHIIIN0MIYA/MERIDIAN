# Restrained Meteor Background Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add restrained meteor streaks to the boot and desktop backgrounds.

**Architecture:** Implement one stateless shared renderer in `haos_game_deck/common.py`, then call it from the existing boot and desktop background draw methods. The helper uses deterministic cycles based on `anim_tick`, keeps all drawing clipped to the supplied rect, and uses the existing `C.DESK_ACCENT_LIGHT` palette.

**Tech Stack:** Python, Pygame, existing HAOS Game Deck rendering helpers.

---

### Task 1: Shared Meteor Renderer

**Files:**
- Modify: `haos_game_deck/common.py`

- [x] **Step 1: Add `draw_restrained_meteors`**

Add a helper below `render_vertical_pixel_text`. It accepts `(surf, rect, tick, max_meteors=2, alpha_scale=1.0)` and draws at most two short diagonal trails. Use `pygame.Surface(rect.size, pygame.SRCALPHA)` so alpha works and clip by drawing on the local overlay.

- [x] **Step 2: Keep motion deterministic**

Use fixed cycle durations and offsets so no persistent random state is needed. Compute progress from `(tick + offset) % cycle` and draw only during a short active window of each cycle.

### Task 2: Wire Into Backgrounds

**Files:**
- Modify: `haos_game_deck/shell_desktop.py`
- Modify: `haos_game_deck/shell_boot.py`

- [x] **Step 1: Desktop call site**

Call `draw_restrained_meteors(self.screen, rect, self.anim_tick, max_meteors=2, alpha_scale=0.75)` at the end of `_draw_desktop_wallpaper`, after star dots and before icons.

- [x] **Step 2: Boot call site**

Call `draw_restrained_meteors(self.screen, screen_rect, self.anim_tick, max_meteors=2, alpha_scale=0.9)` in `_draw_boot_screen`, after boot star dots and before boot text.

### Task 3: Verification

**Files:**
- Test: existing `tests/`

- [x] **Step 1: Compile**

Run `python -m compileall haos_game_deck` and expect success.

- [x] **Step 2: Tests**

Run `python -m pytest` and expect all tests to pass.

- [x] **Step 3: Visual launch**

Run the app, capture screenshots, and confirm the boot/desktop background still renders with no UI overlap.
