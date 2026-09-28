#!/usr/bin/env python3
"""基于规则的概念关联工具

使用本地算法分析概念文件，生成相关概念列表，并添加"## 相关概念"部分。
不依赖外部 API，完全本地运行。
"""
import re
from pathlib import Path
from typing import List, Tuple, Dict, Set
from collections import Counter

# 配置
DACAPO_ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = DACAPO_ROOT / "concepts"
DRY_RUN = False  # 设置为 True 时只打印，不写入文件
MAX_LINKS = 5    # 每个概念最多推荐的关联数

def get_all_concept_names() -> List[str]:
    """获取所有概念名称"""
    files = list(CONCEPT_DIR.glob("*.md"))
    return sorted([f.stem for f in files])

def read_concept_file(filepath: Path) -> Tuple[str, str, bool, dict]:
    """读取概念文件

    Returns:
        (frontmatter, content, has_related_section, metadata)
    """
    text = filepath.read_text(encoding="utf-8")

    # 检查是否已有"相关概念"部分
    has_related = bool(re.search(r'^##\s*相关概念', text, re.MULTILINE))

    # 分离 frontmatter 和内容
    metadata = {}
    parts = text.split('---', 2)
    if len(parts) >= 3 and text.startswith('---'):
        frontmatter = f"---{parts[1]}---"
        content = parts[2].strip()

        # 解析 frontmatter
        for line in parts[1].split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
    else:
        frontmatter = ""
        content = text.strip()

    return frontmatter, content, has_related, metadata

def extract_existing_links(content: str) -> List[str]:
    """提取已有的概念链接"""
    matches = re.findall(r'\[\[([^\]|#]+)', content)
    return [m.strip().replace('.md', '') for m in matches]

def extract_keywords(text: str) -> Set[str]:
    """提取文本中的关键词"""
    # 移除 markdown 语法
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # 移除链接
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)  # 移除 WikiLink
    text = re.sub(r'[#*`]', '', text)  # 移除格式符号

    # 提取中文词组和英文单词
    chinese = set(re.findall(r'[一-龥]{2,}', text))
    english = set(re.findall(r'\b[A-Za-z]{3,}\b', text.lower()))

    return chinese | english

def calculate_similarity(text1: str, text2: str, keywords1: Set[str], keywords2: Set[str]) -> float:
    """计算两个概念的相似度（0-1）"""
    if not keywords1 or not keywords2:
        return 0.0

    # 关键词重叠度
    overlap = len(keywords1 & keywords2)
    union = len(keywords1 | keywords2)
    keyword_score = overlap / union if union > 0 else 0

    # 文本包含关系（一个概念名出现在另一个概念内容中）
    name_mention = 0
    if any(kw in text2.lower() for kw in keywords1):
        name_mention += 0.3
    if any(kw in text1.lower() for kw in keywords2):
        name_mention += 0.3

    return min(1.0, keyword_score * 0.7 + name_mention)

def find_related_concepts_by_rules(
    concept_name: str,
    content: str,
    metadata: dict,
    all_concepts: Dict[str, Tuple[str, dict, Set[str]]]
) -> List[Tuple[str, float, str]]:
    """使用规则引擎找出相关概念

    Returns:
        List of (concept_name, score, reason)
    """
    results = []
    keywords = extract_keywords(content)

    # 提取已有的显式链接
    existing_links = extract_existing_links(content)

    for other_name, (other_content, other_metadata, other_keywords) in all_concepts.items():
        if other_name == concept_name:
            continue

        score = 0.0
        reasons = []

        # 规则 1: 已有显式链接（最高优先级）
        if other_name in existing_links:
            score += 1.0
            reasons.append("已有链接")

        # 规则 2: 同一课程（适用于 course 类型）
        if metadata.get('type') == 'course' and other_metadata.get('type') == 'course':
            same_course_path = metadata.get('course_path', '').split('/')[0] == \
                              other_metadata.get('course_path', '').split('/')[0]
            if same_course_path and metadata.get('course_path'):
                score += 0.8
                reasons.append("同一课程系列")

        # 规则 3: 概念名称包含关系
        if concept_name.lower() in other_name.lower() or other_name.lower() in concept_name.lower():
            score += 0.6
            reasons.append("名称相关")

        # 规则 4: 内容相似度
        similarity = calculate_similarity(content, other_content, keywords, other_keywords)
        if similarity > 0.2:
            score += similarity * 0.5
            reasons.append(f"内容相似({similarity:.2f})")

        # 规则 5: 标签重叠（如果有）
        if 'tags' in metadata and 'tags' in other_metadata:
            # 简单检查是否有共同标签
            if any(tag in str(other_metadata.get('tags', '')) for tag in str(metadata.get('tags', '')).split()):
                score += 0.4
                reasons.append("标签相关")

        # 规则 6: 引用了相同的文章
        concept_articles = set(re.findall(r'\[\[([^\]]+)\]\]', content))
        other_articles = set(re.findall(r'\[\[([^\]]+)\]\]', other_content))
        common_refs = concept_articles & other_articles
        if len(common_refs) > 0:
            score += 0.3 * min(1.0, len(common_refs) / 2)
            reasons.append(f"共同引用({len(common_refs)})")

        if score > 0.3:  # 阈值：只保留得分较高的
            results.append((other_name, score, '; '.join(reasons)))

    # 按得分排序
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:MAX_LINKS]

