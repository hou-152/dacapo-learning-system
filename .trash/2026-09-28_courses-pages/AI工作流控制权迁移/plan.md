---
contract_version: v4
audit_mode: settlement
intent: use
interaction: guided
---

# AI 工作流控制权迁移｜学习计划

## 终局能力

能独立判断一个 AI 工作流中的规则、工具、Skill、上下文与验证机制，哪些应常驻，哪些应按任务状态调用；并据此为自己的内容与学习工作流提出一个可验证的改造方案。

核心原则：[[AI不外包判断]]。相关方法论：[[交互式学习]]、[[第一性原理]]、[[2W2H]]。姊妹课程：[[Agentic Engineering 工作流]]。

## 来源边界

可信候选池：乔木 RSS、AI 内参、用户后续指定材料。

当前最小来源集：

- 地图源／实践源：RSS《Claude Code sends 33k tokens before reading the prompt; OpenCode sends 7k》。入选，因为它提供 Harness、规则文件、MCP 与子 Agent 带来上下文成本的实测案例；限制是单一测量环境与版本快照，不能外推为所有 Harness 的定论。
- 深挖源／反例源：AI 内参《工具更多反而让 Copilot 代码审查变差，GitHub 如何修正》。入选，因为它显示工具能力相同，任务锚点、工具策略与 trace 反馈不同，结果会相反；限制是代码审查场景，迁移到内容工作流时必须重验。
- 未入选：X 链接当前未取得正文，不能作为课程证据。

2026-07-27 概念性续篇来源：

- 来源包：`assets/260726-260727-opus5-context-engineering-source-pack.md`。
- 智力与学习来源包：`assets/260727-intelligence-skill-acquisition-source-pack.md`。
- Context Engine 与学习速度来源包：`assets/260727-context-engine-curriculum-learning-velocity-source-pack.md`。
- 选择压力、Value Function 与 AI Native 文化来源包：`assets/260727-selection-pressure-value-function-ai-native-culture-source-pack.md`。
- 官方来源：Anthropic 的 Opus 5 发布、Claude 官方上下文工程文章。
- 材料主张：Thariq 关于系统提示词缩短约 80% 且编码评测无可测量损失的说明；本课程不把该比例外推成通用规律。
- 观察案例：第三方系统提示词仓库；未经 Anthropic 确认，不作为官方真源。
- 选材理由：新材料直接命中第 8 篇留下的证伪条件——模型继续变强时，Harness 是否会变薄。

## 通过标准

- 能区分「能力存在」与「能力在当前任务中被注入」。
- 能解释上下文膨胀为什么会改变成本、注意力与任务表现。
- 能提出一个适用于自身工作流的常驻／按需调用边界，并说明验证信号。
- 能区分 Harness 的文本厚度、结构深度、控制粒度和责任覆盖。
- 能解释强模型为什么减少显式规则，以及控制为什么迁移到上下文、反馈与元判断。
- 能区分环境、Context Window、上下文、世界模型、行动能力与反馈质量。
- 能区分一次成绩、领域技能、技能获得效率与系统级能力增长。
- 能判断一次 Agent“学习”改变了上下文、外部记忆、模型参数还是学习机制。
- 能区分 Context Window、Context、Context Engineering、Context Engine 与 Curriculum。
- 能区分内容覆盖速度、辅助表现速度与可持续学习速度。
- 能区分运行时搜索、系统学习与人工演化。
- 能解释 Harness、Evaluator、选择压力、Memory／Skill 与文化之间的关系。
- 能区分 Value Function、Reward、Objective、Evaluator、Human values 与 Culture。
- 能在任务或工作流尺度上判断 Token 成本与预期总价值，避免把 Token 更少直接等同价值更高。

## 稳定概念

