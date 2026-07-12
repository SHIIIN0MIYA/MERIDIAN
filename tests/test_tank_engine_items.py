from itertools import permutations
from typing import get_type_hints, Literal

import pytest

from meridian.tank_engine import (
    ARENA_COLS,
    ARENA_ROWS,
    BulletState,
    ItemType,
    MatchPhase,
    MineState,
    PickupState,
    PlayerCommand,
    TankBattleEngine,
)


def commands(red=(0, 0), blue=(0, 0), red_use=False, blue_use=False):
    return {
        "red": PlayerCommand(*red, use_item=red_use),
        "blue": PlayerCommand(*blue, use_item=blue_use),
    }


def pickup_engine(item, player="red"):
    engine = TankBattleEngine(seed=3)
    tank = engine.tanks[player]
    engine.pickup = PickupState(item, tank.x, tank.y)
    engine.update(16, commands())
    return engine


def test_there_are_exactly_four_item_types():
    assert {item.value for item in ItemType} == {
        "repair",
        "shield",
        "speed",
        "mine",
    }


@pytest.mark.parametrize("item", list(ItemType))
def test_each_item_can_be_picked_up_and_consumed(item):
    engine = pickup_engine(item, player="red")
    if item is ItemType.REPAIR:
        engine.tanks["red"].hp = 2
    assert engine.tanks["red"].held_item is item

    events = engine.update(16, commands(red_use=True))

    assert engine.tanks["red"].held_item is None
    assert any(
        e.kind == "item_used" and e.data["item"] == item.value for e in events
    )


def test_full_health_repair_is_not_consumed():
    engine = pickup_engine(ItemType.REPAIR)

    events = engine.update(16, commands(red_use=True))

    assert engine.tanks["red"].held_item is ItemType.REPAIR
    assert all(event.kind != "item_used" for event in events)


def test_pickup_does_not_replace_an_occupied_item_slot():
    engine = pickup_engine(ItemType.SHIELD)
    tank = engine.tanks["red"]
    engine.pickup = PickupState(ItemType.SPEED, tank.x, tank.y)

    engine.update(16, commands())

    assert tank.held_item is ItemType.SHIELD
    assert engine.pickup is not None


def test_shield_absorbs_exactly_one_hit_and_expires_after_15000_ms():
    engine = pickup_engine(ItemType.SHIELD)
    tank = engine.tanks["red"]
    engine.update(16, commands(red_use=True))
    engine._resolve_damage_batch([("red", 2, "blue")])
    assert tank.hp == 2
    assert tank.shield_until_ms == 0

    tank.held_item = ItemType.SHIELD
    engine.update(16, commands(red_use=True))
    engine.update(15_008, commands())
    engine._resolve_damage_batch([("red", 1, "blue")])
    assert tank.hp == 1


def test_same_frame_multi_hit_consumes_shield_once_and_emits_one_block():
    engine = TankBattleEngine(seed=3)
    red = engine.tanks["red"]
    red.shield_until_ms = 10_000
    engine.bullets = [
        BulletState("blue", red.x, red.y, 0.0, 0.0),
        BulletState("blue", red.x, red.y, 0.0, 0.0),
    ]

    events = engine.update(16, commands())

    blocks = [event for event in events if event.kind == "shield_blocked"]
    assert engine.tanks["red"].hp == 2
    assert len(blocks) == 1
    assert blocks[0].player_id == "red"
    assert blocks[0].data == {"attacker": "blue", "source": "bullet"}


def test_mine_damage_block_emits_one_block_with_mine_source():
    engine = TankBattleEngine(seed=3)
    red = engine.tanks["red"]
    red.shield_until_ms = 10_000
    engine.mines = [MineState("blue", red.x, red.y)]

    events = engine.update(16, commands())

    assert engine.tanks["red"].hp == 3
    assert any(event.kind == "mine_triggered" for event in events)
    assert [event.data for event in events if event.kind == "shield_blocked"] == [
        {"attacker": "blue", "source": "mine"}
    ]


