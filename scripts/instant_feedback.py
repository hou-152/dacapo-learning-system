#!/usr/bin/env python3
"""
即时反馈生成器 - 学完概念后生成关联网络可视化

功能：
1. 读取概念关系图谱
2. 计算"解锁"状态（前置概念已掌握）
3. 生成关联网络可视化（Mermaid）
4. 计算复利指数
"""
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
CONCEPTS_DIR = PROJECT_ROOT / "concepts"
CONCEPT_GRAPH = PROJECT_ROOT / "CONCEPT-GRAPH.md"
LEARNING_PROGRESS = PROJECT_ROOT / ".learning-progress"

def load_concept_relations() -> Dict[str, List[str]]:
    """加载概念关系图谱

    返回: {
        "concept_name": ["related_concept_1", "related_concept_2", ...]
    }
    """
    relations = {}

    for concept_file in CONCEPTS_DIR.rglob("*.md"):
        if concept_file.name == "INDEX.md":
            continue

        concept_name = concept_file.stem
        related = []

        try:
            with open(concept_file, 'r', encoding='utf-8') as f:
                in_related_section = False
                for line in f:
                    if line.strip() == "## 相关概念":
                        in_related_section = True
                        continue
                    if in_related_section:
                        if line.startswith("##"):
                            break
                        if line.strip().startswith("- [["):
                            # 提取 [[概念名]]
                            related_concept = line.strip()[4:-2]
                            related.append(related_concept)
        except Exception as e:
            print(f"⚠️  读取 {concept_file} 失败: {e}")
            continue

        relations[concept_name] = related

    return relations

