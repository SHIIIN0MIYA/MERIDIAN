# 跨世界 Lore 与全局完成度实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 以成就、关键目标和 Lore 收集计算八界完成度，并在 25/50/75/100% 解锁跨世界主线档案。

**Architecture:** 新 `completion.py` 使用纯函数从存档事实推导进度，不持久化重复百分比；`lore.py` 注册跨世界条目；`system.py` 只负责展示与一次性解锁写入。

**Tech Stack:** Python、pytest、Pygame、现有 Schema/Lore/通知系统。

## Global Constraints

- 八个世界等权。
- 单世界权重：成就 40%、关键目标 35%、Lore 25%。
- 缺少旧存档证据时计零，不误授、不清档。
- 开发者模式不得写正式解锁。
- 100% 奖励仅改变表现，不阻止正常游戏。
- 不运行 PyInstaller，不推送远程。

---

### Task 1: 完成度领域模型与权重

**Files:**
- Create: `meridian/completion.py`
- Create: `tests/test_completion.py`

**Interfaces:**
- Produces: `WorldCompletion(achievement, objectives, lore, total)`
- Produces: `world_completion(game_id, save_data) -> WorldCompletion`
- Produces: `global_completion(save_data) -> int`

- [ ] **Step 1: 写权重测试**

```python
def test_world_completion_uses_confirmed_weights():
    score = combine_completion(achievement=100, objectives=100, lore=100)
    assert score == 100
    assert combine_completion(100, 0, 0) == 40
    assert combine_completion(0, 100, 0) == 35
    assert combine_completion(0, 0, 100) == 25
```

另测八界平均、截断到 0–100、缺字段为零。

- [ ] **Step 2: 实现不可变模型和纯函数**

使用 dataclass(frozen=True)，所有输入只读。total 由三部分加权并取整数；global 是八个 total 的整数平均。

- [ ] **Step 3: 验证并提交**

Run: `python -m pytest tests/test_completion.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/completion.py tests/test_completion.py
git commit -m "feat: calculate cross-world completion"
```

### Task 2: 八界关键目标定义与旧存档推导

**Files:**
- Modify: `meridian/completion.py`
- Modify only when evidence is unavailable: `meridian/persistence.py`
- Test: `tests/test_completion_objectives.py`

**Interfaces:**
- Produces: `Objective(id, title_key, achieved: Callable[[dict], bool])`
- Produces: `WORLD_OBJECTIVES: dict[str, tuple[Objective, ...]]`

- [ ] **Step 1: 写每界目标数量与边界测试**

每界定义 3–4 个目标。测试至少覆盖阈值前一单位和刚好达到阈值，例如 2048 的 511/512、Tank 的七/八种道具、Air 三种战役状态。

- [ ] **Step 2: 固定目标阈值**

```python
WORLD_OBJECTIVES = {
    "gomoku": (games_completed(1), black_wins(1), white_wins(1), total_wins(10)),
    "snake": (best_score(10), best_score(30), longest_length(25), longest_length(50)),
    "breakout": (levels_cleared(1), levels_cleared(5), levels_cleared(10), hard_clears(1)),
    "2048": (highest_tile(512), highest_tile(1024), highest_tile(2048)),
    "mines": (wins(1), mode_win("9x10"), mode_win("16x40")),
    "tetris": (highest_level(5), highest_level(10), lines_cleared(100), tetrises(10)),
    "air": (campaigns_completed(1), challenge_campaigns_completed(1), boss_rush_clears(1)),
    "tank": (matches_completed(1), wins(1), item_variety(8), sudden_wins(1)),
}
```

Snake 新增 `longest_length` 统计字段，因为现有存档只有分数，无法证明历史长度。旧存档默认零，不根据分数猜测长度。其余目标全部使用现有字段。每个目标在所在世界的 35% 关键目标权重中等分。

- [ ] **Step 3: 验证旧存档安全**

Run: `python -m pytest tests/test_completion_objectives.py tests/test_persistence.py -q -p no:cacheprovider`  
Expected: PASS。

- [ ] **Step 4: 提交**

```bash
git add meridian/completion.py meridian/persistence.py tests/test_completion_objectives.py tests/test_persistence.py
git commit -m "feat: define eight-world objectives"
```

### Task 3: 跨世界 Lore 与阈值解锁

**Files:**
- Modify: `meridian/lore.py`
- Modify: `meridian/system.py`
- Modify: `meridian/localization.py`
- Test: `tests/test_cross_world_lore.py`

