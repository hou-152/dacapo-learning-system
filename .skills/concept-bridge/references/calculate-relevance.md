# 概念相关度计算脚本实现

## 脚本定位

`scripts/calculate-relevance.js` 负责构建全局概念相关度矩阵，供推荐算法使用。

**输入**：概念库目录（`concepts/`）+ 课程目录（`courses/`）  
**输出**：`.learning-progress/concept-relevance.json`

## 数据来源

### 1. 概念库的 relatedConcepts 字段

```markdown
<!-- concepts/对齐.md -->
---
name: 对齐
relatedConcepts:
  - name: RLHF
    relevance: 0.8
  - name: 风格分布压窄
    relevance: 0.6
---
```

### 2. 课程的 .concepts.json

```json
{
  "01.md": {
    "mainConcepts": ["对齐", "风格分布压窄"],
    "relatedConcepts": {
      "perplexity": { "relevance": 0.7 },
      "RLHF": { "relevance": 0.6 }
    }
  }
}
```

### 3. concept-learning 的架构图

```json
{
  "layers": {
    "基础层": ["对齐", "RLHF"],
    "机制层": ["风格分布压窄", "perplexity"]
  },
  "relationships": [
    { "from": "对齐", "to": "RLHF", "type": "实现" },
    { "from": "对齐", "to": "风格分布压窄", "type": "副作用" }
  ]
}
```

## 核心算法

### 阶段 1：收集直接关系

```javascript
const directRelations = new Map();

// 1. 从概念库读取
for (const conceptFile of fs.readdirSync('concepts/')) {
  const { frontmatter } = parseFrontmatter(
    fs.readFileSync(`concepts/${conceptFile}`, 'utf8')
  );
  
  const conceptName = frontmatter.name;
  directRelations.set(conceptName, new Map());
  
  for (const related of frontmatter.relatedConcepts || []) {
    directRelations.get(conceptName).set(related.name, related.relevance);
  }
}

// 2. 从课程 .concepts.json 补充
for (const courseDir of fs.readdirSync('courses/')) {
  const conceptsJsonPath = `courses/${courseDir}/.concepts.json`;
  if (!fs.existsSync(conceptsJsonPath)) continue;
  
  const conceptsJson = JSON.parse(fs.readFileSync(conceptsJsonPath));
  
  for (const [chapter, data] of Object.entries(conceptsJson)) {
    for (const mainConcept of data.mainConcepts) {
      if (!directRelations.has(mainConcept)) {
        directRelations.set(mainConcept, new Map());
      }
      
      for (const [related, { relevance }] of Object.entries(data.relatedConcepts)) {
        // 取最大值（多个来源可能有不同相关度）
        const existing = directRelations.get(mainConcept).get(related) || 0;
        directRelations.get(mainConcept).set(related, Math.max(existing, relevance));
      }
    }
  }
}
```

**输出示例**：
```javascript
Map {
  '对齐' => Map {
    'RLHF' => 0.8,
    '风格分布压窄' => 0.6,
    'perplexity' => 0.7
  },
  'RLHF' => Map {
    '强化学习' => 0.9,
    '对齐' => 0.8
  }
}
```

### 阶段 2：对称化处理

概念关系应该是对称的（A 相关 B ⇒ B 相关 A）。

```javascript
function symmetrize(relations) {
  const symmetricRelations = new Map();
  
  // 初始化
  for (const [concept, _] of relations) {
    symmetricRelations.set(concept, new Map());
  }
  
  // 填充对称关系
  for (const [conceptA, relatedMap] of relations) {
    for (const [conceptB, relevance] of relatedMap) {
      // A → B
      const existing1 = symmetricRelations.get(conceptA)?.get(conceptB) || 0;
      symmetricRelations.get(conceptA).set(conceptB, Math.max(existing1, relevance));
      
      // B → A（对称）
      if (!symmetricRelations.has(conceptB)) {
        symmetricRelations.set(conceptB, new Map());
      }
      const existing2 = symmetricRelations.get(conceptB).get(conceptA) || 0;
      symmetricRelations.get(conceptB).set(conceptA, Math.max(existing2, relevance));
    }
  }
  
  return symmetricRelations;
}
```

