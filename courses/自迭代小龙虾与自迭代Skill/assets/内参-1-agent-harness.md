# LangChain 解剖 agent harness：Agent = 模型 + harness

- 原文标题：The Anatomy of an Agent Harness
- 作者：blog.langchain.com
- 内参日期：2026-07-31
- 来源类型：blog
- 原文：https://blog.langchain.com/the-anatomy-of-an-agent-harness/
- 标签：harness engineering, agents

> 把智能归于模型、把可用性归于 harness，逐项定义当下和未来 agent 需要的核心组件。适合当本主题的结构化索引先读。

## 导读

agent = model + harness

## 核心观点

- 全文的核心等式：**Agent = Model + Harness**。模型承载智能（the model contains the intelligence），harness 是让这份智能变得有用的那个系统（the harness makes that intelligence useful）。
- harness 的定义用的是减法：**If you're not the model, you're the harness.** 凡是不属于模型本身的代码、配置和执行逻辑，都是 harness。
- 作者 Vivek Trivedy 明确说，切分 agent 系统的方式有很多种，很多都很乱（messy），他之所以选这条最干净的界线，是因为它逼人去做一件事——**designing systems around model intelligence**（围绕模型智能来设计系统），而不是围着模型的缺陷打转。
- 全文方法论是**反向推导**：不列 harness 功能清单，而是从「模型这一原语」出发，按 `Behavior we want (or want to fix) → Harness Design to help the model achieve this` 的模式，一项一项推导出今天和明天的 agent 需要什么组件。
- 推导出的核心组件依次是：文件系统 → bash 与代码执行 → 沙箱与默认工具链 → 记忆与搜索（含上下文管理三件套）→ 长时程自主执行。这些原语不是并列的，越往后越依赖前面的，最后开始「复利」（compound）。
- 对未来的判断是双面的：模型变强会吸走一部分 harness 职责，但 harness engineering 不会因此消失——正如 prompt engineering 至今仍然有价值。

## 什么是 harness：一个用减法给出的定义

- 等式先行：Agent = Model + Harness；一句话版本是 **If you're not the model, you're the harness.**
- harness 是「除模型本身之外的每一段代码、配置和执行逻辑」（every piece of code, configuration, and execution logic that isn't the model itself）。
- 关键判断：**a raw model is not an agent**。裸模型只有在 harness 给了它四样东西之后才成为 agent——state（状态）、tool execution（工具执行）、feedback loops（反馈回路）、enforceable constraints（可强制执行的约束）。
- 作者给出的 harness 具体清单：
- System Prompts（系统提示词）
  - Tools、Skills、MCPs 以及它们的描述（descriptions 本身也算 harness）
  - Bundled Infrastructure：filesystem、sandbox、browser
  - Orchestration Logic：subagent spawning、handoffs、model routing
  - Hooks / Middleware，用于确定性执行：compaction、continuation、lint checks
- 注意清单里「描述」和「hooks」的地位：工具的描述文本、以及那些不经模型决策的确定性中间件，同样是 harness 的一等公民。
- 为什么坚持这条界线：不是因为它最准确，而是因为它把注意力从「模型还差什么」转向「该在模型周围造一个什么系统」。

## 为什么需要 harness：从模型视角反推

- 模型能力的素描非常克制：mostly 吃进 text、images、audio、video，吐出 text，**That's it.**
- 开箱即用做不到的四件事，全部是 harness level features：
- 跨交互维持 durable state（持久状态）
  - 执行代码
  - 获取 realtime knowledge（实时知识）
  - 搭建环境、安装依赖包以完成工作
- 结构性结论：**LLM 的结构要求某种把它包起来的机器**（machinery that wraps them to do useful work）。
- 一个人人都用过的例子：为了得到「chatting」这种产品 UX，我们把模型包进一个 while loop，追踪历史消息并 append 新的用户消息——这已经是一副 harness 了。
- 主线心法：**把想要的 agent 行为，转换成 harness 里的一个实际功能**（convert a desired agent behavior into an actual feature in the harness）。
- harness engineering 的双重作用：帮人类注入有用的先验（inject useful priors）来引导 agent 行为；在模型变强之后，用来「surgically extend and correct」模型——外科手术式地扩展与纠正，让模型完成过去不可能的任务。

