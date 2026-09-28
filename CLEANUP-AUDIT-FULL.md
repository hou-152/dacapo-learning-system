# dacapo-学习仓库 - 完整清理审计报告

**审计时间**：2026-09-28  
**审计范围**：整个仓库目录结构、文件内容、历史遗留  
**理论依据**：ETL 模式（Extract-Transform-Load）

---

## 一、ETL 分类审计结果

### Extract 层（原始提取数据 - 应归档）

#### 1.1 旧目录结构（5 个）

| 目录 | 大小估算 | 内容 | 处理建议 |
|---|---|---|---|
| `01-交互式学习/` | 小 | 旧结构残留，仅有 `02-课程真源/和 agent 一起做规划/assets/疑问/` | 移至 `.archive/extract/` |
| `02-课程真源/` | 小 | 2 个旧课程目录：`Agentic Engineering 工作流/`、`梁文锋投资者交流会的战略与技术判断/` | 移至 `.archive/extract/` |
| `04-用户原话与费曼/` | 未知 | 空或极少内容 | 移至 `.archive/extract/` |
| `05-证据原子/` | 未知 | 空或极少内容 | 移至 `.archive/extract/` |
| `11-研究与验收/` | 中 | `Jev打标-历史反馈-2026-09-23/` 子目录 | 移至 `.archive/extract/` |

**小计**：5 个旧目录，全部属于 Extract 阶段的原始数据

---

### Transform 层（转换过程产物 - 应归档）

#### 2.1 根目录临时报告（23 个 .md）

```
CLEANUP-PLAN.md
CONCEPT-COMPOUNDING-REPORT.md
CONCEPT-GRAPH.md
CONCEPT-LINK-AUDIT.md
CONCEPT-LINKING-RESEARCH.md
CONCEPT-MINING-MVP-REPORT.md
CONCEPT-MINING-RESEARCH.md
CONTRADICTIONS.md
GENERALIZATION-TEST-FINAL-REPORT.md
GENERALIZATION-TEST-PROGRESS.md
INTEGRATION-REPORT.md
MIGRATION-PLAN.md
MIGRATION-PURITY-THEORY.md
MVP-FINAL-REPORT.md
RELEASE-v2.0.0.md
SOLUTION-IMPLEMENTATION-PROGRESS.md
SOLUTION-RESEARCH.md
UNIFIED-MANAGEMENT-REPORT.md
WIKILINK-FIX-REPORT.md
purpose.md
落地案例描述-简化版.md
落地案例描述.md
README.md （保留）
```

**处理建议**：
- `README.md` 保留（最终文档）
- `MIGRATION-PURITY-THEORY.md` 保留（刚生成的理论指导）
- 其余 21 个报告移至 `.archive/transform/reports/2026-09-28/`

#### 2.2 根目录压缩包（5 个 .tar.gz）

```bash
# 需要列出具体文件名和大小
ls -lh *.tar.gz
```

**处理建议**：
- 确认内容后移至 `.archive/transform/snapshots/`
- 如果是重复备份，可直接删除

#### 2.3 Git worktrees 残留（3 个）

```
.claude/worktrees/solution-contradiction-1/
.claude/worktrees/solution-contradiction-2/
.claude/worktrees/solution-contradiction-3/
```

**处理建议**：
- 检查是否有未提交的工作
- 确认后用 `git worktree remove` 清理

---

### Load 层（最终成果 - 保留在根目录）

#### 3.1 核心资产目录（保留）

| 目录 | 状态 | 说明 |
|---|---|---|
| `concepts/` | ✅ 保留 | 60 个概念文件 |
| `courses/` | ✅ 保留 | 47 个课程目录（需进一步审核内容质量） |
| `user-feedback/` | ✅ 保留 | 用户反馈数据（2.8M） |
| `scripts/` | ✅ 保留 | 工具脚本 |
| `README.md` | ✅ 保留 | 项目说明 |
| `courses/README.md` | ✅ 保留 | 课程索引 |
| `courses/INDEX.md` | ✅ 保留 | 课程索引 |

---

## 二、用户明确要求的过滤清单

### 1. 学习画布（.canvas 文件）- 不希望进来

**发现数量**：16 个 `.canvas` 文件

```
courses/学习观-于建国/学习画布.canvas
courses/我常常是错的/学习画布.canvas
courses/认识自己-ENTP与天赋挖掘/学习画布.canvas
courses/社会学基本概念/学习画布.canvas
courses/个人学习工作台实践/学习画布.canvas
courses/从知识生产到IP定位/学习画布.canvas
courses/拜物教/学习画布.canvas
courses/这世界既残酷也温柔/学习画布.canvas
courses/自迭代小龙虾与自迭代Skill/学习画布.canvas
courses/frontier-分层/学习画布.canvas
courses/dontbesilent-商业方法论/学习画布.canvas
courses/双向钢人论证与深度思考Prompt/学习画布.canvas
courses/2026气运+1/学习画布.canvas
courses/和 agent 一起做规划/学习画布.canvas
courses/AI 检测原理与课堂判读/学习画布.canvas
courses/知识库/学习画布.canvas
```

