# Gameplay Videos 19–23 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce Chinese gameplay demonstrations `pic/19.mp4` through `pic/23.mp4` with real MERIDIAN rendering, gameplay logic, BGM, and sound effects.

**Architecture:** A temporary command-line capture driver accepts one video number, configures an isolated SDL disk-audio target before importing Pygame, initializes the corresponding real game state, and advances a 60 FPS scripted input timeline. Raw frames stream to FFmpeg while Pygame writes its real mixer output to PCM; a PowerShell batch then muxes each pair and verifies the final MP4 independently.

**Tech Stack:** Python 3.12, Pygame, SDL disk audio driver, FFmpeg/ffprobe 8.1.1.

## Global Constraints

- Create only `19.mp4`, `20.mp4`, `21.mp4`, `22.mp4`, and `23.mp4` in this batch.
- Every file is 1280 × 720, 16:9, 60 FPS, H.264 video plus non-silent AAC audio.
- Every file is 20–45 seconds long and uses project language `zh_hans`.
- No narration, external music, watermark, or post-production explanatory text.
- Prepared board states are allowed; movement, collision, scoring, animation, audio, and result transitions use production game methods.

---

### Task 1: Shared capture driver

**Files:**
- Create temporarily: `tools/capture_gameplay_batch.py`
- Produce intermediates: `pic/.capture-<number>-video.mp4`, `pic/.capture-<number>-audio.raw`

**Interfaces:**
- Consumes: video number `19`–`23`, `meridian.app.Game`, each game event/update/draw method.
- Produces: one H.264 video-only stream and one 44.1 kHz stereo signed-16 PCM stream.

- [ ] Configure `SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=disk`, `SDL_DISKAUDIOFILE`, and an isolated `MERIDIAN_SAVE_PATH` before importing MERIDIAN.
- [ ] Initialize `Game`, set both the instance and localization runtime to `zh_hans`, disable transitions and screen shake, stop the launch chime, and allow the selected state to start its real BGM.
- [ ] Stream complete RGB24 frames to FFmpeg at 1280 × 720 and 60 FPS with a write-all loop that handles partial pipe writes.
- [ ] Pace capture in real time so SDL mixer output remains synchronized with the visual timeline.

### Task 2: 19.mp4 Snake scenario

**Files:**
- Produce: `pic/19.mp4`

**Interfaces:**
- Consumes: `_start_snake_game`, `_handle_snake_playing_event`, `_update_snake`, and `_end_snake_game` through normal update dispatch.
- Produces: a 32-second Snake demonstration.

- [ ] Start a legal short snake moving right and place food one cell ahead before selected movement ticks so `_update_snake` performs real eating, scoring, particles, and SFX.
- [ ] Cross score 5 so `_get_snake_current_interval()` demonstrates real score-based acceleration.
- [ ] Schedule legal direction-key events to form visible turns, then direct the snake into a wall and hold on the Chinese result screen.

### Task 3: 20.mp4 Breakout scenario

**Files:**
- Produce: `pic/20.mp4`

**Interfaces:**
- Consumes: `_start_breakout_game`, `_update_breakout`, collision helpers, and level-clear logic.
- Produces: a 30-second Breakout demonstration.

- [ ] Use mouse control and a prepared reduced brick layout while keeping real brick objects, ball physics, paddle collision, scoring, particles, and SFX.
- [ ] Script paddle position and safe ball trajectories so wall, paddle, and several brick collisions are visible.
- [ ] Leave one final brick for the closing sequence; let the real collision clear it and show the next-level reset.

### Task 4: 21.mp4 2048 scenario

**Files:**
- Produce: `pic/21.mp4`

**Interfaces:**
- Consumes: `_start_2048_game`, `_handle_2048_playing_event`, `_move_2048`, and win handling.
- Produces: a 28-second 2048 demonstration.

- [ ] Prepare a legal board with several small merges and a final separated 1024 pair.
- [ ] Send real arrow-key events at readable intervals to trigger slide, merge, score-floater, particle, spawn, and SFX paths.
- [ ] Arrange the closing input so the real merge logic creates 2048 and enters the Chinese win page.

### Task 5: 22.mp4 Mines scenario

**Files:**
- Produce: `pic/22.mp4`

**Interfaces:**
- Consumes: `_start_mines_game`, `_generate_mines_board`, `_handle_mines_playing_event`, `_use_mines_hint`, and win detection.
- Produces: a 32-second Mines demonstration.

- [ ] Seed randomness, generate a 9 × 9 / 10-mine board around a safe first click, and send real left/right mouse events to reveal and flag cells.
- [ ] Click the real hint control after the board starts and allow its highlight/particle feedback to play.
- [ ] Reveal remaining safe cells through `_reveal_mines_cell` at a readable cadence so the normal win path and Chinese result page appear.

### Task 6: 23.mp4 Tetris scenario

**Files:**
- Produce: `pic/23.mp4`

**Interfaces:**
- Consumes: `_start_tetris_game`, `_handle_tetris_playing_event`, rotation, hold, hard-drop, lock, and clear methods.
- Produces: a 32-second Tetris demonstration.

- [ ] Prepare a legal lower stack with a clear landing channel while keeping NEXT, HOLD, and ghost presentation active.
- [ ] Send real left/right, rotate, and HOLD key events, then hard-drop multiple pieces so the queue changes visibly.
- [ ] Finish with a hard drop that completes at least one row and lets `_clear_tetris_lines` produce real scoring, flash, particles, and SFX.

### Task 7: Mux, visual QA, and cleanup

**Files:**
- Verify: `pic/19.mp4` through `pic/23.mp4`
- Remove: all `.capture-*` files and the temporary capture driver

**Interfaces:**
- Consumes: five video-only streams and five PCM streams.
- Produces: five final H.264/AAC MP4 files and verification evidence.

- [ ] Mux every stream pair with AAC 192 kbps, `-shortest`, and `+faststart`; replace numbered outputs only after a successful encode.
- [ ] Probe each file for duration, resolution, frame rate, codecs, sample rate, channel count, decode errors, black frames, and finite audio volume.
- [ ] Extract four representative frames per video and visually confirm the required action sequence and Chinese UI.
- [ ] Remove intermediates and confirm `pic` contains exactly `01.png`–`17.png` and `18.mp4`–`23.mp4`.