**效果**：
```javascript
// 原始数据：只有 对齐 → RLHF (0.8)
// 对称化后：对齐 → RLHF (0.8) 且 RLHF → 对齐 (0.8)
```

### 阶段 3：计算传递相关度

通过中间概念传递相关性（A → B → C）。

**传递公式**：
```
relevance(A, C) = max(
  direct_relevance(A, C),
  max_over_B(relevance(A, B) × relevance(B, C) × decay_factor)
)
```

**衰减系数**：`decay_factor = 0.7`（避免传递链过长导致噪音）

**实现**：

```javascript
function calculateTransitiveRelevance(relations, maxHops = 2) {
  const transitiveRelations = new Map();
  
  // 复制直接关系
  for (const [concept, related] of relations) {
    transitiveRelations.set(concept, new Map(related));
  }
  
  // 多跳传递
  for (let hop = 1; hop <= maxHops; hop++) {
    const decayFactor = Math.pow(0.7, hop);
    
    for (const [conceptA, relatedA] of relations) {
      for (const [conceptB, relevanceAB] of relatedA) {
        // conceptB 的相关概念
        const relatedB = relations.get(conceptB) || new Map();
        
        for (const [conceptC, relevanceBC] of relatedB) {
          if (conceptC === conceptA) continue;  // 跳过自环
          
          // 传递相关度
          const transitiveRelevance = relevanceAB * relevanceBC * decayFactor;
          
          // 取最大值
          const existing = transitiveRelations.get(conceptA).get(conceptC) || 0;
          if (transitiveRelevance > existing && transitiveRelevance >= 0.5) {
            transitiveRelations.get(conceptA).set(conceptC, transitiveRelevance);
          }
        }
      }
    }
  }
  
  return transitiveRelations;
}
```

**示例**：
```javascript
// 直接关系：
// 对齐 → RLHF (0.8)
// RLHF → 强化学习 (0.9)

// 传递关系（1 跳）：
// 对齐 → 强化学习 = 0.8 × 0.9 × 0.7 = 0.504

// 最终矩阵：
// 对齐 → RLHF (0.8, 直接)
// 对齐 → 强化学习 (0.504, 传递)
```

**为什么需要传递**：
- 帮助发现隐含关系（A 和 C 没有直接标注，但通过 B 强相关）
- 增强推荐覆盖度（学完 A 后，可推荐 C）

**风险控制**：
- `maxHops = 2`：最多 2 跳（避免关系链过长）
- `relevance >= 0.5`：过滤弱传递关系（避免噪音）

### 阶段 4：输出 JSON

```javascript
function exportToJson(relations, outputPath) {
  const json = {};
  
  for (const [concept, related] of relations) {
    json[concept] = {};
    
    // 按相关度降序排列
    const sortedRelated = Array.from(related.entries())
      .sort((a, b) => b[1] - a[1]);
    
    for (const [relatedConcept, relevance] of sortedRelated) {
      json[concept][relatedConcept] = parseFloat(relevance.toFixed(2));
    }
  }
  
  fs.writeFileSync(outputPath, JSON.stringify(json, null, 2));
  console.log(`✅ 相关度矩阵已保存至 ${outputPath}`);
}
```

**输出格式**：
```json
{
  "对齐": {
    "RLHF": 0.8,
    "perplexity": 0.7,
    "风格分布压窄": 0.6,
    "强化学习": 0.5
  },
  "RLHF": {
    "强化学习": 0.9,
    "对齐": 0.8
  }
}
```

## 完整脚本

