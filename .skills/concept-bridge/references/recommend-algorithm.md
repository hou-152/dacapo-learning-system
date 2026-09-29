# 推荐算法详解与调优

## 算法定位

基于已学概念和概念相关度矩阵，生成个性化学习路径推荐。核心目标：推荐「相关度高」且「掌握度低」的概念。

## 输入数据

### 1. 已学概念列表

```javascript
const learnedConcepts = ['对齐', '风格分布压窄'];
```

来源：用户完成的课程章节的 `mainConcepts`

### 2. 概念相关度矩阵

```json
{
  "对齐": {
    "RLHF": 0.8,
    "perplexity": 0.7,
    "强化学习": 0.5
  },
  "风格分布压窄": {
    "困惑度": 0.6
  }
}
```

来源：`scripts/calculate-relevance.js` 的输出

### 3. 概念掌握度

```javascript
const masteryMap = {
  "RLHF": 20,
  "perplexity": 0,
  "强化学习": 80,  // 已掌握，不推荐
  "困惑度": 0
};
```

来源：从概念库的 `mastery` 字段读取

### 4. 课程资源索引

```javascript
const courseIndex = {
  "RLHF": [
    { course: "AI检测原理", chapter: "03.md" },
    { course: "强化学习基础", chapters: ["05.md", "06.md", "07.md"] }
  ],
  "perplexity": [
    { course: "AI检测原理", chapter: "02.md" }
  ]
};
```

来源：扫描 `courses/` 目录的所有 `.concepts.json`

## 核心算法

### 阶段 1：候选概念筛选

```javascript
function getCandidates(learnedConcepts, relevanceMatrix, masteryMap) {
  const candidates = new Set();
  
  for (const learned of learnedConcepts) {
    const related = relevanceMatrix[learned] || {};
    
    for (const [concept, relevance] of Object.entries(related)) {
      // 过滤条件
      if (relevance < 0.5) continue;                    // 相关度过低
      if ((masteryMap[concept] || 0) >= 80) continue;   // 已掌握
      if (learnedConcepts.includes(concept)) continue;  // 已学过
      
      candidates.add(concept);
    }
  }
  
  return Array.from(candidates);
}
```

**过滤规则**：

| 条件 | 阈值 | 原因 |
|------|------|------|
| 相关度 | ≥ 0.5 | 避免推荐不相关的概念 |
| 掌握度 | < 80 | 已掌握的概念无需重复学 |
| 已学 | 排除 | 本次刚学的概念不立即推荐 |

**输出示例**：
```javascript
['RLHF', 'perplexity', '困惑度']
// '强化学习' 被过滤（mastery = 80）
```

### 阶段 2：评分排序

**评分公式**：
```
score = relevance × 0.6 + (1 - mastery/100) × 0.4
```

**权重说明**：
- `relevance × 0.6`：相关度（主要因素）
- `(1 - mastery/100) × 0.4`：掌握度缺口（次要因素）

**实现代码**：

```javascript
function calculateScore(concept, learnedConcepts, relevanceMatrix, masteryMap) {
  // 计算与所有已学概念的最高相关度
  let maxRelevance = 0;
  let bestRelatedConcept = null;
  
  for (const learned of learnedConcepts) {
    const relevance = relevanceMatrix[learned]?.[concept] || 0;
    if (relevance > maxRelevance) {
      maxRelevance = relevance;
      bestRelatedConcept = learned;
    }
  }
  
  // 掌握度缺口（越低越需要学）
  const mastery = masteryMap[concept] || 0;
  const masteryGap = 1 - mastery / 100;
  
  // 综合评分
  const score = maxRelevance * 0.6 + masteryGap * 0.4;
  
  return {
    concept,
    score,
    relevance: maxRelevance,
    relatedTo: bestRelatedConcept,
    mastery
  };
}
```

**评分示例**：

```javascript
// RLHF
relevance = 0.8 (与「对齐」)
mastery = 20
score = 0.8 × 0.6 + (1 - 0.2) × 0.4 = 0.48 + 0.32 = 0.80

// perplexity
relevance = 0.7 (与「对齐」)
mastery = 0
score = 0.7 × 0.6 + (1 - 0) × 0.4 = 0.42 + 0.4 = 0.82

// 排序：perplexity (0.82) > RLHF (0.80)
```

