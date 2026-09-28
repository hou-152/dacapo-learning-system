#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
LEARNING_ROOT = SCRIPT_PATH.parents[1]
PROJECT_ROOT = LEARNING_ROOT.parent
COURSE_ROOT = LEARNING_ROOT / "02-课程真源"
DEFAULT_EXISTING = LEARNING_ROOT / "04-用户原话与费曼" / "user-utterances.jsonl"

START_PATTERN = re.compile(r"^<!-- DBS_USER_RESPONSE_START (\{.*\}) -->$")
END_PATTERN = re.compile(r"^<!-- DBS_USER_RESPONSE_END ([A-Za-z0-9_.:-]+) -->$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
INGRESS_REQUEST_ID_PATTERN = re.compile(r"^ilrq_[0-9a-f]{24}$")
ATTRIBUTION_ID_PATTERN = re.compile(r"^ati_[0-9a-f]{24}$")
ALLOWED_KINDS = {
    "feynman_answer",
    "checkpoint_answer",
    "learning_feedback",
    "learner_question",
    "learner_objection",
    "learner_example",
}
RESPONSE_ATTRIBUTION_FIELDS = {
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
SURFACE_AUTHORS = {"user", "agent", "source_author", "joint", "unknown"}
SEMANTIC_ORIGINS = {
    "user",
    "material",
    "agent",
    "joint",
    "mixed",
    "management",
    "unknown",
}
FIRST_PERSON_POLICIES = {
    "forbidden",
    "exact_quote_only",
    "confirmed_wording_only",
}
LEARNER_SIGNAL_QUALITIES = {"independent", "assisted", "unknown", "not_applicable"}
DEFAULT_ATTRIBUTION_GATEWAY = (
    Path.home()
    / "Documents/工程化 skill/skills/dbs-learning/scripts/attribution_gateway.py"
)
DEFAULT_INTERACTIVE_LEARNING_INGRESS = (
    Path.home()
    / "Documents/工程化 skill/skills/dbs-learning/scripts/interactive_learning_ingress.py"
)
GATEWAY_BOUND_FIELDS = {
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_record_id(response_id: str, text: str) -> str:
    payload = f"{response_id}\x1f{text}".encode("utf-8")
    return "utt_" + hashlib.sha256(payload).hexdigest()[:16]


def stable_learner_signal_id(response_id: str, text: str) -> str:
    payload = f"{response_id}\x1f{text}".encode("utf-8")
    return "lsig_" + hashlib.sha256(payload).hexdigest()[:20]


def stable_quarantine_id(response_id: str, source_sha256: str, reason: str) -> str:
    payload = f"{response_id}\x1f{source_sha256}\x1f{reason}".encode("utf-8")
    return "rquar_" + hashlib.sha256(payload).hexdigest()[:20]


def stable_runtime_response_id(
    course_id: str,
    lesson: str,
    kind: str,
    lesson_sha256: str,
    response_sha256: str,
    ingress_request_id: str,
) -> str:
    payload = "\x1f".join(
        (
            course_id,
            lesson,
            kind,
            lesson_sha256,
            response_sha256,
            ingress_request_id,
        )
    ).encode("utf-8")
    return "rsp_" + hashlib.sha256(payload).hexdigest()[:24]


def _attribution_gateway_path() -> Path:
    configured = os.environ.get("DBS_LEARNING_ATTRIBUTION_GATEWAY")
    path = Path(configured).expanduser() if configured else DEFAULT_ATTRIBUTION_GATEWAY
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f"归属网关不存在：{path}")
    return path


def _interactive_learning_ingress_path() -> Path:
    configured = os.environ.get("DBS_LEARNING_INTERACTIVE_INGRESS")
    path = (
        Path(configured).expanduser()
        if configured
        else DEFAULT_INTERACTIVE_LEARNING_INGRESS
    )
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f"交互式学习预接口不存在：{path}")
    return path


def _revalidate_attribution_envelope(
    envelope_path: str,
    envelope_sha256: str,
) -> dict[str, Any]:
    path = Path(envelope_path).expanduser()
    if not path.is_absolute():
        raise ValueError("attribution.envelope_path 必须是绝对路径")
    result = subprocess.run(
        [
            sys.executable,
            str(_attribution_gateway_path()),
            "validate",
            "--path",
            str(path),
            "--expected-sha256",
            envelope_sha256,
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("归属网关没有返回合法 JSON") from exc
    if result.returncode != 0 or not isinstance(payload, dict) or payload.get("ok") is not True:
        raise ValueError(f"归属 envelope 复验失败：{payload}")
    return payload


def _revalidate_learning_ingress(
    ingress_path: str,
    ingress_sha256: str,
) -> dict[str, Any]:
    path = Path(ingress_path).expanduser()
    if not path.is_absolute():
        raise ValueError("attribution.ingress_path 必须是绝对路径")
    result = subprocess.run(
        [
            sys.executable,
            str(_interactive_learning_ingress_path()),
            "validate",
            "--path",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("交互式学习预接口没有返回合法 JSON") from exc
    if (
        result.returncode != 0
        or not isinstance(payload, dict)
        or payload.get("ok") is not True
        or payload.get("ingress_path") != str(path.resolve())
        or payload.get("ingress_sha256") != ingress_sha256
    ):
        raise ValueError(f"交互式学习 ingress 复验失败：{payload}")
    return payload


def _require_sha256(value: object, location: str) -> str:
    if not isinstance(value, str) or SHA256_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{location} 必须是小写 SHA-256")
    return value


def _require_bool(value: object, location: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{location} 必须是布尔值")
    return value


def _validate_response_attribution(
    metadata: dict[str, Any],
    verbatim: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Return one runtime-validated learner-signal binding or a closed disposition.

    A legacy marker and a direct-runtime unknown-author frame remain parseable so old
    course logs stay readable.  Neither is promoted into the canonical user ledger.
    """

    attribution = metadata.get("attribution")
    if attribution is None:
        return None, "legacy_marker_without_attribution"
    if not isinstance(attribution, dict) or set(attribution) != RESPONSE_ATTRIBUTION_FIELDS:
        raise ValueError("响应归属块字段不完整或被篡改")

    actual_response_sha256 = hashlib.sha256(verbatim.encode("utf-8")).hexdigest()
    declared_response_sha256 = metadata.get("response_sha256")
    if declared_response_sha256 != actual_response_sha256:
        raise ValueError("响应正文与 response_sha256 不一致")

    status = attribution.get("status")
    if status == "runtime_framed_unknown_author":
        if (
            attribution.get("ingress_path") is not None
            or attribution.get("ingress_request_id") is not None
            or attribution.get("ingress_sha256") is not None
            or attribution.get("attribution_id") is not None
            or attribution.get("envelope_path") is not None
            or attribution.get("envelope_sha256") is not None
            or attribution.get("usage_binding") is not None
            or attribution.get("source_revision_sha256") is not None
            or attribution.get("source_locator") is not None
            or attribution.get("surface_author") != "unknown"
            or attribution.get("semantic_origin") != "unknown"
            or attribution.get("feynman_learner_signal_allowed") is not False
            or attribution.get("strict_mastery_evidence_allowed") is not False
            or attribution.get("claim_eligible") is not False
            or attribution.get("first_person_allowed") != "forbidden"
            or attribution.get("learner_signal_quality") != "not_applicable"
        ):
            raise ValueError("unknown-author 响应帧错误开放了归属或下游权限")
        capture_actor = attribution.get("capture_actor")
        if capture_actor != {"kind": "system", "actor_ref": "course_runtime"}:
            raise ValueError("unknown-author 响应帧的 capture_actor 非法")
        if attribution.get("source_channel") != "dbs_response_frame":
            raise ValueError("unknown-author 响应帧的 source_channel 非法")
        return None, "runtime_framed_unknown_author"

    if status != "validated":
        raise ValueError(f"响应归属状态非法：{status}")
    ingress_request_id = attribution.get("ingress_request_id")
    if (
        not isinstance(ingress_request_id, str)
        or INGRESS_REQUEST_ID_PATTERN.fullmatch(ingress_request_id) is None
    ):
        raise ValueError("validated 归属块缺少合法 ingress_request_id")
    attribution_id = attribution.get("attribution_id")
    if (
        not isinstance(attribution_id, str)
        or ATTRIBUTION_ID_PATTERN.fullmatch(attribution_id) is None
    ):
        raise ValueError("validated 归属块缺少合法 attribution_id")
    for field in ("ingress_sha256", "envelope_sha256", "source_revision_sha256"):
        _require_sha256(attribution.get(field), f"attribution.{field}")
    ingress_path = attribution.get("ingress_path")
    if not isinstance(ingress_path, str) or not Path(ingress_path).is_absolute():
        raise ValueError("validated 归属块缺少绝对 ingress_path")
    envelope_path = attribution.get("envelope_path")
    if not isinstance(envelope_path, str) or not Path(envelope_path).is_absolute():
        raise ValueError("validated 归属块缺少绝对 envelope_path")

    source_channel = attribution.get("source_channel")
    if not isinstance(source_channel, str) or not source_channel:
        raise ValueError("validated 归属块缺少 source_channel")
    source_locator = attribution.get("source_locator")
    if (
        not isinstance(source_locator, dict)
        or set(source_locator) != {"kind", "ref"}
        or any(
            not isinstance(source_locator.get(field), str) or not source_locator[field]
            for field in ("kind", "ref")
        )
    ):
        raise ValueError("validated 归属块缺少合法 source_locator")
    capture_actor = attribution.get("capture_actor")
    if (
        not isinstance(capture_actor, dict)
        or set(capture_actor)
        != {"kind", "actor_ref", "receipt_ref", "verification"}
        or not isinstance(capture_actor.get("kind"), str)
        or not capture_actor["kind"]
    ):
        raise ValueError("validated 归属块缺少合法 capture_actor")

    surface_author = attribution.get("surface_author")
    semantic_origin = attribution.get("semantic_origin")
    first_person_allowed = attribution.get("first_person_allowed")
    signal_quality = attribution.get("learner_signal_quality")
    if surface_author not in SURFACE_AUTHORS:
        raise ValueError("validated 归属块的 surface_author 非法")
    if semantic_origin not in SEMANTIC_ORIGINS:
        raise ValueError("validated 归属块的 semantic_origin 非法")
    if first_person_allowed not in FIRST_PERSON_POLICIES:
        raise ValueError("validated 归属块的 first_person_allowed 非法")
    if signal_quality not in LEARNER_SIGNAL_QUALITIES:
        raise ValueError("validated 归属块的 learner_signal_quality 非法")

    learner_allowed = _require_bool(
        attribution.get("feynman_learner_signal_allowed"),
        "attribution.feynman_learner_signal_allowed",
    )
    strict_allowed = _require_bool(
        attribution.get("strict_mastery_evidence_allowed"),
        "attribution.strict_mastery_evidence_allowed",
    )
    claim_eligible = _require_bool(
        attribution.get("claim_eligible"),
        "attribution.claim_eligible",
    )
    if not learner_allowed:
        return None, "validated_but_not_feynman_learner_signal"
    if signal_quality == "not_applicable":
        raise ValueError("已许可 learner signal 不能使用 not_applicable 质量")
    if claim_eligible and not (
        surface_author == "user"
        and semantic_origin == "user"
        and first_person_allowed == "confirmed_wording_only"
    ):
        raise ValueError("claim_eligible 与用户作者、用户语义或措辞确认不一致")
    if strict_allowed and not (
        claim_eligible and signal_quality == "independent"
    ):
        raise ValueError("strict mastery 权限与 claim 或独立生成质量不一致")
    if first_person_allowed == "confirmed_wording_only" and not claim_eligible:
        raise ValueError("confirmed wording 权限不能脱离 claim_eligible")
    verified = _revalidate_attribution_envelope(
        envelope_path,
        str(attribution["envelope_sha256"]),
    )
    if any(attribution.get(field) != verified.get(field) for field in GATEWAY_BOUND_FIELDS):
        raise ValueError("marker 内嵌归属块与真实 attribution envelope 不一致")
    if verified.get("text") != verbatim or verified.get("text_sha256") != actual_response_sha256:
        raise ValueError("attribution envelope 没有绑定 marker 的精确回答字节")

    course_id = metadata.get("course_id")
    lesson_sha256 = metadata.get("lesson_sha256")
    if not isinstance(course_id, str) or not course_id:
        raise ValueError("validated marker 缺少 course_id")
    _require_sha256(lesson_sha256, "metadata.lesson_sha256")
    usage_binding = attribution.get("usage_binding")
    expected_usage = {
        "request_id": ingress_request_id,
        "operation": (usage_binding or {}).get("operation")
        if isinstance(usage_binding, dict)
        else None,
        "actor_ref": capture_actor.get("actor_ref"),
        "course_id": course_id,
        "lesson": metadata.get("lesson"),
        "response_kind": metadata.get("kind"),
        "lesson_sha256": lesson_sha256,
    }
    if (
        not isinstance(usage_binding, dict)
        or usage_binding != expected_usage
        or usage_binding.get("operation")
        not in {"submit_learner_signal", "mastery_check"}
    ):
        raise ValueError("attribution usage binding 与 marker 的请求、课程或课次不一致")
    expected_response_id = stable_runtime_response_id(
        course_id,
        str(metadata["lesson"]),
        str(metadata["kind"]),
        str(lesson_sha256),
        actual_response_sha256,
        ingress_request_id,
    )
    if metadata.get("response_id") != expected_response_id:
        raise ValueError("marker response_id 与 runtime 绑定公式不一致")
    ingress_validation = _revalidate_learning_ingress(
        ingress_path,
        str(attribution["ingress_sha256"]),
    )
    preflight = ingress_validation.get("preflight")
    command = preflight.get("runtime_command") if isinstance(preflight, dict) else None
    if (
        ingress_validation.get("request_id") != ingress_request_id
        or ingress_validation.get("operation") != usage_binding.get("operation")
        or not isinstance(command, dict)
        or command.get("action") != "record_attributed_response"
        or command.get("course_id") != course_id
        or command.get("expected_lesson") != metadata.get("lesson")
        or command.get("kind") != metadata.get("kind")
        or command.get("attribution_id") != attribution_id
        or command.get("attribution_path") != envelope_path
        or command.get("attribution_sha256") != attribution.get("envelope_sha256")
        or command.get("strict_mastery")
        is not (usage_binding.get("operation") == "mastery_check")
    ):
        raise ValueError("hash-bound ingress 没有授权这个精确 runtime 响应帧")
    return dict(attribution), None


def _register_attribution_single_use(
    attribution: dict[str, Any],
    response_id: str,
    seen: dict[str, dict[str, str]],
) -> bool:
    """Return false when one immutable attribution identity owns another frame."""

    identities = {
        "attribution_id": attribution.get("attribution_id"),
        "envelope_sha256": attribution.get("envelope_sha256"),
        "ingress_request_id": attribution.get("ingress_request_id"),
    }
    for label, identity in identities.items():
        if not isinstance(identity, str) or not identity:
            return False
        owner = seen[label].get(identity)
        if owner is not None and owner != response_id:
            return False
    for label, identity in identities.items():
        seen[label][str(identity)] = response_id
    return True


def _new_attribution_use_index() -> dict[str, dict[str, str]]:
    return {
        "attribution_id": {},
        "envelope_sha256": {},
        "ingress_request_id": {},
    }


def _assert_record_attribution_single_use(rows: list[dict[str, Any]]) -> None:
    seen = _new_attribution_use_index()
    for row in rows:
        attribution = row.get("attribution")
        response_id = row.get("response_id")
        if not isinstance(attribution, dict) or not isinstance(response_id, str):
            continue
        if not _register_attribution_single_use(attribution, response_id, seen):
            raise ValueError(
                f"response_id {response_id} 重用了其他响应帧的 attribution／envelope／ingress"
            )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} 不是对象")
            rows.append(value)
    return rows


def load_unique_json_object(raw: str, location: str) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{location} JSON 含重复键：{key}")
            result[key] = value
        return result

    try:
        value = json.loads(raw, object_pairs_hook=unique_object)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{location} 响应标记 JSON 无效：{exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{location} 响应标记必须是对象")
    return value


def parse_marked_file(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    results: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        line_without_newline = lines[index].rstrip("\r\n")
        match = START_PATTERN.fullmatch(line_without_newline)
        if not match:
            index += 1
            continue
        metadata = load_unique_json_object(match.group(1), f"{path}:{index + 1}")
        response_id = metadata.get("response_id")
        lesson = metadata.get("lesson")
        kind = metadata.get("kind")
        if not isinstance(response_id, str) or not response_id:
            raise ValueError(f"{path}:{index + 1} 缺少 response_id")
        if not isinstance(lesson, str) or not lesson:
            raise ValueError(f"{path}:{index + 1} 缺少 lesson")
        if kind not in ALLOWED_KINDS:
            raise ValueError(f"{path}:{index + 1} 非法 kind：{kind}")
        body_start = index + 1
        cursor = body_start
        while cursor < len(lines):
            end_line = lines[cursor].rstrip("\r\n")
            end_match = END_PATTERN.fullmatch(end_line)
            if end_match:
                if end_match.group(1) != response_id:
                    raise ValueError(
                        f"{path}:{cursor + 1} 结束 response_id 与起始标记不一致"
                    )
                break
            if START_PATTERN.fullmatch(end_line):
                raise ValueError(f"{path}:{cursor + 1} 响应标记不允许嵌套")
            cursor += 1
        if cursor >= len(lines):
            raise ValueError(f"{path}:{index + 1} 响应标记没有闭合")

        raw = "".join(lines[body_start:cursor])
        if raw.endswith("\r\n"):
            raw = raw[:-2]
        elif raw.endswith("\n") or raw.endswith("\r"):
            raw = raw[:-1]
        if not raw:
            raise ValueError(f"{path}:{index + 1} 响应正文为空")
        results.append(
            {
                "metadata": metadata,
                "verbatim": raw,
                "start_line": body_start + 1,
                "end_line": cursor,
            }
        )
        index = cursor + 1
    return results


def to_record(
    path: Path,
    parsed: dict[str, Any],
    *,
    source_relative_path: Path | None = None,
    expected_source_sha256: str | None = None,
    snapshot_path: Path | None = None,
    course_root: Path = COURSE_ROOT,
) -> dict[str, Any]:
    metadata = parsed["metadata"]
    verbatim = parsed["verbatim"]
    attribution, blocked_reason = _validate_response_attribution(metadata, verbatim)
    if attribution is None:
        raise ValueError(f"响应未通过归属门：{blocked_reason}")
    if attribution.get("surface_author") != "user":
        raise ValueError("非用户字面作者的 learner signal 不能进入 user-utterances")
    relative = source_relative_path or path.relative_to(COURSE_ROOT)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"非法课程相对路径：{relative}")
    actual_source_sha256 = sha256(path)
    if expected_source_sha256 and actual_source_sha256 != expected_source_sha256:
        raise ValueError(
            f"不可变来源 SHA 不一致：期望 {expected_source_sha256}，实际 {actual_source_sha256}"
        )
    canonical_path = course_root / relative
    course = metadata.get("course") or relative.parts[0]
    response_id = metadata["response_id"]
    claim_eligible = bool(attribution["claim_eligible"])
    surface_author = str(attribution["surface_author"])
    semantic_origin = str(attribution["semantic_origin"])
    attribution_reason = (
        "归属 envelope 已确认用户字面作者、用户语义来源和具体措辞；"
        "仍需独立内容入选流程"
        if claim_eligible
        else "这是归属网关允许的学习者信号；字面作者、语义来源、原创性和第一人称权限"
        "只能读取 attribution，不能由 response marker 推断"
    )
    return {
        "schema_version": "user-utterance/v3",
        "record_id": stable_record_id(response_id, verbatim),
        "response_id": response_id,
        "course_id": metadata.get("course_id"),
        "branch_id": metadata.get("branch_id"),
        "course": course,
        "lesson": metadata["lesson"],
        "lesson_sha256": metadata["lesson_sha256"],
        "response_sha256": metadata["response_sha256"],
        "evidence_type": metadata["kind"],
        "captured_at": metadata.get("captured_at"),
        "speaker": "user",
        "speaker_role": "learner_signal_submitter",
        "speaker_verification": "validated_attribution_learner_signal",
        "attribution": attribution,
        "identity": {
            "surface_author": surface_author,
            "semantic_origin": semantic_origin,
        },
        "verbatim": verbatim,
        "verbatim_status": "source_exact",
        "classification_status": "pending_semantic_atomization",
        "content_roles": [],
        "eligible_for_content_asset": False,
        "eligibility": {
            "as_verbatim_quote": True,
            "as_user_claim": claim_eligible,
            "as_material_fact": False,
            "as_feynman_learner_signal": True,
            "strict_mastery_evidence": bool(
                attribution["strict_mastery_evidence_allowed"]
            ),
            "reason": attribution_reason,
        },
        "source_kind": "attributed_learner_response",
        "source_set": "course_source",
        "source_path": str(canonical_path),
        "snapshot_path": str(snapshot_path) if snapshot_path else None,
        "source_relative_path": relative.as_posix(),
        "source_sha256": actual_source_sha256,
        "locator": {
            "start_line": parsed["start_line"],
            "end_line": parsed["end_line"],
            "response_id": response_id,
        },
    }


def to_learner_signal_record(
    path: Path,
    parsed: dict[str, Any],
    *,
    source_relative_path: Path,
    expected_source_sha256: str,
    snapshot_path: Path,
    course_root: Path = COURSE_ROOT,
) -> dict[str, Any]:
    metadata = parsed["metadata"]
    verbatim = parsed["verbatim"]
    attribution, reason = _validate_response_attribution(metadata, verbatim)
    if attribution is None:
        raise ValueError(f"响应未通过 learner-signal 归属门：{reason}")
    relative = source_relative_path
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"非法课程相对路径：{relative}")
    actual_source_sha256 = sha256(path)
    if actual_source_sha256 != expected_source_sha256:
        raise ValueError(
            f"不可变来源 SHA 不一致：期望 {expected_source_sha256}，实际 {actual_source_sha256}"
        )
    response_id = str(metadata["response_id"])
    return {
        "schema_version": "feynman-learner-signal/v1",
        "signal_id": stable_learner_signal_id(response_id, verbatim),
        "response_id": response_id,
        "course_id": metadata.get("course_id"),
        "course": metadata.get("course") or relative.parts[0],
        "lesson": metadata["lesson"],
        "lesson_sha256": metadata["lesson_sha256"],
        "signal_kind": metadata["kind"],
        "captured_at": metadata.get("captured_at"),
        "verbatim": verbatim,
        "verbatim_sha256": hashlib.sha256(verbatim.encode("utf-8")).hexdigest(),
        "attribution": attribution,
        "permissions": {
            "feynman_learner_signal": True,
            "strict_mastery_evidence": bool(
                attribution["strict_mastery_evidence_allowed"]
            ),
            "user_claim": bool(attribution["claim_eligible"]),
            "first_person": attribution["first_person_allowed"],
            "content_asset": False,
        },
        "source": {
            "canonical_path": str(course_root / relative),
            "snapshot_path": str(snapshot_path),
            "source_relative_path": relative.as_posix(),
            "source_sha256": actual_source_sha256,
            "locator": {
                "start_line": parsed["start_line"],
                "end_line": parsed["end_line"],
                "response_id": response_id,
            },
        },
    }


def to_quarantine_record(
    path: Path,
    parsed: dict[str, Any],
    *,
    reason: str,
    source_relative_path: Path,
    expected_source_sha256: str,
    snapshot_path: Path,
    course_root: Path = COURSE_ROOT,
) -> dict[str, Any]:
    metadata = parsed["metadata"]
    verbatim = parsed["verbatim"]
    relative = source_relative_path
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"非法课程相对路径：{relative}")
    actual_source_sha256 = sha256(path)
    if actual_source_sha256 != expected_source_sha256:
        raise ValueError(
            f"不可变来源 SHA 不一致：期望 {expected_source_sha256}，实际 {actual_source_sha256}"
        )
    response_id = str(metadata["response_id"])
    return {
        "schema_version": "response-attribution-quarantine/v1",
        "quarantine_id": stable_quarantine_id(
            response_id, actual_source_sha256, reason
        ),
        "response_id": response_id,
        "course_id": metadata.get("course_id"),
        "course": metadata.get("course") or relative.parts[0],
        "lesson": metadata["lesson"],
        "signal_kind": metadata["kind"],
        "verbatim": verbatim,
        "verbatim_sha256": hashlib.sha256(verbatim.encode("utf-8")).hexdigest(),
        "observed_attribution": metadata.get("attribution"),
        "reason_code": reason,
        "forced_permissions": {
            "feynman_learner_signal": False,
            "strict_mastery_evidence": False,
            "user_claim": False,
            "first_person": "forbidden",
            "content_asset": False,
        },
        "source": {
            "canonical_path": str(course_root / relative),
            "snapshot_path": str(snapshot_path),
            "source_relative_path": relative.as_posix(),
            "source_sha256": actual_source_sha256,
            "locator": {
                "start_line": parsed["start_line"],
                "end_line": parsed["end_line"],
                "response_id": response_id,
            },
        },
        "promotion_gate": {
            "required": True,
            "accepted_evidence": [
                "validated_attribution_envelope_bound_to_exact_response",
                "explicit_user_hash_confirmation",
            ],
            "reason": "marker 或 unknown-author frame 只能证明课程位置，不能证明作者身份。",
        },
    }


def collect_records() -> list[dict[str, Any]]:
    records, _, _ = collect_records_with_dispositions()
    return records


def collect_records_with_dispositions() -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    records: list[dict[str, Any]] = []
    learner_signals: list[dict[str, Any]] = []
    quarantines: list[dict[str, Any]] = []
    response_ids: set[str] = set()
    attribution_uses = _new_attribution_use_index()
    for path in sorted(COURSE_ROOT.rglob("*.md")):
        if not path.is_file():
            continue
        relative = path.relative_to(COURSE_ROOT)
        source_hash = sha256(path)
        for parsed in parse_marked_file(path):
            response_id = parsed["metadata"]["response_id"]
            if response_id in response_ids:
                raise ValueError(f"response_id 重复：{response_id}")
            response_ids.add(response_id)
            try:
                attribution, reason = _validate_response_attribution(
                    parsed["metadata"], parsed["verbatim"]
                )
            except ValueError as exc:
                attribution, reason = None, "invalid_attribution_contract"
            if (
                attribution is not None
                and not _register_attribution_single_use(
                    attribution, str(response_id), attribution_uses
                )
            ):
                attribution, reason = None, "reused_attribution_contract"
            if attribution is None:
                quarantines.append(
                    to_quarantine_record(
                        path,
                        parsed,
                        reason=str(reason),
                        source_relative_path=relative,
                        expected_source_sha256=source_hash,
                        snapshot_path=path,
                    )
                )
                continue
            learner_signals.append(
                to_learner_signal_record(
                    path,
                    parsed,
                    source_relative_path=relative,
                    expected_source_sha256=source_hash,
                    snapshot_path=path,
                )
            )
            if attribution["surface_author"] == "user":
                records.append(to_record(path, parsed))
    return records, learner_signals, quarantines


def collect_records_from_source(
    source_blob: Path,
    source_relative_path: str,
    source_sha256: str,
    snapshot_path: Path,
    course_root: Path = COURSE_ROOT,
) -> list[dict[str, Any]]:
    records, _, _ = collect_records_from_source_with_dispositions(
        source_blob,
        source_relative_path,
        source_sha256,
        snapshot_path,
        course_root,
    )
    return records


def collect_records_from_source_with_dispositions(
    source_blob: Path,
    source_relative_path: str,
    source_sha256: str,
    snapshot_path: Path,
    course_root: Path = COURSE_ROOT,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    relative = Path(source_relative_path)
    parsed_rows = parse_marked_file(source_blob)
    records: list[dict[str, Any]] = []
    learner_signals: list[dict[str, Any]] = []
    quarantines: list[dict[str, Any]] = []
    response_ids: set[str] = set()
    attribution_uses = _new_attribution_use_index()
    for parsed in parsed_rows:
        response_id = parsed["metadata"]["response_id"]
        if response_id in response_ids:
            raise ValueError(f"同一来源 response_id 重复：{response_id}")
        response_ids.add(response_id)
        try:
            attribution, reason = _validate_response_attribution(
                parsed["metadata"], parsed["verbatim"]
            )
        except ValueError:
            attribution, reason = None, "invalid_attribution_contract"
        if (
            attribution is not None
            and not _register_attribution_single_use(
                attribution, str(response_id), attribution_uses
            )
        ):
            attribution, reason = None, "reused_attribution_contract"
        if attribution is None:
            quarantines.append(
                to_quarantine_record(
                    source_blob,
                    parsed,
                    reason=str(reason),
                    source_relative_path=relative,
                    expected_source_sha256=source_sha256,
                    snapshot_path=snapshot_path,
                    course_root=course_root,
                )
            )
            continue
        learner_signals.append(
            to_learner_signal_record(
                source_blob,
                parsed,
                source_relative_path=relative,
                expected_source_sha256=source_sha256,
                snapshot_path=snapshot_path,
                course_root=course_root,
            )
        )
        if attribution["surface_author"] == "user":
            records.append(
                to_record(
                    source_blob,
                    parsed,
                    source_relative_path=relative,
                    expected_source_sha256=source_sha256,
                    snapshot_path=snapshot_path,
                    course_root=course_root,
                )
            )
    return records, learner_signals, quarantines


def merge_records(existing: list[dict[str, Any]], marked: list[dict[str, Any]]) -> list[dict[str, Any]]:
    _assert_record_attribution_single_use([*existing, *marked])
    result = list(existing)
    by_response = {
        row.get("response_id"): row
        for row in existing
        if isinstance(row.get("response_id"), str)
    }
    record_ids = {row.get("record_id") for row in existing}
    for row in marked:
        response_id = row["response_id"]
        old = by_response.get(response_id)
        if old is not None:
            if old.get("record_id") != row["record_id"]:
                raise ValueError(
                    f"response_id {response_id} 的逐字内容发生变化；必须新增 response_id，不能静默覆盖"
                )
            if old.get("schema_version") != row.get("schema_version") or old.get(
                "attribution"
            ) != row.get("attribution"):
                raise ValueError(
                    f"response_id {response_id} 的归属合同发生变化；必须走显式迁移，不能静默升级"
                )
            continue
        if row["record_id"] in record_ids:
            raise ValueError(f"record_id 碰撞：{row['record_id']}")
        result.append(row)
        by_response[response_id] = row
        record_ids.add(row["record_id"])
    return result


def merge_identity_records(
    existing: list[dict[str, Any]],
    incoming: list[dict[str, Any]],
    *,
    identity_field: str,
) -> list[dict[str, Any]]:
    result = list(existing)
    by_identity = {
        row.get(identity_field): row
        for row in existing
        if isinstance(row.get(identity_field), str)
    }
    for row in incoming:
        identity = row.get(identity_field)
        if not isinstance(identity, str) or not identity:
            raise ValueError(f"{identity_field} 缺失")
        old = by_identity.get(identity)
        if old is not None:
            if old != row:
                raise ValueError(f"{identity_field} {identity} 内容冲突，不能静默覆盖")
            continue
        result.append(row)
        by_identity[identity] = row
    return result


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="提取显式标记的用户逐字学习回答")
    parser.add_argument("--existing", type=Path, default=DEFAULT_EXISTING)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-blob", type=Path)
    parser.add_argument("--source-relative-path")
    parser.add_argument("--source-sha256")
    parser.add_argument("--snapshot-path", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        output = args.output.expanduser().resolve()
        if output == DEFAULT_EXISTING.resolve():
            raise ValueError("禁止直接覆盖 canonical 原话账本；请先输出到 Worker staging")
        source_values = (
            args.source_blob,
            args.source_relative_path,
            args.source_sha256,
            args.snapshot_path,
        )
        if any(value is not None for value in source_values):
            if not all(value is not None for value in source_values):
                raise ValueError(
                    "单来源模式必须同时提供 --source-blob、--source-relative-path、"
                    "--source-sha256 与 --snapshot-path"
                )
            marked, learner_signals, quarantines = (
                collect_records_from_source_with_dispositions(
                args.source_blob.expanduser().resolve(),
                args.source_relative_path,
                args.source_sha256,
                args.snapshot_path.expanduser().resolve(),
            )
            )
        else:
            marked, learner_signals, quarantines = collect_records_with_dispositions()
        existing = load_jsonl(args.existing.expanduser().resolve())
        merged = merge_records(existing, marked)
        write_jsonl(output, merged)
        result = {
            "status": "ok",
            "marked_responses": len(marked),
            "existing_records": len(existing),
            "output_records": len(merged),
            "new_records": len(merged) - len(existing),
            "learner_signals": len(learner_signals),
            "quarantined_response_frames": len(quarantines),
            "quarantine_dispositions": [
                {
                    "response_id": row["response_id"],
                    "reason": row["reason_code"],
                }
                for row in quarantines
            ],
            "output": str(output),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
