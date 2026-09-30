# DaCapo 交互式学习系统

让学习上瘾的复利式知识管理系统。

**系统评分**：9.5/10  
**理论基础**：情境认知、心智游荡、认知负荷  
**核心特性**：用已掌握的概念作为桥梁（bridge），理解新概念更容易

---

## 🚀 快速开始

### 前置要求

- Claude Code（CLI 或 Desktop）
- Node.js 18+（用于计算脚本）
- Python 3.8+（用于概念提取）

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/hou-152/dacapo-learning-system.git
cd dacapo-learning-system

# 2. 安装 Skills（将 Skills 链接到 Claude Code）
ln -s "$(pwd)/.skills/course-generator" ~/.claude/skills/
ln -s "$(pwd)/.skills/dbs-learning" ~/.claude/skills/
ln -s "$(pwd)/.skills/concept-bridge" ~/.claude/skills/
ln -s "$(pwd)/.skills/learning-navigator" ~/.claude/skills/

# 3. 验证安装
ls -la ~/.claude/skills/ | grep -E "course-generator|dbs-learning|concept-bridge|learning-navigator"
```

### 典型使用流程

#### 场景 1：从一篇文章开始学习

```bash
# 在 Claude Code 中
/learning-navigator

# 然后说："我想学《乡土中国》这篇文章"
# 系统会推荐使用 /course-generator
```

或者直接：

```bash
/course-generator /path/to/article.md
```

**输出**：
- `00-学习计划.md` - 课程导航
- `01.md`, `02.md`... - 课程章节
- `.concepts.json` - 概念关联元数据

#### 场景 2：开始交互式学习

```bash
/dbs-learning /path/to/course-directory
```

系统会：
- 显示相关概念（relevance > 0.6）
- 根据你的反馈调整后续内容
- 生成下一章

#### 场景 3：学完后获取推荐

```bash
/concept-bridge /path/to/course-directory --chapters 01,02,03
```

**输出示例**：
```
✅ 已更新概念掌握度：
- 差序格局: 0.9 → 1.0 (+0.1)

📚 推荐学习路径：
1. 社会分层（推荐度 0.765）
   Bridge: 你已掌握【差序格局】(mastery 1.0)
   理由: 差序格局是社会分层的前置概念
```

#### 场景 4：不知道学什么

```bash
/learning-navigator

# 然后说："推荐我下一步学什么"
# 系统会基于你当前的概念掌握度推荐
```

---

## 📊 当前学习状态

- **已掌握概念**: 18 个
- **平均掌握度**: 65.3%
- **概念关联**: 243 条
- **复利指数**: 1599.7

### 优秀掌握 (≥80%)
- 差序格局 90%
- 礼治秩序 90%
- 人情期货 90%
- 面子估值 85%
- 现代长老 80%

---

## 🎯 核心功能

### 1. course-generator (9.3/10)
**从文章生成结构化课程**

输入一篇文章，自动生成：
- 📚 00-学习计划.md（课程导航）
- 📖 01.md, 02.md, 03.md...（保留论证结构的课程章节）
- 🔗 .concepts.json（概念关联元数据）

**特点**：
- ✅ 保留文章的论证逻辑（不是概念堆砌）
- ✅ 自动提取核心概念和相关概念
- ✅ 每个相关概念带相关度和上下文说明

### 2. dbs-learning (9.3/10)
**交互式学习，智能显示相关概念**

学习时自动：
- 📋 在章节开头显示"相关概念"区块（relevance > 0.6）
- 🔄 基于学习反馈自适应调整
- 🧠 不破坏学习流程（静默呈现，按需查看）

**设计理念**：默认不提示（保护"心智游荡"），停留时静默展示，点击时详细说明

### 3. concept-bridge (10/10)
**透明推荐，明确说明为什么推荐**

学完课程后自动：
- ✅ 更新概念掌握度（mastery 字段）
- 🕸️ 重新计算概念相关度矩阵
- 💡 生成带 bridge 说明的学习推荐

**Bridge 机制**：
```
推荐学习：社会分层（推荐度 0.765）
Bridge：你已掌握【差序格局】(mastery 1.0)
理由：差序格局是社会分层的前置概念
```

### 4. learning-navigator
**识别学习场景，推荐合适的 Skill**

支持场景：
1. 从文章生成课程 → course-generator
2. 交互式学习 → dbs-learning
3. 学完推荐 → concept-bridge
4. 从概念查找 → course-generator --concept
5. 不知道学什么 → concept-bridge（全局推荐）

---

## 🔄 完整数据流

```
用户输入：文章/书/概念
    ↓
