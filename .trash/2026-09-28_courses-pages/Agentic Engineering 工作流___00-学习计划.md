course:: [[Agentic Engineering 工作流]]
mirror:: true
source-path:: `../Agentic Engineering 工作流/00-学习计划.md`

# Agentic Engineering 工作流｜学习计划

## 学习目标

把 Kun Chen 的 `Principal's Agentic Engineering Workflow` 拆成一套可复述、可迁移、可执行的 Agentic Engineering 工作系统。学习完成后，应能说明：人作为船长负责什么，Agent 作为船员负责什么，记忆、技能、工具、并行工作树、验证流水线和 First Mate 分别解决什么问题。

## 当前进度

- 当前文章：11.5
- 最近更新：2026-07-10
- 下一步：等待 11.5.md 的 6 行最小学习运行记录；通过后回到总操作卡

## 学习路径

1. 建立总图：用“船长、船、船员、第一副手”的比喻理解整套工作流。
2. 拆分部件：逐步学习终端工作面、记忆文件、技能、单 Agent 协作、多 Agent 并行和验证流水线。
3. 迁移到自己：把每个部件转成自己的 Codex / Claude / Reader / 本地项目工作习惯。

## 学习状态

- 当前理解状态：11 已结算，部分理解；能分开 Human agent 与 Codex agent，仍混淆目标、状态、执行方式和可见结果
- 最近卡点：写出一条可检查的最小学习运行记录
- 最近兴趣方向：Agent 工作流的新瓶颈、Harness Engineering、AI 开发里的 loop 设计
- 下一次理解检查：回答 11.5.md 的 6 行最小学习运行记录

## 费曼验收

- 本轮口头费曼等级：未做
- 生成状态：课程主链条已完成，尚未做完整口头费曼
- 编码状态：结构编码需要通过一次总图复述确认
- 暴露漏洞：如果用户无法把各层职责讲顺，需要补对应漏洞篇
- 下一步修正：根据口头费曼或真实任务反馈，决定补“目标元 skill”“隔离检查 skill”或“验证证据模板”

## 反馈摘要

| 文章 | 用户反馈 | 学习状态判断 | 下一步调整 |
|---|---|---|---|
| 01 | 新课题，无上一轮学习反馈；来源是 Reader 文档 `L8 Principal's Agentic Engineering Workflow` | 信号不足；先建立总图 | 用小步推进方式讲清船长模型，再进入终端环境和工作面 |
| 02 | Reader 反馈关注船长指令清晰度、项目元技能、Single crewmate 门槛、chatroom 式方案讨论和验证证据 | 应用中；已能抓住船长模型，但需要拆清 onboarding 与 loop 的边界 | 把 Ship 讲成稳定指挥中心，并把单 Agent 跑通作为进入多 Agent 前的硬门槛 |
| 03 | Reader 反馈把 onboarding 理解为错题本，关注高质量长指令、线性/总调度多 Agent 模式，以及“给 Agent 验收”和“给我验收”的区别 | 应用中；已能提出迁移问题，适合转成操作卡 | 先把错题本沉淀成 Agent 入职卡，拆清 memory、skill、项目元提示词和验收清单 |
| 04 | Reader 反馈追问常见错误能否全部丢进建站元技能，以及 memory / skill / 项目元提示词的判断条件能否交给 AI | 应用中；适合把规则记忆负担转成 AI 分流和双层验收 | 讲清错误分流、Agent 自查、人类判断三层边界 |
| 05 | Reader 反馈较少，主要划线集中在分流器、错误收集和长期变重风险 | 信号偏少但主线清楚；适合按预告小步推进 | 把分流器迁移到多 Agent，拆线性接力、并行分工和总调度三种模式 |
| 06 | Reader 反馈关注多 Agent 前置门槛、工程化发挥 Agent 智商、以及“谁尽力谁犯罪”的合并责任问题 | 准备应用；分类已基本理解，卡点转向隔离、权限、证据和合并规则 | 讲 worktree、memory / skill 统一入职材料、并行隔离检查卡和合并规则 |
| 07 | Reader 反馈集中在状态、日志、上下文、目标澄清、元 skill 设计和“谁变成大脑”；用户澄清“目标”是误输入，继续按 learning skill 推进 | 准备应用；隔离层已能理解，卡点转向状态调度和职责分层 | 按原计划讲 First Mate，说明它如何接管任务拆分、状态表、验证推进和升级规则 |
| 08 | Reader 反馈把 No Mistakes 拆成“底层风险 → 对应动作”，并指出文章偏技术、有难度 | 准备应用；已能自建风险映射，适合把技术流程转成判断框架 | 用风险闸门讲验证流水线，让每一步都对应一个可理解的失败模式 |
| 09 | Reader 反馈较少，主要划线集中在 First Mate、验证问题清单、原始意图、合并冲突和端到端证据 | 主链条可收束；适合把前 8 篇合成迁移总图 | 收束总图，并把下一步改成口头费曼或真实任务反馈驱动 |
| 10 | 用户从内参候选中明确选择“Agent 闭环工程：从 Prompt 到 Loop / Harness / 验证”；答题后暴露“不是程序员出身”和行动接口未写硬 | 部分理解；Loop / Harness 方向能抓住，但五槽和四槽没有落到可执行格式 | 已生成 10.5.md，补“最小 Codex loop 行动接口” |
| 10.5 | 承接 10.md 答题和批注：`有点困难，我不是程序员出身`、`dbs-learning...当我可以阅读 ok 了`；用户答题写出 `Loop 就是流水线，Harness 就是车间` 和 `agent 完成指令，这样就算完成了` | 部分理解；比喻有效，但完成标准仍然不够可验收 | 已生成 `10.6.md`，补“证据齐全才算完成” |
| 10.6 | 用户指出题目主体歧义，并改用 Human agent 的学习执行任务：阅读、打开文件、Typeless 费曼、停止；补充低模型代工和交叉学习的模型路由 | 基本掌握；Human Loop 与模型路由已能落地 | 已生成 `11.md`，收束为总操作卡 |
| 11 | 承接 Human agent 的真实学习操作和模型路由判断 | 等待答题 | 用 4 行操作卡跑一次真实学习任务 |
| 11.5 | 11 的答案把目标、状态、执行方式和可见结果混在一起 | 部分理解；需要一个可检查的最小运行记录 | 用 6 行完成一次学习运行 |

