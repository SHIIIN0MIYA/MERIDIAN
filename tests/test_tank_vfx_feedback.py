"""Regression tests for Tank Duel visual feedback (remediation R-08, R-09).

R-08: ``tank_destroyed`` was emitted without a position, and the respawn moves
the tank in the same step. A consumer backfilling x/y from the tank therefore
drew the death explosion at the spawn point.

R-09: the destroyed-tank burst used 0.004 px/ms, which ``update_vfx`` integrates
over milliseconds — about 2px of travel over the particle's whole 520ms life.
"""

from __future__ import annotations

import math

from _game_fixture import GameSaveTestCase

# Deliberately no import of the new speed constant: the tests assert on
# magnitudes, so they can run against the pre-fix module and fail on behaviour
# rather than on an ImportError.
from meridian.tank_engine import BulletState
from meridian.tank_vfx import TankVfxState, consume_engine_events, update_vfx


class _Event:
    """Minimal stand-in for tank_engine.EngineEvent."""

    def __init__(self, kind, player_id=None, data=None):
        self.kind = kind
        self.player_id = player_id
        self.data = data or {}


class DestructionEventPositionTests(GameSaveTestCase):
    def _destroy_a_tank(self):
        """Return (events, position at death, position after the respawn)."""
        engine = self.game.tank_engine
        victim = engine.tanks["blue"]
        victim.hp = 1
        engine.bullets = []
        engine.bullets.append(
            BulletState("red", victim.x - 0.5, victim.y, 1.0, 0.0)
        )
        death_position = (victim.x, victim.y)

        events = []
        for _ in range(60):
            events.extend(engine.update(16, {}))
        return events, death_position, (victim.x, victim.y)

    def test_the_destruction_event_carries_the_death_position(self):
        events, death_position, post_respawn = self._destroy_a_tank()
        destroyed = [e for e in events if e.kind == "tank_destroyed"]

        self.assertTrue(destroyed, "the shot should have destroyed the tank")
        event = destroyed[0]
        self.assertIn("x", event.data)
        self.assertIn("y", event.data)
        self.assertAlmostEqual(event.data["x"], death_position[0], places=3)
        self.assertAlmostEqual(event.data["y"], death_position[1], places=3)

    def test_the_position_differs_from_where_the_tank_respawns(self):
        """Guards the actual symptom: the explosion drifting to the spawn."""
        events, death_position, post_respawn = self._destroy_a_tank()
        destroyed = [e for e in events if e.kind == "tank_destroyed"][0]

        moved = (
            abs(destroyed.data["x"] - post_respawn[0]) > 0.5
            or abs(destroyed.data["y"] - post_respawn[1]) > 0.5
        )
        self.assertTrue(
            moved,
            "the tank must have respawned somewhere else, or this test proves nothing",
        )


class ParticleSpeedTests(GameSaveTestCase):
    def _burst(self, effect_level="full"):
        state = TankVfxState()
        consume_engine_events(
            state, [_Event("tank_destroyed", "red", {"x": 10.0, "y": 10.0})],
            effect_level, seed=7,
        )
        return state

    def test_the_burst_actually_moves(self):
        state = self._burst()
        self.assertTrue(state.particles)

        update_vfx(state, 200)          # a third of the 520ms life

        travels = [
            math.hypot(p["x"] - 10.0, p["y"] - 10.0) for p in state.particles
        ]
        self.assertTrue(
            all(distance > 5 for distance in travels),
            f"particles barely moved: {min(travels):.2f}px after 200ms",
        )

    def test_speeds_are_pixels_per_millisecond(self):
        state = self._burst()
        speeds = [math.hypot(p["vx"], p["vy"]) for p in state.particles]

        self.assertTrue(all(s > 0.02 for s in speeds),
                        "a per-frame speed used as px/ms is the R-09 defect")
        self.assertLess(max(speeds), 1.0, "0.5 px/ms would be ~30px per frame")

    def test_the_burst_spreads_in_all_directions(self):
        state = self._burst()
        quadrants = {
            (p["vx"] >= 0, p["vy"] >= 0) for p in state.particles
        }
        self.assertEqual(len(quadrants), 4, "the burst should be radial")

    def test_effects_still_expire(self):
        state = self._burst()
        for _ in range(10):
            update_vfx(state, 100)
        self.assertEqual(state.particles, [])
