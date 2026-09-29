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

    for utt in utterances:
        course = utt.get("course", "")
        lesson = utt.get("lesson", "")
        date = utt.get("snapshot_date", "")
        evidence_type = utt.get("evidence_type", "")
        verbatim = utt.get("verbatim", "")
        content_roles = utt.get("content_roles", [])

        if course and lesson:
            # 记录课程学习轨迹
            timeline["courses"][course][lesson] = {
                "evidence_type": evidence_type,
                "content": verbatim[:200],  # 摘要
                "date": date,
                "roles": content_roles
            }

        # TODO: 提取提及的概念（需要概念列表）
        # TODO: 识别反馈信号类型（深度理解/主动挑战/应用导向/知识缺口/判断标准）

    return timeline

def calculate_mastery_scores(timeline: Dict) -> Dict[str, float]:
    """计算概念掌握度

    基于反馈信号类型计算掌握度：
    - 深度理解型反馈 -> 高掌握度 (0.8-1.0)
    - 应用导向型反馈 -> 中高掌握度 (0.6-0.8)
    - 主动挑战型反馈 -> 中等掌握度 (0.5-0.7)
    - 知识缺口型反馈 -> 低掌握度 (0.2-0.4)
    """
    mastery = {}

    # TODO: 实现掌握度计算逻辑
    # 1. 识别反馈信号类型（基于关键词、长度、内容角色）
    # 2. 提取提及的概念
    # 3. 根据反馈类型和频次计算掌握度

    return mastery

def classify_feedback_signal(verbatim: str, content_roles: List[str]) -> str:
    """分类反馈信号

    返回: "deep_understanding" | "active_challenge" | "application_oriented"
           | "knowledge_gap" | "judgment_criteria" | "low_engagement"
    """
    # 深度理解型特征
    deep_keywords = ["比喻", "就像", "其实就是", "可以理解为", "本质上"]

    # 主动挑战型特征
    challenge_keywords = ["推翻", "质疑", "证据", "为什么", "找文章"]

    # 应用导向型特征
    application_keywords = ["工作流", "实际", "如何使用", "可以用于", "场景"]

    # 知识缺口型特征
    gap_keywords = ["不懂", "不理解", "不知道", "没搞清楚"]

    # 判断标准型特征
    criteria_keywords = ["筛选", "评估", "标准", "入选", "判断"]

    # TODO: 实现分类逻辑

    if len(verbatim) < 50:
        return "low_engagement"

    return "unknown"

def generate_learning_curve(mastery_over_time: Dict) -> Dict:
    """生成学习曲线数据

    返回: {
        "dates": [日期列表],
        "total_concepts": [累计概念数],
        "mastery_avg": [平均掌握度],
        "connections": [累计关联数]
    }
    """
    curve = {
        "dates": [],
        "total_concepts": [],
        "mastery_avg": [],
        "connections": []
    }

    # TODO: 实现学习曲线生成

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

    # 3. 计算概念掌握度
    print("3/4 计算概念掌握度...")
    mastery = calculate_mastery_scores(timeline)
    print(f"   - 计算了 {len(mastery)} 个概念的掌握度")

    # 4. 生成学习曲线
    print("4/4 生成学习曲线...")
    curve = generate_learning_curve({})  # TODO: 传入正确参数

    # 保存结果
    save_progress_data(timeline, mastery, curve)

    print("\n✨ 完成！学习进度追踪数据已恢复")

if __name__ == "__main__":
    main()
