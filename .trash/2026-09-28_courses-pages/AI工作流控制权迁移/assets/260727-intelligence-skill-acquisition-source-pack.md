# 智力、技能获得效率与 Agent 学习｜来源包

date: 2026-07-27
scope: 第 11 篇概念续篇
status: primary-source-backed

## 选材问题

本来源包只支持三个问题：

1. 为什么任务技能与智力需要分开？
2. 为什么高分可能来自先验、经验或外部支架？
3. 当前 Agent 的“学习”发生在模型参数还是系统外部状态？

## 来源

### François Chollet｜On the Measure of Intelligence

- 链接：https://arxiv.org/abs/1911.01547
- 类型：研究论文／理论框架
- 使用主张：单项任务技能受到先验知识和经验影响；智力可被表述为给定任务范围、先验、经验和泛化难度下的技能获得效率。
- 边界：这是一个有影响力的理论定义；心理学与 AI 领域尚未形成唯一的统一口径。

### Chi、Feltovich、Glaser｜Categorization and Representation of Physics Problems by Experts and Novices

- 链接：https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog0502_2
- 类型：实验研究
- 使用主张：物理专家与新手的问题分类和知识组织方式存在差异；专家更多使用底层原理，新手更多使用表面特征。
- 边界：研究对象是物理问题表征，不能直接外推为所有领域的智力差异。

### Macnamara、Hambrick、Oswald｜Deliberate Practice and Performance

- 链接：https://www.psychologicalscience.org/journals/psychological-science/0956797614535810/
- 类型：元分析
- 使用主张：刻意练习能解释一部分表现差异，解释程度随领域变化；练习无法单独解释全部差异。
- 边界：研究结论涉及相关研究汇总，不能直接确定某个个体的成绩由什么造成。

### Brown 等｜Language Models are Few-Shot Learners

- 链接：https://proceedings.neurips.cc/paper_files/paper/2020/hash/1457c0d6bfcb4967418bfb8ac142f64a-Abstract.html
- 类型：NeurIPS 研究论文
- 使用主张：模型可通过文本中的零样本、单样本或少样本条件执行多种任务，评测过程没有梯度更新或微调。
- 边界：论文研究 GPT-3 与特定评测集，不代表所有模型的少样本学习能力。

### Shinn 等｜Reflexion

- 链接：https://arxiv.org/abs/2303.11366
- 类型：Agent 研究论文
- 使用主张：使用语言反馈与情景记忆改善后续决策，方法明确不更新模型权重。
- 边界：论文中的性能提升属于给定基准和 Agent 架构，不能单独证明一般智力提高。

### Wang 等｜Voyager

- 链接：https://arxiv.org/abs/2305.16291
- 类型：具身 Agent 研究论文
- 使用主张：通过自动课程、可增长技能库、环境反馈和自验证积累 Minecraft 能力，绕过模型参数微调。
- 边界：研究处于 Minecraft 环境，技能复用与开放世界表现不能直接外推到现实中的一般智能。

### Finn、Abbeel、Levine｜Model-Agnostic Meta-Learning

- 链接：https://proceedings.mlr.press/v70/finn17a
- 类型：ICML 研究论文
- 使用主张：元学习可训练模型，使其面对新任务时通过少量样本和少量梯度更新获得较好的泛化。
- 边界：MAML 是元学习的一种具体方法，本篇只借用“提高新任务适应效率”的概念，不把它当作 Agent 的通用实现方案。

## 本篇不采用的主张

- 不把“灵性”直接等同于心理测量意义上的 IQ。
- 不把人类工作记忆直接等同于 LLM 的 Context Window。
- 不依据单一产品体验排列当前生图或视频模型的强弱。
- 不把外部记忆增长自动称为模型参数学习。
