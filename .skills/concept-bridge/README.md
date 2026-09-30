# concept-bridge

基于课程学习进度，更新概念掌握度并推荐下一步学习路径。

## 功能说明

自动追踪学习进度，更新概念库中的掌握度数据，并基于概念相关度生成个性化学习推荐。

**核心能力**：
- 根据已完成章节更新概念掌握度
- 计算全局概念相关度矩阵
- 生成带 bridge 说明的学习推荐
- 输出进度报告和学习路径

## 使用场景

- 学完某个课程章节，想更新学习进度
- 想知道「学完这章该学什么」
- 需要个性化的下一步学习路径
- 想查看概念掌握度变化

## 输入格式

```bash
# 标记完成指定章节
/concept-bridge /path/to/course --chapters 01,02,03

# 标记整个课程完成
/concept-bridge /path/to/course --all

# 仅重新计算相关度（不更新掌握度）
/concept-bridge --recalculate-only
```

## Bridge 机制说明

**什么是 Bridge**：

Bridge 是概念 A（已学）→ 概念 B（推荐）之间的关系说明，帮助你理解「为什么现在学这个」。

**生成方式**：
1. 从 `.concepts.json` 的 `context` 字段提取桥接线索
2. 分析概念间的依赖关系（基础/应用/平行）
3. 生成一句话说明

**示例**：
- "你已学习「对齐」，「RLHF」是其具体实现技术"
- "「风格分布压窄」是「对齐」的副作用表现"
- "「perplexity」是检测「对齐」效果的常用指标"

## 工作流程

### 阶段 1：读取课程元数据
- 检查课程目录是否存在 `.concepts.json`
- 解析章节概念关联

### 阶段 2：更新概念掌握度
- 提取已完成章节的 `mainConcepts`
- 读取概念库现状
- 按增量规则更新（首次 +30，二次 +20，三次及以上 +10）
- 记录更新时间与来源课程

**更新规则**：

| 学习次数 | 掌握度增量 | 上限 |
|---|---|---|
| 首次学习 | +30 | 100 |
| 二次巩固 | +20 | 100 |
| 三次及以上 | +10 | 100 |

### 阶段 3：计算概念相关度
调用 `scripts/calculate-relevance.js` 构建全局概念图，输出 `.learning-progress/concept-relevance.json`。

### 阶段 4：生成学习推荐
调用 `scripts/recommend.js` 基于相关度和掌握度生成推荐清单。

**推荐算法**：
```
score = relevance × 0.6 + (1 - mastery/100) × 0.4
```

筛选条件：
- 相关度 ≥ 0.5
- 掌握度 < 80
- 按评分降序排列

### 阶段 5：输出汇总报告
生成进度更新报告，包括：
- 概念掌握度变化表
- 推荐学习路径（带 bridge 说明）
- 匹配的课程资源

## 输出示例

```markdown
# 学习进度更新报告

## 本次学习
- 课程：《AI 检测原理》
- 完成章节：01-03
- 新增概念：3 个

## 概念掌握度变化
| 概念 | 更新前 | 更新后 | 变化 | 来源章节 |
|------|--------|--------|------|----------|
| 对齐 | 40     | 70     | +30  | 01.md    |
| 风格分布压窄 | 0 | 30 | +30  | 01.md    |

## 推荐学习路径

### 1. RLHF（推荐度：0.85）
- **为什么推荐**：你已学习「对齐」，「RLHF」是其核心实现技术
- **当前掌握度**：20%
- **相关课程**：
  - 《AI 检测原理》第 3 章（未学）
  - 《强化学习基础》第 5-7 章

### 2. perplexity（推荐度：0.78）
- **为什么推荐**：「对齐」效果的常用检测指标
- **当前掌握度**：0%
- **相关课程**：
  - 《AI 检测原理》第 2 章（未学）
```

## 脚本依赖

### scripts/calculate-relevance.js
- 职责：构建全局概念相关度矩阵
- 输入：`concepts/` 目录
- 输出：`.learning-progress/concept-relevance.json`

### scripts/recommend.js
- 职责：基于相关度和掌握度生成推荐
- 输入：已学概念列表、相关度矩阵、概念库、课程目录
- 输出：Markdown 格式推荐清单

## 目录约定

```
dacapo-学习仓库/
├── concepts/                  # 概念库（每个概念一个文件）
├── courses/                   # 课程目录
│   ├── INDEX.md              # 课程索引
│   └── <课程名>/
│       ├── .concepts.json    # 章节概念关联（必需）
│       └── .progress-report-*.md  # 本 Skill 生成
├── scripts/
│   ├── calculate-relevance.js
│   └── recommend.js
└── .learning-progress/        # 学习数据（自动创建）
    ├── concept-relevance.json
    └── history.md
```

## 与其他 Skill 的关系

- **依赖 `/course-generator`**：读取其生成的 `.concepts.json`
- **为学习路径规划提供数据**：更新后的掌握度可用于其他 Skills
- **可与 `/dbs-learning` 配合**：学习进度同步到概念库

## 参考文档

详细执行规范见 `SKILL.md`，包括：
- `references/concepts-json-schema.md` — 数据结构详解
- `references/update-mastery.md` — 掌握度更新算法
- `references/calculate-relevance.md` — 相关度计算实现
- `references/recommend-algorithm.md` — 推荐算法详解与调优
