#!/usr/bin/env python3
"""
为所有概念生成关联关系
"""

import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/housibo/Documents/dacapo-学习仓库")
CONCEPTS_DIR = BASE_DIR / "concepts" / "core"

# 读取所有概念
concepts = {}
for filepath in CONCEPTS_DIR.glob("*.md"):
    name = filepath.stem
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取定义
    definition_match = re.search(r'## 定义\s*\n\s*(.+)', content)
    definition = definition_match.group(1) if definition_match else ""

    concepts[name] = {
        'file': filepath,
        'definition': definition,
        'content': content
    }

print(f"读取到 {len(concepts)} 个概念\n")

# 手工定义的概念关联（基于语义分析）
relations = {
    # AI 工作流相关
    "harness": ["context-engineering", "架构约束的确定性执行", "拓扑作为新抽象层"],
    "context-engineering": ["harness", "解空间收窄", "rigor-的搬迁"],
    "Loop Engineering": ["交互式学习", "验证流水线", "自迭代机制"],
    "交互式学习": ["Loop Engineering", "学习工作台", "理解边缘探测"],
    "能力库存与工作记忆": ["harness", "拓扑作为新抽象层", "解空间收窄"],

    # Agent 工作流相关
    "船长船员比喻": ["First Mate", "人机协作规划", "控制权边界"],
    "First Mate": ["船长船员比喻", "并行工作树", "2W2H 框架"],
    "并行工作树": ["First Mate", "验证流水线", "2W2H 框架"],
    "验证流水线": ["并行工作树", "Loop Engineering", "功能与行为验证的缺口"],
    "2W2H 框架": ["First Mate", "并行工作树", "人机协作规划"],

    # 记忆与知识管理
    "四类记忆": ["retain-recall-reflect", "ai-memory", "Hindsight"],
    "retain-recall-reflect": ["四类记忆", "显影与退役判据", "ai-memory"],
    "显影与退役判据": ["retain-recall-reflect", "卡住即信号", "垃圾回收型-agent"],
    "ai-memory": ["四类记忆", "compile-not-retrieve", "知识编译"],
    "compile-not-retrieve": ["ai-memory", "知识编译", "现查模式"],

    # 知识组织
    "现查模式": ["知识编译", "compile-not-retrieve", "摄入查询体检"],
    "知识编译": ["现查模式", "三层架构", "compile-not-retrieve"],
    "三层架构": ["知识编译", "摄入查询体检", "开放知识格式"],
    "摄入查询体检": ["三层架构", "现查模式", "ETL 模式"],
    "开放知识格式": ["三层架构", "主题阅读法", "学习工作台"],

    # 架构与工程
    "架构约束的确定性执行": ["harness", "service-template-与-golden-path", "拓扑作为新抽象层"],
    "service-template-与-golden-path": ["架构约束的确定性执行", "ai-友好度作为选型标准", "rigor-的搬迁"],
    "拓扑作为新抽象层": ["架构约束的确定性执行", "harness", "解空间收窄"],
    "解空间收窄": ["topo作为新抽象层", "context-engineering", "能力库存与工作记忆"],

    # 质量与验证
    "功能与行为验证的缺口": ["验证流水线", "rigor-的搬迁", "卡住即信号"],
    "rigor-的搬迁": ["功能与行为验证的缺口", "service-template-与-golden-path", "context-engineering"],
    "卡住即信号": ["显影与退役判据", "功能与行为验证的缺口", "垃圾回收型-agent"],

    # 系统维护
    "垃圾回收型-agent": ["卡住即信号", "显影与退役判据", "熵与腐化"],
    "熵与腐化": ["垃圾回收型-agent", "自迭代机制", "最小可用软件闭环"],
    "无手打代码": ["ai-友好度作为选型标准", "窗口到系统", "Loop Engineering"],

    # 思维方法
    "第一性原理": ["双向钢人论证", "如实所现", "材料内机制"],
    "双向钢人论证": ["第一性原理", "稻草人谬误", "修辞三要素"],
    "稻草人谬误": ["双向钢人论证", "修辞三要素", "社会行动"],
    "修辞三要素": ["双向钢人论证", "稻草人谬误", "主题阅读法"],

    # 学习方法
    "理解边缘探测": ["交互式学习", "探测规划教学", "学习工作台"],
    "探测规划教学": ["理解边缘探测", "交互式学习", "人机协作规划"],
    "学习工作台": ["理解边缘探测", "收原话归属回填", "开放知识格式"],
    "收原话归属回填": ["学习工作台", "有界 handoff", "主题阅读法"],
    "主题阅读法": ["收原话归属回填", "开放知识格式", "修辞三要素"],

    # 控制与边界
    "控制权边界": ["船长船员比喻", "有界 handoff", "人机协作规划"],
    "有界 handoff": ["控制权边界", "compile-not-retrieve", "收原话归属回填"],
    "人机协作规划": ["控制权边界", "船长船员比喻", "探测规划教学"],

    # 闭环与迭代
    "最小闭环": ["最小可用软件闭环", "ETL 模式", "验证流水线"],
    "最小可用软件闭环": ["最小闭环", "自迭代机制", "熵与腐化"],
    "自迭代机制": ["最小可用软件闭环", "Loop Engineering", "显影与退役判据"],
    "ETL 模式": ["最小闭环", "摄入查询体检", "拓扑作为新抽象层"],

    # 技术与实现
    "ai-友好度作为选型标准": ["service-template-与-golden-path", "无手打代码", "跨模型迁移"],
    "跨模型迁移": ["ai-友好度作为选型标准", "harness", "开放知识格式"],
    "窗口到系统": ["无手打代码", "frontier 分层", "拓扑作为新抽象层"],

    # AI 检测
    "AI 文本可检测性": ["两条检测技术路线", "slop", "U 型位置曲线"],
    "两条检测技术路线": ["AI 文本可检测性", "位置鲁棒性", "slop"],
    "slop": ["AI 文本可检测性", "两条检测技术路线", "理解边缘探测"],

    # 长上下文
    "U 型位置曲线": ["位置鲁棒性", "AI 文本可检测性", "context-engineering"],
    "位置鲁棒性": ["U 型位置曲线", "两条检测技术路线", "harness"],

    # 其他
    "材料内机制": ["第一性原理", "行动实验", "如实所现"],
    "行动实验": ["材料内机制", "理解边缘探测", "显影与退役判据"],
    "如实所现": ["材料内机制", "第一性原理", "树林认知体系"],
    "树林认知体系": ["如实所现", "主题阅读法", "三层架构"],
    "frontier 分层": ["窗口到系统", "三层架构", "拓扑作为新抽象层"],
    "商业方法论": ["金钱性格", "社会行动", "修辞三要素"],
    "金钱性格": ["商业方法论", "ENTP 天赋", "认识自己"],
    "社会行动": ["商业方法论", "稻草人谬误", "斯多葛哲学"],
    "斯多葛哲学": ["社会行动", "如实所现", "修辞三要素"],
    "ENTP 天赋": ["金钱性格", "认识自己", "理解边缘探测"],
}

print("开始更新概念文件的关联关系...\n")

updated_count = 0
for concept_name, related_concepts in relations.items():
    if concept_name not in concepts:
        print(f"⚠️  概念不存在: {concept_name}")
        continue

    filepath = concepts[concept_name]['file']
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已有关联
    if "## 相关概念" not in content:
        print(f"⚠️  {concept_name}: 缺少相关概念部分")
        continue

    # 构建关联列表
    related_list = "\n".join([f"- [[{rc}]]" for rc in related_concepts if rc in concepts])

    # 替换"相关概念"部分
    new_content = re.sub(
        r'## 相关概念\s*\n\s*（待补充）',
        f'## 相关概念\n\n{related_list}',
        content
    )

    # 如果内容有变化，写回文件
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ 更新: {concept_name} ({len(related_concepts)} 个关联)")
        updated_count += 1

print(f"\n📊 统计:")
print(f"  - 更新概念: {updated_count} 个")
print(f"  - 定义关联: {len(relations)} 个")
print(f"  - 关联总数: {sum(len(v) for v in relations.values())} 条")