**为什么这样设计**：
- **相关度优先**（60%）：推荐与已学内容强相关的概念（知识连贯性）
- **掌握度补充**（40%）：优先填补知识空白（学习效率）

### 阶段 3：生成 bridge 说明

**bridge 定义**：一句话说明「为什么推荐这个概念」，即从已学概念到推荐概念的桥接路径。

**数据来源**：
1. `.concepts.json` 的 `context` 字段（优先）
2. 概念库的 `relatedConcepts` 字段
3. 关系类型推断

**实现代码**：

```javascript
function generateBridge(recommendedConcept, relatedConcept, conceptsJson, conceptsDir) {
  // 1. 从课程 .concepts.json 提取 context
  for (const [course, data] of Object.entries(coursesData)) {
    for (const [chapter, chapterData] of Object.entries(data.conceptsJson)) {
      const related = chapterData.relatedConcepts[recommendedConcept];
      if (related && related.context) {
        return related.context;
      }
    }
  }
  
  // 2. 从概念库提取关系说明
  const conceptFile = `${conceptsDir}/${relatedConcept}.md`;
  if (fs.existsSync(conceptFile)) {
    const { frontmatter } = parseFrontmatter(fs.readFileSync(conceptFile, 'utf8'));
    const relatedInfo = frontmatter.relatedConcepts?.find(r => r.name === recommendedConcept);
    if (relatedInfo?.description) {
      return relatedInfo.description;
    }
  }
  
  // 3. 根据关系类型生成默认说明
  return inferBridge(recommendedConcept, relatedConcept);
}

function inferBridge(conceptA, conceptB) {
  // 简单的启发式规则
  const patterns = [
    { keywords: ['技术', '方法', '算法'], template: `${conceptB} 的具体实现技术` },
    { keywords: ['理论', '原理', '基础'], template: `${conceptB} 的理论基础` },
    { keywords: ['应用', '场景', '实践'], template: `${conceptB} 的应用场景` },
    { keywords: ['指标', '评估', '检测'], template: `${conceptB} 效果的检测指标` }
  ];
  
  // 根据概念名称匹配模式
  for (const { keywords, template } of patterns) {
    if (keywords.some(kw => conceptA.includes(kw))) {
      return template;
    }
  }
  
  // 兜底
  return `与 ${conceptB} 强相关的概念`;
}
```

**输出示例**：
```javascript
{
  concept: 'RLHF',
  bridge: '你已学习「对齐」，「RLHF」是其核心实现技术'
}
```

### 阶段 4：匹配课程资源

**目标**：找到包含推荐概念的课程和章节。

**实现**：

```javascript
function findCourses(concept, coursesDir) {
  const courses = [];
  
  for (const courseDir of fs.readdirSync(coursesDir)) {
    const conceptsJsonPath = `${coursesDir}/${courseDir}/.concepts.json`;
    if (!fs.existsSync(conceptsJsonPath)) continue;
    
    const conceptsJson = JSON.parse(fs.readFileSync(conceptsJsonPath));
    
    for (const [chapter, data] of Object.entries(conceptsJson)) {
      if (data.mainConcepts.includes(concept)) {
        courses.push({
          course: courseDir,
          chapter,
          status: '未学'  // TODO: 从学习进度判断
        });
      }
    }
  }
  
  return courses;
}
```

**输出示例**：
```javascript
[
  { course: 'AI检测原理', chapter: '03.md', status: '未学' },
  { course: '强化学习基础', chapter: '05.md', status: '未学' }
]
```

### 阶段 5：生成推荐报告

**Markdown 格式**：

```javascript
function generateReport(recommendations) {
  let report = '### 推荐学习路径\n\n';
  
  for (const [index, rec] of recommendations.entries()) {
    report += `#### ${index + 1}. ${rec.concept}（推荐度：${rec.score.toFixed(2)}）\n`;
    report += `- **为什么推荐**：${rec.bridge}\n`;
    report += `- **当前掌握度**：${rec.mastery}%\n`;
    
    if (rec.courses.length > 0) {
      report += `- **相关课程**：\n`;
      for (const course of rec.courses) {
        report += `  - 《${course.course}》第 ${course.chapter.replace('.md', '')} 章（${course.status}）\n`;
      }
    } else {
      report += `- **相关课程**：暂无（建议搜索外部资源）\n`;
    }
    
    report += '\n';
  }
  
  return report;
}
```

**输出示例**：

```markdown
### 推荐学习路径

