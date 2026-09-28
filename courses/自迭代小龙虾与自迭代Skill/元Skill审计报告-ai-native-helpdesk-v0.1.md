# 元Skill 首份审计报告：ai-native-helpdesk

> 审计方：skill-meta v1（薄壳路由层）
> 审计对象：`~/.agents/skills/ai-native-helpdesk/SKILL.md` + 6 个 aihd-* 子 skill
> 审计方式：静态审计（读文件 + 文档比对 + 判模表静态回放）。运行时行为未实测，与对象自身声明 PRODUCT_VALIDATION_UNKNOWN 一致。
> 证据类型：SOURCE_PRINCIPLE（原文主张）/ OBSERVED_FAILURE（实测失败或冲突）/ ENGINEERING_INFERENCE（机制推导）/ DECISION（裁决）
> 日期：2026-08-25

## 组 1：合同核对（声称 vs 实际）

| # | 结论 | 证据 |
|---|---|---|
| 1.1 | 版本与状态声称一致 | SOURCE_PRINCIPLE：front-matter v1.2.0 / SUB_SKILL_NAVIGATION / RELEASED / PRODUCT_VALIDATION_UNKNOWN，与正文「当前状态」「修订记录」逐项一致 |
| 1.2 | 无合同漂移 | SOURCE_PRINCIPLE：正文声明「只做 4 件事：守门、判模、路由、交接」，模式 A/B/C 是运行模式而非第 5 件事；未发现加料机制 |
| 1.3 | fail-closed 声明自洽 | SOURCE_PRINCIPLE：不随包携带知识库、SOURCE_UNAVAILABLE 不编造、子 skill 缺失不模拟，三处声明互相一致 |

## 组 2：四部件体检

| 部件 | 结论 | 证据 |
|---|---|---|
| front-matter | ✓ | SOURCE_PRINCIPLE：name / description（三模式触发词 + 使用场景）/ license / metadata 齐全 |
| 触发 | ✓ | SOURCE_PRINCIPLE：模式判定规则明确（新手→C、带问题→A、然后呢→B）；子 skill 可独立触发已声明 |
| 流程 | ✓ | SOURCE_PRINCIPLE：A/B/C 流程步骤完整，判模表 6 优先级 + 命中即停 |
| 验证钩子 | ✓ 文本层；执行痕迹缺失 | SOURCE_PRINCIPLE：对话宪法 #6 验证信号 + #8 完成标准；OBSERVED（本轮实测）：6 个子 skill 全部含 validation 语言。ENGINEERING_INFERENCE：验证钩子只有文本定义，无运行回执留存机制，执行率仍 UNKNOWN |

## 组 3：交付物 vs 合同 diff

| # | 结论 | 证据 |
|---|---|---|
| 3.1 | **行数规范失守** | SOURCE_PRINCIPLE：贡献规范「子 skill 每个 ≤ 100 行」；OBSERVED_FAILURE（本轮实测 wc -l）：action 87 ✓ / thinking 94 ✓ / diagnosis 107 / good-question 127 / safety 139 / knowledge 246，6 个里 4 个超限。影响：规范已失守或已废弃，写新子 skill 的人无所适从。最小修复：规范处标注现行上限，或拆分 knowledge（246 行） |
| 3.2 | 主 skill 无其他加料 | SOURCE_PRINCIPLE：术语表、修订记录、失败规则均为支撑件，与 4 件事职责不冲突 |

## 组 4：已知问题回放（2026-08-23 验收报告 11 条）

| 分类 | 条数 | 处理 |
|---|---|---|
| 使用教程文档问题（#1-8、#10、#11） | 10 | DECISION：移出 skill 审计范围，单独立项「ai-native-helpdesk 使用教程修订」 |
| skill 本体问题（#9 行数规范） | 1 | 已并入本报告 3.1 |

## 组 5：触发实测（静态回放，运行时需你实测）

按判模表推导（ENGINEERING_INFERENCE）：

| 测试消息 | 合同预期路由 | 一致性 |
|---|---|---|
| 「我今天什么都不想做，一直拖延」 | 守门无红线 → 判模 2 心理/动机 → aihd-diagnosis | ✓ |
| 「OpenClaw 的 dreaming 插件怎么开」 | 判模 4 事实查询 → aihd-knowledge | ✓ |
| 「为什么我的小龙虾定时任务总是超时」 | 判模 5 因果 → aihd-thinking | ✓ |
| 刚完成回答后「然后呢」 | 模式 B 导航 | ✓ |
| 「帮我看看这篇为什么没流量」 | 信号优先于字面 → aihd-thinking | ✓ |

红线路径不实测；守门规则与 `aihd-safety` 参考文档一致（SOURCE_PRINCIPLE）。

## 审计总评

- 主 skill 本体质量高：四部件齐、验证钩子存在、fail-closed、无合同漂移——你之前担心的「东坡肉式加料」在这个 skill 上没有发现。
- **迭代候选 2 条**：3.1 行数规范失守；组 2 验证钩子无执行痕迹留存。
- **外移 1 项**：使用教程修订（10 条）单独立项。
- 运行时验证（判模真实命中率）需你在真实环境跑 5 条测试消息回填。

## 待你裁决

1. 迭代候选 3.1 / 组 2，挑 1 条进迭代，或都先不挑（明确判定即可）；
2. 使用教程修订是否单独立项；
3. 组 5 的 5 条测试消息，你在真实环境跑一遍，把实际路由回填给我。
