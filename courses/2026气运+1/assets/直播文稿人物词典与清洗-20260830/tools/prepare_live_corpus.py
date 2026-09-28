#!/usr/bin/env python3
"""Safely extract Markdown transcripts from the frozen source ZIP.

The archive was created on a platform that stored UTF-8 filenames through a
CP437-compatible ZIP field. This script recovers those names, rejects path
traversal, preserves file bytes, and writes a reproducible manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def recover_name(name: str) -> str:
    try:
        return name.encode("cp437").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def safe_basename(name: str) -> str:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe archive path: {name!r}")
    base = path.name.strip()
    if not base:
        raise ValueError(f"empty archive filename: {name!r}")
    return re.sub(r"[\x00-\x1f/]", "_", base)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    archive = args.zip.resolve()
    output = args.output.resolve()
    raw_dir = output / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    archive_bytes = archive.read_bytes()
    records: list[dict] = []
    used: dict[str, int] = {}

    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            decoded = recover_name(info.filename)
            if info.is_dir() or "__MACOSX" in PurePosixPath(decoded).parts:
                continue
            if PurePosixPath(decoded).suffix.lower() != ".md":
                continue

            base = safe_basename(decoded)
            count = used.get(base, 0)
            used[base] = count + 1
            if count:
                stem = Path(base).stem
                base = f"{stem}__dup{count + 1}.md"

            data = zf.read(info)
            target = raw_dir / base
            target.write_bytes(data)
            text = data.decode("utf-8-sig", errors="replace")
            records.append(
                {
                    "archive_path": decoded,
                    "output_path": f"raw/{base}",
                    "bytes": len(data),
                    "lines": len(text.splitlines()),
                    "sha256": sha256(data),
                    "decode_replacement_count": text.count("\ufffd"),
                }
            )

    records.sort(key=lambda item: item["output_path"])
    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_archive": str(archive),
        "source_archive_sha256": sha256(archive_bytes),
        "document_count": len(records),
        "total_bytes": sum(item["bytes"] for item in records),
        "documents": records,
    }
    (output / "source-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    summary = {k: manifest[k] for k in ("source_archive_sha256", "document_count", "total_bytes")}
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if records else 2


if __name__ == "__main__":
    raise SystemExit(main())
