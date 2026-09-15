# 贡献指南

我们欢迎任何形式的贡献！无论是 Bug 报告、功能建议还是代码提交。

## 目录

- [环境准备](#环境准备)
- [开发流程](#开发流程)
- [提交规范](#提交规范)
- [测试](#测试)
- [代码质量](#代码质量)
- [文档要求](#文档要求)
- [发布检查](#发布检查)

---

## 环境准备

```bash
# 1. 克隆仓库
git clone https://github.com/CrescentXiong-1/MERIDIAN.git
cd MERIDIAN

# 2. 安装依赖（仅 pygame）
pip install -r requirements.txt

# 3. 开发时额外安装
pip install ruff pytest pyinstaller
```

## 开发流程

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'feat: add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 发起 **Pull Request**

## 提交规范

本项目采用 [约定式提交](https://www.conventionalcommits.org/zh-hans/)：

- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建 / 工具

## 测试

CI 会在 **Python 3.10 / 3.11 / 3.12 × Ubuntu / Windows** 矩阵上运行测试，请确保提交前本地测试全部通过：

```bash
python -m pytest
```

- 测试使用无头 SDL 驱动（`tests/conftest.py` 统一配置），无需图形环境
- 新增功能必须附带对应测试：规则逻辑放入独立引擎（如 `tank_engine.py`）并直接测试，表现层测试走场景工厂
- 修复 Bug 时请先添加复现该 Bug 的回归测试

## 代码质量

```bash
# Lint（CI 使用同一命令）
python -m ruff check MERIDIAN.py meridian tools tests

# 编译检查
python -m compileall -q MERIDIAN.py meridian tools
```

- 行宽上限 100 字符，统一双引号（见 `pyproject.toml`）
- 新游戏请使用扩展接口注册，避免直接修改 `app.py`（详见 README「扩展接口」章节）
- 存档 Schema 变更需递增 `SCHEMA_VERSION` 并提供迁移逻辑

## 文档要求

- 世界观文本请同时提供中英双语版本
- 游戏菜单、成就、Lore 等用户可见文本通过 `localization.py` 统一管理
- 重要用户可见变化请同步更新 [CHANGELOG.md](CHANGELOG.md) 的 `Unreleased` 区段
- 若 README 中描述的功能发生变化，请同步更新根 README 及各语言译文（`docs/readme/`）

## 发布检查

正式发布前，在仓库根目录运行只读的发布检查器：

```bash
python tools/check_release.py
```

它检查版本号、`CHANGELOG.md` 元数据与 Git 标签的一致性。它不打标签、不推送、不打包。

---

感谢每一位为 MERIDIAN 做出贡献的开发者！
