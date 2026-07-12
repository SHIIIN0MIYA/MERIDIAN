"""Deterministic, rendering-independent logic for Tank Duel."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from itertools import permutations
import math
import random
from collections.abc import Mapping as MappingABC, Sequence
from typing import Literal, Mapping


ARENA_COLS = 24
ARENA_ROWS = 12


class TankSnapshotError(ValueError):
    """Raised when a tank battle snapshot is malformed or unsupported."""


class Terrain(str, Enum):
    EMPTY = "."
    BRICK = "B"
    STEEL = "S"
    GRASS = "G"


class ItemType(str, Enum):
    REPAIR = "repair"
    SHIELD = "shield"
    SPEED = "speed"
    MINE = "mine"


class MatchPhase(str, Enum):
    REGULATION = "regulation"
    SUDDEN_DEATH = "sudden_death"
    ENDED = "ended"


@dataclass
class PickupState:
    item: ItemType
    x: float
    y: float


@dataclass
class MineState:
    owner: str
    x: float
    y: float


@dataclass(frozen=True)
class PlayerCommand:
    move_x: int = 0
    move_y: int = 0
    use_item: bool = False


@dataclass
class TankState:
    player_id: str
    x: float
    y: float
    facing_x: int
    facing_y: int
    hp: int = 3
    held_item: ItemType | None = None
    shield_until_ms: int = 0
    speed_until_ms: int = 0
    protected_until_ms: int = 0
    fire_locked_until_ms: int = 0

    @property
    def position(self) -> tuple[float, float]:
        return self.x, self.y


@dataclass
class BulletState:
    owner: str
    x: float
    y: float
    dx: float
    dy: float

    @property
    def direction(self) -> tuple[float, float]:
        return self.dx, self.dy


@dataclass(frozen=True)
class EngineEvent:
    kind: str
    player_id: str | None = None
    data: Mapping[str, object] = field(default_factory=dict)


@dataclass
class Arena:
    rows: list[str]

    def __post_init__(self) -> None:
        if len(self.rows) != ARENA_ROWS or any(
            len(row) != ARENA_COLS for row in self.rows
        ):
            raise ValueError(f"arena must be {ARENA_COLS}x{ARENA_ROWS}")

    def is_walkable(self, x: int | float, y: int | float) -> bool:
        tile_x = math.floor(x)
        tile_y = math.floor(y)
        if not (0 <= tile_x < ARENA_COLS and 0 <= tile_y < ARENA_ROWS):
            return False
        return self.rows[tile_y][tile_x] in {
            Terrain.EMPTY.value,
            Terrain.GRASS.value,
        }

    def has_line_of_sight(
        self, first: tuple[float, float], second: tuple[float, float]
    ) -> bool:
        distance = math.dist(first, second)
        samples = max(1, math.ceil(distance * 4))
        for index in range(1, samples):
            fraction = index / samples
            x = first[0] + (second[0] - first[0]) * fraction
            y = first[1] + (second[1] - first[1]) * fraction
            tile_x, tile_y = math.floor(x), math.floor(y)
            if not (0 <= tile_x < ARENA_COLS and 0 <= tile_y < ARENA_ROWS):
                return False
            if self.rows[tile_y][tile_x] in {
                Terrain.BRICK.value,
                Terrain.STEEL.value,
            }:
                return False
        return True

    def open_neighbor_count(self, point: tuple[float, float]) -> int:
        x, y = math.floor(point[0]), math.floor(point[1])
        return sum(
            self.is_walkable(neighbor_x, neighbor_y)
            for neighbor_x, neighbor_y in (
                (x - 1, y),
                (x + 1, y),
                (x, y - 1),
                (x, y + 1),
            )
        )


_ARENA_ROWS = [
    "SSSSSSSSSSSSSSSSSSSSSSSS",
    "S......................S",
    "S....BB..........BB....S",
    "S......G........G......S",
    "S..S................S..S",
    "S..........BB..........S",
    "S..........SS..........S",
    "S..S................S..S",
    "S......G........G......S",
    "S....BB..........BB....S",
    "S......................S",
    "SSSSSSSSSSSSSSSSSSSSSSSS",
]


class TankBattleEngine:
    SNAPSHOT_VERSION = 1
    STEP_MS = 16
    MOVE_SPEED = 0.004
    BULLET_SPEED = 0.006
    FIRE_INTERVAL_MS = 650
    MAX_BULLETS_PER_PLAYER = 2
    TANK_HALF_SIZE = 0.35
    BULLET_CLASH_DISTANCE = 0.2
    MATCH_DURATION_MS = 180_000
    PICKUP_MIN_INTERVAL_MS = 12_000
    PICKUP_MAX_INTERVAL_MS = 18_000
    PICKUP_SPAWN_CANDIDATES = (
        (10.5, 4.5), (13.5, 4.5), (10.5, 7.5), (13.5, 7.5),
    )
    RESPAWN_CANDIDATES = (
        (1.5, 1.5), (6.5, 1.5), (17.5, 1.5), (22.5, 1.5),
        (1.5, 5.5), (22.5, 5.5), (1.5, 6.5), (22.5, 6.5),
        (1.5, 10.5), (6.5, 10.5), (17.5, 10.5), (22.5, 10.5),
    )

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self.arena = Arena(list(_ARENA_ROWS))
        self.spawn_candidates = list(self.RESPAWN_CANDIDATES)
        self.tanks = {
            "red": TankState("red", 1.5, 1.5, 1, 0),
            "blue": TankState("blue", 22.5, 10.5, -1, 0),
        }
        self.bullets: list[BulletState] = []
        self.score = {"red": 0, "blue": 0}
        self.pickup: PickupState | None = None
        self.mines: list[MineState] = []
        self._rng = random.Random(seed)
        self.elapsed_ms = 0
        self.remaining_ms = self.MATCH_DURATION_MS
        self.phase = MatchPhase.REGULATION
        self.winner: str | None = None
        self.paused = False
        self.next_pickup_ms = self._rng.randint(
            self.PICKUP_MIN_INTERVAL_MS, self.PICKUP_MAX_INTERVAL_MS
        )
        self._fire_elapsed_ms = {"red": 0, "blue": 0}
        self._accumulator_ms = 0

    def update(
        self,
        dt_ms: int,
        commands: Mapping[str, PlayerCommand],
    ) -> list[EngineEvent]:
        if self.paused or self.phase is MatchPhase.ENDED:
            return []
        self._accumulator_ms += max(0, dt_ms)
        events: list[EngineEvent] = []
        while self._accumulator_ms >= self.STEP_MS:
            events.extend(self._step(self.STEP_MS, commands))
            self._accumulator_ms -= self.STEP_MS
            if self.phase is MatchPhase.ENDED:
                self._accumulator_ms = 0
                break
        return events

    def _step(
        self,
        dt_ms: int,
        commands: Mapping[str, PlayerCommand],
    ) -> list[EngineEvent]:
        self.elapsed_ms += dt_ms
        if self.phase is MatchPhase.REGULATION:
            self.remaining_ms = max(0, self.remaining_ms - dt_ms)
        self._expire_effects()
        self._move_tanks_simultaneously(dt_ms, commands)
        events = self._collect_pickup()
        events.extend(self._use_items(commands))
        events.extend(self._spawn_due_bullets(dt_ms))
        self._move_bullets(dt_ms)

        removed: set[int] = set()
        hits: list[tuple[str, int, str, str]] = []
        mine_events, mine_hits = self._collect_mine_triggers()
        events.extend(mine_events)
        hits.extend(mine_hits)
        events.extend(self._collect_bullet_clashes(removed))
        events.extend(self._collect_bullet_impacts(removed, hits))
        self.bullets = [
            bullet for index, bullet in enumerate(self.bullets) if index not in removed
        ]
        events.extend(self._resolve_damage_batch(hits))
        events.extend(self._advance_match_phase())
        events.extend(self._spawn_pickup_if_due())
        return events

    @property
    def music_phase(self) -> Literal["normal", "final", "sprint", "sudden"]:
        if self.phase is MatchPhase.SUDDEN_DEATH:
            return "sudden"
        if self.remaining_ms <= 15_000:
            return "sprint"
        if self.remaining_ms <= 60_000:
            return "final"
        return "normal"

    def _advance_match_phase(self) -> list[EngineEvent]:
        if self.phase is not MatchPhase.REGULATION or self.remaining_ms > 0:
            return []
        if self.score["red"] == self.score["blue"]:
            self.phase = MatchPhase.SUDDEN_DEATH
            return [EngineEvent("sudden_death")]
        self.phase = MatchPhase.ENDED
        self.winner = max(self.score, key=self.score.get)
        return [EngineEvent("match_ended", self.winner)]

    def _spawn_pickup_if_due(self) -> list[EngineEvent]:
        if (
            self.phase is not MatchPhase.REGULATION
            or self.elapsed_ms < self.next_pickup_ms
        ):
            return []
        self.next_pickup_ms = self.elapsed_ms + self._rng.randint(
            self.PICKUP_MIN_INTERVAL_MS, self.PICKUP_MAX_INTERVAL_MS
        )
        if self.pickup is not None:
            return []
        occupied = {
            (math.floor(tank.x), math.floor(tank.y)) for tank in self.tanks.values()
        }
        occupied.update((math.floor(mine.x), math.floor(mine.y)) for mine in self.mines)
        candidates = [
            (x, y) for x, y in self.PICKUP_SPAWN_CANDIDATES
            if self.arena.is_walkable(math.floor(x), math.floor(y))
            and (math.floor(x), math.floor(y)) not in occupied
        ]
        if not candidates:
            return []
        x, y = self._rng.choice(candidates)
        item = self._rng.choice(tuple(ItemType))
        self.pickup = PickupState(item, x, y)
        return [EngineEvent("pickup_spawned", data={"item": item.value})]

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.SNAPSHOT_VERSION,
            "seed": self.seed,
            "arena": {
                "cols": ARENA_COLS,
                "row_count": ARENA_ROWS,
                "rows": ["".join(row) for row in self.arena.rows],
            },
            "paused": self.paused,
            "elapsed_ms": self.elapsed_ms,
            "remaining_ms": self.remaining_ms,
            "phase": self.phase.value,
            "winner": self.winner,
            "music_phase": self.music_phase,
            "next_pickup_ms": self.next_pickup_ms,
            "accumulator_ms": self._accumulator_ms,
            "fire_elapsed_ms": dict(self._fire_elapsed_ms),
            "score": dict(self.score),
            "tanks": {
                player_id: {
                    "x": tank.x,
                    "y": tank.y,
                    "facing_x": tank.facing_x,
                    "facing_y": tank.facing_y,
                    "hp": tank.hp,
                    "held_item": (
                        tank.held_item.value if tank.held_item is not None else None
                    ),
                    "shield_until_ms": tank.shield_until_ms,
                    "speed_until_ms": tank.speed_until_ms,
                    "protected_until_ms": tank.protected_until_ms,
                    "fire_locked_until_ms": tank.fire_locked_until_ms,
                }
                for player_id, tank in self.tanks.items()
            },
            "bullets": [
                {
                    "owner": bullet.owner,
                    "x": bullet.x,
                    "y": bullet.y,
                    "dx": bullet.dx,
                    "dy": bullet.dy,
                }
                for bullet in self.bullets
            ],
            "pickup": (
                None
                if self.pickup is None
                else {
                    "item": self.pickup.item.value,
                    "x": self.pickup.x,
                    "y": self.pickup.y,
                }
            ),
            "mines": [
                {"owner": mine.owner, "x": mine.x, "y": mine.y}
                for mine in self.mines
            ],
            "rng_state": _json_list(self._rng.getstate()),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> TankBattleEngine:
        """Restore a battle from a validated, versioned JSON snapshot."""
        try:
            root = _snapshot_mapping(data, "snapshot")
            if _snapshot_int(root, "version", 1, 1) != cls.SNAPSHOT_VERSION:
                raise TankSnapshotError("unsupported snapshot version")

            seed = _snapshot_int(root, "seed")
            arena_data = _snapshot_mapping(root.get("arena"), "arena")
            if _snapshot_int(arena_data, "cols") != ARENA_COLS:
                raise TankSnapshotError("arena width does not match engine")
            if _snapshot_int(arena_data, "row_count") != ARENA_ROWS:
                raise TankSnapshotError("arena height does not match engine")
            raw_rows = _snapshot_sequence(arena_data.get("rows"), "arena.rows")
            if len(raw_rows) != ARENA_ROWS:
                raise TankSnapshotError("arena has the wrong number of rows")
            terrain_values = {terrain.value for terrain in Terrain}
            rows: list[str] = []
            for row in raw_rows:
                if not isinstance(row, str) or len(row) != ARENA_COLS:
                    raise TankSnapshotError("arena row has the wrong width")
                if any(tile not in terrain_values for tile in row):
                    raise TankSnapshotError("arena contains invalid terrain")
                rows.append(row)

            tank_data = _snapshot_mapping(root.get("tanks"), "tanks")
            player_ids = {"red", "blue"}
            if set(tank_data) != player_ids:
                raise TankSnapshotError("snapshot must contain red and blue tanks")
            tanks: dict[str, TankState] = {}
            for player_id in ("red", "blue"):
                raw = _snapshot_mapping(tank_data[player_id], f"tanks.{player_id}")
                held_value = raw.get("held_item")
                held_item = (
                    None
                    if held_value is None
                    else _snapshot_enum(ItemType, held_value, "held_item")
                )
                facing_x = _snapshot_int(raw, "facing_x", -1, 1)
                facing_y = _snapshot_int(raw, "facing_y", -1, 1)
                if facing_x == 0 and facing_y == 0:
                    raise TankSnapshotError("tank facing direction cannot be zero")
                tanks[player_id] = TankState(
                    player_id,
                    _snapshot_coordinate(raw, "x", ARENA_COLS),
                    _snapshot_coordinate(raw, "y", ARENA_ROWS),
                    facing_x,
                    facing_y,
                    _snapshot_int(raw, "hp", 0, 3),
                    held_item,
                    _snapshot_int(raw, "shield_until_ms", 0),
                    _snapshot_int(raw, "speed_until_ms", 0),
                    _snapshot_int(raw, "protected_until_ms", 0),
                    _snapshot_int(raw, "fire_locked_until_ms", 0),
                )

            score_data = _snapshot_mapping(root.get("score"), "score")
            fire_data = _snapshot_mapping(root.get("fire_elapsed_ms"), "fire_elapsed_ms")
            if set(score_data) != player_ids or set(fire_data) != player_ids:
                raise TankSnapshotError("score and cooldowns require both player IDs")

            bullets = []
            for raw_value in _snapshot_sequence(root.get("bullets"), "bullets"):
                raw = _snapshot_mapping(raw_value, "bullet")
                owner = _snapshot_player(raw.get("owner"), "bullet owner")
                bullets.append(
                    BulletState(
                        owner,
                        _snapshot_number(raw, "x", -1, ARENA_COLS + 1),
                        _snapshot_number(raw, "y", -1, ARENA_ROWS + 1),
                        _snapshot_number(raw, "dx", -1, 1),
                        _snapshot_number(raw, "dy", -1, 1),
                    )
                )

            mines = []
            for raw_value in _snapshot_sequence(root.get("mines"), "mines"):
                raw = _snapshot_mapping(raw_value, "mine")
                mines.append(
                    MineState(
                        _snapshot_player(raw.get("owner"), "mine owner"),
                        _snapshot_coordinate(raw, "x", ARENA_COLS),
                        _snapshot_coordinate(raw, "y", ARENA_ROWS),
                    )
                )

            pickup_value = root.get("pickup")
            pickup = None
            if pickup_value is not None:
                raw = _snapshot_mapping(pickup_value, "pickup")
                pickup = PickupState(
                    _snapshot_enum(ItemType, raw.get("item"), "pickup item"),
                    _snapshot_coordinate(raw, "x", ARENA_COLS),
                    _snapshot_coordinate(raw, "y", ARENA_ROWS),
                )

            phase = _snapshot_enum(MatchPhase, root.get("phase"), "phase")
            winner_value = root.get("winner")
            winner = None if winner_value is None else _snapshot_player(winner_value, "winner")
            paused = root.get("paused")
            if not isinstance(paused, bool):
                raise TankSnapshotError("paused must be a boolean")

            engine = cls(seed=seed)
            engine.arena = Arena(rows)
            engine.tanks = tanks
            engine.bullets = bullets
            engine.score = {
                player_id: _snapshot_int(score_data, player_id, 0)
                for player_id in ("red", "blue")
            }
            engine.pickup = pickup
            engine.mines = mines
            engine.elapsed_ms = _snapshot_int(root, "elapsed_ms", 0)
            engine.remaining_ms = _snapshot_int(
                root, "remaining_ms", 0, cls.MATCH_DURATION_MS
            )
            engine.phase = phase
            engine.winner = winner
            engine.paused = paused
            engine.next_pickup_ms = _snapshot_int(root, "next_pickup_ms", 0)
            engine._fire_elapsed_ms = {
                player_id: _snapshot_int(fire_data, player_id, 0)
                for player_id in ("red", "blue")
            }
            engine._accumulator_ms = _snapshot_int(
                root, "accumulator_ms", 0, cls.STEP_MS - 1
            )
            music_phase = root.get("music_phase")
            if music_phase not in {"normal", "final", "sprint", "sudden"}:
                raise TankSnapshotError("invalid music_phase")
            if music_phase != engine.music_phase:
                raise TankSnapshotError("music_phase is inconsistent with match state")
            rng_state = _tuple_tree(root.get("rng_state"))
            engine._rng.setstate(rng_state)
            return engine
        except TankSnapshotError:
            raise
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise TankSnapshotError(f"invalid tank snapshot: {exc}") from exc

    def _expire_effects(self) -> None:
        for tank in self.tanks.values():
            if tank.shield_until_ms <= self.elapsed_ms:
                tank.shield_until_ms = 0
            if tank.speed_until_ms <= self.elapsed_ms:
                tank.speed_until_ms = 0
            if tank.protected_until_ms <= self.elapsed_ms:
                tank.protected_until_ms = 0
            if tank.fire_locked_until_ms <= self.elapsed_ms:
                tank.fire_locked_until_ms = 0

    def _collect_mine_triggers(
        self,
    ) -> tuple[list[EngineEvent], list[tuple[str, int, str, str]]]:
        triggered: set[int] = set()
        events: list[EngineEvent] = []
        hits: list[tuple[str, int, str, str]] = []
        for index, mine in enumerate(self.mines):
            targets = sorted(
                player_id
                for player_id, tank in self.tanks.items()
                if player_id != mine.owner
                and tank.hp > 0
                and abs(tank.x - mine.x) <= self.TANK_HALF_SIZE
                and abs(tank.y - mine.y) <= self.TANK_HALF_SIZE
            )
            if not targets:
                continue
            target = targets[0]
            triggered.add(index)
            hits.append((target, 1, mine.owner, "mine"))
            events.append(
                EngineEvent(
                    "mine_triggered",
                    target,
                    {"owner": mine.owner},
                )
            )
        self.mines = [
            mine for index, mine in enumerate(self.mines) if index not in triggered
        ]
        return events, hits

    def _collect_pickup(self) -> list[EngineEvent]:
        if self.pickup is None:
            return []
        eligible = sorted(
            player_id
            for player_id, tank in self.tanks.items()
            if tank.hp > 0
            and tank.held_item is None
            and abs(tank.x - self.pickup.x) <= self.TANK_HALF_SIZE
            and abs(tank.y - self.pickup.y) <= self.TANK_HALF_SIZE
        )
        if not eligible:
            return []
        player_id = eligible[0] if len(eligible) == 1 else self._rng.choice(eligible)
        item = self.pickup.item
        self.tanks[player_id].held_item = item
        self.pickup = None
        return [EngineEvent("pickup", player_id, {"item": item.value})]

    def _use_items(
        self, commands: Mapping[str, PlayerCommand]
    ) -> list[EngineEvent]:
        events: list[EngineEvent] = []
        for player_id in sorted(self.tanks):
            tank = self.tanks[player_id]
            item = tank.held_item
            if item is None or not commands.get(player_id, PlayerCommand()).use_item:
                continue
            if item is ItemType.REPAIR:
                if tank.hp >= 3:
                    continue
                tank.hp = min(3, tank.hp + 1)
            elif item is ItemType.SHIELD:
                tank.shield_until_ms = self.elapsed_ms + 15_000
            elif item is ItemType.SPEED:
                tank.speed_until_ms = self.elapsed_ms + 6_000
            elif item is ItemType.MINE:
                if any(mine.owner == player_id for mine in self.mines):
                    continue
                self.mines.append(MineState(player_id, tank.x, tank.y))
            tank.held_item = None
            data = {"item": item.value}
            events.append(EngineEvent("item_used", player_id, data))
        return events

    def _spawn_due_bullets(self, dt_ms: int) -> list[EngineEvent]:
        events: list[EngineEvent] = []
        for player_id, tank in self.tanks.items():
            if tank.hp <= 0:
                continue
            self._fire_elapsed_ms[player_id] += dt_ms
            if tank.fire_locked_until_ms > self.elapsed_ms:
                continue
            fire_interval_ms = (
                430 if tank.speed_until_ms > self.elapsed_ms else self.FIRE_INTERVAL_MS
            )
            if self._fire_elapsed_ms[player_id] < fire_interval_ms:
                continue
            self._fire_elapsed_ms[player_id] -= fire_interval_ms
            owned = sum(bullet.owner == player_id for bullet in self.bullets)
            if owned >= self.MAX_BULLETS_PER_PLAYER:
                continue
            length = math.hypot(tank.facing_x, tank.facing_y)
            dx = tank.facing_x / length
            dy = tank.facing_y / length
            self.bullets.append(BulletState(player_id, tank.x, tank.y, dx, dy))
            events.append(EngineEvent("shot", player_id))
        return events

    def _move_bullets(self, dt_ms: int) -> None:
        distance = self.BULLET_SPEED * dt_ms
        for bullet in self.bullets:
            bullet.x += bullet.dx * distance
            bullet.y += bullet.dy * distance

    def _collect_bullet_clashes(self, removed: set[int]) -> list[EngineEvent]:
        events: list[EngineEvent] = []
        participants: set[int] = set()
        for first_index, first in enumerate(self.bullets):
            for second_index in range(first_index + 1, len(self.bullets)):
                second = self.bullets[second_index]
                if first.owner != second.owner and math.dist(
                    (first.x, first.y), (second.x, second.y)
                ) <= (
                    self.BULLET_CLASH_DISTANCE
                ):
                    participants.update((first_index, second_index))
                    events.append(EngineEvent("bullet_clash"))
        removed.update(participants)
        return events

    def _collect_bullet_impacts(
        self,
        removed: set[int],
        hits: list[tuple[str, int, str, str]],
    ) -> list[EngineEvent]:
        events: list[EngineEvent] = []
        bricks_hit: dict[tuple[int, int], str] = {}
        for index, bullet in enumerate(self.bullets):
            if index in removed:
                continue
            tile_x, tile_y = math.floor(bullet.x), math.floor(bullet.y)
            if not (0 <= tile_x < ARENA_COLS and 0 <= tile_y < ARENA_ROWS):
                removed.add(index)
                continue
            terrain = self.arena.rows[tile_y][tile_x]
            if terrain == Terrain.BRICK.value:
                bricks_hit.setdefault((tile_x, tile_y), bullet.owner)
                removed.add(index)
                events.append(EngineEvent("brick_impact", bullet.owner))
                continue
            if terrain == Terrain.STEEL.value:
                removed.add(index)
                continue
            for target, tank in self.tanks.items():
                if target == bullet.owner or tank.hp <= 0:
                    continue
                if (
                    abs(bullet.x - tank.x) <= self.TANK_HALF_SIZE
                    and abs(bullet.y - tank.y) <= self.TANK_HALF_SIZE
                ):
                    removed.add(index)
                    hits.append((target, 1, bullet.owner, "bullet"))
                    events.append(
                        EngineEvent("tank_hit", target, {"attacker": bullet.owner})
                    )
                    break
        for (tile_x, tile_y), owner in bricks_hit.items():
            self._replace_tile(tile_x, tile_y, Terrain.EMPTY.value)
            events.append(EngineEvent("brick_hit", owner))
        return events

    def _replace_tile(self, x: int, y: int, value: str) -> None:
        row = self.arena.rows[y]
        if isinstance(row, str):
            self.arena.rows[y] = row[:x] + value + row[x + 1 :]
        else:
            row[x] = value

    def _resolve_damage_batch(
        self, hits: list[tuple[str, int, str] | tuple[str, int, str, str]]
    ) -> list[EngineEvent]:
        damage = {"red": 0, "blue": 0}
        attackers: dict[str, list[str]] = {"red": [], "blue": []}
        hit_sources: dict[str, list[tuple[str, str]]] = {"red": [], "blue": []}
        for hit in hits:
            target, amount, attacker = hit[:3]
            source = hit[3] if len(hit) == 4 else "unknown"
            damage[target] += amount
            attackers[target].append(attacker)
            hit_sources[target].append((source, attacker))

        events: list[EngineEvent] = []
        destroyed: list[str] = []
        for target in ("red", "blue"):
            if not damage[target]:
                continue
            tank = self.tanks[target]
            if tank.protected_until_ms > self.elapsed_ms:
                damage[target] = 0
                continue
            if tank.shield_until_ms > self.elapsed_ms:
                damage[target] = max(0, damage[target] - 1)
                tank.shield_until_ms = 0
                source, attacker = sorted(hit_sources[target])[0]
                events.append(EngineEvent(
                    "shield_blocked", target,
                    {"attacker": attacker, "source": source},
                ))
            was_alive = tank.hp > 0
            tank.hp = max(0, tank.hp - damage[target])
            if was_alive and tank.hp == 0:
                destroyed.append(target)

        for target in destroyed:
            attacker = attackers[target][0]
            self.score[attacker] += 1
            self.mines = [mine for mine in self.mines if mine.owner != target]
            events.append(
                EngineEvent("tank_destroyed", target, {"attacker": attacker})
            )
        if self.phase is MatchPhase.SUDDEN_DEATH and len(destroyed) == 1:
            self.phase = MatchPhase.ENDED
            self.winner = attackers[destroyed[0]][0]
            events.append(EngineEvent("match_ended", self.winner))
        elif destroyed:
            events.extend(self._respawn_players(destroyed))
        return events

    def _respawn_players(self, player_ids: list[str]) -> list[EngineEvent]:
        players = tuple(dict.fromkeys(player_ids))
        assignments: list[
            tuple[
                tuple[float, float],
                tuple[tuple[float, float], ...],
            ]
        ] = []
        for points in permutations(self.spawn_candidates, len(players)):
            scores = []
            for player_id, point in zip(players, points):
                enemy_id = "blue" if player_id == "red" else "red"
                scores.append(self._spawn_score(point, self.tanks[enemy_id]))
            objective = (min(scores), sum(scores))
            assignments.append((objective, points))
        best_objective = max(objective for objective, _ in assignments)
        best_assignments = [
            points
            for objective, points in assignments
            if objective == best_objective
        ]
        selected = self._rng.choice(best_assignments)
        chosen = dict(zip(players, selected))

        events: list[EngineEvent] = []
        for player_id in players:
            tank = self.tanks[player_id]
            tank.x, tank.y = chosen[player_id]
            tank.hp = 3
            tank.held_item = None
            tank.shield_until_ms = 0
            tank.speed_until_ms = 0
            tank.protected_until_ms = self.elapsed_ms + 1_500
            tank.fire_locked_until_ms = self.elapsed_ms + 400
            self._fire_elapsed_ms[player_id] = 0
            events.append(
                EngineEvent(
                    "respawn",
                    player_id,
                    {"x": tank.x, "y": tank.y},
                )
            )
        return events

    def _spawn_score(self, point: tuple[float, float], enemy: TankState) -> float:
        if self._spawn_is_blocked(point) or self._projectile_threat(point):
            return float("-inf")
        distance = math.dist(point, enemy.position)
        line_bonus = 0.0 if self.arena.has_line_of_sight(point, enemy.position) else 8.0
        exits = self.arena.open_neighbor_count(point)
        return distance + line_bonus + exits * 2.0

    def _spawn_is_blocked(self, point: tuple[float, float]) -> bool:
        if not self._position_is_walkable(point):
            return True
        if any(
            tank.hp > 0 and self._tanks_overlap(point, tank.position)
            for tank in self.tanks.values()
        ):
            return True
        return any(
            abs(mine.x - point[0]) <= self.TANK_HALF_SIZE
            and abs(mine.y - point[1]) <= self.TANK_HALF_SIZE
            for mine in self.mines
        )

    def _projectile_threat(self, point: tuple[float, float]) -> bool:
        horizon = self.BULLET_SPEED * 750
        for bullet in self.bullets:
            start = (bullet.x, bullet.y)
            end = (bullet.x + bullet.dx * horizon, bullet.y + bullet.dy * horizon)
            vx, vy = end[0] - start[0], end[1] - start[1]
            length_sq = vx * vx + vy * vy
            if length_sq == 0:
                closest = start
            else:
                projection = (
                    (point[0] - start[0]) * vx + (point[1] - start[1]) * vy
                ) / length_sq
                projection = max(0.0, min(1.0, projection))
                closest = (start[0] + projection * vx, start[1] + projection * vy)
            if math.dist(point, closest) <= self.TANK_HALF_SIZE:
                return True
        return False

    @staticmethod
    def _normalized_move(command: PlayerCommand) -> tuple[float, float]:
        length = math.hypot(command.move_x, command.move_y)
        if length == 0:
            return 0.0, 0.0
        return command.move_x / length, command.move_y / length

    def _move_tanks_simultaneously(
        self,
        dt_ms: int,
        commands: Mapping[str, PlayerCommand],
    ) -> None:
        candidates: dict[str, tuple[float, float]] = {}
        for player_id, tank in self.tanks.items():
            command = commands.get(player_id, PlayerCommand())
            move_x, move_y = self._normalized_move(command)
            if move_x or move_y:
                tank.facing_x = _direction(move_x)
                tank.facing_y = _direction(move_y)
            speed_multiplier = 1.25 if tank.speed_until_ms > self.elapsed_ms else 1.0
            distance = self.MOVE_SPEED * speed_multiplier * dt_ms
            candidate = (tank.x + move_x * distance, tank.y + move_y * distance)
            candidates[player_id] = (
                candidate if self._position_is_walkable(candidate) else tank.position
            )

        rejected: set[str] = set()
        player_ids = tuple(self.tanks)
        for index, first_id in enumerate(player_ids):
            for second_id in player_ids[index + 1 :]:
                if self._tanks_overlap(candidates[first_id], candidates[second_id]):
                    rejected.update((first_id, second_id))

        for player_id, tank in self.tanks.items():
            if player_id not in rejected:
                tank.x, tank.y = candidates[player_id]

    def _position_is_walkable(self, position: tuple[float, float]) -> bool:
        x, y = position
        epsilon = 1e-9
        left = math.floor(x - self.TANK_HALF_SIZE)
        right = math.floor(x + self.TANK_HALF_SIZE - epsilon)
        top = math.floor(y - self.TANK_HALF_SIZE)
        bottom = math.floor(y + self.TANK_HALF_SIZE - epsilon)
        return all(
            self.arena.is_walkable(tile_x, tile_y)
            for tile_y in range(top, bottom + 1)
            for tile_x in range(left, right + 1)
        )

    def _tanks_overlap(
        self,
        first: tuple[float, float],
        second: tuple[float, float],
    ) -> bool:
        diameter = self.TANK_HALF_SIZE * 2
        return abs(first[0] - second[0]) < diameter and abs(first[1] - second[1]) < diameter


def _direction(component: float) -> int:
    if component > 0:
        return 1
    if component < 0:
        return -1
    return 0


def _json_list(value: object) -> object:
    if isinstance(value, tuple):
        return [_json_list(item) for item in value]
    return value


def _tuple_tree(value: object) -> tuple:
    if not isinstance(value, list):
        raise TankSnapshotError("rng_state must use JSON arrays")
    return tuple(_tuple_tree(item) if isinstance(item, list) else item for item in value)


def _snapshot_mapping(value: object, name: str) -> MappingABC[str, object]:
    if not isinstance(value, MappingABC) or any(
        not isinstance(key, str) for key in value
    ):
        raise TankSnapshotError(f"{name} must be an object")
    return value


def _snapshot_sequence(value: object, name: str) -> Sequence[object]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TankSnapshotError(f"{name} must be an array")
    return value


def _snapshot_int(
    data: MappingABC[str, object],
    key: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TankSnapshotError(f"{key} must be an integer")
    if minimum is not None and value < minimum:
        raise TankSnapshotError(f"{key} is below its minimum")
    if maximum is not None and value > maximum:
        raise TankSnapshotError(f"{key} is above its maximum")
    return value


def _snapshot_number(
    data: MappingABC[str, object],
    key: str,
    minimum: float,
    maximum: float,
) -> float:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TankSnapshotError(f"{key} must be numeric")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise TankSnapshotError(f"{key} is outside its allowed range")
    return result


def _snapshot_coordinate(
    data: MappingABC[str, object], key: str, limit: float
) -> float:
    value = _snapshot_number(data, key, 0, limit)
    if value >= limit:
        raise TankSnapshotError(f"{key} must be inside the arena")
    return value


def _snapshot_enum(enum_type: type[Enum], value: object, name: str):
    if not isinstance(value, str):
        raise TankSnapshotError(f"{name} must be a string")
    try:
        return enum_type(value)
    except ValueError as exc:
        raise TankSnapshotError(f"invalid {name}") from exc


def _snapshot_player(value: object, name: str) -> str:
    if value not in {"red", "blue"}:
        raise TankSnapshotError(f"invalid {name}")
    return str(value)


__all__ = [
    "ARENA_COLS",
    "ARENA_ROWS",
    "Arena",
    "BulletState",
    "EngineEvent",
    "ItemType",
    "MatchPhase",
    "MineState",
    "PickupState",
    "PlayerCommand",
    "TankBattleEngine",
    "TankSnapshotError",
    "TankState",
    "Terrain",
]
