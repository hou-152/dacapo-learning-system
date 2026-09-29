# .concepts.json 数据结构与生成规则

## 数据结构

```json
{
  "01.md": {
    "mainConcepts": ["概念 A"],
    "relatedConcepts": {
      "概念 B": { "relevance": 0.8, "context": "关系说明" }
    }
  },
  "02.md": {
    "mainConcepts": ["概念 C", "概念 D"],
    "relatedConcepts": {
      "概念 E": { "relevance": 0.7, "context": "理论延伸" },
      "概念 F": { "relevance": 0.6, "context": "对比案例" }
    }
  }
}
```

## 字段说明

### 根对象
- **键名**：章节文件名（如 `01.md`、`02.md`）
- **值**：包含 `mainConcepts` 和 `relatedConcepts` 的对象

### mainConcepts
- **类型**：字符串数组
- **内容**：该章节重点讲解的核心概念
- **数量**：1-2 个
- **作用**：标识章节主题，用于生成章节标题和引言

### relatedConcepts
- **类型**：对象
- **键名**：相关概念名称
- **值**：包含 `relevance` 和 `context` 的对象

#### relevance
- **类型**：数字（0-1）
- **含义**：与主概念的关联度
- **筛选条件**：仅收录 relevance > 0.5 的概念

#### context
- **类型**：字符串
- **内容**：一句话说明关系
- **示例**：
  - "都出自费孝通"
  - "理论延伸"
  - "对比案例"
  - "同属人类学范畴"

## 生成规则

1. **mainConcepts 提取**
   - 从概念网络中识别该章节的核心概念
   - 优先选择高频出现且具有代表性的概念
   - 控制在 1-2 个

2. **relatedConcepts 查询**
   - 从概念网络中查询与 mainConcepts 相关的概念
   - 筛选 relevance > 0.5 的概念
   - 按 relevance 降序排列

3. **context 生成**
   - 基于概念网络中的关系类型生成简短说明
   - 使用具体、清晰的表达
   - 避免抽象或模糊的描述

## 使用场景

- **章节引言生成**：基于 mainConcepts 生成"本章将探讨..."
- **相关概念推荐**：在章节末尾展示 relatedConcepts
- **知识图谱可视化**：将 relevance 映射为连线粗细
- **学习路径规划**：根据 relatedConcepts 推荐后续章节
