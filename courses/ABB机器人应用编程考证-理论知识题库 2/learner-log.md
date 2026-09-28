# 学习证据账本

## 01

```yaml
lesson: 01
status: active
learner_evidence: null
mastery_band: null
route: null
passed_dimensions: []
gap_ids: []
prior_judgment: 初始掌握状态未知
new_evidence: 尚未提交未污染原答
posterior_judgment: 未判定
remaining_alternative: 当前正确率与概念薄弱点均未知
next_discriminator: 一道未展示答案的单选题及作答依据
belief_update: unchanged
explicit_preference: 以通过考试为目标，期望正确率60-70%
next_action: 等待基线题原答
evidence_receipt: null
```

- lesson: 01 | learner_evidence: B（未提供理由）
- lesson: 01 | learner_evidence: 因为机器人很危险，扭矩特别大
- lesson: 01 | learner_evidence: C（变式迁移：低速只降低风险，不消除风险）
- lesson: 01 | learner_evidence: A（未展示变式：由关节角计算末端位姿属于运动学正问题）
- lesson: 01 | learner_evidence: B（未展示变式：同一末端位姿可能对应多组关节角，逆运动学具有多解性）
- lesson: 01 | learner_evidence: C（未展示变式：灵敏度为输出变化量与输入变化量之比，10 ÷ 2 = 5）
- lesson: 01 | learner_evidence: A（未展示题：数字量输入信号的典型特征；正确答案 B）
- lesson: 01 | learner_evidence: B（补救变式：连续变化的 0–10V 压力信号属于模拟量）
- lesson: 01 | learner_evidence: D（未展示题：机器人末端可到达位置的集合；正确答案 A，工作空间）
- lesson: 01 | learner_evidence: B（补救变式：基坐标系与工具坐标系改变的是位置描述的参照框架）
- lesson: 01 | learner_evidence: B（未展示题：直线插补要求末端沿空间直线路径运动）
- lesson: 01 | learner_evidence: A（未展示题：多次到达同一指令位置且彼此接近；正确答案 B，重复定位精度）
- lesson: 01 | learner_evidence: B（补救变式：固定偏差 2 mm 但停靠结果集中，绝对定位精度低、重复定位精度高）
- lesson: 01 | learner_evidence: A（未展示题：真空吸盘漏气会降低吸附力，工件可能脱落）
- lesson: 01 | learner_evidence: B（未展示题，明确标注“蒙一个”：PLC 读取输入、执行程序、更新输出的循环；正确答案 A，扫描周期）
- lesson: 01 | learner_evidence: A（补救变式：错过本轮输入采样的信号通常在下一扫描周期读取）
- lesson: 01 | learner_evidence: B（未展示题：较大 zone 不精确停在目标点，而是平滑衔接下一段轨迹；学习者主动关联 z1000 与 fine）
- lesson: 01 | learner_evidence: A（未展示题：更换重量明显不同的夹具后未更新工具负载数据，会导致运动控制和制动效果变差）
- lesson: 01 | learner_evidence: 不知道（未展示题：TCP 的含义；首次未形成答案）
- lesson: 01 | learner_evidence: B（讲解后的同题复述：TCP 是工具中心点；污染证据，不计首次正确率）
- lesson: 01 | learner_evidence: C（补救变式：焊枪的 TCP 通常设在焊枪尖端）
- lesson: 01 | learner_evidence: A（未展示题：工具坐标系定义错误会影响工具末端位置和姿态计算）
- lesson: 01 | learner_evidence: A（未展示题：特殊姿态下少量末端变化引起关节速度剧增，属于奇异点）
- lesson: 01 | learner_evidence: A，并补充 MoveJ（未展示变式：调整路径或工具姿态避开奇异区域；MoveJ 可用于部分场景，但不保证必然避开）
- lesson: 01 | learner_evidence: A（未展示题：MoveL 重点保证 TCP 沿直线路径运动）
- lesson: 01 | learner_evidence: B（未展示题：MoveJ 按关节空间运动，TCP 路径通常不保证为直线）
- lesson: 01 | learner_evidence: A（未展示题且作答不确定：常开型接近开关未检测物体时的输出；正确答案 B，断开）
- lesson: 01 | learner_evidence: A（补救变式：常闭型接近开关未检测物体时通常导通）
- lesson: 01 | learner_evidence: 我不会（未展示题：PNP 型输出导通时向负载提供的电位；明确知识缺口，不计首次正确率）
- lesson: 01 | learner_evidence: B（补救变式：导通后将 PLC 输入端拉到 0V 的传感器更可能是 NPN 型；学习者联想到二极管）
- lesson: 01 | learner_evidence: A（讲解后的同题复述：PLC 漏型输入通常搭配 PNP 源型输出；污染证据，不计首次正确率）
- lesson: 01 | learner_evidence: C（未展示迁移题：PLC COM 接 +24V，应搭配 NPN 漏型输出；正确答案 B，源漏配对缺口仍存在）
- lesson: 01 | learner_evidence: NPN（补救重建：传感器导通后将信号线接到 0V，判断为 NPN）
- lesson: 01 | learner_evidence: A（补救分步复测：在 +24V → PLC 输入 → NPN → 0V 回路中，PLC 属于源型输入）
- lesson: 01 | learner_evidence: B（反向复测：在 +24V → PNP → PLC 输入 → 0V 回路中，PLC 属于漏型输入）
- lesson: 01 | learner_evidence: B（组合迁移题：传感器输出 +24V 且 PLC COM 接 0V；正确答案 A，PNP 源型输出 + PLC 漏型输入）
- lesson: 01 | learner_evidence: A（分步重建：传感器导通时输出 +24V，判断为 PNP）
- lesson: 01 | learner_evidence: B（分步重建：PLC 公共端接 0V，判断为漏型输入）
- lesson: 01 | learner_evidence: A（讲解后的组合复述：PNP 源型输出 + PLC 漏型输入；需新情境迁移确认）
- lesson: 01 | learner_evidence: B（独立反向迁移：传感器拉到 0V 为 NPN 漏型输出，PLC COM 接 +24V 为源型输入）
- lesson: 01 | learner_evidence: A（未展示题：电磁阀线圈并联续流二极管的作用；正确答案 B，吸收断电时的反向感应电压）
- lesson: 01 | learner_evidence: A（补救变式：继电器线圈断电导致控制器复位或输出损坏时，应在线圈两端增加续流二极管）
- lesson: 01 | learner_evidence: B，并解释“更好被感应到”（未展示题：急停使用常闭触点，使断线也能被识别并触发停机）
- lesson: 01 | learner_evidence: B（未展示题但明确标注“蒙一个”：安全门双通道用于检测单通道故障；选对但理解待验证）
- lesson: 01 | learner_evidence: B（补救变式：安全门一路触点粘连导致双通道不一致时，应禁止机器人运行）
- lesson: 01 | learner_evidence: B（未展示题：安全门关闭后不自动复位，可防止人员仍在危险区时机器人意外重启）
- lesson: 01 | learner_evidence: B（未展示变式：人工复位表示安全条件已恢复，系统进入可启动状态，但不会直接启动机器人）
- lesson: 01 | learner_evidence: A（五题组第1题：气动夹具检修前应释放残余压力，正确）
- lesson: 01 | learner_evidence: 2A 3C 4B 5A（五题组剩余四题：fine 错误，编码器错误，急停恢复与模拟量干扰正确；2/4）
- lesson: 01 | learner_evidence: B A A B B（未提示五题组：使能键、光电检测、真空漏气、MoveJ、安全复位；5/5）
- lesson: 01 | learner_evidence: A B A A C（未提示提高难度五题组：TCP、zone、定位精度正确；PNP 输出与 PLC COM 配对错误；3/5）
- lesson: 01 | learner_evidence: A A A B A（PNP/NPN 五题复测：第 2-5 题正确；第 1 题将拉到 0V 误判为 PNP；4/5）
- lesson: 01 | learner_evidence: A B B B A（主线综合五题：位姿、MoveL、重复定位精度、急停常闭、续流二极管；5/5）

