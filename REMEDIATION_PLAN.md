# MERIDIAN 整改计划

> 依据：对 `meridian/`（32 个模块 / 18,798 行）与 `tests/` 的全量阅读，加上可复现的实测验证。
> 基线：`pytest tests/ -q` → 147 passed；`ruff check meridian/ tests/` → All checks passed。
> 分支：`codex/repair-known-issues`（53 项未提交变更）。
> 每一项缺陷都标注了 `文件:行号`，可直接跳转核对。
> 状态：**决策已全部确认（2026-09-15），本计划可直接执行。** 见 [第 8 节 决策记录](#8-决策记录)。

---

## 目录

- [0. 整改原则与约定](#0-整改原则与约定)
- [1. 任务总览](#1-任务总览)
- [2. 阶段 0：建立验证基线](#2-阶段-0建立验证基线)
- [3. 阶段 1：存档与状态正确性（P0）](#3-阶段-1存档与状态正确性p0)
- [4. 阶段 2：玩家可见缺陷（P1）](#4-阶段-2玩家可见缺陷p1)
- [5. 阶段 3：本地化与健壮性（P2）](#5-阶段-3本地化与健壮性p2)
- [6. 阶段 4：结构与代码卫生（P3）](#6-阶段-4结构与代码卫生p3)
- [7. 明确不做的事](#7-明确不做的事)
- [8. 决策记录](#8-决策记录)
- [9. 回归验证清单](#9-回归验证清单)
- [10. 建议的提交序列](#10-建议的提交序列)

---

## 0. 整改原则与约定

**P1 先于 P2 先于 P3。** 阶段 1 修的是静默的数据错误（玩家不会报 bug，但存档会脏）。阶段 4 是结构性重构，风险最高、收益最慢，必须最后做，且每步单独提交、单独回归。

**每个 R-xx 独立一个提交。** 提交信息带编号，例如 `fix(gomoku): R-01 unify win counters`。便于回滚定位。

**缺陷修复必须带回归测试。** 本项目测试基础设施已经够用（`MERIDIAN_SAVE_PATH` 环境变量可重定向存档，`tests/test_tetris_mines_continue.py:26` 是现成范例），新增测试沿用同一套夹具写法，不要触碰真实存档。

**改动存档结构必须动 `SCHEMA_VERSION`。** 当前为 `5`（`persistence.py:14`）。涉及存档的 R-01、R-04 需要升到 `6` 并在 `SaveManager.migrate`（`persistence.py:212-238`）加分支。

**术语约定**：下文「快照」指 `save_data["progress"][game]["run_state"]`；「活引用」指未拷贝、与游戏内对象共享同一 Python 对象的数据。

---

## 1. 任务总览

| 编号 | 缺陷 | 位置 | 优先级 | 工作量 | 风险 |
|---|---|---|---|---|---|
| R-01 | 五子棋胜场双计数器，撤销后永久分叉 | `gomoku.py:684-692`、`system.py:203-205/326-328/439/443` | **P0** | S | 低 | **✅ 已完成** |
| R-02 | 扫雷计时器跨进程失效，可写入负数最快纪录 | `mines.py:100/139/155/225/363` | **P0** | S | 低 | **✅ 已完成** |
| R-03 | run_state 存/取均为活引用，会原地篡改存档 | `mines.py:133-143`、`gomoku.py:578-581`、`air_raid.py:325-354` | **P0** | S | 低 | **✅ 已完成** |
| R-04 | 恢复路径无维度校验；扫雷改尺寸后可 IndexError | `gomoku.py:578-581/628-637`、`mines.py:96-98/133-143`、`system.py:240-264/708-711` | **P0** | M | 低–中 | **✅ 已完成**（留下 R-04b） |
| R-05 | `wins_on_19` 用 `board_size` 而非棋盘真实尺寸 | `gomoku.py:563/566-568/735` | **P0** | S | 低 | **✅ 已完成** |
| R-06 | 空袭行动章节→关卡索引错位（**已复现**，第 2–8 章剧情回退 1–7 关） | `air_raid.py:114/128/220-222/1665-1668` | P1 | S | 低 |
| R-07 | 解锁横幅永不清除，每次结算重复出现 | `air_raid.py:926/1645` | P1 | S | 低 |
| R-08 | 坦克爆炸特效画在重生点 | `tank_engine.py:803-811`、`tank_battle.py:275-277` | P1 | S | 低 |
| R-09 | 坦克粒子速度单位错误，总位移约 2px | `tank_vfx.py:44-45/61-62` | P1 | S | 低 |
| R-10 | SMOKE 道具无任何游戏效果（纯装饰） | `tank_engine.py:136-152/644` | P1 | M | 中 |
| R-11 | 五子棋开局/继续的转场从不播放 | `gomoku.py:446-454/586`、`shell_transitions.py:33` | P1 | S | 低 |
| R-12 | ZH 键冲突：`RED`/`BLUE` 被坦克方标签覆盖 | `localization.py:282/288/626/627` | P2 | S | 低 |
| R-13 | 五子棋结算标题显示成统计标签「黑方胜场」 | `gomoku.py:1938`、`localization.py:252-253/701` | P2 | S | 低 |
| R-14 | 两套翻译注册机制；被校验的那套无人使用 | `localization.py:587-591/729` | P2 | M | 低 |
| R-15 | `_format_dynamic` 重复模式 + `^TIME` 过宽 | `localization.py:674/700/705` | P2 | S | 低 |
| R-16 | 字体无回退，缺文件即崩溃 | `localization.py:59-69` | P2 | S | 低 |
| R-17 | 启动阻塞 2.0s 合成 13 BGM + 56 音效 | `audio.py:371-374` | P2 | M | 中 |
| R-18 | `_SOUND_CACHE` 无失效入口 | `audio.py:15` | P2 | S | 低 |
| R-19 | `version_label()` 返回常量，版本号从不显示 | `version.py:4-5` | P2 | S | 低 |
| R-20 | 关卡数 `16` 硬编码 5 处 | `system.py:449`、`air_raid.py:900/1047/1322`、`developer.py:114-115` | P2 | S | 低 |
| R-21 | `_deep_merge` 接受类型替换；`save()` 迁移不在 try 内 | `persistence.py:167-176/266` | P2 | S | 低 |
| R-22 | 五子棋逐帧状态由主循环接管 | `app.py:426-537/496/535-537` | P3 | L | **高** |
| R-23 | 屏幕震动两份补丁，且未覆盖扫雷/2048 | `app.py:527-533`、`system.py:387-393` | P3 | S | 低 |
| R-24 | 五个街机游戏约 1400 行重复表现层 | `snake/mines/breakout/g2048/tetris` vs `arcade_common.py` | P3 | XL | 中 |
| R-25 | 死代码、乱码注释、BOM、缺失资源 | 见卡片 | P3 | M | 低 |
| R-26 | 12 个模块无测试；弱断言；缺陷被测试固化 | `tests/` | P2 | L | 低 |
| R-27 | 53 项未提交变更堆积 | 工作区 | P3 | S | 低 | **✅ 已完成** |

工作量：S ≈ 1 小时内，M ≈ 半天，L ≈ 1–2 天，XL ≈ 3 天以上。

---

## 2. 阶段 0：建立验证基线

在任何修复之前完成，否则后续改动无法证明「没有变坏」。

**R-27a 固化基线**
```bash
python -m pytest tests/ -q          # 期望 147 passed
python -m ruff check meridian/ tests/   # 期望 All checks passed
```
把这两个命令的结果（测试数、耗时）记入本文件末尾的「基线快照」小节。

**R-27b 建立存档往返夹具**

新增 `tests/_save_fixture.py`（或直接在 `tests/` 复用一个 `unittest.TestCase` 基类），提供：

- `make_game(**overrides)`：设置 `MERIDIAN_SAVE_PATH` 到临时文件、构造 `Game()`、注册清理。
- `simulate_restart(game)`：不重建 `Game` 对象，而是把 `_pending_run_states` 清空后重新 `_apply_loaded_data()` —— 用于验证「存档 → 恢复」路径。
- `assert_run_state_roundtrip(game, game_id)`：`_clear_run_state` → 重新加载 → 断言恢复出的状态与捕获值等价。

现有 `tests/test_tetris_mines_continue.py:16-41` 已经是可用的骨架，抽出即可。

**R-27c 提升测试速度（前置优化）** ✅ 已完成

实测澄清（原记录有误）：`Game()` 首次构造 **2.055s**，但**第 2、3 次只要 0.018s / 0.016s** —— 因为 `_cached()`（`audio.py:39-44`）把合成结果写进模块级 `_SOUND_CACHE`，那 2 秒是**每进程一次**，不是每次构造一次。所以原计划里「测试套件 7.3s 的绝大部分是反复构造 → 可提速到 1s 以内」的推断是错的：整套测试只构造一次 `Game` 的进程也只付 2s。

已实现的逃生开关：`audio.py` 的 `AudioManager.__init__` 在合成前短路。

```python
if os.environ.get("MERIDIAN_FAST_AUDIO") == "1":
    # Opt-out for test runs: skips the ~2s of procedural synthesis.
    self.enabled = False
    return
```

实测效果：单进程 `Game()` 构造 **2.055s → 0.011s**；测试套件 **6.57s → 4.57s**（正好省下那 2 秒）。4 个构造 `Game()` 的测试文件（`test_achievements`、`test_completion_lore`、`test_registration`、`test_tetris_mines_continue`）各自 `setdefault("MERIDIAN_FAST_AUDIO", "1")`。

安全性：所有音频公开入口都以 `self.enabled` 为守卫（`play` `audio.py:487`、`play_music` `:421`、`_update_crossfade` `:440`），`stop()` 遍历空的 `music_channels`，所以快速模式下全部退化为空操作；已逐个调用验证。`tracks`/`effects` 无外部读取点。

**这个开关与 R-17 的关系**：它解决了测试侧的成本，但**不能替代 R-17** —— 真实玩家启动时仍要等那 2 秒（窗口无响应）。R-17 的价值是消除启动卡顿，其测试提速收益已由本项覆盖。

---

## 3. 阶段 1：存档与状态正确性（P0）

### R-01 统一五子棋胜场计数器 ✅ 已完成

**决策**：D1=A（统计回滚、成就保持解锁）+ D2=B（不做迁移）。

**现状**（同一事实存了两遍）

| 路径 | 用途 | 写入点 | 读取点 |
|---|---|---|---|
| `self.black_wins` / `white_wins` / `draws` | 界面显示 | `gomoku.py:719-723` | `gomoku.py:1048-1049`、`1240`、`1968` |
| `records.gomoku.*` | 持久化（显示真值的载体） | `system.py:326-328` | `system.py:203-205` |
| `statistics.gomoku.*` | **成就与完成度真值** | `gomoku.py:730-734` | `system.py:439/443`、`completion.py:44/130-131` |

**根因**：`_do_undo`（`gomoku.py:684-692`）只回滚实例属性，不回滚 `statistics`。撤销一次胜局后，界面显示与成就进度永久不一致。

**已实施（as-built，与原计划有两处偏离）**

1. **`statistics.gomoku` 成为唯一真值来源**：`system.py` 的 `_apply_loaded_data` 改为从 `save_data["statistics"]["gomoku"]` 读取 `self.black_wins` / `white_wins` / `draws`。`_capture_data` 继续写 `records.gomoku.*` 并标注为 legacy mirror，**存档形状不变、不升 schema**（D2）。
2. **偏离一：没有给 `_record_stat` 加负向支持。** 原计划第 2 项被更彻底的方案取代——新增 `GomokuMixin._adjust_gomoku_outcome(winner, delta)`，它**直接写 statistics 并把实例属性从 statistics 派生**，然后调用 `_check_achievements()`：

   ```python
   stats = self.save_data["statistics"]["gomoku"]
   stats[key] = max(0, stats.get(key, 0) + delta)
   setattr(self, key, stats[key])          # 显示缓存镜像 statistics
   self._check_achievements()
   ```

   这比「两条路径各自 ±1」更强：显示值与统计值**由构造保证相等**，而不是靠两处调用保持同步。于是 `_record_stat` 无需改动，也就没有留下无调用者的负向分支。
3. **`_on_win` 与 `_do_undo` 都只经该入口**：`_on_win` 里原本重复的「实例属性 +1」与「`_record_stat`」两块合并为一次 `_adjust_gomoku_outcome(winner, +1)`；`_do_undo` 的三行条件递减改为一次 `_adjust_gomoku_outcome(was_win, -1)`。双向都走同一入口，漂移在结构上不可能再发生。
4. **不回收已解锁成就**（D1=A）：`_check_achievements` 保持只解锁、不回收。`_achievement_progress` 的 `min(value, target)`（`system.py:459`）使统计回落后**进度条回退、徽章保持点亮**。
5. **边界（有意为之）**：`games_completed` 与 `wins_on_19` **不在撤销回滚范围内**。前者有 `gomoku_stats_completed` 闩锁防止重复计数；后者保持「已达成即保留」，与 D1=A 的「成就一旦解锁不回滚」语义一致。`wins_on_19` 的判定本身由 R-05 修正。
6. **不做迁移**（D2=B）：`SCHEMA_VERSION` 未变。

**已落地的测试**（`tests/test_gomoku_counters.py`，11 个用例，用 R-27b 的夹具）

走子 → 五连 → 撤销后两侧一致；**胜 → 撤销 → 胜**（原缺陷直接回归）；白胜与和棋同理回滚；连续两次撤销不出现负数；计数器从 `statistics` 而非 `records` 读取（把 `records` 设成 99、`statistics` 设成 7，断言读到 7）；计数跨重启存活；`records` 镜像仍被写入；撤销后成就保持解锁而进度值归零；重胜不覆盖原始解锁时间戳。

**验证证据（关键）**：把 `meridian/gomoku.py` 与 `meridian/system.py` 临时回退到修复前，**11 个用例中 7 个失败**，其中直接回归用例报出 `AssertionError: 1 != 2`——界面显示 1、统计为 2，正是漂移本身；修复后 11 个全部通过。全量套件 163 passed，ruff 全通过。

**偏离二：未在 `Bug_Log.md` 增加条目。** 原计划第 4 项要求记录「撤销导致统计回落但成就保留」的语义。考虑到 `Development_Log/Bug_Log.md` 坚持只收录可核验条目、且由你维护，我把它留在本计划中而不擅自改动你的日志格式。

**风险**：实际为低。不涉及迁移，存档形状未变；唯一兼容性影响是旧档若已因历史撤销而分叉，切换读取来源后显示值会变为 `statistics` 一侧的值。

---

### R-02 扫雷计时改为增量累加 ✅ 已完成

**现状**：`mines_start_ticks = pygame.time.get_ticks()`（`mines.py:155`）被持久化（`:139`）并在新进程恢复（`:100`）。新进程 `get_ticks()` 从近 0 重启，而 `mines.py:363` 计算 `get_ticks() - start_ticks` → **负数**。

**后果链**
1. HUD 显示垃圾时间（`mines.py:514/652`）。
2. 胜局时 `mines.py:225` 得到负的 `elapsed_ms`，`:228` 的 `if old is None or self.mines_elapsed_ms < old` **会把负值写入最快纪录**，此后该难度永远无法刷新纪录。

**已实施（as-built）**

计时模型换成「权威 elapsed + 活动段基准」：

- `mines_elapsed_ms` 是权威值，也是**唯一被持久化**的计时字段。
- 新增两个**仅运行时**字段：`mines_timer_base`（当前活动段的起始 tick）与 `mines_resume_elapsed`（本段之前已累计的时间）。
- 新增 `_mines_elapsed_now()`：`mines_resume_elapsed + (get_ticks() - mines_timer_base)`，在 `_update_mines_visual_effects` 与 `_check_mines_win` **两处共用**（与 R-01 同样的思路：单一计算入口，避免两处公式漂移）。
- 恢复时把存档的 `elapsed_ms` 作为 `mines_resume_elapsed`，并把 `mines_timer_base` 重置为**当前进程**的 tick；`start_ticks` 不再持久化、不再读取。
- 胜局写入最快纪录前加 `self.mines_elapsed_ms >= 0` 守卫。

**两处与原计划的偏离**

1. **没有把负值夹到 0。** 原计划写「恢复时 `max(0, ...)`」。但夹到 0 会记录一个 **0 毫秒的伪纪录**，同样不可刷新，而且会让胜局路径的 `>= 0` 守卫变成死代码。改为保留负值、由守卫拦截记录写入，损坏的状态整体交给 R-04 的校验层拒绝——职责更清晰。
2. **`_capture_mines_run_state` 不做重算。** 一度想让捕获时刷新 elapsed，但那会让存档值依赖「捕获发生的时刻」，使「精确恢复」的既有测试变成时间相关。改为只持久化由更新循环保持新鲜的属性；`mines_elapsed_ms` 在 `MINES_PLAYING` 每帧更新，偏差上限一帧（≈16ms），对计时器无意义。

**同时修正的错误测试**：`tests/test_tetris_mines_continue.py:106` 原先写 `game.mines_start_ticks = 9876`，**把缺陷固化成了规格**（断言该 tick 原样往返）。已改为设置 `mines_elapsed_ms` / `mines_resume_elapsed`。

**已落地的测试**（`tests/test_mines_timer.py`，7 个用例）

旧式绝对 tick 存档恢复后不出现负计时；捕获结果不再含 `start_ticks`；恢复后计时继续前进；elapsed 跨重启存活；**负 elapsed 永不写入最快纪录**；正常快速获胜仍被记录；结算后计时冻结。

**验证证据（关键）**：把 `meridian/mines.py` 临时回退到修复前，两个行为级用例报出真实数值：

```
AssertionError: -899834 not greater than or equal to 5000
AssertionError: -899912 is not None : a negative elapsed must never be recorded as a best time
```

第一条即「恢复后计时变成约 −15 分钟」，第二条在 `mines_win` 为真的前提下证明**那个负值确实被写成了最快纪录**。全量套件 170 passed，ruff 全通过。

**风险**：低。`dev_game_speed` 会改 tick 速率（`app.py:553`），但本方案基于 tick 差值，不受影响。

---

### R-03 run_state 值语义（消除活引用）

> **✅ 已完成。** 严重性需要修正：修复前**无法构造出用户可见的故障** —— 因为离开对局会重写快照、`_clear_run_state` 会把快照与实时状态解绑，现有的「清理纪律」掩盖了别名危害。所以本项的价值是**消除潜在隐患并让 R-04 的校验成立**，而不是修复一个已发生的问题。

**已实施（as-built）**：三个游戏统一「捕获深拷贝、恢复深拷贝」。

- `mines.py`：`_capture_mines_run_state` 返回 `copy.deepcopy({...})`（原先直接返回 `self.mines_grid` / `mines_revealed` / `mines_flags` 的活引用）；`_start_mines_game` 恢复分支对三个棋盘 `copy.deepcopy`。
- `gomoku.py`：`_start_new_game` 恢复分支对 `grid` / `move_history` / `win_stones` 深拷贝（原先按引用赋值；捕获侧本来就有拷贝）。
- `air_raid.py`：`_capture_air_run_state` 整体 `copy.deepcopy`；`_begin_air_combat` 在拆包前对 `restore_state` 深拷贝一次（覆盖 `air_player` / `air_enemies` / `air_bullets` / `air_powerups` / `air_missiles` / `air_loadout` 六个容器）。
- 三个文件各加 `import copy`（项目此前无显式 copy 导入）。tank 本来就正确（`to_dict()`），未改动。

**已落地的测试**（`tests/test_run_state_values.py`，6 个用例）

mines 的捕获/恢复不是活引用、恢复后的对局与快照互不影响；gomoku 的捕获/恢复同理；air 的捕获不别名实时战斗状态。

**验证证据（关键）**：把三个源文件临时回退到修复前，**6 个用例全部失败**，且失败信息直接显示被注入的数值出现在快照里（`1, 42`、`7`、`999.0`）以及 `True is not false`。修复后全量套件 176 passed，ruff 全通过。

**现状**

| 游戏 | 捕获 | 恢复 | 判定 |
|---|---|---|---|
| gomoku | 有拷贝（`gomoku.py:630-636`） | **按引用赋值**（`gomoku.py:578-581`） | 恢复后 `self.board.grid` 即存档对象 |
| mines | **完全无拷贝**（`mines.py:135-137`） | **按引用赋值**（`mines.py:96-98`） | 存档即游戏内网格 |
| air | 返回活引用（`air_raid.py:325-354`） | 按引用（`air_raid.py:235-261`） | 同 mines |
| tank | `to_dict()` 深拷贝（`tank_battle.py:350`） | `from_dict` 重建 | **正确范例** |

**根因**：快照是引用而不是值。恢复后 `place_stone` / `_toggle_mines_flag` 等操作会**直接改写 `save_data`**，使内存存档与磁盘语义脱节，也让「捕获→比较→保存」的变更检测（`system.py:394-399`）失去意义。

**修改方案**：统一「捕获深拷贝、恢复深拷贝」。

1. 新增 `meridian/runstate.py`（或并入 `arcade_common.py`）：
   ```python
   def snapshot(value):   return copy.deepcopy(value)
   def restore(value):    return copy.deepcopy(value)
   ```
   配套一个 `validate_run_state(schema_id, data) -> bool | None`（供 R-04 使用）。
2. mines `_capture_mines_run_state`（`mines.py:133-143`）对 `grid`/`revealed`/`flags` 做深拷贝。
3. gomoku `_start_new_game` 恢复分支（`gomoku.py:578-581`）改为拷贝后再赋值（`grid = [row[:] for row in restore_state["grid"]]`）。
4. air 的捕获改为构造纯数据（坐标、血量、计分等标量/可序列化结构），而不是 `self.air_enemies` / `self.air_player` 对象；这同时是 R-06 修复的前置条件。
5. 对齐 tank：新增快照一律走 `to_dict()` 风格。

**验证**
- 新测试：`snapshot = game._capture_mines_run_state()` 后直接改 `game.mines_grid[0][0]`，断言 `snapshot["grid"][0][0]` 不变。
- 新测试：恢复后落子/翻格，断言 `game.save_data["progress"][...]["run_state"]` 不被改动。

**风险**：低。性能影响可忽略（16×16 布尔网格的深拷贝微不足道）。

---

### R-04 恢复路径维度校验与快照自描述
> **✅ 已完成（除 R-04b：提示的界面呈现）。**

**已实施（as-built）**

1. **新模块 `meridian/runstate.py`**：`RunStateVerdict`（RESUMABLE / COMPLETED / REJECTED）+ `validate()`。取代原计划「把 `_is_completed_run_state` 改成三态」的做法——抽成独立模块后可以脱离 `Game` 做纯单元测试，覆盖畸形输入的矩阵。
2. **快照自描述**：`format` + `size`/`board_count` + `mines_count` 只加在 gomoku 与 mines 上。**偏离原计划**（原写「所有 run_state」）：其余四个游戏没有尺寸依赖，加一个无人读取的字段只是无谓改动；将来真要收紧时再连同校验一起加。tank 不在此列——它已有 155 行的 `TankSnapshotError` 校验。
3. **三项校验**：快照内部自洽（网格方正、与行数一致、元素类型正确、`mines_count` 与网格中 `-1` 的个数相符）；**与当前设置一致**（见下）；已完成/无内容的状态归入 `COMPLETED` 静默清理而非报错（「未落一子的棋局」与「已覆盖地雷」都属于此）。`validate()` 对垃圾输入永不抛异常。
4. **失败降级**：`REJECTED` → `_drop_run_state()` 清 `run_active`/`run_state`，并设 `restore_notice`。tank 继续走自己的 `tank_restore_notice`，但两者由同一事实驱动。
5. **设置页交互**：改尺寸/改模式会丢弃该游戏未完成的运行状态。

**实施中发现的漏洞（原计划未覆盖）**

原计划只要求「校验快照结构」，我最初也只做了**内部自洽**检查——但用旧代码复现时发现真实崩溃路径是**跨会话**的：

```
存档：9x9 网格，run_active = True
玩家：把模式改成 16x16 / 40
重载：mines_size = 16，而存档里仍是 9x9 —— 旧代码接受它
恢复后 reveal(14,14) → IndexError: list index out of range
```

快照自身完全自洽，问题在于它与**当前设置**不一致。因此补上了 `expected_size` / `expected_count` 参数，由 `_apply_loaded_data` 传入 `self.board_size` / `self.mines_size` / `self.mines_count`；同时修了一个连带的坑：设置页结尾的 `_save_now()` 会**重新捕获**刚丢掉的运行状态，所以丢弃必须延后到那次保存之后，且用 `_clear_run_state`（带捕获抑制）而非纯内存的 `_drop_run_state`。

**已落地的测试**（`tests/test_run_state_validation.py`，42 个用例）

纯校验矩阵（gomoku 12 + mines 9 + 健壮性 4）、真实加载路径 6、设置页交互 3、设置一致性 5、跨会话 4。包括：19 路快照载入 15 路设置被拒绝；参差网格不抛异常；已完成状态静默清理**不**产生提示；健康快照仍能恢复（防止校验过严）；僵尸输入永不抛异常。

**验证证据**：`runstate.py` 是新模块，回退它会让整个测试文件 `ModuleNotFoundError`，所以第 4 项的「回退验证」改用一段临时脚本直接跑旧代码，实测输出：

```
(a) gomoku 19x19 快照 + 15x15 设置：offered for restore? True
    board.board_count = 15 | len(grid) = 19   ← 第 15-18 行悬挂在棋盘之外
(b) mines 9x9 快照 + 16x16 模式：offered for restore? True
    reveal(14,14) → IndexError: list index out of range
```

全量套件 **221 passed**，ruff 全通过。

**未完成：R-04b（提示的界面呈现）** —— `restore_notice` 目前只被设置、尚未渲染（只有 tank 的既有界面会显示它）。这不构成回归：修复前的行为是**崩溃或静默错位**，现在至少是安全拒绝；而「继续」按钮不再出现本身也是可见信号。渲染一处通用提示是独立的小改动。


**决策**：D2=B（不做迁移）——**旧 `run_state` 一律拒绝，不补字段、不迁移**。这使本项从「L / 中风险」降为「M / 低–中风险」。

**现状与后果**

1. 五子棋快照**不含棋盘尺寸**（`gomoku.py:628-637`），恢复时用 `[...]` 直接索引（`:578-581`，同函数内其他字段却用 `.get()`）→ 19×19 的 grid 可被装进 15×15 的 `Board`。
2. 扫雷快照**不含 size/count**（`mines.py:133-143`），恢复同样直接索引（`:96-98`）。
3. 设置页可在对局中改尺寸：`system.py:679-684`（五子棋有「无子才重建」守卫）与 `system.py:708-711`（扫雷**完全不重建棋盘**）。
4. 于是：在扫雷对局中把尺寸从 16×16 改成 9×9 → `self.mines_size` 变 9 而 `self.mines_grid` 仍是 16×16 → 下次进入时 `_reveal_mines_cell`（`mines.py:171-183`）按 `range(self.mines_size)` 循环 → **IndexError**。

**修改方案**

1. **快照自描述**：所有 `run_state` 顶层加入 `"format": 1` 与 `"size"`（五子棋另加 `"count"`/`"board_count"`，扫雷加 `"mines_count"`）。air 加入 `"level"`/`"mode"`。
2. **统一校验层**：把 `SystemMixin._is_completed_run_state`（`system.py:240-264`）从返回 `bool` 改造成返回三态：
   ```python
   class RunStateVerdict(Enum):
       RESUMABLE = "resumable"
       COMPLETED = "completed"     # 已结束，应清理
       REJECTED  = "rejected"      # 结构损坏，放弃恢复
   ```
   校验项：尺寸匹配、行/列数一致、元素类型正确、`revealed` 与 `grid` 同形、`-1` 值域合法。
3. **失败降级**（对齐 tank 的既有做法 `system.py:228-236`）：`REJECTED` 时清 `run_active`/`run_state`，并设置用户可见提示。复用 tank 的 `tank_restore_notice` 模式，推广为 `self.restore_notice`（字符串或 `None`）。
4. **设置页交互**：改尺寸时若该游戏存在未完成对局，明确清空该局并提示（不要静默保留错配状态）。扫雷的 `cycle_mines`（`system.py:708-711`）需要补上清空逻辑。

**验证**（4 个损坏用例 + 2 个交互用例）
- 尺寸不匹配、行数不齐、元素类型错误（字符串代替 `-1`）、`grid` 与 `revealed` 长度不一致 → 均不抛异常，`run_active` 被清除，提示被设置。
- 扫雷对局中改尺寸后进入菜单 → 不再出现「继续」，或「继续」被拒绝并提示。
- 五子棋 19 路快照载入 15 路配置 → 被拒绝而非静默错位。

**风险**：低–中。触及三个游戏的恢复路径 + 设置页交互，但按 D2=B **不需要迁移**：旧快照没有 `format` 字段，会直接落入 `REJECTED` 分支——这恰好就是 B 想要的降级行为，唯一的代价是旧档玩家丢失一局未完成的对局（不含任何统计与成就）。

---

### R-05 `wins_on_19` 判定改用棋盘真实尺寸

> **✅ 已完成。** 单行修正：`_on_win` 的判定从 `self.board_size == 19` 改为 `self.board.board_count == 19`。理由：`board_size` 是**设置偏好**，作用于下一局；它可以在对局中被修改而棋盘不重建（`gomoku.py` 的 `settings_size_*` 分支只在「无子且未分胜负」时重建棋盘）。因此用设置值判定本局是否 19 路是错误的。

**已落地的测试**（`tests/test_gomoku_board_size.py`，3 个用例）：15 路对局中把设置改成 19 后赢下，断言 `wins_on_19` 未增加且成就未解锁；真正的 19 路胜利仍然授予成就；13 路胜利不计入。

**验证证据（关键）**：把 `meridian/gomoku.py` 临时回退到修复前，核心用例报出 `AssertionError: 1 != 0 : a 15x15 win must not count towards the 19x19 statistic` —— 即旧代码确实把 15×15 的胜利计入了 19 路统计。修复后全量套件通过。

**未改动（有意）**：设置页改尺寸时仍只更新偏好、不重建进行中的棋盘，也不清空对局。这一交互归 R-04（改尺寸时应明确清空未完成对局并提示）。

**现状**：`_handle_settings_event` 无条件写 `self.board_size`（`gomoku.py:563`），只在「无子且未分胜负」时重建棋盘（`:566-568`）；而 `_on_win` 用 `self.board_size == 19` 判定（`gomoku.py:735`）。

**后果**：15 路对局中把设置改成 19 路，赢下后**错误地获得 `gomoku_19_win` 成就**。

**修改方案**：判定改用 `self.board.board_count`（棋盘自身尺寸，唯一权威）。R-04 落地后 `board_size` 与 `board.board_count` 应在所有时机保持一致，可在 `_handle_settings_event` 增加一致性断言。

**验证**：新测试 — 15 路对局 → 设置改成 19 → 赢下 → 断言 `statistics.gomoku.wins_on_19` 未增加、成就未解锁。

**风险**：低。

---

## 4. 阶段 2：玩家可见缺陷（P1）

### R-06 空袭行动章节→关卡索引错位

> **状态：已复现并已定论。** 复现脚本：`tools/repro_r06_air_chapter.py`（`python tools/repro_r06_air_chapter.py`，退出码 1 表示缺陷存在）。语义问题（原 Q2）已通过数据验证解答，见下方「定论」。

**现状**：`_check_air_chapter_story` 把 0 起的**章节索引**存进 `self._pending_brief_level`（`air_raid.py:128`），而 `_handle_air_story_event` 把它当**关卡号**喂回 `_prepare_air_level()`（`air_raid.py:1665-1668`）。于是剧情结束后进入的是 `AIR_LEVELS[章节号]`，而不是被中断的那一关。

**精确机制**：`_prepare_air_level(level)` 在剧情触发时**提前返回**（`air_raid.py:221-222`），此时 `self.air_level` 尚未被赋值（赋值在 `:223`，位于 return 之后）。正确做法是把入参 `level` 原样存下来，而不是存派生出的 `chapter_index`。

**实测影响**（`tools/repro_r06_air_chapter.py`）

| 剧情 | 应进入 | 实际进入 | 偏移 |
|---|---|---|---|
| 第 1 章 | L00 COAST WATCH / MISSION | L00 同 | 正确（纯属巧合，章节索引与首关索引都是 0） |
| 第 2 章 | L02 IRON CLOUD / MISSION | L01 WATCHTOWER / BOSS | −1 |
| 第 3 章 | L04 NIGHT VECTOR / MISSION | L02 IRON CLOUD / MISSION | −2 |
| 第 4 章 | L06 RED SQUALL / MISSION | L03 TEMPEST / BOSS | −3 |
| 第 5 章 | L08 SKY FORT / MISSION | L04 NIGHT VECTOR / MISSION | −4 |
| 第 6 章 | L10 DEEP STATIC / MISSION | L05 BULWARK / BOSS | −5 |
| 第 7 章 | L12 BLACK AURORA / MISSION | L06 RED SQUALL / MISSION | −6 |
| 第 8 章 | L14 LAST HORIZON / MISSION | L07 CHOIR / BOSS | −7 |

偏移量恰为 `−(章节号 − 1)`：**越深入战役，被扔回得越远**。第 8 章剧情会把玩家扔回第 4 章的 Boss。

**Boss Rush 变体（更严重，但仅经开发者面板解锁时可复现）**：Boss Rush 的每一关都是 Boss 关卡（L01/03/05/07/09/11/13/15），且走同一个剧情门（`_start_air_boss_rush` `air_raid.py:203-210`、`_choose_air_supply` `:974-983`）。8 个阶段**全部被重定向**，其中 4 个直接落到普通任务而非 Boss：

| 阶段 | 请求 | 实际 |
|---|---|---|
| 0 | L01 WATCHTOWER / BOSS | L00 COAST WATCH / **MISSION** |
| 1 | L03 TEMPEST / BOSS | L01 WATCHTOWER / BOSS |
| 2 | L05 BULWARK / BOSS | L02 IRON CLOUD / **MISSION** |
| … | … | … |

**可达性说明（诚实边界）**：正常玩家完成标准战役时，8 个章节剧情都会在途中被标记已读，因此经正常途径解锁的 Boss Rush **不受影响**。此变体只在用开发者面板 `unlock`（`developer.py:111-118`，直接置 `challenge_unlocked = True` 而不标记剧情已读）后才出现。**不要把它写成玩家可复现的缺陷**，但它证明了缺陷是「数据语义错配」而非「一处 if 写错」。

**定论：原 Q2 的答案**

数据验证（脚本 Probe B）表明：正常战役中，剧情门**只在每章的第一关（偶数关卡）触发**，从不落在 Boss 关卡上。因此「该章的第一关」与「被中断的那一关」**是同一关** —— 两个候选方案重合，语义问题消失。

于是修复不应新增 `_level_index_for_chapter()` 这类派生计算，而应**把入参 `level` 原样传递**：

```python
# air_raid.py:114  让检查函数记住实际要启动的关卡
def _check_air_chapter_story(self, chapter_index, level):
    ...
    self._pending_brief_level = level          # 原来是 chapter_index
    return True

# air_raid.py:220-221  调用处透传
chapter_index = AIR_LEVELS[level]["chapter"] - 1
if self._check_air_chapter_story(chapter_index, level):
    return

# air_raid.py:1665-1668  消费处保持不变（它本来就是对的）
```

**附带发现**：`_handle_air_story_event`（`air_raid.py:1662-1671`）把 `K_ESCAPE` 与 `K_RETURN`/`K_SPACE` 放在同一分支，因此**在章节剧情页按 ESC 不会退回菜单，而是直接开始该关**。若希望 ESC 可放弃，需把 ESC 单独分出。另：`archive_index` 的键盘分支（`:1672-1689`）被前面的 `return` 遮蔽，键盘无法在剧情档案里翻页（鼠标路径正常）。

**修改方案**

1. 按上述三处改动透传 `level`（这是最小且语义正确的修法）。
2. 可选：把 ESC 从「开始关卡」分支中拆出，改为返回菜单。
3. 顺带修 `archive_index` 键盘分支的不可达问题。

**验证**
- 在 `tools/repro_r06_air_chapter.py` 通过后（退出码 0），把 Probe A/B 的逻辑固化为单元测试：对第 1–8 章分别触发剧情，断言恢复关卡 == 请求关卡。
- 新增 Boss Rush 回归测试：断言 8 个阶段实际进入的关卡都是 Boss 关卡。

**风险**：低（定论后不再是「中」）。改动集中在 `air_raid` 的剧情门，透传一个参数即可；`progress["run_level"]` 不受影响。

---

### R-07 解锁横幅一次性语义

**现状**：`air_challenge_unlocked_notice` 在 `air_raid.py:926` 置位后**从不复位**，结算页在 `:1645` 渲染 → 「CHALLENGE CAMPAIGN + BOSS RUSH UNLOCKED」在**此后每一次结算页重复出现**，包括失败结算。

**决策**：已选 **(b) frame 计数自动清除**（与 `achievement_notifications` 同模式，保证玩家看得见）。

**修改方案**

1. 新增 `air_unlock_notice_frames` 计数器，置位时同时设 `air_challenge_unlocked_notice = True` 与帧数。
2. 在 `AIR_END` 的更新路径递减帧数；归零时复位标志与计数器。
3. 渲染处（`air_raid.py:1645`）只判断标志，不负责清除（把状态变更移出绘制代码——本项目多处违反这一点，见 R-08 的同类问题）。

**验证**：新测试 — 连续两次结算，断言第二次不渲染该横幅。

**风险**：低。

---

### R-08 坦克爆炸坐标改由事件携带

**现状**：`_resolve_damage_batch`（`tank_engine.py:798-811`）在同一步内先发 `tank_destroyed`，紧接着在 `:810` 调用 `_respawn_players(destroyed)` **移动了坦克**。`tank_battle.py:275-277` 才用 `data.setdefault("x", tank.x)` 从坦克**当前（已重生）位置**回填坐标 → 死亡爆炸画在重生点。

**修改方案**：让引擎事件自描述。引擎在发出 `tank_destroyed` 时已知道死亡瞬间的位置，直接写进 `data`：

```python
events.append(EngineEvent("tank_destroyed", target,
                          {"attacker": attacker, "x": victim.x, "y": victim.y}))
```

`tank_battle.py:275-277` 的 `setdefault` 回填保留（对没有坐标的事件仍是兜底），但不再被依赖。这条修改同时消除了同类隐患（任何「事件发出后实体被移动」的场景）。

**验证**：新测试 — 断言 `tank_destroyed` 的 `data` 含 `x`/`y`，且等于死亡瞬间坐标而非重生点（可对比 `_respawn_players` 执行后的位置）。

**风险**：低。

---

### R-09 坦克粒子速度单位

**现状**：`tank_vfx.py:44-45` 设置 `vx = cos(angle) * .004`，而 `update_vfx`（`:61-62`）按**毫秒**积分：`effect["x"] += vx * dt`。粒子生命 520ms → 总位移约 **2.08px**，爆炸特效实质是个静止的点。

**对照**：`air_raid.py:571-575` 使用约 1.2 px/帧（≈0.02 px/ms），视觉正常。

**修改方案**：统一为 px/ms 并在文件头写明单位约定（当前两套单位混用是根因）。把速度改为 **0.05–0.25 px/ms**（约 3–15 px/帧），按粒子类型调档使爆炸有扩散感。同时修正 `score_popups`/`respawn_scans` 等不移动的集合——它们不需要 `vx`/`vy`，`effect.get("vx", 0)` 已经安全，无需改。

**验证**：新测试 — 模拟 200ms 后断言粒子位移落在预期区间（例如 > 5px）。

**风险**：低，但属视觉参数，需人工确认观感（不要只看数值）。

---

### R-10 SMOKE 道具的游戏语义

**现状**：`has_line_of_sight`（`tank_engine.py:136-152`）只检查 `BRICK`/`STEEL`，**从不查询 `self.smokes`**。烟雾在 `:644` 生成、`:551` 过期，但没有任何逻辑消费它。与此同时成就 `tank_arsenal_master` 与统计 `smoke_uses` 都在计它的使用次数 —— 玩家会得到一个「用了但没效果」的道具。

**决策**：已选 **A（实现视线遮挡）**。

- **(a) 实现遮挡**（推荐，它是可玩性道具）：`has_line_of_sight` 增加烟雾判定。需要明确：
  - `SmokeState(player_id, x, y, until_ms)` 的半径（建议 1.5–2 格）与生效条件（仅阻断**敌方**视线，不阻断同队）。
  - 是否影响 `_projectile_threat`（`tank_engine.py:882` 附近的威胁判定）——建议只影响 AI/威胁评估与视线，不影响已发射子弹的物理。
- **(b) 降级为纯视觉**：从成就 `tank_arsenal_master` 的多样性计数（`system.py:453-456`）中移除 `smoke`，并把道具描述改为「释放视觉烟雾」。改动更小但不解决「道具无意义」。

**验证**（按 (a)）
- 新测试：两点之间放置烟雾，断言敌方视线被阻断、同队不受影响。
- 新测试：烟雾过期后视线恢复（依赖 `:551` 的过期逻辑）。
- 补上 `test_tank_engine.py` 中目前只断言「smokes 列表长度」的弱测试（`:377-380`）。

**风险**：中。会改变坦克对局的对抗平衡，需要实际对局验证。

---

### R-11 五子棋转场恢复

**现状**：`_start_new_game` 自己设 `self.state = self.PLAYING`（`gomoku.py:586`），调用者随后才调 `_start_transition(self.PLAYING, "fade")`：

```python
446    if action == "start":
447        self._start_new_game()
448        self._start_transition(self.PLAYING, "fade")     # ← 已被 :586 抢先，提前返回
449    elif action == "continue":
451        self._start_new_game(restore_state=state)
452        self._start_transition(self.PLAYING, "fade")     # ← 同上
453    elif action == "resume":
454        self._start_transition(self.PLAYING, "fade")     # ← 唯一生效的一个
```

`_start_transition` 在 `target_state == self.state` 时**直接返回**（`shell_transitions.py:33`）→ 淡入从不播放。

**对照**：「resume」分支（`gomoku.py:454`）不调用 `_start_new_game`，所以**只有 resume 有淡入** —— 同一菜单里三个入口视觉不一致，这是最容易被玩家察觉的部分。

**修改方案**：从 `_start_new_game` 移除 `self.state = self.PLAYING`，状态切换统一交给 `_start_transition`（与 resume 分支行为对齐）。

**注意**：需排查 `_start_new_game` 的其他调用方是否依赖它设置 state（`shell_transitions.py`、`system.py`、以及五子棋自己的测试）。`tests/test_tetris_mines_continue.py` 对 mines 有类似路径断言，五子棋需补等价测试。

**验证**：新测试 — 从菜单点击 start，断言 `transition_active` 为真，且 `state` 在转场**结束后**才变为 `PLAYING`。

**风险**：低。

---

## 5. 阶段 3：本地化与健壮性（P2）

### R-12 ZH 键冲突（RED / BLUE）

**现状**

```
localization.py:282  "RED":  "红色"      # 打砖块皮肤
localization.py:288  "BLUE": "蓝色"
localization.py:626  "RED":  "红方"      # 坦克对战方
localization.py:627  "BLUE": "蓝方"
```

后者胜出 → **Breakout 皮肤选项「BLUE」在中文下显示为「蓝方」**（消费点 `breakout.py:547`）。

**修改方案**：分域命名。对局方改用独立键（`SIDE_RED` / `SIDE_BLUE`，或 `TANK_RED` / `TANK_BLUE`），皮肤保留 `RED`/`BLUE`；更新消费点。R-14 的自检会防止复发。

**验证**：新测试 — `translate("RED") == "红色"` 且坦克方标签为「红方」。

**风险**：低。

---

### R-13 五子棋结果标题语义

**现状**：`gomoku.py:1938` 拼出 `f"{name} WINS"` 作为**本局胜负标题**，但字典里 `"BLACK WINS"`/`"WHITE WINS"` 是**统计计数**语义「黑方胜场」（`localization.py:252-253`）。于是中文下胜负标题显示为「黑方胜场」。

设计者本意是走动态规则 `^(.+) WINS$ → \1胜利`（`localization.py:701`），但该规则**是死代码** —— 字典命中会先于 `_format_dynamic` 返回（`localization.py:713-719`）。项目里已有正确的键 `BLACK_WINS_RESULT`/`WHITE_WINS_RESULT`（`:101-102`），但只被 `gomoku.py:1124` 使用。

**修改方案**

1. `_draw_game_status`（`gomoku.py:1938`）改用 `BLACK_WINS_RESULT` / `WHITE_WINS_RESULT`。
2. 统计页的胜场标签改用独立键（如 `STAT_BLACK_WINS`），与结果键彻底分离。
3. `^(.+) WINS$` 规则保留为通用兜底，并补一条「不误伤统计标签」的测试。

**验证**：中文下断言结果标题为「黑方胜利」、统计页标签为「黑方胜场」。

**风险**：低。

---

### R-14 统一翻译注册机制

**现状**：项目里有**两套互不兼容**的机制。

| 机制 | 位置 | 校验 | 生产使用 |
|---|---|---|---|
| `register_game_translations` | `localization.py:729-767` | 有归属表 `_TRANSLATION_OWNERS`、冲突检测、批量原子性 | **无 —— 只被测试调用**（`tests/test_registration.py:258-284`） |
| `ZH.update(collect_lore_translations())` | `localization.py:587-591` | 无 | **是** |

后果：
- 生产路径绕过全部校验，Lore 可以覆盖核心 UI 键（例如 `lore.py:796` 重定义 `"LORE"`、`:799` 重定义 `"BYE BYE SEE U NEXT TIME~"`）。
- `except ImportError: pass`（`localization.py:590`）会**静默吞掉 lore 导入失败**，一次性丢失约 267 条翻译且无任何诊断。

**修改方案**

1. 让 Lore 也走受校验的路径：`register_game_translations("lore", collect_lore_translations())`；或在 `ZH.update` 前插入冲突检测（把对 `__core__` 键的覆盖视为错误）。
2. 把 `except ImportError: pass` 改为至少写 stderr；开发模式下直接抛出（与环境变量或 `dev_mode` 联动）。
3. 增加**源码级**自检测试：用 AST 解析 `localization.py`，断言 `ZH` 字面量字典内无重复键（这是静态检查，不增加运行时开销）。这条测试会立刻暴露 R-12 以及其它现存冲突。

**验证**：AST 重复键测试 → 会先失败（暴露现存冲突）→ 逐个裁决后通过。

**风险**：低，但**会暴露一批现存键冲突**，需要人工逐个决定保留哪个语义。建议与 R-12、R-13 放在同一个工作批次内完成。

---

### R-15 `_format_dynamic` 清理

**现状**（35 条正则模式）

- `^UNLOCKED (\d+) / (\d+)$` **重复两次**：`localization.py:700` 与 `:705`。
- `^TIME (.+)$`（`:674`）过宽：任何以 `TIME ` 开头的英文串都会被改写（如 `TIME ATTACK` → `时间 ATTACK`）。

**修改方案**
1. 删除重复模式。
2. 把 `^TIME (.+)$` 收紧为 `^TIME (\d{1,2}:\d{2})$`（当前实际用法是 `mines.py:514` 的 `HUD TIME HH:MM`），或把该模式移到列表末尾降低误伤面。
3. 为 35 条模式建立**表驱动测试**：每条一个正例 + 已知负例（`TIME ATTACK`、`SCOREBOARD` 等），防止后续增删模式时误伤。

**验证**：表驱动测试覆盖全部模式。

**风险**：低。

---

### R-16 字体回退

**现状**：`get_chinese_font`（`localization.py:59-69`）直接 `pygame.font.Font(path, size)`，**无 try/except**。字体文件缺失（非冻结运行、安装不完整、`datas` 打包遗漏）→ `FileNotFoundError` → **首次渲染中文即崩溃**。

**修改方案**

```python
try:
    _font_cache[size] = pygame.font.Font(str(path), size)
except (OSError, pygame.error):
    # 回退到系统 CJK 字体，仅告警一次
    _font_cache[size] = pygame.font.SysFont(
        ["microsoftyahei", "simhei", "notosanscjksc", "arialunicodems"], size)
    _warn_font_fallback_once()
```

同时给 `pygame.font.init()`（`:60-62`）加 `pygame.error` 守卫。

**验证**：新测试 — monkeypatch `resource_path` 指向不存在的文件，断言仍可渲染且不抛异常。

**风险**：低。

---

### R-17 音频启动阻塞 2.0 秒

**现状**：实测 `Game()` 构造 **2.01s**，其中约 2.0s 是主线程上**急切合成 13 首 BGM + 56 个音效**（`audio.py:371-374`），**静音时也照做**。音频全部是程序化合成，无音频文件。

**决策**：已选 **(a) 懒加载 + (c) 静音跳过**。下表保留三个方案的比较作为依据。

**修改方案**

| 方案 | 做法 | 评价 |
|---|---|---|
| (a) 懒加载 | 首次 `play()` / `begin_*` 时才合成并缓存 | 改动集中在 `AudioManager`，调用方零改动。**推荐** |
| (b) 后台线程预热 | `__init__` 后异步填充；未就绪时该次播放跳过 | 实现最复杂，需处理线程安全与 mixer 生命周期 |
| (c) 静音跳过 | `muted` 或不 `enabled` 时不合成，取消静音时按需补齐 | 与 (a) 天然兼容 |

**推荐 (a)+(c)**：实现 `_get_sound(name)` / `_get_bgm(name)` 惰性访问器，替换 `audio.py:371-379` 的预填充循环。注意 BGM 的交叉淡入淡出（`audio.py` 的 `_update_crossfade`，由 `app.py:409` 每帧驱动）依赖音轨对象存在，需要保证「请求即合成」的路径无阻塞尖峰——首次播放 BGM 时若合成耗时较大，可接受一次性卡顿（远好于开机卡 2 秒），或对 BGM 单独保留少量预热。

**配套**：先落地阶段 0 的 `MERIDIAN_FAST_AUDIO` 开关（`R-27c`），它既是测试提速手段，也是本项改造的中间验证点。

**验证**
- 计时测试：构造 `Game()` 断言耗时显著下降（宽松阈值，如 < 0.6s）。
- 断言：未播放任何声音时，缓存为空或仅含少量预热项。
- **人工回归（必须）**：逐个游戏试听关键音效、BGM 切换与淡入淡出、静音/取消静音、音量面板、关机音效。

**风险**：中。音频是全局共享服务，改动面广；自动化测试无法覆盖听感，必须人工把关。

---

### R-18 `_SOUND_CACHE` 失效入口

**现状**：`audio.py:15` 的模块级 `_SOUND_CACHE` **永不清空**，而字体缓存有对应机制（`localization.py:16` 的 `clear_font_cache`，并在 `:21-38` 包装 `pygame.font.quit` / `pygame.quit` 时调用）。若进程内 quit/re-init mixer，缓存的 `Sound` 对象会失效。

**修改方案**：新增 `clear_sound_cache()`，并在 `_install_pygame_lifecycle_hooks` 的包装中一并注册 `pygame.mixer.quit`。与字体缓存保持同构。

**验证**：新测试 — 清空后断言缓存为空；模拟 mixer 重启路径不抛异常。

**风险**：低。

---

### R-19 `version_label()` 假函数

**现状**：`version_label()`（`version.py:4-5`）**忽略 `__version__`**，返回常量 `"MERIDIAN"` → 状态栏（`shell_desktop.py:547`）永远显示 "MERIDIAN"，而 `__version__ = "3.2.0"` **在全项目任何界面上都不出现**。

**决策**：已选 **(a) 显示真实版本**。下表两个方案保留作为依据。

**修改方案**

- **(a) 采纳**：`version_label()` 返回 `f"MERIDIAN {__version__}"`（或状态栏分开渲染设备名与版本）。依据：`tools/check_release.py:25-29` 已经在读取 `__version__`，说明版本号是被有意维护的，只显示不出去是浪费。
- (b) 未采纳：重命名为 `device_label()`。

**验证**：新测试 — 断言状态栏文本包含 `__version__`（按 (a)）。

**风险**：低。中文宽度会使状态栏文本变长，需确认不溢出（`shell_desktop.py:544-560` 的区域）。

**附带发现（已查清，结论与你原本的授权不同，请过目）**：`version.py:1` 的 `__version__ = "3.2.0"` 表面上与 `Version_History.md` 的「v3.3.0-dev 未发布」不一致，但进一步查证后**当前状态其实是自洽的**：

- `tools/check_release.py:12` **硬编码** `RELEASE_VERSION = "3.2.0"`，并要求三件事同时成立：`version.py` 匹配该值、CHANGELOG 存在 `[3.2.0]` 段、工作区干净且无 `v3.2.0` 标签。
- `CHANGELOG.md` 的 3.3.0 内容位于 `## [Unreleased]` 段，尚未成形为 `[3.3.0]`。

因此「`__version__` 停留在 3.2.0」是**「最新已发布版本」的正常语义**，而不是遗漏。单独把 `version.py` 改成 `3.3.0` 会让 `check_release.py` 立刻失败（version 与 release target 不匹配 + CHANGELOG 缺 `[3.3.0]`），是引入回归。

**修正后的做法**：版本号提升是一个**发布动作**，应当与另外两处原子地一起改 —— `meridian/version.py`、`tools/check_release.py` 的 `RELEASE_VERSION`、以及把 CHANGELOG 的 `## [Unreleased]` 改成 `## [3.3.0] - <日期>`。建议在 3.3.0 真正发布时执行（可与 R-19 合并，也可单独）。在此之前 R-19 只改 `version_label()` 让它读 `__version__`，桌面会显示 `MERIDIAN 3.2.0`，即「最后发布的版本」——这是可接受的语义。**我不擅自提升版本号。**

---

### R-20 关卡数硬编码

**现状**：标准关卡数真值由 `arcade_levels.AIR_LEVELS`（`arcade_levels.py:102`）持有，但 `16` 被硬编码在 5 处：

| 位置 | 用法 |
|---|---|
| `system.py:449` | 成就 `air_all_s` 的判定 `len(ratings) >= 16` |
| `air_raid.py:900` | `min(16, self.air_level + 2)` 解锁上限 |
| `air_raid.py:1047` | 关卡选择入口的 `16` |
| `air_raid.py:1322` | 选择页 `min(16, start + 12)` |
| `localization.py:501` | **玩家可见文案** "Earn S on all 16 standard missions" |

另有 `developer.py:114-115` 的 `unlocked=16` / `archive_unlocked=8`。

**修改方案**

1. 在 `arcade_levels.py` 导出派生常量：
   ```python
   STANDARD_MISSION_COUNT = sum(1 for lv in AIR_LEVELS if lv["mode"] == "standard")
   ```
2. 5 处引用改为该常量。
3. `localization.py:501` 的文案改为不含数字的措辞：**已决策采用 `"Earn S on every standard mission"`**（静态字符串更易维护、无翻译歧义），不增加动态正则模式。
4. 顺带修 `completion.py:171` 的 `OBJECTIVES[game_id]`：`WORLD_IDS` 与 `OBJECTIVES` 是两份手工维护的注册表，向 `WORLD_IDS` 添加世界而忘记 `OBJECTIVES` 会**无守卫地 KeyError**。改为在模块加载时做一次一致性断言。

**验证**：新测试 — 断言 `localization` 中该成就描述不含与 `STANDARD_MISSION_COUNT` 冲突的数字；断言 `set(WORLD_IDS) == set(OBJECTIVES)`。

**风险**：低。

---

### R-21 `_deep_merge` 类型替换与 `save()` 迁移异常

**现状（两个相关缺陷）**

1. `_deep_merge`（`persistence.py:167-176`）在类型不匹配时**整体替换**默认值：`{"settings": "x"}` 会让整个 `settings` 变成字符串，随后 `system.py:179` 的 `settings["master_volume"]` 抛 `TypeError`/`KeyError`。只有少数消费者是防御性的（`completion.py:31-39`、`_backfill_tank_statistics`、`lore_condition_met`），其余假设结构正确。
2. `save()`（`persistence.py:263-273`）在 `:266` 调用 `self.migrate(data)`，**不在任何 try 内**；而 `load()`（`:244-261`）有完整的异常处理。迁移假设容器是 dict（`:220-222`、`:229-234` 的 `setdefault` 链），遇到 `"records": []` 会抛 `TypeError`，从**保存路径**抛出。

**决策**：D2=B 移除了「为旧档补形状」这一半工作，本项只保留**对未来数据**的防御性加固。

**修改方案**

1. `_deep_merge` 在类型不匹配时**保留默认值**并丢弃传入值（记录一次告警），而不是替换。语义上「损坏的存档字段不应污染可信默认结构」。
2. `save()` 的 `migrate` 调用包 try（`persistence.py:266`）；失败时降级为写入规范化后的数据——原子写（`:263-273`）已经保证不会损坏现有存档。
3. 增加**存档契约测试**：断言 `default_data()` 的键集合覆盖各游戏实际写入的键。这一条与 D2 无关，且直接针对 `Bug_Log.md` 中 Unreleased 那条 Tank 缺字段问题的成因。

~~原第 2 项：迁移前统一形状规范化~~ —— D2=B 后不再需要（不为旧档做兼容）。

**验证**
- 新测试：`load()` 输入 `{"settings": "x", "statistics": [], "records": []}`，断言得到合法的默认结构而非异常。
- 新测试：`save()` 在数据形状异常时不抛异常且不留半成品文件。

**风险**：中。这类改动会掩盖问题，务必配合告警日志，避免静默吞掉真实损坏。

---

### R-26 测试覆盖补强

**现状**：147 个测试通过，但覆盖高度集中。

- `tank_engine.py` 是**唯一**有实质逻辑测试的模块（66 个用例），恰因为它是不 import pygame 的纯引擎。
- **12 个模块无任何专属测试**：`air_raid.py`（1,877 行）、`arcade_common.py`、`arcade_levels.py`、`lore_expansions.py`、`shell_boot.py`、`shell_password.py`、`shell_transitions.py`、`tank_battle.py`、`tank_items_ui.py`、`tank_vfx.py`、`ui_components.py`、`volume_panel.py`。
- 至少一个测试**把缺陷固化成了规格**：`tests/test_tetris_mines_continue.py:104-105`。
- `test_tank_engine.py` 的弱断言：`test_open_neighbor_count`（`:105-110`）对 0–4 任意值都通过；`test_cannot_walk_into_wall`（`:177`）只断言 `>= 0.5`。
- `test_tank_engine.py` 的空白：EMP 射速锁定、加速 1.25× 移动、穿透穿多目标、warp 排名与保护、地雷移除、骤死双杀、快照中的 `smokes`/`paused`/`winner`/穿透弹/损坏字段。

**修改方案（按性价比排序）**

1. **零成本**：`volume_panel.py` 已是纯状态机，直接补状态转换测试。
2. **低门槛**：`shell_transitions.py` 是纯状态机（`_start_transition`/`_update_transition`），可用 stub 对象测，无需真 `Game`。补「`target_state == self.state` 时提前返回」这条（R-11 的根因）的显式测试。
3. **重构后测**：`air_raid` 的评分（`air_raid.py:868-873`）与进度门禁（`chapter` 计算、`completed // 2 + 1`）应抽成纯函数后再测——这也是 R-06 的前置工作。
4. **修弱断言**：把上述两处改成精确值。
5. **补 `tank_engine.py` 缺口**：按空白清单逐项补，尤其是快照损坏字段与 `smokes` 语义（配合 R-10）。

**验证**：新增测试全部通过，且**不依赖真实存档**。

**风险**：低。

---

## 6. 阶段 4：结构与代码卫生（P3）

### R-22 五子棋逐帧状态回归 GomokuMixin（最高风险项）

**现状**：`GomokuMixin` **没有** `_update_gomoku`，也不在 `_UPDATE_DISPATCH` 中。它的动画状态全部由 `app.py:426-437` 在**每个未登记状态**下推进；`app.py:496` 与 `:535-537` 每帧读取 `self.board.winner`，而 `self.board` 只在五子棋代码里创建（`system.py:187-188`）。

**这为什么是结构性问题**：它使 `GomokuMixin` 不是一个可移除的组件 —— 删掉它，`app.update()` 会直接崩溃。这正是「Mixin 分层没有真正解耦」最硬的证据。

**修改方案**

1. 新增 `GomokuMixin._update_gomoku()`，把以下方法从 `app.py` 迁入：
   `_update_drop_animations`、`_update_magnetic_preview`、`_update_ripples`、`_update_invalid_marks`、`_update_undo_animations`、`_update_win_line`、`_update_win_stone_flash`、`_update_delayed_end_page`、`_update_end_page_animation`、`_update_win_overlay`。
2. `_update_particles` 与 `_update_screen_shake` 是**全项目共享**的（`particles`/`shake_*` 被多个游戏使用），**保留在 `app.py`**。
3. 在 `_UPDATE_DISPATCH` 中为 `MENU`、`PLAYING`、`END`、`SETTINGS` 登记 `_update_gomoku`（当前这四个状态走的是「无表项则落到通用块」的隐式路径）。
4. 把 `app.py:496/535-537` 对 `self.board` 的读取移入这些状态专属的更新路径，消除「主循环无条件依赖某游戏的字段」。

**验证**
- 147 个现有测试全绿。
- **人工回归（必须）**：落子动画、磁吸预览、涟漪、非法提示、撤销动画、胜利连线、棋子依次闪烁、延迟结算页、胜利遮罩、屏幕震动、以及从各状态返回桌面。

**风险**：**高**。触及核心循环（`update()` 每帧执行），是本计划中唯一需要单独批次、单独回归的改动。建议：先只做「迁出」，不改行为；确认无回归后再做第 4 步的依赖解耦。

---

### R-23 屏幕震动统一

**现状**：同一处补丁存在**两份**，且都不完整。

- `app.py:527-533`：在 `_update_screen_shake` 中把 `snake_shake_*`、`breakout_shake_*` 归零。
- `system.py:387-393`：在 `_update_persistence` 中**重复**同样的归零。

两份都**没有覆盖** `mines_shake`（`mines.py:25`、`:535`）与 `g2048_invalid_shake`（`g2048.py:18`、`:344`）→ **关闭「屏幕震动」后，扫雷和 2048 仍在震动**。这是可直接复现的行为不一致。

**修改方案**

1. 在 `SystemMixin`（或一个共享位置）新增 `_shake_fields()`，返回所有游戏的震动字段名元组。
2. `app.py` 与 `system.py` 的两处补丁删除，改为一处统一调用。
3. 覆盖全部四个游戏（snake、breakout、mines、2048）以及坦克（`tank_shake_frames`，`tank_battle.py:272`）与空袭（`shake_duration` 共享）。

**验证**：新测试 — 关闭 `screen_shake_enabled` 后，对每个游戏断言其震动字段被归零。

**风险**：低。

---

### R-24 街机表现层去重（约 1400 行）

**现状**：五个页 1 游戏（snake / mines / breakout / g2048 / tetris）共 3,413 行，其中约 **1,400 行**是复制粘贴的菜单/结算/设置/按钮绘制；`arcade_common.py` 已有 344 行实现同样功能，但**这五个模块没有一个 import 它**（只有 `air_raid.py:4` 与 `tank_battle.py:7-12` 使用）。

重复清单（含行号）：

| 重复内容 | 份数与位置 |
|---|---|
| 左侧标题栏（25 行同构） | `snake.py:580-607`、`mines.py:497-504`、`breakout.py:373-381`、`g2048.py:305-312` |
| 状态面板（≈120 行） | `snake.py:609-649`、`mines.py:506-527`、`breakout.py:383-407`、`g2048.py:314-334` |
| 按钮绘制 | `snake.py:768-828`、`mines.py:79-92`、`breakout.py:430-450`、`g2048.py:50-66`、`tetris.py:515-527` |
| 菜单页 | `snake.py:737-766`、`mines.py:618-637`、`breakout.py:409-428`、`g2048.py:430-452`、`tetris.py:542-598` |
| 结算页 | `snake.py:829-891`、`mines.py:639-659`、`breakout.py:452-478`、`g2048.py:454-476`、`tetris.py:691-716` |
| 事件按压/释放协议 | 五个文件各一份；`tetris.py:337-349` 与 `arcade_common.handle_arcade_buttons:38-54` 完全同构 |

**结局面板尺寸无理由地各不相同**：560×430、560×420、580×360、620×380。

**具体整合障碍**：`draw_arcade_button` 读取 palette 字典的 `"hover"/"panel_dark"/"accent"/"text"` 四个键（`arcade_common.py:20-33`），而这五个游戏使用扁平命名空间（`C.SNAKE_*`、`C.MINES_*` …），从不构造 palette dict。只有 `AIR_PALETTE` / `TANK_PALETTE` 存在。

**修改方案**

1. 新增适配层 `palette_for(prefix)`：把 `C.<PREFIX>_*` 映射为 `{"hover","panel_dark","accent","text"}`。
2. 按风险递增顺序逐游戏迁移：**按钮 → 状态面板 → 菜单页 → 结算页 → 设置页**。每个游戏一个提交。
3. 迁移时统一结局面板尺寸到 **560×430**（已决策）。

**验证**
- 项目已有 `tools/capture_gameplay_batch.py`，可直接复用做**迁移前后截图对比**。
- 新测试：断言按钮绘制实现只有一份（例如 `draw_arcade_button` 被至少 7 个模块引用）。

**风险**：中。视觉回归风险高（本项目已有「双语视觉回归」专项历史，见 `docs/superpowers/plans/2026-07-13-bilingual-visual-regression.md`），必须逐游戏截图确认，且**中英双语都要看**。

---

### R-25 死代码、编码与资源清理

**死代码清单**

| 项 | 位置 | 说明 |
|---|---|---|
| `menu_btns` / `btn_selected_size` / `end_btns` | `gomoku.py:306-309`、`:53` | 只写不读；`_get_*_buttons` 每帧重建，docstring 却声称创建 rect |
| `_rotate_local_point` / `_rotate_point_around` / `_draw_panel_title` | `gomoku.py:130/140/1019` | 无引用（`_draw_menu_logo` 反而内联手写旋转，`:253-257`） |
| `_draw_game_title_banner` | `gomoku.py:1850` | 纯透传，另有未使用的 `sx` |
| `tank_particles` | `tank_battle.py:82/257-261/505-507` | **update+draw 完整接线但无人写入**（已被 `tank_vfx` 取代） |
| `item_status` | `tank_items_ui.py:19-33` | 无调用者 |
| `air_warnings` / `air_preview_tick` / `air_rating_score` | `air_raid.py:51/41/887` | 分别：从不追加、只增不读、从不读取 |
| `_replace_tile` 的 `else` 分支 | `tank_engine.py:761-762` | `from_dict` 保证 `rows` 全为 `str`（`:412-417`），防御性死分支 |
| 字符串颜色分支 | `breakout.py:321-322` | 所有调用点都传元组 |
| `is_chinese()` 语言分支 | `gomoku.py:927-933` | 唯一一处模块自己决定语言的地方，绕过翻译表 |

**编码卫生**

- **乱码注释 24 处**（GBK/UTF-8 混淆残留，仅注释，不影响功能）。**已决策：全部修复。**
  `gomoku.py` 17 处、`snake.py` 3 处、`breakout.py` 2 处、`common.py:286`、`shell_boot.py:33`（docstring）、`shell_desktop.py:891`。
  **注意**：`common.py:286` 有一个字符**已永久丢失**（显示为 `?`），需人工重写该行语义；其余可人工还原。**不要用脚本猜编码**，逐文件用编辑器处理。
- **BOM 不一致**：`shell_boot.py` 与 `shell_desktop.py` 带 UTF-8 BOM，其余 30 个模块不带（会破坏无 BOM 工具链，例如我本次 AST 扫描第一次就失败）。**已决策：统一去掉 BOM。**
- **行尾**：多数文件为 CRLF，`persistence.py` 等少数为 LF，建议统一（`.gitattributes` 或编辑器配置）。

**资源**

- `assets/banner.png` **不存在**，但 7 个 README（`README.md:2` 与 `docs/readme/README_{EN,FR,IT,JA,RU,AR}.md`）都引用它（靠 `onerror="this.style.display='none'"` 掩盖）。**决策：删除全部 7 处引用，不造图。**
- ~~`assets/fonts/OFL.txt` 已被删除但未提交~~ —— **R-27 已提交删除**。实测两者**文本完全相同，仅行尾不同**（被删的 `OFL.txt` 为 LF / 4354 字节，保留的 `FusionPixelFont-LICENSE-OFL.txt` 为 CRLF / 4447 字节，93 行各多 1 字节，正好吻合）。原计划里写的「逐字节相同」不准确——`diff --strip-trailing-cr` 无差异，删除是安全的。
- `tests/__pycache__/test_frame_writer.cpython-312-pytest-8.4.2.pyc` 存在但**源文件已不存在**。清理缓存目录。
- `build/`、`dist/` 已被 `.gitignore:5-6` 覆盖。~~`.pytest_cache/`、`.ruff_cache/`、`pytest-cache-files-*/` 未覆盖~~ —— **此条原判断有误，已更正**：`.pytest_cache/` 与 `.ruff_cache/` 各自带有工具自动生成的 `.gitignore`（内容为 `*`，会连自身一起忽略），`pytest-cache-files-*/` 是空目录，git 对三者均不可见，**无需处理**。本次已新增 `.zcode/` 到 `.gitignore`（与既有的 `.agents/`、`.superpowers/` 同类约定）。
- 补充：仓库缺少 `.gitattributes`，这是行尾（CRLF/LF 混用）与 BOM 不一致反复出现的根因。建议在 R-25 中一并加入（例如 `* text=auto` 并为核心源码声明 `eol=lf`）。

**验证**：`ruff` + 全量测试 + **手工打开每个页面**（乱码清理会触碰大量注释行，虽然不影响行为，但改错缩进就会坏）。

**风险**：低，但工作量大且枯燥，容易在批量编辑中引入缩进错误。

---

## 7. 明确不做的事

**不要给 `translate()` 加缓存。** 它确实无缓存（实测未命中 3.3–8.0 µs/次，35 条正则线性扫描），但**实测渲染总开销只有 2.1–5.1 ms/帧**（桌面最重 5.06 ms），对 60 fps 有 3 倍以上余量。这是**非瓶颈**，优化它只会增加状态管理复杂度而没有可感知收益。R-15 的模式清理已足够。

**不要重构 `tank_engine.py`。** 它是项目里唯一正确的三层架构（纯确定性引擎 + VFX/UI 层 + 渲染 Mixin），`to_dict`/`from_dict` 带 155 行校验，也是唯一有实质测试覆盖的模块。它应该被**当作其他模块的模板**，而不是被"统一风格"。

**不要为了消重而消重。** R-24 的价值在于「一份实现、一处修改」，而不是行数下降本身。如果一个游戏的 UI 确实需要不同外观，允许它保留差异，只共享结构。

**不要在阶段 1–3 期间动 `app.py` 的分发循环。** R-22 触及每帧执行的核心路径，必须与其他修复隔离，否则回归时无法定位是哪一处引起的。

---

## 8. 决策记录

> 全部决策于 2026-09-15 确认。D1–D3 由项目所有者拍定；其余按本计划推荐值执行（"剩下的你看着办"）。

### 已确认（会改变实现方式）

| 编号 | 决策 | 结论 | 对计划的影响 |
|---|---|---|---|
| D1 | 撤销胜局时成就是否回滚 | **A：统计回滚，已解锁成就保持解锁** | R-01 无需为 `_check_achievements` 增加回收逻辑；只需让 `_record_stat` 支持负向调用 |
| D2 | v5 存档兼容程度 | **B：不做迁移，允许丢弃旧档** | R-01 / R-04 **不再需要 `SCHEMA_VERSION` 提升与迁移代码**；旧 `run_state` 由校验层拒绝而非迁移补字段；现存的分叉计数器保持原样、不再修复。R-21 简化为纯防御性加固 |
| D3 | 阶段顺序 | **A：阶段 0 → P0 → P1 → P2 → P3** | 先落 `MERIDIAN_FAST_AUDIO`（3 行，测试 7.3s → 约 1s），再进 P0 |

**D2 的安全兜底（不增加工作量）**：即使不写迁移，现有 `SaveManager.load`（`persistence.py:244-261`）已经把无法读取的存档**隔离**为 `save.corrupt-<ts>.json` 并回退到 `.bak`，而不是静默覆盖；R-04 的校验层同样选择「拒绝并提示」而非崩溃。所以 B 的代价是「旧档可能不被采用」，**不是「旧档被销毁」**。

**D2 的具体删除项**（原计划中有、现在不做）：

- R-01：删除「迁移中把两处分叉计数器按 `max()` 合并」整段，以及相关迁移测试。
- R-04：删除「旧档无 `format` 字段时迁移补齐」整段；旧快照一律走 `REJECTED` 分支。
- R-21：删除「迁移前形状规范化」整段，保留 `_deep_merge` 与 `save()` 两处加固。
- 全局：`SCHEMA_VERSION` 保持 `5` 不动。

### 已采纳默认值（无需再决策）

| 编号 | 项 | 采纳值 |
|---|---|---|
| D4 | SMOKE 道具 | **实现视线遮挡**：`has_line_of_sight` 读取 `self.smokes`，仅阻断敌方视线 |
| D5 | 音频改造 | **懒加载 + 静音跳过**，调用方零改动 |
| D6 | 桌面状态栏 | **显示 `MERIDIAN 3.2.0`**（用上 `__version__`） |
| D7 | R-22 结构重构 | **做**，但排在全部 P0–P2 之后，单独批次、单独回归 |
| — | R-06 剧情页 ESC | 保持现状（等同 ENTER），修 R-06 正确性时不动它 |
| — | R-07 横幅清除 | frame 计数自动清除（与 `achievement_notifications` 同模式） |
| — | R-14 ZH 冲突裁决 | 见下方清单 |
| — | R-19 版本显示 | 同 D6 |
| — | R-20 成就文案 | 去掉数字：`"Earn S on every standard mission"` |
| — | R-24 结局面板 | 统一到 560×430 |
| — | R-25 banner | 删掉 7 个 README 里的 `assets/banner.png` 引用，不造图 |
| — | R-25 乱码注释 | 全部修（仅注释行）；`common.py:286` 因字符已丢失，按上下文重写整句 |
| — | schema 版本 | **不提升**（D2=B 的直接结果） |

### R-14 的 ZH 键冲突清单（实测结果）

`localization.py` 共 **548** 个字符串字面量键，其中 **14 个重复定义、仅 3 个取值冲突**（其余 11 个是同值重复，无害）。清单比原估计小得多：

| 键 | 冲突值 | 裁决 |
|---|---|---|
| `RED` | 红方 / 红色 | 皮肤保留 `RED` = **红色**；阵营新增 `SIDE_RED` = 红方 |
| `BLUE` | 蓝方 / 蓝色 | 皮肤保留 `BLUE` = **蓝色**；阵营新增 `SIDE_BLUE` = 蓝方 |
| `P TO RESUME   ESC FOR MENU` | 两种中文渲染 | 取 `P：继续　ESC：返回菜单`（全角空格，与项目其他提示一致） |

补充事实：`红色`/`蓝色` 目前被定义在后的 `红方`/`蓝方` 覆盖，所以 Breakout 的皮肤选项「BLUE」在中文下现在显示为**蓝方**——R-12 与 R-14 修完后应恢复为「蓝色」。

---

### 附：决策依据（原开放问题，现已全部关闭）

#### Q1（R-01）撤销胜局时，成就进度是否应该回滚？ → **已选 A**

- **选项 A（推荐）**：统计回滚，**已解锁成就保持解锁**。符合主流游戏做法，避免「撤销导致成就消失」的困惑。
- **选项 B**：统计与成就一并回滚。语义更"诚实"，但会出现成就闪烁消失，且 `achievement_notifications` 的队列逻辑需要相应处理。

**影响**：`_record_stat` 的负向调用是否需要触发成就回收（`system.py:461-482` 目前只做解锁，不做回收）。

#### Q2（R-06）~~看完章节剧情后应进入哪一关？~~ → **已解答，无需决策**

~~选项 A：该章节的第一个关卡。选项 B：该章节的最后一个关卡。选项 C：回关卡选择页。~~

**结论**：数据验证（`tools/repro_r06_air_chapter.py` Probe B）表明，正常战役中剧情门**只在每章第一关触发**，从不落在 Boss 关卡上。所以「该章的第一关」与「被中断的那一关」是同一关，三个候选合并为唯一答案：**恢复被中断的关卡**。

修法随之简化为「把入参 `level` 原样透传」三行改动，不需要新增按章节查关卡的函数。详见 [R-06](#r-06-空袭行动章节关卡索引错位)。

**交互决策已定**：剧情页按 ESC 目前等同于按 ENTER（都直接开始该关，`air_raid.py:1664`）。按 D 表**保持现状**，不在 R-06 修复中改动。

#### Q3（R-10）SMOKE 道具走实现还是降级？ → **已选 A（实现视线遮挡）**

- **选项 A（推荐）**：实现视线遮挡。它是可玩性道具，降级会让 8 种道具变成 7 种有效。
- **选项 B**：降级为纯视觉，从成就多样性计数中移除。

**影响**：选项 A 会改变坦克对局的对抗平衡（需要实际对局验证），选项 B 只需改数据和文案。

#### Q4（R-17）音频改造选哪个方案？ → **已选 A（懒加载 + 静音跳过）**

- **选项 A（推荐）**：懒加载 + 静音跳过。调用方零改动。
- **选项 B**：后台线程预热。启动更快但线程安全与 mixer 生命周期复杂。

**影响**：自动化测试无法覆盖听感，选项 A 首次播放 BGM 时可能有一次性的合成卡顿（远好于开机卡 2 秒）。

#### Q5（R-19）状态栏显示什么？ → **已选 A（显示真实版本）**

- **选项 A（推荐）**：显示 `MERIDIAN 3.2.0`（用上 `__version__`）。
- **选项 B**：保持 `MERIDIAN`，把函数重命名为 `device_label()` 并补文档。

**影响**：选项 A 需确认中文模式下状态栏不溢出（`shell_desktop.py:544-560`）。

#### Q6 阶段顺序 → **已选 A（阶段 0 → P0 → P1 → P2 → P3）**

按本计划的顺序（P0 → P1 → P2 → P3），还是先做 R-17（音频）以获得更快的测试反馈？

**说明**：R-17 与技术债相关性低，但它把 `Game()` 构造从 2.0s 降到接近 0，能让后续每个修复的测试循环显著加快。若你希望「先尝到甜头」，可把 R-17 提到阶段 0 之后、阶段 1 之前。

---

## 9. 回归验证清单

### 每个 R-xx 提交的最小验证
```bash
python -m ruff check meridian/ tests/
python -m pytest tests/ -q
```

### 触及存档的提交（R-01、R-03、R-04、R-21）额外验证
1. 用**真实旧存档**（从 `%APPDATA%\MERIDIAN\save.json` 复制一份）跑一次 `load()` → `save()` → 再 `load()`，断言幂等。
2. 确认 `.json.bak` 已生成且可用于回滚。
3. 确认损坏档被隔离为 `save.corrupt-<ts>.json` 而不是被覆盖。

### 触及渲染/交互的提交（R-06 ~ R-11、R-22 ~ R-24）额外验证
复用 `tools/capture_gameplay_batch.py` 生成截图，**中英双语各一轮**，覆盖：
- 桌面两页 → 每个游戏的开机 → 菜单 → 对局 → 暂停 → 结算 → 返回桌面
- 系统设置、玩家档案、成就墙、Lore 阅读器
- 关机流程

### 触及音频的提交（R-17、R-18）额外验证
**必须人工试听**：每个游戏的 BGM 进入/退出与淡入淡出、关键音效（落子、消行、爆炸、成就解锁、按钮）、音量面板三轨调节、静音/取消静音、开机与关机音效。

### 最终验收（全部 R-xx 完成后）
- [ ] `pytest tests/ -q` 全绿，且测试数显著高于 147（新增回归测试）
- [ ] `ruff check meridian/ tests/` 无告警
- [ ] `python tools/check_release.py` 通过
- [ ] `BUILD_EXE.bat` 可产出 `dist/MERIDIAN.exe` 且可运行（注意 `MERIDIAN.spec:7` 的 `datas` 只含 `assets/fonts`，若补了 `banner.png` 需同步）
- [ ] CI 的 3 版本 × 2 平台矩阵全绿
- [ ] 中文模式全流程无英文残留（R-12 ~ R-15 的直接验收项）
- [ ] `Development_Log/Bug_Log.md` 补入本轮修复条目（沿用「只写可核验内容」的既有格式）

---

## 10. 建议的提交序列

```
chore(repo): R-27 拆分并提交 53 项积压变更（文档/模板/日志/资产/代码）
test(infra): R-27a/b 固化基线并抽出存档往返夹具
perf(audio): R-27c 增加 MERIDIAN_FAST_AUDIO 开关，加速测试套件
test(infra): R-26 补 volume_panel / shell_transitions 测试

fix(gomoku): R-01 统一胜场计数器（statistics 为唯一真值，不迁移）
fix(gomoku): R-05 wins_on_19 改用 board_count 判定
fix(mines):  R-02 计时改为增量累加，修正固化缺陷的测试
refactor(runstate): R-03 快照改为值语义（mines/gomoku/air）
feat(persistence): R-04 快照自描述 + 恢复校验三态 + 设置页交互

fix(air):    R-06 修正章节→关卡索引映射，修复档案键盘翻页
fix(air):    R-07 解锁横幅改为一次性通知
fix(tank):   R-08 爆炸坐标由引擎事件携带
fix(tank):   R-09 统一 VFX 速度单位
feat(tank):  R-10 实现 SMOKE 视线遮挡（若选 A）
fix(gomoku): R-11 恢复开局/继续转场

fix(l10n):   R-12 分离 RED/BLUE 皮肤与阵营键
fix(l10n):   R-13 结果标题改用独立键
test(l10n):  R-14 AST 重复键自检（先失败以暴露现存冲突）
refactor(l10n): R-14 统一翻译注册机制
fix(l10n):   R-15 去重模式并收紧 ^TIME
fix(l10n):   R-16 字体回退

perf(audio): R-17 音频改为懒加载 + 静音跳过
fix(audio):  R-18 增加 clear_sound_cache
fix(shell):  R-19 状态栏显示真实版本
refactor(levels): R-20 关卡数改为派生常量
fix(persistence): R-21 _deep_merge 不替换类型 + save 迁移守卫

refactor(arcade): R-23 统一屏幕震动
refactor(gomoku): R-22 逐帧状态回归 GomokuMixin          ← 高风险，独立批次
refactor(arcade): R-24 表现层去重（每游戏一个提交）
chore(cleanup):  R-25 死代码 / 乱码注释 / BOM / 资源
```

---

## 基线快照

| 项 | 值 | 采集时间 |
|---|---|---|
| 测试数 | 147 passed | 2026-09-15 |
| 测试耗时 | 7.27s → **6.57s**（R-27 后复测） | 2026-09-15 |
| ruff | All checks passed | 2026-09-15 |
| `Game()` 构造耗时 | 2.01s（音频合成 ~2.0s） | 2026-09-15 |
| `draw()` DESKTOP / MENU / PLAYING | 5.06 / 4.02 / 2.41 ms（ZH） | 2026-09-15 |
| 核心代码行数 | 18,798（`meridian/*.py`） | 2026-09-15 |
| 测试行数 | 2,472 | 2026-09-15 |

> 本计划中的每一条 `文件:行号` 均经直接读码核对。性能数据为在本机（Windows 10.0.26200 / Python 3.12.5 / pygame 2.6.1，`SDL_VIDEODRIVER=dummy`）实测，不代表终端用户环境。

### R-27 完成记录（2026-09-15）

积压的 53 项变更已按主题拆为 **11 个提交**，工作区现为干净状态；`origin/codex/repair-known-issues` 落后 11 个提交（**未推送**）。

```
cceb032 docs: add development log archive and version history
d24c381 docs: sync six translated READMEs to v3.2.0 facts
fffc917 docs: normalize CHANGELOG version headings
c73f7ec docs: add CONTRIBUTING and issue/PR templates
3b33a28 test: add localization and continue-run regression tests
19824f7 chore(tools): add gameplay capture script
24070f5 chore(assets): add gameplay screenshots
09441c4 chore(assets): remove duplicate font license
8fdd878 chore: ignore ZCode session directory
0692b86 docs: add remediation plan and R-06 chapter mapping reproducer
facb6f4 docs: add design specs and plans for demo videos and continue fixes
```

提交后复测：`ruff` 全通过，`pytest tests/ -q` → **147 passed in 6.57s**（未触碰任何 `meridian/` 源码，因此结果与基线一致）。

**提交过程中核对出的两点**（已回填到 R-25 与 R-19）：

1. 被删的 `assets/fonts/OFL.txt` 与保留的许可文件**并非逐字节相同**，而是行尾不同（LF vs CRLF），文本内容一致——删除安全，但原计划的措辞不准确。
2. `__version__` 停留在 `3.2.0` 是**自洽状态**而非遗漏，因为 `tools/check_release.py:12` 硬编码了发布目标 `3.2.0`。版本号提升必须与 `check_release.py` 和 CHANGELOG 的 `[Unreleased]` → `[3.3.0]` 原子地一起改，属发布动作。**故未提升版本号**，详见 R-19。
