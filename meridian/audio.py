"""Procedural music and sound effects for the game deck."""

from __future__ import annotations

from array import array
import math
import random
from typing import Callable

import pygame


SAMPLE_RATE: int = 44100
MAX_SAMPLE: int = 32767
_SOUND_CACHE: dict[str, pygame.mixer.Sound] = {}


def _square(frequency: float, time_s: float) -> float:
    return 1.0 if math.sin(math.tau * frequency * time_s) >= 0.0 else -1.0


def _triangle(frequency: float, time_s: float) -> float:
    return 2.0 * abs(2.0 * ((time_s * frequency) % 1.0) - 1.0) - 1.0


def _noise(index: int) -> float:
    value = math.sin(index * 12.9898 + 78.233) * 43758.5453
    return (value - math.floor(value)) * 2.0 - 1.0


def _make_sound(samples: list[float]) -> pygame.mixer.Sound:
    pcm = array("h")
    for sample in samples:
        encoded = int(max(-1.0, min(1.0, sample)) * MAX_SAMPLE)
        pcm.extend((encoded, encoded))
    return pygame.mixer.Sound(buffer=pcm.tobytes())


def _cached(name: str, builder: Callable[[], pygame.mixer.Sound]) -> pygame.mixer.Sound:
    sound = _SOUND_CACHE.get(name)
    if sound is None:
        sound = builder()
        _SOUND_CACHE[name] = sound
    return sound


def _tone_sequence(notes: list[float], note_seconds: float = 0.1, volume: float = 0.25,
                  wave: str = "square", decay: float = 0.8) -> pygame.mixer.Sound:
    sample_count = int(SAMPLE_RATE * note_seconds * len(notes))
    samples = []
    oscillator = _triangle if wave == "triangle" else _square
    for index in range(sample_count):
        t = index / SAMPLE_RATE
        note_index = min(len(notes) - 1, int(t / note_seconds))
        note_t = t % note_seconds
        frequency = notes[note_index]
        envelope = max(0.0, 1.0 - note_t / note_seconds) ** decay
        samples.append(oscillator(frequency, t) * envelope * volume)
    return _make_sound(samples)


def _sweep(start: float, end: float, duration: float, volume: float = 0.3,
          noise: float = 0.0, pulse: bool = False) -> pygame.mixer.Sound:
    sample_count = int(SAMPLE_RATE * duration)
    samples = []
    phase = 0.0
    for index in range(sample_count):
        progress = index / max(1, sample_count - 1)
        frequency = start + (end - start) * progress
        phase += frequency / SAMPLE_RATE
        envelope = (1.0 - progress) ** 1.5
        tone = 1.0 if math.sin(math.tau * phase) >= 0.0 else -1.0
        if pulse:
            tone *= 0.45 + 0.55 * abs(math.sin(math.tau * 12.0 * index / SAMPLE_RATE))
        samples.append((tone * (1.0 - noise) + _noise(index) * noise) * envelope * volume)
    return _make_sound(samples)


THEME_MELODY: list[float] = [
    261.63, 329.63, 392.00, 523.25,
    392.00, 329.63, 293.66, 392.00,
    261.63, 349.23, 440.00, 523.25,
    440.00, 349.23, 293.66, 246.94,
]

TANK_TRACK_SPECS: dict[str, float] = {
    "tank_menu": 0.24,
    "tank_normal": 0.18,
    "tank_final": 0.15,
    "tank_sprint": 0.125,
    "tank_sudden": 0.105,
}

# Tank Duel deliberately owns a separate, asymmetric seven-step motif.  Keeping
# it outside THEME_MELODY prevents it from sounding like another world's remix.
TANK_DUEL_MOTIF: tuple[float, ...] = (
    92.50, 138.59, 103.83, 164.81, 116.54, 155.56, 82.41,
    123.47, 110.00, 185.00, 98.00, 146.83, 77.78, 130.81,
)


