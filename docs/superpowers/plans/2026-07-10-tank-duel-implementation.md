# TANK DUEL / 坦克对决 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 MERIDIAN 中交付一款支持八向移动、自动射击、道具争夺、安全重生、三分钟积分制和骤死加时的本地双人坦克对战游戏。

**Architecture:** `meridian/tank_engine.py` 是不依赖 Pygame 的确定性规则引擎；`meridian/tank_battle.py` 是输入、页面、绘制、音效和 MERIDIAN 接入层。引擎以固定时间步消费 `PlayerCommand` 并产生 `EngineEvent`，表现层不得复制胜负、碰撞或道具规则。

**Tech Stack:** Python 3.10+、Pygame 2.x、pytest、Ruff、现有 JSON Schema v4→v5 存档系统。

## Global Constraints

- 红方使用 `W/A/S/D` 和 `F`；蓝方使用方向键和 `Enter`。
- 支持八向移动；斜向速度必须归一化；同轴相反键以后按键为准，释放后回退到仍按下的先按键。
- 自动射击间隔 650ms，过载期间 430ms，每方最多同时存在 2 发炮弹。
- 每方 3 HP；普通受击保护 900ms；重生保护 1500ms；重生后 400ms 才恢复射击。
- 标准对局 180 秒；平分进入骤死；同时击毁在骤死中不得直接判胜。
- 首版只有一张左右镜像地图、四种单槽道具和 12 个成就。
- UI、按钮、像素画风、主旋律变调和中英双语必须与 MERIDIAN 现有内容一致。
- 所有测试必须设置临时 `MERIDIAN_SAVE_PATH`，不得读写真实用户存档。
- 未经用户明确要求，禁止运行 PyInstaller、`BUILD_EXE.bat` 或任何可执行文件打包命令。

## File Structure

- Create `meridian/tank_engine.py`: 纯规则、地图、实体、碰撞、计时、道具、重生、序列化。
- Create `meridian/tank_battle.py`: Pygame 输入顺序、页面、HUD、地图与实体绘制、事件特效。
- Create `tests/test_tank_engine_movement.py`: 地图、移动和输入命令测试。
- Create `tests/test_tank_engine_combat.py`: 炮弹、伤害、墙体和同时命中测试。
- Create `tests/test_tank_engine_items.py`: 四种道具、刷新、安全重生和比赛流程测试。
- Create `tests/test_tank_engine_persistence.py`: 引擎序列化、确定性和恢复测试。
- Create `tests/test_tank_battle.py`: Pygame 页面、双人输入、HUD 和按钮测试。
- Modify `tests/conftest.py`: 全测试套件存档隔离。
- Modify `meridian/app.py`: Mixin、状态分发、初始化、更新和绘制接入。
- Modify `meridian/shell_desktop.py`: 第二页桌面图标与打开动作。
- Modify `meridian/shell_transitions.py`: 坦克页面返回桌面的清理与过渡。
- Modify `meridian/persistence.py`: Schema v5 的 tank 统计和中断状态。
- Modify `meridian/system.py`: 状态统计、12 个成就、统计页和 8×6 成就墙分页。
- Modify `meridian/audio.py`: 五层坦克主旋律变调、坦克音效和暂停音量倍率。
- Modify `meridian/common.py`: 坦克竞技场像素调色常量。
- Modify `meridian/localization.py`: 界面、道具、统计与成就中文映射。
- Modify `meridian/lore.py`: `IRON ARENA / 钢铁斗场` 世界、序章和 Lore。
- Modify `tests/test_smoke.py`, `tests/test_persistence.py`, `tests/test_localization.py`, `tests/test_lore.py`: 系统级回归。
- Modify `README.md`: 第八款游戏、控制、测试文件和功能清单。

---

### Task 1: 隔离测试存档

**Files:**
- Modify: `tests/conftest.py:1-4`
- Create: `tests/test_test_environment.py`

**Interfaces:**
- Produces: 测试进程启动时已设置的 `MERIDIAN_SAVE_PATH: str`，供所有后续 `Game()` 实例使用。

- [ ] **Step 1: 写入会失败的隔离测试**