- 常驻上下文：每轮任务开始前都会携带给模型的规则、工具说明、记忆或材料。
- 按需调用：仅当当前任务状态满足触发条件时，才提供的工具、规则或局部策略。
- 最小充分上下文：足以回答当前可验证问题、但不额外扩大工作记忆的证据集合。
- 反馈循环：依据可观察结果决定继续、修复、切换策略或停止的机制。
- 环境：Agent 外部实际存在的状态、对象、规则和后果。
- Context Window：模型单次推理能够容纳的 token 范围。
- 上下文：当前实际交给模型的观察、状态、指令、记忆、工具信息和返回结果。
- 世界模型：Agent 用来解释观察、预测后果和选择行动的内部结构。
- 任务成绩：系统在特定任务、评价标准与时间点上的输出表现。
- 领域技能：系统在一类任务上能够稳定复现的行为结构。
- 技能获得效率：在给定先验和任务范围下，单位新经验与干预所形成的可迁移能力。
- 系统学习：上下文、外部记忆、Skill 库、Evaluator 或模型参数中的任一持久变化改善后续表现。
- 元学习：让系统面对新任务时，用更少经验获得可迁移技能的学习过程。
- Context Engineering：设计和维护进入模型推理上下文的信息策略。
- Context Engine：本课程对运行时选择、检索、压缩、排序和更新上下文机制的操作性定义。
- Curriculum：跨时间选择学习经验及其呈现顺序的策略。
- 可持续学习速度：单位时间与干预成本带来的、在陌生任务中仍能保持和迁移的能力增量。
- 选择压力：评价标准、现实结果、成功门槛与失败成本共同造成的不同行为保留概率。
- AI Native 文化：本课程对智能系统跨任务运行时，在事实、速度、成本、自主性与责任冲突中稳定保留的行为倾向所作的操作性定义。
- Value Function：强化学习中，在给定策略下从某个状态出发所能获得的未来累计回报期望。
- Human values：关于什么值得追求、哪些代价可接受以及谁承担后果的规范判断。

## 学习路径

1. 区分能力库存与任务上下文。
2. 识别厚 Harness 的真实成本与收益边界。
3. 将 Skill 改写为可触发、可验证的局部策略。
4. 为 DBS／内容工作流设计一个最小反馈循环。
5. 形成可发布的个人判断与验证计划。
6. 用新一代模型材料检验“厚 Harness”判断，进入智能、上下文与控制的第一性原理。
7. 区分上下文与世界模型，解释 Harness 怎样塑造 Agent 的认识、行动与规范世界。
8. 区分成绩、技能与智力，判断 Harness 补偿和 Agent 自身学习的边界。
9. 研究 Context Engine、Curriculum 与 Learning velocity，解释注意力和经验选择怎样塑造智能。
10. 区分搜索、学习与人工演化，研究选择压力怎样经由保留机制形成 AI Native 文化，并校准 Value Function 与 Token 经济学。

## 当前指针

- 当前单元：13（今日收束篇）
- 当前篇：`13.md`（2026-07-27，等待学习反馈）
- 已完成：`01.md`—`12.md`
- 上一篇反馈：用户用元认知、反复思考和内驱力解释长期知识结构；把文件位置和项目状态交给 Agent 召回；用 DBS 一对一反馈提高学习速度，同时为精神性慢阅读保留位置
- 上一篇关键判断：人的长期结构应保存高复用判断，外部 Context Engine 应保存和召回动态状态；高质量上下文可以降低 Agent 进入任务的认知摩擦
- 本篇问题：达尔文类比怎样严谨迁移到 Agent；Harness 能否塑造 AI Native 文化；Value Function 与价值观的关系；Token 经济学应在哪个尺度上核算
- 本篇方向：区分搜索、学习与人工演化，建立 Harness—选择压力—保留机制—文化的概念链，并完成今日收束
- Skill 候选状态：AI Native Culture 目前只是候选认知框架；真实任务、冲突样本、Evaluator 和跨任务证据出现前不固化为 Skill
- 已废弃：旧 `02.md`（过于抽象）→ `.trash/2026-07-14_02.md`、旧预生成 `03.md`（Skill 设计主题，与 02 反馈缺口不匹配）→ 已被重写覆盖
- 证据账本：`learner-log.md#lesson-01`