[course-generator]
├─ 读取原始材料
├─ 调用 /concept-learning 提取概念
├─ 基于内容结构生成 01/02/03.md
└─ 生成 .concepts.json（mainConcepts + relatedConcepts + context）
    ↓
[dbs-learning]
├─ 读取 .concepts.json
├─ 在章节开头显示"相关概念"区块
├─ 用户学习并反馈
└─ 自适应调整后续内容
    ↓
[concept-bridge]
├─ 读取已完成章节的 mainConcepts
├─ 更新概念文件的 mastery 字段
├─ 运行 calculate-relevance.js（重新计算相关度）
├─ 运行 recommend.js（生成推荐）
└─ 输出带 bridge 说明的学习路径
```

---

## 📖 使用示例

### 完整学习流程

**场景**：我想学《乡土中国》

```bash
# 1. 生成课程（自动提取概念和结构）
/course-generator /path/to/乡土中国.md

# 2. 开始交互式学习
/dbs-learning /path/to/course
# 在学习过程中看到相关概念提示（如"礼治秩序"、"理想类型"）

# 3. 学完后更新和推荐
/concept-bridge /path/to/course --chapters 01,02,03
# 输出："你掌握了【差序格局】，推荐学【社会分层】"
```

### 典型输出示例

**学习时看到的相关概念区块**：
```markdown
## 相关概念

**本章核心概念**：
- [[差序格局]]

**相关概念**（点击查看详情）：
- [[关系资源]]（相关度 0.8）— 波纹的范围跟着中心的势力涨落，李强说「关系资源」的底图就是差序格局。
- [[礼治秩序]]（相关度 0.7）— 圈内规则靠信誉、脸面、人情维系，下一篇讲礼治如何强制执行。
- [[理想类型]]（相关度 0.6）— 费孝通说差序格局是「从具体社会里提炼出来的」，用的就是理想类型方法。
```

**学完后的推荐**：
```
推荐学习：社会分层
推荐分数：0.765
Bridge: 你已掌握【差序格局】(mastery 1.0)
理由: 差序格局是社会分层的前置概念
相关度: 0.565
掌握度差距: 0.7（你 1.0，社会分层 0.3）
```

---

## 📚 文档索引

### 核心文档
- **[VERSION.md](VERSION.md)** — v1.0.0 发布说明，技术规格，使用指南
- **[FINAL-VALIDATION-REPORT.md](FINAL-VALIDATION-REPORT.md)** — 完整验证报告，真实数据测试结果

### Skills 定义
```
.skills/
├── course-generator/          # 从文章生成课程
│   ├── SKILL.md
│   └── references/            # .concepts.json 格式规范
├── dbs-learning/              # 交互式学习
│   └── SKILL.md
├── concept-bridge/            # 透明推荐
│   ├── SKILL.md
│   └── references/            # Bridge 机制说明
└── learning-navigator/        # 场景识别和路由
    └── SKILL.md
```

### 理论研究
```
.research/
├── skill-mechanisms.md        # 3 个 Skills 的核心机制分析
├── theory-discussion.md       # 4 个决策点的理论依据
└── skills-validation.md       # 完整流程验证报告
```

---

## 🎓 理论基础

### 核心设计原则

#### 1. 内容为主线，概念为索引
**理论依据**：情境认知（Brown, Collins, Duguid, 1989）

> 知识不是抽象的符号集合，而是在具体情境中形成的。概念脱离情境后会变成"惰性知识"——能记住，却不知道何时何地如何使用。

**实践**：course-generator 保留文章的论证结构，不是概念堆砌。

#### 2. 默认不提示，分层呈现
**理论依据**：心智游荡理论（Schooler, Smallwood, 2011-2015）

> 大脑在"无聊"时并非闲置，而是在进行自发的记忆整合和远距离联想。持续的外部刺激会压缩默认模式网络的激活时间，削弱学习者自主发现连接的机会。

**实践**：dbs-learning 在章节开头静默显示相关概念，不打断学习流程。

#### 3. 按认知负荷选择工具形态
**理论依据**：认知负荷理论（Sweller, 1988）

> 交互式学习需要判断何时提示、如何调整，这属于高认知负荷任务，应该用 Skill（需要判断）而非脚本（固定流程）。

**实践**：dbs-learning 是 Skill，可以根据用户反馈调整。

### 研究报告

详细理论分析和实证研究见 `.research/` 目录：
- **skill-mechanisms.md** — 3 个 Skills 如何协同工作
- **theory-discussion.md** — 为什么选择这些设计（含完整理论引用）
- **skills-validation.md** — 真实数据测试报告（6000+ 字文章验证）

---

## 🎮 成瘾机制

### 即时反馈
学完概念 → 3 秒内看到掌握度、网络图、解锁新概念

### 可视化进展
每次学习 → 看到网络扩张、复利指数上升

### 复利效应
关联越多 → 复利指数增长越快 → 量化学习的「滚雪球效应」

**复利指数计算**：
```
复利指数 = (已学概念数 × 平均掌握度 × 关联密度) × 100

