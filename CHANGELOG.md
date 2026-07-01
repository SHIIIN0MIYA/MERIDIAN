# Changelog

## V3.0.0 (2026-07-02)

### 🏗 Architecture Refactor

- **Split `Game.__init__` into 9 `_init_xxx()` mixin methods**  
  `app.py` constructor reduced from ~350 lines to ~30. Each mixin now owns its own `_init_xxx()`: Transition, Boot, Desktop, Password, Gomoku, Snake, Breakout, 2048, Mines. Tetris, Air Raid, Developer, and System already had init methods.

- **Schema v4 migration** (`persistence.py`)  
  `SCHEMA_VERSION` bumped to 4. New fields for game run-state persistence, skin unlocks, and story progress are auto-populated on old saves via `_deep_merge`.

---

### 🎮 New Features

#### Achievement Wall
- 8×6 badge grid on a dedicated `ACHIEVEMENT_WALL` screen, accessible via desktop icon.
- Click a badge → smooth ease-out-back animation expands it into a detail card.
- Pixel-art close button (X) in the top-right corner of the detail panel.
- Unlocked count footer, gradient background, gold separator line, title shadow.
- Badges have hover effects (inflate, shadow, accent border).
- Unlocked badges show a small gold star on their procedural dot-art icon.

#### Game Save / Resume (All 7 Games)
- Exiting any game mid-session auto-saves the run state to disk.
- Re-entering the same game shows a `CONTINUE` button on the menu.
- `CONTINUE` restores: board, snake body, bricks, 2048 grid, mines grid, tetris grid/piece, Air Raid combat state.
- Run state is cleared when the game is completed or a new game is started.
- Air Raid already had partial `run_active` support; now extended to full combat state.

#### Air Raid Ship Skins
- 4 skins selectable from System Settings or the Air Raid → SKINS page:

| Skin | Ship Color | Engine | Shield | Unlock Requirement |
|------|-----------|--------|--------|-------------------|
| DEFAULT | Cyan | Orange | Blue | Always available |
| CRIMSON | Red | Gold-Orange | Rose | Achievement: **GUNLINE** (Cannon Lv.5) |
| AZURE | Azure Blue | White-Blue | Cyan | Achievement: **PERFECT VECTOR** (First S-Rank) |
| GOLD | Gold | White | Gold | Achievement: **WARDEN PRIME** (All 16 S-Ranks) |

- Dev panel `UNLOCK TEST CONTENT` unlocks all 4 skins instantly.
- Skin colors defined in `C` class (`common.py`); stored in `persistence.py`.

#### Air Raid Story System
- **Prologue** (6 lines) — plays on first visit to the Air Raid menu.
- **Chapter stories** (3–4 lines each, 8 chapters) — play before the first mission of each chapter during a campaign run.
- **Story Archive** — accessible from the Air Raid main menu. 9 entries (prologue + 8 chapters). Chapters unlock progressively as missions are completed.
- Full-screen story reader with A/D page navigation, Enter to close, and pixel font rendering.
- Full Chinese localization of all ~60 story lines.

#### Password Screen Delete Key
- `Backspace` / `Delete` keys remove the last entered digit.
- A red `DEL` button with a pixel-art backspace arrow sits in the bottom-right corner of the numpad.

---

### ✨ Visual Enhancements

#### Achievement Wall Polish
- Gradient background (blue → purple) replaces flat fill.
- Three-layer panel depth (OUTLINE + DESK_ACCENT + GOLD_DARK).
- Title gains a shadow offset for visual weight.
- Gold separator line divides title area from the badge grid.
- Badge progress bars gain a GOLD_LIGHT highlight strip.
- Footer text is containerized in a small status bar.

#### Achievement Detail Card Polish
- `draw_decorative_border()` (Cuphead-style corner squares) replaces the plain rectangle.
- Three nested border layers: OUTLINE → DESK_ACCENT → GOLD_DARK.
- Game-category label (e.g., `SNAKE`, `AIR RAID`) shown in the game's theme color.
- Pixel-art X close button (3×3 block pattern) replaces simple line-drawn X.
- Bottom hint bar container for the close instruction text.

#### Desktop Particle Atmosphere
- **Mouse trail** — cyan particles spawn while the mouse moves, with slight gravity and short lifespan.
- **Icon hover sparks** — gold particles emit from hovered desktop icons.
- **Hourly clock animation** — when the clock hits `:00`, 30 gold/cyan particles burst out in a ring pattern from the clock position.
- All particles managed in a unified `self.desktop_particles` list.