```javascript
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// 工具函数：解析 frontmatter
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]+?)\n---/);
  if (!match) return { frontmatter: {}, body: content };
  
  const yaml = match[1];
  const frontmatter = {};
  
  // 简单的 YAML 解析（生产环境应使用 js-yaml）
  const lines = yaml.split('\n');
  let currentKey = null;
  
  for (const line of lines) {
    if (line.startsWith('  - ')) {
      // 数组项
      if (currentKey === 'relatedConcepts') {
        const nameMatch = line.match(/name:\s*(.+)/);
        const relevanceMatch = line.match(/relevance:\s*(.+)/);
        if (nameMatch) {
          frontmatter.relatedConcepts = frontmatter.relatedConcepts || [];
          frontmatter.relatedConcepts.push({ name: nameMatch[1] });
        } else if (relevanceMatch && frontmatter.relatedConcepts.length > 0) {
          const last = frontmatter.relatedConcepts[frontmatter.relatedConcepts.length - 1];
          last.relevance = parseFloat(relevanceMatch[1]);
        }
      }
    } else {
      const [key, value] = line.split(':').map(s => s.trim());
      if (key && value) {
        frontmatter[key] = value;
        currentKey = key;
      }
    }
  }
  
  return { frontmatter, body: content.slice(match[0].length) };
}

// 主函数
function calculateRelevance(conceptsDir, coursesDir, outputPath) {
  console.log('📊 开始计算概念相关度...');
  
  // 阶段 1：收集直接关系
  const relations = collectDirectRelations(conceptsDir, coursesDir);
  console.log(`✅ 收集到 ${relations.size} 个概念的直接关系`);
  
  // 阶段 2：对称化
  const symmetric = symmetrize(relations);
  console.log(`✅ 完成对称化处理`);
  
  // 阶段 3：传递相关度
  const transitive = calculateTransitiveRelevance(symmetric, 2);
  console.log(`✅ 完成传递相关度计算`);
  
  // 阶段 4：输出
  exportToJson(transitive, outputPath);
}

// CLI 入口
if (require.main === module) {
  const conceptsDir = process.argv[2] || 'concepts/';
  const coursesDir = process.argv[3] || 'courses/';
  const outputPath = process.argv[4] || '.learning-progress/concept-relevance.json';
  
  // 创建输出目录
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  
  calculateRelevance(conceptsDir, coursesDir, outputPath);
}

module.exports = { calculateRelevance };
```

## 使用方式

### 命令行调用

```bash
# 使用默认路径
node scripts/calculate-relevance.js

# 指定路径
node scripts/calculate-relevance.js \
  /path/to/concepts \
  /path/to/courses \
  /path/to/output.json
```

### 从 concept-bridge 调用

```javascript
const { calculateRelevance } = require('./scripts/calculate-relevance.js');

calculateRelevance('concepts/', 'courses/', '.learning-progress/concept-relevance.json');
```

### 输出示例

```
📊 开始计算概念相关度...
✅ 收集到 47 个概念的直接关系
✅ 完成对称化处理
✅ 完成传递相关度计算
✅ 相关度矩阵已保存至 .learning-progress/concept-relevance.json
```

## 性能优化

### 1. 增量更新

仅重新计算变更概念的相关度：

```javascript
function incrementalUpdate(existingRelevance, changedConcepts) {
  // 只重算受影响的概念
  const affected = new Set(changedConcepts);
  
  for (const concept of changedConcepts) {
    // 添加直接相关的概念
    for (const related of existingRelevance[concept] || {}) {
      affected.add(related);
    }
  }
  
  // 只重算 affected 集合
  // ...
}
```

### 2. 缓存结果

```javascript
// 生成指纹
function calculateFingerprint(conceptsDir, coursesDir) {
  const conceptsHash = hashDirectory(conceptsDir);
  const coursesHash = hashDirectory(coursesDir);
  return `${conceptsHash}-${coursesHash}`;
}

// 检查缓存
const fingerprint = calculateFingerprint('concepts/', 'courses/');
const cachePath = `.learning-progress/relevance-cache-${fingerprint}.json`;

if (fs.existsSync(cachePath)) {
  console.log('✅ 使用缓存的相关度矩阵');
  return JSON.parse(fs.readFileSync(cachePath));
}
```