```python
from pathlib import Path
import os


def test_suite_uses_disposable_save_path():
    save_path = Path(os.environ["MERIDIAN_SAVE_PATH"])
    assert save_path.name == "save.json"
    assert "MERIDIAN" not in {part.upper() for part in save_path.parts}
```

- [ ] **Step 2: 验证测试先失败**

Run: `python -m pytest tests/test_test_environment.py -q -p no:cacheprovider`
Expected: FAIL，因为当前环境仍指向真实 `%APPDATA%/MERIDIAN` 或没有隔离变量。

- [ ] **Step 3: 在导入测试模块前创建临时存档目录**

```python
import atexit
import os
from pathlib import Path
import tempfile

_SAVE_DIR = tempfile.TemporaryDirectory(prefix="meridian-tests-")
atexit.register(_SAVE_DIR.cleanup)
os.environ["MERIDIAN_SAVE_PATH"] = str(Path(_SAVE_DIR.name) / "save.json")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
```

- [ ] **Step 4: 验证隔离测试与现有持久化测试**

Run: `python -m pytest tests/test_test_environment.py tests/test_persistence.py -q -p no:cacheprovider`
Expected: PASS，且 `%APPDATA%/MERIDIAN/save.json` 不被访问。

- [ ] **Step 5: 提交**

```bash
git add tests/conftest.py tests/test_test_environment.py
git commit -m "test: isolate Meridian saves"
```

### Task 2: 建立引擎数据模型、地图和八向移动

**Files:**
- Create: `meridian/tank_engine.py`
- Create: `tests/test_tank_engine_movement.py`

**Interfaces:**
- Produces: `PlayerCommand(move_x: int, move_y: int, use_item: bool = False)`。
- Produces: `TankBattleEngine(seed: int = 0)`、`update(dt_ms: int, commands: Mapping[str, PlayerCommand]) -> list[EngineEvent]`。
- Produces: `Terrain`, `ItemType`, `TankState`, `EngineEvent` 和地图常量 `ARENA_COLS=24`, `ARENA_ROWS=12`。

- [ ] **Step 1: 写地图对称、路线连通和斜向速度测试**

```python
import math
import pytest
from meridian.tank_engine import TankBattleEngine, PlayerCommand


def test_arena_is_horizontally_symmetric_and_spawns_are_open():
    engine = TankBattleEngine(seed=7)
    assert engine.arena.rows == [row[::-1] for row in engine.arena.rows]
    assert all(engine.arena.is_walkable(x, y) for x, y in engine.spawn_candidates)


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
```

- [ ] **Step 2: 验证测试先因模块不存在而失败**

Run: `python -m pytest tests/test_tank_engine_movement.py -q`
Expected: collection FAIL with `ModuleNotFoundError: meridian.tank_engine`。

- [ ] **Step 3: 实现公开类型和固定步进骨架**

```python
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

    @property
    def position(self) -> tuple[float, float]:
        return self.x, self.y


class TankBattleEngine:
    STEP_MS = 16
    MOVE_SPEED = 0.004

    def update(self, dt_ms, commands):
        self._accumulator_ms += max(0, dt_ms)
        events = []
        while self._accumulator_ms >= self.STEP_MS:
            events.extend(self._step(self.STEP_MS, commands))
            self._accumulator_ms -= self.STEP_MS
        return events
```

- [ ] **Step 4: 实现 24×12 镜像地图、AABB 墙体碰撞和归一化移动**

使用 `.` 空地、`B` 砖墙、`S` 钢墙、`G` 草丛编码地图。`_normalized_move()` 用 `math.hypot` 归一化非零向量；`_move_tanks_simultaneously()` 先计算双方候选位置，再对墙体和双方重叠进行对称拒绝，禁止按 red→blue 顺序产生偏置。

- [ ] **Step 5: 运行引擎移动测试**

Run: `python -m pytest tests/test_tank_engine_movement.py -q`
Expected: PASS，地图维度、镜像、连通、墙体阻挡和速度归一化全部通过。

- [ ] **Step 6: 提交**

```bash
git add meridian/tank_engine.py tests/test_tank_engine_movement.py
git commit -m "feat: add tank movement engine"
```

### Task 3: 炮弹、伤害和可破坏地形

**Files:**
- Modify: `meridian/tank_engine.py`
- Create: `tests/test_tank_engine_combat.py`

