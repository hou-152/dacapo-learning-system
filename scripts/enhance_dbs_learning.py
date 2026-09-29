#!/usr/bin/env python3
"""
dbs-learning 增强器 - 在文章生成后自动添加 DaCapo 即时反馈

功能：
1. 监听 dbs-learning 生成的新文章
2. 分析用户反馈区的内容
3. 提取反馈信号类型和掌握度
4. 调用 instant_feedback.py 生成可视化反馈
5. 追加到文章末尾
"""
import sys
import re
from pathlib import Path
from datetime import datetime
import json

# 添加 scripts 到路径
sys.path.insert(0, str(Path(__file__).parent))

from instant_feedback import (
    load_concept_relations,
    load_mastery_scores,
    calculate_unlocked_concepts,
    generate_relation_network_mermaid,
    calculate_compound_index
)

def extract_concepts_from_text(text: str, all_concepts: list) -> list:
    """从文本中提取提到的概念"""
    mentioned = []
    text_lower = text.lower()
    
    for concept in all_concepts:
        concept_lower = concept.lower()
        if concept_lower in text_lower or concept in text:
            mentioned.append(concept)
    
    return mentioned

def classify_feedback_signal(feedback_text: str) -> tuple:
    """分类反馈信号
    
    返回: (signal_type, mastery_score)
    """
    if len(feedback_text) < 50:
        return "low_engagement", 0.0
    
    # 深度理解型：用自己的话重新表达概念
    deep_keywords = ["就像", "类似", "相当于", "可以理解为", "本质上", "其实就是", "=", "≈"]
    if any(kw in feedback_text for kw in deep_keywords):
        return "deep_understanding", 0.9
    
    # 判断标准型：提出判断框架或标准
    criteria_keywords = ["判断", "标准", "怎么区分", "边界", "条件", "如果", "则"]
    if any(kw in feedback_text for kw in criteria_keywords):
        return "judgment_criteria", 0.85
    
    # 应用导向型：连接到实际场景
    application_keywords = ["实际", "例子", "场景", "我遇到", "我见过", "可以用来"]
    if any(kw in feedback_text for kw in application_keywords):
        return "application_oriented", 0.7
    
    # 主动挑战型：提出疑问或反例
    challenge_keywords = ["为什么", "但是", "不对", "疑问", "不理解", "有问题"]
    if any(kw in feedback_text for kw in challenge_keywords):
        return "active_challenge", 0.7
    
    # 知识缺口型：明确表达不懂
    gap_keywords = ["不懂", "不理解", "没搞清楚", "不明白", "看不懂"]
    if any(kw in feedback_text for kw in gap_keywords):
        return "knowledge_gap", 0.3
    
    return "low_engagement", 0.5