## 文件系统：最基础的 harness 原语

- 想要的行为：让 agent 拥有持久存储，能与真实数据打交道，能把塞不进 context 的信息卸载出去，并让工作跨 session 存活。
- 问题根源：模型只能直接操作 context window 里的知识。在文件系统之前，用户只能复制粘贴内容给模型——UX 笨拙（clunky），而且对自主 agent 根本不成立。
- 为什么解法是文件系统而不是别的：**世界本来就在用文件系统干活**，所以模型天然被训练在数十亿 token 的「如何使用文件系统」上。自然的解法就变成——harness 自带文件系统抽象与 fs-ops 工具。
- 文件系统解锁的三件事：
- agent 拿到一个 workspace，可以读数据、代码和文档。
  - 工作可以增量累加和卸载，而不必把一切都攥在 context 里；agent 能存中间产物、维持超越单次 session 的状态。
  - 文件系统是天然的**协作面**：多个 agent 与人类通过共享文件协调，Agent Teams 这类架构就依赖它。
- Git 在文件系统之上加了版本能力：追踪工作、回滚错误、开分支做实验。
- 作者的定位判断：文件系统「arguably the most foundational harness primitive」——后面几乎所有能力都要回来找它。

## bash 与代码执行：一个通用工具

- 想要的行为：agent 自主解决问题，人类不必预先设计好每一个工具。
- 今天主流的执行模式是 **ReAct loop**：模型推理 → 通过 tool call 采取行动 → 观察结果 → 在 while loop 里重复。
- 结构性瓶颈：**harness 只能执行它有逻辑的工具**。如果每个可能的动作都要人先造一个工具，agent 的能力上限就是工具表的长度。
- 解法：给 agent 一个通用工具——bash。于是 harness 自带 `bash`，模型靠写代码并执行来自主解决问题。
- 更本质的说法：bash + code exec 是朝着**给模型一台计算机**（giving models a computer）迈出的一大步，剩下的让它自己想办法。模型可以用代码即时设计自己的工具，而不被固定的预配置工具集束缚。
- 边界澄清：harness 仍然会带其他工具，但代码执行已经成为自主解题的**默认通用策略**。

## 沙箱与默认工具链：安全地执行并验证工作

- 想要的行为：给 agent 一个默认配置正确的环境，让它能安全行动、观察结果、持续推进。
- 为什么不能就地跑：本地执行 agent 生成的代码有风险，而且单个本地环境无法扩展到大规模 agent 负载。
- **沙箱给 agent 安全的运行环境**：harness 连到沙箱里跑代码、检查文件、装依赖、完成任务，得到安全隔离的执行。安全再加码可以做命令 allow-list 和网络隔离。
- 沙箱同时解锁规模：环境可以按需创建、在众多任务上扇出（fanned out）、干完就销毁。
- **好环境自带好的默认工具**：harness 负责配置工具链——预装语言运行时和包，git 与测试用的 CLI，用于网页交互与验证的 browser。
- browser、logs、screenshots、test runners 让 agent 有办法观察和分析自己的产出，从而形成 **self-verification loop**：写应用代码 → 跑测试 → 查日志 → 修错误。
- 归属判定很清楚：模型不会自己配执行环境。**agent 在哪运行、有哪些工具可用、能访问什么、如何验证自己的工作，全部是 harness 级的设计决策。**

## 记忆与搜索：让 agent 持续学习，并对抗上下文腐坏

