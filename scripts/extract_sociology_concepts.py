#!/usr/bin/env python3
"""
从社会学课程中提取概念到 DaCapo 概念库

读取 ~/Documents/dbskill-learning/社会学七书共读/ 中的：
1. 00-学习计划.md 的反馈摘要表（识别用户自产概念）
2. 01-09.md 的正文（提取社会学核心概念）
3. 生成 concepts/ 下的概念文件
"""
import re
from pathlib import Path

SOCIOLOGY_COURSE = Path.home() / "Documents/dbskill-learning/社会学七书共读"
DACAPO_CONCEPTS = Path(__file__).parent.parent / "concepts"

# 从学习计划中提取的自产概念
USER_CONCEPTS = [
    ("人情期货", "人情账=期货，咖位差不多、延迟交付、循环飞轮", "03.md"),
    ("面子估值", "面子=一级市场估值，影响力变现给同级，估值矛盾时长老来解释", "03.md"),
    ("现代长老", "现代长老=自媒体博主，租牌的内容长老 vs 波纹长老", "03.md"),
    ("婚礼产品发布会", "婚礼=社交属性的产品发布会，产品=延续两家族的新家庭", "05.md"),
    ("彩礼异化", "形式比功能活得久，彩礼从信用分登记变成一次性保证金", "06.md"),
    ("结构紧张", "倒丁字结构：大底座+窄柱，需要逆熵维持否则会崩溃", "04.md"),
    ("人性三分法", "重建柏拉图灵魂三分：欲望/理性/thymos（承认需求）", "07.md"),
    ("承认与狂热", "承认≈乌合之众群体狂热，溶解型（匿名换归属）vs 署名型（标签换签名）", "07.md"),
    ("铁笼囚徒困境", "铁笼=集体囚徒困境，单方面退出者先受损→纳什锁死", "08.md"),
]

# 社会学核心概念
SOCIOLOGY_CONCEPTS = [
    ("社会学想象力", "个人困境→公共议题的改写能力", "01.md"),
    ("差序格局", "以自我为中心的同心圆社交网络，圈内人情、圈外规则", "02.md"),
    ("礼治秩序", "熟人社会的自治规则，靠眼睛（征信）和面子（信用分）维持", "03.md"),
    ("社会分层", "用收入、职业、教育、权力四把尺子测量不平等", "04.md"),
    ("先赋vs自致", "出生发的（户籍、家庭、波纹）vs 自己挣的（文凭、作品、行情）", "04.md"),
    ("再生产", "家庭作为分层车间，出厂设置=资本/波纹/规矩", "05.md"),
    ("公私界碑", "女权主义三次挪碑：人格→个人的即政治的→交叉相乘", "06.md"),
    ("承认政治", "thymos 两种面额（平等/优越），尊严赤字=第五种货币", "07.md"),
    ("理性化铁笼", "工具理性压倒价值理性，优化器吃掉损失函数", "08.md"),
]

def create_concept_file(name: str, definition: str, source: str, category: str = "sociology"):
    """创建概念文件"""
    concept_file = DACAPO_CONCEPTS / f"{name}.md"
    
    content = f"""---
tags: concept, {category}
firstAppearance: "[[社会学七书共读/{source}]]"
mastery: null
lastStudied: null
studyCount: 0
---

# {name}

## 定义

{definition}

## 相关概念

- [[差序格局]]
- [[礼治秩序]]
- [[社会分层]]

## 来源

首次出现于：[[社会学七书共读/{source}]]
"""
    
    with open(concept_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ 创建概念文件: {name}.md")

def main():
    print("=" * 60)
    print("📚 从社会学课程提取概念到 DaCapo 系统")
    print("=" * 60)
    print()
    
    # 确保 concepts 目录存在
    DACAPO_CONCEPTS.mkdir(exist_ok=True)
    
    # 1. 提取用户自产概念
    print("1️⃣ 提取用户自产概念（9 个）...")
    for name, definition, source in USER_CONCEPTS:
        create_concept_file(name, definition, source, "user-generated")
    print()
    
    # 2. 提取社会学核心概念
    print("2️⃣ 提取社会学核心概念（9 个）...")
    for name, definition, source in SOCIOLOGY_CONCEPTS:
        create_concept_file(name, definition, source, "sociology-core")
    print()
    
    print("=" * 60)
    print("✅ 完成！共创建 18 个概念文件")
    print("=" * 60)
    print()
    print("下一步：运行 rebuild_learning_progress.py 重新计算掌握度")

if __name__ == "__main__":
    main()
