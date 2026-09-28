# Context Engine、Curriculum 与 Learning Velocity｜来源包

date: 2026-07-27
scope: 第 12 篇概念续篇
status: primary-source-backed-with-unknowns

## AI 内参检索结果

### AI 内参｜LLM Agent Engineering 汇总

- 本地路径：`/Users/housibo/Documents/ai 内参/exports/260624/260624-llm-agent-engineering.md`
- 使用内容：Context Engineering、Context Window、Working Memory、Context Bloat、Structured Session Memory。
- 结论边界：这是内部汇总与三级笔记，用作来源地图；其中外部事实继续回到原始官方材料核验。

### Anthropic 官方文章本地快照

- 本地路径：`/Users/housibo/Documents/交互式学习/output/context-engineering-agent-feed-2026-06-24/downloads/anthropic-effective-context-engineering.txt`
- 官方链接：https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- 使用主张：Context Engineering 持续筛选进入有限 Context Window 的信息；Agent 循环中需要反复精炼上下文；高信号、最小充分信息优于无边界堆积。
- 边界：官方文章使用 `Context Engineering`，没有把 `Context Engine` 定义为统一架构名。

## Curriculum 与注意力选择

### Bengio 等｜Curriculum Learning

- 链接：https://icml.cc/2009/papers/119.pdf
- 类型：ICML 研究论文
- 使用主张：训练样本的选择和呈现顺序可以影响学习收敛速度与最终结构；从较容易概念逐步进入复杂概念是一种课程策略。
- 边界：论文实验属于机器学习训练，不能直接覆盖所有人类教学情境。

### Kidd、Piantadosi、Aslin｜The Goldilocks Effect

- 链接：https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0036399
- 类型：婴儿注意力实验
- 使用主张：实验中的婴儿更倾向关注复杂度适中的视觉序列，对过于简单或复杂的序列更易移开注意。
- 边界：研究对象是 7—8 个月婴儿的视觉注意，本文只借用“信息难度需要匹配当前状态”的有限类比。

### Oudeyer、Kaplan、Hafner｜Intrinsic Motivation Systems for Autonomous Mental Development

- 链接：https://doi.org/10.1109/TEVC.2006.890271
- 类型：发展机器人与内在动机研究
- 使用主张：系统可以选择能够最大化学习进展的情境，以此组织自主探索。
- 边界：学习进展驱动是一类计算机制，不能自动解决人类价值和长期目标选择。

## AI 教育与学习速度

### Kestin 等｜AI tutoring outperforms in-class active learning

- 链接：https://www.nature.com/articles/s41598-025-97652-6
- 类型：随机对照实验
- 使用主张：在哈佛一门本科物理课程的两节课中，经过专家提示和教学脚手架设计的 AI Tutor 组取得更高短期学习增量，并用时更少。
- 边界：研究范围是特定课程、短周期和定制 Tutor；作者明确没有主张所有情境下均优于课堂教学。

### Bastani 等｜Generative AI without guardrails can harm learning

- 链接：https://doi.org/10.1073/pnas.2422633122
- 类型：高中数学现场实验
- 使用主张：无保护的生成式 AI 能改善练习表现，同时可能削弱撤掉 AI 后的独立学习；教学保护改变了结果。
- 边界：研究位于特定数学课程与工具设计，不能外推为所有 AI 辅助学习的统一效果。

### OpenAI 官方使命

- 链接：https://openai.com/about/
- 类型：公司官方说明
- 使用主张：OpenAI 当前公开使命是确保 AGI 惠及全人类。
- 边界：本轮没有找到把“教育平权”写成 OpenAI 最初使命原句的官方材料。

## Benchmark 风险

### White 等｜LiveBench

- 链接：https://mlanthology.org/iclr/2025/white2025iclr-livebench/
- 类型：ICLR 2025 研究论文
- 使用主张：测试集污染会削弱静态 Benchmark 的公平性；动态更新问题是一种降低污染风险的设计。
- 边界：数据污染风险不能单独证明某个厂商主动逆向题库或故意操纵成绩。

## 本篇的操作性定义

- `Context Engine`：执行上下文选择、检索、压缩、排序与更新的运行时机制。此定义用于课程推理，不宣称为行业统一标准。
- `可持续学习速度`：在陌生任务中仍可调用的能力增量，除以时间与外部干预成本。此定义用于概念区分，不宣称为现成教育测量指标。
