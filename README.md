<p align="center">
  <img src="assets/banner.png" alt="MERIDIAN Banner" width="800" onerror="this.style.display='none'">
</p>

<h1 align="center">🌐 MERIDIAN · 子午线</h1>

<p align="center"><strong>七界 · 一器</strong></p>
<p align="center"><em>Seven Worlds. One Device.</em></p>

<p align="center">
  <img src="https://github.com/CrescentXiong-1/MERIDIAN/actions/workflows/ci.yml/badge.svg" alt="CI Status">
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python">
  <img src="https://img.shields.io/badge/pygame-2.x-green" alt="Pygame">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
  <img src="https://img.shields.io/badge/tests-50%2B-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/lines-~15%2C700-orange" alt="Lines of Code">
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
- [七界一览](#-七界一览)
- [功能亮点](#-功能亮点)
- [快速开始](#-快速开始)
- [操作说明](#-操作说明)
- [项目结构](#-项目结构)
- [架构设计](#-架构设计)
- [扩展接口](#-扩展接口)
- [打包构建](#-打包构建)
- [测试](#-测试)
- [更新日志](#-更新日志)
- [贡献指南](#-贡献指南)
- [开源协议](#-开源协议)
- [致谢](#-致谢)

---

## 🌌 简介

**MERIDIAN（子午线）** 是一台来历不明的掌上器物。它的"屏幕"并非普通显示屏，而是一面 **共鸣透镜**——七块现实碎片被封存在七个经典街机游戏中，每一个游戏都是通向一个独立世界的稳定门户。

这不是一台普通的游戏机。它是一台**跨维度观测设备**。

本项目使用 **Python + Pygame** 构建，是一个完整的多游戏平台模拟器。它融合了：

- 🎮 **七款经典街机游戏**的完整复刻
- 📚 **深度的世界观叙事系统**，每个游戏都有独立的故事背景
- 🏆 **50+ 成就系统**，跨游戏追踪玩家进度
- 🌍 **完整的双语支持**（简体中文 / English）
- 💾 **崩溃安全的持久化存档**，支持游戏中断恢复
- 🎵 **程序化音频引擎**，动态生成 BGM 和音效
- 🛠 **内置开发者面板**，方便调试和测试

> 语言版本：中文（本文）| English（即将推出）

---

## 🌠 世界观

MERIDIAN 不仅仅是一个游戏合集——它拥有一套完整的**元叙事**框架：

- **开机序列**：共鸣校准 → 维度扫描 → 锚点稳定 → 核心连接
- **密码认证**：「NEXUS AUTHENTICATION」——共鸣匹配验证
- **桌面环境**：状态栏显示「MERIDIAN」设备标识
- **序章系统**：每个游戏首次进入时展示3-5行世界观序章
- **异界档案（LORE）**：桌面第二页的独立阅读器，包含：
  - 8 个分类标签（器物起源 + 七界）
  - 设备背景故事（器物起源 / 连接之核 / 持器者）
  - 每界 1-2 条深层故事条目
  - 通过游戏统计或成就解锁隐藏内容
- **风味文字**：每个游戏的菜单页展示世界观氛围文本
- **全过程双语**：所有文本完整支持中英双语

---

## 🎮 七界一览

| 图标 | 游戏 | 世界名称 | 世界观设定 |
|:---:|------|----------|------------|
| ⚫⚪ | **GOMOKU**<br>五子棋 | 阴阳棋境<br>YIN-YANG BOARD | 混沌与秩序两位古神以黑白棋子推演宇宙命运 |
| 🐍 | **SNAKE**<br>贪吃蛇 | 噬码渊<br>CODE ABYSS | 数字深渊底层的灵蛇，以吞噬数据碎片为生 |
| 🧱 | **BREAKOUT**<br>打砖块 | 星穹壁垒<br>STAR FORTRESS | 失落太空文明留下的能量壁垒与恒星碎片 |
| 🔢 | **2048**<br>数字合成 | 数灵海<br>NUMEN SEA | 纯粹由数字构成的生命体，融合进化的觉醒之路 |
| 💣 | **MINES**<br>扫雷 | 雷原遗迹<br>MINEFIELD RUINS | 大战争百年后的焦土排雷工程师 |
| 🧊 | **TETRIS**<br>俄罗斯方块 | 筑天塔<br>TOWER OF HEAVEN | 异星建筑矩阵从天而降，建造触及真相的通天塔 |
| ✈️ | **AIR RAID**<br>空袭行动 | 守望者战线<br>WARDEN FRONT | 对抗自主战争网络的最后一战 |

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
| **版本迁移** | Schema v4，自动合并旧版存档数据 |
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
- 功能：解锁全部关卡、解锁全部皮肤、触发整点特效、清空存档等
- 仅在当前会话生效，不影响持久化数据

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本 |
|------|------|
| Python | **3.10+** |
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
| **AIR RAID** | 方向键移动 / `Z` 射击 / `X` 导弹 / `Shift` 聚焦模式 |

### 开发者

| 按键 | 功能 |
|:---:|------|
| `F10` | 打开 / 关闭开发者面板 |

---

## 📁 项目结构

```
MERIDIAN/
├── MERIDIAN.py                  # 入口文件
├── MERIDIAN.spec                # PyInstaller 打包配置
├── BUILD_EXE.bat                # Windows 一键构建脚本
├── requirements.txt             # Python 依赖
├── reasonix.toml                # 编辑器配置
│
├── meridian/                    # 核心包
│   ├── __init__.py
│   ├── app.py                   # 游戏组合、主循环、状态分发
│   ├── common.py                # 全局常量、颜色类、布局参数
│   ├── lore.py                  # 世界观数据与注册 API
│   ├── audio.py                 # 程序化 BGM 与音效引擎
│   ├── persistence.py           # 版本化崩溃安全存档管理
│   ├── localization.py          # 运行时双语系统 + 中文字体
│   ├── developer.py             # 开发者面板（仅会话有效）
│   │
│   ├── shell.py                 # Shell 系统聚合
│   ├── shell_boot.py            # 开机引导序列
│   ├── shell_password.py        # 密码锁屏认证
│   ├── shell_desktop.py         # 桌面环境与图标系统
│   ├── shell_transitions.py     # 场景过渡动画
│   │
│   ├── arcade_common.py         # 街机游戏公共 UI + 序章系统
│   ├── arcade_levels.py         # Air Raid 关卡数据
│   │
│   ├── gomoku.py                # 五子棋（阴阳棋境）
│   ├── snake.py                 # 贪吃蛇（噬码渊）
│   ├── breakout.py              # 打砖块（星穹壁垒）
│   ├── g2048.py                 # 2048（数灵海）
│   ├── mines.py                 # 扫雷（雷原遗迹）
│   ├── tetris.py                # 俄罗斯方块（筑天塔）
│   ├── air_raid.py              # 空袭行动（守望者战线）
│   │
│   └── system.py                # 设置、档案、成就、Lore 阅读器
│
├── assets/                      # 静态资源
│   └── fonts/                   # Fusion Pixel Font（SIL Open License 1.1）
│
├── tests/                       # 测试套件（50+ 测试）
│   ├── conftest.py              # 共享 fixtures + SDL 虚拟驱动
│   ├── test_smoke.py            # 冒烟测试
│   ├── test_arcade_games.py     # 街机游戏测试
│   └── test_persistence.py      # 持久化系统测试
│
└── .github/workflows/
    └── ci.yml                   # GitHub Actions CI（Windows, Python 3.10-3.12）
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
    DeveloperMixin,     # 开发者工具
    SystemMixin,        # 设置 / 成就 / Lore
)
```

### 核心设计模式

| 模式 | 应用 |
|------|------|
| **状态机** | `_EVENT_DISPATCH` + `_UPDATE_DISPATCH` + `_DRAW_DISPATCH` 三表驱动 |
| **动态注册** | `_GAME_STATE_REGISTRY` 支持新游戏免修改 `app.py` |
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
                                    ├── SETTINGS → SYSTEM_SETTINGS / PROFILE
                                    ├── ACHIEVEMENT_WALL
                                    └── LORE_READER → LORE_STORY
```

---

## 🔌 扩展接口

为新游戏预留了完整的注册 API，以下函数覆盖从世界观到桌面图标的全部集成：

```python
from meridian.lore import register_game_world, register_device_lore
from meridian.shell_desktop import register_desktop_icon
from meridian.app import _register_game_states
from meridian.localization import register_game_translations

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
    lore_entries=[...],
    desktop_subtitle_en="MY WORLD",
    desktop_subtitle_zh="我的世界",
)

# 2. 注册桌面图标
register_desktop_icon("MYGAME", "open_mygame", page=0, ...)

# 3. 动态注册状态分发（免修改 app.py）
_register_game_states("MYGAME_MENU", "_handle_mygame_menu", [], "_draw_mygame_menu")

# 4. 注册翻译条目
register_game_translations("mygame", {"PLAY": "开始", "SCORE": "得分"})
```

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

## 🧪 测试

项目包含 **50+ 单元测试**，覆盖核心模块：

```bash
# 运行全部测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_smoke.py -v
python -m pytest tests/test_arcade_games.py -v
python -m pytest tests/test_persistence.py -v
```

### 测试覆盖范围

| 测试文件 | 内容 |
|----------|------|
| `test_smoke.py` | 冒烟测试：游戏启动、状态流转、基本渲染 |
| `test_arcade_games.py` | 街机游戏：菜单交互、游戏逻辑、存档恢复 |
| `test_persistence.py` | 持久化：读写存档、版本迁移、崩溃恢复 |

### CI / CD

通过 GitHub Actions 在 **Windows** 平台上对 **Python 3.10 / 3.11 / 3.12** 进行自动化测试。每次 Push 和 Pull Request 均触发。

---

## 📝 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

### 最新版本 V3.1.0 (2026-07-02) — 「MERIDIAN」

- 🌌 **世界观系统**：元叙事框架，七界设定，序章系统，异界档案
- 🔌 **扩展接口**：5 个注册函数，新游戏零修改集成
- 🏆 **成就墙**：V3.0.0 引入，V3.1.0 优化视觉
- 💾 **中断恢复**：全部 7 款游戏支持存档恢复
- ✈️ **Air Raid 剧情**：8 章故事线 + 档案阅读器
- 🎨 **视觉增强**：桌面粒子、退出过渡动画、色彩统一

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
- 确保 `python -m pytest tests/ -v` 全部通过
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
  <sub>MERIDIAN · 七界 · 一器 · Seven Worlds. One Device.</sub>
</p>
