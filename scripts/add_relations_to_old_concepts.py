#!/usr/bin/env python3
"""
为现有概念添加"相关概念"部分
"""

from pathlib import Path

BASE_DIR = Path("/Users/housibo/Documents/dacapo-学习仓库")
CONCEPTS_DIR = BASE_DIR / "concepts" / "core"

# 需要补充关联的现有概念
old_concepts_relations = {
    "harness": ["context-engineering", "架构约束的确定性执行", "拓扑作为新抽象层"],
    "context-engineering": ["harness", "解空间收窄", "rigor-的搬迁"],
    "架构约束的确定性执行": ["harness", "service-template-与-golden-path", "拓扑作为新抽象层"],
    "service-template-与-golden-path": ["架构约束的确定性执行", "ai-友好度作为选型标准", "rigor-的搬迁"],
    "拓扑作为新抽象层": ["架构约束的确定性执行", "harness", "解空间收窄"],
    "解空间收窄": ["拓扑作为新抽象层", "context-engineering", "能力库存与工作记忆"],
    "功能与行为验证的缺口": ["验证流水线", "rigor-的搬迁", "卡住即信号"],
    "rigor-的搬迁": ["功能与行为验证的缺口", "service-template-与-golden-path", "context-engineering"],
    "卡住即信号": ["显影与退役判据", "功能与行为验证的缺口", "垃圾回收型-agent"],
    "垃圾回收型-agent": ["卡住即信号", "显影与退役判据", "熵与腐化"],
    "熵与腐化": ["垃圾回收型-agent", "自迭代机制", "最小可用软件闭环"],
    "无手打代码": ["ai-友好度作为选型标准", "窗口到系统", "Loop Engineering"],
    "ai-友好度作为选型标准": ["service-template-与-golden-path", "无手打代码", "跨模型迁移"],
}

print("开始为现有概念添加关联部分...\n")

updated_count = 0
for concept_name, related_concepts in old_concepts_relations.items():
    filepath = CONCEPTS_DIR / f"{concept_name}.md"

    if not filepath.exists():
        print(f"⚠️  文件不存在: {concept_name}")
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已有"相关概念"部分
    if "## 相关概念" in content or "相关概念" in content:
        print(f"⏭️  跳过已有关联: {concept_name}")
        continue

    # 构建关联列表
    related_list = "\n".join([f"- [[{rc}]]" for rc in related_concepts])

    # 在文末添加"相关概念"部分
    new_content = content.rstrip() + f"\n\n## 相关概念\n\n{related_list}\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ 添加: {concept_name} ({len(related_concepts)} 个关联)")
    updated_count += 1

print(f"\n📊 统计:")
print(f"  - 添加关联: {updated_count} 个概念")