def test_unshielded_damage_emits_no_block_event():
    engine = TankBattleEngine(seed=3)

    events = engine._resolve_damage_batch([("red", 1, "blue", "bullet")])

    assert all(event.kind != "shield_blocked" for event in events)


def test_speed_boost_is_exactly_1_25_and_lasts_6000_ms():
    normal = TankBattleEngine(seed=3)
    boosted = pickup_engine(ItemType.SPEED)
    normal.arena.rows = boosted.arena.rows = [list("." * 24) for _ in range(12)]
    boosted.update(16, commands(red_use=True))
    normal_start = normal.tanks["red"].x
    boosted_start = boosted.tanks["red"].x

    normal.update(160, commands(red=(1, 0)))
    boosted.update(160, commands(red=(1, 0)))

    normal_distance = normal.tanks["red"].x - normal_start
    boosted_distance = boosted.tanks["red"].x - boosted_start
    assert boosted_distance / normal_distance == pytest.approx(1.25)

    boosted.update(5_840, commands())
    start = boosted.tanks["red"].x
    boosted.update(16, commands(red=(1, 0)))
    assert boosted.tanks["red"].x - start == pytest.approx(
        normal_distance / 10
    )


def test_speed_boost_uses_430_ms_fire_interval_then_restores_650_ms():
    boosted = pickup_engine(ItemType.SPEED)
    normal = TankBattleEngine(seed=3)
    boosted.arena.rows = normal.arena.rows = [list("." * 24) for _ in range(12)]
    boosted.update(16, commands(red_use=True))
    boosted._fire_elapsed_ms["red"] = normal._fire_elapsed_ms["red"] = 0

    boosted_events = boosted.update(432, commands())
    normal_events = normal.update(432, commands())

    assert any(e.kind == "shot" and e.player_id == "red" for e in boosted_events)
    assert all(e.kind != "shot" or e.player_id != "red" for e in normal_events)

    boosted.update(5_568, commands())
    boosted.bullets = []
    boosted._fire_elapsed_ms["red"] = 0
    assert all(
        e.kind != "shot" or e.player_id != "red"
        for e in boosted.update(432, commands())
    )
    assert any(
        e.kind == "shot" and e.player_id == "red"
        for e in boosted.update(224, commands())
    )


def test_one_mine_per_player_and_enemy_trigger():
    engine = pickup_engine(ItemType.MINE)
    red = engine.tanks["red"]
    blue = engine.tanks["blue"]
    engine.update(16, commands(red_use=True))
    assert len(engine.mines) == 1

    red.held_item = ItemType.MINE
    engine.update(16, commands(red_use=True))
    assert red.held_item is ItemType.MINE
    assert len(engine.mines) == 1

    blue.x, blue.y = engine.mines[0].x, engine.mines[0].y
    events = engine.update(16, commands())
    assert blue.hp == 2
    assert engine.mines == []
    assert any(event.kind == "mine_triggered" for event in events)


def test_death_clears_the_destroyed_players_mine():
    engine = TankBattleEngine(seed=3)
    engine.mines = [MineState("red", 5, 5), MineState("blue", 6, 6)]
    engine.tanks["red"].hp = 1

    engine._resolve_damage_batch([("red", 1, "blue")])

    assert [mine.owner for mine in engine.mines] == ["blue"]


def test_pause_freezes_every_logic_clock():
    engine = TankBattleEngine(seed=3)
    engine.update(15, commands())
    before = engine.to_dict()
    assert before["accumulator_ms"] == 15
    engine.paused = True

    assert engine.update(5000, commands(red=(1, 0))) == []
    assert engine.to_dict() == before | {"paused": True}


def test_pickup_refresh_uses_a_12000_to_18000_ms_interval():
    for seed in range(20):
        engine = TankBattleEngine(seed=seed)
        assert 12_000 <= engine.next_pickup_ms <= 18_000

    engine = TankBattleEngine(seed=3)
    due = engine.next_pickup_ms
    engine.update(due + 16, commands())
    assert engine.pickup is not None
    assert engine.pickup.item in ItemType
    assert due + 12_000 <= engine.next_pickup_ms <= due + 18_016


