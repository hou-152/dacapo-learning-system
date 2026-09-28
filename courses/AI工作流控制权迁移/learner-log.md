# 学习证据账本

<a id="lesson-01"></a>

- lesson: 01
  status: settled
  note: 已完成，route=advance

- lesson: 02
  status: settled
  route: advance
  mastery_band: partial
  note: 2026-07-14 重写版已结算。学习者完成原答并实际执行了任务锚点→检索→证据包组装。对来源池/证据包的操作层理解正确（实际筛选了 4 篇候选，3/4 命中锚点），但概念层仍有缺口（将来源池理解为”增强搜索”而非”被搜索的索引”；搜索机制明确不懂）。
  prior_gap: source-pool-vs-evidence-pack
  learner_evidence: |
    检查站回答：剩余 12 篇”可以用来增强搜索，比如遇到比较新的前沿问题，可以从中搜索相关资料”。方向对，但混淆了”搜索目标”和”搜索增强器”。
    费曼练习：实际执行了证据包组装——搜了内参、筛出 4 篇候选（Harness Engineering / Skills→可复用工作流 / Agent 注意力瓶颈 / AI 毁掉技能）、区分了”能入选”和”有用但不入选”。
    元问题：追问”规则升级从哪想来的”——对方法论本身有反思意识。
    明确缺口：”具体的搜索机制，不是很懂”。
    Loop 理解：停留在”就是一个循环”的字面理解。
  passed_dimensions: [迁移]
  gap_ids: [search-mechanism, loop-as-decision-cycle]
  posterior_judgment: 操作层的证据包组装已掌握（实际筛选正确）。需要将概念层的两个缺口（搜索三阶段机制、Loop 作为决策状态机）在 03 中补上。
  belief_update: up
  next_action: 进入 03，桥接检索机制与 Loop。

- lesson: 03
  status: settled
  route: advance
  mastery_band: partial
  note: 2026-07-14 已结算。学习者完成费曼练习（结构化记录了找文章的四步流程）和检查站（Loop vs 循环的区分——"有没有自己的判断"，用质量门描述 Loop 的决策机制）。搜索机制缺口大部分闭合（描述了实际的过滤行为），Loop 理解从"就是一个循环"升级到"判断力介入的闭环"。两个轻微缺口：任务锚点仍停留在搜索任务层而非内容判断层；停止条件是"翻不到了"而非"证据够了"。
  learner_evidence: |
    费曼练习——任务锚点："我要去找什么文章才能去支持或者是推翻这些观点？"（搜索任务层）。检索动作：在 AI 内参搜索栏搜 skill，翻了约 15 篇。过滤规则：一篇讲 Heron's skill 和工作流关系的文章"没有提出明确的观点，仅仅是讲了一个面"→淘汰。停止条件："找了大概 15 篇左右，觉得差不多了，再往下面找就找不到了"（资源耗尽型停止）。
    检查站——Loop vs 循环区分："核心区别在于有没有自己的判断"。循环=自动化重复，"继续干"。Loop=判断力介入，每个任务有"是/否"阶段，通过才推进、不通过则回退。观察="浏览整个搜索页面，看哪个结果是符合我要求的"。决定下一步="当我判断'可能够了'的时候"。
  passed_dimensions: [机制, 迁移]
  gap_ids: [task-anchor-formulation, stop-condition]
  posterior_judgment: 搜索机制和 Loop 概念的理解已基本到位。任务锚点从"搜索任务"下沉到"内容判断"层可在 04 费曼练习中自然校准。停止条件从"翻不到了"升级到"证据够了"是下一步。

- lesson: 04
  status: settled
  route: advance
  mastery_band: partial
  note: 2026-07-14 已结算。学习者完成费曼练习和大量行间批注。三种驱动力理解到位（模型内化+控制迁移+注意力瓶颈），形成"人在回路"的自主框架。任务锚点偏差已确认（搜索层vs内容判断层）。关键产出：将"AI不外包判断"精炼为"能外包思考过程，不能外包理解本身"，并增加限定——简单工程判断（yes/no、0/1）可让AI介入。明确缺口：Harness Engineering（"真不理解"）、Workflow（"不太了解"）。检查站未答。
  learner_evidence: |
    四阶段理解——Prompt："提示词其实是一个特定思维的包装（第一性原理、贝叶斯、剃刀原则、费曼）"。Skill："核心是默会——把隐性知识给显性化，但有些默会知识和暗知识无法用言语表达，这就是Skill时代的局限性"。Workflow："确实不是很了解，但知道是由很多Skill组成的，中间出错它并不知道错在哪"。Loop："核心在于把一些判断丢给AI，让AI实现自动化，每个Loop阶段产出由AI判断，OK就过"。
    驱动力A："当智能越来越强的时候，有些东西它就不用提。人聪明一点，工作态度就会好一点——但我现在还属于不够聪明的人，没法证实也没法证伪"。
    驱动力B："Harness Engineering 我不是很理解，比如外部模型的调度、验证、安全和反馈，这个我是真不理解。但玩AI跟管理学、哲学、心理学都有关，要求的是内功不是外功"。
    驱动力C：认同注意力瓶颈判断。
    费曼——两种驱动力并存：模型能力内化+工程控制点迁移（"人在回路"）。人介入频率降低但核心判断不被取代，与注意力碎片化（抖音等短平快内容）直接相关。Harness文章最有力支持（"人的核心价值收敛到定义需求与审视结果"），限定条件=50%低风险改动可autofix，敏感文件需人工审核。"AI不外包判断"软硬边界：简单工程判断（yes/no、0/1）可外包，核心价值判断不可外包。
    精华表述："它能外包你的思考过程，但不能外包你理解本身"。
  passed_dimensions: [准确性, 迁移]
  gap_ids: [harness-engineering, workflow]
  posterior_judgment: 三种驱动力和演化线的概念理解已到位。关键分化发生在"理解本身vs思考过程"的区分上——这是整个课题的核心判断力。Harness Engineering是从概念到工程的最后一里路，需要用他自己的系统（CLAUDE.md、memory、工具）当例子拆解，而非讲技术概念。

