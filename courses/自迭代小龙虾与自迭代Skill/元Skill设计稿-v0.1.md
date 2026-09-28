# 元 Skill 设计稿 v0.1（研究稿，未执行）

> 状态：研究稿，供你决策，未创建任何 SKILL.md、未安装任何东西。
> 依据：`结业-立项-自迭代dbskill.md` 车道 B（触发条件已满足，动工前提 = 车道 A 第一圈验收完成）。
> 日期：2026-08-25

## 1. 定位一句话

元 Skill = **skill 生命周期的守门与路由层**：设计时定合同，审计时出证据，迭代时走受控进化。它自己是一层薄壳，把已有资产串成流水线，不新造机制。

## 2. 不做什么（三个不做）

1. 不新造世界观和机制——所有重活复用现有资产；
2. 不重复现有五个 skill 的活（skill-darwin-lite 管单 skill 优化、loop-engine 管 Loop 设计、nuwa-skill 管造人、engineering-meta 管工程流程、codex-self-optimization 管本地自优化）——元 Skill 只做它们之上的「该用谁、什么顺序、怎么验收」；
3. 不自动改 SKILL.md——任何修改都以候选 + 盲测 + 回滚的方式走，最终覆盖由你批准。

## 3. 触发边界（沿用你的候选规格 06-未来薄Skill候选规格）

应触发：

- 「帮我设计 / 审计 / 迭代一个 skill」
- 「这个 skill 为什么触发错 / 跑不好」
- 「把这次翻车变成一个 skill 的修复方案」

不应触发：

- 通用问答；直接要写某个具体 skill 的正文（那是 nuwa-skill / skill-darwin-lite 的活）；人格塑造；对一切任务强制加载。

## 4. 流程骨架（三阶段，每阶段复用现有资产）

| 阶段 | 干什么 | 复用资产 |
|---|---|---|
| 设计 | 定 skill 的合同：目标、触发边界、流程、验证钩子、回写口子 | `03-Harness-设计合同.md`（四种厚度、必填设计对象）、`06-未来薄Skill候选规格.md` 的三个风险当检查单 |
| 审计 | 对已有 skill 出证据：触发对不对、跑没跑通、验证钩子在不在 | `ITERATION-HARNESS.md`（证据类型 SOURCE_PRINCIPLE / OBSERVED_FAILURE / ENGINEERING_INFERENCE / DECISION、任务包格式） |
| 迭代 | 一条窄假设 → 候选 v2 → 盲测 → 你批准替换或回滚 | `skill-darwin-lite` 的流程、`loop-engine` 的回滚与追溯 |

## 5. 与现有 skill 的分工表

| skill | 管什么 | 元 Skill 不碰 |
|---|---|---|
| skill-darwin-lite | 单 skill 的达尔文式优化执行 | 元 Skill 只路由到它，不重复它的盲测流程 |
| loop-engine | Loop / 工作流的受控迭代 | 元 Skill 在 skill 场景调用它 |
| nuwa-skill | 从人 / 主题蒸馏出 skill | 元 Skill 负责蒸馏之后的合同与验收 |
| engineering-meta | 工程项目的 meta 流程 | 元 Skill 只覆盖 skill 这一窄对象 |
| codex-self-optimization | Codex 本地行为系统优化 | 不覆盖，明确排除 |

## 6. 验收标准（可判分）

1. 用元 Skill 跑一次真实审计：对 dbs-learning 出报告，报告里每条结论带证据类型；
2. 用元 Skill 跑一次真实迭代：一条窄假设 → 候选 → 盲测 → 你批准 / 拒绝，全程有回滚点；
3. 两轮跑完，写 experience-log，由你验证进策略层。

## 7. 开放问题（等你决策）

1. 名字：`audit-intelligence-environment`（你候选规格里的名字）还是别的？
2. 形态：薄壳路由层（推荐，本稿假设）还是独立 harness（更重，和工程 meta 重叠）？
3. 第一份审计对象：dbs-learning（顺理成章，它刚被我们改过）还是别的？
