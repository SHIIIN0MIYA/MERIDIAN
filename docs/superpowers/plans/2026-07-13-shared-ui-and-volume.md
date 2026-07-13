# 公共 UI 与三级音量系统实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立可复用的像素 UI 组件，并把桌面音量入口升级为主音量、音乐、音效三滑块的展开回弹面板。

**Architecture:** `ui_components.py` 提供无游戏规则依赖的布局与绘制原语；`AudioManager` 统一计算最终增益；桌面只管理音量面板状态机。先迁移视觉基准覆盖页面，再逐步迁移其他页面。

**Tech Stack:** Python、Pygame、pytest、现有 persistence Schema 迁移。

## Global Constraints

- 保留八个世界独立配色与装饰。
- 中文必须使用内置 Fusion Pixel 字体、整数缩放和固定基线。
- 展开动画：完整约 420ms、精简约 240ms、关闭即时。
- 最终音乐增益=`master * music * scene`；音效增益=`master * sfx * event`。
- 不运行 PyInstaller，不推送远程。

---

### Task 1: 公共布局与文本安全组件

**Files:**
- Create: `meridian/ui_components.py`
- Create: `tests/test_ui_components.py`
- Modify: `meridian/arcade_common.py`

**Interfaces:**
- Produces: `fit_pixel_text(font, text, color, max_width, preferred_scale=2) -> Surface`
- Produces: `draw_pixel_panel(surface, rect, palette, border=5) -> Rect`
- Produces: `anchored_blit(surface, image, rect, anchor) -> Rect`

- [ ] **Step 1: 写失败测试**

```python
def test_fit_pixel_text_never_exceeds_width():
    result = fit_pixel_text(font, "玩家档案统计页面", WHITE, 90, preferred_scale=3)
    assert result.get_width() <= 90

def test_right_anchor_is_stable_for_different_text_widths():
    short = anchored_blit(screen, short_image, box, "midright")
    long = anchored_blit(screen, long_image, box, "midright")
    assert short.right == long.right == box.right
```

- [ ] **Step 2: 确认失败并实现最小组件**

`fit_pixel_text` 从首选整数 scale 逐级降到 1；仍超宽时返回裁剪错误而不是非整数缩放。`anchored_blit` 支持 `center`、`midleft`、`midright`。

- [ ] **Step 3: 让 `arcade_common.py` 使用公共面板和安全文字**

保持旧函数签名 `draw_arcade_frame`、`draw_arcade_button`、`draw_pause_overlay`，内部委托新组件，避免一次修改全部调用方。

- [ ] **Step 4: 验证并提交**

Run: `python -m pytest tests/test_ui_components.py tests/test_tank_battle.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/ui_components.py meridian/arcade_common.py tests/test_ui_components.py
git commit -m "refactor: add shared pixel UI primitives"
```

### Task 2: Schema 中增加主音量

**Files:**
- Modify: `meridian/persistence.py`
- Modify: `meridian/system.py`
- Test: `tests/test_persistence.py`

**Interfaces:**
- Produces: `settings.master_volume: float`，范围 `[0.0, 1.0]`

- [ ] **Step 1: 写迁移测试**

```python
def test_old_save_gains_master_volume_without_changing_category_levels():
    old = default_data(); old["settings"].pop("master_volume", None)
    old["settings"]["music_volume"] = 0.3
    old["settings"]["sfx_volume"] = 0.7
    migrated = migrate(old)
    assert migrated["settings"]["master_volume"] == 1.0
    assert migrated["settings"]["music_volume"] == 0.3
    assert migrated["settings"]["sfx_volume"] == 0.7
```

- [ ] **Step 2: 确认失败并升级 Schema**

在默认设置中加入 `master_volume: 1.0`，迁移通过深合并补值。`_apply_loaded_data()` 和 `_capture_data()` 双向同步该值。

- [ ] **Step 3: 验证并提交**

Run: `python -m pytest tests/test_persistence.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/persistence.py meridian/system.py tests/test_persistence.py
git commit -m "feat: persist master volume"
```

### Task 3: 统一混音公式

**Files:**
- Modify: `meridian/audio.py`
- Test: `tests/test_audio.py`
- Modify: `tests/test_smoke.py`

**Interfaces:**
- Produces: `AudioManager.set_master_volume(value: float) -> None`
- Produces: `AudioManager.effective_music_volume() -> float`
- Produces: `AudioManager.effective_sfx_volume(event_gain=1.0) -> float`

- [ ] **Step 1: 写公式边界测试**

```python
def test_effective_volume_multiplies_master_category_and_scene():
    audio.master_volume = 0.5; audio.music_volume = 0.8
    audio.sfx_volume = 0.6; audio.scene_volume_scale = 0.25
    assert audio.effective_music_volume() == pytest.approx(0.1)
    assert audio.effective_sfx_volume(0.4) == pytest.approx(0.12)
```

另测 mute 返回 0、setter 钳制范围、事件 channel 收到公式结果。

- [ ] **Step 2: 实现并替换所有直接音量计算**

