import copy
import json

import pytest

from meridian.tank_engine import (
    BulletState,
    ItemType,
    MatchPhase,
    MineState,
    PickupState,
    PlayerCommand,
    TankBattleEngine,
    TankSnapshotError,
)


def progressed_engine(seed=11):
    engine = TankBattleEngine(seed=seed)
    for _ in range(40):
        engine.update(
            16,
            {
                "red": PlayerCommand(1, 1),
                "blue": PlayerCommand(-1, 0),
            },
        )
    engine.update(7, {})
    engine.arena.rows[2] = engine.arena.rows[2].replace("B", ".", 1)
    engine.tanks["red"].held_item = ItemType.SHIELD
    engine.tanks["red"].shield_until_ms = engine.elapsed_ms + 1234
    engine.tanks["blue"].speed_until_ms = engine.elapsed_ms + 2345
    engine.tanks["blue"].protected_until_ms = engine.elapsed_ms + 3456
    engine.tanks["blue"].fire_locked_until_ms = engine.elapsed_ms + 456
    engine.bullets = [BulletState("red", 4.5, 3.5, 1.0, 0.0)]
    engine.mines = [MineState("blue", 12.5, 8.5)]
    engine.pickup = PickupState(ItemType.REPAIR, 8.5, 4.5)
    engine.score = {"red": 2, "blue": 1}
    return engine


def scripted_commands():
    return [
        {"red": PlayerCommand(0, -1), "blue": PlayerCommand(1, 0)},
        {"red": PlayerCommand(1, 0, True), "blue": PlayerCommand()},
        {"red": PlayerCommand(), "blue": PlayerCommand(0, 1)},
    ] * 20


def test_round_trip_preserves_all_rules_state_and_is_json_safe():
    engine = progressed_engine()
    snapshot = engine.to_dict()

    restored = TankBattleEngine.from_dict(json.loads(json.dumps(snapshot)))

    assert restored.to_dict() == snapshot
    assert restored.arena.rows == engine.arena.rows


def test_restored_engine_starts_with_neutral_live_input():
    engine = progressed_engine()
    restored = TankBattleEngine.from_dict(engine.to_dict())
    before = restored.tanks["red"].position

    restored.update(16, {})

    assert restored.tanks["red"].position == before


def test_same_saved_state_and_commands_produce_same_events_and_state():
    left = progressed_engine()
    right = TankBattleEngine.from_dict(left.to_dict())

    assert [left.update(16, command) for command in scripted_commands()] == [
        right.update(16, command) for command in scripted_commands()
    ]
    assert left.to_dict() == right.to_dict()


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("version",), 99),
        (("tanks",), []),
        (("tanks", "green"), {}),
        (("arena", "rows"), ["." * 24] * 11),
        (("arena", "rows", 1), "." * 23),
        (("arena", "rows", 1), "." * 23 + "?"),
        (("phase",), "waiting"),
        (("music_phase",), "overtime"),
        (("winner",), "green"),
        (("remaining_ms",), -1),
        (("score", "red"), -1),
        (("tanks", "red", "hp"), 4),
        (("tanks", "red", "facing_x"), 2),
        (("bullets",), [{"owner": "green", "x": 1, "y": 1, "dx": 1, "dy": 0}]),
        (("rng_state",), [3, [], None]),
    ],
)
def test_invalid_snapshot_raises_tank_snapshot_error(path, value):
    snapshot = progressed_engine().to_dict()
    target = snapshot
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    with pytest.raises(TankSnapshotError):
        TankBattleEngine.from_dict(snapshot)


def test_incomplete_or_non_mapping_snapshot_raises_tank_snapshot_error():
    with pytest.raises(TankSnapshotError):
        TankBattleEngine.from_dict({"version": 1, "tanks": []})
    with pytest.raises(TankSnapshotError):
        TankBattleEngine.from_dict([])  # type: ignore[arg-type]


def test_loading_does_not_alias_mutable_snapshot_data():
    snapshot = progressed_engine().to_dict()
    restored = TankBattleEngine.from_dict(snapshot)
    frozen = copy.deepcopy(restored.to_dict())

    snapshot["arena"]["rows"][1] = "S" * 24
    snapshot["tanks"]["red"]["hp"] = 0

    assert restored.to_dict() == frozen


def test_phase_and_winner_round_trip():
    engine = progressed_engine()
    engine.phase = MatchPhase.ENDED
    engine.winner = "red"

    restored = TankBattleEngine.from_dict(engine.to_dict())

    assert restored.phase is MatchPhase.ENDED
    assert restored.winner == "red"