- lesson: 05
  status: settled
  route: advance
  mastery_band: strong
  note: 2026-07-14 已结算。Harness 缺口大幅闭合。用户完成 5 层费曼分析（规则/记忆/工具/验证/公理），每层有具体例子。关键突破：与 GPT 对话后自主推导出"厚 harness、薄 skill、强 model"公式，推翻 GPT 的"薄 skill、厚 model"结论。小问题：CLAUDE.md 路由表 vs Workflow 区别待澄清。检查站诚实回答"我系统里其实我不清楚"。
  learner_evidence: |
    质疑 CLAUDE.md 分类："这个跟工作流的区别是什么？就是这个系统文件，我记得我给它备注的，更多的是一些记忆或者文风之类类似提示词的东西"。
    突破时刻——与 GPT 对话后："GPT 跟我说现在更倾向于'薄 parameters、薄 skill、厚模型'...等一下，现在更接近'厚 harness、薄 skill、强 model'。哦，我懂你意思了，开始走通了。" 自己推翻了 GPT 的结论并合成到 dbs-learning 框架。
    费曼 5 层分析——规则层："定时心跳 Heartbeat，在特定时间执行某些 skill"；记忆层："统一存在 Harness 里，Agent 交互方式、任务、边界"；工具层："基于 MCP，明确能/不能用，不能死循环、不能泄露 API Key"；验证层："review agent 对抗性审计，两份报告（Agent 看+人看），人最终把关"；公理层："强约束硬指标，不能不懂装懂"。
    检查站："我系统里面其实我并不清楚"已有 Harness 规则。"把 AI不外包判断从 prompt 移到 Harness，实际需要改 agent 这个文件"。
  passed_dimensions: [准确性, 机制, 迁移]
  gap_ids: []
  posterior_judgment: Harness 缺口从"真不理解"到能自主推导"厚 harness、薄 skill、强 model"——这是整个课程到目前为止最大的单次认知跃迁。下一步：把这个公式落到具体 Skill 设计里（四字段薄 Skill）。

- lesson: 06
  status: settled
  route: advance
  mastery_band: strong
  note: 2026-07-14 已结算。强模型三类内容理解到位。费曼练习部分完成——用户用自然语言描述了三级笔记 Workflow 的操作流程，但未按四字段格式化。检查站 Q1 正确（superpower 约束 + 人设描述被取代），但不喜欢"思考脚手架"这个词。Q2 方向对但映射关系轻微缠住——把"厚=内化"和"薄=控制迁移"颠倒了（应该是：强模型内化→薄Skill；控制迁移→厚Harness）。其他产出精彩：AI 行业"两条腿走路"分析、成本驱动的模型路由（简单→Flash/DeepSeek、难→Fable 5）、"什么都重要就等于什么都不重要"。
  learner_evidence: |
    费曼——三级笔记 Workflow："丢给它文章，输入触发条件'/'和三级笔记 Skill。动作：使用三级笔记压缩方法，不要过度压缩文章。产出后让 Agent 让人看一眼确认"。未格式化成四字段但操作逻辑完整。
    检查站 Q1——强模型吃掉的：superpower 型约束（Agent 必须完整写出 Plan/Brief/PRD），这部分取代了人设描述。不喜欢"思考脚手架"这个词。
    检查站 Q2——“厚启薄发”公式 vs 驱动力关系："厚=强模型内化（把人设类、规范类部分内化）。薄=去驱动力+控制迁移变成具体 Skill。共同产出=对人吝啬的注意力——什么都重要就等于什么都不重要"。
    附——AI 行业判断：中国做垂直专业化 vs OpenAI/Anthropic 做通用智能。垂直应用是"智能不足时的妥协"。现在两条腿走路。企业落地的瓶颈是成本：简单任务分流到便宜模型（GPT-4o Flash/DeepSeek），难任务给 Fable 5。
  passed_dimensions: [准确性, 机制, 迁移]
  gap_ids: [formula-driving-force-mapping]
  posterior_judgment: 薄 Skill 和厚 Harness 的概念各自掌握了，但两套框架（三词公式 vs 三种驱动力）之间的映射还差一次对齐。在 07 开头做一次快速映射修正即可，不构成阻塞。可以进入综合阶段——把全部概念串成最小 Loop。

