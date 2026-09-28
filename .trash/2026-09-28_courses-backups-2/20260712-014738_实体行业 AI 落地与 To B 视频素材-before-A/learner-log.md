# 实体行业 AI 落地与 To B 视频素材｜学习证据账本

## lesson-01-evidence-01

```yaml
lesson: 01
status: active
mastery_band: null
route: null
learner_evidence: |
  我是服务于实体行业的 AI 公司。比如 OpenAI 最近开设了一个叫做 AI Lab 的项目组，这让我想到了《AI 内参》里提到的一个比较新的概念——“帮助企业落地 AI 的工程师”。

  通过阅读这些案例，我发现：

  1. 实体经济（以福特公司为例）：
     福特一开始觉得有了 AI 之后可以替代很多工程师，实现高度自动化。但在前几周，他们又重新聘请回了许多工程师。其根本原因在于，很多判断是“AI 无法外包的判断”，只有通过“AI + 工程师”的模式，才能把某一个流程做得更好。

  2. 互联网行业（以美国 Uber 公司为例）：
     《AI 内参》里提到，Uber 仅仅花了几个月的时间，就把整整一年的 Token 额度全部烧完了。

  现在 AI 落地遇到的核心问题是：
  - 很多人并没有起心动念去用 AI 解决具体的业务问题，而只是用来处理 PDF、处理 Excel 等一些非常简单的工作。
  - 与此同时，大家一直都在盲目使用最贵的模型，导致大量的 Token 和成本被白白浪费。

  因此，我认为更好的方向是：将 AI 真正塞进具体的工程和工作流程中，以此来服务实体行业。
passed_dimensions:
  - 区分了模型使用与具体业务流程
  - 提出了模型成本浪费与工作流落地的张力
gap_ids:
  - buyer_metric_missing
  - supervision_cost_missing
  - external_case_unverified
prior_judgment: 掌握状态未知
new_evidence: 学习者原答已保存
posterior_judgment: 初步显示对工作流实施层有直觉，尚缺可验证的 To B 价值定义
remaining_alternative: 学习者可能把“塞进工作流”理解为泛化接入，也可能已能按业务结果和隐性成本设计交付
next_discriminator: 为一个实体企业指定一个流程、一个业务指标和一种需计入验收的看护成本
belief_update: up
explicit_preference: 材料要短；最终作为 AI 视频流水线的文本素材
next_action: 阅读最小补救后完成变式迁移题
evidence_receipt: learner-log.md#lesson-01-evidence-01
```

## lesson-01-feedback-02

```yaml
lesson: 01
feedback_type: learning_material_and_interaction
feedback: |
  场景啊？没有场景啊。因为没有场景，这是一方面；第二方面就是，它一开始没有场景，他没有让我去反馈，没有让我去费曼，也没有让我说“哎，你提一些问题”，而且他前面给我的上下文也很短。不符合我之前所有的交互式学习给我的印象。
effect_on_teaching: 补入等价模拟场景；先接收用户反应与提问，再进入费曼取证；增加上下文，不用一句题干替代材料。
effect_on_mastery: none
```

## lesson-01-evidence-03

```yaml
lesson: 01
status: active
learner_evidence: |
  我一开始也觉得它叫做没有自动化、没有专门化。但是销售仍然干的是销售的活，工程师干的仍然是工程师的活，那它的具体改变是什么呢？

  具体改变是什么？只不过是把一些很细枝末节的……

  我还是有点不太懂，可能是效率问题，或者没有一个……也不对，这个我真不清楚。
diagnosis: 学习者准确指出“岗位不变”时，不能把“接入 AI”误当作“流程被改变”；目前尚未区分局部提速与交接方式、异常闭环、验收指标的改变。
next_action: 先用同一工厂的订单异常，说明 AI 改的不是谁的职业名称，而是信息如何进入系统、何时被拦截、谁只处理例外；再请学习者用自己的话复述。
evidence_receipt: learner-log.md#lesson-01-evidence-03
```

## lesson-01-evidence-04

