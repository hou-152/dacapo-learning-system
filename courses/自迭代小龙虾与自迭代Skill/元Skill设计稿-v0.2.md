# 元Skill 设计稿 v0.2（决策已锁定，待最终 OK 安装）

> 状态：研究完成，方案定稿，**未安装**。
> v0.1 → v0.2 变化：名字定 `skill-meta / 元Skill`；形态定薄壳路由层；首份审计对象定 ai-native-helpdesk。

## 1. 锁定决策

| 项 | 决策 | 来源 |
|---|---|---|
| 名字 | `skill-meta`（中文名：元Skill） | 用户 2026-08-25 |
| 形态 | 薄壳路由层，不新造机制 | 用户 2026-08-25 |
| 首份审计对象 | ai-native-helpdesk（含 6 个 aihd-* 子 skill） | 用户 2026-08-25 |
| 安装位置 | `~/.agents/skills/skill-meta/`（待 OK） | 沿用既有 skill 目录 |

## 2. 职责（4 件事）

识别阶段 → 定合同 → 出证据 → 路由执行。设计走 Harness 设计合同；审计走 ITERATION-HARNESS 证据类型；迭代路由到 skill-darwin-lite + loop-engine。

## 3. 三条硬规则

1. 不自动改 SKILL.md：任何修改走「候选 + 盲测 + 回滚」，最终覆盖由用户批准；
2. 不新造机制：只路由，不发明新流程；
3. 审计结论必须带证据类型（SOURCE_PRINCIPLE / OBSERVED_FAILURE / ENGINEERING_INFERENCE / DECISION）。

## 4. 首份审计计划（ai-native-helpdesk）

审计视角 = 证据视角，分五组：

1. **合同核对**：front-matter 声称（v1.2.0、SUB_SKILL_NAVIGATION / RELEASED / PRODUCT_VALIDATION_UNKNOWN）与正文实际职责是否一致；
2. **四部件体检**：front-matter / 触发（三模式触发词）/ 流程（模式 A/B/C）/ 验证钩子（对话宪法第 6 条 validation 已有——体检它的执行率）；
3. **交付物 vs 合同 diff**：主 skill「只做 4 件事」声称与实际职责逐条对；子 skill 行数规范 vs 实际（上次验收报告问题 #9：6 个里 4 个超 100 行）；
4. **已知问题回放**：上次验收报告 11 个问题中，哪些属于 SKILL.md 可修（进入迭代候选），哪些属于教程文档（移出 skill 审计范围，单独立项）；
5. **触发实测**：3-5 条测试消息走判模（「我今天做不动了」→ diagnosis；「然后呢」→ 模式 B；红线样例 → 守门），记录实际路由 vs 合同预期路由。

## 5. 第一个回归案例（你的东坡肉）

你描述的 Codex 行为「要番茄炒蛋 → 交付东坡肉 → 整改后交付无东坡肉版番茄炒蛋 + 加料」收进元Skill 的验收用例，命名：**合同漂移（scope drift）**。审计时专查一类问题：skill 的执行是否在用户合同之外添加了未要求的机制。这是「交付物 vs 合同 diff」检查项要防的核心病。

## 6. 验收标准（元Skill 自己的第一圈）

1. 对 ai-native-helpdesk 出审计报告：每条结论带证据类型，每条问题配最小修复动作；
2. 你从报告里挑 1 条进入迭代（或不挑，明确判定）；
3. 本轮运行后写 experience-log，策略层规则由你验证。

## 7. 待你最终 OK 的动作

1. 把 `元Skill-SKILL.md草案.md` 安装为 `~/.agents/skills/skill-meta/SKILL.md`；
2. 跑首份审计（按第 4 节五组清单），报告交你决策。
