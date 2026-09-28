#!/usr/bin/env python3
"""
修正课程概念文件中的章节链接
将 WikiLink [[课程名/章节]] 改为实际可点击的文件路径
"""
from pathlib import Path
import re

DACAPO_ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = DACAPO_ROOT / "concepts"

def fix_chapter_links(concept_file: Path):
    """修正单个概念文件中的章节链接"""
    content = concept_file.read_text(encoding="utf-8")

    # 检查是否是课程概念
    if "type: course" not in content:
        return False, "不是课程概念"

    # 提取课程路径
    course_path_match = re.search(r'course_path:\s*(.+)', content)
    if not course_path_match:
        return False, "未找到 course_path"

    course_path = course_path_match.group(1).strip()

    # 查找章节列表部分
    chapter_section_pattern = r'(## 章节列表\n\n)((?:- 第 .+\n)+)'
    match = re.search(chapter_section_pattern, content)

    if not match:
        return False, "未找到章节列表"

    header = match.group(1)
    old_chapters = match.group(2)

    # 统计修改
    changes = 0
    new_lines = []

    for line in old_chapters.split('\n'):
        if not line.strip():
            continue

        # 匹配: - 第 XX 章: `courses/课程名/XX.md`
        if '`courses/' in line:
            new_lines.append(line)
            continue

        # 匹配旧格式需要修改的行
        # 例如: - 第 01 章 或其他格式
        chapter_match = re.search(r'- 第 ([\d\.]+) 章', line)
        if chapter_match:
            chapter_num = chapter_match.group(1)
            new_line = f"- 第 {chapter_num} 章: `{course_path}/{chapter_num}.md`"
            new_lines.append(new_line)
            changes += 1

    if changes == 0:
        return False, "无需修改"

    # 替换内容
    new_chapters = '\n'.join(new_lines) + '\n'
    new_content = content[:match.start()] + header + new_chapters + content[match.end():]

    concept_file.write_text(new_content, encoding="utf-8")
    return True, f"修改 {changes} 个章节链接"

def main():
    print("=== 修正课程概念章节链接 ===\n")

    concept_files = sorted(CONCEPT_DIR.glob("*.md"))
    course_concepts = []

    # 筛选课程概念
    for f in concept_files:
        content = f.read_text(encoding="utf-8")
        if "type: course" in content:
            course_concepts.append(f)

    print(f"找到 {len(course_concepts)} 个课程概念文件\n")

    fixed = 0
    skipped = 0

    for concept_file in course_concepts:
        success, msg = fix_chapter_links(concept_file)

        if success:
            print(f"✓ {concept_file.stem}: {msg}")
            fixed += 1
        else:
            # print(f"- {concept_file.stem}: {msg}")
            skipped += 1

    print(f"\n=== 完成 ===")
    print(f"修改: {fixed} 个")
    print(f"跳过: {skipped} 个")

if __name__ == "__main__":
    main()