### 3. 并行处理

```javascript
// 使用 worker_threads 并行计算
const { Worker } = require('worker_threads');

function parallelCalculate(concepts, workers = 4) {
  const chunks = chunkArray(concepts, Math.ceil(concepts.length / workers));
  
  const promises = chunks.map(chunk => 
    new Promise((resolve, reject) => {
      const worker = new Worker('./worker.js', { workerData: chunk });
      worker.on('message', resolve);
      worker.on('error', reject);
    })
  );
  
  return Promise.all(promises);
}
```

**适用场景**：概念数 > 100 时启用

## 测试用例

### 用例 1：直接关系

**输入**：
```javascript
relations = Map {
  'A' => Map { 'B' => 0.8 }
}
```

**预期输出**：
```json
{
  "A": { "B": 0.8 },
  "B": { "A": 0.8 }
}
```

### 用例 2：传递关系

**输入**：
```javascript
relations = Map {
  'A' => Map { 'B' => 0.8 },
  'B' => Map { 'C' => 0.9 }
}
```

**预期输出**：
```json
{
  "A": { "B": 0.8, "C": 0.50 },
  "B": { "A": 0.8, "C": 0.9 },
  "C": { "B": 0.9, "A": 0.50 }
}
```

### 用例 3：过滤弱关系

**输入**：
```javascript
relations = Map {
  'A' => Map { 'B' => 0.4 },  // < 0.5
  'B' => Map { 'C' => 0.6 }
}
```

**预期输出**：
```json
{
  "A": {},
  "B": { "C": 0.6 },
  "C": { "B": 0.6 }
}
```

## 依赖库

```json
{
  "dependencies": {
    "js-yaml": "^4.1.0"
  }
}
```

安装：
```bash
cd /Users/housibo/Documents/dacapo-学习仓库
npm install js-yaml
```

## 集成到 CI/CD

```bash
# 在课程或概念更新后自动运行
git add concepts/ courses/
git commit -m "更新概念库"

# post-commit hook
node scripts/calculate-relevance.js
git add .learning-progress/concept-relevance.json
git commit --amend --no-edit
```

## 未来扩展

### 1. 基于共现的相关度

统计概念在同一文档中出现的频率：

```javascript
function calculateCoOccurrence(documents) {
  const coOccurrence = new Map();
  
  for (const doc of documents) {
    const concepts = extractConcepts(doc);
    
    for (let i = 0; i < concepts.length; i++) {
      for (let j = i + 1; j < concepts.length; j++) {
        const pair = [concepts[i], concepts[j]].sort().join('-');
        coOccurrence.set(pair, (coOccurrence.get(pair) || 0) + 1);
      }
    }
  }
  
  // 归一化为 0-1
  const maxCount = Math.max(...coOccurrence.values());
  for (const [pair, count] of coOccurrence) {
    coOccurrence.set(pair, count / maxCount);
  }
  
  return coOccurrence;
}
```

### 2. 基于嵌入的相关度

使用语义向量计算相似度：

```javascript
async function calculateEmbeddingRelevance(concepts) {
  const embeddings = await getEmbeddings(concepts.map(c => c.definition));
  
  const relevance = {};
  for (let i = 0; i < concepts.length; i++) {
    for (let j = i + 1; j < concepts.length; j++) {
      const similarity = cosineSimilarity(embeddings[i], embeddings[j]);
      if (similarity > 0.5) {
        relevance[`${concepts[i]}-${concepts[j]}`] = similarity;
      }
    }
  }
  
  return relevance;
}
```

**当前版本不实现**，保持脚本简单且无外部 API 依赖。