**Interfaces:**
- Consumes: `TankBattleEngine.update()`、`PlayerCommand`、`TankState`。
- Produces: `BulletState`；事件类型 `shot`, `bullet_clash`, `brick_hit`, `tank_hit`, `tank_destroyed`。

- [ ] **Step 1: 写自动射击、炮弹上限和同时伤害测试**

```python
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
```

- [ ] **Step 2: 验证测试先失败**

Run: `python -m pytest tests/test_tank_engine_combat.py -q`
Expected: FAIL，因为炮弹与伤害接口尚不存在。

- [ ] **Step 3: 实现自动射击和碰撞批处理**

```python
@dataclass
class BulletState:
    owner: str
    x: float
    y: float
    dx: float
    dy: float


def _resolve_damage_batch(self, hits):
    damage = {"red": 0, "blue": 0}
    for target, amount in hits:
        damage[target] += amount
    for target in ("red", "blue"):
        self._apply_damage(target, damage[target])
```

在每个固定步中依次执行：生成到期炮弹、移动全部炮弹、收集炮弹互撞、墙体碰撞和坦克命中、删除命中实体、批量结算伤害。砖墙命中后删除对应格；钢墙只删除炮弹；草丛不参与碰撞。

- [ ] **Step 4: 运行战斗测试与移动回归**

Run: `python -m pytest tests/test_tank_engine_movement.py tests/test_tank_engine_combat.py -q`
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add meridian/tank_engine.py tests/test_tank_engine_combat.py
git commit -m "feat: add tank combat rules"
```

### Task 4: 道具、比赛计时、骤死和安全重生

**Files:**
- Modify: `meridian/tank_engine.py`
- Create: `tests/test_tank_engine_items.py`

**Interfaces:**
- Produces: `PickupState`, `MineState`, `MatchPhase`。
- Produces: `use_item`, `pickup`, `mine_triggered`, `respawn`, `sudden_death`, `match_ended` 事件。
- Produces: `music_phase -> Literal["normal", "final", "sprint", "sudden"]`。

- [ ] **Step 1: 写四种道具、暂停和比赛流程测试**

```python
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


@pytest.mark.parametrize("item", list(ItemType))
def test_each_item_can_be_picked_up_and_consumed(item):
    engine = pickup_engine(item, player="red")
    events = engine.update(16, commands(red_use=True))
    assert engine.tanks["red"].held_item is None
    assert any(e.kind == "item_used" and e.data["item"] == item.value for e in events)


def test_pause_freezes_every_logic_clock():
    engine = TankBattleEngine(seed=3)
    before = engine.to_dict()
    engine.paused = True
    engine.update(5000, commands(red=(1, 0)))
    assert engine.to_dict() == before | {"paused": True}


def test_tied_regulation_enters_sudden_death_and_double_ko_continues():
    engine = TankBattleEngine(seed=3)
    engine.remaining_ms = 16
    engine.update(32, commands())
    assert engine.phase is MatchPhase.SUDDEN_DEATH
    engine.tanks["red"].hp = engine.tanks["blue"].hp = 1
    engine.bullets = [
        BulletState("blue", engine.tanks["red"].x, engine.tanks["red"].y, -1.0, 0.0),
        BulletState("red", engine.tanks["blue"].x, engine.tanks["blue"].y, 1.0, 0.0),
    ]
    engine.update(16, commands())
    assert engine.winner is None
```

- [ ] **Step 2: 验证测试先失败**

Run: `python -m pytest tests/test_tank_engine_items.py -q`
Expected: FAIL，因为道具与比赛阶段尚不存在。

- [ ] **Step 3: 实现道具和精确持续时间**

维修包满血时不消耗；护盾优先于 HP 吸收一次伤害并在 15000ms 后过期；过载维持 6000ms；每人至多一枚地雷，死亡时清除。刷新间隔使用引擎 RNG 在 `[12000, 18000]` 内抽取，四种类型等概率。

- [ ] **Step 4: 实现安全重生评分和阶段机**

```python
def _spawn_score(self, point, enemy):
    if self._spawn_is_blocked(point) or self._projectile_threat(point):
        return float("-inf")
    distance = math.dist(point, enemy.position)
    line_bonus = 0.0 if self.arena.has_line_of_sight(point, enemy.position) else 8.0
    exits = self.arena.open_neighbor_count(point)
    return distance + line_bonus + exits * 2.0