```python
def effective_music_volume(self):
    if self.muted: return 0.0
    return self.master_volume * self.music_volume * self.scene_volume_scale

def effective_sfx_volume(self, event_gain=1.0):
    if self.muted: return 0.0
    return self.master_volume * self.sfx_volume * clamp(event_gain)
```

- [ ] **Step 3: 验证并提交**

Run: `python -m pytest tests/test_audio.py tests/test_smoke.py tests/test_tank_battle.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/audio.py tests/test_audio.py tests/test_smoke.py
git commit -m "refactor: route audio through master mix"
```

### Task 4: 展开回弹动画状态机

**Files:**
- Create: `meridian/volume_panel.py`
- Create: `tests/test_volume_panel.py`

**Interfaces:**
- Produces: `VolumePanelState(open, phase, elapsed_ms, drag_target)`
- Produces: `update_volume_panel(state, dt_ms, animation_level) -> VolumePanelGeometry`
- Produces: `VolumePanelGeometry(width_ratio, content_alpha, row_offsets, interactive_rect)`

- [ ] **Step 1: 写关键帧测试**

```python
def test_full_open_overshoots_then_settles():
    state = begin_open()
    peak = update_volume_panel(state, 340, "full")
    settled = update_volume_panel(state, 80, "full")
    assert 1.0 < peak.width_ratio <= 1.08
    assert settled.width_ratio == pytest.approx(1.0)

def test_off_mode_switches_immediately():
    assert update_volume_panel(begin_open(), 0, "off").width_ratio == 1.0
```

- [ ] **Step 2: 实现确定性曲线**

纯状态机不读取 `pygame.time`，只消费 `dt_ms`。完整使用 ease-out-back，精简降低 overshoot，关闭直接结束。关闭相位先降低内容 alpha，再收窄 width。

- [ ] **Step 3: 验证并提交**

Run: `python -m pytest tests/test_volume_panel.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/volume_panel.py tests/test_volume_panel.py
git commit -m "feat: add spring volume panel animation"
```

### Task 5: 桌面三滑块交互与绘制

**Files:**
- Modify: `meridian/shell_desktop.py`
- Modify: `meridian/localization.py`
- Test: `tests/test_desktop_volume.py`
- Modify: `tests/visual_scenes.py`

**Interfaces:**
- Consumes: `VolumePanelGeometry`、三个 AudioManager setter
- Produces: `_desktop_volume_rows() -> list[dict]`

- [ ] **Step 1: 写交互测试**

```python
def test_three_desktop_sliders_update_correct_audio_values(game):
    rows = game._desktop_volume_rows()
    assert [row["key"] for row in rows] == ["master", "music", "sfx"]
    drag_to(game, rows[0]["track"], 0.25)
    assert game.audio.master_volume == pytest.approx(0.25, abs=0.02)
```

另测右箭头关闭、翻页取消拖动、动画期间命中区域跟随 geometry、中英文标签。

- [ ] **Step 2: 实现绘制和事件路由**

删除旧单 BGM 滑块假设。扬声器按钮打开面板；每行调用对应 setter；百分比取当前值。关闭箭头只触发 closing phase，不瞬间隐藏。

- [ ] **Step 3: 固定组件关键帧**

在视觉场景测试中直接注入 elapsed，覆盖 collapsed、overshoot、settled、closing 四种 geometry；不新增全屏基准场景。

- [ ] **Step 4: 验证并提交**

Run: `python -m pytest tests/test_desktop_volume.py tests/test_visual_regression.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add meridian/shell_desktop.py meridian/localization.py tests/test_desktop_volume.py tests/visual_scenes.py
git commit -m "feat: expand desktop volume controls"
```

### Task 6: 迁移关键系统页面与完整回归

**Files:**
- Modify: `meridian/system.py`
- Modify: `meridian/tank_battle.py`
- Modify: `meridian/arcade_common.py`
- Test: `tests/test_ui_layout.py`
- Update explicitly: `tests/visual_baselines/en/*.png`, `tests/visual_baselines/zh_hans/*.png`

**Interfaces:**
- Consumes: 公共 UI 原语

- [ ] **Step 1: 写布局契约测试**

对设置、档案、成就墙、Lore、Tank 菜单/暂停/结算返回的关键 rect 做屏幕包含与互不重叠断言。

- [ ] **Step 2: 迁移页面**

保持页面功能和配色，只替换标题、面板、按钮、标签和滑块绘制。禁止顺带重构游戏规则。

- [ ] **Step 3: 显式更新并人工审查 24 张基准图**

Run: `python tools/update_visual_baselines.py --yes`  
检查中英文标题、基线、按钮状态、三滑块和 Tank HUD 后暂存。

- [ ] **Step 4: 完整验证与提交**

```powershell
python -m pytest tests/ -q -p no:cacheprovider
python -m ruff check MERIDIAN.py meridian tests tools
python -m compileall -q MERIDIAN.py meridian tests tools
git diff --check
```

```bash
git add meridian tests tests/visual_baselines
git commit -m "refactor: unify protected MERIDIAN interfaces"
```

