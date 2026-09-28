#!/usr/bin/env python3
"""Verify one-to-one transcript cleaning without source overwrite or line loss."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def metadata(text: str) -> str:
    divider = "\n---\n"
    return text.partition(divider)[0] + (divider if divider in text else "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", required=True, type=Path)
    parser.add_argument("--clean-dir", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    raw_paths = sorted(args.raw_dir.glob("*.md"), key=lambda path: path.name)
    clean_paths = sorted(args.clean_dir.glob("*.md"), key=lambda path: path.name)
    raw_names = [path.name for path in raw_paths]
    clean_names = [path.name for path in clean_paths]
    if raw_names != clean_names:
        raise SystemExit("raw/clean filename sets differ")

    records = []
    for raw_path, clean_path in zip(raw_paths, clean_paths):
        raw_bytes = raw_path.read_bytes()
        clean_bytes = clean_path.read_bytes()
        raw_text = raw_bytes.decode("utf-8-sig")
        clean_text = clean_bytes.decode("utf-8-sig")
        records.append(
            {
                "file": raw_path.name,
                "raw_sha256": sha256(raw_bytes),
                "clean_sha256": sha256(clean_bytes),
                "raw_bytes": len(raw_bytes),
                "clean_bytes": len(clean_bytes),
                "raw_lines": len(raw_text.splitlines()),
                "clean_lines": len(clean_text.splitlines()),
                "line_count_preserved": len(raw_text.splitlines()) == len(clean_text.splitlines()),
                "metadata_preserved": metadata(raw_text) == metadata(clean_text),
                "replacement_character_preserved": raw_text.count("�") == clean_text.count("�"),
                "changed": raw_bytes != clean_bytes,
            }
        )

    ledger = [json.loads(line) for line in args.ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    match_types = Counter((row["source"], row["target"]) for row in ledger if row["kind"] == "match")
    result = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "file_count": len(records),
        "filename_bijection": raw_names == clean_names,
        "all_line_counts_preserved": all(row["line_count_preserved"] for row in records),
        "all_metadata_preserved": all(row["metadata_preserved"] for row in records),
        "all_replacement_character_counts_preserved": all(row["replacement_character_preserved"] for row in records),
        "changed_file_count": sum(row["changed"] for row in records),
        "match_event_count": sum(count for count in match_types.values()),
        "match_type_count": len(match_types),
        "match_types": [
            {"source": source, "target": target, "count": count}
            for (source, target), count in match_types.most_common()
        ],
        "files": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "file_count", "filename_bijection", "all_line_counts_preserved", "all_metadata_preserved",
        "changed_file_count", "match_event_count", "match_type_count",
    )}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
