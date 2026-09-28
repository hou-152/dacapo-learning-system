"""Append-only verbatim capture and conservative, hash-bound attribution review.

`root` is the canonical learning root, never the workspace or course directory.
Callers must verify the source message's user role before capture. A user message
does not prove semantic authorship. Reviews deliberately grant no claim, voice,
content-asset or mastery permission; authenticated attribution stays with the
existing attribution_gateway / interactive_learning_ingress contract.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile

SCHEMA = "user-utterance/workbench-v1"
LEDGER = Path("04-用户原话与费曼/user-utterances.jsonl")
REVIEWS = Path("05-证据原子/workbench-attribution-reviews.jsonl")
ATOMS = Path("05-证据原子/evidence-atoms.jsonl")
ORIGINS = {"user", "material", "mixed", "unknown"}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _append(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(_json(value) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


@contextmanager
def _locked(root: Path):
    directory = root / LEDGER.parent
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".workbench-provenance.lock").open("a") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _contains(value: object, text: str) -> bool:
    if isinstance(value, str):
        return value == text
    if isinstance(value, list):
        text_blocks = [item["text"] for item in value
                       if isinstance(item, dict) and item.get("type") == "text"
                       and isinstance(item.get("text"), str)]
        if text_blocks and "\n".join(text_blocks) == text:
            return True
        return any(_contains(item, text) for item in value)
    if isinstance(value, dict):
        return any(_contains(item, text) for item in value.values())
    return False


def _source(record: dict) -> bytes:
    path = Path(record.get("source_snapshot_path") or record["source_path"])
    if not path.is_absolute():
        raise ValueError("source_path 必须是绝对路径")
    raw = path.read_bytes()
    if _sha(raw) != record["source_sha256"]:
        raise ValueError("来源 SHA-256 绑定失效")
    text = record["verbatim"]
    decoded = raw.decode("utf-8")
    if record.get("kind") == "note":
        # 收件箱笔记是纯文本，整份文件就是这条记录，不做行级 JSON 解析——
        # 否则正文首行恰好是合法 JSON 字面量（例如引用了一句带引号的话）时会被误判成结构化来源。
        if text not in decoded:
            raise ValueError("逐字内容不在指定来源中")
        return raw
    # JSON escaping is transport encoding, not a license to normalize wording.
    try:
        parsed = json.loads(decoded)
    except json.JSONDecodeError:
        parsed = None
    if parsed is not None:
        matched = _contains(parsed, text)
    else:
        line = 1 if record.get("source_snapshot_path") else record["source_line"]
        lines = decoded.splitlines(keepends=True)
        if line > len(lines):
            raise ValueError("来源行号越界")
        try:
            parsed_line = json.loads(lines[line - 1])
        except json.JSONDecodeError:
            offset = sum(len(item) for item in lines[:line - 1])
            position = decoded.find(text, offset)
            matched = position >= offset and position < offset + len(lines[line - 1])
        else:
            matched = _contains(parsed_line, text)
    if not matched:
        raise ValueError("逐字内容不在指定来源中")
    return raw


def _validate_record(record: dict) -> None:
    if record.get("schema_version") != SCHEMA:
        raise ValueError("此接口只处理工作台捕获记录")
    if _sha(record["verbatim"].encode("utf-8")) != record["verbatim_sha256"]:
        raise ValueError("原话 SHA-256 绑定失效")
    expected_id = "utt_wb_" + _sha(record["event_id"].encode("utf-8"))[:24]
    if record["record_id"] != expected_id:
        raise ValueError("记录 ID 绑定失效")
    _source(record)


def _lookup(root: Path, event_id: str) -> dict:
    matches = [row for row in _rows(root / LEDGER)
               if row.get("event_id") == event_id or row.get("record_id") == event_id]
    if len(matches) != 1:
        raise ValueError("记录不存在或 ID 重复")
    record = matches[0]
    _validate_record(record)
    return record


def _review(root: Path, record: dict) -> dict | None:
    result = None
    for review in _rows(root / REVIEWS):
        if review.get("record_id") != record["record_id"]:
            continue
        payload = {key: value for key, value in review.items() if key != "review_id"}
        if review.get("review_id") != "wbr_" + _sha(_json(payload).encode("utf-8")):
            raise ValueError("归属判断内容 SHA-256 绑定失效")
        if (review.get("verbatim_sha256") != record["verbatim_sha256"]
                or review.get("source_sha256") != record["source_sha256"]):
            raise ValueError("归属判断与原话 SHA-256 绑定失效")
        result = review
    return result


def _decorate(root: Path, record: dict) -> dict:
    result = deepcopy(record)
    result["attribution_review"] = _review(root, record)
    result["semantic_origin"] = "unknown"
    result["requested_origin"] = (result["attribution_review"] or {}).get("origin", "unknown")
    result["first_person_allowed"] = "forbidden"
    result["claim_eligible"] = False
    result["strict_mastery_evidence_allowed"] = False
    result["feynman_learner_signal_allowed"] = False
    return result


def capture(root: Path, event: dict) -> dict:
    """Capture a verified user message verbatim; retries return the first record.

    source_sha256 hashes the entire source file (or immutable source_snapshot_path).
    source_line is 1-based. Revised messages require new event IDs. Optional
    source_snapshot_path must contain the same bytes/hash as the source revision.
    """
    root = Path(root).resolve()
    for field in ("id", "kind", "session_id", "message_id", "source_path", "source_sha256", "timestamp", "verbatim"):
        if not isinstance(event.get(field), str) or not event[field]:
            raise ValueError(f"{field} 必须是非空字符串")
    if event["kind"] not in {"dsh", "pi", "note"}:
        raise ValueError("来源 kind 非法")
    if type(event.get("source_line")) is not int or event["source_line"] < 1:
        raise ValueError("source_line 必须是从 1 开始的行号")
    _source(event)
    with _locked(root):
        records = _rows(root / LEDGER)
        existing = [row for row in records if row.get("event_id") == event["id"]]
        if existing:
            if len(existing) != 1:
                raise ValueError("event_id 重复")
            record = existing[0]
            for field in ("kind", "session_id", "message_id", "verbatim"):
                if record[field] != event[field]:
                    raise ValueError("同一 event_id 的内容发生改变；修订必须使用新 ID")
            _validate_record(record)
        else:
            record = {key: event.get(key) for key in (
                "kind", "session_id", "message_id", "source_path", "source_sha256",
                "source_line", "timestamp", "verbatim", "course", "lesson")}
            if event.get("source_snapshot_path"):
                record["source_snapshot_path"] = str(Path(event["source_snapshot_path"]).resolve())
            source = Path(record.get("source_snapshot_path") or record["source_path"]).resolve()
            try:
                relative = source.relative_to(root.parent).as_posix()
            except ValueError:
                relative = "external-workbench-source/" + record["source_sha256"]
            record.update({
                "schema_version": SCHEMA,
                "event_id": event["id"],
                "record_id": "utt_wb_" + _sha(event["id"].encode("utf-8"))[:24],
                "response_id": "workbench:" + event["id"],
                "verbatim_sha256": _sha(event["verbatim"].encode("utf-8")),
                "source_relative_path": relative,
                "speaker": "user", "verbatim_status": "source_exact",
                "speaker_verification": "upstream_user_role_verified_not_semantic_authorship",
                "evidence_type": "workbench_capture", "content_roles": [],
                "classification_status": "unclassified", "eligible_for_content_asset": False,
                "locator": {"line_start": event["source_line"], "message_id": event["message_id"]},
                "identity": {"surface_author": "user", "semantic_origin": "unknown"},
            })
            if any(row.get("record_id") == record["record_id"] for row in records):
                raise ValueError("record_id 碰撞")
            _append(root / LEDGER, record)
        _persist_atom(root, to_atom(record, root))
        return _decorate(root, record)


def _spans(record: dict, spans: list[dict] | None) -> list[dict]:
    result = []
    text = record["verbatim"]
    for span in spans or []:
        quote, origin = span.get("text"), span.get("origin")
        if not isinstance(quote, str) or not quote or origin not in ORIGINS:
            raise ValueError("切片必须含逐字 text 与合法 origin")
        start = span.get("start")
        if start is None:
            start = text.find(quote)
            if start >= 0 and text.find(quote, start + 1) >= 0:
                raise ValueError("重复子串需要明确 start 字符偏移")
        if type(start) is not int or start < 0 or text[start:start + len(quote)] != quote:
            raise ValueError("切片不是原话逐字子串")
        item = {"utf8_start_byte": len(text[:start].encode("utf-8")),
                "utf8_end_byte_exclusive": len(text[:start + len(quote)].encode("utf-8")),
                "text_sha256": _sha(quote.encode("utf-8")), "origin": origin}
        if span.get("source_ref") is not None:
            if not isinstance(span["source_ref"], str):
                raise ValueError("source_ref 必须是字符串；它是待核查引用，不证明材料事实")
            item["source_ref"] = span["source_ref"]
        result.append(item)
    result.sort(key=lambda item: item["utf8_start_byte"])
    if any(a["utf8_end_byte_exclusive"] > b["utf8_start_byte"] for a, b in zip(result, result[1:])):
        raise ValueError("切片不能重叠")
    return result


def set_attribution(root: Path, event_id: str, origin: str, reason: str, spans=None, course=None, lesson=None, manual=False) -> dict:
    """Append a review, never an authenticated authorship or mastery receipt.

    spans = [{text, origin, start?: character_offset, source_ref?: str}].
    Stored spans contain only byte offsets/hashes, not a second verbatim ledger.
    """
    if origin not in ORIGINS or not isinstance(reason, str) or not reason.strip():
        raise ValueError("必须提供合法 origin 与明确 reason")
    root = Path(root).resolve()
    with _locked(root):
        record = _lookup(root, event_id)
        previous = _review(root, record)
        slices = _spans(record, spans) if spans is not None else (previous or {}).get('spans', [])
        restricted_history = any(row.get("record_id") == record["record_id"]
                                 and row.get("origin") in {"mixed", "material"}
                                 for row in _rows(root / REVIEWS))
        if not manual and origin == "user" and (any(span["origin"] != "user" for span in slices)
                                  or restricted_history):
            raise ValueError("混合或材料记录不能整体升级为 user；需另走可信归属核验")
        if origin == "material" and any(span["origin"] == "user" for span in slices):
            raise ValueError("含用户语义候选的切片须标为 mixed")
        payload = {"schema_version": "workbench-attribution-review/v1",
                   "record_id": record["record_id"], "event_id": record["event_id"],
                   "verbatim_sha256": record["verbatim_sha256"],
                   "source_sha256": record["source_sha256"],
                   "origin": origin, "reason": reason, "spans": slices,
                   "course": course if course is not None else (previous or {}).get('course', record.get('course')),
                   "lesson": lesson if lesson is not None else (previous or {}).get('lesson', record.get('lesson')),
                   "manually_reviewed": manual,
                   "status": "pending_gateway_verification", "automatic_upgrade_allowed": False}
        review = {**payload, "review_id": "wbr_" + _sha(_json(payload).encode("utf-8"))}
        if previous != review:
            _append(root / REVIEWS, review)
        _persist_atom(root, to_atom(record, root))
        return _decorate(root, record)


def get_record(root: Path, event_id: str) -> dict:
    root = Path(root).resolve()
    with _locked(root):
        return _decorate(root, _lookup(root, event_id))


def to_atom(record: dict, root: Path) -> dict:
    """Builder integration: dispatch workbench schema here before legacy handling."""
    _validate_record(record)
    review = _review(Path(root), record)
    return {
        "schema_version": "evidence-atom/v1",
        "evidence_id": "ev_" + record["record_id"].removeprefix("utt_") + "_r1",
        "text": record["verbatim"], "version": 1, "status": "workbench_pending_attribution",
        "record": {"parent_record_id": record["record_id"], "atom_index": 1,
                   "record_level": True, "requires_semantic_split": (review or {}).get("origin") == "mixed"},
        "identity": {"surface_author": "user", "semantic_origin": "unknown",
                     "origin_labels": ["工作台逐字记录", "语义归属待核验"]},
        "form": {"text_form": "verbatim_unattributed_learning_record", "exactness": "exact", "speech_act": []},
        "confirmation": {"status": "pending_attribution_review", "scope": "none",
                         "confirmed_by": None, "confirmation_evidence_id": None},
        "verification": {"required": True, "status": "source_matched", "claim_status": "pending_attribution_review", "material_source_ids": []},
        "voice_policy": {"first_person": "forbidden", "reason": "来源角色与人工归属标记不构成可信语义归属合同"},
        "eligibility": {"as_verbatim_quote": False, "as_user_claim": False, "as_material_fact": False,
                        "reason": "仅供逐字回溯与归属复核"},
        "source": {"source_sha256": record["source_sha256"], "source_relative_path": record["source_relative_path"],
                   "canonical_relative_path": None, "legacy_source_path": record["source_path"],
                   "snapshot_path": record.get("source_snapshot_path"), "resolution": "workbench_sha256_match",
                   "locator": record["locator"]},
        "lineage": {"parent_evidence_ids": [], "transformation": "record_exact_copy"},
        "learning": {"course": (review or {}).get("course", record.get("course")), "course_id": None,
                     "lesson": (review or {}).get("lesson", record.get("lesson")),
                     "response_kind": "workbench_capture", "is_feynman_evidence": False,
                     "strict_mastery_evidence_allowed": False, "settlement_status": "pending_attribution_review"},
        "downstream_policy": {"eligible_for_content_asset": False, "use_mode": "attribution_review_only", "agent_summary_may_replace_text": False},
        "attribution_review": review or {"status": "unreviewed", "automatic_upgrade_allowed": False},
    }


def _persist_atom(root: Path, atom: dict) -> None:
    """Update only our derived atom; preserve every unrelated line byte-for-byte."""
    path = root / ATOMS
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = path.read_bytes().splitlines(keepends=True) if path.exists() else []
    replacement = (_json(atom) + "\n").encode("utf-8")
    output, found = [], False
    for line in lines:
        if line.strip() and json.loads(line).get("evidence_id") == atom["evidence_id"]:
            if found:
                raise ValueError("证据 ID 重复")
            output.append(replacement)
            found = True
        else:
            output.append(line)
    if not found:
        if output and not output[-1].endswith(b"\n"):
            output[-1] += b"\n"
        output.append(replacement)
    data = b"".join(output)
    old_data = path.read_bytes() if path.exists() else None
    if old_data == data:
        return
    if old_data is not None:
        trash = root / ".trash"
        trash.mkdir(parents=True, exist_ok=True)
        backup = trash / f"{datetime.now().date().isoformat()}_{path.name}_{_sha(old_data)}"
        try:
            with backup.open("xb") as handle:
                handle.write(old_data)
                handle.flush()
                os.fsync(handle.fileno())
        except FileExistsError:
            if backup.read_bytes() != old_data:
                raise ValueError("证据替换备份发生内容冲突")
    fd, temporary = tempfile.mkstemp(prefix=".workbench-atoms-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