- 想要的行为：agent 记得住见过的东西，也够得着训练时还不存在的信息。
- 硬约束：模型除了权重和当前 context 之外没有额外知识。既然无法编辑权重，**唯一的「加知识」途径就是 context injection**（上下文注入）。
- 记忆的落点仍然是文件系统：harness 支持 `AGENTS.md` 这类 memory file 标准，在 agent 启动时注入 context；agent 增删改这个文件后，harness 再把更新后的文件载入 context。
- 这构成一种 **continual learning**：agent 把一次 session 的知识持久存下来，再注入到未来的 session。
- 知识截止（knowledge cutoffs）的补法：Web Search，以及 Context7 这类 MCP 工具，让 agent 拿到训练停止之后才出现的信息，比如新的库版本和当下数据。作者的结论是——Web Search 和查询最新上下文的工具，是值得直接烤进 harness 的原语。
- 另一条想要的行为：**agent 的表现不应该随着工作推进而衰减。**
- **Context Rot**：模型在 context window 被填满的过程中，推理与完成任务的能力都会变差。所以 context 是宝贵且稀缺的资源，harness 必须有管理策略。
- 全文最锋利的一句定位：**Harnesses today are largely delivery mechanisms for good context engineering.**（今天的 harness 在很大程度上就是好的上下文工程的投递机制。）
- 三件应对武器：
- **Compaction（压缩）**：处理 context window 快满的情况。没有压缩时，对话超过窗口只能让 API 报错——那不行。压缩会智能地卸载并总结已有上下文，让 agent 继续工作。
  - **Tool call offloading（工具输出卸载）**：大段工具输出会在不提供有效信息的情况下污染上下文。超过阈值 token 数时，harness 只保留输出的头部和尾部 token，把完整输出卸载到文件系统，模型需要时再去取。
  - **Skills 与 progressive disclosure（渐进式披露）**：解决启动时载入过多工具或 MCP server、在 agent 还没开始干活就已经拖垮性能的问题。作者特别点出归属——**模型并没有选择让 Skill front-matter 在启动时进入 context，但 harness 可以支持这件事，替模型挡住 context rot。**

## 长时程自主执行：前面的原语开始复利

- 想要的行为：让 agent 自主、正确地完成复杂工作，并且跨越很长的时间跨度。autonomous software creation 是 coding agent 的圣杯（holy grail）。
- 今天模型的三个具体毛病：early stopping（过早停止）、难以分解复杂问题、工作跨越多个 context window 后失去连贯性（incoherence）。好 harness 必须围着这三点做设计。
- 结构性观察：到这一步，**前面的 harness 原语开始复合叠加**（start to compound）——长时程工作需要持久状态、规划、观察和验证，才能横跨多个 context window 继续推进。
- **文件系统与 git 用于跨 session 追踪工作**：agent 在一个长任务中会产出数百万 token，文件系统持久地捕获这些工作以追踪进展；加上 git，新的 agent 能迅速摸清项目的最新状态和历史；多 agent 协作时，文件系统就是共享的**工作账本**（shared ledger of work）。
- **Ralph Loop 用于让工作继续**：这是一种 harness 模式——用 hook 拦截模型的退出企图，在一个干净的 context window 里重新注入原始 prompt，逼 agent 对着完成目标继续工作。之所以可行，正是因为文件系统在：每一轮都从全新上下文开始，但能读到上一轮留下的状态。
- **规划与自验证用于不跑偏**：
- Planning 是模型把目标分解成一系列步骤；harness 通过好的提示词、以及注入「如何使用文件系统里的 plan 文件」的提醒来支持它。
  - 每完成一步后，agent 受益于对正确性的检查，即 self-verification。实现路径有两条：harness 的 hooks 跑一套预定义测试，失败时把错误信息回灌给模型；或者提示模型独立地自评自己的代码。
  - 验证的价值有两层：把解法锚定在测试上（grounds solution in tests），并为自我改进制造反馈信号。

## 模型训练与 harness 设计的耦合