```

候选点最高分胜出；同分用引擎 RNG 选择。重生设置 1500ms 保护和 400ms 射击锁。180000ms 结束时比分不同则结束，相同则进入骤死并停止道具刷新。

- [ ] **Step 5: 运行前三组引擎测试**

Run: `python -m pytest tests/test_tank_engine_movement.py tests/test_tank_engine_combat.py tests/test_tank_engine_items.py -q`
Expected: PASS。

- [ ] **Step 6: 提交**

```bash
git add meridian/tank_engine.py tests/test_tank_engine_items.py
git commit -m "feat: add tank items and match flow"
```

### Task 5: 引擎存档和确定性恢复

**Files:**
- Modify: `meridian/tank_engine.py`
- Create: `tests/test_tank_engine_persistence.py`

**Interfaces:**
- Produces: `TankBattleEngine.to_dict() -> dict[str, object]`。
- Produces: `TankBattleEngine.from_dict(data: Mapping[str, object]) -> TankBattleEngine`。

- [ ] **Step 1: 写往返、非法存档和确定性测试**

```python
def progressed_engine(seed=11):
    engine = TankBattleEngine(seed=seed)
    for _ in range(40):
        engine.update(16, {
            "red": PlayerCommand(1, 1),
            "blue": PlayerCommand(-1, 0),
        })
    return engine


def scripted_commands():
    return [
        {"red": PlayerCommand(0, -1), "blue": PlayerCommand(1, 0)},
        {"red": PlayerCommand(1, 0, True), "blue": PlayerCommand()},
        {"red": PlayerCommand(), "blue": PlayerCommand(0, 1)},
    ] * 20


def test_round_trip_preserves_rules_but_clears_live_input():
    engine = progressed_engine(seed=11)
    restored = TankBattleEngine.from_dict(engine.to_dict())
    assert restored.to_dict() == engine.to_dict()
    before = restored.tanks["red"].position
    restored.update(16, {"red": PlayerCommand(), "blue": PlayerCommand()})
    assert restored.tanks["red"].position == before


def test_same_saved_state_and_commands_produce_same_events():
    left = progressed_engine(seed=11)
    right = TankBattleEngine.from_dict(left.to_dict())
    stream = scripted_commands()
    assert [left.update(16, c) for c in stream] == [right.update(16, c) for c in stream]


def test_invalid_snapshot_raises_tank_snapshot_error():
    with pytest.raises(TankSnapshotError):
        TankBattleEngine.from_dict({"version": 1, "tanks": []})
```

- [ ] **Step 2: 验证测试先失败**

Run: `python -m pytest tests/test_tank_engine_persistence.py -q`
Expected: FAIL，因为序列化接口尚不存在。

- [ ] **Step 3: 实现版本化快照**

快照包含地图、双方状态、炮弹、地雷、拾取物、比分、阶段、剩余时间、冷却、固定步累积量和 `random.Random.getstate()` 的 JSON 安全列表形式。`from_dict()` 校验版本、双方 ID、地图尺寸、数值范围和枚举值；活动按键不属于引擎快照。

- [ ] **Step 4: 运行全部纯引擎测试**

Run: `python -m pytest tests/test_tank_engine_*.py -q`
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add meridian/tank_engine.py tests/test_tank_engine_persistence.py
git commit -m "feat: persist tank matches"
```

### Task 6: Pygame 表现层、双人输入和一致 UI

**Files:**
- Create: `meridian/tank_battle.py`
- Modify: `meridian/common.py`
- Create: `tests/test_tank_battle.py`

**Interfaces:**
- Consumes: `TankBattleEngine`, `PlayerCommand`, `EngineEvent`。
- Produces: `TankBattleMixin` 的 `_init_tank_battle`, `_handle_tank_*_event`, `_update_tank_battle`, `_draw_tank_*`, `_capture_tank_run_state`, `_restore_tank_run_state`。

- [ ] **Step 1: 写后按优先、八向组合和页面绘制测试**

