#!/usr/bin/env python3
"""
对话监听器 - 自动提取学习内容并回填

监听用户的对话，自动识别：
- 新学的概念
- 理解的例子
- 遇到的困惑
- 产生的思考

然后自动回填到对应的学习反馈区。

这是用户说的："在反馈的过程中，能不能帮我补全对应的上下文？"
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
CONCEPTS_DIR = PROJECT_ROOT / "concepts"
DBS_LEARNING_DIR = Path.home() / "Documents" / "dbskill-learning"
LEARNING_PROGRESS = PROJECT_ROOT / ".learning-progress"

class ConversationMonitor:
    """对话监听器"""

    def __init__(self):
        self.session_file = LEARNING_PROGRESS / "current-session.json"
        self.load_session()

    def load_session(self):
        """加载当前会话"""
        if self.session_file.exists():
            with open(self.session_file, 'r', encoding='utf-8') as f:
                self.session = json.load(f)
        else:
            self.session = {
                "start_time": datetime.now().isoformat(),
                "concepts_learned": [],
                "examples": [],
                "confusions": [],
                "insights": []
            }

    def save_session(self):
        """保存会话"""
        LEARNING_PROGRESS.mkdir(exist_ok=True)
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self.session, f, ensure_ascii=False, indent=2)

    def extract_concepts(self, text: str) -> List[str]:
        """从文本中提取概念"""
        concepts = []
        for concept_file in CONCEPTS_DIR.rglob("*.md"):
            if concept_file.name == "INDEX.md":
                continue
            concept_name = concept_file.stem
            if concept_name in text:
                concepts.append(concept_name)
        return concepts

    def extract_examples(self, text: str) -> List[str]:
        """提取例子（包含"例如"、"比如"、"就像"等）"""
        example_patterns = [
            r"例如[：:](.*?)(?:[。\n]|$)",
            r"比如[：:](.*?)(?:[。\n]|$)",
            r"就像(.*?)(?:[。\n]|$)",
            r"比方说(.*?)(?:[。\n]|$)"
        ]
        examples = []
        for pattern in example_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                examples.append(match.group(1).strip())
        return examples

    def extract_confusions(self, text: str) -> List[str]:
        """提取困惑（包含"不懂"、"不理解"、"困惑"等）"""
        confusion_patterns = [
            r"(不懂|不理解|困惑|搞不清楚|不明白)(.*?)(?:[。\n]|$)",
            r"为什么(.*?)(?:[。\n]|$)",
            r"(.*?)不太清楚(?:[。\n]|$)"
        ]
        confusions = []
        for pattern in confusion_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                confusions.append(match.group(0).strip())
        return confusions

    def extract_insights(self, text: str) -> List[str]:
        """提取洞察（包含"原来"、"理解了"、"恍然大悟"等）"""
        insight_patterns = [
            r"原来(.*?)(?:[。\n]|$)",
            r"(我理解了|我懂了|恍然大悟)(.*?)(?:[。\n]|$)",
            r"这样看来(.*?)(?:[。\n]|$)"
        ]
        insights = []
        for pattern in insight_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                insights.append(match.group(0).strip())
        return insights

    def monitor(self, user_message: str, ai_response: str):
        """监听一轮对话"""
        # 提取概念
        concepts = self.extract_concepts(user_message + ai_response)
        for concept in concepts:
            if concept not in self.session["concepts_learned"]:
                self.session["concepts_learned"].append(concept)

        # 提取例子
        examples = self.extract_examples(user_message + ai_response)
        self.session["examples"].extend(examples)

        # 提取困惑
        confusions = self.extract_confusions(user_message)
        self.session["confusions"].extend(confusions)

        # 提取洞察
        insights = self.extract_insights(user_message)
        self.session["insights"].extend(insights)

        self.save_session()

    def generate_feedback_section(self) -> str:
        """生成反馈内容"""
        feedback = []

        feedback.append("## 📚 本次学到的概念")
        if self.session["concepts_learned"]:
            for concept in self.session["concepts_learned"]:
                feedback.append(f"- {concept}")
        else:
            feedback.append("（暂无）")

        feedback.append("\n## 💡 理解的例子")
        if self.session["examples"]:
            for example in self.session["examples"][:5]:  # 最多 5 个
                feedback.append(f"- {example}")
        else:
            feedback.append("（暂无）")

        feedback.append("\n## ❓ 还有的困惑")
        if self.session["confusions"]:
            for confusion in self.session["confusions"][:3]:  # 最多 3 个
                feedback.append(f"- {confusion}")
        else:
            feedback.append("（暂无）")

        feedback.append("\n## 💭 产生的思考")
        if self.session["insights"]:
            for insight in self.session["insights"][:3]:  # 最多 3 个
                feedback.append(f"- {insight}")
        else:
            feedback.append("（暂无）")

        return "\n".join(feedback)

    def backfill_to_article(self, article_path: Path):
        """回填到文章的学习反馈区"""
        if not article_path.exists():
            print(f"⚠️  文章不存在：{article_path}")
            return

        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找学习反馈区
        if "## 学习反馈" not in content:
            print(f"⚠️  文章中没有「学习反馈」区域：{article_path}")
            return

        # 生成反馈内容
        feedback_content = self.generate_feedback_section()

        # 查找"请写在这行下面："后面的位置
        lines = content.split('\n')
        new_lines = []
        feedback_inserted = False

        for i, line in enumerate(lines):
            new_lines.append(line)
            if "请写在这行下面：" in line and not feedback_inserted:
                new_lines.append("")
                new_lines.append("### 自动回填（来自对话）")
                new_lines.append("")
                new_lines.extend(feedback_content.split('\n'))
                feedback_inserted = True

        if feedback_inserted:
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            print(f"✅ 反馈已自动回填到：{article_path}")
        else:
            print(f"⚠️  未找到插入位置")

    def find_latest_article(self, course_name: str) -> Optional[Path]:
        """查找最新的课程文章"""
        course_dir = DBS_LEARNING_DIR / course_name
        if not course_dir.exists():
            return None

        # 查找所有 .md 文件（排除 00-学习计划.md）
        articles = [f for f in course_dir.glob("*.md") if f.name != "00-学习计划.md"]
        if not articles:
            return None

        # 按文件名排序，取最新的
        articles.sort()
        return articles[-1]

    def auto_backfill(self, course_name: str):
        """自动回填到最新文章"""
        latest_article = self.find_latest_article(course_name)
        if latest_article:
            self.backfill_to_article(latest_article)
        else:
            print(f"⚠️  未找到课程「{course_name}」的文章")

    def clear_session(self):
        """清空当前会话"""
        if self.session_file.exists():
            self.session_file.unlink()
        self.load_session()

def main():
    import sys

    monitor = ConversationMonitor()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 conversation_monitor.py backfill <课程名>  # 回填到最新文章")
        print("  python3 conversation_monitor.py clear             # 清空会话")
        print("  python3 conversation_monitor.py show              # 显示当前会话")
        sys.exit(1)

    command = sys.argv[1]

    if command == "backfill":
        if len(sys.argv) < 3:
            print("请指定课程名")
            sys.exit(1)
        course_name = sys.argv[2]
        monitor.auto_backfill(course_name)

    elif command == "clear":
        monitor.clear_session()
        print("✅ 会话已清空")

    elif command == "show":
        print(json.dumps(monitor.session, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
