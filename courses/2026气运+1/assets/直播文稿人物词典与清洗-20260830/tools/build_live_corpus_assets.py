#!/usr/bin/env python3
"""Build a Typeless-like dictionary export and a corpus candidate lexicon."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def parse_hotwords(path: Path) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rule, _, blacklist = line.partition("~~~")
        parts = [part.strip() for part in rule.split("|") if part.strip()]
        if not parts:
            continue
        records.append(
            {
                "term": parts[0],
                "replace_targets": parts[1:],
                "blacklist": [item.strip() for item in blacklist.split("|") if item.strip()],
            }
        )
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--hotwords", required=True, type=Path)
    parser.add_argument("--dictionary-json", required=True, type=Path)
    parser.add_argument("--candidate-csv", required=True, type=Path)
    args = parser.parse_args()

    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    hotwords = parse_hotwords(args.hotwords)
    hotword_terms = {record["term"] for record in hotwords}
    exported_at = datetime.now(timezone.utc).isoformat()

    records = []
    for index, item in enumerate(hotwords, start=1):
        records.append(
            {
                "user_dictionary_id": f"corpus-approved-{index:03d}",
                "term": item["term"],
                "replace": bool(item["replace_targets"]),
                "replace_targets": item["replace_targets"],
                "category": "approved_correction",
                "lang": "zh-CN",
                "auto": False,
                "created_at": exported_at,
                "updated_at": exported_at,
                "blacklist": item["blacklist"],
            }
        )

    expression_terms = [item["term"] for item in profile["oral_markers"]]
    concept_terms = [
        "拿到结果", "气运流转", "气运叠加", "改变世界", "创造价值", "人生攻略",
        "狩猎范围", "互为贵人", "不让好人失望", "向善而行", "认账", "买单",
        "求真", "客观", "真实", "人生复利", "小世界", "原生家庭",
    ]
    seen = hotword_terms.copy()
    for category, terms in (("corpus_expression_candidate", expression_terms), ("concept_candidate", concept_terms)):
        for term in terms:
            if term in seen:
                continue
            seen.add(term)
            records.append(
                {
                    "user_dictionary_id": f"corpus-candidate-{len(records)+1:03d}",
                    "term": term,
                    "replace": False,
                    "replace_targets": [],
                    "category": category,
                    "lang": "zh-CN",
                    "auto": True,
                    "created_at": exported_at,
                    "updated_at": exported_at,
                    "blacklist": [],
                }
            )

    dictionary = {
        "schema_version": "typeless-like-corpus-dictionary/v1",
        "compatibility": "Typeless-inspired local interchange; not claimed as an official Typeless import schema",
        "source": "32 local livestream transcripts; corpus-level candidates include multiple speakers",
        "speaker_attribution": "UNRESOLVED",
        "exported_at": exported_at,
        "exported_count": len(records),
        "total_count": len(records),
        "records": records,
    }
    args.dictionary_json.parent.mkdir(parents=True, exist_ok=True)
    args.dictionary_json.write_text(json.dumps(dictionary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    frequency = {item["term"]: item for item in profile["frequent_tokens"]}
    marker = {item["term"]: item for item in profile["oral_markers"]}
    bigram = {re.sub(r"\s+", "", item["term"]): item for item in profile["token_bigrams"]}
    rows = []
    for term, item in marker.items():
        rows.append((term, "oral_marker", item["count"], item["document_count"], "corpus_candidate"))
    for term, item in frequency.items():
        rows.append((term, "frequent_token", item["count"], item["document_count"], "corpus_candidate"))
    for term, item in bigram.items():
        rows.append((term, "collocation", item["count"], item["document_count"], "corpus_candidate"))
    for item in hotwords:
        counts = marker.get(item["term"]) or frequency.get(item["term"]) or bigram.get(item["term"], {})
        rows.append((item["term"], "approved_hotword", counts.get("count", ""), counts.get("document_count", ""), "approved"))
    rows = sorted(set(rows), key=lambda row: (row[1], -(row[2] if isinstance(row[2], int) else -1), row[0]))

    args.candidate_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.candidate_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["term", "category", "count", "document_count", "status", "attribution"])
        for row in rows:
            writer.writerow([*row, "corpus_level_not_single_speaker"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