```python
def keydown(key):
    return pygame.event.Event(pygame.KEYDOWN, {"key": key})


def keyup(key):
    return pygame.event.Event(pygame.KEYUP, {"key": key})


def press(game, *keys):
    for key in keys:
        game._handle_tank_playing_event(keydown(key))


class SilentAudio:
    def play(self, *_args, **_kwargs):
        pass


@pytest.fixture
def game():
    pygame.init()
    harness = type("TankHarness", (TankBattleMixin,), {})()
    harness.screen = pygame.Surface((WINDOW_W, WINDOW_H))
    harness.font_menu_title = pygame.font.Font(None, 32)
    harness.font_status = pygame.font.Font(None, 18)
    harness.font_btn = pygame.font.Font(None, 20)
    harness.font_small = pygame.font.Font(None, 14)
    harness.audio = SilentAudio()
    harness.anim_tick = 0
    harness._init_tank_battle()
    return harness


def test_red_opposite_keys_use_latest_then_fall_back(game):
    game._handle_tank_playing_event(keydown(pygame.K_a))
    game._handle_tank_playing_event(keydown(pygame.K_d))
    assert game._tank_command("red").move_x == 1
    game._handle_tank_playing_event(keyup(pygame.K_d))
    assert game._tank_command("red").move_x == -1


def test_red_and_blue_can_move_diagonally_and_use_own_items(game):
    press(game, pygame.K_w, pygame.K_d, pygame.K_UP, pygame.K_LEFT)
    assert game._tank_command("red").move_y == -1
    assert game._tank_command("blue").move_x == -1
    game._handle_tank_playing_event(keydown(pygame.K_f))
    assert game._tank_command("red").use_item is True


@pytest.mark.parametrize("state", ["menu", "controls", "playing", "end"])
def test_tank_pages_draw_without_error(game, state):
    getattr(game, f"_draw_tank_{state}")()
```

- [ ] **Step 2: 验证测试先失败**

Run: `python -m pytest tests/test_tank_battle.py -q`
Expected: FAIL，因为 Mixin 尚不存在。

- [ ] **Step 3: 实现输入顺序和页面状态**

使用单调递增序号记录每个按键的按下顺序；每个轴从仍按下的候选键中选序号最大者。`F` 和 `Enter` 只在 KEYDOWN 边沿产生一次 `use_item=True`，下一帧清除。

- [ ] **Step 4: 实现地图、实体、草丛、HUD、菜单和结算绘制**

复用 `draw_arcade_frame`, `draw_arcade_button`, `handle_arcade_buttons`, `draw_pause_overlay`。使用整数坐标和 nearest-neighbor 缩放；草丛最后绘制；红蓝坦克同时通过颜色和炮塔纹样区分。HUD 固定为左红方、中倒计时与比分、右蓝方。

- [ ] **Step 5: 将引擎事件映射到粒子、震屏与音效名称**

映射固定为：`shot→tank_shot`、`bullet_clash→tank_clash`、`brick_hit→tank_brick`、`tank_hit→tank_hit`、`tank_destroyed→tank_explosion`、`pickup→tank_pickup`、`item_used→tank_item`、`sudden_death→tank_alarm`。

- [ ] **Step 6: 运行表现层和纯引擎测试**

Run: `python -m pytest tests/test_tank_battle.py tests/test_tank_engine_*.py -q`
Expected: PASS。

- [ ] **Step 7: 提交**

```bash
git add meridian/tank_battle.py meridian/common.py tests/test_tank_battle.py
git commit -m "feat: render Tank Duel"
```

### Task 7: 接入应用状态、桌面和 Schema v5

**Files:**
- Modify: `meridian/app.py:3-240`
- Modify: `meridian/shell_desktop.py:60-190`
- Modify: `meridian/shell_transitions.py:300-320`
- Modify: `meridian/persistence.py:12-194`
- Modify: `meridian/system.py:64-285`
- Modify: `tests/test_smoke.py`
- Modify: `tests/test_persistence.py`

**Interfaces:**
- Consumes: `TankBattleMixin` 和快照接口。
- Produces: `TANK_MENU`, `TANK_CONTROLS`, `TANK_PLAYING`, `TANK_END` 全状态链路。
- Produces: Schema v5 `statistics.tank`、`progress.tank`。

- [ ] **Step 1: 写系统接入和迁移失败测试**

