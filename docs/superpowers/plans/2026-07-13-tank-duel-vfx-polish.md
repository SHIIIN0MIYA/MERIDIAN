# Tank Duel 二轮视觉与道具特效实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 Tank Duel 增加清晰、分级且不影响规则判定的战斗反馈和八种独立道具表现。

**Architecture:** 纯逻辑引擎继续只产生事件；新 `tank_vfx.py` 将事件转换为确定性视觉状态；`TankBattleMixin` 负责绘制。完整、精简、关闭三个等级共享规则信息，仅调整装饰性效果。

**Tech Stack:** Python、Pygame、pytest、现有 TankBattleEngine 与公共 UI。

## Global Constraints

- 不修改既有伤害、碰撞、计分和道具规则。
- 所有效果由引擎事件驱动。
- 烟幕、EMP、穿甲数量等规则信息在关闭特效时仍可读。
- 八种道具必须使用独立像素图标，不用字母占位。
- 不运行 PyInstaller，不推送远程。

---

### Task 1: 确定性 VFX 状态模型

**Files:**
- Create: `meridian/tank_vfx.py`
- Create: `tests/test_tank_vfx.py`
- Modify: `meridian/tank_battle.py`

**Interfaces:**
- Produces: `TankVfxState`
- Produces: `consume_engine_events(state, events, effect_level, seed) -> None`
- Produces: `update_vfx(state, dt_ms) -> None`

- [ ] **Step 1: 写等级行为测试**

```python
def test_destroy_event_spawns_level_appropriate_effects():
    full = TankVfxState(); reduced = TankVfxState(); off = TankVfxState()
    event = EngineEvent("tank_destroyed", "blue", {"attacker": "red"})
    consume_engine_events(full, [event], "full", seed=7)
    consume_engine_events(reduced, [event], "reduced", seed=7)
    consume_engine_events(off, [event], "off", seed=7)
    assert len(full.particles) > len(reduced.particles) > len(off.particles)
    assert off.score_popups
```

- [ ] **Step 2: 实现状态与生命周期**

状态至少包含 muzzle flashes、shell cases、trails、particles、shock rings、score popups、respawn scans 和 item effects。所有随机数据来自传入 seed。

- [ ] **Step 3: 接入事件但不绘制**

`_handle_tank_engine_events` 在统计与音频之后调用 `consume_engine_events`。原有临时粒子迁移后删除重复实现。

- [ ] **Step 4: 验证并提交**

Run: `python -m pytest tests/test_tank_vfx.py tests/test_tank_battle.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/tank_vfx.py meridian/tank_battle.py tests/test_tank_vfx.py
git commit -m "refactor: add event-driven Tank Duel VFX"
```

### Task 2: 坦克、炮弹、受击、摧毁和重生绘制

**Files:**
- Modify: `meridian/tank_battle.py`
- Modify: `meridian/tank_vfx.py`
- Test: `tests/test_tank_vfx_render.py`

**Interfaces:**
- Produces: `draw_tank_vfx(game, arena, tile, state) -> None`

- [ ] **Step 1: 写绘制调用测试**

通过 mock `pygame.draw` 验证 full 绘制履带帧、后坐炮塔、冲击环和碎片；off 不绘制装饰粒子但仍绘制得分与重生警示。

- [ ] **Step 2: 实现分层顺序**

绘制顺序固定：地形 → 地雷/拾取物 → 炮弹尾迹 → 坦克履带/车体/炮塔 → 炮口/弹壳 → 受击/冲击环/碎片 → 烟幕 → 草丛 → HUD。穿甲炮弹使用金色核心。

- [ ] **Step 3: 固定事件截图**

为 full 模式建立非全屏组件测试 surface，固定 seed 后比较 muzzle、shield、piercing、destroy、respawn 五种事件图。

- [ ] **Step 4: 验证并提交**

Run: `python -m pytest tests/test_tank_vfx_render.py tests/test_tank_battle.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/tank_battle.py meridian/tank_vfx.py tests/test_tank_vfx_render.py
git commit -m "feat: animate Tank Duel combat feedback"
```

### Task 3: 八种像素图标与 HUD 状态

**Files:**
- Create: `meridian/tank_items_ui.py`
- Create: `tests/test_tank_items_ui.py`
- Modify: `meridian/tank_battle.py`

