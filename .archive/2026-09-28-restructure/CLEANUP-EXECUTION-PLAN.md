# 清理执行方案 - 最终版

基于 ETL 理论和用户决策，现在执行完整清理。

---

## 一、决策确认结果

### 重复课程分析结果

#### 1. 如实所现系列（问题 1-A）

**对比结果**：

| 版本 | 章节结构 | 文件大小对比 | 判断 |
|---|---|---|---|
| `如实所现/` | 00-学习计划 + 01-10 + 后记 + 主页 + learner-log | 各章节较小（5-10K） | ✅ 简化版 |
| `如实所现-树林的认知体系/` | 00-学习计划 + 01-10 + 后记 + 主页 | 各章节较大（8-14K） | ✅ 完整版 |

**关键发现**：
- 两个版本章节结构完全相同（01-10 + 后记）
- `如实所现-树林的认知体系/` 的每个章节都比 `如实所现/` 大 20-100%
- `如实所现/` 有 learner-log.md（356 字节，学习日志）
- `如实所现-树林的认知体系/` 更完整（2.4M vs 104K）

**执行决策**：
- ✅ 保留：`如实所现-树林的认知体系/`（完整版）
- ✅ 保留：`如实所现/`（简化版，可能是不同用途）
- ❌ 归档：`如实所现--12f7c256/`、`如实所现-重学-2026-07-15/`、`如实所现与牌一直在你手里--ce8ccdb8/`

#### 2. 牌一直在你手里（问题 2-C）

**检查结果**：
- 有完整的课程章节内容（01｜把眼睛拿回来：建立信息入口检查）
- 不是概念文件，是真实的课程内容
- 只有 1 个章节，可能是单章课程或未完成

**执行决策**：
- ✅ 保留在 courses/ 中
- ✅ 自动生成主页

#### 3. ABB 题库（问题 3-B）

**执行决策**：
- ✅ 保留：`ABB机器人应用编程考证-理论知识题库`（44K）
- ❌ 归档：`ABB机器人应用编程考证-理论知识题库 2`（32K）

---

## 二、完整执行清单

### Phase 1：创建归档结构

```bash
mkdir -p .archive/extract
mkdir -p .archive/transform/reports/2026-09-28
mkdir -p .archive/transform/snapshots
mkdir -p .archive/transform/canvas-views
mkdir -p .archive/extract/duplicate-courses
mkdir -p .archive/extract/incomplete-courses
```

### Phase 2：Transform 层清理（根目录）

#### 2.1 临时报告（21 个）

移至 `.archive/transform/reports/2026-09-28/`：

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
MVP-FINAL-REPORT.md
RELEASE-v2.0.0.md
SOLUTION-IMPLEMENTATION-PROGRESS.md
SOLUTION-RESEARCH.md
UNIFIED-MANAGEMENT-REPORT.md
WIKILINK-FIX-REPORT.md
purpose.md
落地案例描述-简化版.md
落地案例描述.md
```

**保留在根目录**：
- `README.md`
- `MIGRATION-PURITY-THEORY.md`
- `CLEANUP-AUDIT-FULL.md`
- `DUPLICATE-COURSES-ANALYSIS.md`

#### 2.2 压缩包（5 个）

移至 `.archive/transform/snapshots/`：

```
dacapo-interactive-learning-final.tar.gz
dacapo-skills-complete.tar.gz
dacapo-v2.0.0-docs.tar.gz
dacapo-v2.0.0-intelligent-routing.tar.gz
interactive-learning-skills.tar.gz
```

#### 2.3 学习画布（16 个）

移至 `.archive/transform/canvas-views/`：

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

### Phase 3：Extract 层清理（旧目录）

移至 `.archive/extract/`：

```
01-交互式学习/
02-课程真源/
04-用户原话与费曼/
05-证据原子/
11-研究与验收/
```

### Phase 4：Load 层清理（课程内容）

#### 4.1 重复课程归档

移至 `.archive/extract/duplicate-courses/`：

```
courses/如实所现--12f7c256/
courses/如实所现-重学-2026-07-15/
courses/如实所现与牌一直在你手里--ce8ccdb8/
courses/ABB机器人应用编程考证-理论知识题库 2/
```

#### 4.2 生成主页（11 个课程）

为以下缺少主页的课程自动生成：

```
社会学七书共读（9 章节）
AI工作流控制权迁移（8 章节）
钱势金生（8 章节）
LLM Wiki 方法论（7 章节）
ai时代人的控制权边界--14313cd2（5 章节）
让-learning-skill-跨模型真正好用--846d6f1d（5 章节）
实体行业 AI 落地与 To B 视频素材（3 章节）
四级大冲刺（3 章节）
ABB机器人应用编程考证-理论知识题库（2 章节）
牌一直在你手里（1 章节）
```

**主页生成规则**：
- 从课程目录名提取标题
- 从第一章节（01.md）提取简介（前 3 段）
- 列出所有章节链接

### Phase 5：Git worktrees 清理

```
.claude/worktrees/solution-contradiction-1/
.claude/worktrees/solution-contradiction-2/
.claude/worktrees/solution-contradiction-3/
```

先检查未提交的工作，然后用 `git worktree remove` 清理。

---

## 三、清理后的预期结构

### 根目录（干净）

```
dacapo-学习仓库/
├── README.md
├── MIGRATION-PURITY-THEORY.md
├── CLEANUP-AUDIT-FULL.md
├── DUPLICATE-COURSES-ANALYSIS.md
├── concepts/（60 个）
├── courses/（43 个，清理后）
├── user-feedback/
├── scripts/
└── .archive/（隐藏）
```

### Obsidian 视图（干净）

```
├── concepts/
├── courses/
├── user-feedback/
├── scripts/
├── README.md
├── MIGRATION-PURITY-THEORY.md
└── [其他当前工作文档]
```

---

## 四、执行统计

| 类型 | 数量 | 目标位置 |
|---|---|---|
| 临时报告 | 21 | `.archive/transform/reports/` |
| 压缩包 | 5 | `.archive/transform/snapshots/` |
| 学习画布 | 16 | `.archive/transform/canvas-views/` |
| 旧目录 | 5 | `.archive/extract/` |
| 重复课程 | 4 | `.archive/extract/duplicate-courses/` |
| 需生成主页 | 11 | 当前位置（生成主页） |
| Git worktrees | 3 | 检查后清理 |

**总计**：移动/归档 54 项，生成 11 个主页

---

## 五、风险与回滚

### 安全措施

1. 所有移动操作使用 `mv` 而非 `rm`
2. `.archive/` 目录保留至少 30 天
3. 执行前自动创建 git commit

### 回滚方法

如果清理后发现问题：

```bash
# 从 .archive/ 恢复文件
mv .archive/extract/[目录名] ./
mv .archive/transform/reports/2026-09-28/[文件名] ./

# 或回滚 git commit
git log  # 找到清理前的 commit
git reset --hard [commit-hash]
```

---

## 六、执行确认

**准备执行以下操作**：

1. ✅ 创建 `.archive/` 归档结构
2. ✅ 移动 21 个临时报告
3. ✅ 移动 5 个压缩包
4. ✅ 移动 16 个学习画布文件
5. ✅ 移动 5 个旧目录
6. ✅ 移动 4 个重复课程
7. ✅ 为 11 个课程生成主页
8. ✅ 检查并清理 3 个 git worktrees
9. ✅ 创建 git commit 记录清理操作

**预计用时**：3-5 分钟

**确认执行？**（输入 OK 开始）
