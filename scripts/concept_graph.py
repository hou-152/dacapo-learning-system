#!/usr/bin/env python3
"""从概念页双链生成 Mermaid 学习图谱，写回 contents.md 的标记区块。

用法：
    python3 concept_graph.py [--root <学习真源>] [--check]

为什么画「分层」而不是「连线图」：本目录概念页底部的「相关课题」是并列推荐，
不是层级关系。实测入度 >= 10 的 6 个节点之间有 25 条边（83% 密度），画成有向图
只是一团毛线，无法表达结构。真正有信息量的是入度——被多少页引用，即枢纽程度。
"""
import argparse
import os
import re
import sys

START = '<!-- CONCEPT-GRAPH:START -->'
END = '<!-- CONCEPT-GRAPH:END -->'
SKIP = {'README', 'contents'}
HUB_MIN = 10
MID_MIN = 3


def collect(concept_dir):
    files = {os.path.basename(p)[:-3]: p for p in sorted(_glob_md(concept_dir))}
    names = set(files) - SKIP
    edges = set()
    for name in names:
        with open(files[name], encoding='utf-8') as handle:
            text = handle.read()
        for link in re.findall(r'\[\[([^\]|#]+)', text):
            target = link.strip().split('/')[0]
            if target in names and target != name:
                edges.add((name, target))
    indeg = {name: 0 for name in names}
    for _, target in edges:
        indeg[target] += 1
    return indeg


def _glob_md(folder):
    import glob
    return glob.glob(os.path.join(folder, '*.md'))


def layers(indeg):
    hub = sorted((n for n in indeg if indeg[n] >= HUB_MIN), key=lambda n: (-indeg[n], n))
    mid = sorted((n for n in indeg if MID_MIN <= indeg[n] < HUB_MIN), key=lambda n: (-indeg[n], n))
    leaf = sorted((n for n in indeg if indeg[n] < MID_MIN), key=lambda n: (-indeg[n], n))
    return [('hub', f'枢纽层 · 被 {HUB_MIN} 个以上概念页引用', hub),
            ('mid', f'次级层 · 被引用 {MID_MIN}—{HUB_MIN - 1} 次', mid),
            ('leaf', f'叶子层 · 被引用 {MID_MIN - 1} 次以下', leaf)]


def label(name):
    return name.replace('"', "'").replace('[', '（').replace(']', '）')


def render(indeg):
    groups = layers(indeg)
    lines = ['```mermaid', 'graph TD']
    index = 0
    for key, title, nodes in groups:
        if not nodes:
            continue
        lines.append(f'    subgraph {key}["{title}"]')
        lines.append('        direction LR')
        for name in nodes:
            lines.append(f'        n{index}["{label(name)} · {indeg[name]}"]')
            index += 1
        lines.append('    end')
    lines.append('```')
    return '\n'.join(lines)


def block(indeg):
    total = len(indeg)
    linked = sum(1 for n in indeg if indeg[n] > 0)
    return (f'{START}\n'
            f'> 本图由 `08-脚本与工具/concept_graph.py` 从本目录 {total} 个概念页的双链机械生成，'
            f'不要手改；改完概念页后重跑脚本。\n'
            f'> 数字是该页被其他概念页引用的次数；未画连线，原因见脚本说明。\n'
            f'> 有引用的页 {linked} / {total}。\n\n'
            f'{render(indeg)}\n'
            f'{END}')


def apply(contents_path, text, check=False, write=None):
    write = write or (lambda p, t: open(p, 'w', encoding='utf-8').write(t))
    with open(contents_path, encoding='utf-8') as handle:
        body = handle.read()
    if START in body and END in body:
        head, rest = body.split(START, 1)
        _, tail = rest.split(END, 1)
        new = head + text + tail
    else:
        head, sep, tail = body.partition('\n## 总入口')
        new = head + '\n' + text + '\n' + (sep + tail if sep else '')
    if new == body:
        return 'unchanged'
    if check:
        return 'differs'
    write(contents_path, new)
    return 'written'


def main(argv=None):
    root = '/Users/housibo/Documents/DaCapo 内容资产/01-交互式学习'
    parser = argparse.ArgumentParser(description='生成概念图谱 Mermaid')
    parser.add_argument('--root', default=root)
    parser.add_argument('--check', action='store_true', help='只检查是否与文件一致，不写入')
    args = parser.parse_args(argv)
    concept_dir = os.path.join(args.root, '03-知识入口与概念')
    contents = os.path.join(concept_dir, 'contents.md')
    if not os.path.isdir(concept_dir):
        print(f'找不到概念目录：{concept_dir}', file=sys.stderr)
        return 1
    indeg = collect(concept_dir)
    if not indeg:
        print('没有读到概念页', file=sys.stderr)
        return 1
    result = apply(contents, block(indeg), check=args.check)
    print(f'concept_graph: {result}（{len(indeg)} 页）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
