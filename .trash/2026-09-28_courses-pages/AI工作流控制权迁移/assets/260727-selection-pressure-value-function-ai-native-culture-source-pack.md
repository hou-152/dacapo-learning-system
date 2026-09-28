# 第 13 篇来源包｜选择压力、Value Function、AI Native 文化与 Token 经济学

## 用途

本来源包只服务于《13｜收束：谁定义智能的方向——Harness、选择压力与 AI Native 文化》。它负责区分已确认事实、课程推断、类比边界与待验证主张。

## 一、已采用的一手／权威来源

| 来源 | 用于支持 | 边界 |
|---|---|---|
| [Luria 与 Delbrück，1943](https://pmc.ncbi.nlm.nih.gov/articles/PMC1209226/) | 抗性突变可在选择发生前出现 | 经典细菌实验，不能单独概括全部现代进化机制 |
| [Stanford Encyclopedia of Philosophy：Natural Selection](https://plato.stanford.edu/archives/fall2023/entries/natural-selection/) | 自然选择涉及可遗传差异与差异性繁殖 | 权威概念综述，证据类型有别于实验论文 |
| [Sutton 与 Barto：Reinforcement Learning](https://incompleteideas.net/book/RLbook2020.pdf) | Reward、Return 与 Value Function 的标准定义 | 强化学习术语不能直接等同人的伦理价值 |
| [Ouyang 等：InstructGPT](https://arxiv.org/abs/2203.02155) | 人类排序、Reward Model 与模型行为优化的关系 | 特定标注群体偏好不能代表普遍人类价值 |
| [Tree of Thoughts，NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/271db9922b8d1f4dd7aaef84ed5ac703-Abstract-Conference.html) | 运行时生成、评价和回退多条推理路径 | 改善本轮搜索不自动产生持久学习 |
| [Reflexion，NeurIPS 2023](https://papers.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html) | 语言反馈进入 episodic memory，影响后续尝试 | 有持久更新证据，泛化范围仍需按任务测量 |
| [GitHub：Improving token efficiency](https://github.blog/ai-and-ml/github-copilot/improving-token-efficiency-in-github-agentic-workflows/) | Token、调用轮次、工作负载与过程质量需要联合观察 | GitHub 自有工作流案例，不能外推成所有 Agent 的通用比例 |
| [GitHub Agentic Workflows：Outcomes](https://github.github.com/gh-aw/reference/outcomes/) | 成本数据需要连接被接受的结果 | “被接受”仍可能只是代理结果，不等于长期业务价值 |

## 二、本地 AI 内参证据

### Token Efficiency

文件：/Users/housibo/Documents/ai 内参/exports/260624/260624-llm-agent-engineering.md

- 第 791—804 行：规模化运行会把 Token 浪费放大为费用、延迟和可靠性问题。
- 第 818—837 行：效率需要先测量；缩短上下文不能删除关键证据、约束与历史。
- 第 844—874 行：Token 应用于任务关键上下文，结果需要同时观察任务成功与上下文成本。

### AI 经济性与价值捕获

文件：/Users/housibo/Documents/ai 内参/artifacts/ingest/2026-06-25/clean-skill-run-v2/11-ai-investment-payoff-concepts.md

- 第 7—19 行：商业投资最终要产生回报；AI 经济性要核算资本开支、算力、数据改造和组织部署。
- 第 119—131 行：企业采用 AI 后需要创造收入或节省成本；早期亏损不能无限延续。
- 第 140—145 行：技术创造效率与企业能否捕获利润需要分开。

### Token 经济学原条目

文件：/Users/housibo/Documents/ai 内参/artifacts/ingest/2026-05-31/visible-cleanup-260531.md

- 第 108—113 行保存《Token 经济学把 AI 成本结构讲成新的货币战争》的摘要、原视频与 Readwise 入口。
- 本地没有完整逐字稿，也没有找到“每个 Token 的产出至少覆盖自身成本”的逐字原句。

## 三、课程采用的概念边界

### FACT

- Value Function 是给定策略下未来累计回报的期望预测。
- Token 与推理成本会在高频工作流中被规模化放大。
- 只看 Token 数不能证明单位正确工作的效率提高。
- 一次多路径搜索成功不能证明系统发生持久学习。

### INFERENCE

- Harness 可以被视为文化形成的制度环境。
- Evaluator 与现实后果形成选择压力。
- Memory 与 Skill 可以提供经验保留和压缩机制。
- AI Native 文化可以操作化为系统跨任务稳定保留的行为倾向。
- 学习、避免损失与未来选择空间可以进入工作流总价值核算。

### UNKNOWN

- “消耗的 Token 必须有产出，且产出至少覆盖成本”是否来自用户提及视频的逐字原句。
- 当前这套 AI Native 文化框架能否跨真实任务改善结果。
- 几十行 Harness 能否在没有配套 Evaluator、Memory 与治理机制时形成稳定文化。

## 四、写作时禁止越界的结论

- 不把自然选择写成有意图的环境奖励。
- 不把模型采样直接称为遗传变异。
- 不把 Value Function 写成 AI 的伦理价值观。
- 不把 Reward Model 写成全人类价值的完整代表。
- 不把短 Harness 的文字密度直接当作文化已经形成。
- 不把 Token 更少直接当作业务价值更高。
- 不把课程中的三轴框架写成已验证数学定律。