def test_pickups_only_spawn_at_mirrored_central_contest_points():
    seen = set()
    for seed in range(40):
        engine = TankBattleEngine(seed=seed)
        engine.next_pickup_ms = 0
        engine.update(16, commands())
        seen.add((engine.pickup.x, engine.pickup.y))

    assert seen <= set(TankBattleEngine.PICKUP_SPAWN_CANDIDATES)
    assert {(ARENA_COLS - x, ARENA_ROWS - y) for x, y in seen} == seen


def test_pickup_spawn_is_delayed_when_all_central_points_are_occupied():
    engine = TankBattleEngine(seed=3)
    engine.next_pickup_ms = 0
    engine.mines = [MineState("red", x, y) for x, y in engine.PICKUP_SPAWN_CANDIDATES]

    assert engine.update(16, commands()) == []
    assert engine.pickup is None
    assert engine.next_pickup_ms > engine.elapsed_ms


def test_default_respawns_offer_mirrored_left_right_top_bottom_and_outer_routes():
    points = set(TankBattleEngine.RESPAWN_CANDIDATES)
    assert len(points) >= 8
    assert {(ARENA_COLS - x, y) for x, y in points} == points
    assert {(x, ARENA_ROWS - y) for x, y in points} == points
    assert any(y <= 2.5 for _, y in points)
    assert any(y >= ARENA_ROWS - 2.5 for _, y in points)
    assert any(x <= 2.5 for x, _ in points)
    assert any(x >= ARENA_COLS - 2.5 for x, _ in points)


def test_regulation_starts_at_180_seconds_and_music_phase_changes():
    engine = TankBattleEngine(seed=3)
    assert engine.remaining_ms == 180_000
    assert engine.phase is MatchPhase.REGULATION
    assert engine.music_phase == "normal"
    engine.remaining_ms = 45_000
    assert engine.music_phase == "final"
    engine.remaining_ms = 10_000
    assert engine.music_phase == "sprint"


def test_music_phase_has_a_literal_return_type():
    assert get_type_hints(TankBattleEngine.music_phase.fget)["return"] == Literal[
        "normal", "final", "sprint", "sudden"
    ]


def test_tied_regulation_enters_sudden_death_and_stops_pickups():
    engine = TankBattleEngine(seed=3)
    engine.remaining_ms = 16

    events = engine.update(32, commands())

    assert engine.phase is MatchPhase.SUDDEN_DEATH
    assert engine.music_phase == "sudden"
    assert engine.pickup is None
    assert any(event.kind == "sudden_death" for event in events)
    engine.update(20_000, commands())
    assert engine.pickup is None


def test_unequal_regulation_score_ends_the_match():
    engine = TankBattleEngine(seed=3)
    engine.score["red"] = 2
    engine.remaining_ms = 16

    events = engine.update(32, commands())

    assert engine.phase is MatchPhase.ENDED
    assert engine.winner == "red"
    assert any(event.kind == "match_ended" for event in events)
    before = engine.to_dict()
    engine.update(5_000, commands(red=(1, 0)))
    assert engine.to_dict() == before


def test_respawn_chooses_highest_scoring_safe_candidate():
    engine = TankBattleEngine(seed=3)
    engine.arena.rows = [list("." * 24) for _ in range(12)]
    engine.spawn_candidates = [(2.0, 6.0), (10.0, 6.0), (18.0, 6.0)]
    engine.tanks["blue"].x, engine.tanks["blue"].y = 20.0, 6.0
    engine.bullets = [BulletState("blue", 2.0, 6.0, 0.0, 0.0)]
    engine.tanks["red"].hp = 1

    events = engine._resolve_damage_batch([("red", 1, "blue")])

    assert engine.tanks["red"].position == (10.0, 6.0)
    assert any(event.kind == "respawn" for event in events)