```python
def test_tank_desktop_icon_and_dispatch_are_registered(game):
    actions = {item["action"] for page in game.desktop_pages for item in page}
    assert "open_tank" in actions
    for state in (game.TANK_MENU, game.TANK_CONTROLS, game.TANK_PLAYING, game.TANK_END):
        assert state in game._EVENT_DISPATCH
        assert state in game._DRAW_DISPATCH


def test_schema_four_adds_tank_without_resetting_other_games(manager):
    old = default_data()
    old["schema_version"] = 4
    old["statistics"]["snake"]["best_score"] = 17
    migrated = manager.migrate(old)
    assert migrated["schema_version"] == 5
    assert migrated["statistics"]["snake"]["best_score"] == 17
    assert migrated["progress"]["tank"] == {"run_active": False, "run_state": None}
```

- [ ] **Step 2: 验证测试先失败**

Run: `python -m pytest tests/test_smoke.py tests/test_persistence.py -q`
Expected: FAIL 于 tank 图标、状态或 Schema v5 断言。

- [ ] **Step 3: 接入 `Game` 和桌面**

导入并继承 `TankBattleMixin`；初始化时调用 `_init_tank_battle()`；四个状态分别接入事件、更新和绘制分发表。第二页注册 `TANK DUEL / open_tank`；桌面打开动作进入 `TANK_MENU`；返回桌面时清空按键顺序和一次性道具输入。

- [ ] **Step 4: 将存档升级到 Schema v5**

`default_statistics()["tank"]` 固定包含设计文档列出的统计键；`default_progress()["tank"]` 为中断状态；`migrate()` 在 `<5` 时只补入 tank 默认结构并保留所有已有游戏数据。`GAME_STATES["tank_playing"] = "tank"`，待恢复游戏循环加入 `tank`。

- [ ] **Step 5: 实现中断恢复失败降级**

`_restore_tank_run_state()` 捕获 `TankSnapshotError`，只将 `progress.tank.run_active=False` 和 `run_state=None`，保留 `statistics.tank` 与其他存档内容，并设置本地化提示键 `TANK SAVE COULD NOT BE RESTORED`。

- [ ] **Step 6: 运行系统测试**

Run: `python -m pytest tests/test_smoke.py tests/test_persistence.py tests/test_tank_battle.py -q`
Expected: PASS。

- [ ] **Step 7: 提交**

```bash
git add meridian/app.py meridian/shell_desktop.py meridian/shell_transitions.py meridian/persistence.py meridian/system.py tests/test_smoke.py tests/test_persistence.py
git commit -m "feat: integrate Tank Duel"
```

### Task 8: 统计、12 个成就和成就墙分页

**Files:**
- Modify: `meridian/system.py:12-60,287-347,686-870`
- Modify: `meridian/tank_battle.py`
- Modify: `tests/test_persistence.py`
- Modify: `tests/test_smoke.py`

**Interfaces:**
- Consumes: `_record_stat(game, key, amount, mode)`。
- Produces: 12 个 `tank_*` 成就定义；`achievement_wall_page: int`；每页 48 个徽章。

- [ ] **Step 1: 写成就唯一性、条件和分页测试**

```python
def test_tank_has_twelve_unique_achievements():
    tank = [a for a in ACHIEVEMENTS if a[3] == "tank"]
    assert len(tank) == 12
    assert len({a[0] for a in tank}) == 12


def test_achievement_wall_pages_48_then_12(game):
    game.achievement_wall_page = 0
    assert len(game._get_achievement_wall_badges()) == 48
    game.achievement_wall_page = 1
    assert len(game._get_achievement_wall_badges()) == 12


def test_tank_achievement_conditions_unlock_once(game):
    game.save_data["statistics"]["tank"]["matches_completed"] = 1
    game._check_achievements()
    game._check_achievements()
    assert list(game.save_data["achievements"]).count("tank_first_clash") == 1
```

- [ ] **Step 2: 验证测试先失败**

Run: `python -m pytest tests/test_persistence.py tests/test_smoke.py -q`
Expected: FAIL 于数量和分页断言。

- [ ] **Step 3: 添加 12 个成就和复合进度键**

成就 ID 与进度键固定映射如下，通用 `_achievement_progress()` 继续读取数值：

