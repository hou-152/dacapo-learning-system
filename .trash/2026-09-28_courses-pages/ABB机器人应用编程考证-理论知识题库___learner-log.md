course:: [[ABB机器人应用编程考证-理论知识题库]]
mirror:: true
source-path:: `../ABB机器人应用编程考证-理论知识题库/learner-log.md`

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
- lesson: 02 | learner_evidence: A A C B B（原题第44-48题：0/5；正确序列B B A A A；主要缺口为ABB专有IO配置与硬件型号）
- lesson: 02 | learner_evidence: A A C B B（原题第49-53题：第49-51题正确；第52、53题正确答案均为C；3/5）
- lesson: 02 | learner_evidence: A C C D A（原题第54-58题：第55-58题正确；第54题按题库原文正确答案C“同进轴式”；4/5）
- lesson: 02 | explicit_preference: “这样子就变成了刷题了呀？”；停止题库顺序刷题，题库只用于诊断，恢复单概念 Learner-first 闭环
- lesson: 02 | learner_evidence: “控制器要知道它当前的位置，就是知道它的坐标”；已理解位置反馈目标，尚未区分直线关节与旋转关节的被测物理量
- lesson: 02 | learner_evidence: “一个是线位移，一个是角动量，是吧？角度偏移”；线位移正确，将角位移误称为角动量后自我修正为角度偏移
- lesson: 02 | learner_evidence: “物理量叫做角位移，偏移了60度，正60度”；准确计算角位移并给出方向，边界为正负号取决于坐标正方向约定；route: advance
- lesson: 02 | learner_evidence: “减速器在功率不变情况下把速度降下来，从而增强扭矩；更核心的是精准度”；已掌握速度换扭矩主线，关键缺口为将减速器与实际精度自动提升等同，尚未纳入齿隙与弹性边界
- lesson: 02 | learner_evidence: “几乎没有齿隙的定位更稳定；齿隙会产生微小偏移量造成误差”；准确解释换向齿隙导致定位误差，减速器精度边界通过；route: advance
- lesson: 02 | learner_evidence: “谐波减速器精度高、价格贵、齿隙小；高动态意味着动作精准，换向时误差不会变大”；已理解低齿隙有利于换向，关键缺口为将高动态等同于静态精度，并将谐波减速器误解为不会产生误差
- lesson: 02 | learner_evidence: “贴着指令去运动的那个更好”；正确识别高动态表现为运动过程跟随紧密，尚缺少延迟与超调机制说明
- lesson: 02 | learner_evidence: “虽然精确但会震荡；要求1秒完成却需要1.2秒”；准确区分最终定位精度与动态响应，能用震荡和滞后解释高动态不足；mastery_band: 基本掌握；route: advance
- lesson: 02 | learner_evidence: “应该是2的4次方，也就是8”；已掌握n位对应2^n种组合的机制，计算时将2^4误算为8
- lesson: 02 | learner_evidence: “00001111是什么意思？15进制？”；断点定位为不理解二进制位权与位串到十进制数值的映射
- lesson: 02 | learner_evidence: “00101 = 6”；尚未稳定按右起位权1、2、4、8、16求和，正确值为5
- lesson: 02 | learner_evidence: “00110 = 6，0+2+4”；正确按位权4与2求和，二进制转十进制基础通过，进入GO组信号迁移
- lesson: 02 | learner_evidence: “1010 = 0+2+0+8 = 10”；正确将4位GO位模式换算为十进制，位权迁移通过
- lesson: 02 | learner_evidence: “不懂2,4,5,7表示几个物理输出点、是否连续”；GO数值已会，当前断点为物理IO地址清单语义
- lesson: 02 | learner_evidence: “3 n”；正确判断地址3,6,9使用3个物理输出点且不连续，地址清单语义通过
- lesson: 02 | learner_evidence: “2的3次方，然后范围应该是7”；正确识别3位组合数公式与最大值7，需将范围完整表述为0-7
- lesson: 02 | learner_evidence: “1,4,6,9；4位；16种组合；范围0-15”；GO地址清单、位数与数值范围完成新情境迁移；mastery_band: 完全掌握；route: advance
- lesson: 02 | learner_evidence: “PNP，漏输出就是从……”；PNP识别正确，但将输出+24V误判为漏型且电流方向说明未完成，PNP/NPN配对缺口重新打开
- lesson: 02 | learner_evidence: “输出端变成24伏，说明把电流拉回”；将+24V输出方向判断反，尚未建立输出电压与正负电源轨连接的对应
- lesson: 02 | learner_evidence: “PNP是源型输出，PLC COM接0V为漏型输入，GO使用4点，1010=12”；源漏配对与地址数量均正确，二进制位权换算回退；正确值1010=10
- lesson: 02 | learner_evidence: “1101 = 1+0+4+8”；位权相加正确，十进制结果13；IO源漏配对、GO地址与二进制换算通过；route: advance
- lesson: 02 | learner_evidence: “本轮读不到，等下一轮；因为循环已过读取输入阶段”；准确解释PLC输入映像与循环扫描时序，标准扫描机制通过；route: advance
- lesson: 02 | learner_evidence: “256是2的8次方，大概需要8个二进制位”；从未知状态独立推导灰度级数量与每像素位数关系，正确得到8 bit即1 byte
- lesson: 02 | learner_evidence: “直接记了，应该是1MB”；答案正确但未展示整图容量计算，明确偏好为考前压缩讲解；保留一道变式迁移验证
- lesson: 02 | learner_evidence: “512×512约0.5MB、512KB”；将宽高同时减半误判为容量减半，正确应为原容量1/4即0.25MB、256KB
- lesson: 02 | learner_evidence: “256×256为1/16MB、64KB”；正确迁移二维分辨率缩放与容量平方关系，图像存储量概念通过；route: advance
- lesson: 02 | learner_evidence: “相机远离物体，实际范围变大，因为视野变大”；结论正确，尚需用固定视角覆盖宽度解释机制
- lesson: 02 | learner_evidence: “工作距离2倍时覆盖宽度4倍”；混淆线性尺寸与面积，正确为宽高各2倍、面积4倍
- lesson: 02 | learner_evidence: “距离3倍，宽度3倍，面积9倍”；正确迁移固定视角下线性尺度与面积关系，工作距离—视野概念通过；route: advance
- lesson: 02 | learner_evidence: “第一阶段MoveJ，第二阶段MoveL，最终fine；MoveL从上到下走直线，fine精确停稳而非平滑过渡”；正确选择运动指令与停止方式，需将MoveL机制表述为TCP直线约束；RAPID基础通过
- lesson: 02 | learner_evidence: “用起点、终点、半径画圆弧的工具；需要起点、终点和中点，因为只有终点无法确定半径”；圆弧路径约束理解正确，缺少ABB术语MoveC，并需将中点表述为圆弧经过点；mastery_band: 基本掌握；route: advance
- lesson: 02 | learner_evidence: “不能直接恢复；人先看一眼、站远点，再恢复，避免撞击”；安全方向正确，尚未给出危险区确认、故障排除、人工复位与独立启动的正式顺序
- lesson: 02 | learner_evidence: “排除原因→关闭安全门→安全复位并确定无人→启动；复位后不立即运动”；已理解复位与启动分离，顺序缺口为必须在关门和复位前确认危险区无人；mastery_band: 基本掌握；route: advance
- lesson: 02 | learner_evidence: “HOME是原点，System.xml是系统文件；RAPID、SYSPAR不知道”；System.xml方向正确，将HOME目录误解为机器人原点，ABB备份目录映射需最小记忆
- lesson: 02 | learner_evidence: “RAPID应该是根目录，系统配置有问题查SYSPAR”；SYSPAR映射正确，仍将RAPID误解为根目录；正确映射为RAPID存程序代码
- lesson: 02 | learner_evidence: “请求写权限可能是怕瞎改、防呆设置”；核心方向正确，尚需补充读写分离、并发覆盖与真实设备安全影响机制
- lesson: 02 | learner_evidence: “乙不能写，只能看；甲已经在写，两人一起写难以处理”；准确解释读写分离与并发写冲突，RobotStudio写权限机制通过；route: advance
- lesson: 02 | learner_evidence: “控制器应该校准；反馈说明要求90但只到85，也可能到了限位”；理解反馈暴露位置误差，关键缺口为将正常闭环纠偏与校准、限位故障混合
- lesson: 02 | learner_evidence: “应该是纠偏；校准是单位不对，纠偏是实际值向目标值靠拢”；闭环纠偏机制正确，校准定义偏窄，需补零点、比例和坐标映射边界
- lesson: 02 | learner_evidence: “真实已是90但反馈85，是编码器有问题，要让编码器对齐真实位置”；正确区分反馈标定误差与正常闭环纠偏，闭环伺服概念通过；route: advance
- lesson: 02 | learner_evidence: “实际约102而目标100，绝对定位精度低；多次落点集中，重复定位精度高”；准确解释目标偏差与落点离散度，完成延迟迁移；mastery_band: 完全掌握；route: advance
- lesson: 02 | learner_evidence: C A ? C D D D D ? B（未见混合诊断第64、66、75、90、120、150、180、220、260、300题；4/10；第75、260题明确不会；主要缺口为RAPID赋值、PLC助记符及ABB专有事实）
- lesson: 02 | learner_evidence: “reg1 := reg2 + 3，在reg2=5时为赋值，reg1=8”；正确理解RAPID赋值方向与:=符号；route: advance
- lesson: 02 | learner_evidence: “从左母线开始连接常闭触点使用LDI”；正确应用PLC助记符的起始与取反规则，待并联场景迁移
- lesson: 02 | learner_evidence: “并联常闭触点使用ORI”；正确迁移并联与取反规则，LD/LDI/OR/ORI概念通过；route: advance
- lesson: 02 | learner_evidence: “耦合、变位机、储存，编码器信号未答”；4项延迟记忆回收3/4，RFID、示教器放置、图像处理边界通过；增量编码器A/B/Z信号为当前缺口
- lesson: 02 | learner_evidence: “Z用于连续测速”；将Z基准脉冲与A/B连续脉冲混淆，正确为A/B频率用于测速、Z每转一次提供基准
- lesson: 02 | learner_evidence: “Z为每转一次基准，A/B用于连续测速”；正确区分增量编码器三路信号功能，编码器缺口通过；route: advance
- lesson: 02 | learner_evidence: A A B D C C C B A C（未见单选第70、80、100、130、160、190、230、240、270、290题；2/10；仅第70、230题正确；RAPID与RobotStudio专有指令为主要短板）
- lesson: 02 | learner_evidence: “物体意义不同会导致灰度不同，机缘巧合得到相同直方图”；知道不同图像可能共享直方图，但尚未明确直方图丢弃空间位置、只保留灰度计数
- lesson: 02 | learner_evidence: “直方图只统计哪个灰度出现较多，而不是位置；数量不变则直方图不变”；准确解释空间信息丢失与多对一关系，灰度直方图概念通过；route: advance
- lesson: 02 | learner_evidence: A B B D B（RAPID/RobotStudio定向回收：ACTUNIT、Offs、TPErase、robtarget、KeepPosition；5/5；短时识别通过，待全新混合题验证）
- lesson: 02 | learner_evidence: C B C A D A D C C C（全新单选第71、81、101、131、161、191、231、241、271、291题；6/10；第71、131、161、231题错误；修复后全新题正确率60%）
- lesson: 02 | learner_evidence: D A ? A B B B B B A（考前校准单选第72、82、102、132、162、192、232、242、272、292题；3/10；仅第192、242、272题正确；最近6组全新诊断27/60=45%）
- lesson: 02 | learner_evidence: “频闪光原理类似快门时间，极短时间冻结高速运动、减少拖影”；准确连接有效曝光时间与运动模糊，频闪照明机制通过；route: advance
- lesson: 02 | learner_evidence: 对 错 对 对 对 对 对 错 错 对（未见判断题第1、25、50、75、100、125、150、175、200、225题；6/10；第1、175、200、225题错误；正确率从上一组40%提升至60%）
- lesson: 02 | learner_evidence: “MoveAbsJ用于六个绝对关节角且不要求TCP直线；MoveL用于末端直线；tool0理解为六轴法兰中心；柔轮会变形”；运动指令机制正确，tool0与谐波柔轮边界补齐；route: advance
- lesson: 02 | learner_evidence: ? 对 错 错 对 ? 错 错 对 对（未见判断题第10、35、60、85、110、135、160、185、210、235题；6/10；第10、135题不会；第110、185题错误；连续第二组60%）
- lesson: 02 | learner_evidence: “拆除应该直接连；把int2和ch2用CONNECT连接”；仍混淆Attacher/Detacher，并将信号触发层与中断标识符到TRAP程序的绑定层混合
- lesson: 02 | explicit_preference: “这有点难，怕是选择题”；考前对RAPID专有语法按选择/判断识别层级训练，不要求无提示默写完整代码
- lesson: 02 | learner_evidence: B B B A A（原题第44-48题：第44、45、47、48题正确；第46题正确答案A，ABB 标准 IO 板卡一般为 PNP 类型；4/5）