def test_respawn_has_1500_ms_protection_and_400_ms_fire_lock():
    engine = TankBattleEngine(seed=3)
    engine.tanks["red"].hp = 1
    engine._resolve_damage_batch([("red", 1, "blue")])
    red = engine.tanks["red"]
    assert red.protected_until_ms == 1_500
    assert red.fire_locked_until_ms == 400

    engine._resolve_damage_batch([("red", 1, "blue")])
    assert red.hp == 3
    engine._fire_elapsed_ms["red"] = engine.FIRE_INTERVAL_MS
    engine.update(384, commands())
    assert all(bullet.owner != "red" for bullet in engine.bullets)

    engine.update(16, commands())
    assert any(bullet.owner == "red" for bullet in engine.bullets)
    engine.update(1_104, commands())
    engine._resolve_damage_batch([("red", 1, "blue")])
    assert red.hp == 2


def sudden_death_engine():
    engine = TankBattleEngine(seed=3)
    engine.arena.rows = [list("." * 24) for _ in range(12)]
    engine.phase = MatchPhase.SUDDEN_DEATH
    engine.remaining_ms = 0
    engine.tanks["red"].x, engine.tanks["red"].y = 4.0, 6.0
    engine.tanks["blue"].x, engine.tanks["blue"].y = 20.0, 6.0
    engine.tanks["red"].hp = engine.tanks["blue"].hp = 1
    return engine


def test_sudden_death_single_ko_ends_without_respawn():
    engine = sudden_death_engine()
    engine.bullets = [BulletState("red", 20.0, 6.0, 0.0, 0.0)]

    events = engine.update(16, commands())

    assert engine.phase is MatchPhase.ENDED
    assert engine.winner == "red"
    assert engine.tanks["blue"].hp == 0
    assert any(event.kind == "match_ended" for event in events)
    assert all(event.kind != "respawn" for event in events)


def test_sudden_death_double_ko_continues_independent_of_bullet_order():
    specs = (
        ("blue", 4.0, 6.0),
        ("red", 20.0, 6.0),
    )
    snapshots = []
    for order in permutations(specs):
        engine = sudden_death_engine()
        engine.bullets = [
            BulletState(owner, x, y, 0.0, 0.0) for owner, x, y in order
        ]

        events = engine.update(16, commands())

        assert engine.phase is MatchPhase.SUDDEN_DEATH
        assert engine.winner is None
        assert engine.tanks["red"].hp == engine.tanks["blue"].hp == 3
        assert sum(event.kind == "respawn" for event in events) == 2
        snapshots.append(engine.to_dict())
    assert snapshots[0] == snapshots[1]


class AllocationEngine(TankBattleEngine):
    def __init__(self, seed, red_fallback, blue_fallback):
        super().__init__(seed=seed)
        self.spawn_candidates = [(5.0, 5.0), (10.0, 5.0)]
        self.fallback = {"red": red_fallback, "blue": blue_fallback}
        self.tanks["red"].hp = self.tanks["blue"].hp = 0

    def _spawn_score(self, point, enemy):
        respawning_player = "blue" if enemy.player_id == "red" else "red"
        return 10.0 if point == (5.0, 5.0) else self.fallback[respawning_player]


def shared_point_owner(engine):
    engine._respawn_players(["red", "blue"])
    return next(
        player_id
        for player_id, tank in engine.tanks.items()
        if tank.position == (5.0, 5.0)
    )


def test_joint_respawn_maximizes_minimum_score_before_total_score():
    engine = AllocationEngine(seed=3, red_fallback=1.0, blue_fallback=9.0)

    assert shared_point_owner(engine) == "red"


def test_tied_shared_respawn_point_is_awarded_to_both_players_across_seeds():
    owners = {
        shared_point_owner(
            AllocationEngine(seed=seed, red_fallback=9.0, blue_fallback=9.0)
        )
        for seed in range(20)
    }

    assert owners == {"red", "blue"}


def test_joint_respawn_is_symmetric_when_player_labels_are_swapped():
    red_needs_shared = AllocationEngine(seed=7, red_fallback=1.0, blue_fallback=9.0)
    blue_needs_shared = AllocationEngine(seed=7, red_fallback=9.0, blue_fallback=1.0)

    assert shared_point_owner(red_needs_shared) == "red"
    assert shared_point_owner(blue_needs_shared) == "blue"
