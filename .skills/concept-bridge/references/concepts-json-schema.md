# .concepts.json 数据结构详解

## 文件定位

`.concepts.json` 是课程目录的概念关联元数据，由 `/course-generator` 生成，由 `/concept-bridge` 读取和使用。

**位置**：`courses/<课程名>/.concepts.json`

## 完整结构

```json
{
  "01.md": {
    "mainConcepts": ["对齐", "风格分布压窄"],
    "relatedConcepts": {
      "perplexity": {
        "relevance": 0.7,
        "context": "下一章引入的检测指标"
      },
      "RLHF": {
        "relevance": 0.6,
        "context": "对齐的具体技术"
      }
    }
  },
  "02.md": {
    "mainConcepts": ["perplexity", "困惑度"],
    "relatedConcepts": {
      "对齐": {
        "relevance": 0.8,
        "context": "上一章的核心概念"
      },
      "AI 检测": {
        "relevance": 0.7,
        "context": "困惑度的主要应用场景"
      }
    }
  }
}
```

## 字段说明

### 顶层键名

- **格式**：章节文件名（`01.md`, `02.md`, ...）
- **要求**：必须与实际文件名完全一致（包括扩展名）
- **顺序**：按章节顺序排列（非必需，但推荐）

### mainConcepts（数组）

**定义**：本章节重点讲解的核心概念（1-2 个）

**示例**：
```json
"mainConcepts": ["对齐", "风格分布压窄"]
```

**规则**：
- 数量：1-2 个（不超过 3 个）
- 来源：从章节标题或首段提取
- 命名：使用概念库的标准名称（精确匹配）
- 唯一性：同一概念不应在多个章节都作为 mainConcept（除非是多章深入）

**如何确定**：
1. 优先从章节标题（`## 这一篇要解决的问题`）识别
2. 或统计章节中概念出现频率（≥ 3 次）
3. 或从小结部分提取关键词

### relatedConcepts（对象）

**定义**：与本章节相关的其他概念（非核心但相关）

**示例**：
```json
"relatedConcepts": {
  "perplexity": {
    "relevance": 0.7,
    "context": "下一章引入的检测指标"
  },
  "RLHF": {
    "relevance": 0.6,
    "context": "对齐的具体技术"
  }
}
```

**字段**：
- **键名**：概念名称（精确匹配概念库）
- **relevance**：相关度（0.5-1.0）
- **context**：关系说明（一句话）

### relevance（相关度）

**定义**：概念之间的关联强度（0-1 的浮点数）

**取值范围**：
- `0.9-1.0`：直接依赖（如「RLHF」与「强化学习」）
- `0.7-0.8`：强相关（如「对齐」与「RLHF」）
- `0.5-0.6`：弱相关（如「对齐」与「token 预测」）
- `< 0.5`：不记录（避免噪音）

**来源优先级**：
1. **真实数据**：从 `concept-relevance.json` 读取（最可靠）
2. **架构图**：从 concept-learning 的架构图推断
3. **层级关系**：
   - 同层概念：0.8
   - 相邻层：0.7
   - 跨层：0.5-0.6
4. **人工标注**：生成后手动调整

### context（关系说明）

**定义**：一句话说明为什么这两个概念相关

**格式要求**：
- 长度：10-30 字
- 类型：陈述句（不用问句）
- 内容：具体关系（不用泛泛而谈）

**常见模式**：

1. **时序关系**：
   - `"下一章引入的检测指标"`
   - `"上一章的核心概念"`
   - `"第 5 章深入讲解"`

2. **层级关系**：
   - `"对齐的具体实现技术"`
   - `"风格分布压窄的理论基础"`
   - `"perplexity 的应用场景"`

3. **对比关系**：
   - `"与 RLHF 的对比方法"`
   - `"风格分布压窄的反向指标"`

4. **因果关系**：
   - `"对齐的副作用表现"`
   - `"困惑度升高的原因"`

**反例**（避免）：
- ❌ `"相关概念"`（太模糊）
- ❌ `"很重要"`（无信息量）
- ❌ `"参见文档"`（无具体说明）

## 生成流程

**由 course-generator 生成时**：

1. **提取 mainConcepts**：
   ```javascript
   // 从章节标题提取
   const title = chapter.match(/^##\s+(.+)$/m)[1];
   const mainConcepts = extractConceptsFromText(title);
   
   // 或从概念出现频率提取
   const conceptFreq = countConceptOccurrences(chapter);
   const mainConcepts = conceptFreq.slice(0, 2).map(c => c.name);
   ```