- lesson: 07
  status: settled
  route: advance
  mastery_band: strong
  note: 2026-07-14 已结算。Loop 概念达到 AHA——"Loop 给我的震撼很大，它其实就有点像小龙虾"，在自己系统中认出了 Loop 模式。提出三条第一性原理问题（最小 Loop / 五个词 / 小龙虾），从概念学习进入原理追问。检查站写了详细五阶段运行流程，自认"验证和决策说得比较纰漏"，正确指出"三级笔记最缺心跳"。Harness 理解精确——"Claude Code 就是 DeepSeek 的 harness = 封装"。费曼练习未完成（没画 Loop 格式图），但在做更高层次的综合。公式 vs 驱动力映射已纠正。
  learner_evidence: |
    AHA时刻——"我操，我觉得你这个 Loop 给我的震撼很大，它其实就有点像小龙虾。你能不能就从第一性原理给我讲一下：最小 Loop 的第一性原理是什么？这几个词的第一性原理是什么？小龙虾的第一性原理是什么？"
    Harness 理解——"模型是 DeepSeek，我一般会去接 Claude Code，而 Claude Code 就是它的 harness。也就是说，我要去用一些东西让这个 DeepSeek 封装起来，让它变得很牛逼。" 精确：模型=处理，Harness=剩下四个阶段。
    检查站——五阶段流程写完整：心跳=定时检测工作空间新内容并预处理；输入=提取内容丢给 Agent 对话窗口；处理=大模型按工作流处理（LLM Wiki方式）；验证=检查内容是否合格；决策=确认通过进入下一步。自认"三级笔记最缺心跳"。
  passed_dimensions: [准确性, 机制, 边界, 迁移]
  gap_ids: []
  posterior_judgment: 从概念吸收进入原理层追问——这是学习梯度上升的信号，不是缺口。终篇（08）应该用第一性原理回答收束，帮用户把七篇的零散洞察压成可发布、可验证的个人判断。

- lesson: 08
  status: settled
  route: complete
  mastery_band: strong
  note: 2026-07-14 终篇已结算。课程完成。用户将 Loop 连接到生物学负反馈调节（更深层原理），识别 Loop 的复利效应。检查站用三句话正确概括第一性原理（触发条件→处理→负反馈调节）。费曼练习部分完成（提出"性价比"验证方向但未形成完整判断段落）。从"Harness Engineering 真不理解"到独立推导"厚 Harness、薄 Skill、强模型"——整个课程最大的认知跃迁已完成。
  learner_evidence: |
    Loop 连接生物学——"哎我操，这他妈的有点像那个生物里面的反馈调节。可能叫做负反馈调节。" 将 Loop 识别为控制论/生物学的通用结构。
    复利系统——"其实这个 loop 是一个复利系统。只要它一直是正向的调整，它其实能够变得很好。但对这个系统我还不是很了解。" 识别 Loop 的累积改进效应。
    费曼——"在保证产出的结果不变的情况下，能不能用更有性价比的方式？" 关注成本效益验证但暂未形成完整方案。
    检查站——Loop 第一性原理："1. 反馈的触发条件 2. 反馈的处理 3. 反馈的负反馈调节"。三句话，正确且简洁。
  passed_dimensions: [准确性, 机制, 边界, 迁移]
  gap_ids: []
  posterior_judgment: 课程完成。用户的核心收获不是八个概念，而是三个自己推导的洞察——"能外包思考过程不能外包理解本身"（04）、"厚 Harness 薄 Skill 强模型"（05）、"Loop=负反馈调节"（08）。这三个是用户自己走通的，不是被教的。下一步建议：改一个真实 Skill（三级笔记或龙虾日报）为四字段，加心跳，跑一圈，用实际运行结果修正判断。
  course_outcome: |
    终局能力达成：能独立判断 AI 工作流中哪些应常驻、哪些应按任务状态调用；能为自己的系统提出可验证的改造方案。
    用户形成个人判断：AI 工作流控制权正在从模型内部迁移到模型外部，驱动力来自模型内化+控制迁移+注意力瓶颈三重叠加，最终形态是厚 Harness+薄 Skill+强模型，人只在高价值判断节点介入。
    验证方案已建立：Harness 变薄/介入频率不降/薄 Skill 不可行三个验证方向。
