from itertools import permutations

import pytest

from meridian.tank_engine import BulletState, PlayerCommand, TankBattleEngine


def commands(red=(0, 0), blue=(0, 0)):
    return {"red": PlayerCommand(*red), "blue": PlayerCommand(*blue)}


def open_arena_engine():
    engine = TankBattleEngine(seed=1)
    engine.arena.rows = [list("." * 24) for _ in range(12)]
    engine.tanks["red"].x, engine.tanks["red"].y = 4.0, 6.0
    engine.tanks["blue"].x, engine.tanks["blue"].y = 20.0, 6.0
    return engine


def test_auto_fire_uses_eight_way_facing_and_caps_two_bullets():
    engine = open_arena_engine()
    engine.update(16, commands(red=(1, 1)))
    engine.update(2000, commands())
    red_bullets = [b for b in engine.bullets if b.owner == "red"]
    assert len(red_bullets) == 2
    assert red_bullets[0].direction == pytest.approx((2 ** -0.5, 2 ** -0.5))


def test_same_step_hits_are_resolved_without_player_order_bias():
    engine = open_arena_engine()
    engine.tanks["red"].hp = engine.tanks["blue"].hp = 1
    engine.bullets = [
        BulletState("blue", 4.0, 6.0, -1.0, 0.0),
        BulletState("red", 20.0, 6.0, 1.0, 0.0),
    ]
    events = engine.update(16, commands())
    assert engine.score == {"red": 1, "blue": 1}
    assert sum(e.kind == "tank_destroyed" for e in events) == 2


def test_opposing_bullets_cancel_each_other():
    engine = open_arena_engine()
    engine.bullets = [
        BulletState("red", 10.0, 6.0, 1.0, 0.0),
        BulletState("blue", 10.3, 6.0, -1.0, 0.0),
    ]

    events = engine.update(16, commands())

    assert engine.bullets == []
    assert [event.kind for event in events] == ["bullet_clash"]


def test_same_owner_bullets_do_not_clash():
    engine = open_arena_engine()
    engine.bullets = [
        BulletState("red", 10.0, 6.0, 0.0, 0.0),
        BulletState("red", 10.0, 6.0, 0.0, 0.0),
    ]

    events = engine.update(16, commands())

    assert len(engine.bullets) == 2
    assert all(event.kind != "bullet_clash" for event in events)


def test_three_bullet_clashes_are_independent_of_list_order():
    bullet_specs = (
        ("red", 10.0),
        ("red", 10.1),
        ("blue", 10.05),
    )

    for ordering in permutations(bullet_specs):
        engine = open_arena_engine()
        engine.bullets = [
            BulletState(owner, x, 6.0, 0.0, 0.0) for owner, x in ordering
        ]

        events = engine.update(16, commands())

        assert engine.bullets == []
        assert sum(event.kind == "bullet_clash" for event in events) == 2


def test_brick_is_destroyed_by_a_bullet():
    engine = open_arena_engine()
    engine.arena.rows[6][6] = "B"
    engine.bullets = [BulletState("red", 5.95, 6.5, 1.0, 0.0)]

    events = engine.update(16, commands())

    assert engine.arena.rows[6][6] == "."
    assert engine.bullets == []
    assert any(event.kind == "brick_hit" for event in events)


def test_steel_blocks_a_bullet_without_being_destroyed():
    engine = open_arena_engine()
    engine.arena.rows[6][6] = "S"
    engine.bullets = [BulletState("red", 5.95, 6.5, 1.0, 0.0)]

    engine.update(16, commands())

    assert engine.arena.rows[6][6] == "S"
    assert engine.bullets == []


def test_grass_does_not_block_a_bullet():
    engine = open_arena_engine()
    engine.arena.rows[6][6] = "G"
    engine.bullets = [BulletState("red", 5.95, 6.5, 1.0, 0.0)]

    engine.update(16, commands())

    assert engine.arena.rows[6][6] == "G"
    assert len(engine.bullets) == 1


def test_same_step_brick_hits_do_not_depend_on_bullet_order():
    engine = open_arena_engine()
    engine.arena.rows[6][6] = "B"
    engine.bullets = [
        BulletState("red", 5.95, 6.5, 1.0, 0.0),
        BulletState("blue", 7.05, 6.5, -1.0, 0.0),
    ]

    events = engine.update(16, commands())

    assert engine.arena.rows[6][6] == "."
    assert engine.bullets == []
    assert sum(event.kind == "brick_hit" for event in events) == 2
