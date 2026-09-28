#!/usr/bin/env python3
"""
从课程章节中提取细粒度概念
"""

import os
import re
import json
from pathlib import Path

# 工作目录
BASE_DIR = Path("/Users/housibo/Documents/dacapo-学习仓库")
COURSES_DIR = BASE_DIR / "courses"
CONCEPTS_DIR = BASE_DIR / "concepts" / "core"

# 确保概念目录存在
CONCEPTS_DIR.mkdir(parents=True, exist_ok=True)

# 读取现有概念列表
existing_concepts = set()
if CONCEPTS_DIR.exists():
    for f in CONCEPTS_DIR.glob("*.md"):
        concept_name = f.stem
        existing_concepts.add(concept_name)

print(f"现有概念数量: {len(existing_concepts)}")
print(f"现有概念: {sorted(existing_concepts)}\n")

# 遍历所有课程
extracted_concepts = []
course_count = 0

for course_dir in sorted(COURSES_DIR.iterdir()):
    if not course_dir.is_dir():
        continue

    course_name = course_dir.name
    course_count += 1

    print(f"[{course_count}] 处理课程: {course_name}")

    # 查找第一章
    chapter_files = sorted(course_dir.glob("*.md"))
    if not chapter_files:
        print(f"  ⚠️ 未找到章节文件")
        continue

    first_chapter = chapter_files[0]
    print(f"  📖 读取: {first_chapter.name}")

    # 读取章节内容（前 1500 字符）
    try:
        with open(first_chapter, 'r', encoding='utf-8') as f:
            content = f.read(1500)
    except Exception as e:
        print(f"  ❌ 读取失败: {e}")
        continue

    # 提取标题作为上下文
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    chapter_title = title_match.group(1) if title_match else first_chapter.stem

    # 输出章节标题和内容预览
    print(f"  📝 章节标题: {chapter_title}")
    print(f"  📄 内容预览 (前 200 字):\n{content[:200]}...\n")

    # 记录课程信息供后续人工提取
    extracted_concepts.append({
        'course': course_name,
        'chapter': chapter_title,
        'file': str(first_chapter),
        'preview': content[:500]
    })

# 保存提取结果供人工审查
output_file = BASE_DIR / "scripts" / "concept_extraction_raw.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(extracted_concepts, f, ensure_ascii=False, indent=2)

print(f"\n✅ 已处理 {course_count} 个课程")
print(f"✅ 提取数据已保存到: {output_file}")
print(f"\n下一步: 人工审查提取结果，创建概念文件")
