---
name: concept-bridge
description: 基于课程学习进度，更新概念掌握度并推荐下一步学习路径。读取课程目录的 .concepts.json，根据已完成章节更新概念库掌握度，计算概念相关度，生成带 bridge 说明的个性化推荐。适用于「学完这章该学什么」「更新我的学习进度」「推荐相关课程」的场景。
---

# 概念桥接器

## 一、任务定位

基于课程学习进度，自动更新概念掌握度，并推荐下一步学习路径。输入是课程目录路径 + 已完成章节；输出是概念掌握度更新报告 + 带 bridge 说明的学习推荐。

## 二、输入格式

```bash
/concept-bridge /path/to/course --chapters 01,02,03
```

**参数说明**：
- `--chapters`：已完成章节列表（逗号分隔，如 `01,02,03`）
- 可选 `--all`：标记整个课程已完成

**示例**：
```bash
# 标记完成前 3 章
/concept-bridge /Users/housibo/Documents/dacapo-学习仓库/courses/AI检测原理 --chapters 01,02,03

# 标记整个课程完成
/concept-bridge /Users/housibo/Documents/dacapo-学习仓库/courses/如实所现 --all
```

## 三、核心流程

### 阶段 1：读取课程元数据（1 分钟）

1. 检查课程目录是否存在 `.concepts.json`
2. 如不存在，提示用户先运行 `/course-generator` 或手动创建
3. 解析 `.concepts.json` 获取章节概念关联

**数据结构**（详见 `references/concepts-json-schema.md`）：
```json
{
  "01.md": {
    "mainConcepts": ["对齐", "风格分布压窄"],
    "relatedConcepts": {
      "perplexity": { "relevance": 0.7, "context": "下一章引入的检测指标" },
      "RLHF": { "relevance": 0.6, "context": "对齐的具体技术" }
    }
  }
}
```

### 阶段 2：更新概念掌握度（2 分钟）

**输入**：已完成章节的 `mainConcepts`

**处理逻辑**（详见 `references/update-mastery.md`）：

1. **提取已学概念**：
   - 遍历已完成章节
   - 收集所有 `mainConcepts`
   - 去重得到概念列表

2. **读取概念库现状**：
   - 从 `/Users/housibo/Documents/dacapo-学习仓库/concepts/` 读取各概念文件
   - 提取当前 `mastery` 字段（0-100）

3. **增量更新规则**：
   - 首次学习：`mastery += 30`
   - 二次巩固：`mastery += 20`
   - 三次及以上：`mastery += 10`（上限 100）
   - 记录更新时间与来源课程

4. **写回概念文件**：
   - 更新 `mastery` 字段
   - 追加 `learningHistory` 记录：
     ```json
     {
       "date": "2026-09-30",
       "source": "courses/AI检测原理/01.md",
       "masteryBefore": 40,
       "masteryAfter": 70
     }
     ```

**输出**：更新报告（Markdown 表格）
```markdown
| 概念 | 更新前 | 更新后 | 变化 | 来源章节 |
|------|--------|--------|------|----------|
| 对齐 | 40     | 70     | +30  | 01.md    |
| 风格分布压窄 | 0 | 30 | +30  | 01.md    |
```

### 阶段 3：计算概念相关度（2 分钟）

调用 `scripts/calculate-relevance.js` 获取全局概念关系。

**脚本职责**（详见 `references/calculate-relevance.md`）：
- 读取所有概念文件的 `relatedConcepts` 字段
- 构建全局概念图（节点 = 概念，边 = 相关度）
- 计算传递相关度（A → B → C）
- 输出 `.learning-progress/concept-relevance.json`

**输出格式**：
```json
{
  "对齐": {
    "RLHF": 0.8,
    "perplexity": 0.7,
    "风格分布压窄": 0.6
  }
}
```

**调用方式**：
```bash
node /Users/housibo/Documents/dacapo-学习仓库/scripts/calculate-relevance.js
```

**何时调用**：
- 每次 concept-bridge 运行时都调用（确保数据最新）
- 或用户手动触发：`/concept-bridge --recalculate-only`

### 阶段 4：生成学习推荐（3 分钟）