**Interfaces:**
- Produces: `CROSS_WORLD_THRESHOLDS = ((25, id), (50, id), (75, id), (100, id))`
- Produces: `_unlock_completion_lore() -> list[str]`

- [ ] **Step 1: 写一次性解锁测试**

```python
def test_completion_threshold_unlocks_once(game):
    fake_completion(game, 50)
    first = game._unlock_completion_lore()
    second = game._unlock_completion_lore()
    assert first == ["resonance_25", "resonance_50"]
    assert second == []
```

另测 24/25、49/50、74/75、99/100 和 dev_mode 不写入。

- [ ] **Step 2: 编写四篇中英文档案**

每篇至少明确连接三个世界。100% 最终档案综合八界，不虚构玩家具体对局结果。使用 `register_device_lore` 或新增跨世界分类，ID 固定为 `resonance_25/50/75/100`。

- [ ] **Step 3: 接入通知与保存**

解锁只把新 ID 加入现有 `lore.unlocked_entries`，并使用现有通知队列。调用点位于正常统计/存档更新后，developer mode 直接返回空列表。

- [ ] **Step 4: 验证并提交**

Run: `python -m pytest tests/test_cross_world_lore.py tests/test_lore.py tests/test_localization.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/lore.py meridian/system.py meridian/localization.py tests/test_cross_world_lore.py
git commit -m "feat: unlock cross-world resonance lore"
```

### Task 4: 全局完成度与八界卡片界面

**Files:**
- Modify: `meridian/system.py`
- Modify: `meridian/localization.py`
- Create: `tests/test_completion_ui.py`
- Modify: `tests/visual_scenes.py`

**Interfaces:**
- Consumes: `world_completion()`、`global_completion()`、`WORLD_OBJECTIVES`
- Produces: `_completion_world_cards() -> list[dict]`

- [ ] **Step 1: 写卡片数据测试**

```python
def test_profile_exposes_eight_equal_world_cards(game):
    cards = game._completion_world_cards()
    assert [card["game_id"] for card in cards] == list(WORLD_IDS)
    assert all(set(card) >= {"total", "achievement", "objectives", "lore"} for card in cards)
```

- [ ] **Step 2: 实现档案页布局**

顶部显示全局像素进度条/环，下方八卡分页或网格。点击卡片打开目标清单；未完成目标显示本地化标题，锁定 Lore 只显示 `???`，不泄露正文。

- [ ] **Step 3: 更新档案截图场景**

固定一个 37% 存档状态，英文和中文都覆盖全局条、卡片和分解值。显式更新基准图并检查文本边界。

- [ ] **Step 4: 验证并提交**

Run: `python -m pytest tests/test_completion_ui.py tests/test_visual_regression.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/system.py meridian/localization.py tests/test_completion_ui.py tests/visual_scenes.py tests/visual_baselines
git commit -m "feat: show eight-world completion profile"
```

### Task 5: 100% 桌面变化与完整验收

**Files:**
- Modify: `meridian/shell_desktop.py`
- Modify: `meridian/system.py`
- Test: `tests/test_completion_unlocks.py`
- Update explicitly: desktop visual baselines
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: `global_completion(save_data)`
- Produces: `_completion_desktop_variant() -> "normal" | "resonant"`

- [ ] **Step 1: 写纯表现奖励测试**

```python
def test_resonant_desktop_requires_one_hundred_percent(game):
    fake_completion(game, 99); assert game._completion_desktop_variant() == "normal"
    fake_completion(game, 100); assert game._completion_desktop_variant() == "resonant"
```

并断言 100% 不改变任何 desktop button enabled 状态。

- [ ] **Step 2: 实现克制的共振变化**

只改变桌面背景细节、状态栏点缀或粒子色，不移动图标、不隐藏功能、不增加高频闪烁。Reduced 减少动态，Off 使用静态边框。

- [ ] **Step 3: 更新 Unreleased 与基准图**

CHANGELOG 的 `Unreleased` 记录截图系统、公共 UI/音量、Tank VFX、完成度与跨世界 Lore。显式更新桌面和档案基准。

- [ ] **Step 4: 完整验证与提交**

```powershell
python -m pytest tests/ -q -p no:cacheprovider
python -m ruff check MERIDIAN.py meridian tests tools
python -m compileall -q MERIDIAN.py meridian tests tools
git diff --check
git status --short --branch
```

```bash
git add meridian tests tests/visual_baselines CHANGELOG.md
git commit -m "feat: complete MERIDIAN resonance progression"
```
