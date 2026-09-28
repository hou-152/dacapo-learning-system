#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


LEARNING_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = LEARNING_ROOT.parent
CONTENT_ROOT = PROJECT_ROOT / "02-内容系统"
OUTPUT_JSONL = LEARNING_ROOT / "05-证据原子" / "quarantined-agent-claims.jsonl"
OUTPUT_MD = LEARNING_ROOT / "05-证据原子" / "归属污染隔离区.md"
CONTENT_AUDIT = CONTENT_ROOT / "03-处理状态" / "第一人称归属回滚审计.md"

SPECS = [
    {
        "id": "qa_20260714_001",
        "path": CONTENT_ROOT / "01-原始素材区" / "完整副本" / "历史文稿与审计" / "三条逐字稿-v1.md",
        "start": 7,
        "end": 7,
        "reason": "Agent 为文稿补出的发现过程；没有对应用户逐字证据。",
    },
    {
        "id": "qa_20260714_002",
        "path": CONTENT_ROOT / "01-原始素材区" / "完整副本" / "历史文稿与审计" / "三条逐字稿-v1.md",
        "start": 29,
        "end": 29,
        "reason": "用户说过当前理解是循环，但「我以前以为」的递进时间线由 Agent 改写。",
    },
    {
        "id": "qa_20260714_003",
        "path": CONTENT_ROOT / "01-原始素材区" / "完整副本" / "历史文稿与审计" / "三条逐字稿-v1.md",
        "start": 31,
        "end": 31,
        "reason": "把多个工作流拆开的发现过程没有用户逐字证据。",
    },
    {
        "id": "qa_20260714_004",
        "path": CONTENT_ROOT / "01-原始素材区" / "完整副本" / "历史文稿与审计" / "三条逐字稿-v1.md",
        "start": 61,
        "end": 61,
        "reason": "8 轮学习是材料事实，但「最后得到答案」的第一人称叙事由 Agent 生成。",
    },
    {
        "id": "qa_20260714_005",
        "path": CONTENT_ROOT / "01-原始素材区" / "完整副本" / "历史文稿与审计" / "三条逐字稿-v1.md",
        "start": 79,
        "end": 79,
        "reason": "公式可能受用户表达支持，但「我把它压成」宣称了未经证明的措辞作者身份。",
    },
    {
        "id": "qa_20260714_006",
        "path": LEARNING_ROOT / "02-课程真源" / "AI工作流控制权迁移" / "08.md",
        "start": 102,
        "end": 106,
        "reason": "Agent 把分散证据合成为一段新判断，并宣称「就是你自己的判断」；合成文本不是用户原话。",
    },
    {
        "id": "qa_20260714_007",
        "path": LEARNING_ROOT / "02-课程真源" / "AI工作流控制权迁移" / "复盘.md",
        "start": 52,
        "end": 60,
        "reason": "复盘中的聚合判断由 Agent 编写，只有其中单独列出的三条可回到各自用户原话。",
    },
    {
        "id": "qa_20260714_008",
        "path": LEARNING_ROOT / "02-课程真源" / "AI工作流控制权迁移" / "复盘.md",
        "start": 62,
        "end": 66,
        "reason": "验证方案是 Agent 设计的后续机制，不能写成用户已经建立的个人方案。",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_lines(path: Path, start: int, end: int) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if start < 1 or end > len(lines) or start > end:
        raise ValueError(f"行号越界：{path}:{start}-{end}")
    return "\n".join(lines[start - 1:end])


def main() -> int:
    rows = []
    for spec in SPECS:
        path = spec["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append(
            {
                "schema_version": "attribution-quarantine/v1",
                "quarantine_id": spec["id"],
                "text": extract_lines(path, spec["start"], spec["end"]),
                "identity": {
                    "surface_author": "agent",
                    "semantic_origin": "agent",
                    "origin_labels": ["Agent 连接"],
                },
                "confirmation": {
                    "status": "unconfirmed",
                    "scope": "none",
                },
                "voice_policy": {
                    "first_person_allowed": False,
                    "reason": spec["reason"],
                },
                "source": {
                    "path": path.relative_to(PROJECT_ROOT).as_posix(),
                    "line_start": spec["start"],
                    "line_end": spec["end"],
                    "source_sha256": sha256(path),
                },
                "downstream_policy": {
                    "eligible_for_content_asset": False,
                    "requires_user_wording_confirmation": True,
                },
            }
        )

    with OUTPUT_JSONL.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    lines = [
        "# 归属污染隔离区",
        "",
        "> 这里保存已经发现的 Agent 连接污染。它们不会被删除，但禁止作为用户原话或第一人称素材进入内容生产。",
        "",
        "## 规则",
        "",
        "- underlying judgment 可能有用户证据，不等于 Agent 写出的整句话就是用户原话。",
        "- 一旦需要采用这些句子，只能先回到对应用户逐字证据，或让用户确认具体措辞与第一人称。",
        "",
        "## 当前隔离项",
        "",
    ]
    for row in rows:
        source = row["source"]
        lines.extend(
            [
                f"### {row['quarantine_id']}",
                "",
                f"- 标签：[Agent 连接]",
                f"- 来源：{source['path']}:L{source['line_start']}-L{source['line_end']}",
                f"- 原因：{row['voice_policy']['reason']}",
                "",
                "原文：",
                "",
                row["text"],
                "",
            ]
        )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")

    audit_lines = [
        "# 第一人称归属回滚审计",
        "",
        "最后更新：2026-07-14",
        "",
        "## 结论",
        "",
        f"- 已隔离 {len(rows)} 处 Agent 连接或 Agent 合成。",
        "- 旧逐字稿保留在原始素材副本，不覆盖、不删除。",
        "- 这些句子全部禁止作为用户第一人称；应回到证据原子重新装配。",
        "",
        "## 机器真源",
        "",
        "- ../01-交互式学习/05-证据原子/quarantined-agent-claims.jsonl",
        "",
        "## 阅读视图",
        "",
        "- ../01-交互式学习/05-证据原子/归属污染隔离区.md",
        "",
    ]
    CONTENT_AUDIT.write_text("\n".join(audit_lines), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "quarantined_items": len(rows),
                "jsonl": OUTPUT_JSONL.relative_to(PROJECT_ROOT).as_posix(),
                "audit": CONTENT_AUDIT.relative_to(PROJECT_ROOT).as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