**处理建议**：
- 移至 `.archive/transform/canvas-views/`
- 或直接删除（因为这些是工作台生成的视图产物，可重新生成）

---

### 2. 空文章或无实质内容的课程

#### 2.1 缺少主页的课程（14 个）

缺少 `主页.md` 的课程：

```
ABB机器人应用编程考证-理论知识题库 2
ABB机器人应用编程考证-理论知识题库
AI工作流控制权迁移
ai时代人的控制权边界--14313cd2
LLM Wiki 方法论
牌一直在你手里
钱势金生
让-learning-skill-跨模型真正好用--846d6f1d
如实所现--12f7c256
如实所现-重学-2026-07-15
如实所现与牌一直在你手里--ce8ccdb8
社会学七书共读
实体行业 AI 落地与 To B 视频素材
四级大冲刺
```

**分析**：
- 部分课程有章节文件（01.md, 02.md 等）但缺少主页
- 部分课程可能是从旧系统迁移时未完全处理
- 需要逐个检查：
  - 有章节内容 → 补充主页
  - 无章节或内容不完整 → 移至待处理

**示例检查结果**：
- `让-learning-skill-跨模型真正好用--846d6f1d/`：有 5 个章节（01-05.md）+ learner-log.md + plan.md → **有实质内容，需补充主页**
- `AI工作流控制权迁移/`：有 8 个章节（01-08.md）+ 复盘.md → **有实质内容，需补充主页**

#### 2.2 重复或版本混乱的课程

| 课程名 | 问题 | 处理建议 |
|---|---|---|
| `ABB机器人应用编程考证-理论知识题库` 和 `ABB机器人应用编程考证-理论知识题库 2` | 疑似重复 | 合并或删除重复版本 |
| `如实所现`、`如实所现--12f7c256`、`如实所现-重学-2026-07-15`、`如实所现-树林的认知体系` | 多个版本 | 明确哪个是最终版本，其他归档 |
| `如实所现与牌一直在你手里--ce8ccdb8` | 疑似复合概念或临时版本 | 检查内容，决定保留或合并 |

#### 2.3 空概念文件

