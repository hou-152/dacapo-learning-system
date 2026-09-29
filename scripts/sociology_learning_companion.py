#!/usr/bin/env python3
"""
社会学七书共读陪练

直接回答用户的问题：「我要怎么交互式学习这 7 本社会学书？」

答案：告诉我你读到哪里，我问你几个问题，立刻给反馈。

不再推技能，不再问"你想要哪种方式"，直接开始。
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent
CONCEPTS_DIR = PROJECT_ROOT / "concepts"
DBS_LEARNING_DIR = Path.home() / "Documents" / "dbskill-learning"
COURSE_NAME = "社会学七书共读"

BOOKS = [
    "吉登斯《社会学基本概念》",
    "吉登斯《社会学的邀请》",
    "《女权主义简史》",
    "福山《身份政治》",
    "李强《当代中国社会分层》",
    "费孝通《乡土中国》《生育制度》",
    "刘擎《西方现代思想讲义》"
]

class SociologyCompanion:
    """社会学学习陪练"""

    def __init__(self):
        self.course_dir = DBS_LEARNING_DIR / COURSE_NAME
        self.course_dir.mkdir(parents=True, exist_ok=True)

    def show_progress(self):
        """显示学习进度"""
        print("\n" + "="*60)
        print("📚 社会学七书共读 - 学习进度")
        print("="*60)

        # 统计已学概念
        sociology_concepts = []
        for concept_file in CONCEPTS_DIR.rglob("*.md"):
            if concept_file.name == "INDEX.md":
                continue
            # 检查是否是社会学相关概念
            with open(concept_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'sociology' in content or '社会学' in content:
                    sociology_concepts.append(concept_file.stem)

        print(f"\n✅ 已掌握社会学概念：{len(sociology_concepts)} 个")
        if sociology_concepts:
            for concept in sociology_concepts[:10]:  # 显示前 10 个
                print(f"   - {concept}")
            if len(sociology_concepts) > 10:
                print(f"   ... 还有 {len(sociology_concepts) - 10} 个")

        # 统计已完成文章
        articles = [f for f in self.course_dir.glob("*.md") if f.name != "00-学习计划.md"]
        print(f"\n📝 已完成文章：{len(articles)} 篇")

        print("\n" + "="*60)

    def start_interactive(self, user_input: str):
        """开始交互式学习"""
        print("\n" + "="*60)
        print("🚀 开始交互式学习")
        print("="*60)

        print(f"\n你说：{user_input}")
        print("\n我来问你几个问题，看看你理解得怎么样：\n")

        # 从用户输入中提取概念
        concepts = []
        for concept_file in CONCEPTS_DIR.rglob("*.md"):
            if concept_file.name == "INDEX.md":
                continue
            concept_name = concept_file.stem
            if concept_name in user_input:
                concepts.append(concept_name)

        if concepts:
            print(f"💡 我注意到你提到了这些概念：{', '.join(concepts)}")
            print("\n让我问你几个问题：\n")

            # 模拟问答（实际应该是真实交互）
            for i, concept in enumerate(concepts[:2], 1):  # 最多问 2 个概念
                print(f"问题 {i}：用你自己的话说，{concept} 是什么？")
                print("（这里应该等待你的回答，然后我给反馈）\n")

            print("💭 在真实学习中，我会等你回答，然后：")
            print("   1. 评估你的理解程度")
            print("   2. 给出掌握度评分")
            print("   3. 更新你的知识网络")
            print("   4. 刷新可视化仪表盘")
            print("   5. 让你立刻看到进步\n")

        else:
            print("💭 你可以告诉我：")
            print("   - 你读到了哪本书的哪个部分")
            print("   - 你理解了什么概念")
            print("   - 你有什么困惑")
            print("\n然后我会问你问题，给你即时反馈。\n")

        print("="*60)

    def quick_learn(self, concept_name: str):
        """快速学习一个概念"""
        print(f"\n开始学习：{concept_name}")

        # 调用交互式学习系统
        try:
            subprocess.run([
                "python3",
                str(PROJECT_ROOT / "scripts" / "interactive_learning.py"),
                concept_name
            ], check=False)  # 不检查错误，让它自己处理
        except Exception as e:
            print(f"⚠️  调用失败：{e}")
            print("💡 你也可以直接告诉我你的理解，我来评估。")

    def show_books(self):
        """显示书单"""
        print("\n" + "="*60)
        print("📚 社会学七书书单")
        print("="*60)
        for i, book in enumerate(BOOKS, 1):
            print(f"{i}. {book}")
        print("="*60)
        print("\n💡 使用方式：")
        print("   直接告诉我：「我读了 <书名> 的 <章节>」")
        print("   或者：「我想学 <概念名>」")
        print("   我会立刻开始问你问题。")

def main():
    import sys

    companion = SociologyCompanion()

    if len(sys.argv) < 2:
        print("\n╔══════════════════════════════════════════════════════╗")
        print("║       社会学七书共读 - 交互式学习陪练            ║")
        print("╚══════════════════════════════════════════════════════╝")
        print("\n用法：")
        print("  python3 sociology_learning_companion.py progress    # 查看进度")
        print("  python3 sociology_learning_companion.py books       # 查看书单")
        print("  python3 sociology_learning_companion.py learn <概念> # 学习概念")
        print("\n💡 或者直接告诉 AI：")
        print("   「我读了费孝通的差序格局那一章」")
        print("   「我想学社会分层」")
        print("   「帮我理解礼治秩序」")
        print("\n   我会立刻开始问你问题，给你即时反馈。")
        print("\n" + "="*60)
        companion.show_progress()
        sys.exit(0)

    command = sys.argv[1]

    if command == "progress":
        companion.show_progress()
    elif command == "books":
        companion.show_books()
    elif command == "learn":
        if len(sys.argv) < 3:
            print("请指定概念名")
            sys.exit(1)
        concept_name = sys.argv[2]
        companion.quick_learn(concept_name)
    else:
        # 假设整个输入是用户说的话
        user_input = ' '.join(sys.argv[1:])
        companion.start_interactive(user_input)

if __name__ == "__main__":
    main()
