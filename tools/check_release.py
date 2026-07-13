"""Read-only checks for local release metadata and Git state."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_version_module(repo: Path) -> ModuleType:
    version_file = repo / "meridian" / "version.py"
    spec = importlib.util.spec_from_file_location("meridian_release_version", version_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {version_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_metadata(repo: Path) -> list[str]:
    """Return release metadata problems without changing the repository."""
    version = _load_version_module(repo).__version__
    changelog = repo / "CHANGELOG.md"
    if not changelog.is_file():
        return ["CHANGELOG.md is missing"]
    try:
        text = changelog.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["CHANGELOG.md is not valid UTF-8"]
    if f"[{version}]" not in text:
        return ["version missing from CHANGELOG.md"]
    return []


def _run_git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def check_git(repo: Path, version: str) -> list[str]:
    """Return local Git-state problems using read-only commands."""
    problems = []
    if _run_git(repo, "status", "--porcelain").strip():
        problems.append("working tree is not clean")
    tag = f"v{version}"
    if _run_git(repo, "tag", "--list", tag).strip():
        problems.append(f"local tag {tag} already exists")
    return problems


def main() -> int:
    version = _load_version_module(REPO_ROOT).__version__
    problems = check_metadata(REPO_ROOT) + check_git(REPO_ROOT, version)
    if problems:
        print(*problems, sep="\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