| ID | 统计键 | 目标 |
|---|---|---:|
| `tank_first_clash` | `matches_completed` | 1 |
| `tank_first_victory` | `wins` | 1 |
| `tank_sharpshooter` | `accurate_matches` | 1 |
| `tank_demolition` | `bricks_destroyed` | 100 |
| `tank_arsenal_master` | `item_variety` | 4 |
| `tank_iron_will` | `iron_will_kills` | 1 |
| `tank_sudden_victor` | `sudden_wins` | 1 |
| `tank_mine_expert` | `mine_hits` | 20 |
| `tank_shield_wall` | `shield_blocks` | 25 |
| `tank_overdrive_ace` | `overdrive_double_kills` | 1 |
| `tank_turnaround` | `comeback_wins` | 1 |
| `tank_arena_legend` | `matches_completed` | 50 |

比赛结束时，发射数不少于 10 且命中率不低于 50% 才增加 `accurate_matches`；`item_variety` 是四个 `*_uses > 0` 的数量；其余单局条件在事件发生时累计，重复检查不得重复解锁。

- [ ] **Step 4: 实现 8×6 分页而非压缩网格**

`_get_achievement_wall_badges()` 只切片 `ACHIEVEMENTS[page*48:(page+1)*48]`，徽章保存全局 index；左右键、鼠标 PREV/NEXT 按钮和页码 `1 / 2` 使用现有按钮质感。打开详情时禁止换页，关闭详情后才能切换。

- [ ] **Step 5: 运行统计、成就和系统回归**

Run: `python -m pytest tests/test_persistence.py tests/test_smoke.py tests/test_tank_battle.py -q`
Expected: PASS。

- [ ] **Step 6: 提交**

```bash
git add meridian/system.py meridian/tank_battle.py tests/test_persistence.py tests/test_smoke.py
git commit -m "feat: add Tank Duel achievements"
```

### Task 9: 动态音乐、音效、双语和 Lore

**Files:**
- Modify: `meridian/audio.py:87-249,252-372`
- Modify: `meridian/localization.py`
- Modify: `meridian/lore.py`
- Modify: `meridian/tank_battle.py`
- Modify: `tests/test_smoke.py`
- Modify: `tests/test_localization.py`
- Modify: `tests/test_lore.py`

**Interfaces:**
- Produces: `AudioManager.set_tank_phase(phase: str) -> None`。
- Produces: `AudioManager.set_scene_volume_scale(scale: float, fade_ms: int = 0) -> None`。
- Produces: tank 音轨 `tank_menu`, `tank_normal`, `tank_final`, `tank_sprint`, `tank_sudden`。

- [ ] **Step 1: 写音频层级、翻译和世界注册测试**

```python
def test_tank_music_layers_and_effects_exist(game):
    assert {"tank_menu", "tank_normal", "tank_final", "tank_sprint", "tank_sudden"} <= game.audio.tracks.keys()
    assert {"tank_shot", "tank_hit", "tank_explosion", "tank_pickup", "tank_alarm"} <= game.audio.effects.keys()


def test_tank_english_and_chinese_copy_is_complete():
    set_language("zh_hans")
    assert translate("TANK DUEL") == "坦克对决"
    assert translate("SUDDEN DEATH") == "骤死决胜"
    assert translate("REPAIR KIT") == "维修包"


def test_iron_arena_world_is_registered():
    world = get_world("tank")
    assert world["world_name_en"] == "IRON ARENA"
    assert world["world_name_zh"] == "钢铁斗场"
    assert 3 <= len(world["prologue_en"]) <= 5
```

- [ ] **Step 2: 验证测试先失败**

Run: `python -m pytest tests/test_smoke.py tests/test_localization.py tests/test_lore.py -q`
Expected: FAIL 于 tank 音轨、翻译或世界注册。

- [ ] **Step 3: 生成五层同旋律变调和专属音效**

五层使用同一 `THEME_MELODY` 的低音变调，beat_seconds 分别为菜单 `0.24`、普通 `0.18`、最后一分钟 `0.15`、最后冲刺 `0.125`、骤死 `0.105`。`sync_state("tank_playing")` 根据 `tank_phase` 选轨；阶段变化走现有 700ms 交叉淡化。暂停调用 `set_scene_volume_scale(0.6)`，恢复以 300ms 回到 `1.0`。