- 现状：Claude Code、Codex 这类今天的 agent 产品，是**模型与 harness 同时在 loop 里**做的 post-training。这让模型在 harness 设计者认为它「应该天生擅长」的动作上变强——文件系统操作、bash 执行、planning、用 subagent 并行工作。
- 由此形成一个反馈回路：发现有用的原语 → 加进 harness → 用它训练下一代模型 → 模型在自己被训练的那副 harness 里越来越强。循环往复。
- 这种协同演化（co-evolution）对泛化有副作用：**改动工具逻辑会导致模型表现变差。** 作者举的例子是 Codex-5.3 prompting guide 里描述的 `apply_patch` 文件编辑工具逻辑——一个真正智能的模型在不同 patch 方法之间切换本该毫无压力，但「harness 在 loop 里」的训练方式造成了这种过拟合（overfitting）。
- 但关键的反转是：**模型被 post-train 时用的那副 harness，不一定是你这项任务的最佳 harness。**
- 证据一：Terminal Bench 2.0 榜单上，Opus 4.6 在 Claude Code 里的得分远低于同一个 Opus 4.6 在其他 harness 里的得分。
  - 证据二：LangChain 自己**只改 harness**，就把他们的 coding agent 在 Terminal Bench 2.0 上从 Top 30 提到了 Top 5。
- 结论：为你的任务优化 harness，还有大量汁水可榨（a lot of juice to be squeezed out）。

## harness engineering 会走向何处

- 一个必然趋势：模型变强之后，今天住在 harness 里的一部分东西会被**吸收进模型**——planning、self-verification、长时程连贯性都会变得原生，从而需要更少的 context injection。
- 表面推论是 harness 应该越来越不重要。作者的反驳类比很干脆：**正如 prompt engineering 今天仍然有价值，harness engineering 很可能会继续对构建好 agent 有用。**
- 支撑这个判断的是一条区分：harness 今天确实在给模型的缺陷打补丁（patch over model deficiencies），但它同时也在围绕模型智能做系统工程。**一个配置良好的环境、正确的工具、持久的状态、验证的回路，会让任何模型都更高效，与它的基座智能无关。**
- LangChain 把 harness engineering 当作活跃的研究领域，用来改进他们的 harness 构建库 `deepagents`。作者列出三个正在探索的开放问题：
- 编排数百个 agent 在同一个共享 codebase 上并行工作
  - 让 agent 分析自己的 trace，识别并修复 harness 级的失败模式
  - harness 不再预配置，而是为给定任务**即时动态组装**（just-in-time）合适的工具与上下文
- 全文的收束句，也是它自己的定义回环：**The model contains the intelligence and the harness is the system that makes that intelligence useful.**

## 概念网络

### 关键概念

#### Harness（框架 / 马具）

**context**：全文的定义对象。作者用减法给出边界——「If you're not the model, you're the harness」，即「every piece of code, configuration, and execution logic that isn't the model itself」。具体包含 System Prompts、Tools/Skills/MCPs 及其描述、bundled infrastructure（filesystem、sandbox、browser）、orchestration logic（subagent spawning、handoffs、model routing）、以及用于确定性执行的 hooks/middleware。

**费曼一下**：马具本身不产生力气，力气在马身上；但没有马具，马的力气没法变成拉车这件有用的事。harness 就是套在模型外面的那副装备——它不聪明，但它决定了模型的聪明能落到哪里、能不能持续、出错时能不能被纠正。

#### Agent = Model + Harness

**context**：文章的核心等式，也是 TLDR 的第一句。作者强调 raw model is not an agent，模型只有在 harness 提供 state、tool execution、feedback loops 和 enforceable constraints 之后才成为 agent。

**费曼一下**：把「agent」这个模糊的词做了一次因式分解。以后评价一个 agent 好不好，可以分开问两个问题：模型这一项有多强？框架这一项做了多少事？两项是可以独立优化、也可以独立归因的。

#### Harness Engineering（框架工程）

**context**：作者称之为「how we build systems around models to turn them into work engines」——把模型变成工作引擎的系统构建方式。它的两个作用是帮人类注入有用的先验（inject useful priors），以及在模型变强后「surgically extend and correct」模型。

**费曼一下**：不是给模型写更好的提示词，而是给模型造更好的工作环境。就像同一个工人，在工具齐全、流程清晰、有质检环节的车间里，产出会和在空地上完全不同——你改的不是人，是车间。

#### Harness level feature（框架级能力）