调用 `scripts/recommend.js` 生成个性化推荐。

**输入数据**：
1. 已学概念列表（从阶段 2）
2. 概念相关度矩阵（从阶段 3）
3. 概念掌握度（从概念库）
4. 课程目录元数据（从 `courses/INDEX.md`）

**推荐算法**（详见 `references/recommend-algorithm.md`）：

1. **候选概念筛选**：
   - 从已学概念的 `relatedConcepts` 中提取
   - 过滤已掌握概念（mastery ≥ 80）
   - 过滤相关度 < 0.5 的概念

2. **评分排序**：
   ```
   score = relevance × 0.6 + (1 - mastery/100) × 0.4
   ```
   - `relevance`：与已学概念的最高相关度
   - `mastery`：当前掌握度（越低优先级越高）

3. **生成 bridge 说明**：
   - 分析概念 A（已学）→ 概念 B（推荐）的关系
   - 从 `.concepts.json` 的 `context` 字段提取桥接线索
   - 生成一句话说明：
     ```
     "你已学习「对齐」，「RLHF」是其具体实现技术"
     "「风格分布压窄」是「对齐」的副作用表现"
     ```

4. **匹配课程资源**：
   - 查询 `courses/` 目录
   - 查找包含推荐概念的课程
   - 定位到具体章节

**输出格式**：
```markdown
### 推荐学习路径

#### 1. RLHF（推荐度：0.85）
- **为什么推荐**：你已学习「对齐」，「RLHF」是其核心实现技术
- **当前掌握度**：20%
- **相关课程**：
  - 《AI 检测原理》第 3 章（未学）
  - 《强化学习基础》第 5-7 章

#### 2. perplexity（推荐度：0.78）
- **为什么推荐**：「对齐」效果的常用检测指标
- **当前掌握度**：0%
- **相关课程**：
  - 《AI 检测原理》第 2 章（未学）
```

**调用方式**：
```bash
node /Users/housibo/Documents/dacapo-学习仓库/scripts/recommend.js \
  --learned "对齐,风格分布压窄" \
  --relevance-file .learning-progress/concept-relevance.json \
  --concepts-dir concepts/ \
  --courses-dir courses/
```

### 阶段 5：输出汇总报告（1 分钟）

**报告结构**：
```markdown
# 学习进度更新报告

## 本次学习
- 课程：《AI 检测原理》
- 完成章节：01-03
- 新增概念：3 个

## 概念掌握度变化
[表格见阶段 2 输出]

## 推荐学习路径
[内容见阶段 4 输出]

## 数据更新
- ✅ 概念库已更新（3 个文件）
- ✅ 相关度矩阵已重新计算
- 📊 当前概念总数：47 个
- 📈 平均掌握度：32%

---
生成时间：2026-09-30 14:23
```

**保存位置**：
- 主报告：`courses/<课程名>/.progress-report-<日期>.md`
- 追加到：`.learning-progress/history.md`（历史记录）

## 四、脚本依赖

### scripts/calculate-relevance.js

**职责**：构建全局概念相关度矩阵

**输入**：
- `concepts/` 目录（所有概念文件）
- 可选：`--output` 指定输出路径

**输出**：
- `.learning-progress/concept-relevance.json`

**运行频率**：
- 每次 concept-bridge 调用时
- 新增概念后手动触发

**详细实现**：见 `references/calculate-relevance.md`

### scripts/recommend.js

**职责**：基于相关度和掌握度生成推荐

**输入参数**：
- `--learned`：已学概念列表（逗号分隔）
- `--relevance-file`：相关度矩阵文件路径
- `--concepts-dir`：概念库目录
- `--courses-dir`：课程目录

**输出**：
- Markdown 格式的推荐清单（stdout）
- JSON 格式的结构化数据（可选 `--json`）

**详细实现**：见 `references/recommend-algorithm.md`

## 五、目录与文件约定

