#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from extract_marked_user_responses import _validate_response_attribution


SCRIPT_PATH = Path(__file__).resolve()
LEARNING_ROOT = SCRIPT_PATH.parents[1]
import sys
sys.path.insert(0, str(LEARNING_ROOT / "08-脚本与工具/learning-workbench"))
import provenance as workbench_provenance
PROJECT_ROOT = LEARNING_ROOT.parent
INPUT_PATH = LEARNING_ROOT / "04-用户原话与费曼" / "user-utterances.jsonl"
SNAPSHOT_ROOT = (
    LEARNING_ROOT
    / "01-原始素材区"
    / "完整副本"
    / "dbskill-learning-structured-copy"
    / "00-原始素材快照"
)
INCREMENTAL_SNAPSHOT_ROOT = (
    LEARNING_ROOT / "01-原始素材区" / "增量摄取" / "课程修订"
)
CANONICAL_ROOT = LEARNING_ROOT / "02-课程真源"
OUTPUT_ROOT = LEARNING_ROOT / "05-证据原子"
OUTPUT_PATH = OUTPUT_ROOT / "evidence-atoms.jsonl"
FEYNMAN_PATH = OUTPUT_ROOT / "feynman-evidence-atoms.jsonl"
INDEX_PATH = OUTPUT_ROOT / "证据原子索引.md"
SPLIT_MANIFEST_PATH = OUTPUT_ROOT / "curated-evidence-splits.json"
FEYNMAN_SPAN_MANIFEST_NAME = "curated-feynman-spans.json"

FEYNMAN_KINDS = {"feynman_answer", "checkpoint_answer"}
MATERIAL_RISK_PATTERNS = (
    re.compile(r"https?://", re.I),
    re.compile(r"\b\d+(?:\.\d+)?%"),
    re.compile(r"(?:文章|作者|研究|报告|数据显示|资料|新闻|论文).{0,16}(?:说|认为|指出|提到|显示|发现)"),
    re.compile(r"(?:阿德勒|贝叶斯|第一性原理).{0,20}(?:是|认为|主张|来自)"),
)

CURATED_SPLITS: list[dict] = []
ATTRIBUTION_FIELDS = {
    "status",
    "ingress_path",
    "ingress_request_id",
    "ingress_sha256",
    "attribution_id",
    "envelope_path",
    "envelope_sha256",
    "usage_binding",
    "source_channel",
    "source_revision_sha256",
    "source_locator",
    "capture_actor",
    "surface_author",
    "semantic_origin",
    "feynman_learner_signal_allowed",
    "strict_mastery_evidence_allowed",
    "claim_eligible",
    "first_person_allowed",
    "learner_signal_quality",
}


def validated_record_attribution(record: dict) -> dict | None:
    """Validate the attribution-aware v3 ledger record without upgrading v2 rows.

    Historical v2 rows remain readable for migration review.  New v3 rows must
    carry the fixed runtime binding and may never derive authorship from speaker.
    """

    if record.get("schema_version") != "user-utterance/v3":
        return None
    attribution = record.get("attribution")
    if not isinstance(attribution, dict) or set(attribution) != ATTRIBUTION_FIELDS:
        raise ValueError(f"v3 学习者信号归属块非法：{record.get('record_id')}")
    revalidated, blocked_reason = _validate_response_attribution(
        {
            "response_id": record.get("response_id"),
            "course_id": record.get("course_id"),
            "lesson": record.get("lesson"),
            "kind": record.get("evidence_type"),
            "lesson_sha256": record.get("lesson_sha256"),
            "response_sha256": record.get("response_sha256"),
            "attribution": attribution,
        },
        str(record.get("verbatim") or ""),
    )
    if revalidated is None or revalidated != attribution:
        raise ValueError(
            f"v3 学习者信号无法复验 envelope／ingress：{record.get('record_id')}：{blocked_reason}"
        )
    if (
        attribution.get("status") != "validated"
        or attribution.get("feynman_learner_signal_allowed") is not True
        or type(attribution.get("strict_mastery_evidence_allowed")) is not bool
        or type(attribution.get("claim_eligible")) is not bool
    ):
        raise ValueError(f"v3 学习者信号未通过归属门：{record.get('record_id')}")
    identity = record.get("identity")
    if (
        not isinstance(identity, dict)
        or identity.get("surface_author") != attribution.get("surface_author")
        or identity.get("semantic_origin") != attribution.get("semantic_origin")
    ):
        raise ValueError(f"v3 学习者信号 identity 与 attribution 不一致：{record.get('record_id')}")
    eligibility = record.get("eligibility")
    if (
        not isinstance(eligibility, dict)
        or eligibility.get("as_feynman_learner_signal") is not True
        or eligibility.get("as_user_claim") is not attribution.get("claim_eligible")
        or eligibility.get("strict_mastery_evidence")
        is not attribution.get("strict_mastery_evidence_allowed")
    ):
        raise ValueError(f"v3 学习者信号权限与 attribution 不一致：{record.get('record_id')}")
    if attribution.get("claim_eligible") is True and not (
        attribution.get("surface_author") == "user"
        and attribution.get("semantic_origin") == "user"
        and attribution.get("first_person_allowed") == "confirmed_wording_only"
    ):
        raise ValueError(f"v3 学习者信号错误开放 user claim：{record.get('record_id')}")
    if attribution.get("strict_mastery_evidence_allowed") is True and not (
        attribution.get("claim_eligible") is True
        and attribution.get("learner_signal_quality") == "independent"
    ):
        raise ValueError(f"v3 学习者信号错误开放 strict mastery：{record.get('record_id')}")
    return attribution


