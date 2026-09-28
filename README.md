# DaCapo 交互式学习仓库

**版本**: v2.0.0  
**更新日期**: 2026-09-28

一个基于 Obsidian + AI Skills 的交互式学习系统，通过概念提取、关系网络和跨项目关联实现「复利式学习」。

---

## 📚 核心特性

### 智能路由系统（v2.0.0 新增）
- **5 种意图自动识别**：学习、查看进度、探索关联、可视化、推荐
- **历史上下文检索**：自动获取已学概念的掌握度和依赖关系
- **统一入口**：一个 `/dacapo` 命令搞定所有学习场景

### 概念复利
- **概念提取**：从学习材料中自动提取关键概念
- **关系网络**：构建概念间的语义关联（依赖、组成、对比、应用）
- **跨项目草蛇灰线**：发现不同课程中的概念关联

### 四个「化」
- **结构化**：每个概念独立文件，frontmatter 记录状态
- **网络化**：局部网络（单课程）+ 全局 Hub（核心概念）
- **可视化**：Obsidian Graph View + Mermaid 图谱
- **资产化**：学习笔记可重用、可追溯、可复利

---

## 🗂️ 目录结构

```
dacapo-学习仓库/
├── concepts/              # 概念库（60+ 概念，每个概念一个文件）
│   ├── harness.md
│   ├── context-engineering.md
│   └── ...
│
├── courses/               # 课程真源（47 个课程，282 个章节）
│   ├── INDEX.md          # 课程机械索引（自动生成，不要手改）
│   ├── README.md         # 课程结构说明
│   └── [课程名]/
│       ├── 00-学习计划.md
│       ├── 01.md, 02.md, ...
│       ├── 结课-立项-*.md
│       ├── assets/       # 选材、疑问、反馈上下文
│       └── 学习画布.canvas
│
├── scripts/               # 工具脚本（Python）
│   ├── backend.py        # 后端核心逻辑
│   ├── extract_course_concepts.py
│   ├── generate_concept_graph.py
│   ├── rebuild_course_index.py
│   ├── build_evidence_atoms.py
│   └── ...
│
├── user-feedback/         # 用户反馈数据（JSONL）
│   ├── user-utterances.jsonl
│   ├── learner-signals.jsonl
│   └── ...
│
├── 04-用户原话与费曼/    # 用户原话归档
├── 05-证据原子/          # 证据归属判定
│
├── .obsidian/            # Obsidian 配置
├── .learning-progress/   # 学习进度追踪
│
└── 文档/
    ├── RELEASE-v2.0.0.md              # 版本发布说明
    ├── MVP-FINAL-REPORT.md            # MVP 完成报告
    ├── CONCEPT-MINING-MVP-REPORT.md   # 概念挖掘报告
    ├── GENERALIZATION-TEST-FINAL-REPORT.md  # 泛化测试报告
    └── ...
```

---

## 🚀 快速开始

### 1. 在 Obsidian 中打开

```bash
open -a Obsidian ~/Documents/dacapo-学习仓库/
```

### 2. 开始学习（推荐方式）

使用统一入口 `/dacapo`（需要安装 Skills）：

```bash
# 学习某个概念
/dacapo 我想深入学习 harness 这个概念

# 查看学习进度
/dacapo 查看我的学习进度

# 探索概念关联
/dacapo 发现与 harness 相关的概念

# 可视化图谱
/dacapo 可视化概念网络
```

### 3. 查询概念（通过 dacapo-wiki）

```bash
# 查询概念上下文
dacapo-wiki context "harness"

# JSON 格式输出（供其他工具调用）
dacapo-wiki context "harness" --format json
```

### 4. 查看课程

打开 `courses/INDEX.md` 查看所有课程列表（47 个课程，282 个章节）。

---

## 🛠️ 脚本工具

### 核心脚本

| 脚本 | 功能 | 用法 |
|------|------|------|
| `backend.py` | 后端核心逻辑（62KB） | `python scripts/backend.py` |
| `extract_course_concepts.py` | 从课程中提取概念 | `python scripts/extract_course_concepts.py [课程目录]` |
| `generate_concept_graph.py` | 生成概念关系图谱 | `python scripts/generate_concept_graph.py` |
| `rebuild_course_index.py` | 重建课程索引（自动生成 INDEX.md） | `python scripts/rebuild_course_index.py` |
| `build_evidence_atoms.py` | 构建证据原子（52KB） | `python scripts/build_evidence_atoms.py` |

### 测试脚本

- `test_backend.py` — 后端单元测试
- `test_provenance.py` — 溯源测试

### 辅助脚本

- `build_attribution_quarantine.py` — 归属隔离区构建
- `build_legacy_response_candidates.py` — 遗留响应候选构建
- `extract_marked_user_responses.py` — 提取标记的用户响应
- `verify_consolidation.py` — 验证整合结果

---