- [ ] **Step 4: 添加英文主键、中文映射、世界与 Lore**

注册游戏名、菜单、操作、道具、HUD、结算、统计、12 个成就标题与说明、恢复失败提示。`register_game_world("tank", ...)` 使用以下序章：

```python
prologue_en = [
    "THE IRON ARENA ACCEPTS TWO SIGNALS.",
    "RED AND BLUE WAKE BENEATH THE SAME SKY.",
    "NO SPAWN IS SAFE FOREVER.",
    "ONLY THE LAST SCORE SURVIVES THE BELL.",
]
prologue_zh = [
    "钢铁斗场接纳了两道信号。",
    "红与蓝在同一片天空下苏醒。",
    "没有任何出生点永远安全。",
    "钟声落下时，唯有比分得以留存。",
]
```

新增两条 Lore：`arena_origin`（`THE FIRST BELL / 初鸣之钟`，完成 1 局解锁）和 `moving_spawn`（`NO FIXED HOME / 无定之所`，完成 10 局解锁）。正文分别解释斗场计时器起源与动态重生协议，只引用 `matches_completed` 统计键。

- [ ] **Step 5: 运行音频、本地化和 Lore 测试**

Run: `python -m pytest tests/test_smoke.py tests/test_localization.py tests/test_lore.py tests/test_tank_battle.py -q`
Expected: PASS。

- [ ] **Step 6: 提交**

```bash
git add meridian/audio.py meridian/localization.py meridian/lore.py meridian/tank_battle.py tests/test_smoke.py tests/test_localization.py tests/test_lore.py
git commit -m "feat: polish Tank Duel presentation"
```

### Task 10: 全量集成、文档与验收

**Files:**
- Modify: `README.md`
- Modify: `.github/workflows/ci.yml` only if the current worktree version does not already run Ruff and pytest.
- Test: all files under `tests/`

**Interfaces:**
- Consumes: Tasks 1–9 的完整功能。
- Produces: 用户可从桌面完成进入、对战、暂停、恢复、加时、结算、重赛和返回桌面的闭环。

- [ ] **Step 1: 添加跨模块验收测试**

在 `tests/test_tank_battle.py` 添加一条完整的缩短计时对局：打开桌面图标、新对局、双方移动、拾取并使用道具、强制平分到时、进入骤死、非同时击毁结束、进入结算、点击 REMATCH。断言状态序列严格为 `TANK_MENU → TANK_PLAYING → TANK_END → TANK_PLAYING`。

- [ ] **Step 2: 运行新增坦克测试**

Run: `python -m pytest tests/test_tank_engine_*.py tests/test_tank_battle.py -q -p no:cacheprovider`
Expected: 全部 PASS。

- [ ] **Step 3: 更新 README**

把“七界”改为“八界”，新增 `TANK DUEL / 坦克对决 / IRON ARENA / 钢铁斗场` 行、红蓝控制表、道具说明、测试文件列表和成就总数 60。保留 Python 3.10–3.12 与 Pygame 2.x 要求。

- [ ] **Step 4: 运行完整验证**

Run: `python -m pytest tests/ -q -p no:cacheprovider`
Expected: 现有 74 个测试与所有新增测试全部 PASS。
Run: `python -m ruff check .`
Expected: `All checks passed!`
Run: `python -m compileall -q MERIDIAN.py meridian tests`
Expected: exit code 0。
Run: `git diff --check`
Expected: 无输出。

- [ ] **Step 5: 手工运行验收，不执行打包**

Run: `python MERIDIAN.py`
Expected: 桌面第二页显示 TANK DUEL；中英文均能完整完成一局；红蓝八向移动和后按优先正确；按钮、HUD、音乐层级、暂停音量、重生、道具、骤死和结算均符合规格。关闭程序后确认存档可恢复。不得运行 PyInstaller 或 `BUILD_EXE.bat`。

- [ ] **Step 6: 最终提交**

```bash
git add README.md .github/workflows/ci.yml tests meridian
git commit -m "feat: complete Tank Duel"
```

提交前必须用 `git diff --cached --name-status` 确认没有纳入与坦克对决无关的用户改动；如果工作区仍包含预先存在的修改，只暂存本计划实际触及且已审阅的 hunks。
