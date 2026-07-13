# 中英文截图回归系统实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为十二个关键页面建立 24 张确定性中英文基准图和可诊断的像素差异测试。

**Architecture:** 独立视觉场景工厂负责构造固定 `Game` 状态；比较器负责尺寸、像素和差异图；显式更新脚本是唯一可写基准图的入口。测试不依赖桌面截图或人工输入。

**Tech Stack:** Python、pytest、Pygame；不新增图片处理依赖。

## Global Constraints

- 固定逻辑分辨率 `1280×720`、随机种子、时钟、电量、动画帧和语言。
- 基准图必须使用项目内置中文字体，禁止系统字体回退。
- 普通测试不得更新基准图。
- 首批严格限制为 12 场景 × 2 语言。
- 不运行 PyInstaller，不推送远程。

---

### Task 1: 视觉场景模型与环境冻结

**Files:**
- Create: `tests/visual_scenes.py`
- Create: `tests/test_visual_scenes.py`
- Modify: `tests/conftest.py`

**Interfaces:**
- Produces: `SCENE_NAMES: tuple[str, ...]`
- Produces: `build_scene(name: str, language: str) -> Game`
- Produces: `render_scene(name: str, language: str) -> pygame.Surface`

- [ ] **Step 1: 写场景清单失败测试**

```python
def test_visual_suite_has_exactly_twelve_named_scenes():
    assert SCENE_NAMES == (
        "desktop_page_1", "desktop_page_2", "system_settings",
        "profile_statistics", "achievement_wall", "lore_list",
        "tank_menu", "tank_controls", "tank_playing", "tank_paused",
        "tank_sudden_death", "tank_end",
    )
```

- [ ] **Step 2: 确认测试失败**

Run: `python -m pytest tests/test_visual_scenes.py -q -p no:cacheprovider`  
Expected: FAIL，模块不存在。

- [ ] **Step 3: 实现场景工厂骨架**

```python
def build_scene(name: str, language: str) -> Game:
    set_language(language)
    game = Game()
    game.anim_tick = 120
    game.transition_active = False
    game.desktop_particles.clear()
    game.screen_shake_enabled = False
    configure = SCENE_BUILDERS[name]
    configure(game)
    return game

def render_scene(name: str, language: str) -> pygame.Surface:
    game = build_scene(name, language)
    game.draw()
    return game.screen.copy()
```

通过 monkeypatch 固定桌面时间为 `12:34`、电量为 `88%`。场景构造后不得读取真实系统时间。

- [ ] **Step 4: 验证并提交**

Run: `python -m pytest tests/test_visual_scenes.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add tests/visual_scenes.py tests/test_visual_scenes.py tests/conftest.py
git commit -m "test: add deterministic visual scene factory"
```

### Task 2: 十二个场景的固定状态

**Files:**
- Modify: `tests/visual_scenes.py`
- Test: `tests/test_visual_scenes.py`

**Interfaces:**
- Consumes: `build_scene()`
- Produces: 每个场景的明确状态构造函数 `_scene_<name>(game: Game) -> None`

- [ ] **Step 1: 写状态断言**

```python
def test_tank_visual_states_are_not_random_defaults():
    playing = build_scene("tank_playing", "en")
    assert playing.state == playing.TANK_PLAYING
    assert playing.tank_engine.score == {"red": 2, "blue": 1}
    assert playing.tank_engine.tanks["red"].held_item is ItemType.PIERCING

    sudden = build_scene("tank_sudden_death", "zh_hans")
    assert sudden.tank_engine.phase is MatchPhase.SUDDEN_DEATH
```

- [ ] **Step 2: 确认断言失败**

Run: `python -m pytest tests/test_visual_scenes.py -q -p no:cacheprovider`  
Expected: FAIL，默认状态不符合固定值。

- [ ] **Step 3: 完成构造器**

桌面固定页码；设置固定三个音量值和完整动画；档案固定统计页；成就墙固定第一页和已解锁集合；Lore 固定第一分类。Tank 场景固定比分、HP、道具、炮弹、烟幕、暂停、骤死和结算数据。不得调用随机对局推进来“碰出”目标状态。

- [ ] **Step 4: 验证并提交**

Run: `python -m pytest tests/test_visual_scenes.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add tests/visual_scenes.py tests/test_visual_scenes.py
git commit -m "test: define visual regression scene states"
```

### Task 3: 像素比较器与差异输出

**Files:**
- Create: `tests/visual_compare.py`
- Create: `tests/test_visual_compare.py`

**Interfaces:**
- Produces: `compare_surfaces(actual, expected, tolerance=0.0005) -> VisualDiff`
- Produces: `VisualDiff(different_pixels, total_pixels, ratio, diff_surface)`

