# HAO'S GAME DECK

**Pixel-Art Handheld Game Collection** — 掌机像素风小游戏合集

启动后先看开机动画，在 `SYSTEM READY` 页面选择 English 或简体中文，再进入桌面 UI。语言选择会自动保存，也可在统一设置中心随时切换。

---

## Included Games

| Icon | Game | Controls |
|------|------|----------|
| **GOMOKU** | 五子棋 | Mouse click to place stone · `U` Undo · `R` Restart |
| **SNAKE** | 贪吃蛇 | `WASD` / Arrow keys |
| **BREAKOUT** | 打砖块 | `A` `D` to move paddle · `R` Restart |
| **2048** | 2048 | `WASD` / Arrow keys to merge tiles |
| **MINES** | 扫雷 | Left click to open · Right click to flag · Double click to chord |
| **TETRIS** | Falling blocks | Arrow keys / `WASD` · `Space` Hard drop · `C` Hold · `P` Pause |
| **AIR RAID** | 飞机大战 | `WASD` / Arrow keys · `Shift` Focus · `Space` Missile |

---

## Requirements

- **Python 3.10+**
- **pygame 2.x**

```powershell
pip install pygame
```

## Run

```powershell
cd "D:\Codex项目文件夹"
python HAOS_GAME_DECK.py
```

Or wherever you extracted the folder:

```powershell
cd "path\to\HAOS_GAME_DECK"
python HAOS_GAME_DECK.py
```

---

## Global Controls

| Key | Action |
|-----|--------|
| `ESC` | Back to previous screen / Shutdown from Desktop |
| Arrow keys / `WASD` | Game controls |
| `Space` / `C` / `P` | Tetris hard drop / hold / pause |

---

## Sharing

Zip the entire `HAOS_GAME_DECK` folder and send it. The recipient needs:

1. Python 3.10+ installed
2. `pip install pygame`
3. Run `python HAOS_GAME_DECK.py`

No other dependencies required.

---

## Audio

- Hidden BGM volume slider on the desktop screen
- One recognizable main melody arranged into six distinct BGM variations
- Crossfaded BGM transitions between the desktop and games
- Mirrored power-on and power-off melodies with rising/falling pitch
- Game-specific action sounds for Gomoku, Snake, Breakout, 2048, and Mines
- A shared Game Over motif transposed to a different key for each game
- Shared keyboard and mouse-button UI sounds
- No external audio files or extra dependencies required
- Audio automatically disables itself if no sound device is available

## Chinese Font

简体中文界面使用随项目分发的 Fusion Pixel Font（缝合像素字体）简体中文比例宽度版本。字体采用 SIL Open Font License 1.1，授权文件位于 `assets/fonts/`。

---

## Project Structure

```text
HAOS_GAME_DECK.py          Compatibility entry point
haos_game_deck/
  app.py                   Game composition and main loop
  audio.py                 Procedural background music and input sounds
  common.py                Shared constants, helpers, Board, Particle
  shell.py                 Boot, shutdown, desktop, transitions
  gomoku.py                Gomoku UI and gameplay
  snake.py                 Snake UI and gameplay
  breakout.py              Breakout UI and gameplay
  g2048.py                 2048 UI and gameplay
  mines.py                 Minesweeper UI and gameplay
  tetris.py                Falling-block UI and gameplay
```

Each game is isolated in its own mixin module. `app.Game` composes those
modules while preserving the original runtime state, controls, and entry point.