def attribution_origin_labels(attribution: dict) -> list[str]:
    labels = ["学习者提交"]
    labels.append(
        {
            "user": "用户执笔（已确认）",
            "agent": "Agent 执笔",
            "source_author": "来源作者执笔",
            "joint": "共同执笔",
            "unknown": "字面作者待核验",
        }.get(str(attribution.get("surface_author")), "字面作者待核验")
    )
    labels.append(
        {
            "user": "用户语义（已确认）",
            "material": "材料语义",
            "agent": "Agent 语义",
            "joint": "共同语义",
            "mixed": "混合语义",
            "management": "管理指针",
            "unknown": "语义来源待核验",
        }.get(str(attribution.get("semantic_origin")), "语义来源待核验")
    )
    return labels


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def load_records(path: Path = INPUT_PATH) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("speaker") != "user":
                raise ValueError(f"第 {line_number} 行不是用户记录：{record.get('record_id')}")
            if record.get("verbatim_status") != "source_exact":
                raise ValueError(f"第 {line_number} 行不是逐字记录：{record.get('record_id')}")
            validated_record_attribution(record)
            records.append(record)
    return records


def build_snapshot_map(
    roots: list[Path] | None = None,
    aliases: dict[str, list[Path]] | None = None,
) -> dict[str, list[Path]]:
    result: dict[str, list[Path]] = {}
    for root in roots or [SNAPSHOT_ROOT, INCREMENTAL_SNAPSHOT_ROOT]:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            result.setdefault(sha256(path), []).append(path)
    for source_hash, paths in (aliases or {}).items():
        result.setdefault(source_hash, []).extend(paths)
    return result


def choose_snapshot(paths: list[Path]) -> Path | None:
    if not paths:
        return None

    def rank(path: Path) -> tuple[int, str]:
        value = path.as_posix()
        if "/课程真源/" in value:
            return (0, value)
        if "/Logseq课程页面/" in value:
            return (1, value)
        if "/Logseq派生视图/" in value:
            return (2, value)
        return (3, value)

    return sorted(paths, key=rank)[0]


def has_material_risk(text: str) -> bool:
    return any(pattern.search(text) for pattern in MATERIAL_RISK_PATTERNS)


def resolve_source(
    record: dict,
    snapshot_map: dict[str, list[Path]],
    *,
    project_root: Path = PROJECT_ROOT,
    canonical_root: Path = CANONICAL_ROOT,
) -> dict:
    expected_sha = record["source_sha256"]
    source_relative = Path(record["source_relative_path"])
    if source_relative.is_absolute() or ".." in source_relative.parts:
        raise ValueError(
            f"用户原话来源路径不是安全相对路径：{record.get('record_id')}"
        )
    project_candidate = project_root / source_relative
    course_candidate = canonical_root / source_relative
    canonical_path = (
        project_candidate
        if project_candidate.is_file()
        and sha256(project_candidate) == expected_sha
        else course_candidate
    )
    canonical_match = canonical_path.is_file() and sha256(canonical_path) == expected_sha
    snapshot_path = choose_snapshot(snapshot_map.get(expected_sha, []))

    if canonical_match:
        resolution = "canonical_sha256_match"
    elif snapshot_path:
        resolution = "immutable_snapshot_sha256_match"
    else:
        resolution = "unresolved"

    return {
        "canonical_relative_path": (
            canonical_path.relative_to(project_root).as_posix() if canonical_match else None
        ),
        "canonical_sha256_match": canonical_match,
        "legacy_source_path": record.get("source_path"),
        "legacy_snapshot_path": record.get("snapshot_path"),
        "snapshot_relative_path": (
            snapshot_path.relative_to(project_root).as_posix() if snapshot_path else None
        ),
        "source_relative_path": record["source_relative_path"],
        "source_sha256": expected_sha,
        "resolution": resolution,
        "locator": record.get("locator", {}),
    }


