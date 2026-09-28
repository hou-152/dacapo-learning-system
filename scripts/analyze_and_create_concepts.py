#!/usr/bin/env python3
"""
智能分析章节内容，提取并创建概念文件
"""

import json
import re
from pathlib import Path

BASE_DIR = Path("/Users/housibo/Documents/dacapo-学习仓库")
CONCEPTS_DIR = BASE_DIR / "concepts" / "core"

# 读取提取的原始数据
with open(BASE_DIR / "scripts" / "concept_extraction_raw.json", 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# 读取现有概念
existing_concepts = set()
for f in CONCEPTS_DIR.glob("*.md"):
    existing_concepts.add(f.stem)

# 手工提取的概念列表（基于章节内容分析）
concepts_to_create = [
    # 从 AI工作流控制权迁移 提取
    {"name": "Loop Engineering", "definition": "通过循环迭代优化 AI 工作流的工程方法", "course": "AI工作流控制权迁移", "chapter": "01"},
    {"name": "交互式学习", "definition": "基于交互反馈动态调整学习路径的学习模式", "course": "AI工作流控制权迁移", "chapter": "01"},
    {"name": "第一性原理", "definition": "从最基本的真理出发进行推导的思维方法", "course": "AI工作流控制权迁移", "chapter": "01"},
    {"name": "能力库存与工作记忆", "definition": "区分可调用能力与当前激活能力的架构概念", "course": "AI工作流控制权迁移", "chapter": "01"},

    # 从 Agentic Engineering 工作流 提取
    {"name": "船长船员比喻", "definition": "用船长船员关系描述人与 Agent 的协作模式", "course": "Agentic Engineering 工作流", "chapter": "00"},
    {"name": "First Mate", "definition": "Agent 系统中的第一副手角色", "course": "Agentic Engineering 工作流", "chapter": "00"},
    {"name": "并行工作树", "definition": "多个 Agent 并行执行任务的树形结构", "course": "Agentic Engineering 工作流", "chapter": "00"},
    {"name": "验证流水线", "definition": "自动化验证代码变更的流程系统", "course": "Agentic Engineering 工作流", "chapter": "00"},

    # 从 Hindsight 提取
    {"name": "四类记忆", "definition": "Hindsight 系统中的四种记忆类型分类", "course": "Hindsight", "chapter": "00"},
    {"name": "retain-recall-reflect", "definition": "记忆系统的三个核心操作：保留、回忆、反思", "course": "Hindsight", "chapter": "00"},
    {"name": "显影与退役判据", "definition": "判断知识何时显现和何时淘汰的标准", "course": "Hindsight", "chapter": "00"},

    # 从 LLM Wiki 方法论 提取
    {"name": "现查模式", "definition": "即时检索而非预先编译知识的工作模式", "course": "LLM Wiki 方法论", "chapter": "00"},
    {"name": "知识编译", "definition": "将知识预先整理成可直接使用的形式", "course": "LLM Wiki 方法论", "chapter": "00"},
    {"name": "三层架构", "definition": "LLM Wiki 的分层知识组织结构", "course": "LLM Wiki 方法论", "chapter": "00"},
    {"name": "摄入查询体检", "definition": "知识维护的三个原子操作", "course": "LLM Wiki 方法论", "chapter": "00"},

    # 从 context-harness-engineering 提取
    {"name": "ETL 模式", "definition": "Extract-Transform-Load 数据处理模式", "course": "context-harness-engineering", "chapter": "00"},
    {"name": "最小闭环", "definition": "能够独立完成验证的最小系统单元", "course": "context-harness-engineering", "chapter": "00"},

    # 从 双向钢人论证与深度思考Prompt 提取
    {"name": "双向钢人论证", "definition": "同时强化正反两方观点的论证方法", "course": "双向钢人论证与深度思考Prompt", "chapter": "00"},
    {"name": "稻草人谬误", "definition": "攻击对方观点的扭曲版本而非真实论点", "course": "双向钢人论证与深度思考Prompt", "chapter": "00"},

    # 从 AI 检测原理与课堂判读 提取
    {"name": "AI 文本可检测性", "definition": "AI 生成文本的可识别特征与检测机制", "course": "AI 检测原理与课堂判读", "chapter": "00"},
    {"name": "两条检测技术路线", "definition": "AI 文本检测的两种主要技术方向", "course": "AI 检测原理与课堂判读", "chapter": "00"},

    # 从 2026气运+1 提取
    {"name": "材料内机制", "definition": "基于材料内部证据构建的运作机制", "course": "2026气运+1", "chapter": "00"},
    {"name": "行动实验", "definition": "可观察、可反驳的行动验证方式", "course": "2026气运+1", "chapter": "00"},

    # 从 AI 时代更重要的三种技能 提取
    {"name": "slop", "definition": "AI 生成内容中的低质量产出", "course": "AI 时代更重要的三种技能", "chapter": "00"},
    {"name": "理解边缘探测", "definition": "探测学习者理解边界的测试方法", "course": "AI 时代更重要的三种技能", "chapter": "00"},
    {"name": "探测规划教学", "definition": "AI 辅助学习的三阶段流程", "course": "AI 时代更重要的三种技能", "chapter": "00"},

    # 从 ai时代人的控制权边界 提取
    {"name": "控制权边界", "definition": "人与 AI 系统之间的控制权分界线", "course": "ai时代人的控制权边界", "chapter": "00"},

    # 从 frontier-分层 提取
    {"name": "frontier 分层", "definition": "前沿技术的分层理解框架", "course": "frontier-分层", "chapter": "00"},

    # 从 dontbesilent-商业方法论 提取
    {"name": "商业方法论", "definition": "系统化的商业实践方法体系", "course": "dontbesilent-商业方法论", "chapter": "00"},

    # 从 多 Agent 编排 2W2H 提取
    {"name": "2W2H 框架", "definition": "Who-What-When-How 的多 Agent 编排框架", "course": "多 Agent 编排 2W2H", "chapter": "00"},

    # 从 开放知识格式 OKF 提取
    {"name": "开放知识格式", "definition": "标准化的知识表示和交换格式", "course": "开放知识格式 OKF", "chapter": "00"},

    # 从 自迭代小龙虾与自迭代Skill 提取
    {"name": "自迭代机制", "definition": "系统通过反馈自我改进的机制", "course": "自迭代小龙虾与自迭代Skill", "chapter": "00"},

    # 从 最小可用软件闭环 提取
    {"name": "最小可用软件闭环", "definition": "能独立验证和运行的最小软件单元", "course": "最小可用软件闭环", "chapter": "00"},

    # 从 和 agent 一起做规划 提取
    {"name": "人机协作规划", "definition": "人与 Agent 共同进行规划的协作模式", "course": "和 agent 一起做规划", "chapter": "00"},

    # 从 让-learning-skill-跨模型真正好用 提取
    {"name": "跨模型迁移", "definition": "技能在不同 AI 模型间迁移的能力", "course": "让-learning-skill-跨模型真正好用", "chapter": "00"},

    # 从 迷失在中间 提取
    {"name": "U 型位置曲线", "definition": "长上下文中信息检索准确率的 U 型分布", "course": "迷失在中间：语言模型如何使用长上下文", "chapter": "00"},
    {"name": "位置鲁棒性", "definition": "模型对信息位置变化的稳定性", "course": "迷失在中间：语言模型如何使用长上下文", "chapter": "00"},

    # 从 个人学习工作台实践 提取
    {"name": "学习工作台", "definition": "个人学习的系统化工作环境", "course": "个人学习工作台实践", "chapter": "00"},
    {"name": "收原话归属回填", "definition": "学习工作台的核心操作流程", "course": "个人学习工作台实践", "chapter": "00"},

    # 从 钱势金生 提取
    {"name": "金钱性格", "definition": "个人与金钱关系的基本性格特征", "course": "钱势金生", "chapter": "01"},

    # 从 社会学基本概念 提取
    {"name": "社会行动", "definition": "韦伯社会学中的基本分析单元", "course": "社会学基本概念", "chapter": "00"},

    # 从 斯多葛生活哲学 提取
    {"name": "斯多葛哲学", "definition": "强调理性与内在控制的古希腊哲学流派", "course": "斯多葛生活哲学", "chapter": "00"},

    # 从 修辞学 提取
    {"name": "修辞三要素", "definition": "逻各斯、情感、品格三位一体的说服体系", "course": "修辞学", "chapter": "00"},

    # 从 如实所现 提取
    {"name": "如实所现", "definition": "不加解释地观察事物本来面目", "course": "如实所现", "chapter": "00"},
    {"name": "树林认知体系", "definition": "如实所现课程的认知框架系统", "course": "如实所现-树林的认知体系", "chapter": "00"},

    # 从 认识自己 提取
    {"name": "ENTP 天赋", "definition": "MBTI 中 ENTP 类型的天赋特质", "course": "认识自己-ENTP与天赋挖掘", "chapter": "00"},

    # 从 我常常是错的 提取
    {"name": "ai-memory", "definition": "AI 系统的记忆管理机制", "course": "我常常是错的", "chapter": "00"},
    {"name": "compile-not-retrieve", "definition": "编译而非检索的知识组织策略", "course": "我常常是错的", "chapter": "00"},
    {"name": "有界 handoff", "definition": "有明确边界的任务交接机制", "course": "我常常是错的", "chapter": "00"},

    # 从 主题阅读 提取
    {"name": "主题阅读法", "definition": "围绕特定主题横跨多本书的阅读方法", "course": "主题阅读", "chapter": "00"},

    # 从 把 AI 从窗口变成系统 提取
    {"name": "窗口到系统", "definition": "将 AI 从工具界面升级为系统级能力", "course": "把 AI 从窗口变成系统", "chapter": "00"},
]

print(f"待创建概念数量: {len(concepts_to_create)}")
print(f"现有概念数量: {len(existing_concepts)}\n")

# 创建概念文件
created_count = 0
skipped_count = 0

for concept in concepts_to_create:
    name = concept['name']
    definition = concept['definition']
    course = concept['course']
    chapter = concept['chapter']

    # 检查是否已存在
    filename = f"{name}.md"
    filepath = CONCEPTS_DIR / filename

    if filepath.exists() or name in existing_concepts:
        print(f"⏭️  跳过已存在: {name}")
        skipped_count += 1
        continue

    # 创建概念文件
    content = f"""# {name}

## 定义

{definition}

## 首次出现

[[{course}]] - {chapter}

## 相关概念

（待补充）
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 创建: {name}")
    created_count += 1

print(f"\n📊 统计:")
print(f"  - 新建: {created_count} 个")
print(f"  - 跳过: {skipped_count} 个")
print(f"  - 总计: {len(existing_concepts) + created_count} 个核心概念")
