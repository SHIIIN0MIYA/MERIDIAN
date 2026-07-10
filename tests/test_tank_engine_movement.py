import math
from collections import deque

import pytest

from meridian.tank_engine import (
    ARENA_COLS,
    ARENA_ROWS,
    TankBattleEngine,
    PlayerCommand,
)


def test_arena_is_horizontally_symmetric_and_spawns_are_open():
    engine = TankBattleEngine(seed=7)

    assert len(engine.arena.rows) == ARENA_ROWS == 12
    assert all(len(row) == ARENA_COLS == 24 for row in engine.arena.rows)
    assert engine.arena.rows == [row[::-1] for row in engine.arena.rows]
    assert all(engine.arena.is_walkable(x, y) for x, y in engine.spawn_candidates)


def test_all_walkable_arena_tiles_are_connected():
    engine = TankBattleEngine(seed=7)
    walkable = {
        (x, y)
        for y in range(ARENA_ROWS)
        for x in range(ARENA_COLS)
        if engine.arena.is_walkable(x, y)
    }
    reached = {next(iter(walkable))}
    frontier = deque(reached)

    while frontier:
        x, y = frontier.popleft()
        for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if neighbor in walkable and neighbor not in reached:
                reached.add(neighbor)
                frontier.append(neighbor)

    assert reached == walkable


def test_diagonal_movement_is_normalized():
    straight = TankBattleEngine(seed=7)
    diagonal = TankBattleEngine(seed=7)
    sx, sy = straight.tanks["red"].position
    dx, dy = diagonal.tanks["red"].position

    straight.update(160, {"red": PlayerCommand(1, 0), "blue": PlayerCommand()})
    diagonal.update(160, {"red": PlayerCommand(1, 1), "blue": PlayerCommand()})

    assert math.dist((sx, sy), straight.tanks["red"].position) == pytest.approx(
        math.dist((dx, dy), diagonal.tanks["red"].position), rel=1e-3
    )


def test_fixed_step_accumulates_partial_frames():
    engine = TankBattleEngine(seed=7)
    start = engine.tanks["red"].position

    engine.update(15, {"red": PlayerCommand(1, 0)})
    assert engine.tanks["red"].position == start

    engine.update(1, {"red": PlayerCommand(1, 0)})
    assert engine.tanks["red"].x == pytest.approx(start[0] + 0.064)


def test_brick_wall_blocks_tank_aabb():
    engine = TankBattleEngine(seed=7)
    engine.tanks["red"].x = 4.5
    engine.tanks["red"].y = 2.5

    engine.update(160, {"red": PlayerCommand(1, 0)})

    assert engine.tanks["red"].x <= 4.65


def test_head_on_movement_is_resolved_symmetrically():
    engine = TankBattleEngine(seed=7)
    engine.tanks["red"].x, engine.tanks["red"].y = 10.0, 1.5
    engine.tanks["blue"].x, engine.tanks["blue"].y = 11.5, 1.5

    engine.update(
        160,
        {"red": PlayerCommand(1, 0), "blue": PlayerCommand(-1, 0)},
    )

    red_distance = engine.tanks["red"].x - 10.0
    blue_distance = 11.5 - engine.tanks["blue"].x
    assert red_distance == pytest.approx(blue_distance)
    assert engine.tanks["blue"].x - engine.tanks["red"].x >= 0.7
