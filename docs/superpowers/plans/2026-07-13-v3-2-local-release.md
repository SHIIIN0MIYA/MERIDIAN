# MERIDIAN v3.2.0 本地发布实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将当前 Tank Duel 版本整理为可验证、可追踪但不推送的本地 `v3.2.0` 稳定节点。

**Architecture:** 用 `meridian/version.py` 提供唯一版本号，以纯检查脚本验证版本、日志、Git 状态和质量门槛。发布日志与标签创建分离，脚本不执行打包、推送或打标签。

**Tech Stack:** Python 3.10–3.12、pytest、Ruff、Git、Markdown、Pygame 2.x。

## Global Constraints

- 不运行 PyInstaller、`BUILD_EXE.bat` 或任何打包命令。
- 不推送 GitHub 或 Gitee。
- 创建 `v3.2.0` 注释标签前必须再次取得用户确认。
- `v3.2.0` 不依赖尚未开发的 v3.3 截图测试。
- 每项修改使用 TDD，并在提交前运行 `git diff --check`。

---

### Task 1: 唯一版本号来源

**Files:**
- Create: `meridian/version.py`
- Modify: `meridian/__init__.py`
- Modify: `meridian/shell_desktop.py`
- Test: `tests/test_version.py`

**Interfaces:**
- Produces: `meridian.version.__version__: str`
- Produces: `meridian.version.version_label() -> str`

- [ ] **Step 1: 写失败测试**

```python
from meridian.version import __version__, version_label

def test_release_version_has_one_canonical_value():
    assert __version__ == "3.2.0"
    assert version_label() == "MERIDIAN 3.2.0"
```

- [ ] **Step 2: 确认测试先失败**

Run: `python -m pytest tests/test_version.py -q -p no:cacheprovider`  
Expected: FAIL，提示 `meridian.version` 不存在。

- [ ] **Step 3: 最小实现并接入桌面**

```python
# meridian/version.py
__version__ = "3.2.0"

def version_label() -> str:
    return f"MERIDIAN {__version__}"
```

在 `meridian/__init__.py` 导出 `__version__`。在桌面状态栏或设置页的版本位置调用 `version_label()`，禁止复制字符串 `3.2.0`。

- [ ] **Step 4: 验证**

Run: `python -m pytest tests/test_version.py tests/test_smoke.py -q -p no:cacheprovider`  
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add meridian/version.py meridian/__init__.py meridian/shell_desktop.py tests/test_version.py
git commit -m "feat: add canonical MERIDIAN version"
```

### Task 2: 重建 v3.2.0 更新日志顶部

**Files:**
- Modify: `CHANGELOG.md`
- Test: `tests/test_release_metadata.py`

**Interfaces:**
- Consumes: `meridian.version.__version__`
- Produces: UTF-8 Changelog，包含 `Unreleased` 与 `[3.2.0] - 2026-07-13`

- [ ] **Step 1: 写日志结构测试**

```python
from pathlib import Path

def test_changelog_declares_unreleased_and_v320():
    text = Path("CHANGELOG.md").read_text(encoding="utf-8")
    assert text.startswith("# Changelog\n")
    assert "## [Unreleased]" in text
    assert "## [3.2.0] - 2026-07-13" in text
    assert "Tank Duel" in text and "坦克对决" in text
    assert "�" not in text
```

- [ ] **Step 2: 确认当前乱码导致失败**

Run: `python -m pytest tests/test_release_metadata.py -q -p no:cacheprovider`  
Expected: FAIL，命中结构缺失或替换字符检查。

- [ ] **Step 3: 整理日志**

顶部必须包含：

```markdown
# Changelog

## [Unreleased]

### Added

### Changed

### Fixed

## [3.2.0] - 2026-07-13

### Added
- 新增本地双人游戏 Tank Duel（坦克对决）。
- 新增八种战术道具与十二项坦克成就。
```

继续写明输入、三分钟积分、3 HP、骤死、Schema v5、统计、恢复、双语、音乐、转场和视觉修复。保留可正确解码的旧版本历史；对无法可靠恢复的乱码段落使用 Git 历史核对后重写摘要，不凭空猜测。

- [ ] **Step 4: 验证**

Run: `python -m pytest tests/test_release_metadata.py -q -p no:cacheprovider`  
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add CHANGELOG.md tests/test_release_metadata.py
git commit -m "docs: prepare v3.2.0 changelog"
```

### Task 3: 只读发布检查器

**Files:**
- Create: `tools/check_release.py`
- Test: `tests/test_release_check.py`
- Modify: `README.md`

**Interfaces:**
- Produces: `check_metadata(repo: Path) -> list[str]`
- Produces: CLI exit 0（通过）或 1（列出问题）

- [ ] **Step 1: 写纯函数失败测试**

```python
from pathlib import Path
from tools.check_release import check_metadata

def test_release_check_accepts_repository_metadata():
    assert check_metadata(Path.cwd()) == []
```

另写临时目录测试，制造版本与 Changelog 不一致并断言返回 `version missing from CHANGELOG.md`。

- [ ] **Step 2: 确认模块不存在**

Run: `python -m pytest tests/test_release_check.py -q -p no:cacheprovider`  
Expected: FAIL。

- [ ] **Step 3: 实现检查器**

```python
def check_metadata(repo: Path) -> list[str]:
    issues = []
    changelog = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"[{__version__}]" not in changelog:
        issues.append("version missing from CHANGELOG.md")
    return issues
```

CLI 另外通过 `subprocess.run(["git", "status", "--porcelain"], ...)` 检查工作树，通过 `git tag --list v3.2.0` 检查重复标签。不得调用 `git tag`、`git push`、PyInstaller 或构建命令。

- [ ] **Step 4: 文档与验证**

README 写明：

```powershell
python tools/check_release.py
```

Run: `python -m pytest tests/test_release_check.py -q -p no:cacheprovider`  
Expected: PASS。

- [ ] **Step 5: 提交**

```bash
git add tools/check_release.py tests/test_release_check.py README.md
git commit -m "chore: add local release checks"
```

### Task 4: v3.2.0 发布候选验证与标签确认门

**Files:**
- Modify only if validation reveals a release-blocking defect.

**Interfaces:**
- Produces: clean `master` release candidate ready for user tag confirmation.

- [ ] **Step 1: 运行发布检查**

Run: `python tools/check_release.py`  
Expected: exit 0；若仅因当前计划提交未完成导致工作树不净，先完成计划内提交后重跑。

- [ ] **Step 2: 完整质量门槛**

```powershell
python -m pytest tests/ -q -p no:cacheprovider
python -m ruff check MERIDIAN.py meridian tests tools
python -m compileall -q MERIDIAN.py meridian tests tools
git diff --check
git status --short --branch
```

Expected: 全部 exit 0，pytest 无失败，工作树无跟踪改动。

- [ ] **Step 3: 报告候选状态并暂停**

向用户报告版本、提交、测试数量和当前标签状态，明确询问是否创建本地 `v3.2.0` 注释标签。未获得确认不得继续。

- [ ] **Step 4: 仅在确认后创建标签**

```bash
git tag -a v3.2.0 -m "MERIDIAN 3.2.0 - Tank Duel"
git show --no-patch --decorate v3.2.0
```

Expected: 标签指向已验证的发布提交。不要 push。

