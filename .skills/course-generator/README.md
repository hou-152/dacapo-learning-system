# course-generator

从深度文章或概念名生成结构化课程目录。

## 功能说明

将长文章或概念拆分成系统化的学习课程，包括：
- 提取核心概念并规划章节安排
- 生成完整课程框架（主页、章节文件、学习计划）
- 为每个章节标注关联概念（`.concepts.json`）
- 自动更新课程索引

## 使用场景

- 把深度文章变成结构化课程
- 围绕某个概念设计学习路径
- 生成课程大纲和章节框架
- 为已有内容创建学习导航

## 输入输出格式

### 输入方式 1：基于文章

```bash
/course-generator /path/to/article.md
```

要求：清洗稿或完整转写稿（≥ 3,000 字），有明确知识结构。

### 输入方式 2：基于概念

```bash
/course-generator --concept "概念名"
```

要求：概念已存在于概念库，且有足够关联概念可展开（≥ 5 个）。

### 输出结构

生成目录位于：`courses/<课程名>/`

```
<课程名>/
├── 主页.md                  # 课程入口与导航
├── 00-学习计划.md            # 预期收获、前置知识、学习路径
├── 01.md                    # 第 1 章
├── 02.md                    # 第 2 章
├── ...
├── .concepts.json           # 章节概念关联元数据
└── assets/                  # 图片资源（如需要）
```

### `.concepts.json` 格式示例

```json
{
  "01.md": {
    "mainConcepts": ["对齐", "风格分布压窄"],
    "relatedConcepts": {
      "perplexity": { "relevance": 0.7, "context": "下一章引入的检测指标" },
      "RLHF": { "relevance": 0.6, "context": "对齐的具体技术" }
    }
  },
  "02.md": {
    "mainConcepts": ["RLHF"],
    "relatedConcepts": {
      "对齐": { "relevance": 0.7, "context": "上一章讲解的理论基础" }
    }
  }
}
```

## 章节拆分原则

- 每章聚焦 1-2 个核心概念
- 单章字数 1,500-3,000 字
- 保留完整论证链条
- 章节间有明确递进关系

**章节数量参考**：
- 短文（3,000-8,000 字）：3-5 章
- 中篇（8,000-15,000 字）：6-8 章
- 长文（> 15,000 字）：8-12 章

## 与其他 Skill 的关系

- **依赖 `/concept-learning`**：从文章提取核心概念
- **为 `/concept-bridge` 提供数据**：生成的 `.concepts.json` 用于更新概念掌握度
- **为 `/dbs-learning` 提供框架**：生成的课程可作为交互式学习的起点

## 参考文档

详细执行规范见 `SKILL.md`，包括：
- `references/concepts-json-schema.md` — 概念元数据结构详解
- `references/generate-concepts-json.md` — 自动生成算法
- `references/content-structure-parsing.md` — 内容结构解析原则
