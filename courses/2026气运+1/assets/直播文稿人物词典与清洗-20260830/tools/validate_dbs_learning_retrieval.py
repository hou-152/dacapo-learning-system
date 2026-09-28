#!/usr/bin/env python3
"""Replay the dbs-learning source route for the livestream corpus assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-dir", required=True, type=Path)
    parser.add_argument("--resolver", required=True, type=Path)
    parser.add_argument("--installed-skill", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    course_dir = args.course_dir.resolve()
    plan = course_dir / "00-学习计划.md"
    asset_root = course_dir / "assets" / "直播文稿人物词典与清洗-20260830"
    relative_targets = [
        "assets/直播文稿人物词典与清洗-20260830/README.md",
        "assets/直播文稿人物词典与清洗-20260830/profile/人物背景与表达画像.md",
        "assets/直播文稿人物词典与清洗-20260830/dictionary/常用词与口头禅.md",
        "assets/直播文稿人物词典与清洗-20260830/dictionary/typeless-like-dictionary.json",
        "assets/直播文稿人物词典与清洗-20260830/audit/ADVERSARIAL-AUDIT.md",
    ]
    plan_text = plan.read_text(encoding="utf-8")
    checks = []
    for relative in relative_targets:
        path = course_dir / relative
        completed = subprocess.run(
            ["python3", str(args.resolver), "check", "--path", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        checks.append(
            {
                "relative_path": relative,
                "listed_in_plan": relative in plan_text,
                "resolver_ok": payload.get("ok") is True and payload.get("status") == "readable",
                "selected_path": payload.get("selected_path"),
                "sha256": sha256(path),
            }
        )

    raw_files = sorted((asset_root / "raw").glob("*.md"))
    clean_files = sorted((asset_root / "cleaned").glob("*.md"))
    result = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "course_dir": str(course_dir),
        "plan": str(plan),
        "plan_sha256": sha256(plan),
        "installed_skill": str(args.installed_skill),
        "installed_skill_realpath": str(args.installed_skill.resolve()),
        "canonical_skill_realpath": str((course_dir.parents[1] / "09-Skills" / "dbs-learning" / "SKILL.md").resolve()),
        "skill_realpath_aligned": args.installed_skill.resolve() == (course_dir.parents[1] / "09-Skills" / "dbs-learning" / "SKILL.md").resolve(),
        "checks": checks,
        "all_plan_entries_present": all(item["listed_in_plan"] for item in checks),
        "all_resolver_checks_readable": all(item["resolver_ok"] for item in checks),
        "raw_document_count": len(raw_files),
        "clean_document_count": len(clean_files),
        "raw_clean_filename_bijection": [path.name for path in raw_files] == [path.name for path in clean_files],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "skill_realpath_aligned": result["skill_realpath_aligned"],
        "all_plan_entries_present": result["all_plan_entries_present"],
        "all_resolver_checks_readable": result["all_resolver_checks_readable"],
        "raw_document_count": result["raw_document_count"],
        "clean_document_count": result["clean_document_count"],
        "raw_clean_filename_bijection": result["raw_clean_filename_bijection"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