def load_mastery_scores() -> Dict[str, float]:
    """加载概念掌握度"""
    mastery_file = LEARNING_PROGRESS / "mastery.json"
    if not mastery_file.exists():
        return {}

    with open(mastery_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_unlocked_concepts(
    learned_concept: str,
    relations: Dict[str, List[str]],
    mastery: Dict[str, float]
) -> Tuple[List[str], List[str]]:
    """计算学完这个概念后解锁的新概念

    返回: (新解锁的概念列表, 接近解锁的概念列表)
    """
    def get_mastery_score(concept):
        """提取掌握度分数"""
        m = mastery.get(concept, 0)
        if isinstance(m, dict):
            return m.get("score", 0)
        return m

    unlocked = []
    near_unlock = []

    # 找到所有依赖 learned_concept 的概念
    for concept, related in relations.items():
        if learned_concept in related:
            # 检查其他前置概念是否都已掌握
            dependencies = related
            mastered_deps = sum(1 for dep in dependencies if get_mastery_score(dep) >= 0.6)
            total_deps = len(dependencies)

            if mastered_deps == total_deps:
                unlocked.append(concept)
            elif mastered_deps >= total_deps - 1:
                near_unlock.append(concept)

    return unlocked, near_unlock

def generate_relation_network_mermaid(
    center_concept: str,
    relations: Dict[str, List[str]],
    mastery: Dict[str, float],
    depth: int = 1
) -> str:
    """生成关联网络的 Mermaid 图

    Args:
        center_concept: 中心概念
        relations: 概念关系图谱
        mastery: 概念掌握度
        depth: 展开深度（1=只显示直接关联，2=显示二度关联）

    返回: Mermaid 图的 Markdown 代码
    """
    def get_mastery_score(concept):
        """提取掌握度分数"""
        m = mastery.get(concept, 0)
        if isinstance(m, dict):
            return m.get("score", 0)
        return m

    mermaid = ["```mermaid", "graph TD"]

    # 中心概念（高亮）
    mastery_score = get_mastery_score(center_concept)
    center_style = "fill:#ffd700,stroke:#333,stroke-width:3px"
    mermaid.append(f'    CENTER["{center_concept}\\n掌握度: {mastery_score:.0%}"]')
    mermaid.append(f'    style CENTER {center_style}')

    # 前置概念（依赖）
    dependencies = relations.get(center_concept, [])
    for dep in dependencies:
        dep_mastery = get_mastery_score(dep)
        dep_color = "#90EE90" if dep_mastery >= 0.6 else "#FFB6C1"
        mermaid.append(f'    DEP_{dep}["{dep}\\n{dep_mastery:.0%}"]')
        mermaid.append(f'    style DEP_{dep} fill:{dep_color}')
        mermaid.append(f'    DEP_{dep} --> CENTER')

    # 后续概念（被引用）
    for concept, related in relations.items():
        if center_concept in related:
            concept_mastery = get_mastery_score(concept)
            concept_color = "#90EE90" if concept_mastery >= 0.6 else "#E0E0E0"
            mermaid.append(f'    POST_{concept}["{concept}\\n{concept_mastery:.0%}"]')
            mermaid.append(f'    style POST_{concept} fill:{concept_color}')
            mermaid.append(f'    CENTER --> POST_{concept}')

    mermaid.append("```")
    return "\n".join(mermaid)

def calculate_compound_index(
    learned_concepts: int,
    total_connections: int,
    avg_mastery: float
) -> float:
    """计算复利指数

    复利指数 = (已学概念数 × 平均掌握度 × 关联密度)
    关联密度 = 总关联数 / (已学概念数 × (已学概念数 - 1))
    """
    if learned_concepts <= 1:
        return 0.0

    max_connections = learned_concepts * (learned_concepts - 1)
    connection_density = total_connections / max_connections if max_connections > 0 else 0

    compound_index = learned_concepts * avg_mastery * connection_density * 100
    return compound_index

def generate_instant_feedback(concept_name: str) -> str:
    """生成学完概念后的即时反馈

    返回: Markdown 格式的反馈报告
    """
    # 加载数据
    relations = load_concept_relations()
    mastery = load_mastery_scores()

    # 更新掌握度
    mastery[concept_name] = 1.0  # 刚学完，标记为完全掌握

    # 计算解锁状态
    unlocked, near_unlock = calculate_unlocked_concepts(concept_name, relations, mastery)

    # 计算统计数据（处理新格式）
    scores = []
    for m in mastery.values():
        if isinstance(m, dict):
            scores.append(m.get("score", 0))
        else:
            scores.append(m)

    learned_count = sum(1 for s in scores if s >= 0.6)
    avg_mastery = sum(scores) / len(scores) if scores else 0
    total_connections = sum(len(related) for related in relations.values())
    compound_index = calculate_compound_index(learned_count, total_connections, avg_mastery)

    # 生成反馈报告
    feedback = [
        f"# 🎉 完成学习：{concept_name}",
        "",
        "---",
        "",
        "## 📊 学习进度",
        "",
        f"- **已掌握概念**: {learned_count} 个",
        f"- **平均掌握度**: {avg_mastery:.1%}",
        f"- **知识网络**: {total_connections} 条关联",
        f"- **复利指数**: {compound_index:.1f}",
        "",
        "---",
        "",
        "## 🔓 解锁新概念",
        ""
    ]

    if unlocked:
        feedback.append("✨ 恭喜！你已经可以理解这些概念了：")
        feedback.append("")
        for concept in unlocked:
            feedback.append(f"- **{concept}** - 所有前置概念已掌握")
    else:
        feedback.append("暂无新概念解锁")

    feedback.append("")

    if near_unlock:
        feedback.append("🔜 接近解锁（还差 1 个前置概念）：")
        feedback.append("")
        for concept in near_unlock:
            feedback.append(f"- {concept}")

    feedback.extend([
        "",
        "---",
        "",
        "## 🕸️ 关联网络",
        "",
        generate_relation_network_mermaid(concept_name, relations, mastery),
        "",
        "---",
        "",
        "## 💡 应用建议",
        "",
        f"基于你的学习特征，建议下一步：",
        "",
        "1. 如果想深入机制层，可以学习解锁的新概念",
        "2. 如果想横向展开，可以查看相关应用案例",
        "3. 如果想验证理解，可以尝试用自己的话解释给别人",
        "",
    ])

    return "\n".join(feedback)

def main():
    """测试用例"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python instant_feedback.py <概念名>")
        sys.exit(1)

    concept_name = sys.argv[1]
    feedback = generate_instant_feedback(concept_name)

    # 保存到文件
    output_file = LEARNING_PROGRESS / f"feedback-{concept_name}.md"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(feedback)

    print(feedback)
    print(f"\n📁 反馈已保存到: {output_file}")

if __name__ == "__main__":
    main()