```yaml
lesson: 01
status: active
learner_evidence: |
  把它从一些简单的、重复的、不需要判断力的事情中抽离出来，让 AI 去放大它的判断力。

  AI 不外包判断。

  你可以外包你的思考过程，但不能外包你的理解本身。
passed_dimensions:
  - 区分了重复性执行与需承担后果的判断
  - 说明了 AI 的价值是放大专业人员判断，而非以岗位替代为目标
diagnosis: 核心机制已掌握；还需用一个新业务场景把“判断不可外包”落到可执行的边界，即哪些步骤可交给 AI、哪些必须由人签字承担结果。
next_action: 变式迁移题
evidence_receipt: learner-log.md#lesson-01-evidence-04
```

## lesson-01-evidence-05

```yaml
lesson: 01
status: completed
mastery_band: demonstrated_transfer
route: advance
learner_evidence: |
  AI 可以预测天气、整理历史销量和库存，并建议“明天多进 20% 原料”。负责人要结合经验决定是否拍板。

  还要判断模型是否只是拟合了过去、建议是否可靠，模型本身会不会有问题。
passed_dimensions:
  - 在新场景中区分数据整理和预测建议，与经营者承担后果的决策
  - 主动提出模型有效性和失效风险，而非把建议当作事实
diagnosis: 已完成本章核心迁移。下一章可进入“把建议放进流程前，怎样验证它、设边界和处理例外”。
evidence_receipt: learner-log.md#lesson-01-evidence-05
```

## lesson-02-evidence-01

```yaml
lesson: 02
status: active
learner_evidence: |
  最不该着急自动化的是人处理意外，也就是例外。
passed_dimensions:
  - 指出了 AI 工作流中不宜仓促自动化的例外处理环节
diagnosis: 方向正确，但尚未说明例外的具体触发条件以及为何其后果需要人承担。
next_action: 用一个小龙虾采购例外完成费曼补全
evidence_receipt: learner-log.md#lesson-02-evidence-01
```

## lesson-02-evidence-02

```yaml
lesson: 02
status: completed
mastery_band: demonstrated_transfer
route: advance
learner_evidence: |
  突然出现瘟疫，导致小龙虾产量断崖式下滑、价格可能剧烈变化时，不能让 AI 自动下采购单。
passed_dimensions:
  - 用外部冲击举出历史模式失效的具体例外
  - 明确了异常状态下应停止自动执行并交由人判断
diagnosis: 已掌握第 02 篇的关键边界：落地不是把建议直接变成动作，而是要有规则、例外升级与人工刹车。
evidence_receipt: learner-log.md#lesson-02-evidence-02
```

## lesson-03-evidence-01

```yaml
lesson: 03
status: active
learner_evidence: |
  可以根据小龙虾采购工作流做定制化。

  1. 路由分化：哪个地方用便宜的模型，哪个地方用贵的模型，做专门化路由；切割一部分上下文给便宜模型，把更聪明、更贵的部分放在关键环节。

  2. 异常治理：后续迭代、复盘、处理突发应急情况，包括安全性问题。
passed_dimensions:
  - 将路由落实为按业务环节和风险分配模型能力，而非统一选最强模型
  - 将异常治理识别为上线后的持续交付，而非一次性部署
diagnosis: 已形成可售服务雏形。仍需明确客户购买的经营结果、服务边界和收费节奏；“安全性”还需区分数据／权限安全与供应链经营异常。
next_action: 用一句面对客户的话，说明持续服务替客户负责什么结果，以及不替客户承担什么决策。
evidence_receipt: learner-log.md#lesson-03-evidence-01
```

## lesson-03-evidence-02

```yaml
lesson: 03
status: completed
mastery_band: demonstrated_transfer
route: complete
learner_evidence: |
  我觉得未来 AI 的落地，肯定是能够承诺客户持续改善其工作流的效率，但绝对不能为客户承担风险。
passed_dimensions:
  - 明确了持续服务的价值在于改善工作流，而非一次性卖模型
  - 明确了服务商不应替客户承担最终经营风险
diagnosis: 已完成三篇路径。商业表达上应将“承诺改善”落为共同定义并持续跟踪的指标，避免把不可控结果写成无条件保证。
evidence_receipt: learner-log.md#lesson-03-evidence-02
```