#### 1. perplexity（推荐度：0.82）
- **为什么推荐**：「对齐」效果的常用检测指标
- **当前掌握度**：0%
- **相关课程**：
  - 《AI 检测原理》第 2 章（未学）

#### 2. RLHF（推荐度：0.80）
- **为什么推荐**：你已学习「对齐」，「RLHF」是其核心实现技术
- **当前掌握度**：20%
- **相关课程**：
  - 《AI 检测原理》第 3 章（未学）
  - 《强化学习基础》第 5-7 章
```

## 完整脚本

```javascript
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function recommend({
  learnedConcepts,
  relevanceFile,
  conceptsDir,
  coursesDir,
  topN = 5
}) {
  // 加载数据
  const relevanceMatrix = JSON.parse(fs.readFileSync(relevanceFile));
  const masteryMap = loadMasteryMap(conceptsDir);
  
  // 1. 候选筛选
  const candidates = getCandidates(learnedConcepts, relevanceMatrix, masteryMap);
  console.log(`📋 候选概念：${candidates.length} 个`);
  
  // 2. 评分排序
  const scored = candidates.map(concept => 
    calculateScore(concept, learnedConcepts, relevanceMatrix, masteryMap)
  ).sort((a, b) => b.score - a.score);
  
  // 3. 取 Top N
  const topRecommendations = scored.slice(0, topN);
  
  // 4. 生成 bridge 说明
  for (const rec of topRecommendations) {
    rec.bridge = generateBridge(rec.concept, rec.relatedTo, coursesDir, conceptsDir);
  }
  
  // 5. 匹配课程资源
  for (const rec of topRecommendations) {
    rec.courses = findCourses(rec.concept, coursesDir);
  }
  
  // 6. 生成报告
  const report = generateReport(topRecommendations);
  console.log(report);
  
  return topRecommendations;
}

function loadMasteryMap(conceptsDir) {
  const masteryMap = {};
  
  for (const file of fs.readdirSync(conceptsDir)) {
    if (!file.endsWith('.md')) continue;
    
    const content = fs.readFileSync(`${conceptsDir}/${file}`, 'utf8');
    const { frontmatter } = parseFrontmatter(content);
    
    masteryMap[frontmatter.name] = frontmatter.mastery || 0;
  }
  
  return masteryMap;
}

// CLI 入口
if (require.main === module) {
  const learned = process.argv[2]?.split(',') || [];
  const relevanceFile = process.argv[3] || '.learning-progress/concept-relevance.json';
  const conceptsDir = process.argv[4] || 'concepts/';
  const coursesDir = process.argv[5] || 'courses/';
  
  if (learned.length === 0) {
    console.error('❌ 用法：node recommend.js "概念1,概念2" [relevance文件] [concepts目录] [courses目录]');
    process.exit(1);
  }
  
  recommend({
    learnedConcepts: learned,
    relevanceFile,
    conceptsDir,
    coursesDir
  });
}

module.exports = { recommend };
```

## 使用方式

### 命令行调用

```bash
# 基础用法
node scripts/recommend.js "对齐,风格分布压窄"

# 指定路径
node scripts/recommend.js \
  "对齐,风格分布压窄" \
  .learning-progress/concept-relevance.json \
  concepts/ \
  courses/
```

### 从 concept-bridge 调用

```javascript
const { recommend } = require('./scripts/recommend.js');

const recommendations = recommend({
  learnedConcepts: ['对齐', '风格分布压窄'],
  relevanceFile: '.learning-progress/concept-relevance.json',
  conceptsDir: 'concepts/',
  coursesDir: 'courses/',
  topN: 5
});
```

### JSON 输出模式

```bash
node scripts/recommend.js "对齐" --json > recommendations.json
```

```json
[
  {
    "concept": "RLHF",
    "score": 0.80,
    "relevance": 0.8,
    "relatedTo": "对齐",
    "mastery": 20,
    "bridge": "你已学习「对齐」，「RLHF」是其核心实现技术",
    "courses": [
      { "course": "AI检测原理", "chapter": "03.md", "status": "未学" }
    ]
  }
]
```

## 调优参数

### 1. 权重调整

```javascript
// 默认：相关度 60%，掌握度 40%
const RELEVANCE_WEIGHT = 0.6;
const MASTERY_WEIGHT = 0.4;