**context**：指模型开箱即用做不到、必须由 harness 提供的能力。作者列举四项：维持跨交互的 durable state、执行代码、访问 realtime knowledge、搭建环境并安装依赖包。

**费曼一下**：一个判断归属的分诊标准。遇到 agent 做不到的事，先问它属于「模型不够聪明」还是「没人给它这个能力」。绝大多数看起来像智力问题的失败，其实是第二类——那就不该等模型升级，而该动手改框架。

#### 从期望行为反推 harness 设计

**context**：全文的推导方法，作者写成 `Behavior we want (or want to fix) → Harness Design to help the model achieve this`，并明确说不做穷举清单，而是从「帮模型做有用的工作」这个起点推导出一组功能。

**费曼一下**：不是先看别人的框架有什么组件然后照抄，而是先说清楚「我希望它表现成什么样」，再倒推需要什么机制。这样得到的每个组件都带着理由，日后模型变了、任务变了，你知道哪些该留哪些该扔。

#### Filesystem 作为最基础的 harness 原语

**context**：作者称文件系统「arguably the most foundational harness primitive」。理由不只是好用，还包括一条训练侧的论证——世界本来就用文件系统干活，模型天然在数十亿 token 的文件系统用法上训练过。它解锁工作区、增量卸载与持久状态、以及多 agent 与人类共享的协作面（Agent Teams 依赖它）。

**费曼一下**：给模型一块能写字的白板，而且是它从小就学会用的那种白板。context window 是短期记忆，文件系统是长期记忆兼公共桌面——后面的记忆、Ralph Loop、长时程协作，全都要回到这块白板上。

#### ReAct loop

**context**：文中指出今天 agent 的主要执行模式——模型推理、通过 tool call 采取行动、观察结果，在 while loop 中重复。它同时暴露了一个结构性瓶颈：harness 只能执行它有逻辑的工具。

**费曼一下**：想一步、动一下、看一眼结果、再想下一步。这个循环本身很朴素，真正决定上限的是「动一下」这一步能动用什么——如果工具表是固定的，agent 的能力也就被这张表框死了。

#### 通用工具与「给模型一台计算机」

**context**：作者主张与其强迫用户为每个可能的动作造工具，不如给 agent 一个通用工具：harness 自带 bash，让模型通过写代码并执行来自主解决问题。这被称作朝「giving models a computer」迈出的一大步，模型可以用代码即时设计自己的工具。

**费曼一下**：与其给厨师准备一百把专用刀，不如给他一间能自己打铁的作坊。代码执行是元工具——它让工具集从「事先枚举」变成「按需生成」，agent 的能力边界不再由设计者的想象力决定。

#### Sandbox（沙箱）

**context**：解决「代码在哪里跑」的问题。本地跑 agent 生成的代码有风险，单个本地环境也无法扩展到大规模负载。沙箱提供安全隔离的执行环境，可叠加命令 allow-list 与网络隔离，并支持按需创建、扇出、用完销毁。

**费曼一下**：给 agent 一间一次性实验室——它可以在里面随便炸，炸完把房间扔掉再开一间新的。安全和扩展性其实是同一件事的两面：因为环境是隔离且可抛弃的，所以既能放心让它折腾，也能同时开一百间。

#### Self-verification loop（自验证回路）

**context**：由 browser、logs、screenshots、test runners 这类观察工具支撑，让 agent 能「write application code, run tests, inspect logs, and fix errors」。在长时程章节进一步展开为两条实现路径：harness 的 hooks 跑预定义测试并在失败时回灌错误信息，或提示模型独立自评代码。作者指出验证的价值是把解法锚定在测试上，并创造自我改进的反馈信号。

**费曼一下**：让 agent 长出眼睛。只会写不会看的 agent，错了也不知道错在哪；能跑测试、能读日志、能截图对照，它才第一次拥有了「我干得对不对」这个信号——而所有自我改进都要从这个信号开始。

#### Context injection（上下文注入）

