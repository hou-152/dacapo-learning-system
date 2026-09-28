#!/usr/bin/env python3
"""
DaCapo 统一课程索引生成器
基于概念库生成课程索引，使用 WikiLink 格式
"""
from __future__ import annotations

import re
from pathlib import Path


DACAPO_ROOT = Path.home() / "Documents" / "dacapo-学习仓库"
CONCEPT_ROOT = DACAPO_ROOT / "concepts"
INDEX_PATH = DACAPO_ROOT / "courses" / "INDEX.md"


def parse_concept_frontmatter(concept_file: Path) -> dict:
    """解析概念文件的 frontmatter"""
    content = concept_file.read_text(encoding="utf-8")

    # 提取 frontmatter
    if not content.startswith("---"):
        return {}

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    frontmatter_text = parts[1]
    metadata = {}

    current_key = None
    current_list = []

    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # 处理列表项
        if line.startswith("- "):
            if current_key:
                current_list.append(line[2:].strip())
            continue

        # 处理键值对
        if ":" in line:
            # 保存上一个列表
            if current_key and current_list:
                metadata[current_key] = current_list
                current_list = []

            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if value:  # 单行值
                metadata[key] = value
                current_key = None
            else:  # 准备接收列表
                current_key = key

    # 保存最后一个列表
    if current_key and current_list:
        metadata[current_key] = current_list

    return metadata


def format_status(status: str) -> str:
    """格式化课程状态为中文"""
    if status == "completed":
        return "已完成"
    if status.startswith("in-progress"):
        parts = status.split("-")
        if "waiting" in status:
            return f"当前 {parts[2]}，等待学习者回答"
        return f"当前 {parts[2]}"
    if status.startswith("available"):
        # available-01-to-14 → 已有 01-14
        parts = status.split("-")
        if len(parts) >= 4:
            return f"已有 {parts[1]}—{parts[3]}"
    return "暂无课程"


def generate_course_index() -> str:
    """生成课程索引 Markdown"""
    # 扫描所有课程概念
    course_concepts = []
    for concept_file in CONCEPT_ROOT.glob("*.md"):
        metadata = parse_concept_frontmatter(concept_file)
        if metadata.get("type") == "course":
            course_name = concept_file.stem.replace("-", " ")  # 恢复空格
            lesson_count = metadata.get("lesson_count", 0)
            # 确保 lesson_count 是整数
            if isinstance(lesson_count, str):
                try:
                    lesson_count = int(lesson_count)
                except ValueError:
                    lesson_count = 0

            course_concepts.append({
                "name": course_name,
                "file": concept_file.stem,
                "lessons": metadata.get("lessons", []),
                "status": metadata.get("status", "unknown"),
                "lesson_count": lesson_count
            })

    # 按课程名排序
    course_concepts.sort(key=lambda x: x["name"])

    # 生成 Markdown
    lines = [
        "# DaCapo 课程索引",
        "",
        "> 本索引基于概念库自动生成。每个课程都是一个概念，可通过 dacapo-wiki 探索关联。",
        "",
        f"**统计**: {len(course_concepts)} 个课程，共 {sum(c['lesson_count'] for c in course_concepts)} 个章节",
        "",
        "| 课程 | 章节 | 状态 |",
        "|------|------|------|",
    ]

    for course in course_concepts:
        # WikiLink 格式：[[概念名]]
        wikilink = f"[[{course['file']}|{course['name']}]]"

        # 章节列表
        lessons = course["lessons"]
        if isinstance(lessons, list) and lessons:
            lesson_display = f"{lessons[0]}—{lessons[-1]}" if len(lessons) > 1 else lessons[0]
        else:
            lesson_display = "-"

        # 状态
        status = format_status(course["status"])

        lines.append(f"| {wikilink} | {lesson_display} | {status} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 使用方式")
    lines.append("")
    lines.append("### 查看课程")
    lines.append("```bash")
    lines.append("# 通过 dacapo-wiki 查询课程")
    lines.append("dacapo-wiki context \"Agentic Engineering 工作流\"")
    lines.append("```")
    lines.append("")
    lines.append("### 探索关联")
    lines.append("```bash")
    lines.append("# 发现相关课程")
    lines.append("dacapo-wiki search \"工作流\"")
    lines.append("```")
    lines.append("")
    lines.append("### 学习路径")
    lines.append("```bash")
    lines.append("# 开始学习某个课程")
    lines.append("/dacapo 我想学习 Agentic Engineering 工作流")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main():
    """主函数"""
    print("=== DaCapo 课程索引生成 ===\n")

    # 生成索引
    index_content = generate_course_index()

    # 写入文件
    INDEX_PATH.write_text(index_content, encoding="utf-8")

    print(f"✓ 索引已生成: {INDEX_PATH}")

    # 统计
    course_count = len([f for f in CONCEPT_ROOT.glob("*.md")
                       if parse_concept_frontmatter(f).get("type") == "course"])
    print(f"✓ 包含 {course_count} 个课程")


if __name__ == "__main__":
    main()
