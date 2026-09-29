#!/usr/bin/env python3
"""
从 concepts/ 目录更新 mastery.json

读取每个概念文件的 frontmatter，提取 mastery 数据
"""
import json
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
CONCEPTS_DIR = PROJECT_ROOT / "concepts"
LEARNING_PROGRESS = PROJECT_ROOT / ".learning-progress"

def extract_frontmatter(content: str) -> dict:
    """提取 YAML frontmatter"""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    
    yaml_content = match.group(1)
    frontmatter = {}
    
    for line in yaml_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # 处理不同类型的值
            if value == 'null' or value == '':
                frontmatter[key] = None
            elif value.isdigit():
                frontmatter[key] = int(value)
            elif value.replace('.', '').isdigit():
                frontmatter[key] = float(value)
            else:
                frontmatter[key] = value
    
    return frontmatter

def update_mastery():
    """更新 mastery.json"""
    mastery = {}
    
    for concept_file in CONCEPTS_DIR.rglob("*.md"):
        if concept_file.name == "INDEX.md":
            continue
        
        concept_name = concept_file.stem
        
        with open(concept_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter = extract_frontmatter(content)
        
        # 只记录有 mastery 数据的概念
        mastery_score = frontmatter.get('mastery')
        if mastery_score is not None and mastery_score > 0:
            mastery[concept_name] = {
                "score": mastery_score,
                "signal_type": "deep_understanding",  # 默认
                "mention_count": frontmatter.get('studyCount', 1),
                "first_date": frontmatter.get('lastStudied', datetime.now().strftime("%Y-%m-%d")),
                "last_date": frontmatter.get('lastStudied', datetime.now().strftime("%Y-%m-%d")),
                "total_signals": frontmatter.get('studyCount', 1)
            }
    
    # 保存到 mastery.json
    output_file = LEARNING_PROGRESS / "mastery.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mastery, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 mastery.json")
    print(f"   概念总数: {len(mastery)}")
    print(f"   平均掌握度: {sum(m['score'] for m in mastery.values()) / len(mastery):.1%}")

if __name__ == "__main__":
    update_mastery()