```yaml
lesson: 01
status: settled
learner_evidence: learner-log.md:24
mastery_band: 基本掌握
route: advance
passed_dimensions: [准确性, 机制, 边界, 迁移]
gap_ids: [pnp_npn_pairing_stability]
prior_judgment: 初始掌握状态未知
new_evidence: 有效基线约70%-75%，两组未提示综合五题均为5/5，多个错题已通过变式复测
posterior_judgment: 已达到题库正确率60%-70%的阶段目标，可以进入原题正式刷题
remaining_alternative: PNP/NPN组合判断仍可能不稳定
next_discriminator: 在后续原题中混入PNP/NPN延迟复测
belief_update: up
explicit_preference: 每轮5题；不提供泄露答案的作答示例
next_action: 进入02，从原题第29题起正式刷题
evidence_receipt: 01-批注回应报告.md
```

## 02

```yaml
lesson: 02
status: active
learner_evidence: null
mastery_band: null
route: null
passed_dimensions: []
gap_ids: [pnp_npn_pairing_stability]
prior_judgment: 01已基本掌握并通过验证
new_evidence: 尚未提交第29-33题原答
posterior_judgment: 未判定
remaining_alternative: 原题正确率能否稳定达到60%-70%
next_discriminator: 第29-33题首次作答
belief_update: unchanged
explicit_preference: 每轮5题；不提供答案示例
next_action: 等待第29-33题答案
evidence_receipt: null
```

- lesson: 02 | learner_evidence: B C C C A（原题第29-33题：第29题错误，正确答案D；第30-33题正确；4/5）
- lesson: 02 | learner_evidence: B（第29题补救变式：把被测变化转换为电信号的是转换元件）
- lesson: 02 | learner_evidence: B A C A C（原题第34-38题：第34、36、38题正确；第35题正确答案B，第37题正确答案B；3/5）
- lesson: 02 | learner_evidence: A A（第35、37题补救变式：负载端失压优先检查中间线路断路；通信分类依据为信号形式；2/2）
- lesson: 02 | learner_evidence: B A C B B（原题第39-43题：第39、41、42题正确；第40题正确答案B，第43题正确答案C；3/5）
- lesson: 02 | learner_evidence: B B B A A（原题第44-48题：第44、45、47、48题正确；第46题正确答案A，ABB 标准 IO 板卡一般为 PNP 类型；4/5）