**Interfaces:**
- Produces: `draw_item_icon(surface, item, rect, palette, active=False) -> None`
- Produces: `item_status(engine, player_id) -> ItemStatus`

- [ ] **Step 1: 写图标唯一性测试**

```python
def test_all_eight_icons_have_unique_pixel_signatures():
    signatures = {item: icon_signature(render_icon(item)) for item in ItemType}
    assert len(set(signatures.values())) == 8
```

另测 HUD：EMP 返回剩余毫秒、穿甲返回剩余弹数、超速返回剩余时间、护盾返回 active。

- [ ] **Step 2: 实现纯代码像素图标**

图标分别表达十字扳手、护罩、履带闪电、地雷、EMP 波纹、穿甲弹头、烟云、分解门。不得使用单个拉丁字母作为主体。

- [ ] **Step 3: 替换地图拾取与 HUD 字母**

HUD 显示图标、翻译名称、F/Enter 提示和适用计时/计数。蓝方继续右锚定。

- [ ] **Step 4: 验证并提交**

Run: `python -m pytest tests/test_tank_items_ui.py tests/test_tank_battle.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/tank_items_ui.py meridian/tank_battle.py tests/test_tank_items_ui.py
git commit -m "feat: draw eight tactical item icons"
```

### Task 4: 八种道具专属特效与音效

**Files:**
- Modify: `meridian/tank_vfx.py`
- Modify: `meridian/tank_battle.py`
- Modify: `meridian/audio.py`
- Test: `tests/test_tank_item_effects.py`
- Test: `tests/test_audio.py`

**Interfaces:**
- Produces: `tank_repair`, `tank_shield_break`, `tank_overdrive`, `tank_mine_arm`, `tank_emp`, `tank_piercing`, `tank_smoke`, `tank_warp` 音效键

- [ ] **Step 1: 写事件到效果/音效映射测试**

对八个 `item_used` 事件断言产生唯一 VFX kind 和唯一 sound key；对 mute/master/sfx 公式断言 channel volume。

- [ ] **Step 2: 补充引擎表现事件数据**

若现有 `item_used` 数据不足，只允许增加表现所需 data（位置、item、remaining），不得改变规则。跃迁事件包含 origin/destination；盾破事件已有 attacker/source 时保留兼容。

- [ ] **Step 3: 实现视觉与程序化音效**

维修聚合、护盾破裂、超速残影、地雷脉冲、EMP 扫描、穿甲高亮、分层烟幕、跃迁拆解/重组。音效峰值限制在统一 event gain 内。

- [ ] **Step 4: 验证并提交**

Run: `python -m pytest tests/test_tank_item_effects.py tests/test_audio.py tests/test_tank_engine_items.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/tank_vfx.py meridian/tank_battle.py meridian/audio.py tests/test_tank_item_effects.py tests/test_audio.py
git commit -m "feat: distinguish Tank Duel item feedback"
```

### Task 5: 公共 UI 页面、基准更新与全量验证

**Files:**
- Modify: `meridian/tank_battle.py`
- Modify: `meridian/localization.py`
- Modify: `tests/visual_scenes.py`
- Update explicitly: Tank-related files under `tests/visual_baselines/`

**Interfaces:**
- Consumes: 公共 UI、八种图标、TankVfxState

- [ ] **Step 1: 迁移开始页和结算页**

开始页展示两套操作、3 分钟/3 HP/自动射击和八种道具入口。结算页展示胜者、比分、双方命中率、道具使用、重赛与菜单。所有动态文字使用安全布局。

- [ ] **Step 2: 更新固定视觉场景**

截图使用 reduced 效果；固定道具、EMP、穿甲、烟幕和结算数据。显式重建 24 图后只接受预期 Tank 与公共 UI 差异。

- [ ] **Step 3: 完整验证**

```powershell
python -m pytest tests/ -q -p no:cacheprovider
python -m ruff check MERIDIAN.py meridian tests tools
python -m compileall -q MERIDIAN.py meridian tests tools
git diff --check
```

- [ ] **Step 4: 提交**

```bash
git add meridian/tank_battle.py meridian/localization.py tests/visual_scenes.py tests/visual_baselines
git commit -m "feat: complete Tank Duel visual polish"
```