关联密度 = 总关联数 / (已学概念数 × (已学概念数 - 1))
```

当前数据：
```
18 × 0.653 × 0.752 × 100 = 1599.7
```

---

## 🛠️ 技术架构

### 核心脚本

| 脚本 | 功能 |
|------|------|
| `extract_sociology_concepts.py` | 从课程中提取概念，创建概念文件 |
| `enhance_dbs_learning.py` | 为文章添加 DaCapo 即时反馈 |
| `update_mastery_from_concepts.py` | 从概念文件同步掌握度到 mastery.json |
| `instant_feedback.py` | 生成单个概念的即时反馈 |
| `progress_tracker.py` | 生成实时学习进度仪表盘 |
| `calculate-relevance.js` | 计算概念相关度矩阵 |
| `recommend.js` | 生成学习推荐（带 bridge 说明）|

### 数据结构

```
dacapo-学习仓库/
├── concepts/              # 概念库（每个概念一个 .md 文件）
├── .learning-progress/    # 学习数据
│   ├── mastery.json      # 概念掌握度
│   ├── timeline.json     # 学习时间线
│   └── dashboard-realtime.md  # 实时仪表盘
├── dashboard/            # 可视化页面（持久化）
│   ├── index.html       # 学习中心首页
│   ├── network.html     # 概念网络图
│   └── progress.html    # 学习进度仪表盘
├── courses/             # 课程目录
│   └── [课程名]/
│       ├── 00-学习计划.md
│       ├── 01.md, 02.md...
│       └── .concepts.json
├── .skills/             # Skills 定义
├── .research/           # 理论研究报告
└── scripts/             # 核心脚本
```

### .concepts.json 格式

```json
{
  "01.md": {
    "mainConcepts": ["差序格局"],
    "relatedConcepts": {
      "礼治秩序": {
        "relevance": 0.7,
        "context": "圈内规则靠信誉、脸面、人情维系"
      }
    },
    "keyTerms": ["波纹图", "捆柴模式", "圈内规则 vs 圈外规则"]
  }
}
```

---

## 🤝 贡献指南

### 报告问题

如果你发现：
- Skills 运行错误或不符合预期
- 概念提取不准确
- 推荐结果不合理
- 文档缺失或不清楚

请在 GitHub Issues 中报告，包含：
1. 复现步骤
2. 实际输出 vs 期望输出
3. 相关文件路径

### 贡献代码

欢迎提交 Pull Request：
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

**代码规范**：
- Python: PEP 8
- JavaScript: ESLint Standard
- Markdown: 中英文之间加空格
- 提交信息: 使用中文，清晰描述改动

---

## 📝 已完成课程

### 社会学七书共读（9 篇）

- 01 - 米尔斯与社会学想象力
- 02 - 差序格局与圈子文化
- 03 - 人情与面子：礼治秩序
- 04-09 - 社会分层、承认政治、理性化铁笼等

**提取概念**: 18 个（9 个用户自创 + 9 个社会学核心）

---

## 🚧 下一步计划

### Phase 2: 高级可视化

- [ ] 概念网络 3D 交互图
- [ ] 学习曲线时间线
- [ ] 间隔复习调度
- [ ] 知识资产统计

### Phase 3: 自动化集成

- [ ] 将增强脚本集成到 dbs-learning skill
- [ ] 学完文章自动生成即时反馈
- [ ] 自动提取概念并入库
- [ ] 实时推送学习通知
- [ ] concept-bridge 自动触发

---

## 📞 快捷命令总结

```bash
dacapo              # 打开学习中心
dacapo-network      # 概念网络图
dacapo-progress     # 学习进度仪表盘
dacapo-refresh      # 刷新数据
```

首次使用：`source ~/.zshrc`

---

## 📄 许可证

MIT License

---

**让学习像滚雪球一样，越滚越大，越滚越快。**