def to_atom(
    record: dict,
    snapshot_map: dict[str, list[Path]],
    parent_policy: dict | None = None,
    *,
    project_root: Path = PROJECT_ROOT,
    canonical_root: Path = CANONICAL_ROOT,
) -> dict:
    if record.get("schema_version") == workbench_provenance.SCHEMA:
        return workbench_provenance.to_atom(record, LEARNING_ROOT)
    text = record["verbatim"]
    attribution = validated_record_attribution(record)
    attribution_pending = attribution is None
    material_risk = has_material_risk(text)
    source = resolve_source(
        record,
        snapshot_map,
        project_root=project_root,
        canonical_root=canonical_root,
    )
    source_verified = source["resolution"] != "unresolved"
    record_id = record["record_id"]
    eligible_as_user_claim = bool(
        attribution is not None
        and attribution.get("claim_eligible")
        and not material_risk
    )

    origin_labels = (
        ["归属待核验", "逐字学习记录"]
        if attribution_pending
        else ["用户原话"]
    )
    if material_risk and not attribution_pending:
        origin_labels.append("材料事实候选")

    atom = {
        "schema_version": "evidence-atom/v1",
        "evidence_id": f"ev_{record_id.removeprefix('utt_')}_r1",
        "text": text,
        "version": 1,
        "status": (
            "legacy_pending_attribution" if attribution_pending else "current"
        ),
        "record": {
            "parent_record_id": record_id,
            "atom_index": 1,
            "record_level": True,
            "requires_semantic_split": material_risk,
        },
        "identity": {
            "surface_author": "unknown" if attribution_pending else "user",
            "semantic_origin": (
                "unknown"
                if attribution_pending
                else "unresolved_mixed" if material_risk else "user"
            ),
            "origin_labels": origin_labels,
            "speaker_verification": record.get("speaker_verification"),
        },
        "form": {
            "text_form": (
                "verbatim_unattributed_learning_record"
                if attribution_pending
                else "verbatim_user_record"
            ),
            "exactness": "exact",
            "speech_act": record.get("content_roles", []),
        },
        "confirmation": {
            "status": (
                "pending_attribution_review"
                if attribution_pending
                else "not_required_user_original"
            ),
            "scope": "none" if attribution_pending else "wording",
            "confirmed_by": None if attribution_pending else "user",
            "confirmation_evidence_id": None if attribution_pending else record_id,
        },
        "verification": {
            "required": material_risk,
            "status": "source_matched" if source_verified else "unresolved",
            "claim_status": "pending_atom_split" if material_risk else "not_applicable",
            "material_source_ids": [],
        },
        "voice_policy": {
            "first_person": (
                "forbidden"
                if attribution_pending
                else "forbidden_until_atom_split"
                if material_risk
                else "exact_verbatim_only"
            ),
            "reason": (
                "旧记录没有 hash-bound attribution；仅保留原始字节与 lineage，迁移确认前禁止第一人称使用"
                if attribution_pending
                else "整段可能同时含用户表达与材料转述，拆分前禁止改写成用户第一人称"
                if material_risk
                else "用户逐字原话，只允许原样引用或无语义变化的切片"
            ),
        },
        "eligibility": {
            "as_verbatim_quote": not attribution_pending,
            "as_user_claim": eligible_as_user_claim,
            "as_material_fact": False,
            "reason": (
                "旧记录只作逐字回溯，不能由 speaker=user 或历史目录名推断用户身份"
                if attribution_pending
                else "混合记录可作为用户逐字发言回溯，但拆分前不能作为用户原创判断"
                if material_risk
                else "用户逐字原话；用户判断资格仍受精确引用和下游语境约束"
            ),
        },
        "source": source,
        "lineage": {
            "parent_evidence_ids": [],
            "transformation": "record_exact_copy",
        },
        "learning": {
            "course": record.get("course"),
            "course_id": record.get("course_id"),
            "lesson": record.get("lesson"),
            "response_kind": record.get("evidence_type"),
            "is_feynman_evidence": bool(
                not attribution_pending
                and record.get("evidence_type") in FEYNMAN_KINDS
            ),
            "settlement_status": (
                "legacy_pending_attribution"
                if attribution_pending
                else "evidence_recorded"
            ),
        },
        "downstream_policy": {
            "eligible_for_content_asset": (
                eligible_as_user_claim if not attribution_pending else False
            ),
            "use_mode": (
                "attribution_review_only"
                if attribution_pending
                else "manual_semantic_split_required"
                if material_risk
                else "exact_quote_or_curated_atom"
            ),
            "agent_summary_may_replace_text": False,
        },
    }
    if attribution_pending:
        atom["attribution_review"] = {
            "status": "legacy_pending_attribution",
            "source_schema_version": record.get("schema_version") or "unversioned",
            "automatic_upgrade_allowed": False,
            "preserved_verbatim_sha256": hashlib.sha256(
                text.encode("utf-8")
            ).hexdigest(),
            "reason": "缺少固定形状且 hash-bound 的 attribution envelope",
        }
    if attribution is not None:
        first_person = {
            "forbidden": "forbidden",
            "exact_quote_only": "exact_learner_submission_only",
            "confirmed_wording_only": "exact_verbatim_only",
        }[str(attribution["first_person_allowed"])]
        atom["status"] = (
            "current"
            if attribution["semantic_origin"] in {"user", "material", "agent"}
            else "current_pending_semantic_review"
        )
        atom["identity"] = {
            "surface_author": attribution["surface_author"],
            "semantic_origin": attribution["semantic_origin"],
            "origin_labels": attribution_origin_labels(attribution),
            "speaker_verification": record.get("speaker_verification"),
            "attribution_id": attribution["attribution_id"],
            "attribution_envelope_sha256": attribution["envelope_sha256"],
        }
        atom["form"] = {
            "text_form": "verbatim_attributed_learner_signal",
            "exactness": "exact",
            "speech_act": record.get("content_roles", []),
        }
        atom["confirmation"] = {
            "status": (
                "confirmed_hash_bound_user_claim"
                if attribution["claim_eligible"]
                else "validated_learner_signal_only"
            ),
            "scope": (
                "authorship_wording_semantic"
                if attribution["claim_eligible"]
                else "learner_signal"
            ),
            "confirmed_by": "attribution_gateway",
            "confirmation_evidence_id": attribution["attribution_id"],
        }
        atom["voice_policy"] = {
            "first_person": first_person,
            "reason": (
                "只允许按 attribution 中已确认的措辞与第一人称范围使用"
                if attribution["claim_eligible"]
                else "可用于教学反馈，但不得由学习者提交行为推断原创作者或用户观点"
            ),
        }
        atom["eligibility"] = {
            "as_verbatim_quote": True,
            "as_user_claim": eligible_as_user_claim,
            "as_material_fact": False,
            "reason": (
                "归属证据已打开用户 claim；内容资产仍需独立入选"
                if eligible_as_user_claim
                else "归属只允许 learner signal，不允许用户观点升级"
            ),
        }
        atom["learning"].update(
            {
                "is_feynman_evidence": bool(
                    attribution["feynman_learner_signal_allowed"]
                    and record.get("evidence_type") in FEYNMAN_KINDS
                ),
                "is_attribution_bound_learner_signal": True,
                "strict_mastery_evidence_allowed": attribution[
                    "strict_mastery_evidence_allowed"
                ],
                "learner_signal_quality": attribution["learner_signal_quality"],
            }
        )
        atom["downstream_policy"] = {
            "eligible_for_content_asset": False,
            "use_mode": (
                "confirmed_user_claim_requires_content_selection"
                if eligible_as_user_claim
                else "learning_signal_only"
            ),
            "agent_summary_may_replace_text": False,
        }
    if parent_policy:
        expected_parent_sha = parent_policy.get("parent_verbatim_sha256")
        if expected_parent_sha is not None and expected_parent_sha != hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest():
            raise ValueError(f"人工切片父记录 SHA 不一致：{record_id}")
        atom["record"]["requires_semantic_split"] = False
        atom["record"]["split_status"] = (
            "complete"
            if parent_policy.get("coverage") == "complete_non_whitespace"
            else "selected_exact_spans"
        )
        atom["record"]["coverage"] = parent_policy.get("coverage")
        if parent_policy.get("feynman_parent_policy"):
            atom["record"]["feynman_parent_policy"] = parent_policy[
                "feynman_parent_policy"
            ]
        if parent_policy.get("unselected_text_policy"):
            atom["record"]["unselected_text_policy"] = parent_policy[
                "unselected_text_policy"
            ]
        requested_parent_origin = parent_policy["semantic_origin"]
        atom["identity"]["semantic_origin"] = (
            "unknown"
            if attribution_pending and requested_parent_origin == "user"
            else requested_parent_origin
        )
        atom["identity"]["origin_labels"] = parent_policy["origin_labels"]
        if attribution_pending:
            atom["identity"]["surface_author"] = "unknown"
            atom["identity"]["origin_labels"] = [
                "归属待核验",
                "人工切片父记录",
            ]
            atom["attribution_review"]["requested_parent_semantic_origin"] = (
                requested_parent_origin
            )
        atom["verification"] = {
            "required": False,
            "status": "resolved_by_curated_atoms",
            "claim_status": "child_atoms_only",
            "material_source_ids": [],
        }
        atom["voice_policy"] = {
            "first_person": "forbidden",
            "reason": parent_policy["reason"],
        }
        atom["eligibility"] = {
            "as_verbatim_quote": not attribution_pending,
            "as_user_claim": False,
            "as_material_fact": False,
            "reason": parent_policy["reason"],
        }
        atom["downstream_policy"] = {
            "eligible_for_content_asset": False,
            "use_mode": "use_curated_children_only",
            "agent_summary_may_replace_text": False,
        }
    return atom


