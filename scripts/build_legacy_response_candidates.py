#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
LEARNING_ROOT = SCRIPT_PATH.parents[1]
PROJECT_ROOT = LEARNING_ROOT.parent
COURSE_ROOT = LEARNING_ROOT / "02-课程真源"
DEFAULT_MANIFEST = (
    LEARNING_ROOT
    / "04-用户原话与费曼"
    / "legacy-response-candidate-manifest.json"
)
DEFAULT_OUTPUT = (
    LEARNING_ROOT / "04-用户原话与费曼" / "legacy-response-candidates.jsonl"
)
DEFAULT_VIEW = (
    LEARNING_ROOT / "04-用户原话与费曼" / "待核验旧课原话候选.md"
)
REMOVAL_REVIEW_ROOT = (
    PROJECT_ROOT / "02-内容系统/03-处理状态/摄取队列/来源生命周期"
)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def stable_candidate_id(
    source_relative_path: str,
    source_sha256: str,
    start_line: int,
    end_line: int,
    verbatim: str,
) -> str:
    payload = "\x1f".join(
        (source_relative_path, source_sha256, str(start_line), str(end_line), verbatim)
    ).encode("utf-8")
    return "legacy_cand_" + hashlib.sha256(payload).hexdigest()[:20]


def removal_fallbacks(project_root: Path) -> dict[str, Path]:
    root = project_root / "02-内容系统/03-处理状态/摄取队列/来源生命周期"
    result: dict[str, Path] = {}
    if not root.is_dir():
        return result
    for path in sorted(root.glob("SRCREV-*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("task_type") != "review_source_removal":
            continue
        source = value.get("source") or {}
        if source.get("root_id") != "canonical_courses":
            continue
        relative = str(source.get("relative_path") or "")
        snapshot = str(source.get("snapshot_relative_path") or "")
        if not relative or not snapshot:
            continue
        canonical = (
            Path("01-交互式学习/02-课程真源") / relative
        ).as_posix()
        candidate = project_root / snapshot
        if not candidate.is_file() or sha256(candidate) != source.get("sha256"):
            raise ValueError(f"来源删除审查的快照无效：{path}")
        result[canonical] = candidate
    return result


def resolve_candidate_source(
    project_root: Path,
    source_relative: str,
    fallbacks: dict[str, Path] | None = None,
) -> tuple[Path, str | None]:
    canonical = project_root / source_relative
    if canonical.is_file():
        return canonical, None
    fallback = (fallbacks or removal_fallbacks(project_root)).get(source_relative)
    if fallback is None:
        raise ValueError(f"候选来源不存在：{canonical}")
    return fallback, fallback.relative_to(project_root).as_posix()


def locate_exact_span(
    source_text: str,
    start_line: int,
    end_line: int,
    verbatim: str,
) -> dict[str, int]:
    lines = source_text.splitlines()
    if start_line < 1 or end_line < start_line or end_line > len(lines):
        raise ValueError(f"非法行范围：{start_line}-{end_line}／共 {len(lines)} 行")
    selected = "\n".join(lines[start_line - 1 : end_line])
    start = selected.find(verbatim)
    if start < 0:
        raise ValueError(f"候选文本不在行范围内：{start_line}-{end_line}")
    if selected.find(verbatim, start + 1) >= 0:
        raise ValueError(f"候选文本在行范围内不唯一：{start_line}-{end_line}")
    prefix = selected[:start]
    start_line_offset = prefix.count("\n")
    start_column = len(prefix.rsplit("\n", 1)[-1]) + 1
    end_prefix = selected[: start + len(verbatim)]
    end_line_offset = end_prefix.count("\n")
    end_column_exclusive = len(end_prefix.rsplit("\n", 1)[-1]) + 1
    return {
        "start_line": start_line + start_line_offset,
        "start_column": start_column,
        "end_line": start_line + end_line_offset,
        "end_column_exclusive": end_column_exclusive,
    }


def build_candidates(manifest: dict[str, Any], project_root: Path) -> list[dict[str, Any]]:
    if manifest.get("schema_version") != "legacy-response-candidate-manifest/v1":
        raise ValueError("legacy candidate manifest schema 非法")
    candidates = manifest.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("manifest.candidates 必须是列表")

    result: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    seen_ids: set[str] = set()
    fallbacks = removal_fallbacks(project_root)
    for index, item in enumerate(candidates, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"第 {index} 个候选不是对象")
        key = str(item.get("key", "")).strip()
        if not key or key in seen_keys:
            raise ValueError(f"候选 key 缺失或重复：{key}")
        seen_keys.add(key)
        source_relative = str(item.get("source_relative_path", "")).strip()
        relative = Path(source_relative)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"候选来源路径非法：{source_relative}")
        source, snapshot_relative = resolve_candidate_source(
            project_root, source_relative, fallbacks
        )
        text = source.read_text(encoding="utf-8")
        verbatim = item.get("verbatim")
        if not isinstance(verbatim, str) or not verbatim:
            raise ValueError(f"候选逐字文本为空：{key}")
        declared = item.get("locator") or {}
        start_line = declared.get("start_line")
        end_line = declared.get("end_line")
        if not isinstance(start_line, int) or not isinstance(end_line, int):
            raise ValueError(f"候选行号非法：{key}")
        exact_span = locate_exact_span(text, start_line, end_line, verbatim)
        source_hash = sha256(source)
        candidate_id = stable_candidate_id(
            source_relative,
            source_hash,
            start_line,
            end_line,
            verbatim,
        )
        if candidate_id in seen_ids:
            raise ValueError(f"候选 ID 碰撞：{candidate_id}")
        seen_ids.add(candidate_id)
        source_metadata = {
            "canonical_relative_path": source_relative,
            "source_sha256": source_hash,
            "declared_line_range": {
                "start_line": start_line,
                "end_line": end_line,
            },
            "exact_span": exact_span,
        }
        if snapshot_relative is not None:
            source_metadata["snapshot_relative_path"] = snapshot_relative
        result.append(
            {
                "schema_version": "legacy-user-response-candidate/v1",
                "candidate_id": candidate_id,
                "curation_key": key,
                "course": item.get("course"),
                "lesson": item.get("lesson"),
                "verbatim": verbatim,
                "candidate_evidence_type": item.get("candidate_evidence_type"),
                "is_feynman_candidate": item.get("is_feynman_candidate") is True,
                "speaker_verification": item.get(
                    "speaker_verification", "legacy_structural_candidate"
                ),
                "semantic_origin": item.get(
                    "semantic_origin", "unverified_user_candidate"
                ),
                "verification_status": "pending_source_revalidation",
                "eligible_for_content_asset": False,
                "first_person_allowed": False,
                "boundary_basis": item.get("boundary_basis"),
                "risk": item.get("risk"),
                "source": source_metadata,
                "promotion_gate": {
                    "required": True,
                    "accepted_evidence": [
                        "raw_chat_message",
                        "readwise_or_notion_original",
                        "explicit_user_verbatim_confirmation",
                    ],
                    "reason": item.get(
                        "source_revalidation_reason",
                        "旧课正文混有 Agent 课程内容；结构边界只能召回候选，不能证明说话者。",
                    ),
                },
            }
        )
    return result


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def render_view(rows: list[dict[str, Any]]) -> str:
    course_counts = Counter(row["course"] for row in rows)
    feynman = sum(row["is_feynman_candidate"] for row in rows)
    lines = [
        "# 待核验旧课原话候选",
        "",
        "> 本页中的文字只是从旧课程混排正文中逐字切出的说话者候选，不是已确认的 `[用户原话]`。",
        "> 未通过原始消息、Readwise／Notion 原评论或 DaCapo 逐字确认前，禁止进入内容资产和第一人称文稿。",
        "",
        "## 统计",
        "",
        f"- 候选：{len(rows)} 条",
        f"- 费曼／部分费曼候选：{feynman} 条",
        f"- 可直接进入内容资产：0 条",
        "",
        "## 按课题",
        "",
    ]
    for course, count in sorted(course_counts.items()):
        lines.append(f"- {course}：{count} 条")
    lines.extend(["", "## 候选明细", ""])
    for row in rows:
        source = row["source"]
        span = source["exact_span"]
        lines.extend(
            [
                f"### {row['curation_key']}｜{row['lesson']}",
                "",
                f"- 类型候选：`{row['candidate_evidence_type']}`",
                f"- 费曼候选：{'是' if row['is_feynman_candidate'] else '否'}",
                f"- 来源：`{source['canonical_relative_path']}:{span['start_line']}:{span['start_column']}`",
                f"- 状态：`{row['verification_status']}`",
                f"- 召回依据：`{row['speaker_verification']}`",
                f"- 风险：{row['risk']}",
                f"- 回查原因：{row['promotion_gate']['reason']}",
                "",
                "> " + row["verbatim"].replace("\n", "\n> "),
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="构建旧课程中的待核验用户逐字候选")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--view", type=Path, default=DEFAULT_VIEW)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    rows = build_candidates(manifest, args.project_root.expanduser().resolve())
    write_jsonl(args.output, rows)
    args.view.write_text(render_view(rows), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "ok",
                "candidates": len(rows),
                "feynman_candidates": sum(row["is_feynman_candidate"] for row in rows),
                "eligible_for_content_asset": 0,
                "output": str(args.output),
                "view": str(args.view),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
