#!/usr/bin/env python3
"""
学习进度追踪系统 - 从用户反馈数据中恢复学习轨迹

功能：
1. 从 user-utterances.jsonl 提取学习记录
2. 建立概念掌握度时间线
3. 生成学习曲线数据
4. 识别学习模式和偏好
"""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
USER_FEEDBACK = PROJECT_ROOT / "user-feedback" / "user-utterances.jsonl"
LEARNING_PROGRESS = PROJECT_ROOT / ".learning-progress"
CONCEPTS_DIR = PROJECT_ROOT / "concepts"

def load_utterances() -> List[Dict]:
    """加载用户原话数据"""
    utterances = []
    with open(USER_FEEDBACK, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                utterances.append(json.loads(line))
    return utterances

def load_concept_names() -> List[str]:
    """加载所有概念名（从 concepts/ 目录）"""
    concept_files = list(CONCEPTS_DIR.rglob("*.md"))
    concepts = []
    for f in concept_files:
        if f.name != "INDEX.md":
            # 去掉 .md 后缀作为概念名
            concept_name = f.stem
            concepts.append(concept_name)
    return concepts

def extract_learning_timeline(utterances: List[Dict]) -> Dict:
    """提取学习时间线

    返回: {
        "courses": {课程名: {课时: {反馈类型, 内容, 日期}}},
        "concepts_mentioned": {概念名: [提及次数, 首次日期, 最近日期]},
        "feedback_signals": {日期: [信号类型列表]}
    }
    """
    timeline = {
        "courses": defaultdict(dict),
        "concepts_mentioned": defaultdict(lambda: [0, None, None]),
        "feedback_signals": defaultdict(list)
    }

    # 加载概念列表
    concept_names = load_concept_names()
    print(f"   - 加载了 {len(concept_names)} 个概念")

    for utt in utterances:
        course = utt.get("course", "")
        lesson = utt.get("lesson", "")
        date = utt.get("snapshot_date", "")
        evidence_type = utt.get("evidence_type", "")
        verbatim = utt.get("verbatim", "")
        content_roles = utt.get("content_roles", [])

        # 跳过空日期的记录（无法建立时间线）
        if not date:
            continue

        if course and lesson:
            # 记录课程学习轨迹
            timeline["courses"][course][lesson] = {
                "evidence_type": evidence_type,
                "content": verbatim[:200],  # 摘要
                "date": date,
                "roles": content_roles
            }

        # 提取提及的概念（模糊匹配）
        verbatim_lower = verbatim.lower()
        for concept in concept_names:
            concept_lower = concept.lower()
            if concept_lower in verbatim_lower or concept in verbatim:
                count, first_date, last_date = timeline["concepts_mentioned"][concept]
                timeline["concepts_mentioned"][concept][0] = count + 1

                # 更新首次和最近日期
                if first_date is None or date < first_date:
                    timeline["concepts_mentioned"][concept][1] = date
                if last_date is None or date > last_date:
                    timeline["concepts_mentioned"][concept][2] = date

        # 识别反馈信号类型
        signal_type = classify_feedback_signal(verbatim, content_roles)
        if signal_type != "low_engagement":
            timeline["feedback_signals"][date].append({
                "type": signal_type,
                "verbatim": verbatim[:100],
                "course": course,
                "lesson": lesson
            })

    return timeline

def calculate_mastery_scores(timeline: Dict, utterances: List[Dict]) -> Dict[str, Dict]:
    """计算概念掌握度

    基于反馈信号类型计算掌握度：
    - 深度理解型反馈 -> 高掌握度 (0.8-1.0)
    - 判断标准型反馈 -> 高掌握度 (0.8-1.0)
    - 应用导向型反馈 -> 中高掌握度 (0.6-0.8)
    - 主动挑战型反馈 -> 中高掌握度 (0.6-0.8)
    - 知识缺口型反馈 -> 低掌握度 (0.2-0.4)
    """
    mastery = {}
    concept_names = list(timeline["concepts_mentioned"].keys())

    # 信号类型到掌握度的映射
    signal_to_score = {
        "deep_understanding": 0.9,
        "judgment_criteria": 0.85,
        "application_oriented": 0.7,
        "active_challenge": 0.7,
        "knowledge_gap": 0.3,
        "low_engagement": 0.0
    }

    # 为每个概念计算掌握度
    for concept in concept_names:
        concept_lower = concept.lower()
        concept_signals = []

        # 找出提及该概念的所有 utterance 及其信号类型
        for utt in utterances:
            verbatim = utt.get("verbatim", "")
            date = utt.get("snapshot_date", "")

            # 跳过空日期
            if not date:
                continue

            verbatim_lower = verbatim.lower()

            if concept_lower in verbatim_lower or concept in verbatim:
                signal_type = classify_feedback_signal(verbatim, utt.get("content_roles", []))
                if signal_type != "low_engagement":
                    concept_signals.append({
                        "type": signal_type,
                        "date": date,
                        "score": signal_to_score.get(signal_type, 0.5)
                    })

        # 取最近一次反馈信号的掌握度（体现最新理解水平）
        if concept_signals:
            concept_signals.sort(key=lambda x: x["date"], reverse=True)
            latest_signal = concept_signals[0]

            count, first_date, last_date = timeline["concepts_mentioned"][concept]
            mastery[concept] = {
                "score": latest_signal["score"],
                "signal_type": latest_signal["type"],
                "mention_count": count,
                "first_date": first_date,
                "last_date": last_date,
                "total_signals": len(concept_signals)
            }

    return mastery

def classify_feedback_signal(verbatim: str, content_roles: List[str]) -> str:
    """分类反馈信号

    返回: "deep_understanding" | "active_challenge" | "application_oriented"
           | "knowledge_gap" | "judgment_criteria" | "low_engagement"
    """
    # 低参与型：长度过短
    if len(verbatim) < 50:
        return "low_engagement"

    # 深度理解型特征
    deep_keywords = ["比喻", "就像", "其实就是", "可以理解为", "本质上", "类似于", "相当于"]
    if any(kw in verbatim for kw in deep_keywords):
        return "deep_understanding"

    # 主动挑战型特征
    challenge_keywords = ["推翻", "质疑", "证据", "为什么", "找文章", "反驳", "不对", "有问题"]
    if any(kw in verbatim for kw in challenge_keywords):
        return "active_challenge"

    # 应用导向型特征
    application_keywords = ["工作流", "实际", "如何使用", "可以用于", "场景", "怎么用", "用来"]
    if any(kw in verbatim for kw in application_keywords):
        return "application_oriented"

    # 知识缺口型特征
    gap_keywords = ["不懂", "不理解", "不知道", "没搞清楚", "不明白", "没理解"]
    if any(kw in verbatim for kw in gap_keywords):
        return "knowledge_gap"

    # 判断标准型特征
    criteria_keywords = ["筛选", "评估", "标准", "入选", "判断", "选择", "识别"]
    if any(kw in verbatim for kw in criteria_keywords):
        return "judgment_criteria"

    # 基于 content_roles 判断
    if "judgment" in content_roles:
        return "judgment_criteria"
    if "question" in content_roles:
        return "active_challenge"
    if "viewpoint" in content_roles and len(verbatim) > 150:
        return "deep_understanding"
    if "example" in content_roles:
        return "application_oriented"

    return "low_engagement"

def generate_learning_curve(timeline: Dict, mastery: Dict) -> Dict:
    """生成学习曲线数据

    返回: {
        "dates": [日期列表],
        "total_concepts": [累计概念数],
        "mastery_avg": [平均掌握度],
        "daily_signals": [每日反馈信号数]
    }
    """
    curve = {
        "dates": [],
        "total_concepts": [],
        "mastery_avg": [],
        "daily_signals": []
    }

    # 收集所有非空日期并排序
    all_dates = set()
    for concept_info in mastery.values():
        if concept_info["first_date"]:
            all_dates.add(concept_info["first_date"])
        if concept_info["last_date"]:
            all_dates.add(concept_info["last_date"])

    for date in timeline["feedback_signals"].keys():
        if date:  # 跳过空日期
            all_dates.add(date)

    sorted_dates = sorted(list(all_dates))

    # 按日期累计计算
    cumulative_concepts = set()
    for date in sorted_dates:
        # 累计到该日期的概念数
        for concept, info in mastery.items():
            if info["first_date"] and info["first_date"] <= date:
                cumulative_concepts.add(concept)

        # 计算当日平均掌握度（所有已学概念）
        if cumulative_concepts:
            scores = [mastery[c]["score"] for c in cumulative_concepts if c in mastery]
            avg_score = sum(scores) / len(scores) if scores else 0.0
        else:
            avg_score = 0.0

        # 当日反馈信号数
        signals_count = len(timeline["feedback_signals"].get(date, []))

        curve["dates"].append(date)
        curve["total_concepts"].append(len(cumulative_concepts))
        curve["mastery_avg"].append(round(avg_score, 3))
        curve["daily_signals"].append(signals_count)

    return curve

def save_progress_data(timeline: Dict, mastery: Dict, curve: Dict):
    """保存学习进度数据"""
    LEARNING_PROGRESS.mkdir(exist_ok=True)

    # 保存时间线
    with open(LEARNING_PROGRESS / "timeline.json", 'w', encoding='utf-8') as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)

    # 保存掌握度
    with open(LEARNING_PROGRESS / "mastery.json", 'w', encoding='utf-8') as f:
        json.dump(mastery, f, ensure_ascii=False, indent=2)

    # 保存学习曲线
    with open(LEARNING_PROGRESS / "learning-curve.json", 'w', encoding='utf-8') as f:
        json.dump(curve, f, ensure_ascii=False, indent=2)

    print(f"✅ 学习进度数据已保存到 {LEARNING_PROGRESS}/")

