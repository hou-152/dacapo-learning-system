#!/usr/bin/env python3
"""
完整学习流程演示 - 学习一个概念的完整体验

演示 5 步流程：
1. 理解边缘探测
2. 自适应教学
3. 即时反馈
4. 掌握度评估
5. 路径推荐
"""
import sys
from pathlib import Path

# 添加 scripts 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from adaptive_learning import (
    detect_baseline,
    adjust_teaching_depth,
    evaluate_mastery,
    recommend_next_concepts,
    save_learning_session
)
from instant_feedback import generate_instant_feedback
from progress_tracker import generate_dashboard
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
LEARNING_PROGRESS = PROJECT_ROOT / ".learning-progress"

def load_current_mastery():
    """加载当前掌握度"""
    mastery_file = LEARNING_PROGRESS / "mastery.json"
    if not mastery_file.exists():
        return {}

    with open(mastery_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 转换为简单格式 {概念名: 分数}
    mastery = {}
    for concept, info in data.items():
        if isinstance(info, dict):
            mastery[concept] = info.get("score", 0)
        else:
            mastery[concept] = info

    return mastery

def update_mastery(concept_name: str, new_score: float):
    """更新掌握度"""
    mastery_file = LEARNING_PROGRESS / "mastery.json"

    if mastery_file.exists():
        with open(mastery_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    # 更新或添加
    if concept_name in data and isinstance(data[concept_name], dict):
        data[concept_name]["score"] = new_score
        data[concept_name]["last_date"] = datetime.now().strftime("%Y-%m-%d")
    else:
        data[concept_name] = {
            "score": new_score,
            "signal_type": "deep_understanding",
            "mention_count": 1,
            "first_date": datetime.now().strftime("%Y-%m-%d"),
            "last_date": datetime.now().strftime("%Y-%m-%d"),
            "total_signals": 1
        }

    with open(mastery_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    """完整学习流程演示"""
    print("=" * 60)
    print("🎓 DaCapo 自适应学习系统 - 完整流程演示")
    print("=" * 60)
    print()

    # 选择概念
    if len(sys.argv) > 1:
        concept_name = sys.argv[1]
    else:
        concept_name = "Loop Engineering"

    print(f"📚 准备学习概念：{concept_name}\n")

    # 加载当前掌握度
    mastery = load_current_mastery()
    print(f"📊 当前已掌握 {len(mastery)} 个概念\n")

    # ===== Step 1: 理解边缘探测 =====
    print("─" * 60)
    print("Step 1: 理解边缘探测")
    print("─" * 60)
    baseline = detect_baseline(concept_name, mastery)
    print(f"基线水平: {baseline['baseline_level']:.0%}")
    print(f"已掌握前置概念: {baseline['related_mastered']}")
    print()

    # ===== Step 2: 自适应教学深度调整 =====
    print("─" * 60)
    print("Step 2: 自适应教学深度调整")
    print("─" * 60)
    teaching = adjust_teaching_depth(baseline, concept_name)
    print(f"跳过定义: {'是' if teaching['skip_definition'] else '否'}")
    print(f"教学重点: {teaching['focus_on']}")
    print(f"深度等级: {'⭐' * teaching['depth_level']}")
    print()

    # ===== Step 3: 即时反馈 =====
    print("─" * 60)
    print("Step 3: 即时反馈生成")
    print("─" * 60)
    print("生成关联网络、解锁状态、复利指数...\n")

    # 先更新掌握度（模拟学完）
    update_mastery(concept_name, 0.75)

    # 生成即时反馈
    feedback = generate_instant_feedback(concept_name)
    print(feedback[:500] + "...\n")  # 只显示前 500 字符

    # ===== Step 4: 掌握度评估 =====
    print("─" * 60)
    print("Step 4: 掌握度评估（模拟）")
    print("─" * 60)
    mock_responses = [
        f"{concept_name} 的核心是判断力介入，和简单循环不同，它需要在每个节点做决策",
        "在实际应用中，我会在关键检查点设置 yes/no 判断，而不是让所有任务无脑执行"
    ]
    mastery_score = evaluate_mastery(concept_name, mock_responses)
    print(f"评估掌握度: {mastery_score:.0%}")
    print()

    # 更新实际掌握度
    update_mastery(concept_name, mastery_score)

    # ===== Step 5: 路径推荐 =====
    print("─" * 60)
    print("Step 5: 路径推荐")
    print("─" * 60)
    mastery[concept_name] = mastery_score
    recommendations = recommend_next_concepts(concept_name, mastery, "application_oriented")

    if recommendations:
        print("推荐下一步学习：\n")
        for i, (concept, score, reason) in enumerate(recommendations, 1):
            print(f"{i}. {concept}")
            print(f"   推荐度: {score:.0%}")
            print(f"   理由: {reason}\n")
    else:
        print("暂无推荐（可能相关概念已全部掌握）\n")

    # ===== 保存会话 =====
    session_data = {
        "concept": concept_name,
        "timestamp": datetime.now().isoformat(),
        "baseline": baseline,
        "teaching_strategy": teaching,
        "mastery_score": mastery_score,
        "recommendations": [
            {"concept": c, "score": s, "reason": r}
            for c, s, r in recommendations
        ]
    }
    save_learning_session(concept_name, session_data)
    print("✅ 学习会话已保存\n")

    # ===== 更新仪表盘 =====
    print("─" * 60)
    print("生成实时进度仪表盘")
    print("─" * 60)
    dashboard = generate_dashboard()
    print("\n查看完整仪表盘：.learning-progress/dashboard-realtime.md\n")

    print("=" * 60)
    print("🎉 完整学习流程演示完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