def extract_feedback_from_article(article_path: Path) -> str:
    """从文章中提取用户反馈"""
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找「学习反馈」区域
    feedback_section = re.search(r'## 学习反馈\n\n.*?请写在这行下面：\n\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    
    if feedback_section:
        feedback_text = feedback_section.group(1).strip()
        # 过滤掉模板行
        template_lines = [
            "你可以写：",
            "1. 哪里看懂了？",
            "2. 哪里没看懂？",
            "3. 哪个地方想展开？",
            "4. 这个主题和你的真实问题有什么关系？"
        ]
        for line in template_lines:
            feedback_text = feedback_text.replace(line, "")
        
        return feedback_text.strip()
    
    return ""

def generate_enhanced_feedback(article_path: Path, concepts_mentioned: list) -> str:
    """生成增强的即时反馈
    
    返回: Markdown 格式的反馈内容
    """
    # 提取用户反馈
    feedback_text = extract_feedback_from_article(article_path)
    
    if not feedback_text:
        return "\n\n---\n\n## 🤖 DaCapo 即时反馈\n\n暂无反馈，期待你的学习心得！\n"
    
    # 分析反馈信号
    signal_type, mastery_score = classify_feedback_signal(feedback_text)
    
    signal_names = {
        "deep_understanding": "深度理解型 🌟",
        "judgment_criteria": "判断标准型 🎯",
        "application_oriented": "应用导向型 🔧",
        "active_challenge": "主动挑战型 💪",
        "knowledge_gap": "知识缺口型 📚",
        "low_engagement": "低参与型"
    }
    
    # 加载当前掌握度数据
    relations = load_concept_relations()
    mastery = load_mastery_scores()
    
    # 更新提到的概念的掌握度
    newly_mastered = []
    for concept in concepts_mentioned:
        old_score = mastery.get(concept, 0)
        if isinstance(old_score, dict):
            old_score = old_score.get("score", 0)
        
        mastery[concept] = mastery_score
        
        if old_score < 0.6 and mastery_score >= 0.6:
            newly_mastered.append(concept)
    
    # 计算统计数据
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
    
    # 生成反馈
    feedback = [
        "\n\n---",
        "",
        "## 🤖 DaCapo 即时反馈",
        "",
        "### 📊 反馈分析",
        "",
        f"**反馈类型**: {signal_names.get(signal_type, signal_type)}",
        f"**概念掌握度**: {mastery_score:.0%}",
        "",
    ]
    
    if signal_type == "deep_understanding":
        feedback.append("✨ 你用自己的话重新表达了概念，说明理解深入！")
    elif signal_type == "application_oriented":
        feedback.append("🔧 你连接到了实际场景，这是学以致用的关键！")
    elif signal_type == "judgment_criteria":
        feedback.append("🎯 你提出了判断标准，建立了概念边界！")
    elif signal_type == "active_challenge":
        feedback.append("💪 你提出了挑战性问题，这是深度学习的标志！")
    elif signal_type == "knowledge_gap":
        feedback.append("📚 你明确了不懂的地方，这是学习的起点！")
    
    feedback.extend([
        "",
        "---",
        "",
        "### 🌱 学习进度",
        "",
        f"- **已掌握概念**: {learned_count} 个",
        f"- **平均掌握度**: {avg_mastery:.1%}",
        f"- **知识网络**: {total_connections} 条关联",
        f"- **复利指数**: {compound_index:.1f}",
        ""
    ])
    
    if newly_mastered:
        feedback.extend([
            "### 🎉 新掌握的概念",
            ""
        ])
        for concept in newly_mastered:
            feedback.append(f"- ✅ **{concept}** (掌握度: {mastery_score:.0%})")
        feedback.append("")
    
    # 生成概念关联网络（只为主要概念生成）
    if concepts_mentioned:
        main_concept = concepts_mentioned[0]
        feedback.extend([
            "---",
            "",
            "### 🕸️ 概念关联网络",
            "",
            generate_relation_network_mermaid(main_concept, relations, mastery, depth=1),
            ""
        ])
    
    feedback.extend([
        "---",
        "",
        f"📅 反馈生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        ""
    ])
    
    return "\n".join(feedback)

def enhance_article(article_path: Path, concepts_mentioned: list = None):
    """为文章添加 DaCapo 即时反馈
    
    Args:
        article_path: 文章路径
        concepts_mentioned: 文章中提到的概念列表（可选，会自动提取）
    """
    article_path = Path(article_path)
    
    if not article_path.exists():
        print(f"❌ 文章不存在: {article_path}")
        return
    
    # 读取文章内容
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有 DaCapo 反馈
    if "## 🤖 DaCapo 即时反馈" in content:
        print(f"⚠️  文章已经包含 DaCapo 反馈，跳过")
        return
    
    # 自动提取概念（如果未提供）
    if concepts_mentioned is None:
        from instant_feedback import load_concept_relations
        relations = load_concept_relations()
        all_concepts = list(relations.keys())
        concepts_mentioned = extract_concepts_from_text(content, all_concepts)
    
    # 生成即时反馈
    enhanced_feedback = generate_enhanced_feedback(article_path, concepts_mentioned)
    
    # 追加到文章末尾
    with open(article_path, 'a', encoding='utf-8') as f:
        f.write(enhanced_feedback)
    
    print(f"✅ 已为文章添加 DaCapo 即时反馈: {article_path.name}")
    print(f"   提到的概念: {', '.join(concepts_mentioned) if concepts_mentioned else '无'}")

def main():
    """命令行入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python enhance_dbs_learning.py <文章路径> [概念1 概念2 ...]")
        print()
        print("示例:")
        print("  python enhance_dbs_learning.py ~/Documents/dbskill-learning/社会学七书共读/03.md")
        print("  python enhance_dbs_learning.py ~/Documents/dbskill-learning/社会学七书共读/04.md 差序格局 礼治秩序")
        sys.exit(1)
    
    article_path = Path(sys.argv[1]).expanduser()
    concepts = sys.argv[2:] if len(sys.argv) > 2 else None
    
    enhance_article(article_path, concepts)

if __name__ == "__main__":
    main()
