# Changelog

## [Unreleased]

### Added

- 新增 12 个关键页面、24 张中英文确定性视觉基准及人工截图检查清单。
- 新增跨世界完成度：成就 40%、关键目标 35%、Lore 25%，所有已登记世界等权计算。
- 新增 25%／50%／75%／100% 四篇跨世界共振档案，以及 100% 桌面共振外观。
- Tank Duel 新增八种独立像素道具图标、三级战斗特效和八种专属道具音效。

### Changed

- 桌面音量入口升级为主音量、音乐、音效三滑块展开面板，包含过冲回弹与平滑收回动画。
- 公共像素 UI 统一标题、面板、按钮、文本安全宽度和左右锚定规则。
- 所有音乐和音效统一经过主音量混音，Tank 炮弹与道具音效不再绕过总体音量。
- Tank Duel 结算统计改为红蓝独立两行卡片，避免中文长文本和蓝方信息移位。

### Fixed

- 修复中文界面字号、边界和右对齐不稳定问题，并统一继续使用内置像素中文字体。
- 修复视觉基准工具可能读取玩家真实存档的问题。

## [3.2.0] - 2026-07-13

### Added

- 新增本地双人游戏 **Tank Duel（坦克对决）**：红方使用 WASD，蓝方使用方向键；支持八向移动、相反方向同时按下时后按优先，以及自动射击。
- F（红方）和 Enter（蓝方）使用单槽道具；包含修复、护盾、加速、地雷、EMP、穿甲弹、烟雾和传送八种道具。
- 对局时长 3 分钟，双方各有 3 HP；加入随机安全重生、平局骤死，以及砖墙、钢墙和草丛构成的中心镜像地图。
- 新增 12 项 Tank Duel 成就、完整中英文文本、独立动态配乐、专属转场和对局统计。

### Changed

- 存档 Schema 升级至 v5，并支持 Tank Duel 对局中断后的状态恢复。

### Fixed

- 完成 Tank Duel 后续 UI 与音频修复，改善战斗信息显示和音效反馈。

## V3.1.0 (2026-07-02) — 「MERIDIAN」

### 🌌 Worldview System — MERIDIAN

- **Frame Narrative**: 掌机真名揭示——**MERIDIAN（子午线）**，一台连接诸多异界的神秘器物。它的屏幕是一面「共鸣透镜」，每个游戏模块是通向一个独立世界的稳定门户。
- **Connected Worlds**: 每个游戏获得独立世界观设定：
  - **GOMOKU** → 阴阳棋境：混沌与秩序两位古神的宇宙棋局
  - **SNAKE** → 噬码渊：数字深渊中以代码为食的灵蛇
  - **BREAKOUT** → 星穹壁垒：失落太空文明的能量图书馆
  - **2048** → 数灵海：纯粹数字生命体的融合进化之海
  - **MINES** → 雷原遗迹：大战争百年后焦土上的排雷工程师
  - **TETRIS** → 筑天塔：异星建筑矩阵与通天塔的建造
  - **AIR RAID** → 守望者战线：WARDEN 对自主战争网络的最终战役（已有完整故事）
- **Prologue System**: 首次进入每个游戏时展示 3-5 行世界观序章画面，按 Enter/Space/点击跳过，自动保存已读状态。
- **Menu Flavor Text**: 每个游戏菜单页在标题与按钮之间展示一行世界观风味文字（中英双语）。
- **Lore Archive**: 桌面第二页新增 **LORE** 图标，打开全屏档案阅读器。包含：
  - 根据器物与已登记世界动态生成分类标签
  - 设备背景 lore（器物起源 / 连接之核 / 持器者）
  - 每界 1-2 条深层故事，通过统计数据或成就解锁
  - 分类导航、条目列表、全屏阅读视图
- **Boot Sequence**: 开机动画注入 MERIDIAN 世界观——进度条四阶段轮换显示共鸣校准/维度扫描/锚点稳定/核心连接信息；SYSTEM READY 界面副标题改为「ALL REALMS STABLE」并添加风味文字。
- **Password Screen**: 标题改为「NEXUS AUTHENTICATION」，错误提示改为「RESONANCE MISMATCH」。
- **Desktop Polish**: 状态栏标题改为「MERIDIAN」；所有游戏图标获得英文副标题（如 GOMOKU → "TACTICAL BOARD"）。
- **Bilingual**: 全部世界观文本（序章、风味文字、lore 条目）完整中英双语，通过 `localization.py` 统一管理。

### 🔌 Extensibility API — New Game Integration

为未来新游戏加入留好接口，新游戏开发者只需调用以下函数即可完成全部集成：

| 函数 | 位置 | 用途 |
|------|------|------|
| `register_game_world(game_id, ...)` | `lore.py` | 注册新游戏世界（名称、序章、风味文字、深层 lore） |
| `register_desktop_icon(label, action, ...)` | `shell_desktop.py` | 注册桌面图标（含双语副标题） |
| `_register_game_states(state_name, ...)` | `app.py` | 动态 dispatch 表注册（无需修改 app.py） |
| `_check_and_show_prologue(game_id)` | `arcade_common.py` | 通用序章系统（ArcadeHubMixin） |
| `register_game_translations(game_id, dict)` | `localization.py` | 翻译条目批量注册 |

详见各模块的 docstring。

### 📁 File Changes

- **New**: `haos_game_deck/lore.py` — 世界观文本数据 + 注册 API（~350 lines）
- **Modified**: 17 files — `common.py`, `persistence.py`, `localization.py`, `arcade_common.py`, `app.py`, `shell_boot.py`, `shell_password.py`, `shell_desktop.py`, `system.py`, `gomoku.py`, `snake.py`, `breakout.py`, `g2048.py`, `mines.py`, `tetris.py`, `air_raid.py`, `CHANGELOG.md`
- **Lines**: ~1,200 added

---

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