// 情况 1：强调知识连贯性（适合理论学习）
// 相关度 80%，掌握度 20%
const score = relevance * 0.8 + masteryGap * 0.2;

// 情况 2：强调查漏补缺（适合考试复习）
// 相关度 40%，掌握度 60%
const score = relevance * 0.4 + masteryGap * 0.6;
```

**如何选择**：
- 新手学习：相关度权重 ↑（跟随知识链条）
- 复习巩固：掌握度权重 ↑（优先弱项）

### 2. 过滤阈值

```javascript
// 默认
const MIN_RELEVANCE = 0.5;
const MIN_MASTERY_TO_SKIP = 80;

// 情况 1：严格推荐（减少噪音）
const MIN_RELEVANCE = 0.7;  // 只推荐强相关

// 情况 2：宽松推荐（增加发现性）
const MIN_RELEVANCE = 0.4;  // 包含弱相关
```

### 3. 推荐数量

```javascript
// 默认：Top 5
const topN = 5;

// 快速浏览：Top 3
// 深度规划：Top 10
```

### 4. 多样性增强

避免推荐的概念都来自同一领域：

```javascript
function diversifyRecommendations(recommendations, maxPerCategory = 2) {
  const diverse = [];
  const categoryCount = {};
  
  for (const rec of recommendations) {
    const category = getConcept(rec.concept).category;
    
    if ((categoryCount[category] || 0) < maxPerCategory) {
      diverse.push(rec);
      categoryCount[category] = (categoryCount[category] || 0) + 1;
    }
    
    if (diverse.length >= topN) break;
  }
  
  return diverse;
}
```

## 评估指标

### 1. 推荐准确率

用户实际学习的概念是否在推荐列表中：

```javascript
function evaluateAccuracy(recommendations, actualLearned) {
  const recommended = recommendations.map(r => r.concept);
  const hits = actualLearned.filter(c => recommended.includes(c));
  
  return hits.length / actualLearned.length;
}
```

### 2. 推荐覆盖率

有多少候选概念被推荐：

```javascript
const coverage = recommendations.length / candidates.length;
```

### 3. 平均相关度

```javascript
const avgRelevance = recommendations.reduce((sum, r) => sum + r.relevance, 0) / recommendations.length;
```

## 测试用例

### 用例 1：单概念推荐

**输入**：
- learnedConcepts: `['对齐']`
- relevanceMatrix: `{ '对齐': { 'RLHF': 0.8, 'perplexity': 0.7 } }`
- masteryMap: `{ 'RLHF': 0, 'perplexity': 0 }`

**预期输出**：
```javascript
[
  { concept: 'RLHF', score: 0.88, relevance: 0.8, mastery: 0 },
  { concept: 'perplexity', score: 0.82, relevance: 0.7, mastery: 0 }
]
```

### 用例 2：过滤已掌握概念

**输入**：
- masteryMap: `{ 'RLHF': 90 }`（已掌握）

**预期输出**：
- RLHF 不在推荐列表中

### 用例 3：无相关概念

**输入**：
- learnedConcepts: `['孤立概念']`
- relevanceMatrix: `{ '孤立概念': {} }`

**预期输出**：
```javascript
[]  // 空列表
```

## 未来扩展

### 1. 学习路径规划

生成多步学习路径（A → B → C → D）：

```javascript
function planLearningPath(targetConcept, learnedConcepts, relevanceMatrix) {
  // 使用 Dijkstra 算法找最短路径
  const path = findShortestPath(learnedConcepts, targetConcept, relevanceMatrix);
  return path;
}
```

### 2. 个性化推荐

根据学习历史调整权重：

```javascript
function personalizeWeights(learningHistory) {
  const avgLearningSpeed = calculateAvgSpeed(learningHistory);
  
  // 学习快 → 增加相关度权重（探索更广）
  // 学习慢 → 增加掌握度权重（巩固基础）
  return avgLearningSpeed > 0.5 ? { rel: 0.7, mas: 0.3 } : { rel: 0.5, mas: 0.5 };
}
```

### 3. 协同过滤

基于其他学习者的路径推荐：

```javascript
function collaborativeRecommend(userId, allUsersHistory) {
  // 找到相似学习者
  const similarUsers = findSimilarUsers(userId, allUsersHistory);
  
  // 推荐他们学过但我未学的概念
  return getUnlearnedConcepts(userId, similarUsers);
}
```

**当前版本不实现**，保持算法简单且无用户数据依赖。
