#!/usr/bin/env python3
"""Build an evidence-first lexical profile from extracted Chinese transcripts."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import jieba
import jieba.analyse
import jieba.posseg


ORAL_MARKERS = (
    "能理解吗",
    "大家能理解",
    "你们记住",
    "我想告诉",
    "我跟你讲",
    "兄弟们",
    "各位",
    "就这么简单",
    "说白了",
    "其实",
    "对吧",
    "我认为",
    "记住",
    "懂吗",
    "明白吗",
    "我觉得",
    "我希望",
    "你看",
    "所以说",
    "假设",
    "如果我是",
    "拿到结果",
    "客观",
    "真实",
    "认账",
    "买单",
    "无限进化",
    "向善而行",
    "气运加一",
    "气运+1",
    "气运＋1",
)

STOPWORDS = {
    "的", "了", "和", "是", "我", "你", "他", "她", "它", "我们", "你们", "他们",
    "这个", "那个", "这些", "那些", "一个", "一种", "一些", "一下", "然后", "就是",
    "因为", "所以", "但是", "如果", "还是", "不是", "没有", "有", "在", "到", "把",
    "被", "让", "给", "对", "跟", "跟着", "而", "而且", "就", "也", "都", "还",
    "很", "更", "最", "非常", "特别", "可能", "可以", "应该", "能够", "觉得", "认为",
    "说", "讲", "问", "看", "想", "知道", "明白", "理解", "怎么", "为什么", "什么",
    "这样", "那样", "这里", "那里", "现在", "今天", "时候", "事情", "东西", "问题",
    "大家", "各位", "啊", "呀", "吗", "吧", "呢", "嘛", "哎", "嗯", "呃", "哦",
    "又", "再", "已经", "一直", "其实", "反正", "这种", "那么", "这么", "多少", "里面",
}


def body_from_markdown(text: str) -> str:
    lines = text.splitlines()
    try:
        divider = lines.index("---")
    except ValueError:
        return text
    return "\n".join(lines[divider + 1 :]).strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def usable_token(word: str, flag: str) -> bool:
    word = word.strip()
    if len(word) < 2 or word in STOPWORDS:
        return False
    if flag in {"x", "uj", "ul", "e", "y", "o", "w", "m", "r", "p", "c", "d", "f"}:
        return False
    if re.fullmatch(r"[\W_]+", word):
        return False
    return bool(re.search(r"[\u4e00-\u9fffA-Za-z]", word))


def top_records(counts: collections.Counter, doc_counts: collections.Counter, limit: int) -> list[dict]:
    return [
        {"term": term, "count": count, "document_count": doc_counts[term]}
        for term, count in counts.most_common(limit)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    raw_dir = args.raw_dir.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    paths = sorted(raw_dir.glob("*.md"), key=lambda p: p.name)
    if not paths:
        raise SystemExit("no Markdown transcripts found")

    token_counts: collections.Counter = collections.Counter()
    token_docs: collections.Counter = collections.Counter()
    proper_counts: collections.Counter = collections.Counter()
    proper_docs: collections.Counter = collections.Counter()
    bigram_counts: collections.Counter = collections.Counter()
    bigram_docs: collections.Counter = collections.Counter()
    marker_counts: collections.Counter = collections.Counter()
    marker_docs: collections.Counter = collections.Counter()
    document_stats: list[dict] = []
    bodies: list[str] = []

    for path in paths:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        body = body_from_markdown(text)
        bodies.append(body)
        tagged = [(pair.word.strip(), pair.flag) for pair in jieba.posseg.cut(body)]
        selected = [(word, flag) for word, flag in tagged if usable_token(word, flag)]
        words = [word for word, _ in selected]
        unique = set(words)
        token_counts.update(words)
        token_docs.update(unique)

        proper = [word for word, flag in selected if flag.startswith(("nr", "nt", "nz")) or flag == "eng"]
        proper_counts.update(proper)
        proper_docs.update(set(proper))

        doc_bigrams = set()
        for left, right in zip(words, words[1:]):
            if left in STOPWORDS or right in STOPWORDS:
                continue
            phrase = f"{left} {right}"
            bigram_counts[phrase] += 1
            doc_bigrams.add(phrase)
        bigram_docs.update(doc_bigrams)

        for marker in ORAL_MARKERS:
            count = body.count(marker)
            if count:
                marker_counts[marker] += count
                marker_docs[marker] += 1

        clauses = [item.strip() for item in re.split(r"[。！？!?；;\n]+", body) if item.strip()]
        clause_lengths = [len(re.sub(r"\s+", "", item)) for item in clauses]
        document_stats.append(
            {
                "file": path.name,
                "body_characters": len(body),
                "body_sha256": sha256_text(body),
                "clauses": len(clauses),
                "average_clause_characters": round(sum(clause_lengths) / len(clause_lengths), 2) if clause_lengths else 0,
                "first_person_count": body.count("我"),
                "second_person_count": body.count("你"),
                "replacement_character_count": body.count("\ufffd"),
            }
        )

    all_text = "\n".join(bodies)
    tfidf = [
        {"term": term, "weight": round(weight, 8)}
        for term, weight in jieba.analyse.extract_tags(all_text, topK=300, withWeight=True)
        if term not in STOPWORDS and len(term.strip()) >= 2
    ]
    text_rank = [
        {"term": term, "weight": round(weight, 8)}
        for term, weight in jieba.analyse.textrank(all_text, topK=300, withWeight=True)
        if term not in STOPWORDS and len(term.strip()) >= 2
    ]

    common_bigrams = [
        {"term": term, "count": count, "document_count": bigram_docs[term]}
        for term, count in bigram_counts.most_common()
        if count >= 4 and bigram_docs[term] >= 2
    ][:300]

    result = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": {
            "jieba_version": getattr(jieba, "__version__", "UNKNOWN"),
            "method": "jieba POS + frequency + TF-IDF + TextRank + token bigrams",
            "speaker_attribution": "UNRESOLVED; corpus-level statistics may include guests and quoted speech",
        },
        "document_count": len(paths),
        "body_characters": len(all_text),
        "documents": document_stats,
        "oral_markers": top_records(marker_counts, marker_docs, len(marker_counts)),
        "frequent_tokens": top_records(token_counts, token_docs, 500),
        "proper_noun_candidates": top_records(proper_counts, proper_docs, 500),
        "token_bigrams": common_bigrams,
        "tfidf": tfidf,
        "textrank": text_rank,
    }
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"document_count": len(paths), "body_characters": len(all_text), "output": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