**context**：作者的硬约束推论——模型除权重和当前 context 之外没有额外知识；在无法编辑权重的前提下，「the only way to add knowledge is via context injection」。记忆文件、Web Search、MCP 工具都是这条通道上的具体实现。

**费曼一下**：你没法给模型动脑手术，只能在它每次开口之前，往它面前的桌子上多放几张纸。一切「让 AI 知道更多」的花样，本质上都是在决定往桌上放什么、什么时候放、放多少。

#### Memory file 与 continual learning（记忆文件与持续学习）

**context**：harness 支持 `AGENTS.md` 这类 memory file 标准，在 agent 启动时注入 context；agent 编辑后 harness 再载入更新版本。作者称其为一种 continual learning——agent 把一次 session 的知识持久存下来并注入未来的 session。

**费曼一下**：给模型一本它自己写、自己每天开工前先读一遍的工作笔记。权重改不了，但笔记可以改——于是「学习」这件事被从训练环节挪到了运行环节，由框架而不是训练管道来承担。

#### Context Rot（上下文腐坏）

**context**：文中引用的概念，指模型随着 context window 被填满，在推理和完成任务上都会变差。作者由此得出「context 是宝贵而稀缺的资源」，harness 必须有管理策略，并给出全文最锋利的定位——「Harnesses today are largely delivery mechanisms for good context engineering」。

**费曼一下**：塞得越满未必记得越牢，反而会越糊涂。这是对「上下文窗口越大越好」的直接反驳——窗口大小是容量，不是效能。真正的手艺在于往里放什么、什么时候清理，而这活儿是框架干的。

#### Compaction（压缩）

**context**：应对 context window 接近填满的策略。作者用反问点出必要性——没有压缩时，对话超出窗口的结果就是 API 报错，「that's not good」。压缩会智能地卸载并总结已有上下文，让 agent 得以继续工作。

**费曼一下**：桌子快堆满时，把旧材料归纳成一页纸的摘要、原件收进抽屉，腾出桌面继续干活。它换来的是连续性：一个能压缩的 agent 不会因为聊得太久就突然断片。

#### Tool call offloading（工具输出卸载）

**context**：针对大段工具输出污染上下文却不提供有效信息的问题。harness 对超过阈值 token 数的输出只保留头部和尾部 token，把完整输出卸载到文件系统，模型需要时再去访问。

**费曼一下**：只把目录和结尾摆在桌上，整本书塞进书架，需要时再去翻。这是「文件系统作为 context 延伸」的最直接用法——信息没有丢，只是从昂贵的近处挪到了便宜的远处。

#### Progressive disclosure（渐进式披露）与 Skills

**context**：Skills 被定位为 harness 级原语，解决启动时载入过多工具或 MCP server、在 agent 开始干活前就拖垮性能的问题。作者特别强调归属——模型并没有选择让 Skill front-matter 在启动时进入 context，是 harness 替它做了这个保护性取舍。

**费曼一下**：先给一份目录，用到哪一章再翻哪一章。它的深层含义是：能力的「存在」和能力的「在场」应该分开——你可以拥有一百个技能，但不必让这一百个同时占着注意力。

#### Ralph Loop

**context**：一种 harness 模式——用 hook 拦截模型的退出企图，在干净的 context window 中重新注入原始 prompt，迫使 agent 对着完成目标继续工作。作者指出它之所以可行是因为文件系统在：每次迭代都从新鲜上下文开始，但会读取上一次迭代留下的状态。

**费曼一下**：模型想收工时，框架把它叫回来，递上同一份任务书和一张干净的桌子，说「接着干」。它把「长时间工作」拆成了许多次短时间工作，靠磁盘上的状态接力——连贯性不来自记忆，来自留在外部的痕迹。

#### 模型训练与 harness 设计的耦合

**context**：Claude Code、Codex 这类产品是模型与 harness 同在 loop 中做的 post-training，形成「发现原语 → 加进 harness → 训练下一代模型」的反馈回路，模型在自己被训练的 harness 里越来越强。副作用是过拟合——改动工具逻辑会让表现变差（作者以 Codex-5.3 prompting guide 中的 `apply_patch` 为例）。反转在于：Terminal Bench 2.0 上 Opus 4.6 在 Claude Code 里的得分远低于它在其他 harness 里的得分，LangChain 只改 harness 就把自家 coding agent 从 Top 30 提到 Top 5。

