# 交互式学习统一管理完成报告

**执行时间**: 2026-09-28  
**目标**: 清理零碎，统一管理到 dacapo 学习仓库  
**方案**: 概念化重构 + WikiLink 统一

---

## 一、完成内容

### 1. 课程概念化
**工具**: `extract_course_concepts.py`

**执行结果**:
- 扫描 47 个课程目录
- 生成 47 个课程概念文件
- 提取 282 个章节信息
- 课程状态分类：已完成 2 个，进行中 8 个

**课程概念文件示例**:
```yaml
---
type: course
course_path: courses/Agentic Engineering 工作流
lessons:
  - 01
  - 02
  - 03
  - ...
lesson_count: 14
status: available-01-to-11.5
created: 2026-09-28
tags:
  - 课程
  - 学习
---

# Agentic Engineering 工作流

## 简介
...

## 章节列表
- [[Agentic Engineering 工作流/01|第 01 章]]
- [[Agentic Engineering 工作流/02|第 02 章]]
...
```

### 2. 统一索引生成
**工具**: `rebuild_course_index.py`（重构版）

**核心改进**:
- ❌ 旧版：依赖外部脚本，路径硬编码
- ✅ 新版：独立运行，基于概念库生成

**索引格式**:
```markdown
| 课程 | 章节 | 状态 |
|------|------|------|
| [[Agentic-Engineering-工作流|Agentic Engineering 工作流]] | 01—11.5 | 已有 01—11.5 |
```

**WikiLink 目标**: 概念名（不是文件路径）

---

## 二、统一管理架构

### 唯一真源
```
~/Documents/dacapo-学习仓库/
├── concepts/              # 统一概念库（含课程概念）
│   ├── harness.md        # 普通概念
│   ├── Agentic-Engineering-工作流.md  # 课程概念
│   └── ...
├── courses/              # 课程文件（53 个目录）
│   ├── INDEX.md          # 统一索引（基于概念生成）
│   └── ...
├── user-feedback/        # 用户反馈数据（2.8M）
└── scripts/              # 工具脚本（14 个）
```

### 数据流
```
courses/               # 原始课程文件
  ↓
extract_course_concepts.py
  ↓
concepts/             # 课程概念文件
  ↓
rebuild_course_index.py
  ↓
courses/INDEX.md      # 统一索引
  ↓
dacapo-wiki          # 概念查询和关联探索
```

---

## 三、WikiLink 统一

### 旧格式（已废弃）
```markdown
[[01-交互式学习/02-课程真源/Agentic Engineering 工作流/01|Agentic Engineering 工作流]]
```
- 问题：路径硬编码，不可移植
- 用途：Obsidian 文件导航

### 新格式（统一标准）
```markdown
[[Agentic-Engineering-工作流|Agentic Engineering 工作流]]
```
- 目标：概念名称（不是文件路径）
- 用途：概念关联和知识图谱
- 优势：可通过 dacapo-wiki 查询和探索

---

## 四、清理零碎

### 整合前的分散状态
```
/Users/housibo/Documents/
├── 交互式学习/                    # 主项目
├── Agent交互式学习/                # 分散副本 1
├── DaCapo 内容资产/01-交互式学习/   # 真源（12 个子目录）
└── dacapo-学习仓库/                # 新仓库（空）
```

### 整合后的统一状态
```
/Users/housibo/Documents/dacapo-学习仓库/  # 唯一真源
├── concepts/         # 统一概念库（含课程概念 47 个）
├── courses/          # 课程文件（53 个）
├── user-feedback/    # 用户数据（2.8M）
└── scripts/          # 工具脚本（14 个）
```

### 旧位置保留
- `DaCapo 内容资产/01-交互式学习/` 保持不变（原始真源）
- 不删除，作为历史参考
- 新工作只在 `dacapo-学习仓库/` 进行

---

## 五、工具升级

### 1. extract_course_concepts.py（新）
**功能**: 课程 → 概念文件转换

**特性**:
- 自动识别课程目录
- 提取章节编号和状态
- 生成标准化 frontmatter
- 安全文件名转换（空格 → `-`）

