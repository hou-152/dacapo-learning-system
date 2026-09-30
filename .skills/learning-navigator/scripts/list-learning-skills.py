#!/usr/bin/env python3
"""
列出 DaCapo 交互式学习系统的所有 skills
"""

import os
import sys
from pathlib import Path

# DaCapo 学习系统的固定 skills
LEARNING_SKILLS = {
    "course-generator",
    "dbs-learning",
    "concept-bridge",
}

def find_skills_dir():
    """查找 .skills 目录"""
    # 从当前目录开始向上查找
    current = Path.cwd()

    # 检查当前目录及其父目录
    for _ in range(5):  # 最多向上查找 5 层
        skills_dir = current / ".skills"
        if skills_dir.exists() and skills_dir.is_dir():
            return skills_dir

        parent = current.parent
        if parent == current:  # 到达根目录
            break
        current = parent

    # 回退到固定路径
    fallback = Path.home() / "Documents" / "dacapo-学习仓库" / ".skills"
    if fallback.exists():
        return fallback

    return None

def extract_description(skill_path):
    """从 SKILL.md 提取 description"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return "无描述"

    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            in_frontmatter = False
            for line in f:
                line = line.strip()

                if line == "---":
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        break  # 结束 frontmatter
                    continue

                if in_frontmatter and line.startswith("description:"):
                    desc = line[len("description:"):].strip()
                    # 移除引号
                    if desc.startswith('"') and desc.endswith('"'):
                        desc = desc[1:-1]
                    elif desc.startswith("'") and desc.endswith("'"):
                        desc = desc[1:-1]
                    return desc
    except Exception as e:
        return f"读取失败: {e}"

    return "无描述"

def main():
    skills_dir = find_skills_dir()
    if not skills_dir:
        print("Error: Cannot find .skills directory", file=sys.stderr)
        sys.exit(1)

    results = []
    for skill_name in sorted(LEARNING_SKILLS):
        skill_path = skills_dir / skill_name
        if not skill_path.exists():
            continue

        description = extract_description(skill_path)
        results.append({
            "name": skill_name,
            "description": description,
            "path": str(skill_path)
        })

    # 输出格式：name|description|path
    for skill in results:
        print(f"{skill['name']}|{skill['description']}|{skill['path']}")

if __name__ == "__main__":
    main()
