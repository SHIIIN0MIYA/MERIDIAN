# Achievement Wall Design

Date: 2026-06-30

## Goal
Add a dedicated desktop entry named `WALL` that opens a full-screen achievement wall. The wall presents all 48 existing achievements as an 8 x 6 badge grid, with no scrolling. Clicking a badge smoothly enlarges it into a detail view.

## Existing Context
The project already has an achievement system in `haos_game_deck/system.py`:

- `ACHIEVEMENTS` contains 48 achievement definitions.
- `save_data["achievements"]` stores unlocked achievement ids and timestamps.
- The existing profile page has `ACHIEVEMENTS` and `STATISTICS` tabs.
- No persistence schema change is needed for the wall because the wall can reuse the existing definitions and unlock state.

The desktop currently opens apps through `DesktopMixin._handle_desktop_event`, using desktop page items defined in `Game.__init__` in `haos_game_deck/app.py`.

## Requirements
- Add a desktop icon labeled `WALL` or `ACHIEVEMENT WALL`.
- Clicking the icon enters a new full-screen wall state.
- The wall shows all 48 achievements in an 8 x 6 grid.
- Unlocked badges use bright gold/cyan styling, show a small pixel icon, and show the achievement title.
- Locked badges use muted dark styling, show a lock mark, and may show `???` or a muted title.
- The footer shows completion progress as `UNLOCKED x / 48` and an `ESC RETURN` hint.
- Pressing `ESC` returns to the desktop.
- Clicking any badge opens a smooth enlarged detail view.
- The detail transition must feel fluid rather than abrupt: badge position/size interpolates from its grid cell into a centered detail panel, with fade-in text.
- The detail view shows title, description, progress, target, and unlock timestamp when unlocked.
- Clicking outside the detail view or pressing `ESC` closes the detail view with a reverse transition. Pressing `ESC` again returns to desktop.
- Do not rebuild `dist/HAOS_GAME_DECK.exe` unless explicitly requested.

## Proposed Architecture
Add a new app state `ACHIEVEMENT_WALL` in `haos_game_deck/app.py`, handled by methods in `SystemMixin` because the wall is achievement/profile UI and uses existing achievement data. Add one desktop item in `self.desktop_pages` and one dispatch branch in `DesktopMixin._handle_desktop_event`.

Keep the wall state local to `SystemMixin`:

- `achievement_wall_pressed_index`: index of pressed badge or `None`.
- `achievement_wall_detail_index`: selected badge index or `None`.
- `achievement_wall_detail_frame`: transition frame for open/close animation.
- `achievement_wall_detail_closing`: whether the detail panel is closing.

The grid layout is deterministic and derived from `ACHIEVEMENTS`, so tests can assert 48 cells and drawing can stay stateless aside from selection/animation.

## Visual Design
The wall is a full-screen pixel panel consistent with system/profile screens. Use a dark desktop panel background, gold outer frame, cyan accent separators, and compact badge cells.

Each badge cell is stable in size. The 8 x 6 grid fits inside the main panel below the title and above the footer. Badge visuals are deliberately compact:

- Top/center: small pixel icon generated from the achievement id/game key.
- Bottom: short title scaled to fit.
- Locked state: dark fill, muted border, lock glyph, low-contrast title or `???`.
- Unlocked state: gold border, cyan highlight, brighter title.

The detail animation uses the selected badge's source rect and a centered target rect. It interpolates x/y/w/h with ease-out cubic on open and ease-in cubic on close. The background behind the selected panel darkens with alpha during the transition. Text fades in after the panel reaches most of its size.

## Testing
- Add unit/smoke coverage for the new state draw path and event behavior.
- Assert achievement wall grid returns 48 badge buttons.
- Assert clicking a badge sets the detail index.
- Assert ESC closes an open detail first and returns to desktop when no detail is open.
- Run `python -m compileall haos_game_deck`.
- Run `python -m pytest`.
- Generate source-rendered screenshots for wall and detail state for visual inspection.

## Non-Goals
- Do not change achievement definitions or add new achievements.
- Do not change save schema.
- Do not remove the existing profile achievements list.
- Do not package or rebuild the exe unless explicitly requested.
