"""Deterministic animation state for the desktop volume panel."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VolumePanelState:
    open: bool = False
    phase: str = "closed"
    elapsed_ms: float = 0.0
    drag_target: str | None = None


@dataclass(frozen=True)
class VolumePanelGeometry:
    width_ratio: float
    content_alpha: float
    row_offsets: tuple[float, float, float]
    interactive_rect: tuple[float, float, float, float] | None


@dataclass(frozen=True)
class _AnimationProfile:
    open_ms: float
    content_close_ms: float
    width_close_ms: float
    back_strength: float
    overshoot_limit: float


_PROFILES = {
    "full": _AnimationProfile(420.0, 120.0, 240.0, 1.70158, 1.08),
    "reduced": _AnimationProfile(240.0, 70.0, 170.0, 0.7, 1.04),
}


def begin_open(
    state: VolumePanelState | None = None,
    drag_target: str | None = None,
) -> VolumePanelState:
    if state is None:
        state = VolumePanelState()
    state.open = True
    state.phase = "opening"
    state.elapsed_ms = 0.0
    state.drag_target = drag_target
    return state


def begin_close(state: VolumePanelState) -> VolumePanelState:
    state.open = False
    state.phase = "closing_content"
    state.elapsed_ms = 0.0
    state.drag_target = None
    return state


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def _ease_out_back(progress: float, strength: float) -> float:
    progress = _clamp_unit(progress)
    if progress == 0.0:
        return 0.0
    if progress == 1.0:
        return 1.0
    shifted = progress - 1.0
    return 1.0 + (strength + 1.0) * shifted ** 3 + strength * shifted ** 2


def _opening_geometry(state: VolumePanelState, profile: _AnimationProfile) -> VolumePanelGeometry:
    progress = _clamp_unit(state.elapsed_ms / profile.open_ms)
    width = min(profile.overshoot_limit, max(0.0, _ease_out_back(progress, profile.back_strength)))
    alpha = _clamp_unit(progress / 0.65)
    offsets = tuple(
        (12.0 + index * 6.0)
        * (1.0 - _clamp_unit((progress - index * 0.08) / 0.5))
        for index in range(3)
    )
    return VolumePanelGeometry(width, alpha, offsets, None)


def _open_geometry() -> VolumePanelGeometry:
    return VolumePanelGeometry(1.0, 1.0, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0, 1.0))


def _closed_geometry() -> VolumePanelGeometry:
    return VolumePanelGeometry(0.0, 0.0, (0.0, 0.0, 0.0), None)


def _closing_geometry(state: VolumePanelState, profile: _AnimationProfile) -> VolumePanelGeometry:
    if state.phase == "closing_content":
        progress = _clamp_unit(state.elapsed_ms / profile.content_close_ms)
        return VolumePanelGeometry(1.0, 1.0 - progress, (0.0, 0.0, 0.0), None)
    progress = _clamp_unit(state.elapsed_ms / profile.width_close_ms)
    width = 1.0 - progress * progress
    offsets = (8.0 * progress, 12.0 * progress, 16.0 * progress)
    return VolumePanelGeometry(width, 0.0, offsets, None)


def update_volume_panel(
    state: VolumePanelState,
    dt_ms: float,
    animation_level: str,
) -> VolumePanelGeometry:
    """Advance ``state`` using only the supplied elapsed time and return its geometry."""
    if animation_level == "off":
        state.phase = "open" if state.open else "closed"
        state.elapsed_ms = 0.0
        if not state.open:
            state.drag_target = None
        return _open_geometry() if state.open else _closed_geometry()

    profile = _PROFILES.get(animation_level, _PROFILES["full"])
    remaining = max(0.0, float(dt_ms))

    if state.phase == "opening":
        state.elapsed_ms += remaining
        if state.elapsed_ms >= profile.open_ms:
            state.phase = "open"
            state.elapsed_ms = 0.0
            return _open_geometry()
        return _opening_geometry(state, profile)

    while remaining > 0.0 and state.phase in {"closing_content", "closing_width"}:
        duration = (
            profile.content_close_ms
            if state.phase == "closing_content"
            else profile.width_close_ms
        )
        available = duration - state.elapsed_ms
        consumed = min(remaining, available)
        state.elapsed_ms += consumed
        remaining -= consumed
        if state.elapsed_ms >= duration:
            state.elapsed_ms = 0.0
            if state.phase == "closing_content":
                state.phase = "closing_width"
            else:
                state.phase = "closed"

    if state.phase == "open":
        return _open_geometry()
    if state.phase == "closed":
        return _closed_geometry()
    if state.phase in {"closing_content", "closing_width"}:
        return _closing_geometry(state, profile)
    return _closed_geometry()
