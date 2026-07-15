<p align="center">
  <img src="assets/banner.png" alt="MERIDIAN Banner" width="800" onerror="this.style.display='none'">
</p>

<h1 align="center">🌐 MERIDIAN · 子午线</h1>

<p align="center"><strong>诸界 · 一器</strong></p>
<p align="center"><em>Many Worlds. One Device.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python">
  <img src="https://img.shields.io/badge/pygame-2.x-green" alt="Pygame">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
  <img src="https://img.shields.io/badge/achievements-60-brightgreen" alt="Achievements">
</p>

<p align="center">
  <strong>中文</strong> |
  <a href="docs/readme/README_EN.md">English</a> |
  <a href="docs/readme/README_FR.md">Français</a> |
  <a href="docs/readme/README_RU.md">Русский</a> |
  <a href="docs/readme/README_IT.md">Italiano</a> |
  <a href="docs/readme/README_JA.md">日本語</a> |
  <a href="docs/readme/README_AR.md">العربية</a>
</p>

---

## 📖 目录

- [简介](#-简介)
- [世界观](#-世界观)
- [异界一览](#-异界一览)
- [功能亮点](#-功能亮点)
- [快速开始](#-快速开始)
- [操作说明](#-操作说明)
- [项目结构](#-项目结构)
- [架构设计](#-架构设计)
- [扩展接口](#-扩展接口)
- [打包构建](#-打包构建)
- [更新日志](#-更新日志)
- [贡献指南](#-贡献指南)
- [开源协议](#-开源协议)
- [致谢](#-致谢)

---

## 🌌 简介

**MERIDIAN（子午线）** 是一台来历不明的掌上器物。它的"屏幕"并非普通显示屏，而是一面 **共鸣透镜**——来自诸界的现实碎片被封存在不同游戏模块中，每一个模块都是通向一个独立世界的稳定门户。

这不是一台普通的游戏机。它是一台**跨维度观测设备**。

本项目使用 **Python + Pygame** 构建，是一个完整的多游戏平台模拟器。它融合了：

- 🎮 **八款经典街机游戏**的完整复刻
- 📚 **深度的世界观叙事系统**，每个游戏都有独立的故事背景
- 🏆 **60 项成就**，跨游戏追踪玩家进度
- 🌍 **完整的双语支持**（简体中文 / English）
- 💾 **崩溃安全的持久化存档**，支持游戏中断恢复
- 🎵 **程序化音频引擎**，动态生成 BGM 和音效
- 🛠 **内置开发者面板**，方便调试和测试

> 语言版本：中文（本文）及页面顶部链接的六种译文。

---

## 🌠 世界观

MERIDIAN 不仅仅是一个游戏合集——它拥有一套完整的**元叙事**框架：

- **开机序列**：共鸣校准 → 维度扫描 → 锚点稳定 → 核心连接
- **密码认证**：「NEXUS AUTHENTICATION」——共鸣匹配验证
- **桌面环境**：状态栏显示「MERIDIAN」设备标识
- **序章系统**：每个游戏首次进入时展示3-5行世界观序章
- **异界档案（LORE）**：桌面第二页的独立阅读器，包含：
  - 根据器物与已发现异界动态生成分类标签
  - 设备背景故事（器物起源 / 连接之核 / 持器者）
  - 每界的普通正文始终可以阅读
  - 达成统计或成就条件后获得对应 Lore 完成度信用
  - 四篇跨世界共鸣档案分别在全局完成度达到 25% / 50% / 75% / 100% 时开放
- **风味文字**：每个游戏的菜单页展示世界观氛围文本
- **全过程双语**：所有文本完整支持中英双语

---

## 🎮 异界一览

| 图标 | 游戏 | 世界名称 | 世界观设定 |
|:---:|------|----------|------------|
| ⚫⚪ | **GOMOKU**<br>五子棋 | 阴阳棋境<br>YIN-YANG BOARD | 混沌与秩序两位古神以黑白棋子推演宇宙命运 |
| 🐍 | **SNAKE**<br>贪吃蛇 | 噬码渊<br>CODE ABYSS | 数字深渊底层的灵蛇，以吞噬数据碎片为生 |
| 🧱 | **BREAKOUT**<br>打砖块 | 星穹壁垒<br>STAR FORTRESS | 失落太空文明留下的能量壁垒与恒星碎片 |
| 🔢 | **2048**<br>数字合成 | 数灵海<br>NUMEN SEA | 纯粹由数字构成的生命体，融合进化的觉醒之路 |
| 💣 | **MINES**<br>扫雷 | 雷原遗迹<br>MINEFIELD RUINS | 大战争百年后的焦土排雷工程师 |
| 🧊 | **TETRIS**<br>俄罗斯方块 | 筑天塔<br>TOWER OF HEAVEN | 异星建筑矩阵从天而降，建造触及真相的通天塔 |
| ✈️ | **AIR RAID**<br>空袭行动 | 守望者战线<br>WARDEN FRONT | 对抗自主战争网络的最后一战 |
| 🛡️ | **TANK DUEL**<br>坦克对决 | 钢铁斗场<br>IRON ARENA | 红蓝双坦克在镜像战场争夺补给，以三分钟积分与骤死决出胜者 |

---

## ✨ 功能亮点

### 🎯 核心体验

- **开机动画**：完整的 MERIDIAN 世界观启动序列，四阶段进度条
- **密码锁屏**：数字键盘 + 删除键，像素风格认证界面
- **桌面环境**：两页图标布局，鼠标拖尾粒子特效，整点时钟动画
- **游戏内菜单**：统一的街机风格 UI，含 Continue / New Game / Settings

### 🏆 成就墙

- 8×6 成就徽章网格
- 点击徽章展开详情卡片（缓出回弹动画）
- 像素艺术关闭按钮
- 解锁进度统计、渐变背景、金色分隔线
- 解锁徽章上显示金色星星标记
- 最多 3 个成就通知可同时叠加显示

### 💾 存档系统

| 功能 | 说明 |
|------|------|
| **自动保存** | 退出游戏时自动保存运行状态 |
| **中断恢复** | 重新进入游戏显示「继续」按钮 |
| **崩溃安全** | 原子写入 + 备份机制，防止存档损坏 |
| **版本迁移** | Schema v5，自动合并旧版存档数据 |
| **跨游戏统计** | 统一的游戏时间、胜率、最佳成绩追踪 |

### ✈️ Air Raid 专属内容

- **飞船皮肤系统**：4 种可解锁皮肤（DEFAULT / CRIMSON / AZURE / GOLD）
- **剧情系统**：序章 + 8 章故事线，全中文剧情
- **故事档案馆**：9 个条目的全屏阅读器
- **16 个标准关卡** + Boss Rush + Challenge 模式
- **武器升级系统**：Cannon / Spread / Laser / Missile

### 🎨 视觉特效

- 统一的色彩调色板（`C` 类集中管理 45+ Air Raid 颜色）
- 桌面粒子系统（鼠标拖尾 / 图标悬停火花 / 整点时钟爆发）
- 游戏专属退出过渡动画（每款游戏反向播放其入场效果）
- Air Raid 三层过渡特效（星空覆盖 + 弹幕帷幕 + 同心雷达环）
- 成就详情卡片装饰边框（Cuphead 风格角标）

### 🌍 本地化

- 运行时动态语言切换
- Fusion Pixel Font（缝合像素字体）简体中文比例宽度版本
- `localization.py` 统一翻译管理，支持批量注册
- 覆盖范围：UI 标签、游戏菜单、成就描述、剧情文本、Lore 条目

### 🛠 开发者工具

- **F10 开发者面板**：鼠标悬停高亮 + 点击激活
- 功能：解锁测试内容、强制结算、调整游戏速度、触发整点特效等
- 仅在当前会话生效，不影响持久化数据

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本 |
|------|------|
| Python | **3.10–3.12** |
| pygame | **2.0+**（<3.0） |
| 操作系统 | Windows / macOS / Linux |

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/CrescentXiong-1/MERIDIAN.git
cd MERIDIAN

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动
python MERIDIAN.py
```

> 💡 **提示**：本项目仅依赖 `pygame`，无其他第三方库。

### 分发给他人

直接将整个 `MERIDIAN` 文件夹打包发送。接收方只需满足上述环境要求即可运行。

---

## 🕹 操作说明

### 通用操作

| 按键 | 功能 |
|:---:|------|
| `ESC` | 返回上级菜单 / 关机（桌面） |
| `Enter` | 确认 / 跳过序章 |
| `方向键 / WASD` | 导航 / 游戏操控 |
| `鼠标` | 桌面图标选择、成就墙交互 |

### 游戏专属操作

| 游戏 | 特殊按键 |
|------|----------|
| **GOMOKU** | 鼠标点击落子，`U` 撤销 |
| **SNAKE** | 方向键控制蛇的移动 |
| **BREAKOUT** | 方向键 / 鼠标控制挡板 |
| **2048** | 方向键合并数字方块 |
| **MINES** | 左键翻开 / 右键标旗 |
| **TETRIS** | `↑` 旋转 / `↓` 软降 / `Space` 硬降 / `C` 暂存 / `P` 暂停 |
| **AIR RAID** | 自动射击；方向键移动 / `Shift` 聚焦 / `Space` 发射导弹 |
| **TANK DUEL（红方）** | `WASD` 八向移动 / `F` 使用道具；自动射击 |
| **TANK DUEL（蓝方）** | `方向键` 八向移动 / `Enter` 使用道具；自动射击 |

Tank Duel 采用地图拾取与单道具槽：维修包恢复 1 HP，护盾抵挡一次伤害，过载短时提升移速与射速，地雷则会留在当前位置等待对手触发。双方初始 3 HP，受击后短暂无敌；三分钟内击毁对手得 1 分，平分时进入骤死。

### 开发者

| 按键 | 功能 |
|:---:|------|
| `F10` | 打开 / 关闭开发者面板 |

---

## 📁 项目结构

```text
MERIDIAN/
├── MERIDIAN.py                  # 程序入口
├── meridian/                    # 主循环、Shell、八款游戏与共享系统
│   ├── shell_*.py               # 开机、认证、桌面和转场
│   ├── gomoku.py … tetris.py    # 六款经典单人游戏
│   ├── air_raid.py              # Air Raid 战役与街机玩法
│   ├── tank_engine.py           # Tank Duel 确定性规则引擎
│   ├── tank_battle.py           # Tank Duel Pygame 表现层
│   └── system.py 等             # 存档、完成度、Lore、本地化、音频与共享 UI
├── tests/                       # 规则、存档、注册与回归测试
├── tools/                       # 发布检查及开发辅助工具
├── assets/                      # 字体等静态资源
├── docs/                        # 多语言说明与设计文档
└── Development_Log/            # 开发记录与决策历史
```

---

## 🏗 架构设计

MERIDIAN 采用 **Mixin 组合模式** 进行架构设计：

```
Game(
    ShellMixin,         # 引导 / 桌面 / 密码 / 过渡
    GomokuMixin,        # 五子棋
    MinesMixin,         # 扫雷
    Game2048Mixin,      # 2048
    BreakoutMixin,      # 打砖块
    SnakeMixin,         # 贪吃蛇
    TetrisMixin,        # 俄罗斯方块
    ArcadeHubMixin,     # 街机公共系统
    AirRaidMixin,       # 空袭行动
    TankBattleMixin,    # 坦克对决表现层
    DeveloperMixin,     # 开发者工具
    SystemMixin,        # 设置 / 成就 / Lore
)
```

### 核心设计模式

| 模式 | 应用 |
|------|------|
| **状态机** | `_EVENT_DISPATCH` + `_UPDATE_DISPATCH` + `_DRAW_DISPATCH` 三表驱动 |
| **有界扩展注册** | 状态、初始化器、桌面图标、Lore 与翻译可在创建 `Game` 前显式注册 |
| **Mixin 组合** | 每个游戏和系统模块通过 Mixin 注入到 `Game` 类 |
| **原子写入** | 存档先写临时文件后重命名，防止写入中断导致损坏 |
| **版本迁移** | `SaveManager._deep_merge()` 自动填充新增字段 |

### 状态流转

```
BOOT → SYSTEM_READY → PASSWORD → DESKTOP
                                    ├── GOMOKU_MENU → GOMOKU_PLAYING → GOMOKU_END
                                    ├── SNAKE_MENU → SNAKE_PLAYING → SNAKE_END
                                    ├── BREAKOUT_MENU → BREAKOUT_PLAYING → BREAKOUT_END
                                    ├── G2048_MENU → G2048_PLAYING → G2048_END
                                    ├── MINES_MENU → MINES_PLAYING → MINES_END
                                    ├── TETRIS_MENU → TETRIS_PLAYING → TETRIS_END
                                    ├── AIR_MENU → AIR_SELECT → AIR_PLAYING → AIR_END
                                    ├── TANK_MENU → TANK_PLAYING → TANK_END
                                    ├── SETTINGS → SYSTEM_SETTINGS / PROFILE
                                    ├── ACHIEVEMENT_WALL
                                    └── LORE_READER → LORE_STORY
```

---

## 🔌 扩展接口

扩展模块须由宿主在创建 `Game()` 前显式导入；项目不自动扫描插件，也不支持热加载或第三方存档协议。注册只影响之后创建的实例。

```python
from meridian.lore import register_game_world, register_lore_entry
from meridian.shell_desktop import register_desktop_icon
from meridian.app import register_game_initializer, register_game_state
from meridian.localization import register_game_translations

def init_mygame(game):
    game.mygame_score = 0

def handle_event(game, event): ...
def update(game): ...
def draw(game): ...

# 1. 注册游戏世界（世界观、序章、风味文字、深层 Lore）
register_game_world(
    "mygame",
    world_name_en="MY WORLD",
    world_name_zh="我的世界",
    world_summary_en="A world of wonder",
    world_summary_zh="奇妙的世界",
    prologue_en=["Line 1", "Line 2", "Line 3"],
    prologue_zh=["第一行", "第二行", "第三行"],
    menu_flavor_en="The crystals hum with ancient power...",
    menu_flavor_zh="水晶随着古老的力量嗡嗡作响…",
    lore_entries=[],
    desktop_subtitle_en="MY WORLD",
    desktop_subtitle_zh="我的世界",
)

# 2. 追加带完成条件的 Lore；正文始终可读，满足条件后计入完成度
register_lore_entry(
    "mygame", "mygame_mastery",
    title_en="CRYSTAL MASTERY", title_zh="水晶精通",
    content_en=["The crystal answers."], content_zh=["水晶作出了回应。"],
    unlock="stat:mygame:score:100",
)

# 3. 注册初始化器、状态处理器与第 3 页桌面入口
register_game_initializer(init_mygame)
register_game_state(
    "MYGAME_MENU",
    event_handler=handle_event,
    update_methods=[update],
    draw_handler=draw,
)
register_desktop_icon(
    "MYGAME", "open_mygame", page=2,
    subtitle_en="MY WORLD", subtitle_zh="我的世界",
    target_state="MYGAME_MENU", transition_effect="fade",
)

# 4. 注册翻译；默认拒绝覆盖其他模块拥有的键
register_game_translations("mygame", {"MYGAME_PLAY": "开始"})
```

`register_game_state()` 的事件、更新和绘制处理器可以是 `Game` 方法名，也可以是接收 `game` 的 callable。桌面图标可使用 `target_state` 转场，或改为 `on_activate(game)` 回调；启用的图标必须且只能选择一种激活方式。翻译键按 `game_id` 记录来源，跨模块冲突默认报错，只有显式传入 `replace=True` 才会覆盖。旧的 `_register_game_states()` 仅作为兼容包装保留。

> 📝 各模块的完整 API 文档请参见源码中的 docstring：`meridian/lore.py`、`meridian/app.py`、`meridian/shell_desktop.py`、`meridian/localization.py`

---

## 📦 打包构建

### Windows 一键构建

```bash
# 运行构建脚本（需要安装 PyInstaller）
BUILD_EXE.bat
```

生成的 `MERIDIAN.exe` 位于 `dist/` 目录下。

### 手动构建

```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --clean MERIDIAN.spec
```

> ⚠️ 构建前请确保 `pygame` 已安装，且 `MERIDIAN.spec` 中的路径配置正确。

---

## 🔎 本地发布检查

在仓库根目录运行只读的发布检查器：

```bash
python tools/check_release.py
```

该命令只检查版本与 `CHANGELOG.md` metadata，以及工作区和本地版本标签的 Git 状态。它不打标签、不推送，也不打包。源码静态检查可另行运行：

```bash
python -m ruff check MERIDIAN.py meridian tools
python -m compileall -q MERIDIAN.py meridian tools
```

---

## 📝 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

### 最新稳定版本 V3.2.0 (2026-07-13) — 「Tank Duel」

- 🎮 **本地双人对战**：红方 WASD、蓝方方向键，支持八向移动、后按键优先与自动射击
- 🧰 **八种战术道具**：修复、护盾、加速、地雷、EMP、穿甲弹、烟雾与传送，采用单道具槽
- ⚔️ **完整对局规则**：3 分钟、每方 3 HP、随机安全重生、平局骤死与中心镜像地图
- 🏆 **完整系统集成**：新增 12 项成就、中英文文本、动态配乐、专属转场与对局统计
- 💾 **中断恢复**：存档 Schema 升级至 v5，支持 Tank Duel 对局快照恢复

稳定版之后完成的修缮记录在 [CHANGELOG.md](CHANGELOG.md) 的 `Unreleased` 小节，不作为已发布的 v3.3 宣传。

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！无论是 Bug 报告、功能建议还是代码提交。

### 贡献流程

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'feat: add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 发起 **Pull Request**

### 提交规范

本项目采用 [约定式提交](https://www.conventionalcommits.org/zh-hans/)：
- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建 / 工具

### 开发建议

- 新游戏请使用扩展接口注册，避免直接修改 `app.py`
- 世界观文本请同时提供中英双语版本
- 存档 Schema 变更需递增 `SCHEMA_VERSION` 并提供迁移逻辑

---

## 📄 开源协议

本项目基于 **MIT License** 开源。

内置字体 **Fusion Pixel Font（缝合像素字体）** 采用 [SIL Open Font License 1.1](assets/fonts/FusionPixelFont-LICENSE-OFL.txt)。

---

## 🙏 致谢

- **[Pygame](https://www.pygame.org/)** — 游戏开发框架
- **[Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font)** — 缝合像素字体，提供优美的简体中文字体支持
- **所有贡献者** — 感谢每一位为 MERIDIAN 做出贡献的开发者

---

<p align="center">
  <sub>MERIDIAN · 诸界 · 一器 · Many Worlds. One Device.</sub>
</p>