## 📊 数据说明

### 概念库（concepts/）

- 每个概念一个 `.md` 文件
- frontmatter 记录：
  - `mastery`: 掌握度（0.0-1.0）
  - `dependencies`: 前置概念
  - `tags`: 分类标签
  - `created`: 创建时间
  - `updated`: 更新时间

### 用户反馈数据（user-feedback/）

JSONL 格式，记录学习过程：

- `user-utterances.jsonl` — 用户原话（895KB）
- `learner-signals.jsonl` — 学习信号
- `readwise-evidence-revision-history.jsonl` — Readwise 证据修订历史（1.5MB）
- `readwise-provenance-assessments.jsonl` — Readwise 溯源评估（194KB）
- `legacy-response-candidates.jsonl` — 遗留响应候选（96KB）
- `verbatim-source-spans.jsonl` — 逐字来源片段（94KB）

### 课程数据（courses/）

- 47 个课程，282 个章节
- 每个课程独立目录，标准结构：
  - `00-学习计划.md` — 学习目标、材料池、进度
  - `01.md`, `02.md`, ... — 课程正文
  - `结课-立项-*.md` — 结课交付物
  - `assets/` — 选材、疑问、反馈上下文

---

## 📖 深入阅读

### 核心文档

- [RELEASE-v2.0.0.md](./RELEASE-v2.0.0.md) — v2.0.0 智能路由系统发布说明
- [MVP-FINAL-REPORT.md](./MVP-FINAL-REPORT.md) — MVP 完成报告（泛化测试 4.3/5 分）
- [CONCEPT-MINING-MVP-REPORT.md](./CONCEPT-MINING-MVP-REPORT.md) — 概念挖掘方法论
- [GENERALIZATION-TEST-FINAL-REPORT.md](./GENERALIZATION-TEST-FINAL-REPORT.md) — 泛化能力测试

### 研究文档

- [CONCEPT-GRAPH.md](./CONCEPT-GRAPH.md) — 概念图谱设计
- [SOLUTION-RESEARCH.md](./SOLUTION-RESEARCH.md) — 解决方案研究
- [INTEGRATION-REPORT.md](./INTEGRATION-REPORT.md) — 集成报告
- [UNIFIED-MANAGEMENT-REPORT.md](./UNIFIED-MANAGEMENT-REPORT.md) — 统一管理报告

### 项目规划

- [purpose.md](./purpose.md) — 学习目标
- [MIGRATION-PLAN.md](./MIGRATION-PLAN.md) — 迁移计划
- [CLEANUP-PLAN.md](./CLEANUP-PLAN.md) — 清理计划

---

## 🎯 设计理念

### 提示词占 10%，harness 占 90%

不依赖复杂提示词，而是通过：
- Skill 组合
- Obsidian 基建
- Git worktree 并行
- 结构化数据

实现工程化的学习系统。

### 局部网络 + 全局 Hub

- **局部网络**：每篇文章/课程的完整概念关系（丰富语义）
- **全局 Hub**：只显示 inDegree >= 3 的核心概念（避免熵增）

### 可复利的学习资产

- 每次学习留下结构化笔记
- 概念网络自动积累
- 跨项目发现「草蛇灰线」
- 学习效果呈复利增长（测试验证：2.4x 效果提升）

---

## 📦 技术栈

| 层次 | 技术 | 作用 |
|------|------|------|
| **基建层** | Obsidian | Graph View、wikilink、双向链接 |
| **处理层** | Python Scripts | 概念提取、关系识别、图谱生成 |
| **可视化层** | Mermaid | 独立概念网络图 |
| **协作层** | Git worktree | 并行开发、隔离测试 |
| **智能层** | AI Skills | dacapo-main、dacapo-learning、dacapo-wiki |

---

## 🔧 开发者指南

### 添加新课程

1. 在 `courses/` 下创建课程目录
2. 创建 `00-学习计划.md`
3. 开始添加课程正文（`01.md`, `02.md`, ...）
4. 运行 `python scripts/rebuild_course_index.py` 更新索引

### 提取概念

```bash
python scripts/extract_course_concepts.py courses/[课程名]
```

### 生成概念图谱

```bash
python scripts/generate_concept_graph.py
```

### 测试后端

```bash
python scripts/test_backend.py
```

---

## 📈 统计数据

- **概念数量**: 60+
- **课程数量**: 47 个
- **章节数量**: 282 个
- **用户反馈**: ~1MB JSONL 数据
- **脚本工具**: 16 个 Python 脚本
- **文档报告**: 15+ 份研究/报告文档

---

## 🤝 贡献

这是个人学习仓库，暂不接受外部贡献。

如有问题或建议，请通过 Issue 反馈。

---

## 📄 许可证

见 LICENSE 文件

---

**构建者**: DaCapo Team  
**生成时间**: 2026-09-28  
**仓库理念**: 让学习像复利一样增长