def load_split_manifest(
    path: Path = SPLIT_MANIFEST_PATH,
) -> tuple[dict[str, dict], list[dict]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema_version") != "curated-evidence-splits/v1":
        raise ValueError("人工切片清单 schema 非法")
    parents = value.get("parents")
    atoms = value.get("atoms")
    if not isinstance(parents, dict) or not isinstance(atoms, list):
        raise ValueError("人工切片清单缺少 parents 或 atoms")
    parents = dict(parents)
    feynman_path = path.with_name(FEYNMAN_SPAN_MANIFEST_NAME)
    if feynman_path.is_file():
        feynman_value = json.loads(feynman_path.read_text(encoding="utf-8"))
        if feynman_value.get("schema_version") != "curated-feynman-spans/v1":
            raise ValueError("费曼精确切片清单 schema 非法")
        span_parents = feynman_value.get("parents")
        if not isinstance(span_parents, dict):
            raise ValueError("费曼精确切片清单缺少 parents")
        provenance = feynman_value.get("classification_provenance")
        if not isinstance(provenance, dict):
            raise ValueError("费曼精确切片清单缺少 classification_provenance")
        spans: list[dict] = []
        for parent_record_id, parent_value in span_parents.items():
            if not isinstance(parent_value, dict):
                raise ValueError(f"费曼精确切片父项非法：{parent_record_id}")
            parent_sha = parent_value.get("parent_verbatim_sha256")
            parent_spans = parent_value.get("spans")
            if not isinstance(parent_sha, str) or len(parent_sha) != 64:
                raise ValueError(f"费曼精确切片父 SHA 非法：{parent_record_id}")
            if not isinstance(parent_spans, list):
                raise ValueError(f"费曼精确切片父项缺少 spans：{parent_record_id}")
            policy = {
                "coverage": parent_value.get("coverage"),
                "semantic_origin": parent_value.get("semantic_origin"),
                "origin_labels": parent_value.get("origin_labels"),
                "reason": parent_value.get("reason"),
                "parent_verbatim_sha256": parent_sha,
                "feynman_parent_policy": parent_value.get("feynman_parent_policy"),
                "unselected_text_policy": parent_value.get("unselected_text_policy"),
            }
            if (
                policy["coverage"] != "selected_exact_spans"
                or policy["feynman_parent_policy"] != "children_only"
                or policy["unselected_text_policy"] != "preserve_parent_only"
                or not isinstance(policy["semantic_origin"], str)
                or not isinstance(policy["origin_labels"], list)
                or not isinstance(policy["reason"], str)
            ):
                raise ValueError(f"费曼精确切片父策略非法：{parent_record_id}")
            if parent_record_id in parents and parents[parent_record_id] != policy:
                raise ValueError(f"费曼精确切片父策略冲突：{parent_record_id}")
            parents[parent_record_id] = policy
            basis = parent_value.get("feynman_basis")
            if not isinstance(basis, dict):
                raise ValueError(f"费曼精确切片缺少学习依据：{parent_record_id}")
            for item in parent_spans:
                if not isinstance(item, dict):
                    raise ValueError(f"费曼精确切片项非法：{parent_record_id}")
                value = dict(item)
                utf8_span = value.pop("utf8_span", None)
                if (
                    not isinstance(utf8_span, list)
                    or len(utf8_span) != 2
                    or not all(type(offset) is int for offset in utf8_span)
                ):
                    raise ValueError(f"费曼精确切片范围非法：{parent_record_id}")
                value["parent_record_id"] = str(parent_record_id)
                value["parent_utf8_span"] = {
                    "utf8_start_byte": utf8_span[0],
                    "utf8_end_byte_exclusive": utf8_span[1],
                    "parent_verbatim_sha256": parent_sha,
                }
                section = value.pop("section", None)
                if not isinstance(section, str) or not section:
                    raise ValueError(f"费曼精确切片缺少 section：{parent_record_id}")
                value["feynman_basis"] = {**basis, "section": section}
                value["classification_provenance"] = dict(provenance)
                spans.append(value)
        atoms = [*atoms, *spans]
    return parents, atoms


def validate_complete_coverage(
    parent: dict,
    splits: list[dict],
    policy: dict,
) -> None:
    if policy.get("coverage") != "complete_non_whitespace":
        return
    cursor = 0
    for split in sorted(
        splits,
        key=lambda item: int(str(item["suffix"]).removeprefix("a")),
    ):
        text = split["text"]
        start = parent["text"].find(text, cursor)
        if start < 0:
            raise ValueError(
                f"完整切片顺序不匹配：{split['parent_record_id']}／{split['suffix']}"
            )
        if parent["text"][cursor:start].strip():
            raise ValueError(
                f"完整切片之间存在未覆盖文本：{split['parent_record_id']}／{split['suffix']}"
            )
        cursor = start + len(text)
    if parent["text"][cursor:].strip():
        raise ValueError(f"完整切片末尾存在未覆盖文本：{splits[0]['parent_record_id']}")


def exact_parent_utf8_span(
    parent_text: str,
    selected_text: str,
    declared_span: dict | None = None,
) -> dict[str, int | str]:
    raw = parent_text.encode("utf-8")
    parent_sha = hashlib.sha256(raw).hexdigest()
    if declared_span is not None:
        start_byte = declared_span.get("utf8_start_byte")
        end_byte = declared_span.get("utf8_end_byte_exclusive")
        if (
            type(start_byte) is not int
            or type(end_byte) is not int
            or start_byte < 0
            or end_byte < start_byte
            or end_byte > len(raw)
            or declared_span.get("parent_verbatim_sha256") != parent_sha
        ):
            raise ValueError("人工切片声明的父记录 UTF-8 span 非法")
    else:
        start = parent_text.find(selected_text)
        if start < 0:
            raise ValueError("人工切片不在父记录中")
        if parent_text.find(selected_text, start + 1) >= 0:
            raise ValueError("人工切片在父记录中不唯一，必须显式声明 UTF-8 span")
        end = start + len(selected_text)
        start_byte = len(parent_text[:start].encode("utf-8"))
        end_byte = len(parent_text[:end].encode("utf-8"))
    try:
        rebuilt = raw[start_byte:end_byte].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("人工切片 UTF-8 span 切断多字节字符") from exc
    if rebuilt != selected_text:
        raise ValueError("人工切片 UTF-8 span 无法逐字重建")
    return {
        "utf8_start_byte": start_byte,
        "utf8_end_byte_exclusive": end_byte,
        "parent_verbatim_sha256": parent_sha,
        "span_text_sha256": hashlib.sha256(selected_text.encode("utf-8")).hexdigest(),
    }


def split_text(parent_text: str, split: dict) -> str:
    declared = split.get("text")
    if isinstance(declared, str):
        return declared
    span = split.get("parent_utf8_span")
    if not isinstance(span, dict):
        raise ValueError("人工切片同时缺少 text 与父记录 UTF-8 span")
    raw = parent_text.encode("utf-8")
    start = span.get("utf8_start_byte")
    end = span.get("utf8_end_byte_exclusive")
    if (
        type(start) is not int
        or type(end) is not int
        or start < 0
        or end <= start
        or end > len(raw)
        or span.get("parent_verbatim_sha256")
        != hashlib.sha256(raw).hexdigest()
    ):
        raise ValueError("人工切片声明的父记录 UTF-8 span 非法")
    try:
        return raw[start:end].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("人工切片 UTF-8 span 切断多字节字符") from exc


def select_feynman_atoms(
    record_atoms: list[dict], curated_atoms: list[dict]
) -> list[dict]:
    return select_feynman_from_atoms([*record_atoms, *curated_atoms])


def select_feynman_from_atoms(atoms: list[dict]) -> list[dict]:
    """Project the Feynman ledger from current Evidence without guessing roles."""
    return [
        atom
        for atom in atoms
        if atom.get("status") in {"current", "current_pending_semantic_review"}
        and (atom.get("identity") or {}).get("semantic_origin") == "user"
        and (atom.get("learning") or {}).get("is_feynman_evidence") is True
        and not (
            (atom.get("record") or {}).get("record_level") is True
            and (atom.get("record") or {}).get("feynman_parent_policy")
            == "children_only"
        )
    ]


def build_curated_atoms(
    record_atoms: list[dict],
    manifest_splits: list[dict],
    parent_policies: dict[str, dict],
    *,
    project_root: Path = PROJECT_ROOT,
) -> list[dict]:
    by_record = {
        atom["record"]["parent_record_id"]: atom
        for atom in record_atoms
    }
    curated: list[dict] = []
    all_splits = CURATED_SPLITS + manifest_splits
    by_parent: dict[str, list[dict]] = {}
    split_ids: set[tuple[str, str]] = set()
    for split in all_splits:
        if split.get("is_feynman_evidence") is not None and not isinstance(
            split.get("parent_utf8_span"), dict
        ):
            raise ValueError(
                f"费曼切片必须显式声明父记录 UTF-8 span：{split['parent_record_id']}／{split['suffix']}"
            )
        split_id = (str(split["parent_record_id"]), str(split["suffix"]))
        if split_id in split_ids:
            raise ValueError(
                f"人工切片 identity 重复：{split_id[0]}／{split_id[1]}"
            )
        split_ids.add(split_id)
        by_parent.setdefault(split["parent_record_id"], []).append(split)
    for parent_record_id, splits in by_parent.items():
        declared_ranges = []
        for split in splits:
            span = split.get("parent_utf8_span")
            if isinstance(span, dict):
                start = span.get("utf8_start_byte")
                end = span.get("utf8_end_byte_exclusive")
                if type(start) is not int or type(end) is not int:
                    raise ValueError(
                        f"人工切片 UTF-8 span 类型非法：{parent_record_id}／{split['suffix']}"
                    )
                declared_ranges.append(
                    (
                        start,
                        end,
                        str(split["suffix"]),
                    )
                )
        previous_end = -1
        for start, end, suffix in sorted(declared_ranges):
            if start < previous_end:
                raise ValueError(
                    f"人工切片 UTF-8 span 重叠：{parent_record_id}／{suffix}"
                )
            previous_end = end
    for parent_record_id, policy in parent_policies.items():
        if parent_record_id not in by_record:
            raise ValueError(f"人工切片父记录不存在：{parent_record_id}")
        validate_complete_coverage(
            by_record[parent_record_id],
            by_parent.get(parent_record_id, []),
            policy,
        )

    for split in all_splits:
        parent = by_record[split["parent_record_id"]]
        text = split_text(parent["text"], split)
        if text not in parent["text"]:
            raise ValueError(
                f"人工切片不在父记录中：{split['parent_record_id']}／{split['suffix']}"
            )
        atom = json.loads(json.dumps(parent, ensure_ascii=False))
        atom["evidence_id"] = (
            f"ev_{split['parent_record_id'].removeprefix('utt_')}_{split['suffix']}"
        )
        atom["text"] = text
        atom["record"] = {
            "parent_record_id": split["parent_record_id"],
            "atom_index": int(split["suffix"].removeprefix("a")),
            "record_level": False,
            "requires_semantic_split": False,
            "parent_utf8_span": exact_parent_utf8_span(
                parent["text"], text, split.get("parent_utf8_span")
            ),
        }
        attributed_parent = "attribution_id" in (parent.get("identity") or {})
        attribution_pending_parent = not attributed_parent
        parent_semantic_origin = (parent.get("identity") or {}).get(
            "semantic_origin", "unknown"
        )
        parent_claim_allowed = (parent.get("eligibility") or {}).get(
            "as_user_claim"
        ) is True
        parent_content_allowed = (parent.get("downstream_policy") or {}).get(
            "eligible_for_content_asset"
        ) is True
        requested_semantic_origin = split.get(
            "semantic_origin", parent_semantic_origin
        )
        semantic_origin = (
            "unknown"
            if attribution_pending_parent and requested_semantic_origin == "user"
            else requested_semantic_origin
        )
        origin_labels = split.get(
            "origin_labels",
            (parent.get("identity") or {}).get("origin_labels", []),
        )
        if attribution_pending_parent:
            origin_labels = ["归属待核验", "人工逐字切片"]
            if semantic_origin == "material":
                origin_labels.append("材料语义候选")
        text_form = split.get(
            "text_form",
            (parent.get("form") or {}).get(
                "text_form", "verbatim_unattributed_learning_record"
            ),
        )
        speech_act = split.get("speech_act")
        reason = split.get("reason")
        if not isinstance(speech_act, list) or not speech_act:
            raise ValueError(
                f"人工切片缺少 speech_act：{split['parent_record_id']}／{split['suffix']}"
            )
        if not isinstance(reason, str) or not reason:
            raise ValueError(
                f"人工切片缺少 reason：{split['parent_record_id']}／{split['suffix']}"
            )
        if attributed_parent:
            requested_claim = split.get("as_user_claim", parent_claim_allowed)
            requested_first_person = split.get(
                "first_person",
                (parent.get("voice_policy") or {}).get(
                    "first_person", "forbidden"
                ),
            )
            requested_content = split.get(
                "eligible_for_content_asset", parent_content_allowed
            )
            if semantic_origin == "user" and parent_semantic_origin != "user":
                raise ValueError(
                    f"归属绑定父记录的人工切片不能把语义升级为 user："
                    f"{split['parent_record_id']}／{split['suffix']}"
                )
            if requested_claim is True and not parent_claim_allowed:
                raise ValueError(
                    f"人工切片不能超越父记录 user claim 权限："
                    f"{split['parent_record_id']}／{split['suffix']}"
                )
            if requested_first_person != "forbidden" and (
                parent.get("voice_policy") or {}
            ).get("first_person") == "forbidden":
                raise ValueError(
                    f"人工切片不能超越父记录第一人称权限："
                    f"{split['parent_record_id']}／{split['suffix']}"
                )
            if requested_content is True and not parent_content_allowed:
                raise ValueError(
                    f"人工切片不能超越父记录内容资产权限："
                    f"{split['parent_record_id']}／{split['suffix']}"
                )
            if requested_claim is True and semantic_origin != "user":
                raise ValueError(
                    f"非 user 语义的人工切片不能开放 user claim："
                    f"{split['parent_record_id']}／{split['suffix']}"
                )
            if requested_first_person != "forbidden" and semantic_origin != "user":
                raise ValueError(
                    f"非 user 语义的人工切片不能开放第一人称："
                    f"{split['parent_record_id']}／{split['suffix']}"
                )
        atom["identity"]["semantic_origin"] = semantic_origin
        atom["identity"]["origin_labels"] = origin_labels
        atom["form"]["text_form"] = text_form
        atom["form"]["speech_act"] = speech_act
        verification_status = split.get("verification_status", "not_applicable")
        confirmation_status = {
            "user": "not_required_user_original",
            "material": "pending_material_verification",
            "management": "not_applicable_management_pointer",
        }.get(semantic_origin, "pending_review")
        atom["confirmation"] = {
            "status": confirmation_status,
            "scope": "wording",
            "confirmed_by": "user",
            "confirmation_evidence_id": split["parent_record_id"],
        }
        if attributed_parent:
            atom["confirmation"] = json.loads(
                json.dumps(parent["confirmation"], ensure_ascii=False)
            )
        else:
            atom["confirmation"] = {
                "status": "pending_attribution_review",
                "scope": "none",
                "confirmed_by": None,
                "confirmation_evidence_id": None,
            }
        atom["verification"] = {
            "required": split.get(
                "verification_required",
                verification_status != "not_applicable",
            ),
            "status": verification_status,
            "claim_status": split.get("claim_status", verification_status),
            "material_source_ids": split.get("material_source_ids", []),
        }
        atom["voice_policy"] = {
            "first_person": "forbidden" if attribution_pending_parent else split.get(
                "first_person",
                (parent.get("voice_policy") or {}).get(
                    "first_person", "forbidden"
                )
                if attributed_parent
                else "forbidden",
            ),
            "reason": reason,
        }
        atom["eligibility"] = {
            "as_verbatim_quote": False if attribution_pending_parent else split.get(
                "as_verbatim_quote", True
            ),
            "as_user_claim": False if attribution_pending_parent else split.get(
                "as_user_claim",
                parent_claim_allowed
                if attributed_parent
                else False,
            ),
            "as_material_fact": False if attribution_pending_parent else split.get(
                "as_material_fact", False
            ),
            "reason": reason,
        }
        atom["lineage"] = {
            "parent_evidence_ids": [parent["evidence_id"]],
            "transformation": "split_exact_span",
        }
        atom["downstream_policy"] = {
            "eligible_for_content_asset": False if attribution_pending_parent else split.get(
                "eligible_for_content_asset",
                parent_content_allowed
                if attributed_parent
                else False,
            ),
            "use_mode": split.get(
                "use_mode",
                "attribution_review_only"
                if attribution_pending_parent
                else "exact_quote_or_curated_atom"
                if semantic_origin == "user"
                else "material_verification_required",
            ),
            "agent_summary_may_replace_text": False,
        }
        parent_is_feynman = bool(parent["learning"]["is_feynman_evidence"])
        default_is_feynman = bool(
            parent_is_feynman
            and atom["identity"]["semantic_origin"] == "user"
            and atom["eligibility"]["as_user_claim"] is True
        )
        requested_is_feynman = split.get(
            "is_feynman_evidence", default_is_feynman
        )
        is_feynman = (
            False if attribution_pending_parent else requested_is_feynman
        )
        if not isinstance(is_feynman, bool):
            raise ValueError(
                f"人工切片费曼标记非法：{split['parent_record_id']}／{split['suffix']}"
            )
        atom["learning"]["is_feynman_evidence"] = is_feynman
        if is_feynman:
            if atom["identity"]["semantic_origin"] != "user":
                raise ValueError(
                    f"非用户语义不能进入费曼证据：{split['parent_record_id']}／{split['suffix']}"
                )
            feynman_kind = split.get("feynman_kind")
            if feynman_kind is None and parent["learning"]["response_kind"] in FEYNMAN_KINDS:
                feynman_kind = parent["learning"]["response_kind"]
            if feynman_kind not in FEYNMAN_KINDS:
                raise ValueError(
                    f"费曼切片缺少合法 feynman_kind：{split['parent_record_id']}／{split['suffix']}"
                )
            atom["learning"]["feynman_kind"] = feynman_kind
        if attribution_pending_parent:
            atom["status"] = "legacy_pending_attribution"
            atom["identity"]["surface_author"] = "unknown"
            atom["learning"]["settlement_status"] = "legacy_pending_attribution"
            atom["attribution_review"] = {
                "status": "legacy_pending_attribution",
                "automatic_upgrade_allowed": False,
                "parent_evidence_id": parent["evidence_id"],
                "requested_semantic_origin": requested_semantic_origin,
                "requested_as_user_claim": split.get("as_user_claim"),
                "requested_first_person": split.get("first_person"),
                "requested_content_asset_eligibility": split.get(
                    "eligible_for_content_asset"
                ),
                "requested_is_feynman_evidence": requested_is_feynman,
                "reason": "人工逐字边界不能替代父记录缺失的 attribution envelope",
            }
        if split.get("feynman_basis") is not None:
            basis = split["feynman_basis"]
            if (
                not isinstance(basis, dict)
                or basis.get("course_id") != parent["learning"].get("course_id")
                or basis.get("lesson") != parent["learning"].get("lesson")
                or basis.get("section") not in {"费曼到任务", "检查站"}
            ):
                raise ValueError(
                    f"费曼切片学习依据与父记录不一致：{split['parent_record_id']}／{split['suffix']}"
                )
            canonical = (parent.get("source") or {}).get("canonical_relative_path")
            lesson_path = (
                project_root / Path(str(canonical)).parent / f"{basis['lesson']}.md"
                if canonical
                else None
            )
            if (
                lesson_path is None
                or not lesson_path.is_file()
                or sha256(lesson_path) != basis.get("lesson_sha256")
            ):
                raise ValueError(
                    f"费曼切片 lesson SHA 无法核验：{split['parent_record_id']}／{split['suffix']}"
                )
            atom["learning"]["feynman_basis"] = basis
        if split.get("classification_provenance") is not None:
            provenance = split["classification_provenance"]
            if provenance != {
                "status": "agent_curated",
                "method": "exact_span_manual_review",
                "user_confirmed": False,
            }:
                raise ValueError(
                    f"费曼切片分类来源非法：{split['parent_record_id']}／{split['suffix']}"
                )
            atom["classification_provenance"] = provenance
        if split.get("sensitivity") is not None:
            atom["sensitivity"] = split["sensitivity"]
        curated.append(atom)
    return curated


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def render_index(record_atoms: list[dict], curated_atoms: list[dict]) -> str:
    course_counts = Counter(atom["learning"]["course"] for atom in record_atoms)
    kind_counts = Counter(atom["learning"]["response_kind"] for atom in record_atoms)
    resolution_counts = Counter(atom["source"]["resolution"] for atom in record_atoms)
    split_count = sum(atom["record"]["requires_semantic_split"] for atom in record_atoms)
    feynman_count = len(select_feynman_atoms(record_atoms, curated_atoms))
    pending_attribution_count = sum(
        atom.get("status") == "legacy_pending_attribution"
        for atom in record_atoms
    )

    lines = [
        "# 证据原子索引",
        "",
        "> 本页是机器真源 `evidence-atoms.jsonl` 的阅读索引，不替代逐字记录。",
        "",
        "## 当前统计",
        "",
        f"- 逐字学习记录：{len(record_atoms)} 条",
        f"- 归属待迁移确认：{pending_attribution_count} 条",
        f"- 已人工逐字切分的证据原子：{len(curated_atoms)} 条",
        f"- 证据原子总数：{len(record_atoms) + len(curated_atoms)} 条",
        f"- 费曼与检查站证据：{feynman_count} 条",
        f"- 需要继续拆分材料转述的长记录：{split_count} 条",
        f"- 无法解析到本地 SHA-256 真源：{resolution_counts.get('unresolved', 0)} 条",
        "",
        "## 按课题",
        "",
    ]
    for course, count in sorted(course_counts.items()):
        lines.append(f"- {course}：{count} 条")

    lines.extend(["", "## 按学习证据类型", ""])
    for kind, count in sorted(kind_counts.items()):
        lines.append(f"- `{kind}`：{count} 条")

    lines.extend(
        [
            "",
            "## 使用规则",
            "",
            "- `semantic_origin: user`：只在 hash-bound attribution 明确开放 claim 后，才可作为用户表达候选。",
            "- `status: legacy_pending_attribution`：只保留原始字节与 lineage，不得用于用户 claim、第一人称、费曼掌握度或内容资产。",
            "- `semantic_origin: unresolved_mixed`：整段可能含材料转述，必须先拆分。",
            "- `first_person: exact_verbatim_only`：只允许逐字引用，不允许 Agent 改写后冒充用户。",
            "- `[用户确认]` 写在 confirmation 中，不会改变真实执笔者。",
            "",
            "详见 [[归属与第一人称规则]]。",
            "",
        ]
    )
    return "\n".join(lines)


def build_evidence_bundle(
    records: list[dict],
    snapshot_map: dict[str, list[Path]],
    *,
    split_manifest_path: Path = SPLIT_MANIFEST_PATH,
    project_root: Path = PROJECT_ROOT,
    canonical_root: Path = CANONICAL_ROOT,
) -> tuple[list[dict], list[dict], list[dict]]:
    parent_policies, manifest_splits = load_split_manifest(split_manifest_path)
    record_atoms = [
        to_atom(
            record,
            snapshot_map,
            parent_policies.get(record["record_id"]),
            project_root=project_root,
            canonical_root=canonical_root,
        )
        for record in records
    ]
    curated_atoms = build_curated_atoms(
        record_atoms,
        manifest_splits,
        parent_policies,
        project_root=project_root,
    )
    atoms = record_atoms + curated_atoms
    unresolved = [
        atom for atom in record_atoms if atom["source"]["resolution"] == "unresolved"
    ]
    if unresolved:
        unresolved_ids = ", ".join(
            atom["record"]["parent_record_id"] for atom in unresolved[:5]
        )
        raise ValueError(f"存在 {len(unresolved)} 条无法回溯的记录：{unresolved_ids}")
    return record_atoms, curated_atoms, atoms


def _main() -> int:
    parser = argparse.ArgumentParser(description="从用户逐字账本构建证据原子")
    parser.add_argument("--input", type=Path, default=INPUT_PATH)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--split-manifest", type=Path, default=SPLIT_MANIFEST_PATH)
    parser.add_argument("--snapshot-root", type=Path, action="append")
    args = parser.parse_args()

    output_root = args.output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    records = load_records(args.input.expanduser().resolve())
    roots = (
        [path.expanduser().resolve() for path in args.snapshot_root]
        if args.snapshot_root
        else [SNAPSHOT_ROOT, INCREMENTAL_SNAPSHOT_ROOT]
    )
    snapshot_map = build_snapshot_map(roots)
    record_atoms, curated_atoms, atoms = build_evidence_bundle(
        records,
        snapshot_map,
        split_manifest_path=args.split_manifest.expanduser().resolve(),
    )

    output_path = output_root / "evidence-atoms.jsonl"
    feynman_path = output_root / "feynman-evidence-atoms.jsonl"
    index_path = output_root / "证据原子索引.md"
    write_jsonl(output_path, atoms)
    write_jsonl(
        feynman_path,
        select_feynman_atoms(record_atoms, curated_atoms),
    )
    index_path.write_text(render_index(record_atoms, curated_atoms), encoding="utf-8")

    result = {
        "status": "ok",
        "user_records": len(record_atoms),
        "curated_atoms": len(curated_atoms),
        "evidence_atoms": len(atoms),
        "feynman_evidence": len(select_feynman_atoms(record_atoms, curated_atoms)),
        "requires_semantic_split": sum(atom["record"]["requires_semantic_split"] for atom in record_atoms),
        "unresolved_sources": 0,
        "output": str(output_path),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    with workbench_provenance._locked(LEARNING_ROOT):
        return _main()


if __name__ == "__main__":
    raise SystemExit(main())
