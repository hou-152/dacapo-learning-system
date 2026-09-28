#!/usr/bin/env python3
"""用 Jev（TypeSafe System One）给课程反馈区里的用户手写反馈打标。

用途：把散在课程正文「## 学习反馈」区、从未进入工作台账本的历史反馈，
批量转成带置信度的结构化标签，供人工核对。对应疑问卡 W-0922-1 的实测设计。

边界：
- 只读课程 Markdown，不改任何课程文件。
- Jev 的输出是「模型建议」，不是用户事实，也不构成掌握认证。
- 密钥从 ~/.dsh-secrets/jev.env 或环境变量读取，不写入本仓库。

用法：
  python3 jev_label_feedback.py --root <真源根> --out <报告目录> [--limit N] [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

ENV_FILE = Path.home() / '.dsh-secrets/jev.env'
TEMPLATE_MARKERS = ('你可以写', '哪里看懂了', '请写在这行下面', '哪里没看懂',
                    '哪个地方想展开', '这个主题和你的真实问题有什么关系')

# 助手在工作台里写下的说明性文字，不属于用户反馈
ASSISTANT_ECHO = ('工作台会自动收集', '直接在原来的聊天中反馈即可', '用一条具体反馈演示整个过程')

QUESTIONS = {
    'label': {
        'type': 'choice',
        'instructions': '这条学习反馈主要在做什么？按主要动作选一个。',
        'criteria': {
            '复述': '把材料里的话换个说法讲一遍，或总结对方说了什么',
            '举例': '给出自己的新例子、经历或演示一次',
            '边界': '说出条件、反例、什么情况下不成立',
            '迁移': '把它用到一个没见过的新情境里做判断，或接上自己的工作流',
            '疑问': '提出问题、指出没看懂、或明确要反驳的地方',
        },
    },
    'is_course_feedback': {
        'type': 'noul',
        'instructions': '这条是否在讨论课程里的理解、疑问或应用，而不是软件配置、流程安排或工具说明？',
        'criteria': {'true': '在讨论课程内容本身', 'false': '配置、流程或工具说明'},
    },
    'has_next_action': {
        'type': 'noul',
        'instructions': '这条里是否写明了下一步要做的具体动作？',
    },
}


def load_env():
    if ENV_FILE.exists():
        pairs = (line.split('=', 1) for line in ENV_FILE.read_text().splitlines() if '=' in line)
        for key, value in pairs:
            os.environ.setdefault(key.strip(), value.strip())
    key = os.environ.get('JEV_API_KEY', '')
    if not key:
        raise SystemExit('缺少 JEV_API_KEY：请先运行 ~/.dsh-secrets/设置Jev密钥.command')
    return key, os.environ.get('JEV_BASE_URL', 'https://api.typesafe.ai'), os.environ.get('JEV_MODEL', 'jev-latest')


def harvest(root: Path):
    """抽出反馈区里用户手写的正文。"""
    rows = []
    for path in sorted(root.glob('*/*.md')):
        text = path.read_text(encoding='utf-8', errors='replace')
        if '## 学习反馈' not in text:
            continue
        block = text.split('## 学习反馈', 1)[1]
        parts = re.split(r'请写在这行下面[：:]?\s*\n', block)
        body = (parts[1] if len(parts) > 1 else block).split('<!--')[0]
        lines = [line.strip() for line in body.splitlines()]
        lines = [line for line in lines if line and not any(m in line for m in TEMPLATE_MARKERS)]
        body = '\n'.join(lines).strip()
        if len(body) < 20:
            continue
        rows.append({'course': path.parent.name, 'file': path.name, 'text': body,
                     'chars': len(body), 'suspect_assistant': any(a in body for a in ASSISTANT_ECHO)})
    return rows


def ask(key, base, model, state, timeout=60):
    body = {'state': state[:6000], 'model': model, 'questions': QUESTIONS}
    request = urllib.request.Request(base.rstrip('/') + '/v1/systemone',
                                     data=json.dumps(body).encode(),
                                     headers={'Authorization': 'Bearer ' + key,
                                              'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    root, out = Path(args.root).resolve(), Path(args.out).resolve()
    rows = harvest(root)
    if args.limit:
        rows = rows[:args.limit]
    print(f'抽出反馈 {len(rows)} 条，可疑助手文本 {sum(r["suspect_assistant"] for r in rows)} 条')
    if args.dry_run:
        for row in rows[:10]:
            print(f'  {row["course"]}/{row["file"]}  {row["chars"]} 字  {row["text"][:50]!r}')
        return

    key, base, model = load_env()
    results, failures, tokens = [], [], 0
    started = time.time()
    for index, row in enumerate(rows, 1):
        begin = time.time()
        try:
            payload = ask(key, base, model, row['text'])
            answers = payload['answers']
            tokens += payload.get('usage', {}).get('input_tokens', 0)
            results.append({
                **{k: row[k] for k in ('course', 'file', 'chars', 'suspect_assistant')},
                'text': row['text'],
                'label': answers['label']['choice'],
                'label_confidence': answers['label'].get('confidence'),
                'label_probabilities': answers['label'].get('probabilities'),
                'is_course_feedback': answers['is_course_feedback']['noul'],
                'has_next_action': answers['has_next_action']['noul'],
                'elapsed': round(time.time() - begin, 2),
                'model': payload.get('model'),
            })
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, TimeoutError) as exc:
            failures.append({'course': row['course'], 'file': row['file'], 'error': str(exc)[:200]})
        if index % 10 == 0:
            print(f'  已完成 {index}/{len(rows)}，用时 {time.time()-started:.0f}s')

    stamp = dt.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / 'jev-label-results.json'
    json_path.write_text(json.dumps({'generated_at': stamp, 'model': results[0]['model'] if results else '',
                                     'input_tokens': tokens, 'results': results,
                                     'failures': failures}, ensure_ascii=False, indent=1))

    lines = [f'# Jev 打标结果｜历史课程反馈', '',
             f'- 生成时间：{stamp}', f'- 模型：{results[0]["model"] if results else "—"}',
             f'- 样本：{len(results)} 条（失败 {len(failures)} 条）',
             f'- input tokens 合计：{tokens}（按 $0.042/1M 计约 ${tokens/1e6*0.042:.5f}）',
             '- 性质：模型建议，不是用户事实，也不构成掌握认证；须人工核对。', '',
             '| 课程 | 篇 | 字数 | Jev 判定 | 置信度 | 是课程反馈 | 有下一步 | 原文开头 |',
             '|---|---|---:|---|---:|---:|---:|---|']
    for row in results:
        head = row['text'][:40].replace('|', '／').replace('\n', ' ')
        lines.append('| {course} | {file} | {chars} | {label} | {conf:.2f} | {fb:.2f} | {nx:.2f} | {head} |'.format(
            conf=row['label_confidence'] or 0, fb=row['is_course_feedback'],
            nx=row['has_next_action'], head=head, **row))
    if failures:
        lines += ['', '## 失败', ''] + [f'- {f["course"]}/{f["file"]}：{f["error"]}"' for f in failures]
    md_path = out / 'jev-label-report.md'
    md_path.write_text('\n'.join(lines) + '\n')

    import collections
    print('标签分布:', dict(collections.Counter(r['label'] for r in results)))
    print('平均置信度: %.2f' % (sum(r['label_confidence'] or 0 for r in results) / max(1, len(results))))
    print(f'写出 {json_path}')
    print(f'写出 {md_path}')


if __name__ == '__main__':
    main()