**费曼一下**：模型和框架一起长大，会长出默契，也会长出依赖——换一副框架就手生。这有两个后果：一是模型的分数从来不是模型一个人的分数；二是「原厂框架」并不等于「最优框架」，为自己的任务重调框架，往往比换模型划算得多。

### 概念网络

```mermaid
graph TD
C1["Agent = 模型 + harness"]
C2["模型：智能来源，只吃数据吐文本"]
C3["harness：模型之外的全部代码与执行逻辑"]
C4["harness 级能力：模型开箱做不到的事"]
C5["从期望行为反推 harness 设计"]
C6["文件系统：最基础的 harness 原语"]
C7["bash 与代码执行：通用工具"]
C8["沙箱：安全且可扩展的执行环境"]
C9["自验证回路：写码 跑测试 看日志 修错"]
C10["上下文注入：唯一的加知识途径"]
C11["记忆文件与持续学习"]
C12["上下文腐坏：context 是稀缺资源"]
C13["compaction 压缩"]
C14["工具输出卸载"]
C15["渐进式披露与 Skills"]
C16["Ralph Loop：拦截退出并续跑"]
C17["长时程自主执行"]
C18["模型训练与 harness 设计耦合"]
C19["为任务优化 harness 的收益空间"]
C1 -->|层级| C2
C1 -->|层级| C3
C2 -->|缺口| C4
C3 -->|承载| C4
C4 -->|驱动| C5
C5 -->|推导| C6
C5 -->|推导| C7
C5 -->|推导| C10
C6 -->|支撑| C7
C7 -->|需要| C8
C8 -->|支撑| C9
C10 -->|实现| C11
C10 ---|张力| C12
C12 -->|应对| C13
C12 -->|应对| C14
C12 -->|应对| C15
C6 -->|支撑| C11
C6 -->|支撑| C16
C16 -->|支撑| C17
C9 -->|支撑| C17
C13 -->|支撑| C17
C18 -->|演化| C3
C18 ---|张力| C19
C19 -->|回到| C1
```

整个网络的顶点是一条等式：Agent = Model + Harness。它把 agent 这个混沌的对象切成两块可以分别追问的东西——模型（C2）与 harness（C3）。这不是分类学游戏，而是全文所有推导的**发生器**：一旦承认智能只在模型那一侧，其余一切就都落在 harness 这一侧，harness 的组件清单也就不再是别人的最佳实践汇编，而是从模型缺什么反推出来的必然结果。

**第一条主链是「缺口 → 反推 → 原语」。** 模型的能力素描极其克制：吃进多模态数据，吐出文本，仅此而已。由此暴露的四个缺口（C4：持久状态、执行代码、实时知识、环境搭建）不是智力问题，而是能力归属问题。作者把它们统一转成一个可操作的推导模式（C5）：先说清想要什么行为，再设计对应的 harness 机制。文件系统（C6）、bash 与代码执行（C7）、沙箱（C8）、自验证（C9）就是沿着这条链一节一节被推出来的，且顺序不可交换——先有工作区才谈得上写代码，先有代码执行才需要安全的地方跑，跑起来了才有结果可观察可验证。

**第二条主链是「知识注入 → 上下文稀缺 → 管理策略」。** 无法编辑权重这个硬约束，把所有「让 agent 更懂」的手段都压缩成同一条通道：context injection（C10）。记忆文件（C11）和 Web Search 走的是这条通道的正向——往里放东西。但正向用力立刻撞上反向的约束：context rot（C12）说明这条通道有代价，塞得越满效能越差。于是 compaction（C13）、工具输出卸载（C14）、渐进式披露（C15）三件武器全部诞生于同一个张力，它们的共同动作也一致——把信息从昂贵的 context 里挪到便宜的文件系统里，需要时再取回。这解释了为什么作者说今天的 harness「largely delivery mechanisms for good context engineering」。