## 来源记录

| 日期 | 类型 | 路径或说明 | 用途 |
|---|---|---|---|
| 2026-06-25 | Reader 视频转写 | https://read.readwise.io/read/01kvr3g2vyrznv6chm8gqhvc6v | 作为第 1 篇和后续课程的核心材料 |
| 2026-06-25 | 用户消息 | 用户发送 Reader 链接并指定 `dbs-learning` | 确定使用交互式学习工作流生成连续课程 |
| 2026-06-25 | Reader highlights / notes | https://read.readwise.io/read/01kvzja13644zz77d0593d78d7 | 作为第 2 篇反馈来源，调整为“稳定指挥中心 + 单 Agent 门槛 + onboarding/loop 边界” |
| 2026-06-25 | Reader 同步 | https://read.readwise.io/read/01kvzksrxy1cszvn3k3yqjdggs | 第 2 篇已同步到 Reader，供下一轮划线和反馈 |
| 2026-06-25 | Reader highlights / notes | https://read.readwise.io/read/01kvzksrxy1cszvn3k3yqjdggs | 作为第 3 篇反馈来源，调整为“错题本式 onboarding + memory/skill/元提示词边界” |
| 2026-06-25 | Reader 同步 | https://read.readwise.io/read/01kvzn36zd1r35wfesd3h34yq2 | 第 3 篇已同步到 Reader，供下一轮划线和反馈 |
| 2026-06-25 | Reader highlights / notes | https://read.readwise.io/read/01kvzn36zd1r35wfesd3h34yq2 | 作为第 4 篇反馈来源，调整为“错误分流 + 双层验收” |
| 2026-06-25 | Reader 同步 | https://read.readwise.io/read/01kvzpgwazstysbs21zq28aqsz | 第 4 篇已同步到 Reader，供下一轮划线和反馈 |
| 2026-06-26 | Reader highlights / notes | https://read.readwise.io/read/01kvzpgwazstysbs21zq28aqsz | 作为第 5 篇反馈来源，基于分流器主线小步推进多 Agent 模式 |
| 2026-06-26 | Reader 同步 | https://read.readwise.io/read/01kvzym6dtgq858fgdrh3mfyhr | 第 5 篇已同步到 Reader，供下一轮划线和反馈 |
| 2026-06-26 | Reader highlights / notes | https://read.readwise.io/read/01kvzym6dtgq858fgdrh3mfyhr | 作为第 6 篇反馈来源，回应工程化边界、隔离检查和合并责任 |
| 2026-06-26 | 用户消息 / 并行 agent 取证 | 用户要求按“Agent A/B/C 并行分工，最后合并成下一篇课程”行动 | 分别分析 memory / skill、multi Agent / worktree 和 Reader 真实卡点，再合并为第 6 篇 |
| 2026-06-26 | Reader 同步 | https://read.readwise.io/read/01kw009s178f4kxnbdctr0nqsy | 第 6 篇已同步到 Reader，供下一轮划线和反馈 |
| 2026-06-26 | Reader highlights / notes | https://read.readwise.io/read/01kw009s178f4kxnbdctr0nqsy | 作为第 7 篇反馈来源，回应状态日志、元 skill、职责分层和 First Mate 调度 |
| 2026-06-26 | 用户消息 | 用户澄清“目标”是误输入，实际是 OK，按 learning skill 继续 | 修正第 7 篇方向，按学习计划推进 First Mate |
| 2026-06-26 | Reader 同步 | https://read.readwise.io/read/01kw01x4e2bx53q7hthtmr15me | 第 7 篇已同步到 Reader，供下一轮划线和反馈 |
| 2026-06-26 | Reader highlights / notes | https://read.readwise.io/read/01kw01x4e2bx53q7hthtmr15me | 作为第 8 篇反馈来源，基于用户的风险映射讲验证流水线 |
| 2026-06-26 | Reader 同步 | https://read.readwise.io/read/01kw036e8mb1f7qntn300aq17b | 第 8 篇已同步到 Reader，供下一轮划线和反馈 |
| 2026-06-26 | Reader highlights / notes | https://read.readwise.io/read/01kw036e8mb1f7qntn300aq17b | 作为第 9 篇反馈来源，基于划线点收束 Agentic Engineering 迁移总图 |
| 2026-06-26 | Reader 同步 | https://read.readwise.io/read/01kw1m1b202a66z4qapya9v2z8 | 第 9 篇已同步到 Reader，供口头费曼或真实任务反馈 |
| 2026-07-09 | neican 内参 | `assets/260706-260708-agent-loop-harness-source-index.md` | 第 10 篇主教材索引：人的注意力、Harness Engineering、loop 设计 |
| 2026-07-09 | 用户消息 | 用户确认选择“Agent 闭环工程：从 Prompt 到 Loop / Harness / 验证” | 将新材料作为旧课题补充篇，避免新建平行课题 |

