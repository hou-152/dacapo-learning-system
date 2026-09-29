#!/usr/bin/env python3
"""
交互式学习系统 - 完整流程
让学习上瘾的核心引擎

用户说什么 → 我直接开始交互式学习 → 自动反馈 → 可视化刷新

不再问"你想要哪种方式？"，直接开始。
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
CONCEPTS_DIR = PROJECT_ROOT / "concepts"
LEARNING_PROGRESS = PROJECT_ROOT / ".learning-progress"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"

class InteractiveLearning:
    """交互式学习引擎"""

    def __init__(self):
        self.session_log = []
        LEARNING_PROGRESS.mkdir(exist_ok=True)

    def extract_concepts_from_dialogue(self, dialogue: str) -> List[str]:
        """从对话中提取概念"""
        concepts = []
        for concept_file in CONCEPTS_DIR.rglob("*.md"):
            if concept_file.name == "INDEX.md":
                continue
            concept_name = concept_file.stem
            if concept_name in dialogue:
                concepts.append(concept_name)
        return concepts

    def auto_quiz(self, concept_name: str) -> Dict[str, float]:
        """自动问答评估（模拟）"""
        print(f"\n📚 开始学习：{concept_name}")
        print("=" * 60)

        # 读取概念定义
        concept_file = CONCEPTS_DIR / f"{concept_name}.md"
        if not concept_file.exists():
            print(f"⚠️  概念文件不存在：{concept_file}")
            return {"score": 0.0}

        with open(concept_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取定义
        lines = content.split('\n')
        definition = ""
        for i, line in enumerate(lines):
            if line.strip() == "## 定义":
                if i + 2 < len(lines):
                    definition = lines[i + 2].strip()
                break

        if definition:
            print(f"\n💡 定义：{definition}")

        print("\n" + "=" * 60)
        print("\n✅ 学习完成！")
        print("\n💭 如果这是真实学习，我会问你 2-3 个问题。")
        print("现在假设你的回答都很棒，掌握度评分：0.85")

        return {"score": 0.85}

    def update_mastery(self, concept_name: str, score: float):
        """更新掌握度"""
        concept_file = CONCEPTS_DIR / f"{concept_name}.md"
        if not concept_file.exists():
            return

        with open(concept_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 更新 frontmatter
        lines = content.split('\n')
        updated_lines = []
        in_frontmatter = False
        mastery_updated = False
        last_studied_updated = False
        study_count_updated = False

        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    updated_lines.append(line)
                else:
                    # 即将结束 frontmatter
                    if not mastery_updated:
                        updated_lines.append(f"mastery: {score:.2f}")
                    if not last_studied_updated:
                        updated_lines.append(f"lastStudied: {datetime.now().strftime('%Y-%m-%d')}")
                    if not study_count_updated:
                        updated_lines.append("studyCount: 1")
                    in_frontmatter = False
                    updated_lines.append(line)
            elif in_frontmatter and line.startswith('mastery:'):
                updated_lines.append(f"mastery: {score:.2f}")
                mastery_updated = True
            elif in_frontmatter and line.startswith('lastStudied:'):
                updated_lines.append(f"lastStudied: {datetime.now().strftime('%Y-%m-%d')}")
                last_studied_updated = True
            elif in_frontmatter and line.startswith('studyCount:'):
                # 增加学习次数
                try:
                    old_count = int(line.split(':')[1].strip())
                    updated_lines.append(f"studyCount: {old_count + 1}")
                except:
                    updated_lines.append("studyCount: 1")
                study_count_updated = True
            else:
                updated_lines.append(line)

        with open(concept_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines))

    def generate_instant_feedback(self, concept_name: str):
        """生成即时反馈"""
        print(f"\n🎉 正在生成即时反馈...")
        try:
            subprocess.run([
                "python3",
                str(PROJECT_ROOT / "scripts" / "instant_feedback.py"),
                concept_name
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️  即时反馈生成失败：{e}")

    def refresh_dashboard(self):
        """刷新可视化仪表盘"""
        print("\n🔄 正在刷新可视化...")
        try:
            # 更新 mastery.json
            subprocess.run([
                "python3",
                str(PROJECT_ROOT / "scripts" / "update_mastery_from_concepts.py")
            ], check=True, capture_output=True)

            # 刷新进度追踪
            subprocess.run([
                "python3",
                str(PROJECT_ROOT / "scripts" / "progress_tracker.py")
            ], check=True, capture_output=True)

            print("✅ 可视化已刷新")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  刷新失败：{e}")

    def open_dashboard(self):
        """打开可视化仪表盘"""
        print("\n🌐 正在打开学习仪表盘...")
        dashboard_file = DASHBOARD_DIR / "index.html"
        subprocess.run(["open", str(dashboard_file)])

    def learn(self, concept_name: str, auto_open_dashboard: bool = True):
        """完整学习流程"""
        print(f"\n{'='*60}")
        print(f"🚀 开始交互式学习")
        print(f"{'='*60}")

        # 1. 自动问答
        result = self.auto_quiz(concept_name)
        score = result.get("score", 0.0)

        # 2. 更新掌握度
        self.update_mastery(concept_name, score)
        print(f"\n✅ 掌握度已更新：{score:.0%}")

        # 3. 生成即时反馈
        self.generate_instant_feedback(concept_name)

        # 4. 刷新可视化
        self.refresh_dashboard()

        # 5. 打开仪表盘
        if auto_open_dashboard:
            self.open_dashboard()

        print(f"\n{'='*60}")
        print("🎉 学习完成！")
        print(f"{'='*60}")
        print("\n💡 下一步：")
        print("   - 查看可视化仪表盘，看到你的知识网络扩张")
        print("   - 继续学习其他概念")
        print(f"   - 运行 `python3 scripts/interactive_learning.py <概念名>` 继续")

def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 interactive_learning.py <概念名>")
        print("\n或者直接告诉 AI：「我想学 <概念名>」")
        sys.exit(1)

    concept_name = sys.argv[1]
    learner = InteractiveLearning()
    learner.learn(concept_name)

if __name__ == "__main__":
    main()
