"""Deterministic 60 fps capture driver for MERIDIAN gameplay videos 19-23."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import random
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PIC = ROOT / "pic"
W, H, FPS = 1280, 720, 60
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def configure_sdl(number: int) -> tuple[Path, Path, Path]:
    raw_audio = PIC / f".capture-{number}-audio.raw"
    video_only = PIC / f".capture-{number}-video.mp4"
    save_path = PIC / f".capture-{number}-save.json"
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "disk"
    os.environ["SDL_DISKAUDIOFILE"] = str(raw_audio)
    os.environ["SDL_DISKAUDIOAPPEND"] = "0"
    os.environ["MERIDIAN_SAVE_PATH"] = str(save_path)
    return raw_audio, video_only, save_path


def key_event(pygame, key):
    return pygame.event.Event(pygame.KEYDOWN, {"key": key, "unicode": "", "mod": 0})


def mouse_event(pygame, event_type, pos, button):
    return pygame.event.Event(event_type, {"pos": pos, "button": button})


class Timeline:
    duration = 30.0

    def __init__(self, game, pygame):
        self.game = game
        self.pygame = pygame
        self.fired: set[str] = set()
        self.cursor = None

    def once(self, name: str, t: float, now: float, action):
        if now >= t and name not in self.fired:
            self.fired.add(name)
            action()

    def before_update(self, now: float):
        raise NotImplementedError

    def after_update(self, now: float):
        pass


class SnakeTimeline(Timeline):
    duration = 32.0

    def __init__(self, game, pygame):
        super().__init__(game, pygame)
        game._start_snake_game()
        game.snake = [(12, 9), (12, 10), (12, 11)]
        game.snake_dir = game.snake_next_dir = (1, 0)
        game.snake_score = 0
        game.snake_move_timer = 0

    def before_update(self, now):
        g, p = self.game, self.pygame
        if g.state != g.SNAKE_PLAYING:
            return
        head_r, head_c = g.snake[-1]
        if now < 22.5:
            # Follow a large loop using the game's real direction handler.
            target = None
            if g.snake_next_dir == (1, 0) and head_c >= 20:
                target = p.K_DOWN
            elif g.snake_next_dir == (0, 1) and head_r >= 20:
                target = p.K_LEFT
            elif g.snake_next_dir == (-1, 0) and head_c <= 3:
                target = p.K_UP
            elif g.snake_next_dir == (0, -1) and head_r <= 3:
                target = p.K_RIGHT
            if target is not None:
                g._handle_snake_playing_event(key_event(p, target))
            # Feed consecutive cells until the score crosses both speed thresholds.
            if g.snake_score < 10:
                dc, dr = g.snake_next_dir
                candidate = (head_r + dr, head_c + dc)
                if 0 <= candidate[0] < 24 and 0 <= candidate[1] < 24:
                    g.snake_food = candidate
        self.once("turn_up", 22.5, now, lambda: g._handle_snake_playing_event(key_event(p, p.K_UP)))

        def prepare_death():
            g.snake = [(3, 12), (2, 12), (1, 12), (0, 12)]
            g.snake_dir = g.snake_next_dir = (0, -1)
            g.snake_move_timer = g._get_snake_current_interval() - 1

        self.once("wall_death", 25.0, now, prepare_death)


class BreakoutTimeline(Timeline):
    duration = 30.0

    def __init__(self, game, pygame):
        super().__init__(game, pygame)
        game.breakout_control_mode = "keyboard"
        game._start_breakout_game()
        game.breakout_bricks = game.breakout_bricks[:8]
        self.hit_index = 0

    def _aim_at_brick(self):
        g = self.game
        live = next((b for b in g.breakout_bricks if b.get("alive", True)), None)
        if live is None:
            return
        ball = g.breakout_ball
        ball["x"] = live["x"] + live["w"] / 2
        ball["y"] = live["y"] + live["h"] + ball["radius"] + 1
        ball["vx"] = 0.35
        ball["vy"] = -abs(g.breakout_ball_speed)

    def before_update(self, now):
        g = self.game
        if g.state != g.BREAKOUT_PLAYING:
            return
        # Keep the paddle under ordinary play while all collisions remain real.
        g.breakout_paddle["x"] = max(214, min(214 + 640 - g.breakout_paddle["width"],
                                                 g.breakout_ball["x"] - g.breakout_paddle["width"] / 2))

        def wall_bounce():
            b = g.breakout_ball
            b.update(x=214 + b["radius"] + 1, y=430, vx=-abs(g.breakout_ball_speed), vy=-1.0)

        def paddle_bounce():
            b, pad = g.breakout_ball, g.breakout_paddle
            b.update(x=pad["x"] + pad["width"] * 0.7,
                     y=pad["y"] - b["radius"] - 1, vx=1.0, vy=abs(g.breakout_ball_speed))

        self.once("wall", 3.0, now, wall_bounce)
        self.once("paddle", 5.2, now, paddle_bounce)
        for index, at in enumerate((7.5, 9.7, 11.9, 14.1, 16.3, 18.5, 20.7, 23.0)):
            self.once(f"brick-{index}", at, now, self._aim_at_brick)


class Game2048Timeline(Timeline):
    duration = 28.0

    def __init__(self, game, pygame):
        super().__init__(game, pygame)
        random.seed(2048)
        game._start_2048_game()
        game.g2048_grid = [
            [2, 2, 4, 4],
            [8, 0, 8, 0],
            [16, 16, 32, 0],
            [0, 64, 0, 64],
        ]
        game.g2048_score = 0
        game.g2048_moves = 0
        game.g2048_spawn_anims.clear()

    def before_update(self, now):
        g, p = self.game, self.pygame
        if g.state != g.G2048_PLAYING:
            return
        for name, at, key in (
            ("left", 3.2, p.K_LEFT), ("down", 6.2, p.K_DOWN),
            ("right", 9.2, p.K_RIGHT), ("up", 12.2, p.K_UP),
        ):
            self.once(name, at, now, lambda key=key: g._handle_2048_playing_event(key_event(p, key)))

        def prepare_win():
            g.g2048_grid = [
                [1024, 1024, 0, 0],
                [128, 64, 32, 16],
                [8, 4, 2, 0],
                [0, 0, 0, 0],
            ]
            g.g2048_score = max(g.g2048_score, 14800)
            g.g2048_spawn_anims.clear()
            g.g2048_merge_anims.clear()
            g.g2048_slide_anims.clear()

        self.once("prepare-win", 16.5, now, prepare_win)
        self.once("win", 19.0, now,
                  lambda: g._handle_2048_playing_event(key_event(p, p.K_LEFT)))


class MinesTimeline(Timeline):
    duration = 32.0

    def __init__(self, game, pygame):
        super().__init__(game, pygame)
        random.seed(2209)
        game.mines_size = 9
        game.mines_count = 10
        game._start_mines_game(track=False)
        self.mines = []
        self.safe = []

    def click_cell(self, r, c, button=1):
        p, g = self.pygame, self.game
        pos = g._get_mines_cell_rect(r, c).center
        self.cursor = pos
        g._handle_mines_playing_event(mouse_event(p, p.MOUSEBUTTONDOWN, pos, button))
        if button == 1:
            g._handle_mines_playing_event(mouse_event(p, p.MOUSEBUTTONUP, pos, button))

    def before_update(self, now):
        g, p = self.game, self.pygame
        if g.state != g.MINES_PLAYING:
            return

        def first_reveal():
            self.click_cell(4, 4)
            self.mines = [(r, c) for r in range(9) for c in range(9) if g.mines_grid[r][c] == -1]
            self.safe = [(r, c) for r in range(9) for c in range(9)
                         if g.mines_grid[r][c] != -1 and not g.mines_revealed[r][c]]

        self.once("first", 3.0, now, first_reveal)
        for index, at in enumerate((6.0, 8.2, 10.4)):
            self.once(f"flag-{index}", at, now,
                      lambda index=index: self.click_cell(*self.mines[index], button=3))

        def hint():
            pos = g._get_mines_hint_button()["rect"].center
            self.cursor = pos
            g._handle_mines_playing_event(mouse_event(p, p.MOUSEBUTTONDOWN, pos, 1))
            g._handle_mines_playing_event(mouse_event(p, p.MOUSEBUTTONUP, pos, 1))

        self.once("hint", 12.5, now, hint)
        for index, at in enumerate((15.0, 17.0, 19.0, 21.0, 23.0)):
            def reveal(index=index):
                remaining = [(r, c) for r, c in self.safe
                             if not g.mines_revealed[r][c] and not g.mines_flags[r][c]]
                if remaining:
                    self.click_cell(*remaining[min(index, len(remaining) - 1)])
            self.once(f"safe-{index}", at, now, reveal)

        def finish():
            for r in range(9):
                for c in range(9):
                    if g.state != g.MINES_PLAYING:
                        return
                    if g.mines_grid[r][c] != -1 and not g.mines_revealed[r][c]:
                        g._reveal_mines_cell(r, c)

        self.once("finish", 25.5, now, finish)


class TetrisTimeline(Timeline):
    duration = 32.0

    def __init__(self, game, pygame):
        super().__init__(game, pygame)
        random.seed(2310)
        game._start_tetris_game()
        game.tetris_grid = [[None for _ in range(10)] for _ in range(22)]
        for col in range(10):
            if col not in (3, 4, 5, 6):
                game.tetris_grid[21][col] = "J"
        game.tetris_current = game._new_tetris_piece("T")
        game.tetris_next = "I"
        game.tetris_hold = None
        game.tetris_can_hold = True

    def before_update(self, now):
        g, p = self.game, self.pygame
        if g.state != g.TETRIS_PLAYING:
            return
        for name, at, key in (
            ("rotate-t", 3.0, p.K_UP), ("move-t", 5.0, p.K_RIGHT),
            ("hold-t", 7.0, p.K_c), ("drop-i", 10.0, p.K_SPACE),
            ("swap-hold", 14.0, p.K_c), ("rotate-held", 16.0, p.K_z),
            ("move-held", 18.0, p.K_LEFT), ("drop-held", 20.0, p.K_SPACE),
        ):
            self.once(name, at, now,
                      lambda key=key: g._handle_tetris_playing_event(key_event(p, key)))

        def prepare_tetris():
            g.tetris_grid = [[None for _ in range(10)] for _ in range(22)]
            for row in range(18, 22):
                for col in range(10):
                    if col != 5:
                        g.tetris_grid[row][col] = "Z"
            g.tetris_current = {"kind": "I", "x": 3, "y": 0, "rotation": 1}
            g.tetris_next = "O"
            g.tetris_can_hold = True
            g.tetris_fall_tick = 0
            g.tetris_lock_tick = 0

        self.once("prepare-tetris", 23.0, now, prepare_tetris)
        self.once("tetris", 25.0, now,
                  lambda: g._handle_tetris_playing_event(key_event(p, p.K_SPACE)))


TIMELINES = {
    19: SnakeTimeline,
    20: BreakoutTimeline,
    21: Game2048Timeline,
    22: MinesTimeline,
    23: TetrisTimeline,
}


def write_all(pipe, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = pipe.write(view)
        if written is None:
            raise BrokenPipeError("ffmpeg stdin closed")
        view = view[written:]


def draw_cursor(pygame, surface, pos) -> None:
    if pos is None:
        return
    x, y = pos
    pygame.draw.circle(surface, (255, 255, 255), (x, y), 10, 2)
    pygame.draw.circle(surface, (25, 25, 35), (x, y), 4)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("number", type=int, choices=sorted(TIMELINES))
    args = parser.parse_args()
    PIC.mkdir(exist_ok=True)
    raw_audio, video_only, _ = configure_sdl(args.number)

    import pygame
    from meridian.app import Game
    from meridian.localization import set_language

    pygame.init()
    random.seed(args.number * 1009)
    game = Game()
    game.language = "zh_hans"
    set_language("zh_hans")
    game.animation_level = "full"
    game.screen_shake_enabled = True
    game.achievement_notifications.clear()
    game.transition_active = False
    pygame.mixer.stop()
    game.audio.current_track = None
    game.audio.previous_music_index = None

    timeline = TIMELINES[args.number](game, pygame)
    ffmpeg = subprocess.Popen([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
        "-f", "rawvideo", "-pixel_format", "rgb24",
        "-video_size", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video_only),
    ], stdin=subprocess.PIPE)
    assert ffmpeg.stdin is not None

    frames = round(timeline.duration * FPS)
    clock = pygame.time.Clock()
    try:
        for frame in range(frames):
            now = frame / FPS
            timeline.before_update(now)
            game.update()
            timeline.after_update(now)
            game.draw()
            draw_cursor(pygame, game.screen, timeline.cursor)
            write_all(ffmpeg.stdin, pygame.image.tobytes(game.screen, "RGB"))
            clock.tick_busy_loop(FPS)
    finally:
        ffmpeg.stdin.close()
        return_code = ffmpeg.wait()
        game.audio.stop()
        pygame.quit()
    if return_code:
        raise SystemExit(return_code)
    print(f"captured {args.number}: {frames} frames, {timeline.duration:.1f}s")
    print(f"audio={raw_audio}")
    print(f"video={video_only}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
