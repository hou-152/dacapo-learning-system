#!/usr/bin/env python3
"""Batch wrapper around HaujetZhao/asr-hotword with a full audit ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def split_metadata(text: str) -> tuple[str, str]:
    """Keep the document heading/source block byte-for-byte stable."""
    divider = "\n---\n"
    if divider not in text:
        return "", text
    heading, body = text.split(divider, 1)
    return heading + divider, body


def correct_preserving_lines(corrector, body: str):
    """Correct each line independently so paragraph boundaries cannot collapse."""
    corrected_parts: list[str] = []
    matches: list[tuple[str, str, float]] = []
    similars: list[tuple[str, str, float]] = []
    for line in body.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        ending = line[len(content) :]
        result = corrector.correct(content, k=100, blacklist_window=5)
        corrected_parts.append(result.text + ending)
        matches.extend(result.matches)
        similars.extend(result.similars)
    return "".join(corrected_parts), matches, similars


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine-dir", required=True, type=Path)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--hotwords", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--threshold", type=float, default=0.97)
    parser.add_argument("--similar-threshold", type=float, default=0.90)
    parser.add_argument("--include", action="append", default=[])
    args = parser.parse_args()

    sys.path.insert(0, str(args.engine_dir.resolve()))
    from hotword import PhonemeCorrector  # pylint: disable=import-error,import-outside-toplevel

    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    ledger_path = args.ledger.resolve()
    manifest_path = args.manifest.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    corrector = PhonemeCorrector(
        threshold=args.threshold,
        similar_threshold=args.similar_threshold,
    )
    hotword_text = args.hotwords.read_text(encoding="utf-8")
    hotword_count = corrector.update_hotwords(hotword_text)

    include = set(args.include)
    paths = sorted(input_dir.glob("*.md"), key=lambda path: path.name)
    if include:
        paths = [path for path in paths if path.name in include]
    if not paths:
        raise SystemExit("no input files selected")

    file_records = []
    ledger_records = []
    for path in paths:
        input_bytes = path.read_bytes()
        text = input_bytes.decode("utf-8-sig", errors="strict")
        metadata, body = split_metadata(text)
        corrected_body, matches, similars = correct_preserving_lines(corrector, body)
        output_text = metadata + corrected_body
        output_bytes = output_text.encode("utf-8")
        target = output_dir / path.name
        target.write_bytes(output_bytes)

        for wrong, right, score in matches:
            ledger_records.append(
                {
                    "kind": "match",
                    "file": path.name,
                    "source": wrong,
                    "target": right,
                    "score": round(score, 8),
                }
            )
        for source, target_word, score in similars:
            if (source, target_word, score) in matches:
                continue
            ledger_records.append(
                {
                    "kind": "similar_only",
                    "file": path.name,
                    "source": source,
                    "target": target_word,
                    "score": round(score, 8),
                }
            )

        file_records.append(
            {
                "file": path.name,
                "input_bytes": len(input_bytes),
                "output_bytes": len(output_bytes),
                "input_sha256": sha256(input_bytes),
                "output_sha256": sha256(output_bytes),
                "metadata_preserved": output_text.startswith(metadata),
                "match_count": len(matches),
                "similar_only_count": sum(1 for item in ledger_records if item["file"] == path.name and item["kind"] == "similar_only"),
            }
        )

    with ledger_path.open("w", encoding="utf-8") as handle:
        for record in ledger_records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": "HaujetZhao/asr-hotword",
        "engine_commit": "7e282137e780ac4096cac537bef360235d2efe43",
        "threshold": args.threshold,
        "similar_threshold": args.similar_threshold,
        "hotword_count": hotword_count,
        "hotwords_sha256": sha256(hotword_text.encode("utf-8")),
        "processing_scope": "body_after_first_markdown_divider_line_by_line",
        "file_count": len(file_records),
        "total_matches": sum(item["match_count"] for item in file_records),
        "files": file_records,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file_count": manifest["file_count"], "total_matches": manifest["total_matches"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
