#!/usr/bin/env python3
"""
审核并清理不合理的概念关联
识别质量低的 WikiLink 并生成审核报告
"""
from pathlib import Path
import re
from collections import defaultdict

DACAPO_ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = DACAPO_ROOT / "concepts"
REPORT_FILE = DACAPO_ROOT / "CONCEPT-LINK-AUDIT.md"

# 不合理关联的启发式规则
SUSPICIOUS_PATTERNS = [
    # 规则1: 题库与非题库课程的关联
    {
        "name": "题库与普通课程混杂",
        "check": lambda src, tgt: (
            ("题库" in src or "考证" in src) and
            ("题库" not in tgt and "考证" not in tgt) and
            tgt not in ["2026气运-1"]  # 排除合理的特殊关联
        )
    },
    # 规则2: 名称完全不相关（没有共同关键词）
    {
        "name": "名称无共同关键词",
        "check": lambda src, tgt: len(extract_keywords(src) & extract_keywords(tgt)) == 0
    },
]

def extract_keywords(name: str) -> set:
    """提取概念名称中的关键词"""
    # 移除常见连接词和标点
    name = re.sub(r'[-_—\s]+', ' ', name)
    # 移除数字和特殊标记
    name = re.sub(r'\d+|--[a-f0-9]+', '', name)
    # 分词（简单按空格和常见分隔符）
    words = re.findall(r'[一-鿿]+|[a-zA-Z]+', name)
    # 过滤停用词
    stopwords = {'与', '和', '的', '了', '在', '是', '有', '个', '中', '学习', '课程'}
    return {w for w in words if len(w) > 1 and w not in stopwords}

def read_concept_links(concept_file: Path) -> list:
    """读取概念文件中的相关概念列表"""
    content = concept_file.read_text(encoding="utf-8")

    # 查找"相关概念"部分
    match = re.search(r'## 相关概念\n\n((?:- \[\[.+?\]\]\n)+)', content)
    if not match:
        return []

    links_text = match.group(1)
    links = re.findall(r'\[\[(.+?)\]\]', links_text)
    return links

def analyze_quality():
    """分析所有概念关联的质量"""
    concept_files = sorted(CONCEPT_DIR.glob("*.md"))

    # 收集所有关联
    all_links = {}
    for f in concept_files:
        links = read_concept_links(f)
        if links:
            all_links[f.stem] = links

    # 检测问题
    issues = defaultdict(list)

    for src_name, targets in all_links.items():
        for tgt_name in targets:
            # 检查目标是否存在
            tgt_file = CONCEPT_DIR / f"{tgt_name}.md"
            if not tgt_file.exists():
                issues["空链（目标不存在）"].append((src_name, tgt_name))
                continue

            # 应用启发式规则
            for rule in SUSPICIOUS_PATTERNS:
                if rule["check"](src_name, tgt_name):
                    issues[rule["name"]].append((src_name, tgt_name))

    return all_links, issues

def generate_report(all_links, issues):
    """生成审核报告"""
    report = f"""# 概念关联质量审核报告

**生成时间**: 2026-09-28
**审核范围**: {len(all_links)} 个概念，{sum(len(v) for v in all_links.values())} 条关联

---

## 执行摘要

"""

    # 统计
    total_links = sum(len(v) for v in all_links.values())
    total_issues = sum(len(v) for v in issues.values())

    report += f"- **总关联数**: {total_links}\n"
    report += f"- **发现问题**: {total_issues} 条\n"
    report += f"- **问题比例**: {total_issues/total_links*100:.1f}%\n\n"

    report += "---\n\n## 问题清单\n\n"

    # 按问题类型列出
    for issue_type, items in sorted(issues.items(), key=lambda x: -len(x[1])):
        report += f"### {issue_type}（{len(items)} 条）\n\n"
        report += "| 源概念 | 目标概念 |\n"
        report += "|--------|----------|\n"
        for src, tgt in items[:20]:  # 只显示前 20 条
            report += f"| {src} | {tgt} |\n"

        if len(items) > 20:
            report += f"\n*还有 {len(items) - 20} 条未显示*\n"

        report += "\n"

    report += "---\n\n## 建议操作\n\n"

    if "空链（目标不存在）" in issues:
        report += f"""### 1. 修复空链（{len(issues["空链（目标不存在）"])} 条）

**操作**: 删除这些不存在的 WikiLink

```python
# 自动删除空链
python3 scripts/clean_broken_links.py
```

"""

    if "题库与普通课程混杂" in issues:
        report += f"""### 2. 清理题库误关联（{len(issues["题库与普通课程混杂"])} 条）

**原因**: 规则引擎误判，ABB 题库与其他课程无实质关联

**操作**: 人工审核后删除

"""

    if "名称无共同关键词" in issues:
        report += f"""### 3. 审核弱关联（{len(issues["名称无共同关键词"])} 条）

**原因**: 可能是误判，也可能是深层关联（需人工判断）

**操作**: 逐条审核，保留有价值的，删除无意义的

"""

    report += """---

## 下一步

1. 执行自动修复脚本清理空链和明显错误
2. 人工审核边缘案例
3. 重新生成概念图谱
4. 在 Obsidian 中验证关系图效果

*本报告由 `scripts/audit_concept_links.py` 自动生成*
"""

    return report

def main():
    print("=== 概念关联质量审核 ===\n")

    print("分析关联质量...")
    all_links, issues = analyze_quality()

    total_links = sum(len(v) for v in all_links.values())
    total_issues = sum(len(v) for v in issues.values())

    print(f"✓ 分析完成")
    print(f"  - 总关联: {total_links} 条")
    print(f"  - 发现问题: {total_issues} 条")
    print(f"  - 问题比例: {total_issues/total_links*100:.1f}%\n")

    # 生成报告
    report = generate_report(all_links, issues)
    REPORT_FILE.write_text(report, encoding="utf-8")

    print(f"✓ 报告已生成: {REPORT_FILE}\n")

    # 输出摘要
    for issue_type, items in sorted(issues.items(), key=lambda x: -len(x[1])):
        print(f"  - {issue_type}: {len(items)} 条")

if __name__ == "__main__":
    main()
