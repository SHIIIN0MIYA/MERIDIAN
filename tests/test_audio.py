from unittest.mock import patch

import pytest

from meridian.audio import AudioManager


class RecordingChannel:
    def __init__(self):
        self.volumes = []
        self.played = []

    def set_volume(self, value):
        self.volumes.append(value)

    def play(self, sound, **_kwargs):
        self.played.append(sound)

    def stop(self):
        pass


@pytest.fixture
def audio():
    manager = AudioManager.__new__(AudioManager)
    manager.enabled = True
    manager.master_volume = 1.0
    manager.music_volume = 0.55
    manager.sfx_volume = 1.0
    manager.muted = False
    manager.scene_volume_scale = 1.0
    manager.music_channels = []
    manager.effects = {}
    return manager


def test_effective_volume_multiplies_master_category_and_scene(audio):
    audio.master_volume = 0.5
    audio.music_volume = 0.8
    audio.sfx_volume = 0.6
    audio.scene_volume_scale = 0.25

    assert audio.effective_music_volume() == pytest.approx(0.1)
    assert audio.effective_sfx_volume(0.4) == pytest.approx(0.12)


def test_effective_volume_is_zero_when_muted(audio):
    audio.muted = True

    assert audio.effective_music_volume() == 0.0
    assert audio.effective_sfx_volume(0.4) == 0.0


def test_volume_setters_and_event_gain_are_clamped(audio):
    audio.set_master_volume(2.0)
    audio.set_music_volume(-1.0)
    audio.set_sfx_volume(2.0)

    assert audio.master_volume == 1.0
    assert audio.music_volume == 0.0
    assert audio.sfx_volume == 1.0
    assert audio.effective_sfx_volume(-0.5) == 0.0
    assert audio.effective_sfx_volume(1.5) == 1.0


def test_tank_event_channel_receives_effective_sfx_volume(audio):
    channel = RecordingChannel()
    sound = object()
    audio.effects = {"tank_shot": sound}
    audio.master_volume = 0.5
    audio.sfx_volume = 0.8

    with patch("meridian.audio.pygame.mixer.find_channel", return_value=channel):
        audio.play("tank_shot", 0.46)

    assert channel.volumes == [pytest.approx(0.184)]
    assert channel.played == [sound]


def test_music_channel_receives_effective_music_volume(audio):
    active = RecordingChannel()
    audio.music_channels = [active]
    audio.active_music_index = 0
    audio.previous_music_index = None
    audio.current_track = "tank_normal"
    audio.master_volume = 0.5
    audio.music_volume = 0.8
    audio.scene_volume_scale = 0.25
    audio.scene_volume_fade_duration_ms = 0
    audio.scene_volume_scale_target = 0.25
    audio.crossfade_duration_ms = 1
    audio.crossfade_started_at = -10

    audio._update_crossfade()

    assert active.volumes == [pytest.approx(0.1)]