def _theme_variation(style: str) -> list[float]:
    melody = list(THEME_MELODY)
    if style.startswith("tank_"):
        melody = [note * 0.5 for note in melody]
    elif style == "gomoku":
        melody = [note * 0.75 for note in melody]
    elif style == "snake":
        melody = [
            note * (2.0 if index in (3, 7, 11, 15) else 1.0)
            for index, note in enumerate(melody)
        ]
    elif style == "breakout":
        melody = [
            note * (1.5 if index % 4 == 3 else 1.0)
            for index, note in enumerate(melody)
        ]
    elif style == "2048":
        melody = [
            note * (0.5 if index % 4 == 0 else 1.0)
            for index, note in enumerate(melody)
        ]
    elif style == "mines":
        melody = [note * 0.5 for note in melody]
    elif style == "tetris":
        melody = [
            note * (1.25 if index % 4 in (0, 3) else 0.75)
            for index, note in enumerate(melody)
        ]
    elif style == "air":
        melody = [note * (1.5 if index % 4 == 0 else 1.0) for index, note in enumerate(melody)]
    return melody


def _make_bgm(bass: list[float], beat_seconds: float, style: str) -> pygame.mixer.Sound:
    melody = _theme_variation(style)
    total_seconds = beat_seconds * len(melody)
    sample_count = int(SAMPLE_RATE * total_seconds)
    samples = []
    rng = random.Random(style)

    for index in range(sample_count):
        t = index / SAMPLE_RATE
        beat_index = min(len(melody) - 1, int(t / beat_seconds))
        beat_t = t % beat_seconds
        edge = min(1.0, beat_t / 0.01) * max(
            0.0, min(1.0, (beat_seconds - beat_t) / 0.045)
        )
        lead_frequency = melody[beat_index]
        bass_frequency = bass[(beat_index // 2) % len(bass)]

        if style == "desktop":
            lead = _square(lead_frequency, t) * 0.09
            harmony = _square(lead_frequency / 2.0, t) * 0.035
            low = _square(bass_frequency, t) * 0.05
            beat = 0.025 if beat_t < 0.026 else 0.0
        elif style == "gomoku":
            lead = _triangle(lead_frequency, t) * 0.085
            harmony = math.sin(math.tau * lead_frequency * 1.5 * t) * 0.025
            low = _triangle(bass_frequency, t) * 0.045
            beat = 0.012 if beat_t < 0.02 else 0.0
        elif style == "snake":
            wobble = 1.0 + 0.018 * math.sin(math.tau * 6.0 * t)
            lead = _square(lead_frequency * wobble, t) * 0.075
            harmony = _square(lead_frequency * 2.0, t) * 0.018
            low = _square(bass_frequency, t) * 0.06
            beat = 0.035 if beat_t < 0.018 else 0.0
        elif style == "breakout":
            lead = _square(lead_frequency, t) * 0.075
            harmony = _triangle(lead_frequency * 2.0, t) * 0.03
            low = _square(bass_frequency, t) * 0.065
            beat = (_noise(index) * 0.045) if beat_t < 0.035 else 0.0
        elif style == "2048":
            lead = _triangle(lead_frequency, t) * 0.075
            harmony = _triangle(lead_frequency * 0.5, t) * 0.035
            low = math.sin(math.tau * bass_frequency * t) * 0.05
            beat = 0.02 if beat_t < 0.018 else 0.0
        elif style == "tetris":
            wobble = 1.0 + 0.012 * math.sin(math.tau * 7.0 * t)
            lead = _square(lead_frequency * wobble, t) * 0.075
            harmony = _triangle(lead_frequency * 0.75, t) * 0.032
            low = _square(bass_frequency, t) * 0.06
            beat = (_noise(index) * 0.025) if beat_t < 0.025 else 0.0
        else:
            lead = _square(lead_frequency, t) * 0.055
            harmony = math.sin(math.tau * lead_frequency * 0.5 * t) * 0.035
            low = _triangle(bass_frequency, t) * 0.055
            beat = (_noise(index + rng.randint(0, 4)) * 0.025) if beat_t < 0.028 else 0.0

        samples.append((lead + harmony + low) * edge + beat)

    return _make_sound(samples)


def _make_tank_bgm(beat_seconds: float, phase: str) -> pygame.mixer.Sound:
    """Build Tank Duel's own tracked-vehicle march, independent of the deck theme."""
    motif = TANK_DUEL_MOTIF
    total_seconds = beat_seconds * len(motif)
    sample_count = int(SAMPLE_RATE * total_seconds)
    samples: list[float] = []
    phase_weight = {"menu": 0.72, "normal": 0.86, "final": 0.94,
                    "sprint": 1.0, "sudden": 1.08}.get(phase, 0.86)
    for index in range(sample_count):
        t = index / SAMPLE_RATE
        step = min(len(motif) - 1, int(t / beat_seconds))
        step_t = t % beat_seconds
        gate = min(1.0, step_t / 0.008) * max(
            0.0, min(1.0, (beat_seconds - step_t) / 0.035)
        )
        lead_hz = motif[step]
        bass_hz = (46.25, 41.20, 51.91, 38.89)[(step // 3) % 4]
        # Alternating track clatter and a short command-radio chirp make the
        # identity recognisably mechanical instead of melodic-theme based.
        lead = _triangle(lead_hz * (2.0 if step % 5 == 3 else 1.0), t) * 0.052
        growl = _square(bass_hz, t) * 0.052
        clatter = _noise(index + step * 97) * (0.040 if step_t < 0.018 else 0.0)
        offbeat = _noise(index + 311) * (
            0.025 if beat_seconds * 0.48 < step_t < beat_seconds * 0.55 else 0.0
        )
        chirp = 0.0
        if phase in {"final", "sprint", "sudden"} and step % 7 == 6:
            chirp = _square(740.0 + 90.0 * math.sin(t * 19.0), t) * 0.018
        samples.append(((lead + growl) * gate + clatter + offbeat + chirp) * phase_weight)
    return _make_sound(samples)


def _build_tracks() -> dict[str, pygame.mixer.Sound]:
    tracks = {
        "desktop": _cached("bgm_desktop", lambda: _make_bgm(
            [130.81, 146.83, 174.61, 123.47], 0.24, "desktop")),
        "gomoku": _cached("bgm_gomoku", lambda: _make_bgm(
            [110.00, 130.81, 146.83, 98.00], 0.32, "gomoku")),
        "snake": _cached("bgm_snake", lambda: _make_bgm(
            [164.81, 196.00, 146.83, 174.61], 0.17, "snake")),
        "breakout": _cached("bgm_breakout", lambda: _make_bgm(
            [98.00, 123.47, 110.00, 116.54], 0.145, "breakout")),
        "2048": _cached("bgm_2048", lambda: _make_bgm(
            [130.81, 146.83, 123.47, 146.83], 0.22, "2048")),
        "mines": _cached("bgm_mines", lambda: _make_bgm(
            [73.42, 65.41, 61.74, 55.00], 0.29, "mines")),
        "tetris": _cached("bgm_tetris", lambda: _make_bgm(
            [110.00, 130.81, 98.00, 146.83], 0.16, "tetris")),
        "air": _cached("bgm_air", lambda: _make_bgm(
            [82.41, 110.00, 98.00, 123.47], 0.14, "air")),
    }
    for name, beat_seconds in TANK_TRACK_SPECS.items():
        phase = name.removeprefix("tank_")
        tracks[name] = _cached(
            f"bgm_{name}_duel_v2",
            lambda beat_seconds=beat_seconds, phase=phase: _make_tank_bgm(
                beat_seconds, phase
            ),
        )
    return tracks


def _build_effects() -> dict[str, pygame.mixer.Sound]:
    power_theme = [261.63, 329.63, 392.00, 523.25, 659.25]
    effects = {
        "key": _cached("sfx_key", lambda: _sweep(880, 600, 0.065, 0.18)),
        "gomoku_place": _cached("sfx_gomoku_place", lambda: _sweep(210, 105, 0.09, 0.3, noise=0.22)),
        "gomoku_line": _cached("sfx_gomoku_line", lambda: _tone_sequence(
            [261.63, 329.63, 392.00, 523.25, 659.25], 0.105, 0.24, "triangle")),
        "snake_turn": _cached("sfx_snake_turn", lambda: _sweep(520, 760, 0.045, 0.16)),
        "snake_eat": _cached("sfx_snake_eat", lambda: _tone_sequence(
            [523.25, 659.25, 783.99], 0.055, 0.22)),
        "breakout_wall": _cached("sfx_breakout_wall", lambda: _sweep(420, 290, 0.045, 0.17)),
        "breakout_paddle": _cached("sfx_breakout_paddle", lambda: _sweep(240, 520, 0.075, 0.22)),
        "breakout_brick": _cached("sfx_breakout_brick", lambda: _sweep(640, 180, 0.07, 0.25, noise=0.18)),
        "2048_slide": _cached("sfx_2048_slide", lambda: _sweep(170, 310, 0.11, 0.18, noise=0.08)),
        "mines_pulse": _cached("sfx_mines_pulse", lambda: _sweep(95, 150, 0.48, 0.24, pulse=True)),
        "mines_explosion": _cached("sfx_mines_explosion", lambda: _sweep(115, 34, 0.72, 0.42, noise=0.68)),
        "power_on": _cached("sfx_power_on", lambda: _tone_sequence(
            power_theme, 0.13, 0.26, "triangle", 0.42)),
        "power_off": _cached("sfx_power_off", lambda: _tone_sequence(
            list(reversed(power_theme)), 0.13, 0.26, "triangle", 0.42)),
        "button_click": _cached("sfx_button_click", lambda: _sweep(550, 750, 0.06, 0.22)),
        "achievement": _cached("sfx_achievement", lambda: _tone_sequence(
            [523.25, 659.25, 783.99, 1046.50], 0.085, 0.24, "triangle", 0.45)),
        "error": _cached("sfx_error", lambda: _sweep(180, 55, 0.28, 0.35, noise=0.35)),
        "tetris_move": _cached("sfx_tetris_move", lambda: _sweep(320, 410, 0.035, 0.18)),
        "tetris_rotate": _cached("sfx_tetris_rotate", lambda: _sweep(430, 680, 0.06, 0.22)),
        "tetris_drop": _cached("sfx_tetris_drop", lambda: _sweep(210, 55, 0.11, 0.32, noise=0.16)),
        "tetris_hold": _cached("sfx_tetris_hold", lambda: _sweep(280, 560, 0.09, 0.22)),
        "tetris_clear1": _cached("sfx_tetris_clear1", lambda: _tone_sequence([523.25], 0.12, 0.22)),
        "tetris_clear2": _cached("sfx_tetris_clear2", lambda: _tone_sequence([523.25, 659.25], 0.10, 0.22)),
        "tetris_clear3": _cached("sfx_tetris_clear3", lambda: _tone_sequence([523.25, 659.25, 783.99], 0.09, 0.22)),
        "tetris_clear4": _cached("sfx_tetris_clear4", lambda: _tone_sequence([523.25, 659.25, 783.99, 1046.50], 0.08, 0.24)),
        "air_shield": _cached("sfx_air_shield", lambda: _sweep(280, 980, 0.18, 0.24)),
        "air_hit": _cached("sfx_air_hit", lambda: _sweep(180, 48, 0.3, 0.34, noise=0.45)),
        "air_clear": _cached("sfx_air_clear", lambda: _tone_sequence([392, 523.25, 659.25, 783.99], 0.11, 0.24)),
        "air_blast": _cached("sfx_air_blast", lambda: _sweep(210, 55, 0.12, 0.28, noise=0.55)),
        "air_power": _cached("sfx_air_power", lambda: _tone_sequence([440, 659.25, 880], 0.07, 0.21)),
        "air_missile": _cached("sfx_air_missile", lambda: _sweep(180, 1250, 0.32, 0.32, noise=0.12)),
        "air_empty": _cached("sfx_air_empty", lambda: _tone_sequence([180, 140], 0.055, 0.16)),
        "air_phase": _cached("sfx_air_phase", lambda: _tone_sequence([110, 220, 440, 880], 0.11, 0.28, "triangle")),
        "air_graze": _cached("sfx_air_graze", lambda: _sweep(760, 1080, 0.035, 0.12)),
        "tank_shot": _cached("sfx_tank_shot", lambda: _sweep(310, 92, 0.11, 0.34, noise=0.18)),
        "tank_clash": _cached("sfx_tank_clash", lambda: _sweep(980, 240, 0.08, 0.28, noise=0.32)),
        "tank_brick": _cached("sfx_tank_brick", lambda: _sweep(270, 72, 0.16, 0.30, noise=0.48)),
        "tank_hit": _cached("sfx_tank_hit", lambda: _sweep(190, 48, 0.24, 0.38, noise=0.52)),
        "tank_explosion": _cached("sfx_tank_explosion", lambda: _sweep(145, 28, 0.62, 0.46, noise=0.72)),
        "tank_pickup": _cached("sfx_tank_pickup", lambda: _tone_sequence([261.63, 392.0, 523.25], 0.07, 0.24, "triangle")),
        "tank_item": _cached("sfx_tank_item", lambda: _sweep(180, 740, 0.18, 0.25, pulse=True)),
        "tank_alarm": _cached("sfx_tank_alarm", lambda: _tone_sequence([110, 164.81, 110, 164.81], 0.13, 0.30)),
    }
    roots = {"gomoku": 196.00, "snake": 220.00, "breakout": 174.61, "2048": 246.94, "mines": 146.83, "tetris": 196.00, "air": 164.81}
    for game, root in roots.items():
        effects[f"gameover_{game}"] = _cached(
            f"sfx_gameover_{game}",
            lambda root=root: _tone_sequence(
                [root * 1.5, root * 1.25, root, root * 0.75], 0.18, 0.25, "triangle", 0.45
            ),
        )
    return effects


class AudioManager:
    """Switches scene music and plays shared game event effects."""

    STATE_TRACKS: dict[str, str | None] = {
        "desktop": "desktop",
        "system_ready": "desktop",
        "password": "desktop",
        "menu": "gomoku", "playing": "gomoku", "end": "gomoku", "settings": "gomoku",
        "snake_menu": "snake", "snake_playing": "snake", "snake_end": "snake", "snake_settings": "snake",
        "breakout_menu": "breakout", "breakout_playing": "breakout",
        "breakout_end": "breakout", "breakout_settings": "breakout",
        "g2048_menu": "2048", "g2048_playing": "2048", "g2048_end": "2048",
        "mines_menu": "mines", "mines_playing": "mines", "mines_end": "mines", "mines_settings": "mines",
        "tetris_menu": "tetris", "tetris_playing": "tetris", "tetris_end": "tetris",
        "air_menu": "air", "air_select": "air", "air_controls": "air",
        "air_brief": "air", "air_archive": "air", "air_supply": "air",
        "air_playing": "air", "air_end": "air",
        "tank_menu": "tank_menu", "tank_controls": "tank_menu",
        "tank_playing": "tank_normal", "tank_end": "tank_menu",
        "system_settings": "desktop", "profile": "desktop",
    }

    def __init__(self) -> None:
        self.enabled: bool = pygame.mixer.get_init() is not None
        self.music_volume: float = 0.55
        self.sfx_volume: float = 1.0
        self.muted: bool = False
        self.current_track: str | None = None
        self.tank_phase: str = "normal"
        self.scene_volume_scale: float = 1.0
        self.scene_volume_scale_start: float = 1.0
        self.scene_volume_scale_target: float = 1.0
        self.scene_volume_fade_started_at: int = 0
        self.scene_volume_fade_duration_ms: int = 0
        self.music_channels: list = []
        self.active_music_index: int = 0
        self.previous_music_index: int | None = None
        self.crossfade_started_at: int = 0
        self.crossfade_duration_ms: int = 700
        self.tracks: dict = {}
        self.effects: dict = {}
        if not self.enabled:
            return
        try:
            pygame.mixer.set_num_channels(max(16, pygame.mixer.get_num_channels()))
            self.music_channels = [pygame.mixer.Channel(0), pygame.mixer.Channel(1)]
            self.tracks = _build_tracks()
            self.effects = _build_effects()
            for channel in self.music_channels:
                channel.set_volume(0.0)
            self.play("power_on", 0.9)
        except pygame.error:
            self.enabled = False

    def sync_state(self, state: str) -> None:
        track = self.STATE_TRACKS.get(state)
        if state == "tank_playing":
            track = f"tank_{self.tank_phase}"
        self.play_music(track)
        self._update_crossfade()

    def set_tank_phase(self, phase: str) -> None:
        if phase not in {"normal", "final", "sprint", "sudden"}:
            phase = "normal"
        if phase == self.tank_phase:
            return
        self.tank_phase = phase
        if self.current_track and self.current_track.startswith("tank_") and self.current_track != "tank_menu":
            self.play_music(f"tank_{phase}")

    def set_scene_volume_scale(self, scale: float, fade_ms: int = 0) -> None:
        target = max(0.0, min(1.0, float(scale)))
        self._update_scene_volume_scale()
        self.scene_volume_scale_start = self.scene_volume_scale
        self.scene_volume_scale_target = target
        self.scene_volume_fade_started_at = pygame.time.get_ticks()
        self.scene_volume_fade_duration_ms = max(0, int(fade_ms))
        if self.scene_volume_fade_duration_ms == 0:
            self.scene_volume_scale = target
        self._update_crossfade()

    def _update_scene_volume_scale(self) -> None:
        if self.scene_volume_fade_duration_ms <= 0:
            self.scene_volume_scale = self.scene_volume_scale_target
            return
        elapsed = pygame.time.get_ticks() - self.scene_volume_fade_started_at
        progress = max(0.0, min(1.0, elapsed / self.scene_volume_fade_duration_ms))
        self.scene_volume_scale = self.scene_volume_scale_start + (
            self.scene_volume_scale_target - self.scene_volume_scale_start
        ) * progress
        if progress >= 1.0:
            self.scene_volume_fade_duration_ms = 0

    def play_music(self, track_name: str | None) -> None:
        if not self.enabled or not self.music_channels or track_name == self.current_track:
            return
        old_index = self.active_music_index if self.current_track is not None else None
        new_index = 1 - self.active_music_index
        new_channel = self.music_channels[new_index]
        new_channel.stop()

        self.current_track = track_name
        self.previous_music_index = old_index
        self.active_music_index = new_index
        self.crossfade_started_at = pygame.time.get_ticks()

        if track_name is not None and track_name in self.tracks:
            new_channel.set_volume(0.0)
            new_channel.play(self.tracks[track_name], loops=-1)
        else:
            new_channel.stop()

    def _update_crossfade(self) -> None:
        if not self.enabled or not self.music_channels:
            return
        self._update_scene_volume_scale()
        elapsed = pygame.time.get_ticks() - self.crossfade_started_at
        progress = max(0.0, min(1.0, elapsed / self.crossfade_duration_ms))
        active = self.music_channels[self.active_music_index]
        if self.current_track is not None:
            active.set_volume((0.0 if self.muted else self.music_volume * self.scene_volume_scale) * progress)
        if self.previous_music_index is not None:
            previous = self.music_channels[self.previous_music_index]
            previous.set_volume((0.0 if self.muted else self.music_volume * self.scene_volume_scale) * (1.0 - progress))
            if progress >= 1.0:
                previous.stop()
                self.previous_music_index = None

    def set_music_volume(self, value: float) -> None:
        self.music_volume = max(0.0, min(1.0, float(value)))
        self._update_crossfade()

    def set_sfx_volume(self, value: float) -> None:
        self.sfx_volume = max(0.0, min(1.0, float(value)))

    def set_muted(self, muted: bool) -> None:
        self.muted = bool(muted)
        self._update_crossfade()

    def begin_shutdown(self) -> None:
        self.play_music(None)
        self.play("power_off", 0.9)

    def play(self, effect_name: str, volume: float = 1.0) -> None:
        sound = self.effects.get(effect_name)
        if not self.enabled or sound is None:
            return
        channel = pygame.mixer.find_channel()
        if channel is not None:
            effective = 0.0 if self.muted else volume * self.sfx_volume
            channel.set_volume(max(0.0, min(1.0, effective)))
            channel.play(sound)

    def play_gameover(self, game_name: str) -> None:
        self.play(f"gameover_{game_name}", 0.9)

    def handle_input_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self.play("key", 0.5)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 2, 3):
            self.play("key", 0.45)

    def stop(self) -> None:
        for channel in self.music_channels:
            channel.stop()
