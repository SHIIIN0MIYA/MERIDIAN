"""Read-only checks for local release metadata and Git state."""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
RELEASE_TAG = "v3.2.0"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_version(repo: Path) -> str:
    version_file = repo / "meridian" / "version.py"
    tree = ast.parse(version_file.read_text(encoding="utf-8"), filename=str(version_file))
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == "__version__":
            version = ast.literal_eval(node.value)
            if isinstance(version, str):
                return version
    raise ValueError(f"__version__ string not found in {version_file}")


def check_metadata(repo: Path) -> list[str]:
    """Return release metadata problems without changing the repository."""
    version = _load_version(repo)
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


def check_git(repo: Path) -> list[str]:
    """Return local Git-state problems using read-only commands."""
    problems = []
    if _run_git(repo, "status", "--porcelain").strip():
        problems.append("working tree is not clean")
    if _run_git(repo, "tag", "--list", RELEASE_TAG).strip():
        problems.append(f"local tag {RELEASE_TAG} already exists")
    return problems


def main() -> int:
    problems = check_metadata(REPO_ROOT) + check_git(REPO_ROOT)
    if problems:
        print(*problems, sep="\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