- [ ] **Step 1: 写比较边界测试**

```python
def test_compare_rejects_size_mismatch():
    with pytest.raises(ValueError, match="size mismatch"):
        compare_surfaces(pygame.Surface((10, 10)), pygame.Surface((11, 10)))

def test_compare_reports_one_changed_pixel():
    first = pygame.Surface((10, 10)); second = first.copy()
    second.set_at((2, 3), (255, 0, 0))
    diff = compare_surfaces(first, second, tolerance=0)
    assert diff.different_pixels == 1
    assert diff.ratio == pytest.approx(0.01)
```

- [ ] **Step 2: 确认失败并实现**

使用 `pygame.surfarray.array3d`（可用时）或锁定 surface 后逐像素比较。差异图保持相同尺寸：相同像素变暗，差异像素使用洋红色。

- [ ] **Step 3: 验证并提交**

Run: `python -m pytest tests/test_visual_compare.py -q -p no:cacheprovider`  
Expected: PASS。

```bash
git add tests/visual_compare.py tests/test_visual_compare.py
git commit -m "test: add visual pixel comparator"
```

### Task 4: 显式基准更新工具

**Files:**
- Create: `tools/update_visual_baselines.py`
- Create: `tests/test_visual_baseline_tool.py`
- Create: `tests/visual_baselines/en/.gitkeep`
- Create: `tests/visual_baselines/zh_hans/.gitkeep`

**Interfaces:**
- Produces: `write_baselines(root: Path) -> list[Path]`

- [ ] **Step 1: 写 24 文件测试**

```python
def test_update_tool_writes_exactly_twenty_four_pngs(tmp_path):
    paths = write_baselines(tmp_path)
    assert len(paths) == 24
    assert all(path.suffix == ".png" for path in paths)
```

- [ ] **Step 2: 实现显式工具**

```python
def write_baselines(root: Path) -> list[Path]:
    written = []
    for language in ("en", "zh_hans"):
        for scene in SCENE_NAMES:
            target = root / language / f"{scene}.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(render_scene(scene, language), target)
            written.append(target)
    return written
```

CLI 必须打印将被覆盖的目录并要求 `--yes`；测试直接调用纯函数。

- [ ] **Step 3: 验证、生成并人工检查**

Run: `python -m pytest tests/test_visual_baseline_tool.py -q -p no:cacheprovider`  
Run: `python tools/update_visual_baselines.py --yes`  
Expected: 写入 24 张图。逐张检查中英文、字体、边界和固定状态后才暂存。

- [ ] **Step 4: 提交**

```bash
git add tools/update_visual_baselines.py tests/test_visual_baseline_tool.py tests/visual_baselines
git commit -m "test: generate bilingual visual baselines"
```

### Task 5: 基准回归、边界断言与 CI

**Files:**
- Create: `tests/test_visual_regression.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`

**Interfaces:**
- Consumes: `render_scene()`、`compare_surfaces()`、24 张基准图

- [ ] **Step 1: 写参数化回归**

```python
@pytest.mark.parametrize("language", ("en", "zh_hans"))
@pytest.mark.parametrize("scene", SCENE_NAMES)
def test_visual_baseline(scene, language, tmp_path):
    actual = render_scene(scene, language)
    expected = pygame.image.load(BASELINES / language / f"{scene}.png")
    diff = compare_surfaces(actual, expected)
    if not diff.passed:
        pygame.image.save(actual, tmp_path / f"{language}-{scene}-actual.png")
        pygame.image.save(diff.diff_surface, tmp_path / f"{language}-{scene}-diff.png")
    assert diff.passed, f"{language}/{scene}: {diff.ratio:.6%} pixels differ"
```

- [ ] **Step 2: 增加 UI 边界断言**

对截图场景公开的标题、按钮和 HUD rect 断言 `screen.get_rect().contains(rect)`，并断言相邻文本矩形不相交。不能只依赖像素图。

- [ ] **Step 3: CI 与文档**

CI 在现有 pytest 后运行视觉测试；若失败，使用 `actions/upload-artifact@v4` 上传临时差异目录。README 说明基准更新命令和审核要求。

- [ ] **Step 4: 完整验证与提交**

```powershell
python -m pytest tests/ -q -p no:cacheprovider
python -m ruff check MERIDIAN.py meridian tests tools
python -m compileall -q MERIDIAN.py meridian tests tools
git diff --check
```

Expected: 全部通过。

```bash
git add tests/test_visual_regression.py .github/workflows/ci.yml README.md
git commit -m "test: enforce bilingual visual regression"
```