**两条主链在文件系统上交汇，并在长时程执行处复利。** C6 同时是第一条链的起点原语和第二条链的卸载目的地，这正是作者称它「最基础」的原因——它既是工作区，也是记忆载体，还是多 agent 的共享账本。长时程自主执行（C17）不是第六个新组件，而是前面所有原语叠加后涌现的能力：Ralph Loop（C16）靠文件系统在干净上下文之间接力，自验证（C9）提供不跑偏的信号，compaction（C13）提供跨窗口的连续性。三者缺一，长任务就会退回到 early stopping 与 incoherence。

**最外层是一对没有被作者调和的张力。** 模型训练与 harness 设计的耦合（C18）向内塑造 harness——被验证有用的原语会进入下一代模型的训练，模型于是在自己出生的框架里越来越顺手，甚至出现换个文件编辑工具就掉分的过拟合。这股力量指向「原厂框架最优」。但 C19 给出的证据指向相反方向：同一个 Opus 4.6 换个 harness，榜单位置可以天差地别；只改 harness 就能把 coding agent 从 Top 30 推到 Top 5。两者的张力是真实的，它意味着模型的分数从来不是模型一个人的分数，也意味着优化空间恰恰藏在耦合的缝隙里。

**最后，网络是闭合的。** C19 回到 C1 不是修辞：正因为等式的两项可以独立优化，「为你的任务优化 harness」才是一个有明确对象的工程动作，而不是模糊的调优直觉。作者对未来的判断也从这个闭环长出——模型变强会把 planning、self-verification、长时程连贯性吸收进 C2 一侧，harness 的补丁职能会萎缩；但 harness 的另一半职能（围绕模型智能做系统工程：好的环境、对的工具、持久的状态、验证的回路）与基座智能无关，因此不会随模型变强而消失。

## 费曼 x3

大多数人谈论 AI 能力时谈的是模型。但真正决定一个 agent 能不能干活的，往往是模型之外那一层。把这层说清楚只需要一个减法：如果你不是模型，你就是 harness。系统提示词、工具与技能的描述、文件系统与沙箱、子 agent 的编排逻辑、拦截退出的 hook——凡是不属于权重的部分，全在这一侧。

这个划分之所以有力，不在于它精确，而在于它逼你换一种提问方式：不再问模型还差什么，而是问我想要什么行为、该在模型周围造一个什么系统让它做到。裸模型吃进文本图像音频，吐出文本，仅此而已。它记不住上一次会话，跑不了代码，够不着训练之后发生的世界。每一项缺口都不是等模型变强就会自动填上的，而是一条明确的工程需求：给它一个工作区，于是有了文件系统；给它一台计算机，于是有了 bash 和代码执行；让它安全地折腾，于是有了沙箱；让它看得见自己干得对不对，于是有了测试、日志与自验证回路。

最反直觉的一条是：上下文不是越多越好。模型在窗口被填满的过程中会变笨，这叫 context rot。于是今天的 harness 在很大程度上只是「好的上下文工程的投递机制」——压缩、把冗长的工具输出卸载到磁盘只留头尾、用渐进式披露让技能到用时才展开。这些取舍模型自己无权决定，是别人替它做的。

更有意思的是，模型和框架已经开始互相塑造。今天的 agent 产品在训练时就把 harness 放进了 loop，模型于是在自己长大的那副框架里越来越顺手，顺手到换一种文件编辑工具就会掉分。但这并不意味着模型最适合的框架就是它出生的那副：同一个 Opus 换个 harness，榜单名次可以天差地别；只改框架不换模型，也能把一个编码 agent 从三十名开外推进前五。

所以值得记住的不是某个具体组件，而是那句收束：智能在模型里，让智能变得有用的那个系统在 harness 里。模型每强一分，今天由框架承担的一部分职责就会被吸走；但只要「为这项任务配一个更合适的环境」这件事还存在，这层工程就不会消失。你手上的模型也许和别人一样，你造的那副框架不一样。
