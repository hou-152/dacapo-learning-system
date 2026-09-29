#!/usr/bin/env python3
"""
进度追踪器 - 生成实时进度仪表盘

功能：
1. 读取 .learning-progress/ 数据
2. 生成今日学习摘要
3. 生成本周进展统计
4. 计算掌握度分布
5. 推荐下一步
"""
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
LEARNING_PROGRESS = PROJECT_ROOT / ".learning-progress"

def load_mastery_scores() -> Dict[str, float]:
    """加载概念掌握度"""
    mastery_file = LEARNING_PROGRESS / "mastery.json"
    if not mastery_file.exists():
        return {}

    with open(mastery_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_timeline() -> Dict:
    """加载学习时间线"""
    timeline_file = LEARNING_PROGRESS / "timeline.json"
    if not timeline_file.exists():
        return {"courses": {}, "concepts_mentioned": {}, "feedback_signals": {}}

    with open(timeline_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_today_learning() -> List[str]:
    """获取今日学习的概念"""
    # 读取今天的 session 文件
    session_dir = LEARNING_PROGRESS / "session_states"
    if not session_dir.exists():
        return []

    today = datetime.now().strftime("%Y%m%d")
    today_sessions = list(session_dir.glob(f"*_{today}_*.json"))

    concepts = []
    for session_file in today_sessions:
        concept_name = session_file.stem.split('_')[0]
        concepts.append(concept_name)

    return concepts

def get_weekly_stats(timeline: Dict) -> Dict:
    """获取本周学习统计"""
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # 统计本周新增概念
    concepts_mentioned = timeline.get("concepts_mentioned", {})
    new_concepts = []
    review_concepts = []

    for concept, data in concepts_mentioned.items():
        if isinstance(data, list) and len(data) >= 3:
            first_date = data[1]
            if first_date and first_date >= week_ago:
                new_concepts.append(concept)
            elif first_date and first_date < week_ago:
                last_date = data[2]
                if last_date and last_date >= week_ago:
                    review_concepts.append(concept)

    return {
        "new_concepts": len(new_concepts),
        "review_concepts": len(review_concepts),
        "total_learning_hours": 0.0,  # TODO: 从 session 时长计算
        "network_growth": 0  # TODO: 从图谱变化计算
    }

def calculate_mastery_distribution(mastery: Dict[str, float]) -> Dict:
    """计算掌握度分布"""
    distribution = {
        "excellent": [],  # >= 0.8
        "good": [],       # 0.6 - 0.8
        "learning": [],   # 0.4 - 0.6
        "weak": []        # < 0.4
    }

    for concept, data in mastery.items():
        # 处理新格式：{"score": 0.7, "signal_type": "..."}
        if isinstance(data, dict):
            score = data.get("score", 0)
        else:
            score = data

        if score >= 0.8:
            distribution["excellent"].append(concept)
        elif score >= 0.6:
            distribution["good"].append(concept)
        elif score >= 0.4:
            distribution["learning"].append(concept)
        else:
            distribution["weak"].append(concept)

    return distribution

def calculate_category_mastery(mastery: Dict[str, float]) -> Dict[str, float]:
    """按类别计算掌握度"""
    # 简单启发式：根据概念名关键词分类
    categories = defaultdict(list)

    for concept, data in mastery.items():
        # 处理新格式
        if isinstance(data, dict):
            score = data.get("score", 0)
        else:
            score = data

        if any(kw in concept for kw in ["工程", "流水线", "harness", "验证"]):
            categories["工程实践"].append(score)
        elif any(kw in concept for kw in ["机制", "原理", "理论", "拓扑"]):
            categories["理论基础"].append(score)
        elif any(kw in concept for kw in ["context", "记忆", "理解"]):
            categories["认知能力"].append(score)
        else:
            categories["其他"].append(score)

    # 计算平均掌握度
    category_avg = {}
    for cat, scores in categories.items():
        if scores:
            category_avg[cat] = sum(scores) / len(scores)

    return category_avg

def generate_progress_bar(value: float, max_width: int = 20) -> str:
    """生成进度条"""
    filled = int(value * max_width)
    bar = "█" * filled + "░" * (max_width - filled)
    return f"[{bar}] {value:.0%}"

def generate_dashboard() -> str:
    """生成实时进度仪表盘"""
    mastery = load_mastery_scores()
    timeline = load_timeline()

    # 今日学习
    today_concepts = get_today_learning()

    # 本周统计
    weekly = get_weekly_stats(timeline)

    # 掌握度分布
    distribution = calculate_mastery_distribution(mastery)

    # 类别掌握度
    category_mastery = calculate_category_mastery(mastery)

    # 生成 Markdown
    lines = [
        "# 📊 学习进度仪表盘",
        "",
        f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## 今日学习",
        ""
    ]

    if today_concepts:
        for concept in today_concepts:
            concept_data = mastery.get(concept, 0)
            if isinstance(concept_data, dict):
                score = concept_data.get("score", 0)
            else:
                score = concept_data
            lines.append(f"- ✅ **{concept}** ({score:.0%})")
    else:
        lines.append("- 今天还没开始学习")

    lines.extend([
        "",
        "---",
        "",
        "## 本周进展",
        "",
        f"- **新增概念**: {weekly['new_concepts']} 个",
        f"- **复习概念**: {weekly['review_concepts']} 个",
        f"- **学习时长**: {weekly['total_learning_hours']:.1f} 小时",
        f"- **网络增长**: {weekly['network_growth']} 条关联",
        "",
        "---",
        "",
        "## 掌握度分布",
        ""
    ])

    total_concepts = len(mastery)
    if total_concepts > 0:
        lines.append(f"**总计**: {total_concepts} 个概念")
        lines.append("")
        lines.append(f"- 🟢 优秀 (≥80%): {len(distribution['excellent'])} 个")
        lines.append(f"- 🟡 良好 (60-80%): {len(distribution['good'])} 个")
        lines.append(f"- 🟠 学习中 (40-60%): {len(distribution['learning'])} 个")
        lines.append(f"- 🔴 薄弱 (<40%): {len(distribution['weak'])} 个")
    else:
        lines.append("暂无数据")

    lines.extend([
        "",
        "---",
        "",
        "## 分类掌握度",
        ""
    ])

    if category_mastery:
        for category, avg_score in sorted(category_mastery.items(), key=lambda x: x[1], reverse=True):
            bar = generate_progress_bar(avg_score, 15)
            lines.append(f"- **{category}**: {bar}")
    else:
        lines.append("暂无数据")

    lines.extend([
        "",
        "---",
        "",
        "## 推荐下一步",
        ""
    ])

    # 简单推荐：找掌握度最高的类别中未掌握的概念
    if category_mastery and mastery:
        best_category = max(category_mastery.items(), key=lambda x: x[1])[0]
        lines.append(f"基于你在「{best_category}」类别的优势，推荐继续深入该领域")
    else:
        lines.append("开始学习第一个概念吧！")

    return "\n".join(lines)

def main():
    """生成并输出仪表盘"""
    dashboard = generate_dashboard()

    # 保存到文件
    output_file = LEARNING_PROGRESS / "dashboard-realtime.md"
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(dashboard)

    print(dashboard)
    print(f"\n📁 仪表盘已保存到: {output_file}")

if __name__ == "__main__":
    main()