def add_related_section(filepath: Path, related_concepts: List[Tuple[str, float, str]]) -> bool:
    """在文件末尾添加"相关概念"部分"""

    if not related_concepts:
        return False

    text = filepath.read_text(encoding="utf-8")

    # 如果已有相关概念部分，跳过
    if re.search(r'^##\s*相关概念', text, re.MULTILINE):
        return False

    # 生成相关概念部分
    related_section = "\n\n## 相关概念\n\n"
    for concept, score, reason in related_concepts:
        related_section += f"- [[{concept}]]\n"

    new_content = text.rstrip() + related_section

    if DRY_RUN:
        print(f"  [DRY RUN] 将添加: {[c[0] for c in related_concepts]}")
        return True

    filepath.write_text(new_content, encoding="utf-8")
    return True

def process_all_concepts():
    """批量处理所有概念"""

    print(f"📚 开始处理概念关联（本地规则引擎）...")
    print(f"概念目录: {CONCEPT_DIR}")
    print(f"DRY_RUN: {DRY_RUN}")
    print()

    # 第一遍：加载所有概念
    print("🔍 加载所有概念...")
    all_concepts = {}
    files = sorted(CONCEPT_DIR.glob("*.md"))

    for filepath in files:
        concept_name = filepath.stem
        _, content, _, metadata = read_concept_file(filepath)
        keywords = extract_keywords(content)
        all_concepts[concept_name] = (content, metadata, keywords)

    print(f"✅ 已加载 {len(all_concepts)} 个概念\n")

    # 第二遍：分析关联
    stats = {
        'total': len(files),
        'processed': 0,
        'skipped': 0,
        'updated': 0,
        'failed': 0
    }

    for i, filepath in enumerate(files, 1):
        concept_name = filepath.stem
        print(f"[{i}/{stats['total']}] {concept_name}")

        try:
            _, content, has_related, metadata = read_concept_file(filepath)

            if has_related:
                print(f"  ⏭️  已有相关概念部分，跳过")
                stats['skipped'] += 1
                continue

            # 提取已有链接（作为参考）
            existing_links = extract_existing_links(content)
            if existing_links:
                print(f"  📎 已有链接: {', '.join(existing_links[:3])}")

            # 使用规则引擎分析
            print(f"  🔍 分析关联...")
            related = find_related_concepts_by_rules(
                concept_name, content, metadata, all_concepts
            )

            if related:
                print(f"  ✨ 推荐 ({len(related)}):")
                for concept, score, reason in related:
                    print(f"     - {concept} (得分: {score:.2f}, 原因: {reason})")

                if add_related_section(filepath, related):
                    stats['updated'] += 1
                    print(f"  ✅ 已添加")
                else:
                    stats['skipped'] += 1
            else:
                print(f"  ⚠️  未找到相关概念")
                stats['skipped'] += 1

            stats['processed'] += 1

        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            stats['failed'] += 1
            import traceback
            traceback.print_exc()

        print()

    # 统计报告
    print("=" * 60)
    print("📊 处理完成统计")
    print("=" * 60)
    print(f"总概念数: {stats['total']}")
    print(f"已处理:   {stats['processed']}")
    print(f"已更新:   {stats['updated']}")
    print(f"已跳过:   {stats['skipped']}")
    print(f"失败:     {stats['failed']}")
    print()

    if not DRY_RUN and stats['updated'] > 0:
        print("✅ 下一步: 运行 generate_concept_graph.py 重新生成图谱")
    elif DRY_RUN:
        print("ℹ️  这是 DRY_RUN 模式，没有实际修改文件")
        print("   设置 DRY_RUN = False 以实际写入")

if __name__ == "__main__":
    process_all_concepts()
