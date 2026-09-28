#!/usr/bin/env python3
"""
DaCapo 课程概念提取工具 v2
将课程目录转换为概念文件，修复 Obsidian 双链格式
"""
from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime


# 配置
DACAPO_ROOT = Path.home() / "Documents" / "dacapo-学习仓库"
COURSE_ROOT = DACAPO_ROOT / "courses"
CONCEPT_ROOT = DACAPO_ROOT / "concepts"

LESSON_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)(?:[^/]*)\.md$")
NON_LESSON_MARKERS = ("审计", "批注回应报告", "学习计划", "补充阅读")
COURSE_AUXILIARY_DIRS = {
    ".trash", "backups", "backups 2", "journals", "logseq", "pages"
}


def is_course_dir(path: Path) -> bool:
    """判断是否为课程目录"""
    if not path.is_dir() or path.is_symlink() or path.name in COURSE_AUXILIARY_DIRS:
        return False

    files = list(path.glob("*.md"))
    names = {f.name for f in files}

    # 有 plan.md 或 learner-log.md 或编号课程
    has_plan = bool({"00-学习计划.md", "plan.md", "learner-log.md"} & names)
    has_lessons = any(LESSON_PATTERN.match(f.name) for f in files
                     if not any(marker in f.stem for marker in NON_LESSON_MARKERS))

    return has_plan or has_lessons


def extract_lesson_numbers(course: Path) -> list[str]:
    """提取课程的所有章节编号"""
    lessons = []
    for f in course.glob("*.md"):
        match = LESSON_PATTERN.match(f.name)
        if match and not any(marker in f.stem for marker in NON_LESSON_MARKERS):
            lessons.append(match.group(1))

    # 按数字排序
    return sorted(lessons, key=lambda x: tuple(int(p) for p in x.split(".")))


def extract_course_status(course: Path) -> str:
    """提取课程状态"""
    plan_path = course / "plan.md"
    log_path = course / "learner-log.md"

    plan_text = plan_path.read_text(encoding="utf-8") if plan_path.exists() else ""
    log_text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    combined = plan_text + "\n" + log_text

    # 检查是否完成
    if re.search(r"已结业|状态[：:]\s*`?completed`?|course_completed", combined, re.I):
        return "completed"

    # 检查当前进度
    current_matches = re.findall(r"当前(?:单元|课|篇)[：:]\s*`?([0-9]+(?:\.[0-9]+)?)", combined)
    if current_matches:
        current = current_matches[-1]
        if re.search(r"等待|pending|await", combined, re.I):
            return f"in-progress-{current}-waiting"
        return f"in-progress-{current}"

    # 返回已有章节范围
    lessons = extract_lesson_numbers(course)
    if lessons:
        return f"available-{lessons[0]}-to-{lessons[-1]}"

    return "empty"


def generate_concept_file(course: Path) -> str:
    """为课程生成概念文件内容（修复 Obsidian 双链）"""
    course_name = course.name
    lessons = extract_lesson_numbers(course)
    status = extract_course_status(course)

    # 读取 plan.md 或第一个课程文件获取简介
    definition = ""
    plan_path = course / "plan.md"
    if plan_path.exists():
        plan_content = plan_path.read_text(encoding="utf-8")
        # 提取前 200 字作为定义
        lines = [line.strip() for line in plan_content.split("\n") if line.strip() and not line.startswith("#")]
        definition = " ".join(lines[:3])[:200] if lines else ""

    if not definition and lessons:
        first_lesson = course / f"{lessons[0]}.md"
        if first_lesson.exists():
            content = first_lesson.read_text(encoding="utf-8")
            lines = [line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")]
            definition = " ".join(lines[:2])[:200] if lines else ""

    # 生成 frontmatter
    frontmatter = {
        "type": "course",
        "course_path": f"courses/{course_name}",
        "lessons": lessons,
        "lesson_count": len(lessons),
        "status": status,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "tags": ["课程", "学习"]
    }

    # 生成 Markdown
    content = "---\n"
    for key, value in frontmatter.items():
        if isinstance(value, list):
            content += f"{key}:\n"
            for item in value:
                content += f"  - {item}\n"
        else:
            content += f"{key}: {value}\n"
    content += "---\n\n"

    content += f"# {course_name}\n\n"

    if definition:
        content += f"## 简介\n\n{definition}\n\n"

    content += f"## 课程信息\n\n"
    content += f"- **章节数**: {len(lessons)}\n"
    content += f"- **课程路径**: `courses/{course_name}`\n"
    content += f"- **状态**: {status}\n\n"

    # 修复：使用相对路径，不用 WikiLink
    if lessons:
        content += f"## 章节列表\n\n"
        for lesson in lessons:
            content += f"- 第 {lesson} 章: `courses/{course_name}/{lesson}.md`\n"
        content += "\n"

    content += f"## 访问课程\n\n"
    content += f"完整课程位于: `courses/{course_name}/`\n\n"
    content += f"通过 dacapo-wiki 查询此课程:\n"
    content += f"```bash\n"
    content += f"dacapo-wiki context \"{course_name}\"\n"
    content += f"```\n"

    return content


def main():
    """主函数：扫描课程，生成概念文件"""
    print("=== DaCapo 课程概念提取 v2 ===\n")

    # 确保概念目录存在
    CONCEPT_ROOT.mkdir(parents=True, exist_ok=True)

    # 扫描课程
    courses = sorted([d for d in COURSE_ROOT.iterdir() if is_course_dir(d)])
    print(f"发现 {len(courses)} 个课程目录\n")

    generated = 0
    for course in courses:
        course_name = course.name
        # 生成安全的文件名（替换空格和特殊字符）
        safe_name = re.sub(r'[^\w一-鿿-]+', '-', course_name)
        concept_file = CONCEPT_ROOT / f"{safe_name}.md"

        # 生成概念文件
        content = generate_concept_file(course)
        concept_file.write_text(content, encoding="utf-8")

        print(f"✓ {course_name} → {concept_file.name}")
        generated += 1

    print(f"\n=== 完成 ===")
    print(f"重新生成 {generated} 个课程概念文件")
    print(f"位置: {CONCEPT_ROOT}")
    print(f"\n✅ 修复: Obsidian 双链格式问题")
    print(f"   使用相对路径代替 WikiLink")

    # 生成统计
    print(f"\n=== 统计 ===")
    total_lessons = sum(len(extract_lesson_numbers(c)) for c in courses)
    print(f"总章节数: {total_lessons}")

    completed = sum(1 for c in courses if extract_course_status(c) == "completed")
    print(f"已完成课程: {completed}")

    in_progress = sum(1 for c in courses if "in-progress" in extract_course_status(c))
    print(f"进行中课程: {in_progress}")


if __name__ == "__main__":
    main()
