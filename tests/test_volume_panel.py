import pytest

from meridian import volume_panel


def test_full_open_overshoots_then_settles():
    state = volume_panel.begin_open()

    peak = volume_panel.update_volume_panel(state, 340, "full")
    settled = volume_panel.update_volume_panel(state, 80, "full")

    assert 1.0 < peak.width_ratio <= 1.08
    assert settled.width_ratio == pytest.approx(1.0)
    assert settled.content_alpha == 1.0
    assert state.phase == "open"


def test_reduced_open_is_shorter_with_lower_overshoot():
    full = volume_panel.update_volume_panel(volume_panel.begin_open(), 340, "full")
    state = volume_panel.begin_open()

    peak = volume_panel.update_volume_panel(state, 180, "reduced")
    settled = volume_panel.update_volume_panel(state, 60, "reduced")

    assert 1.0 < peak.width_ratio < full.width_ratio
    assert settled.width_ratio == 1.0
    assert state.phase == "open"


def test_off_mode_switches_immediately():
    state = volume_panel.begin_open(drag_target="master")

    geometry = volume_panel.update_volume_panel(state, 0, "off")

    assert geometry.width_ratio == 1.0
    assert geometry.content_alpha == 1.0
    assert geometry.row_offsets == (0.0, 0.0, 0.0)
    assert geometry.interactive_rect == (0.0, 0.0, 1.0, 1.0)
    assert state.phase == "open"


def test_close_fades_content_before_collapsing_width():
    state = volume_panel.begin_open()
    volume_panel.update_volume_panel(state, 420, "full")
    volume_panel.begin_close(state)

    fading = volume_panel.update_volume_panel(state, 60, "full")

    assert fading.width_ratio == 1.0
    assert 0.0 < fading.content_alpha < 1.0
    assert fading.interactive_rect is None
    assert state.phase == "closing_content"

    collapsing = volume_panel.update_volume_panel(state, 120, "full")
    assert collapsing.content_alpha == 0.0
    assert 0.0 < collapsing.width_ratio < 1.0
    assert state.phase == "closing_width"


def test_dt_crosses_close_phases_and_can_finish_in_one_update():
    state = volume_panel.begin_open(drag_target="sfx")
    volume_panel.update_volume_panel(state, 420, "full")
    volume_panel.begin_close(state)

    closed = volume_panel.update_volume_panel(state, 1000, "full")

    assert closed.width_ratio == 0.0
    assert closed.content_alpha == 0.0
    assert closed.interactive_rect is None
    assert state.phase == "closed"
    assert state.drag_target is None


def test_exact_phase_boundaries_and_negative_dt_are_stable():
    state = volume_panel.begin_open()
    initial = volume_panel.update_volume_panel(state, -20, "full")
    boundary = volume_panel.update_volume_panel(state, 420, "full")
    unchanged = volume_panel.update_volume_panel(state, 100, "full")

    assert initial.width_ratio == 0.0
    assert boundary.width_ratio == 1.0
    assert unchanged == boundary


def test_opening_geometry_staggers_three_rows_and_disables_interaction():
    state = volume_panel.begin_open()

    geometry = volume_panel.update_volume_panel(state, 120, "full")

    assert len(geometry.row_offsets) == 3
    assert geometry.row_offsets[0] < geometry.row_offsets[1] < geometry.row_offsets[2]
    assert geometry.interactive_rect is None
    assert "pygame" not in volume_panel.__dict__
