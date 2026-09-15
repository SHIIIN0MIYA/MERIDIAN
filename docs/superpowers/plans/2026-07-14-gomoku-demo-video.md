# Gomoku Demo Video Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce `pic/18.mp4`, a roughly 30-second 1280 × 720 Gomoku demonstration with the project's original BGM and synchronized sound effects.

**Architecture:** Run the real `Game` draw, update, input, animation, and audio paths on a fixed 60 FPS timeline. Pipe rendered RGB frames to FFmpeg, capture Pygame's mixed output through SDL's disk audio driver, then mux the two streams into H.264/AAC MP4. The capture controller only schedules mouse motion and click events; gameplay and feedback remain owned by MERIDIAN.

**Tech Stack:** Python 3.12, Pygame, SDL disk audio driver, FFmpeg/ffprobe 8.1.1.

## Global Constraints

- Output is `pic/18.mp4` only; no other numbered video is produced.
- Resolution is 1280 × 720, 16:9, 60 FPS.
- Video is H.264 and audio is AAC.
- Preserve MERIDIAN's Gomoku BGM, placement sound, win-line sound, and game-over sound.
- Enable MERIDIAN's built-in `zh_hans` localization for the entire capture; do not add post-production text replacements.
- Do not add narration, external music, watermark, or explanatory titles.
- Duration remains between 20 and 45 seconds and the content remains Gomoku-only.

---

### Task 1: Deterministic capture controller

**Files:**
- Create temporarily: `tools/capture_gomoku_video.py`
- Produce intermediate: `pic/.18-video-only.mp4`
- Produce intermediate: `pic/.18-audio.raw`

**Interfaces:**
- Consumes: `meridian.app.Game`, `Game._handle_game_event`, `Game.update`, `Game.draw`, and the logical 1280 × 720 `Game.screen`.
- Produces: synchronized video-only H.264 frames and SDL mixer PCM audio.

- [ ] **Step 1: Configure isolated capture runtime**

Set `SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=disk`, `SDL_DISKAUDIOFILE=pic/.18-audio.raw`, and `MERIDIAN_SAVE_PATH=pic/.18-save.json` before importing Pygame or MERIDIAN. Initialize one `Game`, set both `game.language` and the localization runtime to `zh_hans`, call `_start_new_game()`, disable transitions and screen shake, and leave the real audio manager enabled.

- [ ] **Step 2: Define the 30-second input timeline**

Use frames 0–1799. Move a visible capture cursor from outside the board toward the first target during seconds 2–5. Schedule nine legal alternating moves ending in a horizontal black five at row 7, columns 4–8. Send actual `pygame.MOUSEMOTION` and `pygame.MOUSEBUTTONDOWN` events to `_handle_game_event` so magnetic preview, placement animation, statistics, SFX, and `_on_win()` use production code.

- [ ] **Step 3: Capture real frames and mixer output**

For every frame, call `game.update()` and `game.draw()`, draw only the standard pointer marker after the game frame, and write `pygame.image.tostring(game.screen, "RGB")` to an FFmpeg stdin pipe configured for `rawvideo`, `rgb24`, `1280x720`, and `60` FPS. Pace the loop with `pygame.time.Clock().tick(60)` so SDL's audio callback produces a matching real-time PCM stream.

- [ ] **Step 4: Verify intermediates exist**

Run the capture script and require an exit code of 0. Confirm `.18-video-only.mp4` and `.18-audio.raw` both exist and are non-empty; remove the isolated save and backup files.

### Task 2: Encode and mux final MP4

**Files:**
- Create: `pic/18.mp4`
- Remove: `pic/.18-video-only.mp4`
- Remove: `pic/.18-audio.raw`

**Interfaces:**
- Consumes: Task 1 H.264 stream and SDL PCM stream.
- Produces: final H.264/AAC MP4.

- [ ] **Step 1: Detect SDL audio format**

Read SDL initialization output and confirm the captured PCM sample rate, channel count, and sample format. MERIDIAN's audio generator is 44,100 Hz stereo signed 16-bit PCM; use the actual SDL-reported format if it differs.

- [ ] **Step 2: Mux video and audio**

Use FFmpeg with the matching raw-audio input declaration, trim audio to video duration, encode audio as AAC, copy or re-encode video as H.264, and enable `+faststart`. Write the result atomically to `pic/18.mp4`.

- [ ] **Step 3: Remove intermediates**

After successful muxing, remove the raw audio, video-only MP4, temporary save, and capture helper. Leave the approved design and implementation plan documents intact.

### Task 3: Playback and requirement verification

**Files:**
- Verify: `pic/18.mp4`

**Interfaces:**
- Consumes: the final MP4.
- Produces: objective codec metadata, audio-level evidence, and visual samples.

- [ ] **Step 1: Probe technical metadata**

Run `ffprobe` and verify exactly one H.264 1280 × 720 60 FPS video stream, exactly one AAC audio stream, and a duration between 20 and 45 seconds.

- [ ] **Step 2: Verify the audio is not silent**

Run FFmpeg `volumedetect`; require a finite mean volume and max volume rather than `-inf`.

- [ ] **Step 3: Inspect representative frames**

Extract frames near 5 seconds, 14 seconds, 23 seconds, and 28 seconds. Visually confirm magnetic preview/early placement, mid-match alternating stones, five-line animation, and the final result page.

Also confirm the status panel, achievement notification, and final result page use Chinese text generated by the game localization system.

- [ ] **Step 4: Check output folder naming**

Confirm the existing `01.png`–`17.png` remain unchanged and the only new numbered asset is `18.mp4`.