#### Game-Specific Exit Transitions
- Returning to the desktop from any game now plays that game's **entry transition in reverse** instead of a plain fade.
- Gomoku → grid tiles; Snake → scan lines; Breakout → falling bricks; 2048 → number tiles; Mines → radar; Tetris → dropping blocks; Air Raid → bullet curtain.
- Implemented by storing `_desktop_return_effect` when entering a game; zero changes to the 24 `_go_desktop()` call sites.

#### Air Raid Transition Redesign
- Old: a single cyan polygon sweeping top-to-bottom.
- New: three-layer effect — dark starfield overlay, bullet-dot curtain streaming horizontally, and expanding concentric radar rings from screen center.
- Period is tied to the transition frame count; works bidirectionally.

#### Hourly Clock Effect Redesign
- Old: 30 random-direction particles.
- New: 60 particles arranged in a perfect ring + 12 golden star sparkles with longer life + clock text pulses gold and scales up over 35 frames + 3 expanding gold rings with fading alpha.

#### Notification Queue Stacking
- Up to 3 achievement notifications display simultaneously, stacked vertically.
- Each has its own independent frame counter and slide-in/fade-out animation.
- Sound effect plays only once when multiple achievements unlock in the same frame.

---

### 🎨 Color Palette Consolidation

- 45 Air Raid colors (`AIR_PALETTE`, `AIR_WEAPON_COLORS`, `AIR_ENEMY_COLORS`, VFX, backgrounds) moved from module-level dicts to `C` class constants in `common.py`.
- Snake alternate skin colors (`lime`, `red`) moved to `C.SNAKE_LIME_*` / `C.SNAKE_RED_*`.
- Overlay alpha shades moved to `C.OVERLAY_PAUSE` / `C.OVERLAY_END`.
- Updated all references in `air_raid.py`, `snake.py`, `arcade_common.py`.

---

### 🛠 Developer Tools

- **Mouse interaction for the F10 dev panel** — mouse hover highlights items, mouse click activates them. Extracted `_dev_action_rect(index)` helper for consistent layout between draw and hit-test.
- **Fixed `TRIGGER HOUR FX`** — was placed inside `_activate_air_developer_action()` which only fires for `air_*` prefixed actions. Moved to the main `_activate_developer_action()` method.
- **`UNLOCK TEST CONTENT` now unlocks all 4 Air Raid skins** (in addition to all 16 campaign levels).

---

### 🌐 Chinese Localization

- Achievement Wall: `"ACHIEVEMENT WALL"` → `"成就墙"`, `"ESC RETURN"`, `"CLICK OUTSIDE OR ESC TO CLOSE"`.
- Skin system: skin names (`DEFAULT`, `CRIMSON`, `AZURE`, `GOLD`), unlock hints, UI labels.
- Air Raid story: all 60+ prologue and chapter story lines fully translated.
- Game menus: `"CONTINUE"` → `"继续"`, `"NEW GAME"` → `"新游戏"`.
- Story archive: `"STORY ARCHIVE"`, `"PROLOGUE"`, chapter names, navigation hints.

---

### 🔧 Engineering

- **`requirements.txt`** — created with `pygame>=2.0,<3`.
- **GitHub Actions CI** — `.github/workflows/ci.yml` runs on Windows with Python 3.10/3.11/3.12 matrix. Tests execute with headless SDL drivers.
- **`tests/conftest.py`** — centralized SDL dummy driver setup, removed duplicate `os.environ.setdefault` from 3 test files.
- **`.gitignore`** — added `.agents/`, `tests/.tmp/`, `*.exe`, `*.manifest`.

---

### 🐛 Bug Fixes

- **ESC close flash on achievement wall** — `_achievement_wall_detail_t()` was inverting `t` during closing, causing the panel to re-expand instead of shrink. Removed the incorrect inversion.
- **X button click delay on achievement wall** — `achievement_wall_detail_frame` kept incrementing while the detail was open (100+ frames). Closing animation waited for it to decrement to 0 before showing any change. Added `_start_achievement_wall_close()` to cap the frame at 24.
- **Skin page click area offset** — click detection used hardcoded `x=300` while the drawn list used `panel.x + 40` (140px offset). Unified to the same formula.
- **Story text English font** — `render_pixel_text` uses the default pygame font for non-Chinese text. Story rendering now always uses `get_chinese_font(14)` for consistent pixel-font appearance across both languages.

---

### 📊 Stats

- **Files changed**: 18 modified, 4 created
- **Tests**: 50 passing (no regressions)
- **Lines**: ~2,200 added, ~400 removed (net +1,800)
