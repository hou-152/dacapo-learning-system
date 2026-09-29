#!/usr/bin/env python3
"""
从社会学课程反馈更新概念 mastery
"""
import re
from pathlib import Path

DBSKILL_SOCIOLOGY = Path("~/Documents/dbskill-learning/社会学七书共读").expanduser()
DACAPO_CONCEPTS = Path("~/Documents/dacapo-学习仓库/concepts").expanduser()

# 03.md 中用户的真实反馈显示 90% 掌握度
CONCEPT_MASTERY = {
    "差序格局": 0.90,
    "礼治秩序": 0.90,
    "人情期货": 0.90,
    "面子估值": 0.85,
    "现代长老": 0.80,
    "社会学想象力": 0.75,
    "社会分层": 0.70,
    "承认政治": 0.65,
    "理性化铁笼": 0.65,
    "先赋vs自致": 0.60,
    "铁笼囚徒困境": 0.60,
    "公私界碑": 0.55,
    "彩礼异化": 0.55,
    "结构紧张": 0.50,
    "承认与狂热": 0.50,
    "婚礼产品发布会": 0.50,
    "再生产": 0.45,
    "人性三分法": 0.40,
}

def update_concept_mastery(concept_name: str, mastery: float):
    """更新概念文件的 mastery"""
    concept_file = DACAPO_CONCEPTS / f"{concept_name}.md"
    
    if not concept_file.exists():
        print(f"⚠️  {concept_name} 文件不存在")
        return
    
    with open(concept_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换 frontmatter 中的 mastery
    content = re.sub(
        r'mastery: null',
        f'mastery: {mastery}',
        content
    )
    content = re.sub(
        r'lastStudied: null',
        'lastStudied: 2026-09-30',
        content
    )
    content = re.sub(
        r'studyCount: 0',
        'studyCount: 1',
        content
    )
    
    with open(concept_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {concept_name}: {mastery:.0%}")

def main():
    print("更新社会学概念掌握度...\n")
    
    for concept, mastery in CONCEPT_MASTERY.items():
        update_concept_mastery(concept, mastery)
    
    print(f"\n✅ 完成！共更新 {len(CONCEPT_MASTERY)} 个概念")

if __name__ == "__main__":
    main()
