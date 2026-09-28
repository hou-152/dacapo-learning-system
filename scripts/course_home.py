#!/usr/bin/env python3
"""生成课程主页：把一课的进度、未结疑问、相关研究、相关概念、产出聚到一页。

课程主页是入口，不是真源。数字和清单都从各层真源机械汇总，改数据请改对应的
真源文件，不要手改主页。

为什么要有主页：学习画布只画「课程正文 / 反馈 / 疑问 / 候选」四类文件，研究和
概念两层在画布上完全不可见。主页把这两层一并聚进来，让一课的上下文有一个入口。

用法：
    python3 course_home.py --course 个人学习工作台实践
    python3 course_home.py --all
    python3 course_home.py --all --check     # 只报告差异，不写入
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys

DEFAULT_ROOT = '/Users/housibo/Documents/DaCapo 内容资产/01-交互式学习'
COURSE_RE = re.compile(r'\d{2}\.md$')
CLOSED = ('已解决', '已撤回')
HOME = '主页.md'


def read(path):
    with open(path, encoding='utf-8') as handle:
        return handle.read()


def section(text, title):
    m = re.search(r'^##\s+' + re.escape(title) + r'\s*$\n(.*?)(?=^##\s|\Z)', text, re.S | re.M)
    return m.group(1).strip() if m else ''


def latest_update(course_dir):
    stamps = [os.stat(p).st_mtime for p in glob.glob(os.path.join(course_dir, '*.md'))]
    if not stamps:
        return ''
    return datetime.datetime.fromtimestamp(max(stamps)).strftime('%Y-%m-%d')


def questions(course_dir):
    rows = []
    for p in sorted(glob.glob(os.path.join(course_dir, 'assets/疑问/*.md'))):
        text = read(p)
        m = re.search(r'^- 状态：(.+)$', text, re.M)
        title = next((line.lstrip('# ').strip() for line in text.splitlines() if line.strip()), '')
        rows.append({
            'id': os.path.basename(p)[:-3],
            'title': title,
            'state': m.group(1).strip() if m else '未标状态',
            'age': max(0, int((datetime.datetime.now().timestamp() - os.stat(p).st_mtime) / 86400)),
            'path': os.path.relpath(p, os.path.dirname(os.path.dirname(course_dir))),
        })
    return rows


def candidates(root, course):
    out = []
    for p in sorted(glob.glob(os.path.join(root, '06-内容候选/工作台候选/*.md'))):
        text = read(p)
        if f'course: {json.dumps(course, ensure_ascii=False)}' in text:
            m = re.search(r'^# (.+)$', text, re.M)
            out.append({'title': m.group(1).strip() if m else os.path.basename(p),
                        'path': os.path.relpath(p, root)})
    return out


def mentions(root, course, folder):
    """在某一层里找出提到该课程的文件。"""
    out = []
    pattern = os.path.join(root, folder, '**', '*.md')
    for p in sorted(glob.glob(pattern, recursive=True)):
        if course in read(p):
            out.append({'title': os.path.basename(p)[:-3].replace('_', ' '),
                        'path': os.path.relpath(p, root)})
    return out


def link(path, text):
    return f'[[{path}|{text}]]'


def render(root, course):
    course_dir = os.path.join(root, '02-课程真源', course)
    plan_path = os.path.join(course_dir, '00-学习计划.md')
    if not os.path.exists(plan_path):
        raise SystemExit(f'找不到学习计划：{plan_path}')
    goal = section(read(plan_path), '学习目标') or '（00-学习计划.md 里没有「学习目标」一节）'
    lessons = sorted(f for f in os.listdir(course_dir) if COURSE_RE.fullmatch(f))
    rows = questions(course_dir)
    open_rows = [q for q in rows if q['state'] not in CLOSED]
    closed_rows = [q for q in rows if q['state'] in CLOSED]
    cands = candidates(root, course)
    studies = mentions(root, course, '11-研究与验收')
    concepts = mentions(root, course, '03-知识入口与概念')
    oldest = max((q['age'] for q in open_rows), default=0)

    out = [f'# {course}｜课题主页', '',
           '> 本页由 `08-脚本与工具/course_home.py` 从各层真源机械汇总，是入口不是真源；'
           '改数据请改对应真源文件。', '']
    out += [f"**{len(lessons)} 篇正文**　｜　"
            f"未结疑问 {len(open_rows)} 条" + (f"（最老 {oldest} 天）" if oldest else '') + '　｜　'
            f"已结清 {len(closed_rows)} 条　｜　"
            f"内容候选 {len(cands)} 条　｜　"
            f"最近更新 {latest_update(course_dir)}", '']

    out += ['## 这一课要解决什么', '', goal, '']

    out += ['## 正文', '']
    if lessons:
        for name in lessons:
            out.append(f"- {link(os.path.relpath(os.path.join(course_dir, name), root), name[:-3])}")
    else:
        out.append('- 还没有正文')
    out.append('')

    out += ['## 未结疑问', '']
    if open_rows:
        out.append('| 疑问 | 状态 | 已挂 |')
        out.append('|---|---|---:|')
        for q in sorted(open_rows, key=lambda x: -x['age']):
            out.append(f"| {link(q['path'], q['title'])} | {q['state']} | {q['age']} 天 |")
        if closed_rows:
            out.append('')
            out.append(f"已结清／已撤回 {len(closed_rows)} 条："
                       + '、'.join(link(q['path'], q['id']) for q in closed_rows))
    else:
        out.append('本课题当前无未结疑问。')
    out.append('')

    out += ['## 相关研究', '']
    if studies:
        for item in studies:
            out.append(f"- {link(item['path'], item['title'])}")
    else:
        out.append('本课还没有关联的研究文档。')
    out.append('')

    out += ['## 相关概念', '']
    if concepts:
        for item in concepts:
            out.append(f"- {link(item['path'], item['title'])}")
    else:
        out.append('本课还没有关联的概念页——概念层与课程层尚未连上。')
    out.append('')

    out += ['## 产出去向', '']
    if cands:
        for item in cands:
            out.append(f"- {link(item['path'], item['title'])}")
    else:
        out.append('本课暂无内容候选。')
    out.append('')

    out += ['## 这一课的下一件事', '']
    todo = []
    if open_rows:
        triggered = sum(1 for q in open_rows if q['state'] == '已触发')
        waiting = len(open_rows) - triggered
        parts = []
        if triggered:
            parts.append(f'已触发 {triggered} 条在办')
        if waiting:
            parts.append(f'待触发 {waiting} 条等条件')
        todo.append(f"未结疑问 {len(open_rows)} 条（{'、'.join(parts)}）：`Phase 2.5` 每篇至少推掉一条。")
    if not concepts:
        todo.append('概念层还没接上——本课没引用任何 `03-知识入口与概念/` 的页面。')
    if not studies:
        todo.append('还没有研究文档挂在这一课下。')
    if not todo:
        todo.append('当前没有欠项。')
    out += [f'{i}. {item}' for i, item in enumerate(todo, 1)]
    out.append('')
    return '\n'.join(out).rstrip() + '\n'


def write_home(root, course, check=False):
    course_dir = os.path.join(root, '02-课程真源', course)
    target = os.path.join(course_dir, HOME)
    body = render(root, course)
    old = read(target) if os.path.exists(target) else None
    if old == body:
        return 'unchanged'
    if check:
        return 'differs'
    with open(target, 'w', encoding='utf-8') as handle:
        handle.write(body)
    return 'written'


def courses(root):
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(root, '02-课程真源', '*'))
                  if os.path.isdir(p) and os.path.exists(os.path.join(p, '00-学习计划.md')))


def main(argv=None):
    parser = argparse.ArgumentParser(description='生成课程主页')
    parser.add_argument('--root', default=DEFAULT_ROOT)
    parser.add_argument('--course')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    targets = [args.course] if args.course else (courses(args.root) if args.all else [])
    if not targets:
        parser.error('请给 --course <课程名> 或 --all')
    stats = {}
    for course in targets:
        try:
            result = write_home(args.root, course, check=args.check)
        except SystemExit as exc:
            result = f'error: {exc}'
        stats[result.split(':')[0]] = stats.get(result.split(':')[0], 0) + 1
        print(f'{course}: {result}')
    print('汇总:', stats)
    return 0


if __name__ == '__main__':
    sys.exit(main())
