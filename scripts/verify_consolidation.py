#!/usr/bin/env python3
"""只读验证统一真源、迁移快照与兼容入口。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def tree_hash(root: Path) -> tuple[str, int, int]:
    digest = hashlib.sha256()
    count = 0
    size = 0
    files = sorted(
        (path for path in root.rglob("*") if path.is_file() and not path.is_symlink()),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    for path in files:
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        file_hash = hashlib.sha256(data).hexdigest()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
        count += 1
        size += len(data)
    return digest.hexdigest(), count, size


def resolved(path: Path) -> str | None:
    try:
        return str(path.resolve(strict=True))
    except FileNotFoundError:
        return None


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, ok: bool, **details: object) -> None:
        checks.append({"name": name, "ok": ok, **details})

    required = [
        "01-原始素材区",
        "02-课程真源",
        "04-用户原话与费曼",
        "05-证据原子",
        "09-Skills/dbs-learning",
        "09-Skills/dbs-learning-strict",
        "10-历史资产",
    ]
    for relative in required:
        path = ROOT / relative
        check(f"required:{relative}", path.is_dir(), path=str(path))

    links = {
        "/Users/housibo/Documents/交互式学习/交互式学习真源": ROOT,
        "/Users/housibo/Documents/dbskill-learning": ROOT / "02-课程真源",
        "/Users/housibo/Documents/工程化 skill/skills/dbs-learning": ROOT / "09-Skills/dbs-learning",
        "/Users/housibo/Documents/工程化 skill/skills/dbs-learning-strict": ROOT / "09-Skills/dbs-learning-strict",
        "/Users/housibo/.agents/skills/dbs-learning": ROOT / "09-Skills/dbs-learning",
        "/Users/housibo/.agents/skills/dbs-learning-strict": ROOT / "09-Skills/dbs-learning-strict",
        "/Users/housibo/.claude/skills/dbs-learning": ROOT / "09-Skills/dbs-learning",
        "/Users/housibo/.claude/skills/dbs-learning-strict": ROOT / "09-Skills/dbs-learning-strict",
        "/Users/housibo/.codex/skills/dbs-learning": ROOT / "09-Skills/dbs-learning",
        "/Users/housibo/.codex/skills/dbs-learning-strict": ROOT / "09-Skills/dbs-learning-strict",
    }
    for raw_path, expected in links.items():
        path = Path(raw_path)
        actual = resolved(path)
        expected_resolved = resolved(expected)
        check(
            f"link:{raw_path}",
            path.is_symlink() and actual == expected_resolved,
            actual=actual,
            expected=expected_resolved,
        )

    physical_root = Path("/Users/housibo/Documents/DaCapo 内容资产/01-交互式学习")
    check(
        "physical-root:DaCapo",
        not physical_root.is_symlink() and resolved(physical_root) == str(ROOT),
        actual=resolved(physical_root),
        expected=str(ROOT),
    )

    snapshots = {
        ROOT / "01-原始素材区/迁移前真源/2026-08-19_dbskill-learning": "cf2f5d907765a20ceceaa585889b1b48038eed2582e2e536cb57e2cac3da84e0",
        ROOT / "10-历史资产/Agent交互式学习": "d46dce332ad44bf303e9f595b0ba788f81b32f3b247ad1bac020bb789c81f3ac",
    }
    for path, expected_hash in snapshots.items():
        actual_hash, file_count, byte_count = tree_hash(path)
        check(
            f"tree:{path.name}",
            actual_hash == expected_hash,
            actual=actual_hash,
            expected=expected_hash,
            files=file_count,
            bytes=byte_count,
        )

    truth = (ROOT / "SOURCE_OF_TRUTH.md").read_text(encoding="utf-8")
    start = "<!-- DBS_LEARNING_RUNTIME_CONFIG_START -->"
    end = "<!-- DBS_LEARNING_RUNTIME_CONFIG_END -->"
    check("runtime-config-markers", truth.count(start) == 1 and truth.count(end) == 1)

    canonical_plan = ROOT / "02-课程真源/拜物教/00-学习计划.md"
    archived_plan = ROOT / "01-原始素材区/迁移前真源/2026-08-19_DaCapo-课程真源/拜物教/00-学习计划.md"
    check(
        "course-conflict:拜物教",
        canonical_plan.read_bytes() == archived_plan.read_bytes(),
        canonical=str(canonical_plan),
        selected_from=str(archived_plan),
    )
    check(
        "current-course:双向钢人论证与深度思考Prompt",
        (ROOT / "02-课程真源/双向钢人论证与深度思考Prompt/02.md").is_file(),
    )

    ok = all(bool(item["ok"]) for item in checks)
    print(json.dumps({"ok": ok, "root": str(ROOT), "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
