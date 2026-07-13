<p align="center">
  <img src="../../assets/banner.png" alt="MERIDIAN Banner" width="800" onerror="this.style.display='none'">
</p>

<h1 align="center">🌐 MERIDIAN · 子午线</h1>

<p align="center"><strong>Many Worlds. One Device.</strong></p>
<p align="center"><em>诸界 · 一器</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python">
  <img src="https://img.shields.io/badge/pygame-2.x-green" alt="Pygame">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
  <img src="https://img.shields.io/badge/lines-~15%2C700-orange" alt="Lines of Code">
</p>

<p align="center">
  <a href="../../README.md">中文</a> |
  <strong>English</strong> |
  <a href="README_FR.md">Français</a> |
  <a href="README_RU.md">Русский</a> |
  <a href="README_IT.md">Italiano</a> |
  <a href="README_JA.md">日本語</a> |
  <a href="README_AR.md">العربية</a>
</p>

---

## 📖 Table of Contents

- [Introduction](#-introduction)
- [Worldbuilding](#-worldbuilding)
- [Connected Worlds](#-connected-worlds)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Controls](#-controls)
- [Project Structure](#-project-structure)
- [Architecture](#-architecture)
- [Extension API](#-extension-api)
- [Building](#-building)
- [Changelog](#-changelog)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🌌 Introduction

**MERIDIAN** is a handheld device of unknown origin. Its "screen" is not an ordinary display — it is a **Resonance Lens**. Fragments from many realities are sealed within its game modules, each serving as a stable portal into an independent world.

This is not an ordinary game console. It is a **cross-dimensional observation device**.

Built with **Python + Pygame**, this project is a complete multi-game platform simulator. It combines:

- 🎮 **A growing collection of fully recreated classic arcade games**
- 📚 **A deep worldbuilding narrative system**, each game with its own lore
- 🏆 **50+ achievement system** tracking player progress across games
- 🌍 **Complete bilingual support** (Simplified Chinese / English)
- 💾 **Crash-safe persistence** with mid-game resume
- 🎵 **Procedural audio engine** generating dynamic BGM and SFX
- 🛠 **Built-in developer panel** for debugging and testing

---

## 🌠 Worldbuilding

MERIDIAN is more than a game collection — it has a complete **meta-narrative** framework:

- **Boot Sequence**: Resonance Calibration → Dimensional Scan → Anchor Stabilization → Core Connection
- **Password Authentication**: "NEXUS AUTHENTICATION" — resonance match verification
- **Desktop Environment**: Status bar displays the "MERIDIAN" device identifier
- **Prologue System**: Each game shows a 3-5 line worldbuilding prologue on first visit
- **Lore Archive**: An independent reader on the second desktop page, containing:
  - Category tabs generated from the artifact and every registered world
  - Device background stories (Origin / Nexus Core / The Bearer)
  - 1-2 deep lore entries per world
  - Hidden entries unlocked via stats or achievements
- **Flavor Text**: Each game's menu page displays atmospheric worldbuilding text
- **Full Bilingual**: All text supports both Chinese and English

---

## 🎮 Connected Worlds

| Icon | Game | World Name | Lore |
|:---:|------|------------|------|
| ⚫⚪ | **GOMOKU** | Yin-Yang Board<br>阴阳棋境 | The ancient gods Chaos and Order deduce the universe's fate with black and white stones |
| 🐍 | **SNAKE** | Code Abyss<br>噬码渊 | A spirit serpent dwelling in the depths of the digital abyss, feeding on data fragments |
| 🧱 | **BREAKOUT** | Star Fortress<br>星穹壁垒 | Energy ramparts and stellar fragments left by a lost spacefaring civilization |
| 🔢 | **2048** | Numen Sea<br>数灵海 | Sentient beings made purely of numbers, on an awakening path of fusion and evolution |
| 💣 | **MINES** | Minefield Ruins<br>雷原遗迹 | A demining engineer on the scorched earth a century after the Great War |
| 🧊 | **TETRIS** | Tower of Heaven<br>筑天塔 | Alien construction matrices descend from the sky — build a tower that touches the truth |
| ✈️ | **AIR RAID** | Warden Front<br>守望者战线 | The final battle against the autonomous war network |

---

## ✨ Features

### 🎯 Core Experience

- **Boot Animation**: Full MERIDIAN worldbuilding startup sequence with a four-stage progress bar
- **Password Lock Screen**: Numeric keypad + delete key, pixel-art authentication interface
- **Desktop Environment**: Two-page icon layout, mouse trail particle effects, hourly clock animation
- **In-Game Menus**: Unified arcade-style UI with Continue / New Game / Settings

### 🏆 Achievement Wall

- 8×6 achievement badge grid
- Click a badge to expand a detail card (ease-out-back animation)
- Pixel-art close button
- Unlock progress stats, gradient background, gold separator line
- Gold star markers on unlocked badges
- Up to 3 achievement notifications stacked simultaneously

### 💾 Save System

| Feature | Description |
|---------|-------------|
| **Auto Save** | Run state auto-saved on game exit |
| **Resume** | "Continue" button appears when re-entering a game |
| **Crash-Safe** | Atomic write + backup mechanism prevents save corruption |
| **Version Migration** | Schema v4, auto-merges legacy save data |
| **Cross-Game Stats** | Unified tracking of play time, win rates, and best scores |

### ✈️ Air Raid Exclusives

- **Ship Skin System**: 4 unlockable skins (DEFAULT / CRIMSON / AZURE / GOLD)
- **Story System**: Prologue + 8-chapter storyline, fully localized
- **Story Archive**: 9-entry full-screen reader
- **16 Standard Missions** + Boss Rush + Challenge Mode
- **Weapon Upgrade System**: Cannon / Spread / Laser / Missile

### 🎨 Visual Effects

- Unified color palette (class `C` centrally managing 45+ Air Raid colors)
- Desktop particle system (mouse trail / icon hover sparks / hourly clock burst)
- Game-specific exit transition animations (each game plays its entry effect in reverse)
- Air Raid three-layer transition (starfield overlay + bullet curtain + concentric radar rings)
- Achievement detail card decorative borders (Cuphead-style corner squares)

### 🌍 Localization

- Runtime dynamic language switching
- Fusion Pixel Font — Simplified Chinese proportional-width variant
- `localization.py` centralized translation management with batch registration
- Coverage: UI labels, game menus, achievement descriptions, story text, Lore entries

### 🛠 Developer Tools

- **F10 Developer Panel**: Mouse hover highlight + click to activate
- Functions: unlock all levels, unlock all skins, trigger hourly FX, wipe saves, etc.
- Session-only effects, no impact on persistent data

---

## 🚀 Quick Start

### Requirements

| Dependency | Version |
|------------|---------|
| Python | **3.10+** |
| pygame | **2.0+** (<3.0) |
| OS | Windows / macOS / Linux |

### Installation & Run

```bash
# 1. Clone the repository
git clone https://github.com/CrescentXiong-1/MERIDIAN.git
cd MERIDIAN

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python MERIDIAN.py
```

> 💡 **Note**: The only dependency is `pygame`. No other third-party libraries are required.

### Sharing

Zip the entire `MERIDIAN` folder and send it. The recipient only needs Python 3.10+ and `pip install pygame`.

---

## 🕹 Controls

### General

| Key | Action |
|:---:|--------|
| `ESC` | Return to previous menu / Shutdown (desktop) |
| `Enter` | Confirm / Skip prologue |
| `Arrow Keys / WASD` | Navigate / Game controls |
| `Mouse` | Desktop icon selection, Achievement Wall interaction |

### Game-Specific

| Game | Special Keys |
|------|-------------|
| **GOMOKU** | Mouse click to place stone, `U` to undo |
| **SNAKE** | Arrow keys to control snake direction |
| **BREAKOUT** | Arrow keys / mouse to control paddle |
| **2048** | Arrow keys to merge tiles |
| **MINES** | Left click to reveal / Right click to flag |
| **TETRIS** | `↑` Rotate / `↓` Soft drop / `Space` Hard drop / `C` Hold / `P` Pause |
| **AIR RAID** | Arrow keys to move / `Z` Fire / `X` Missile / `Shift` Focus mode |

### Developer

| Key | Action |
|:---:|--------|
| `F10` | Toggle developer panel |

---

## 📁 Project Structure

```
MERIDIAN/
├── MERIDIAN.py                  # Entry point
├── MERIDIAN.spec                # PyInstaller build config
├── BUILD_EXE.bat                # Windows one-click build script
├── requirements.txt             # Python dependencies
├── reasonix.toml                # Editor configuration
│
├── meridian/                    # Core package
│   ├── __init__.py
│   ├── app.py                   # Game composition, main loop, state dispatch
│   ├── common.py                # Global constants, color class, layout params
│   ├── lore.py                  # Worldbuilding data & registration API
│   ├── audio.py                 # Procedural BGM & sound effect engine
│   ├── persistence.py           # Versioned crash-safe save management
│   ├── localization.py          # Runtime bilingual system + Chinese font
│   ├── developer.py             # Developer panel (session-only)
│   │
│   ├── shell.py                 # Shell system aggregator
│   ├── shell_boot.py            # Boot sequence
│   ├── shell_password.py        # Password lock-screen auth
│   ├── shell_desktop.py         # Desktop environment & icon system
│   ├── shell_transitions.py     # Scene transition animations
│   │
│   ├── arcade_common.py         # Shared arcade UI + prologue system
│   ├── arcade_levels.py         # Air Raid campaign data
│   │
│   ├── gomoku.py                # Gomoku (Yin-Yang Board)
│   ├── snake.py                 # Snake (Code Abyss)
│   ├── breakout.py              # Breakout (Star Fortress)
│   ├── g2048.py                 # 2048 (Numen Sea)
│   ├── mines.py                 # Minesweeper (Minefield Ruins)
│   ├── tetris.py                # Tetris (Tower of Heaven)
│   ├── air_raid.py              # Air Raid (Warden Front)
│   │
│   └── system.py                # Settings, profile, achievements, Lore reader
│
├── assets/                      # Static assets
│   └── fonts/                   # Fusion Pixel Font (SIL Open License 1.1)
│
└── tools/
    └── check_release.py         # Local release metadata checker
```

---

## 🏗 Architecture

MERIDIAN uses a **Mixin composition pattern** for its architecture:

```
Game(
    ShellMixin,         # Boot / Desktop / Password / Transitions
    GomokuMixin,        # Gomoku
    MinesMixin,         # Minesweeper
    Game2048Mixin,      # 2048
    BreakoutMixin,      # Breakout
    SnakeMixin,         # Snake
    TetrisMixin,        # Tetris
    ArcadeHubMixin,     # Shared arcade systems
    AirRaidMixin,       # Air Raid
    DeveloperMixin,     # Developer tools
    SystemMixin,        # Settings / Achievements / Lore
)
```

### Core Design Patterns

| Pattern | Application |
|---------|------------|
| **State Machine** | Triple-table dispatch: `_EVENT_DISPATCH` + `_UPDATE_DISPATCH` + `_DRAW_DISPATCH` |
| **Dynamic Registration** | `_GAME_STATE_REGISTRY` allows new games without modifying `app.py` |
| **Mixin Composition** | Each game and system module injected into `Game` via Mixins |
| **Atomic Write** | Saves write to temp file then rename, preventing corruption from partial writes |
| **Version Migration** | `SaveManager._deep_merge()` auto-fills new fields on old saves |

### State Flow

```
BOOT → SYSTEM_READY → PASSWORD → DESKTOP
                                    ├── GOMOKU_MENU → GOMOKU_PLAYING → GOMOKU_END
                                    ├── SNAKE_MENU → SNAKE_PLAYING → SNAKE_END
                                    ├── BREAKOUT_MENU → BREAKOUT_PLAYING → BREAKOUT_END
                                    ├── G2048_MENU → G2048_PLAYING → G2048_END
                                    ├── MINES_MENU → MINES_PLAYING → MINES_END
                                    ├── TETRIS_MENU → TETRIS_PLAYING → TETRIS_END
                                    ├── AIR_MENU → AIR_SELECT → AIR_PLAYING → AIR_END
                                    ├── SETTINGS → SYSTEM_SETTINGS / PROFILE
                                    ├── ACHIEVEMENT_WALL
                                    └── LORE_READER → LORE_STORY
```

---

## 🔌 Extension API

A complete registration API is provided for new games, covering everything from worldbuilding to desktop icons:

```python
from meridian.lore import register_game_world, register_device_lore
from meridian.shell_desktop import register_desktop_icon
from meridian.app import _register_game_states
from meridian.localization import register_game_translations

# 1. Register game world (lore, prologue, flavor text, deep lore)
register_game_world(
    "mygame",
    world_name_en="MY WORLD",
    world_name_zh="我的世界",
    world_summary_en="A world of wonder",
    world_summary_zh="奇妙的世界",
    prologue_en=["Line 1", "Line 2", "Line 3"],
    prologue_zh=["第一行", "第二行", "第三行"],
    menu_flavor_en="The crystals hum with ancient power...",
    menu_flavor_zh="水晶随着古老的力量嗡嗡作响…",
    lore_entries=[...],
    desktop_subtitle_en="MY WORLD",
    desktop_subtitle_zh="我的世界",
)

# 2. Register desktop icon
register_desktop_icon("MYGAME", "open_mygame", page=0, ...)

# 3. Register state dispatch (no changes to app.py needed)
_register_game_states("MYGAME_MENU", "_handle_mygame_menu", [], "_draw_mygame_menu")

# 4. Register translations
register_game_translations("mygame", {"PLAY": "开始", "SCORE": "得分"})
```

> 📝 See source docstrings for full API docs: `meridian/lore.py`, `meridian/app.py`, `meridian/shell_desktop.py`, `meridian/localization.py`

---

## 📦 Building

### Windows One-Click Build

```bash
# Run the build script (requires PyInstaller)
BUILD_EXE.bat
```

The generated `MERIDIAN.exe` will be in the `dist/` directory.

### Manual Build

```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --clean MERIDIAN.spec
```

> ⚠️ Ensure `pygame` is installed and paths in `MERIDIAN.spec` are correct before building.

---

## 📝 Changelog

See [CHANGELOG.md](../../CHANGELOG.md) for the full history.

### Latest: V3.1.0 (2026-07-02) — "MERIDIAN"

- 🌌 **Worldview System**: Meta-narrative framework, connected-world lore, prologue system, Lore archive
- 🔌 **Extension API**: 5 registration functions, zero-modification new-game integration
- 🏆 **Achievement Wall**: Introduced in V3.0.0, polished in V3.1.0
- 💾 **Game Resume**: All 7 games support mid-session save and resume
- ✈️ **Air Raid Story**: 8-chapter campaign with story archive
- 🎨 **Visual Polish**: Desktop particles, exit transition animations, unified color palette

---

## 🤝 Contributing

Contributions of any kind are welcome! Bug reports, feature suggestions, and code submissions.

### Contribution Flow

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a **Pull Request**

### Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Testing
- `chore:` Build / tooling

### Development Guidelines

- Use the extension API to register new games rather than modifying `app.py` directly
- Provide both Chinese and English versions for worldbuilding text
- Increment `SCHEMA_VERSION` and provide migration logic when changing save schema

---

## 📄 License

This project is open source under the **MIT License**.

The bundled **Fusion Pixel Font** is licensed under the [SIL Open Font License 1.1](../../assets/fonts/FusionPixelFont-LICENSE-OFL.txt).

---

## 🙏 Acknowledgments

- **[Pygame](https://www.pygame.org/)** — Game development framework
- **[Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font)** — Beautiful pixel font for Simplified Chinese rendering
- **All Contributors** — Thank you to every developer who has contributed to MERIDIAN

---

<p align="center">
  <sub>MERIDIAN · Many Worlds. One Device. · 诸界 · 一器</sub>
</p>
