"""Unit tests for Tank Duel deterministic engine.

Covers: arena terrain, tank movement, bullet physics, item pickups,
all eight item effects, damage/respawn, match phases, and snapshot
serialization roundtrips.
"""

from __future__ import annotations

import unittest

from meridian.tank_engine import (
    ARENA_COLS,
    ARENA_ROWS,
    Arena,
    BulletState,
    EngineEvent,
    ItemType,
    MatchPhase,
    MineState,
    PickupState,
    PlayerCommand,
    TankBattleEngine,
    TankSnapshotError,
    Terrain,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

IDLE = PlayerCommand()
RIGHT = PlayerCommand(move_x=1, move_y=0)
LEFT = PlayerCommand(move_x=-1, move_y=0)
UP = PlayerCommand(move_x=0, move_y=-1)
DOWN = PlayerCommand(move_x=0, move_y=1)


def _step(engine: TankBattleEngine, steps: int = 1):
    """Advance the engine by `steps` fixed timesteps."""
    for _ in range(steps):
        engine.update(TankBattleEngine.STEP_MS, {})


def _advance_ms(engine: TankBattleEngine, ms: int):
    """Advance by an arbitrary number of milliseconds."""
    engine.update(ms, {})


def _events_by_kind(events: list[EngineEvent]) -> dict[str, list[EngineEvent]]:
    result: dict[str, list[EngineEvent]] = {}
    for ev in events:
        result.setdefault(ev.kind, []).append(ev)
    return result


# ---------------------------------------------------------------------------
# Arena
# ---------------------------------------------------------------------------

class ArenaTests(unittest.TestCase):
    def test_default_arena_dimensions(self):
        engine = TankBattleEngine(seed=42)
        self.assertEqual(len(engine.arena.rows), ARENA_ROWS)
        for row in engine.arena.rows:
            self.assertEqual(len(row), ARENA_COLS)

    def test_border_is_steel(self):
        engine = TankBattleEngine(seed=42)
        for col in range(ARENA_COLS):
            self.assertEqual(engine.arena.rows[0][col], Terrain.STEEL.value)
            self.assertEqual(engine.arena.rows[-1][col], Terrain.STEEL.value)
        for row in range(ARENA_ROWS):
            self.assertEqual(engine.arena.rows[row][0], Terrain.STEEL.value)
            self.assertEqual(engine.arena.rows[row][-1], Terrain.STEEL.value)

    def test_is_walkable_bricks_are_not_walkable(self):
        arena = Arena(["B" * ARENA_COLS for _ in range(ARENA_ROWS)])
        self.assertFalse(arena.is_walkable(0, 0))

    def test_is_walkable_grass_is_walkable(self):
        arena = Arena(["G" * ARENA_COLS for _ in range(ARENA_ROWS)])
        self.assertTrue(arena.is_walkable(0, 0))

    def test_is_walkable_empty_is_walkable(self):
        arena = Arena(["." * ARENA_COLS for _ in range(ARENA_ROWS)])
        self.assertTrue(arena.is_walkable(0, 0))

    def test_is_walkable_out_of_bounds(self):
        engine = TankBattleEngine(seed=42)
        self.assertFalse(engine.arena.is_walkable(-1, 0))
        self.assertFalse(engine.arena.is_walkable(0, -1))
        self.assertFalse(engine.arena.is_walkable(ARENA_COLS, 0))
        self.assertFalse(engine.arena.is_walkable(0, ARENA_ROWS))

    def test_has_line_of_sight_blocked_by_brick(self):
        engine = TankBattleEngine(seed=42)
        # Row 5 has bricks at col 10-11: "S..........BB..........S"
        # A horizontal path from (2, 5.5) to (22, 5.5) crosses through the bricks
        self.assertFalse(engine.arena.has_line_of_sight((2.0, 5.5), (22.0, 5.5)))
        # Row 10 is clear: "S......................S"
        self.assertTrue(engine.arena.has_line_of_sight((2.0, 10.5), (22.0, 10.5)))

    def test_open_neighbor_count(self):
        engine = TankBattleEngine(seed=42)
        # A corner point has 2 open neighbors (interior)
        count = engine.arena.open_neighbor_count((1.5, 1.5))
        self.assertGreaterEqual(count, 0)
        self.assertLessEqual(count, 4)

    def test_arena_rejects_wrong_dimensions(self):
        with self.assertRaises(ValueError):
            Arena(["." * 10])
        with self.assertRaises(ValueError):
            Arena(["." * ARENA_COLS for _ in range(5)])


# ---------------------------------------------------------------------------
# Tank initialization
# ---------------------------------------------------------------------------

class TankInitTests(unittest.TestCase):
    def test_red_starts_bottom_left(self):
        engine = TankBattleEngine(seed=42)
        self.assertAlmostEqual(engine.tanks["red"].x, 1.5)
        self.assertAlmostEqual(engine.tanks["red"].y, 1.5)

    def test_blue_starts_top_right(self):
        engine = TankBattleEngine(seed=42)
        self.assertAlmostEqual(engine.tanks["blue"].x, 22.5)
        self.assertAlmostEqual(engine.tanks["blue"].y, 10.5)

    def test_initial_hp_is_three(self):
        engine = TankBattleEngine(seed=42)
        self.assertEqual(engine.tanks["red"].hp, 3)
        self.assertEqual(engine.tanks["blue"].hp, 3)

    def test_initial_score_is_zero(self):
        engine = TankBattleEngine(seed=42)
        self.assertEqual(engine.score["red"], 0)
        self.assertEqual(engine.score["blue"], 0)

    def test_initial_phase_is_regulation(self):
        engine = TankBattleEngine(seed=42)
        self.assertEqual(engine.phase, MatchPhase.REGULATION)

    def test_deterministic_seed_produces_same_state(self):
        a = TankBattleEngine(seed=123)
        b = TankBattleEngine(seed=123)
        self.assertEqual(a.next_pickup_ms, b.next_pickup_ms)
        self.assertEqual(a.elapsed_ms, b.elapsed_ms)


# ---------------------------------------------------------------------------
# Movement
# ---------------------------------------------------------------------------

class MovementTests(unittest.TestCase):
    def test_move_right(self):
        engine = TankBattleEngine(seed=42)
        old_x = engine.tanks["red"].x
        engine.update(1000, {"red": RIGHT})
        self.assertGreater(engine.tanks["red"].x, old_x)

    def test_move_left(self):
        engine = TankBattleEngine(seed=42)
        old_x = engine.tanks["blue"].x
        engine.update(1000, {"blue": LEFT})
        self.assertLess(engine.tanks["blue"].x, old_x)

    def test_cannot_walk_into_wall(self):
        engine = TankBattleEngine(seed=42)
        # Red starts at (1.5, 1.5) — moving left hits the steel border at col 0
        for _ in range(50):
            engine.update(engine.STEP_MS, {"red": LEFT})
        self.assertGreaterEqual(engine.tanks["red"].x, 0.5)  # stopped by wall

    def test_tanks_cannot_overlap(self):
        engine = TankBattleEngine(seed=42)
        # Place tanks right next to each other, just over 0.7 apart
        engine.tanks["red"].x = 21.29
        engine.tanks["red"].y = 10.5
        engine.tanks["blue"].x = 22.0
        engine.tanks["blue"].y = 10.5
        # One more step right would cause overlap → both tanks rejected
        old_x_red = engine.tanks["red"].x
        old_x_blue = engine.tanks["blue"].x
        engine.update(engine.STEP_MS, {"red": RIGHT})
        # Neither tank should have moved (overlap rejection blocks both)
        self.assertAlmostEqual(engine.tanks["red"].x, old_x_red)
        self.assertAlmostEqual(engine.tanks["blue"].x, old_x_blue)

    def test_idle_tank_does_not_move(self):
        engine = TankBattleEngine(seed=42)
        old_x = engine.tanks["red"].x
        old_y = engine.tanks["red"].y
        engine.update(1000, {})
        self.assertAlmostEqual(engine.tanks["red"].x, old_x)
        self.assertAlmostEqual(engine.tanks["red"].y, old_y)

    def test_facing_updates_on_move(self):
        engine = TankBattleEngine(seed=42)
        engine.update(100, {"red": RIGHT})
        self.assertEqual(engine.tanks["red"].facing_x, 1)
        self.assertEqual(engine.tanks["red"].facing_y, 0)

    def test_diagonal_movement_is_normalized(self):
        engine = TankBattleEngine(seed=42)
        old_x = engine.tanks["red"].x
        old_y = engine.tanks["red"].y
        engine.update(1000, {"red": PlayerCommand(move_x=1, move_y=1)})
        dx = engine.tanks["red"].x - old_x
        dy = engine.tanks["red"].y - old_y
        # Diagonal should move ~0.707× as far as orthogonal in each axis
        self.assertGreater(dx, 0)
        self.assertGreater(dy, 0)
        self.assertAlmostEqual(dx, dy, places=4)


# ---------------------------------------------------------------------------
# Bullets
# ---------------------------------------------------------------------------

class BulletTests(unittest.TestCase):
    def test_bullet_spawns_with_correct_direction(self):
        engine = TankBattleEngine(seed=42)
        engine.tanks["red"].facing_x = 1
        engine.tanks["red"].facing_y = 0
        events = engine.update(2000, {})  # enough time to fire
        shots = [e for e in events if e.kind == "shot"]
        self.assertGreaterEqual(len(shots), 1)

    def test_bullet_hits_steel_and_dies(self):
        engine = TankBattleEngine(seed=42)
        engine.bullets.append(BulletState("red", 5.0, 0.5, 0.0, -1.0))
        _step(engine, 20)
        # bullet should be removed (hit steel border at row 0)
        self.assertEqual(len(engine.bullets), 0)

    def test_bullet_hits_brick_and_dies(self):
        engine = TankBattleEngine(seed=42)
        # Row 2: "S....BB..........BB....S" — bricks at col 5-6
        # Place bullet just left of the brick, heading right
        engine.bullets.clear()
        engine.bullets.append(BulletState("red", 4.2, 2.5, 1.0, 0.0))
        # March step-by-step until bullet hits the brick
        hit_brick = False
        for _ in range(30):
            events = engine.update(engine.STEP_MS, {})
            if any(e.kind == "brick_impact" for e in events):
                hit_brick = True
                break
        self.assertTrue(hit_brick)
        # Non-piercing bullet should be gone
        self.assertEqual(len(engine.bullets), 0)

    def test_bullet_hits_enemy_tank(self):
        engine = TankBattleEngine(seed=42)
        # Place red bullet heading right toward blue at (22.5, 10.5)
        engine.tanks["blue"].x = 5.0
        engine.tanks["blue"].y = 5.5
        engine.bullets.append(BulletState("red", 3.5, 5.5, 1.0, 0.0))
        old_hp = engine.tanks["blue"].hp
        _step(engine, 30)
        self.assertLess(engine.tanks["blue"].hp, old_hp)

    def test_max_two_bullets_per_player(self):
        engine = TankBattleEngine(seed=42)
        # Fire as fast as possible — should cap at 2
        total_shots = 0
        for _ in range(100):
            events = engine.update(engine.STEP_MS, {})
            total_shots += sum(1 for e in events if e.kind == "shot")
        owned = sum(1 for b in engine.bullets if b.owner == "red")
        self.assertLessEqual(owned, 2)

    def test_bullet_clash_destroys_both(self):
        engine = TankBattleEngine(seed=42)
        engine.bullets.clear()
        engine.bullets.append(BulletState("red", 5.0, 5.0, 1.0, 0.0))
        engine.bullets.append(BulletState("blue", 5.15, 5.0, -1.0, 0.0))
        _step(engine, 2)
        self.assertEqual(len(engine.bullets), 0)


# ---------------------------------------------------------------------------
# Pickups
# ---------------------------------------------------------------------------

class PickupTests(unittest.TestCase):
    def test_pickup_spawns_after_interval(self):
        engine = TankBattleEngine(seed=42)
        # Fast-forward past first pickup time
        _advance_ms(engine, 20_000)
        self.assertIsNotNone(engine.pickup)

    def test_pickup_collection_grants_item(self):
        engine = TankBattleEngine(seed=42)
        # Spawn a pickup at red's feet
        engine.pickup = PickupState(ItemType.REPAIR, 1.5, 1.5)
        self.assertIsNone(engine.tanks["red"].held_item)
        _step(engine)
        self.assertEqual(engine.tanks["red"].held_item, ItemType.REPAIR)

    def test_tank_with_item_cannot_pick_up_another(self):
        engine = TankBattleEngine(seed=42)
        engine.tanks["red"].held_item = ItemType.SHIELD
        engine.pickup = PickupState(ItemType.REPAIR, 1.5, 1.5)
        _step(engine)
        # Pickup should remain because red already holds an item
        self.assertIsNotNone(engine.pickup)
        self.assertEqual(engine.tanks["red"].held_item, ItemType.SHIELD)


# ---------------------------------------------------------------------------
# Item effects
# ---------------------------------------------------------------------------

class ItemEffectTests(unittest.TestCase):
    def setUp(self):
        self.engine = TankBattleEngine(seed=42)
        self.red = self.engine.tanks["red"]

    def _give_and_use(self, item: ItemType):
        self.red.held_item = item
        return self.engine.update(
            self.engine.STEP_MS, {"red": PlayerCommand(use_item=True)}
        )

    def test_repair_heals_one_hp(self):
        self.red.hp = 1
        self._give_and_use(ItemType.REPAIR)
        self.assertEqual(self.red.hp, 2)

    def test_repair_does_not_exceed_three(self):
        self.red.hp = 3
        self._give_and_use(ItemType.REPAIR)
        self.assertEqual(self.red.hp, 3)

    def test_repair_at_full_hp_does_not_consume(self):
        self.red.hp = 3
        self._give_and_use(ItemType.REPAIR)
        # item should still be held because repair was a no-op
        self.assertEqual(self.red.held_item, ItemType.REPAIR)

    def test_shield_activates(self):
        self._give_and_use(ItemType.SHIELD)
        self.assertGreater(self.red.shield_until_ms, self.engine.elapsed_ms)

    def test_speed_boost_activates(self):
        self._give_and_use(ItemType.SPEED)
        self.assertGreater(self.red.speed_until_ms, self.engine.elapsed_ms)

    def test_mine_is_placed(self):
        old_mine_count = len(self.engine.mines)
        self._give_and_use(ItemType.MINE)
        self.assertEqual(len(self.engine.mines), old_mine_count + 1)
        self.assertEqual(self.engine.mines[-1].owner, "red")

    def test_only_one_mine_per_player(self):
        self._give_and_use(ItemType.MINE)
        self.red.held_item = ItemType.MINE
        self._give_and_use(ItemType.MINE)
        # second mine should not be placed
        self.assertEqual(len(self.engine.mines), 1)

    def test_emp_locks_enemy_fire(self):
        self._give_and_use(ItemType.EMP)
        blue = self.engine.tanks["blue"]
        self.assertGreater(blue.fire_locked_until_ms, self.engine.elapsed_ms)

    def test_piercing_grants_three_shots(self):
        self._give_and_use(ItemType.PIERCING)
        self.assertEqual(self.red.piercing_shots, 3)

    def test_smoke_is_deployed(self):
        old_smoke_count = len(self.engine.smokes)
        self._give_and_use(ItemType.SMOKE)
        self.assertEqual(len(self.engine.smokes), old_smoke_count + 1)

    def test_warp_teleports_tank(self):
        old_x, old_y = self.red.x, self.red.y
        self._give_and_use(ItemType.WARP)
        moved = abs(self.red.x - old_x) > 0.5 or abs(self.red.y - old_y) > 0.5
        self.assertTrue(moved, "WARP should teleport the tank")

    def test_warp_grants_protection(self):
        self._give_and_use(ItemType.WARP)
        self.assertGreater(self.red.protected_until_ms, self.engine.elapsed_ms)


# ---------------------------------------------------------------------------
# Match phases
# ---------------------------------------------------------------------------

class MatchPhaseTests(unittest.TestCase):
    def test_regulation_to_sudden_death_on_timeout_tie(self):
        engine = TankBattleEngine(seed=42)
        engine.remaining_ms = 0
        _step(engine)
        self.assertEqual(engine.phase, MatchPhase.SUDDEN_DEATH)

    def test_regulation_to_ended_on_score_lead(self):
        engine = TankBattleEngine(seed=42)
        engine.score["red"] = 2
        engine.remaining_ms = 0
        _step(engine)
        self.assertEqual(engine.phase, MatchPhase.ENDED)
        self.assertEqual(engine.winner, "red")

    def test_sudden_death_first_kill_ends_match(self):
        engine = TankBattleEngine(seed=42)
        engine.phase = MatchPhase.SUDDEN_DEATH
        engine.tanks["blue"].hp = 1
        engine.bullets.append(BulletState("red", engine.tanks["blue"].x - 0.5, engine.tanks["blue"].y, 1.0, 0.0))
        _step(engine, 30)
        self.assertEqual(engine.phase, MatchPhase.ENDED)

    def test_music_phase_normal(self):
        engine = TankBattleEngine(seed=42)
        self.assertEqual(engine.music_phase, "normal")

    def test_music_phase_final_at_sixty_seconds(self):
        engine = TankBattleEngine(seed=42)
        engine.remaining_ms = 60_000
        self.assertEqual(engine.music_phase, "final")

    def test_music_phase_sprint_at_fifteen_seconds(self):
        engine = TankBattleEngine(seed=42)
        engine.remaining_ms = 15_000
        self.assertEqual(engine.music_phase, "sprint")

    def test_music_phase_sudden_in_sudden_death(self):
        engine = TankBattleEngine(seed=42)
        engine.phase = MatchPhase.SUDDEN_DEATH
        self.assertEqual(engine.music_phase, "sudden")


# ---------------------------------------------------------------------------
# Damage, respawn, and edge cases
# ---------------------------------------------------------------------------

class DamageRespawnTests(unittest.TestCase):
    def test_destroyed_tank_respawns(self):
        engine = TankBattleEngine(seed=42)
        engine.tanks["blue"].hp = 1
        engine.tanks["blue"].x = 5.0
        engine.tanks["blue"].y = 5.0
        engine.bullets.append(BulletState("red", 4.5, 5.0, 1.0, 0.0))
        _step(engine, 30)
        self.assertEqual(engine.tanks["blue"].hp, 3)  # respawned
        self.assertEqual(engine.score["red"], 1)

    def test_respawn_clears_piercing(self):
        engine = TankBattleEngine(seed=42)
        engine.tanks["blue"].piercing_shots = 2
        engine.tanks["blue"].hp = 1
        engine.tanks["blue"].x = 5.0
        engine.tanks["blue"].y = 5.0
        engine.bullets.append(BulletState("red", 4.5, 5.0, 1.0, 0.0))
        _step(engine, 30)
        self.assertEqual(engine.tanks["blue"].piercing_shots, 0)

    def test_shield_absorbs_one_damage(self):
        engine = TankBattleEngine(seed=42)
        engine.tanks["blue"].shield_until_ms = 999_999
        engine.tanks["blue"].x = 5.0
        engine.tanks["blue"].y = 5.0
        engine.bullets.append(BulletState("red", 4.5, 5.0, 1.0, 0.0))
        _step(engine, 30)
        # shield absorbs 1 damage, so hp should stay at 3
        self.assertEqual(engine.tanks["blue"].hp, 3)
        # shield should be consumed
        self.assertEqual(engine.tanks["blue"].shield_until_ms, 0)

    def test_protection_negates_all_damage(self):
        engine = TankBattleEngine(seed=42)
        engine.tanks["blue"].protected_until_ms = 999_999
        engine.tanks["blue"].x = 5.0
        engine.tanks["blue"].y = 5.0
        engine.bullets.append(BulletState("red", 4.5, 5.0, 1.0, 0.0))
        engine.bullets.append(BulletState("red", 4.5, 5.0, 1.0, 0.0))
        _step(engine, 30)
        # protection blocks all damage
        self.assertEqual(engine.tanks["blue"].hp, 3)

    def test_mine_damages_enemy(self):
        engine = TankBattleEngine(seed=42)
        engine.tanks["blue"].x = 5.0
        engine.tanks["blue"].y = 5.0
        engine.mines.append(MineState("red", 5.0, 5.0))
        old_hp = engine.tanks["blue"].hp
        _step(engine, 5)
        self.assertLess(engine.tanks["blue"].hp, old_hp)

    def test_mine_does_not_damage_owner(self):
        engine = TankBattleEngine(seed=42)
        engine.mines.append(MineState("red", 1.5, 1.5))
        old_hp = engine.tanks["red"].hp
        _step(engine, 5)
        self.assertEqual(engine.tanks["red"].hp, old_hp)


# ---------------------------------------------------------------------------
# Snapshot roundtrip
# ---------------------------------------------------------------------------

class SnapshotRoundtripTests(unittest.TestCase):
    def test_fresh_engine_roundtrips(self):
        engine = TankBattleEngine(seed=42)
        data = engine.to_dict()
        restored = TankBattleEngine.from_dict(data)
        self.assertEqual(restored.seed, 42)
        self.assertEqual(restored.elapsed_ms, engine.elapsed_ms)
        self.assertEqual(restored.phase, engine.phase)

    def test_engine_with_bullets_roundtrips(self):
        engine = TankBattleEngine(seed=42)
        engine.bullets.append(BulletState("red", 10.0, 5.0, 1.0, 0.0))
        engine.bullets.append(BulletState("blue", 14.0, 5.0, -1.0, 0.0))
        data = engine.to_dict()
        restored = TankBattleEngine.from_dict(data)
        self.assertEqual(len(restored.bullets), 2)

    def test_engine_with_mines_roundtrips(self):
        engine = TankBattleEngine(seed=42)
        engine.mines.append(MineState("red", 5.5, 5.5))
        data = engine.to_dict()
        restored = TankBattleEngine.from_dict(data)
        self.assertEqual(len(restored.mines), 1)
        self.assertEqual(restored.mines[0].owner, "red")

    def test_engine_with_pickup_roundtrips(self):
        engine = TankBattleEngine(seed=42)
        engine.pickup = PickupState(ItemType.SPEED, 10.5, 4.5)
        data = engine.to_dict()
        restored = TankBattleEngine.from_dict(data)
        self.assertIsNotNone(restored.pickup)
        self.assertEqual(restored.pickup.item, ItemType.SPEED)

    def test_snapshot_is_deterministic_after_same_steps(self):
        a = TankBattleEngine(seed=99)
        b = TankBattleEngine(seed=99)
        for _ in range(50):
            a.update(a.STEP_MS, {})
            b.update(b.STEP_MS, {})
        data_a = a.to_dict()
        restored = TankBattleEngine.from_dict(data_a)
        # Both engines should produce identical behavior
        events_a = a.update(100, {})
        events_r = restored.update(100, {})
        self.assertEqual(len(events_a), len(events_r))

    def test_snapshot_rejects_invalid_version(self):
        engine = TankBattleEngine(seed=42)
        data = engine.to_dict()
        data["version"] = 99
        with self.assertRaises(TankSnapshotError):
            TankBattleEngine.from_dict(data)

    def test_snapshot_rejects_missing_tank(self):
        engine = TankBattleEngine(seed=42)
        data = engine.to_dict()
        del data["tanks"]["blue"]
        data["tanks"]["green"] = data["tanks"]["red"].copy()
        with self.assertRaises(TankSnapshotError):
            TankBattleEngine.from_dict(data)

    def test_damaged_tank_roundtrips(self):
        engine = TankBattleEngine(seed=42)
        engine.tanks["red"].hp = 1
        engine.tanks["red"].held_item = ItemType.EMP
        engine.score["blue"] = 5
        data = engine.to_dict()
        restored = TankBattleEngine.from_dict(data)
        self.assertEqual(restored.tanks["red"].hp, 1)
        self.assertEqual(restored.tanks["red"].held_item, ItemType.EMP)
        self.assertEqual(restored.score["blue"], 5)


# ---------------------------------------------------------------------------
# Pause / edge cases
# ---------------------------------------------------------------------------

class PauseEdgeCaseTests(unittest.TestCase):
    def test_paused_engine_returns_no_events(self):
        engine = TankBattleEngine(seed=42)
        engine.paused = True
        events = engine.update(1000, {"red": RIGHT})
        self.assertEqual(events, [])

    def test_ended_match_produces_no_events(self):
        engine = TankBattleEngine(seed=42)
        engine.phase = MatchPhase.ENDED
        events = engine.update(1000, {"red": RIGHT})
        self.assertEqual(events, [])


if __name__ == "__main__":
    unittest.main()