2. **查询 relatedConcepts**：
   ```javascript
   // 从 concept-learning 的架构图
   const relatedFromGraph = getRelatedFromArchitecture(mainConcepts);
   
   // 或从概念库的 relatedConcepts 字段
   const relatedFromDB = concepts[mainConcept].relatedConcepts;
   ```

3. **计算 relevance**：
   ```javascript
   // 优先使用真实相关度数据
   if (conceptRelevance[conceptA][conceptB]) {
     relevance = conceptRelevance[conceptA][conceptB];
   } else {
     // 按层级估算
     relevance = estimateRelevance(conceptA, conceptB, architecture);
   }
   ```

4. **生成 context**：
   ```javascript
   // 判断是否在相邻章节
   if (nextChapter.mainConcepts.includes(concept)) {
     context = `下一章引入的${concept.category}`;
   } else if (prevChapter.mainConcepts.includes(concept)) {
     context = `上一章的核心概念`;
   } else {
     // 根据关系类型
     context = generateContextByRelationType(conceptA, conceptB);
   }
   ```

## 使用场景

### 被 concept-bridge 读取

```javascript
// 读取课程的 .concepts.json
const concepts = JSON.parse(fs.readFileSync('.concepts.json'));

// 提取已完成章节的 mainConcepts
const completedChapters = ['01.md', '02.md'];
const learnedConcepts = completedChapters
  .flatMap(chapter => concepts[chapter].mainConcepts);

// 收集相关概念用于推荐
const relatedForRecommendation = completedChapters
  .flatMap(chapter => Object.keys(concepts[chapter].relatedConcepts));
```

### 被 calculate-relevance.js 使用

```javascript
// 补充全局相关度矩阵
for (const [chapter, data] of Object.entries(concepts)) {
  for (const [related, {relevance}] of Object.entries(data.relatedConcepts)) {
    // 将课程内的相关度合并到全局矩阵
    if (!globalRelevance[mainConcept]?.[related]) {
      globalRelevance[mainConcept][related] = relevance;
    }
  }
}
```

## 验证规则

**必需检查**（由 course-generator 在生成后自动执行）：

1. **文件名一致性**：
   ```javascript
   const actualFiles = fs.readdirSync('.').filter(f => f.match(/^\d+\.md$/));
   const jsonKeys = Object.keys(concepts);
   assert(jsonKeys.every(k => actualFiles.includes(k)));
   ```

2. **概念存在性**：
   ```javascript
   const allConcepts = [...mainConcepts, ...Object.keys(relatedConcepts)];
   for (const concept of allConcepts) {
     assert(fs.existsSync(`concepts/${concept}.md`), `概念 ${concept} 不存在`);
   }
   ```

3. **relevance 范围**：
   ```javascript
   for (const {relevance} of Object.values(relatedConcepts)) {
     assert(relevance >= 0.5 && relevance <= 1.0);
   }
   ```

4. **mainConcepts 唯一性**（警告级）：
   ```javascript
   const mainConceptCount = {};
   for (const {mainConcepts} of Object.values(concepts)) {
     for (const c of mainConcepts) {
       mainConceptCount[c] = (mainConceptCount[c] || 0) + 1;
     }
   }
   for (const [c, count] of Object.entries(mainConceptCount)) {
     if (count > 2) console.warn(`概念 ${c} 在 ${count} 个章节作为 mainConcept`);
   }
   ```

## 手动维护指南

**何时需要手动编辑**：

1. **课程生成后发现概念标注错误**
2. **新增章节后补充元数据**
3. **调整相关度或 context 说明**

**编辑规范**：

1. 保持 JSON 格式正确（使用 Prettier 或 `jq` 格式化）
2. 概念名称必须与概念库文件名一致（区分大小写）
3. relevance 保留 1 位小数（如 `0.7`）
4. context 使用中文，不超过 30 字
5. 编辑后运行验证脚本：
   ```bash
   node scripts/validate-concepts-json.js courses/<课程名>/.concepts.json
   ```

## 版本演进

**当前版本**：v1.0（2026-09-30）

**未来可能扩展**：

1. **章节难度标注**：
   ```json
   "difficulty": "beginner" | "intermediate" | "advanced"
   ```

2. **预计学习时间**：
   ```json
   "estimatedMinutes": 30
   ```

3. **前置章节依赖**：
   ```json
   "prerequisites": ["01.md", "02.md"]
   ```

4. **概念首次出现标记**：
   ```json
   "firstAppearance": true
   ```

**向后兼容承诺**：新增字段可选，旧版本工具可正常运行。