**检查结果**：所有 concepts/*.md 文件都大于 100 字节，**未发现空概念文件**

---

## 三、.trash/ 目录审计

`.trash/2026-09-28_*` 目录已经包含大量历史清理：

```
2026-09-28_02-课程真源/
2026-09-28_03-知识入口与概念/
2026-09-28_AI实战营-从Demo到产品/
2026-09-28_AI实战营-前沿速递/
2026-09-28_articles/
2026-09-28_courses-backups/
2026-09-28_courses-backups-2/
2026-09-28_courses-journals/
2026-09-28_courses-logseq/
2026-09-28_courses-pages/
2026-09-28_graph/
2026-09-28_raw-sources/
2026-09-28_泛化测试-A类-陌生领域/
2026-09-28_泛化测试-B类-低结构化/
2026-09-28_泛化测试-C类-多模态/
2026-09-28_泛化测试-直播稿/
```

**处理建议**：
- 保留 30 天后统一清理
- 这些已经是正确的清理流程

---

## 四、清理优先级与执行计划

### Phase 1：立即清理（Transform 层产物）

**目标**：清理根目录，让用户看到干净的最终成果

1. **创建归档结构**
   ```bash
   mkdir -p .archive/extract
   mkdir -p .archive/transform/reports/2026-09-28
   mkdir -p .archive/transform/snapshots
   mkdir -p .archive/transform/canvas-views
   ```

2. **移动 21 个临时报告**
   ```bash
   # 保留 README.md 和 MIGRATION-PURITY-THEORY.md
   # 移动其余 21 个
   ```

3. **移动 5 个 .tar.gz 压缩包**
   ```bash
   mv *.tar.gz .archive/transform/snapshots/
   ```

4. **移动 16 个学习画布文件**
   ```bash
   find courses/ -name "学习画布.canvas" -exec mv {} .archive/transform/canvas-views/ \;
   ```

### Phase 2：提取层清理（Extract 层原始数据）

**目标**：清理旧目录结构

5. **移动 5 个旧目录**
   ```bash
   mv 01-交互式学习/ .archive/extract/
   mv 02-课程真源/ .archive/extract/
   mv 04-用户原话与费曼/ .archive/extract/
   mv 05-证据原子/ .archive/extract/
   mv 11-研究与验收/ .archive/extract/
   ```

### Phase 3：内容质量审核（Load 层清理）

**目标**：确保最终成果的质量

6. **审核 14 个缺少主页的课程**
   - 逐个检查内容完整性
   - 有内容的补充主页
   - 无内容或不完整的移至 `.archive/extract/incomplete-courses/`

7. **处理重复课程**
   - ABB 题库：合并或删除重复
   - 如实所现系列：明确最终版本

8. **补充 Transform 清洗**
   - 清理简介中的空 WikiLink（之前已发现的问题）

---

## 五、清理后的目录结构（预期）

### 根目录（干净）

```
dacapo-学习仓库/
├── README.md                      ← 项目说明
├── MIGRATION-PURITY-THEORY.md     ← 理论指导文档
├── concepts/                      ← 60 个概念
├── courses/                       ← 课程（清理后）
│   ├── README.md
│   ├── INDEX.md
│   └── [47 个课程目录]
├── user-feedback/                 ← 用户反馈数据
├── scripts/                       ← 工具脚本
└── .archive/                      ← 历史产物（隐藏）
    ├── extract/                   ← 原始提取数据
    │   ├── 01-交互式学习/
    │   ├── 02-课程真源/
    │   ├── 04-用户原话与费曼/
    │   ├── 05-证据原子/
    │   ├── 11-研究与验收/
    │   └── incomplete-courses/    ← 不完整的课程
    └── transform/                 ← 转换过程产物
        ├── reports/2026-09-28/    ← 21 个临时报告
        ├── snapshots/             ← 5 个 .tar.gz
        └── canvas-views/          ← 16 个学习画布
```

### Obsidian 左侧文件列表（预期效果）

用户打开 Obsidian 后只看到：
```
├── concepts/
├── courses/
├── user-feedback/
├── scripts/
├── README.md
└── MIGRATION-PURITY-THEORY.md
```

`.archive/` 目录因为以 `.` 开头，在 Obsidian 中默认隐藏。

---

## 六、风险与待确认事项

### 风险 1：.tar.gz 压缩包可能包含唯一数据源

**需要确认**：
- 5 个压缩包的具体内容是什么？
- 是否是 courses/ 的备份副本？
- 还是包含未迁移的原始数据？

**确认方法**：
```bash
# 列出压缩包内容（不解压）
for f in *.tar.gz; do echo "=== $f ==="; tar -tzf "$f" | head -20; done
```

### 风险 2：旧目录中可能有未迁移内容

**需要确认**：
- `02-课程真源/` 中的 2 个课程是否已完全迁移到 `courses/`？
- `11-研究与验收/Jev打标-历史反馈-2026-09-23/` 中的标注数据是否已入库？

**确认方法**：
- 对比旧目录和新目录的内容
- 确认 user-feedback/ 中是否已包含标注数据

### 风险 3：学习画布可能包含用户的学习笔记

**需要确认**：
- `.canvas` 文件是否只是视图配置？
- 还是包含用户手写的笔记内容？

**确认方法**：
- 打开几个 `.canvas` 文件查看内容
- 如果只是节点位置和连线，可以删除
- 如果包含独立内容，需要提取后再删除

### 风险 4：缺少主页的课程可能是有意设计

**需要确认**：
- 有些课程可能是"片段集合"而非完整课程
- 需要用户判断哪些应该保留、哪些应该清理

---

## 七、执行前的最终确认清单

**请用户确认以下决策**：

1. ✅ **学习画布 (.canvas)**：全部移至 `.archive/` 或删除？
2. ⚠️ **临时报告**：21 个报告移至 `.archive/transform/reports/`？
3. ⚠️ **.tar.gz 压缩包**：需要先检查内容，还是直接归档？
4. ⚠️ **旧目录**：5 个旧目录全部移至 `.archive/extract/`？
5. ⚠️ **缺少主页的课程**：需要逐个审核，还是批量处理？
6. ⚠️ **重复课程（如实所现、ABB）**：需要用户指定保留哪个版本？

---

## 八、理论对照检查

| ETL 原则 | 当前问题 | 解决方案 |
|---|---|---|
| Extract 和 Load 应分离 | 旧目录（Extract）和新目录（Load）混在一起 | 移动旧目录到 `.archive/extract/` |
| Transform 产物应归档 | 21 个报告、5 个压缩包平铺在根目录 | 移动到 `.archive/transform/` |
| Load 层应只包含最终成果 | 学习画布是工作台视图，非核心资产 | 移除或归档 `.canvas` 文件 |
| 最终成果应完整可用 | 14 个课程缺少主页 | 补充主页或移除不完整课程 |

---

**审计完成时间**：2026-09-28  
**下一步**：等待用户确认清理方案，然后执行 Phase 1-3