def main():
    """主流程"""
    print("📊 开始分析学习进度...")

    # 1. 加载用户原话数据
    print("1/4 加载 user-utterances.jsonl...")
    utterances = load_utterances()
    print(f"   - 加载了 {len(utterances)} 条用户原话")

    # 2. 提取学习时间线
    print("2/4 提取学习时间线...")
    timeline = extract_learning_timeline(utterances)
    print(f"   - 识别了 {len(timeline['courses'])} 个课程")
    print(f"   - 识别了 {len(timeline['concepts_mentioned'])} 个概念提及")
    print(f"   - 收集了 {sum(len(v) for v in timeline['feedback_signals'].values())} 个反馈信号")

    # 3. 计算概念掌握度
    print("3/4 计算概念掌握度...")
    mastery = calculate_mastery_scores(timeline, utterances)
    print(f"   - 计算了 {len(mastery)} 个概念的掌握度")

    if mastery:
        avg_mastery = sum(m["score"] for m in mastery.values()) / len(mastery)
        print(f"   - 平均掌握度: {avg_mastery:.2f}")

    # 4. 生成学习曲线
    print("4/4 生成学习曲线...")
    curve = generate_learning_curve(timeline, mastery)
    print(f"   - 生成了 {len(curve['dates'])} 个时间点的学习曲线")

    # 保存结果
    save_progress_data(timeline, mastery, curve)

    # 输出统计摘要
    print("\n" + "="*60)
    print("📈 学习进度统计摘要")
    print("="*60)

    print(f"\n课程学习:")
    for course, lessons in list(timeline['courses'].items())[:5]:
        print(f"  • {course}: {len(lessons)} 课时")

    if mastery:
        print(f"\n掌握度最高的 5 个概念:")
        top_mastery = sorted(mastery.items(), key=lambda x: x[1]["score"], reverse=True)[:5]
        for concept, info in top_mastery:
            print(f"  • {concept}: {info['score']:.2f} ({info['signal_type']})")

        print(f"\n提及最频繁的 5 个概念:")
        top_mentions = sorted(mastery.items(), key=lambda x: x[1]["mention_count"], reverse=True)[:5]
        for concept, info in top_mentions:
            print(f"  • {concept}: {info['mention_count']} 次提及")

    print(f"\n生成的文件:")
    print(f"  • {LEARNING_PROGRESS / 'timeline.json'}")
    print(f"  • {LEARNING_PROGRESS / 'mastery.json'}")
    print(f"  • {LEARNING_PROGRESS / 'learning-curve.json'}")

    print("\n✨ 完成！学习进度追踪数据已恢复")

if __name__ == "__main__":
    main()