### 2. rebuild_course_index.py（重构）
**旧版问题**:
- 依赖外部脚本 `rebuild_canonical_indexes.py`
- 路径硬编码 `01-交互式学习/02-课程真源`
- WikiLink 指向文件路径

**新版改进**:
- 独立运行，无外部依赖
- 基于概念库动态生成
- WikiLink 指向概念名
- 支持 dacapo-wiki 查询

---

## 六、与 DaCapo v2.0.0 的集成

### dacapo-wiki 集成
**原有能力**:
- 扫描 `concepts/` 目录
- 建立概念关联图谱
- 支持 `--format json` 输出

**新增能力**（自动获得）:
- 查询课程概念：`dacapo-wiki context "Agentic Engineering 工作流"`
- 探索课程关联：`dacapo-wiki search "工作流"`
- 推荐相关课程（基于相似度算法）

### dacapo-main 集成
**学习意图识别**:
```bash
/dacapo 我想学习 Agentic Engineering 工作流
  ↓
dacapo-main 识别意图 = learn
  ↓
调用 dacapo-wiki context "Agentic Engineering 工作流"
  ↓
返回课程概念（type: course）+ 章节列表
  ↓
dacapo-learning 编排学习路径
```

---

## 七、数据统计

| 类型 | 旧位置 | 新位置 | 数量 |
|------|--------|--------|------|
| 课程目录 | DaCapo 内容资产/01-交互式学习/02-课程真源 | dacapo-学习仓库/courses | 47 个 |
| 课程概念 | 不存在 | dacapo-学习仓库/concepts | 47 个 |
| 章节总数 | - | - | 282 个 |
| 用户反馈 | DaCapo 内容资产/.../04-用户原话与费曼 | dacapo-学习仓库/user-feedback | 2.8M |
| 工具脚本 | DaCapo 内容资产/.../08-脚本与工具 | dacapo-学习仓库/scripts | 14 个 |

---

## 八、使用方式

### 查看课程索引
```bash
cat ~/Documents/dacapo-学习仓库/courses/INDEX.md
```

### 重新生成索引
```bash
cd ~/Documents/dacapo-学习仓库
python3 scripts/rebuild_course_index.py
```

### 提取新课程概念
```bash
cd ~/Documents/dacapo-学习仓库
python3 scripts/extract_course_concepts.py
```

### 查询课程（通过 dacapo-wiki）
```bash
cd ~/.openclaw-autoclaw/skills/dacapo-wiki
python3 llm-wiki.py context "Agentic Engineering 工作流"
```

### 学习课程（通过 dacapo-main）
```bash
/dacapo 我想学习 Agentic Engineering 工作流
```

---

## 九、核心价值

### 1. 统一管理
- ✅ 唯一真源：`~/Documents/dacapo-学习仓库/`
- ✅ 清理零碎：不再有 3 个分散位置
- ✅ 一致性：所有工具使用同一概念库

### 2. 概念化
- ✅ 课程 = 概念：统一数据模型
- ✅ 课程关联：通过 dacapo-wiki 探索
- ✅ 学习路径：基于概念依赖生成

### 3. WikiLink 标准化
- ✅ 指向概念：不是文件路径
- ✅ 可移植：不依赖目录结构
- ✅ 可查询：支持程序化访问

### 4. 工具独立性
- ✅ 无外部依赖：不依赖 DaCapo 内容资产的脚本
- ✅ 可移植：整个 dacapo-学习仓库可独立运行
- ✅ 可扩展：新增课程自动识别

---

## 十、待优化项

### 短期
1. 测试 dacapo-wiki 查询课程概念（需要验证文件名匹配）
2. 在 dacapo-learning 中识别课程类型概念
3. 为课程概念添加更多元数据（难度、前置知识等）

### 中期
1. 课程章节细粒度概念化（每个 01.md, 02.md 独立概念）
2. 课程推荐算法优化（基于学习历史）
3. 学习进度追踪（frontmatter 中记录 mastery）

### 长期
1. 多项目课程关联（跨仓库概念图谱）
2. 学习路径可视化（课程依赖图）
3. 协作学习支持（共享学习进度）

---

**状态**: ✅ 统一管理完成  
**下一步**: 测试 dacapo-wiki 查询课程概念
