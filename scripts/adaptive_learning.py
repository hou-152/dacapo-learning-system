#!/usr/bin/env python3
"""
自适应学习引擎 - 核心交互层

功能：
1. 理解边缘探测（baseline detection）
2. 自适应教学内容调整
3. 掌握度评估
4. 路径推荐
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
CONCEPTS_DIR = PROJECT_ROOT / "concepts"
COURSES_DIR = PROJECT_ROOT / "courses"
LEARNING_PROGRESS = PROJECT_ROOT / ".learning-progress"

def detect_baseline(concept_name: str, prior_knowledge: Dict[str, float]) -> Dict:
    """理解边缘探测 - 3 个快速问题判断基线

    Args:
        concept_name: 要学习的概念
        prior_knowledge: 已掌握概念的掌握度 {概念名: 掌握度}

    Returns: {
        "has_heard": bool,
        "can_explain": bool,
        "related_mastered": List[str],
        "baseline_level": float  # 0-1
    }
    """
    # 读取概念文件，找出前置概念
    concept_file = None
    for cf in CONCEPTS_DIR.rglob(f"{concept_name}.md"):
        concept_file = cf
        break

    if not concept_file:
        return {
            "has_heard": False,
            "can_explain": False,
            "related_mastered": [],
            "baseline_level": 0.0
        }

    # 提取相关概念
    related_concepts = []
    try:
        with open(concept_file, 'r', encoding='utf-8') as f:
            in_related = False
            for line in f:
                if "## 相关概念" in line or "## 前置概念" in line:
                    in_related = True
                    continue
                if in_related:
                    if line.startswith("##"):
                        break
                    if "[[" in line:
                        concept = line.strip().split("[[")[1].split("]]")[0]
                        related_concepts.append(concept)
    except Exception as e:
        print(f"⚠️  读取概念文件失败: {e}")

    # 计算已掌握的前置概念
    mastered_related = [
        c for c in related_concepts
        if prior_knowledge.get(c, 0) >= 0.6
    ]

    # 基线水平 = 已掌握前置概念比例
    baseline_level = len(mastered_related) / len(related_concepts) if related_concepts else 0.0

    return {
        "has_heard": False,  # 需要用户回答
        "can_explain": False,  # 需要用户回答
        "related_mastered": mastered_related,
        "baseline_level": baseline_level
    }

def adjust_teaching_depth(baseline: Dict, concept_name: str) -> Dict:
    """根据基线调整教学深度

    Returns: {
        "skip_definition": bool,
        "focus_on": str,  # "mechanism" | "application" | "basics"
        "depth_level": int  # 1-3
    }
    """
    baseline_level = baseline["baseline_level"]
    has_heard = baseline["has_heard"]
    can_explain = baseline["can_explain"]

    if baseline_level >= 0.7:
        # 前置概念掌握很好，可以直接讲机制和应用
        return {
            "skip_definition": True,
            "focus_on": "mechanism",
            "depth_level": 3
        }
    elif baseline_level >= 0.4:
        # 有一定基础，快速过定义，重点讲应用
        return {
            "skip_definition": False,
            "focus_on": "application",
            "depth_level": 2
        }
    else:
        # 基础薄弱，从定义开始，多举例子
        return {
            "skip_definition": False,
            "focus_on": "basics",
            "depth_level": 1
        }

def evaluate_mastery(concept_name: str, user_responses: List[str]) -> float:
    """掌握度评估 - 基于情境迁移问题的回答

    Args:
        concept_name: 概念名
        user_responses: 用户对 2 个情境问题的回答

    Returns: 掌握度 (0-1)
    """
    # 简单实现：根据回答长度和关键词判断
    total_score = 0.0

    for response in user_responses:
        score = 0.0

        # 长度分：能详细解释说明理解深度
        if len(response) > 200:
            score += 0.3
        elif len(response) > 100:
            score += 0.2
        elif len(response) > 50:
            score += 0.1

        # 关键词分：包含概念核心术语
        if concept_name.lower() in response.lower():
            score += 0.1

        # 迁移能力分：能否应用到新场景
        transfer_keywords = ["可以", "应该", "首先", "然后", "因为", "所以"]
        if any(kw in response for kw in transfer_keywords):
            score += 0.1

        total_score += min(score, 0.5)  # 单个回答最多 0.5

    return min(total_score, 1.0)

def recommend_next_concepts(
    current_concept: str,
    mastery_scores: Dict[str, float],
    learning_style: str = "application_oriented"
) -> List[Tuple[str, float, str]]:
    """推荐下一个学习概念

    Args:
        current_concept: 刚学完的概念
        mastery_scores: 所有概念的掌握度
        learning_style: 学习风格 (application_oriented | theory_deep | challenge_seeking)

    Returns: [(概念名, 推荐度, 推荐理由), ...]
    """
    # 读取当前概念的相关概念
    concept_file = None
    for cf in CONCEPTS_DIR.rglob(f"{current_concept}.md"):
        concept_file = cf
        break

    if not concept_file:
        return []

    related_concepts = []
    try:
        with open(concept_file, 'r', encoding='utf-8') as f:
            in_related = False
            for line in f:
                if "## 相关概念" in line:
                    in_related = True
                    continue
                if in_related:
                    if line.startswith("##"):
                        break
                    if "[[" in line:
                        concept = line.strip().split("[[")[1].split("]]")[0]
                        related_concepts.append(concept)
    except Exception as e:
        print(f"⚠️  读取相关概念失败: {e}")
        return []

    recommendations = []
    for concept in related_concepts:
        # 跳过已掌握的
        if mastery_scores.get(concept, 0) >= 0.7:
            continue

        # 计算推荐度
        score = 0.5  # 基础分
        reason_parts = []

        # 依赖关系：如果前置概念都掌握了，推荐度+0.3
        # TODO: 实现前置概念检查

        # 学习风格匹配
        if learning_style == "application_oriented":
            if "工程" in concept or "实践" in concept or "流水线" in concept:
                score += 0.2
                reason_parts.append("实践导向")
        elif learning_style == "theory_deep":
            if "机制" in concept or "原理" in concept or "理论" in concept:
                score += 0.2
                reason_parts.append("理论深度")

        reason = f"与 {current_concept} 直接相关"
        if reason_parts:
            reason += "，" + "、".join(reason_parts)

        recommendations.append((concept, score, reason))

    # 按推荐度排序
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations[:3]

def save_learning_session(concept_name: str, session_data: Dict):
    """保存学习会话数据"""
    session_dir = LEARNING_PROGRESS / "session_states"
    session_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_file = session_dir / f"{concept_name}_{timestamp}.json"

    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

def main():
    """测试用例"""
    print("🧪 测试自适应学习引擎\n")

    # 模拟已有掌握度
    prior_knowledge = {
        "context-engineering": 0.7,
        "架构约束的确定性执行": 0.5
    }

    # 1. 理解边缘探测
    print("=== Step 1: 理解边缘探测 ===")
    baseline = detect_baseline("harness", prior_knowledge)
    print(f"基线水平: {baseline['baseline_level']:.1%}")
    print(f"已掌握前置: {baseline['related_mastered']}\n")

    # 2. 调整教学深度
    print("=== Step 2: 调整教学深度 ===")
    teaching = adjust_teaching_depth(baseline, "harness")
    print(f"教学策略: {teaching}\n")

    # 3. 掌握度评估
    print("=== Step 3: 掌握度评估 ===")
    mock_responses = [
        "harness 就是用来限制 agent 行为的工具集，可以通过自定义 linter 和测试来确保输出质量",
        "如果错误率上升，我会先检查 harness 的验证规则是否还适用，然后看是不是上下文配置变了"
    ]
    mastery = evaluate_mastery("harness", mock_responses)
    print(f"评估掌握度: {mastery:.1%}\n")

    # 4. 路径推荐
    print("=== Step 4: 路径推荐 ===")
    prior_knowledge["harness"] = mastery
    recommendations = recommend_next_concepts("harness", prior_knowledge, "application_oriented")
    for i, (concept, score, reason) in enumerate(recommendations, 1):
        print(f"{i}. {concept} (推荐度: {score:.1%}) - {reason}")

if __name__ == "__main__":
    main()
