#!/usr/bin/env python3
"""用 Jev（TypeSafe System One）给课程正文打「可复用度」标签。

用途：把过去的交互式学习资产变成可检索的素材索引——哪些篇目已经成型、
可以直接进 content-system 做排列组合，哪些还需要重构。

边界：
- 只读课程正文，不改任何课程文件。
- 输出是模型建议，不是事实判断；发布前仍须人工抽核。
- 密钥从 ~/.dsh-secrets/jev.env 或环境变量读取。

用法：
  python3 jev_label_lessons.py --root <真源根> --out <输出目录> [--limit N] [--sample N]
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

ENV_FILE = Path.home() / '.dsh-secrets/jev.env'
LESSON_RE = re.compile(r'^\d+(?:\.\d+)?\.md$')

QUESTIONS = {
    'standalone': {
        'type': 'noul',
        'instructions': '这篇里有没有至少一句脱离原文也能单独成立、可被别人引用的判断？',
        'criteria': {'true': '有可独立引用的判断句', 'false': '只是叙述或复述'},
    },
    'shape': {
        'type': 'choice',
        'instructions': '这篇最适合怎么被复用？',
        'criteria': {
            '直接组合': '判断句与结构已经成型，可与别的篇目拼装成新内容',
            '需重构': '有料但结构不适合直接搬，需要重写',
            '只适合存档': '主要价值是记录，不构成可发布的内容素材',
        },
    },
}


def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())
    key = os.environ.get('JEV_API_KEY', '')
    if not key:
        raise SystemExit('缺少 JEV_API_KEY：请先运行 ~/.dsh-secrets/设置Jev密钥.command')
    return key, os.environ.get('JEV_BASE_URL', 'https://api.typesafe.ai'), os.environ.get('JEV_MODEL', 'jev-latest')


def lessons(root: Path):
    rows = []
    for path in sorted(root.glob('*/*.md')):
        if LESSON_RE.fullmatch(path.name):
            rows.append({'course': path.parent.name, 'file': path.name, 'path': path,
                         'chars': len(re.sub(r'\s+', '', path.read_text(encoding='utf-8', errors='replace')))})
    return rows


def ask(key, base, model, text, timeout=60):
    body = {'state': text[:6000], 'model': model, 'questions': QUESTIONS}
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
    parser.add_argument('--sample', type=int, default=0, help='每隔 N 篇取一篇做抽样')
    args = parser.parse_args()
    root, out = Path(args.root).resolve(), Path(args.out).resolve()
    rows = lessons(root)
    if args.sample:
        rows = rows[::args.sample]
    if args.limit:
        rows = rows[:args.limit]
    print(f'课程正文 {len(rows)} 篇')

    key, base, model = load_env()
    results, failures, tokens = [], [], 0
    started = time.time()
    for index, row in enumerate(rows, 1):
        try:
            payload = ask(key, base, model, row['path'].read_text(encoding='utf-8', errors='replace'))
            answers = payload['answers']
            tokens += payload.get('usage', {}).get('input_tokens', 0)
            results.append({'course': row['course'], 'file': row['file'], 'chars': row['chars'],
                            'shape': answers['shape']['choice'],
                            'shape_confidence': answers['shape'].get('confidence'),
                            'standalone': answers['standalone']['noul'],
                            'model': payload.get('model')})
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, TimeoutError) as exc:
            failures.append({'course': row['course'], 'file': row['file'], 'error': str(exc)[:160]})
        if index % 25 == 0:
            print(f'  已完成 {index}/{len(rows)}，用时 {time.time()-started:.0f}s')

    stamp = dt.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'lessons-reuse-results.json').write_text(json.dumps(
        {'generated_at': stamp, 'model': results[0]['model'] if results else '',
         'input_tokens': tokens, 'results': results, 'failures': failures}, ensure_ascii=False, indent=1))

    shapes = collections.Counter(r['shape'] for r in results)
    by_course = collections.Counter(r['course'] for r in results if r['shape'] == '直接组合')
    lines = ['# 课程正文可复用度｜Jev 打标', '',
             f'- 生成时间：{stamp}', f'- 模型：{results[0]["model"] if results else "—"}',
             f'- 样本：{len(results)} 篇（失败 {len(failures)} 篇）',
             f'- input tokens：{tokens}（按 $0.042/1M 计约 ${tokens/1e6*0.042:.4f}）',
             '- 性质：模型建议，不是事实判断；进 content-system 前须人工抽核。', '',
             '## 形态分布', '']
    for name, count in shapes.most_common():
        lines.append(f'- {name}：{count} 篇')
    lines += ['', f'- 有可独立引用判断的篇数：{sum(1 for r in results if r["standalone"] >= 0.5)}/{len(results)}', '',
              '## 判为「直接组合」的篇目（按课程）', '']
    for course, count in by_course.most_common():
        lines.append(f'- {course}：{count} 篇')
    lines += ['', '## 逐篇明细', '', '| 课程 | 篇 | 字数 | 形态 | 置信度 | 可独立引用 |',
              '|---|---|---:|---|---:|---:|']
    for r in sorted(results, key=lambda x: (-(x['shape_confidence'] or 0))):
        lines.append('| {course} | {file} | {chars} | {shape} | {conf:.2f} | {stand:.2f} |'.format(
            conf=r['shape_confidence'] or 0, stand=r['standalone'], **r))
    (out / 'lessons-reuse-report.md').write_text('\n'.join(lines) + '\n')
    print('形态分布:', dict(shapes))
    print(f'写出 {out}/lessons-reuse-report.md')


if __name__ == '__main__':
    main()