**必需目录**：
```
dacapo-学习仓库/
├── concepts/                  # 概念库（每个概念一个文件）
├── courses/                   # 课程目录
│   ├── INDEX.md              # 课程索引
│   └── <课程名>/
│       ├── .concepts.json    # 章节概念关联（必需）
│       ├── 主页.md
│       ├── 01.md, 02.md, ...
│       └── .progress-report-*.md  # 本 skill 生成
├── scripts/                   # 辅助脚本
│   ├── calculate-relevance.js
│   └── recommend.js
└── .learning-progress/        # 学习数据（自动创建）
    ├── concept-relevance.json
    └── history.md
```

**概念文件结构**（示例）：
```markdown
---
name: 对齐
category: AI 技术
mastery: 70
lastUpdated: 2026-09-30
---

# 对齐

## 定义
[...]

## 相关概念
- RLHF (0.8)
- 风格分布压窄 (0.6)

## 学习历史
- 2026-09-30：从 40% 提升至 70%（课程：AI 检测原理/01.md）
```

## 六、任务边界

**做的事**：
- 更新概念掌握度（基于完成章节）
- 计算全局概念相关度
- 生成个性化学习推荐
- 输出进度报告

**不做的事**：
- 不评价学习质量（只记录完成事实）
- 不生成新课程（推荐现有课程）
- 不修改课程内容
- 不强制学习路径（只提供建议）

## 七、质量自检

交付前逐条检查：

1. **数据完整性**：
   - [ ] 所有已完成章节的 mainConcepts 都已提取
   - [ ] 概念库文件都已更新（检查时间戳）
   - [ ] concept-relevance.json 已重新生成

2. **推荐合理性**：
   - [ ] 推荐概念的 relevance ≥ 0.5
   - [ ] 推荐概念的 mastery < 80
   - [ ] bridge 说明能清晰解释「为什么推荐」

3. **报告可读性**：
   - [ ] 表格对齐，数字正确
   - [ ] 课程链接可点击
   - [ ] 无「undefined」或空值

4. **文件写入**：
   - [ ] 概念文件的 learningHistory 已追加
   - [ ] .progress-report 已保存到课程目录
   - [ ] .learning-progress/history.md 已追加记录

## 八、错误处理

**常见错误与解决**：

1. **缺少 .concepts.json**：
   ```
   ❌ 错误：课程目录未找到 .concepts.json
   💡 解决：运行 /course-generator 重新生成，或手动创建
   ```

2. **概念文件不存在**：
   ```
   ⚠️ 警告：概念「XXX」在库中不存在，跳过更新
   💡 建议：运行 /concept-learning 提取该概念
   ```

3. **脚本执行失败**：
   ```
   ❌ 错误：calculate-relevance.js 返回错误码 1
   💡 检查：Node.js 版本 ≥ 18，依赖已安装（npm install）
   ```

4. **章节号不存在**：
   ```
   ⚠️ 警告：章节 04.md 不在 .concepts.json 中，跳过
   ```

## 九、参考文档

- `references/concepts-json-schema.md` — .concepts.json 数据结构详解
- `references/update-mastery.md` — 概念掌握度更新算法
- `references/calculate-relevance.md` — 相关度计算脚本实现
- `references/recommend-algorithm.md` — 推荐算法详解与调优
- `/course-generator` — 课程生成器（生成 .concepts.json）
- `/concept-learning` — 概念提取器（创建概念文件）

---

## 调用示例

```bash
# 基础用法：标记完成章节
/concept-bridge /Users/housibo/Documents/dacapo-学习仓库/courses/AI检测原理 --chapters 01,02,03

# 标记整个课程完成
/concept-bridge courses/如实所现 --all

# 仅重新计算相关度（不更新掌握度）
/concept-bridge --recalculate-only

# 查看某个概念的学习路径推荐（不更新进度）
/concept-bridge --recommend-for "对齐" --dry-run
```

## 十、未来扩展

**潜在功能**（当前版本不实现）：

1. **间隔重复提醒**：
   - 根据遗忘曲线计算复习时间
   - 自动生成复习任务清单

2. **学习路径可视化**：
   - 生成概念图（已学 / 未学 / 推荐）
   - D3.js 或 Mermaid 图表

3. **多人协作**：
   - 对比不同学习者的进度
   - 生成小组学习建议

4. **自适应推荐**：
   - 根据学习速度调整推荐数量
   - 识别薄弱环节（多次学习但 mastery 仍低）
