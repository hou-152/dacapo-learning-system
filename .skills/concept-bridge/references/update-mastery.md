# 概念掌握度更新算法

## 算法定位

基于课程章节完成情况，增量更新概念库中各概念的 `mastery` 字段（掌握度，0-100）。

## 核心原则

1. **增量更新**：每次学习累加，不覆盖
2. **递减增幅**：首次 +30，二次 +20，三次及以上 +10
3. **记录来源**：追加学习历史，可追溯
4. **上限保护**：mastery 不超过 100

## 输入数据

### 1. 已完成章节列表

```javascript
const completedChapters = ['01.md', '02.md', '03.md'];
```

来源：用户通过 `/concept-bridge --chapters 01,02,03` 提供

### 2. 课程 .concepts.json

```json
{
  "01.md": {
    "mainConcepts": ["对齐", "风格分布压窄"]
  },
  "02.md": {
    "mainConcepts": ["perplexity", "困惑度"]
  }
}
```

### 3. 概念库现状

从 `concepts/<概念名>.md` 读取 frontmatter：

```yaml
---
name: 对齐
mastery: 40
lastUpdated: 2026-09-15
learningHistory:
  - date: 2026-09-15
    source: manual-input
    masteryBefore: 0
    masteryAfter: 40
---
```

## 算法流程

### 步骤 1：提取已学概念

```javascript
const learnedConcepts = [];

for (const chapter of completedChapters) {
  const chapterData = conceptsJson[chapter];
  if (!chapterData) {
    console.warn(`⚠️ 章节 ${chapter} 不在 .concepts.json 中`);
    continue;
  }
  
  learnedConcepts.push(...chapterData.mainConcepts);
}

// 去重（同一概念可能在多章出现）
const uniqueConcepts = [...new Set(learnedConcepts)];
```

**输出示例**：
```javascript
['对齐', '风格分布压窄', 'perplexity', '困惑度']
```

### 步骤 2：读取概念现状

```javascript
const conceptStates = {};

for (const concept of uniqueConcepts) {
  const filePath = `concepts/${concept}.md`;
  
  if (!fs.existsSync(filePath)) {
    console.warn(`⚠️ 概念「${concept}」不存在，跳过更新`);
    continue;
  }
  
  const content = fs.readFileSync(filePath, 'utf8');
  const frontmatter = parseFrontmatter(content);
  
  conceptStates[concept] = {
    mastery: frontmatter.mastery || 0,
    learningHistory: frontmatter.learningHistory || [],
    filePath
  };
}
```

**输出示例**：
```javascript
{
  "对齐": {
    mastery: 40,
    learningHistory: [{ date: "2026-09-15", source: "manual-input", ... }],
    filePath: "concepts/对齐.md"
  }
}
```

### 步骤 3：计算增幅

**规则表**：

| 学习次数 | 增幅 | 说明 |
|----------|------|------|
| 第 1 次  | +30  | 首次学习，建立初步理解 |
| 第 2 次  | +20  | 巩固强化 |
| 第 3+ 次 | +10  | 持续复习，增幅递减 |

**实现代码**：

```javascript
function calculateIncrement(learningHistory) {
  const learningCount = learningHistory.length;
  
  if (learningCount === 0) return 30;  // 首次学习
  if (learningCount === 1) return 20;  // 二次巩固
  return 10;                            // 三次及以上
}
```

**边界处理**：

```javascript
function applyIncrement(currentMastery, increment) {
  const newMastery = currentMastery + increment;
  return Math.min(newMastery, 100);  // 上限保护
}
```

### 步骤 4：更新概念文件

```javascript
const updates = [];

for (const [concept, state] of Object.entries(conceptStates)) {
  const increment = calculateIncrement(state.learningHistory);
  const masteryBefore = state.mastery;
  const masteryAfter = applyIncrement(masteryBefore, increment);
  
  // 构造新历史记录
  const newHistoryEntry = {
    date: new Date().toISOString().split('T')[0],  // YYYY-MM-DD
    source: `courses/${courseName}/${chapter}`,
    masteryBefore,
    masteryAfter
  };
  
  // 读取文件内容
  const content = fs.readFileSync(state.filePath, 'utf8');
  const { frontmatter, body } = parseFrontmatter(content);
  
  // 更新 frontmatter
  frontmatter.mastery = masteryAfter;
  frontmatter.lastUpdated = newHistoryEntry.date;
  frontmatter.learningHistory = [
    ...(frontmatter.learningHistory || []),
    newHistoryEntry
  ];
  
  // 写回文件
  const newContent = stringifyFrontmatter(frontmatter, body);
  fs.writeFileSync(state.filePath, newContent);
  
  // 记录更新
  updates.push({
    concept,
    masteryBefore,
    masteryAfter,
    increment,
    source: newHistoryEntry.source
  });
}
```

### 步骤 5：生成更新报告

```javascript
function generateReport(updates) {
  let report = '## 概念掌握度变化\n\n';
  report += '| 概念 | 更新前 | 更新后 | 变化 | 来源章节 |\n';
  report += '|------|--------|--------|------|----------|\n';
  
  for (const update of updates) {
    const change = `+${update.increment}`;
    const source = update.source.split('/').pop();  // 只显示章节文件名
    
    report += `| ${update.concept} | ${update.masteryBefore} | ${update.masteryAfter} | ${change} | ${source} |\n`;
  }
  
  return report;
}
```

**输出示例**：

```markdown
## 概念掌握度变化

| 概念 | 更新前 | 更新后 | 变化 | 来源章节 |
|------|--------|--------|------|----------|
| 对齐 | 40     | 70     | +30  | 01.md    |
| 风格分布压窄 | 0 | 30 | +30  | 01.md    |
| perplexity | 50 | 70 | +20  | 02.md    |
| 困惑度 | 0 | 30 | +30  | 02.md    |
```

## 边界情况处理

### 1. 概念不存在

```javascript
if (!fs.existsSync(`concepts/${concept}.md`)) {
  console.warn(`⚠️ 概念「${concept}」在库中不存在，跳过更新`);
  console.log(`💡 建议：运行 /concept-learning 提取该概念`);
  continue;
}
```

**不做的事**：不自动创建概念文件（应由 `/concept-learning` 负责）

### 2. 掌握度已达上限

```javascript
if (state.mastery >= 100) {
  console.log(`✅ 概念「${concept}」已完全掌握，无需更新`);
  continue;
}
```

**是否记录**：仍追加 learningHistory，但 mastery 保持 100

### 3. 同一概念在多章出现

```javascript
// 只更新一次（按最早出现的章节）
const firstAppearance = completedChapters.find(ch => 
  conceptsJson[ch].mainConcepts.includes(concept)
);

newHistoryEntry.source = `courses/${courseName}/${firstAppearance}`;
```

### 4. 概念文件格式错误

```javascript
try {
  const { frontmatter, body } = parseFrontmatter(content);
} catch (err) {
  console.error(`❌ 概念文件 ${concept}.md 格式错误：${err.message}`);
  console.log(`💡 请手动检查文件结构`);
  continue;
}
```

## 学习历史数据结构

### learningHistory 数组

```yaml
learningHistory:
  - date: 2026-09-15
    source: manual-input
    masteryBefore: 0
    masteryAfter: 40
  - date: 2026-09-30
    source: courses/AI检测原理/01.md
    masteryBefore: 40
    masteryAfter: 70
```

**字段说明**：

- `date`：学习日期（YYYY-MM-DD）
- `source`：学习来源（课程路径 / `manual-input` / `import`）
- `masteryBefore`：更新前掌握度
- `masteryAfter`：更新后掌握度

**用途**：

1. 可追溯学习路径
2. 分析学习效率（某概念学了多次仍不提升 → 标记为难点）
3. 生成学习时间线
4. 支持回退操作（未来功能）

## 性能优化

### 批量读写

```javascript
// ❌ 低效：逐个文件读写
for (const concept of concepts) {
  const content = fs.readFileSync(`concepts/${concept}.md`);
  // ... 处理
  fs.writeFileSync(`concepts/${concept}.md`, newContent);
}

// ✅ 高效：批量读取，批量写入
const readTasks = concepts.map(c => 
  fs.promises.readFile(`concepts/${c}.md`, 'utf8')
);
const contents = await Promise.all(readTasks);

// ... 处理

const writeTasks = contents.map((content, i) => 
  fs.promises.writeFile(`concepts/${concepts[i]}.md`, content)
);
await Promise.all(writeTasks);
```

### 缓存概念库

```javascript
// 首次运行时缓存所有概念文件
const conceptCache = new Map();

function getConcept(name) {
  if (!conceptCache.has(name)) {
    const content = fs.readFileSync(`concepts/${name}.md`, 'utf8');
    conceptCache.set(name, parseFrontmatter(content));
  }
  return conceptCache.get(name);
}
```

**适用场景**：一次性更新 > 10 个概念

## 测试用例

### 用例 1：首次学习

**输入**：
- 概念：`对齐`
- 当前 mastery：0
- learningHistory：`[]`

**预期输出**：
- mastery：30
- learningHistory 新增 1 条

### 用例 2：二次巩固

**输入**：
- 概念：`对齐`
- 当前 mastery：30
- learningHistory：1 条

**预期输出**：
- mastery：50
- learningHistory 新增 1 条

### 用例 3：上限保护

**输入**：
- 概念：`对齐`
- 当前 mastery：95
- learningHistory：5 条

**预期输出**：
- mastery：100（不是 105）
- learningHistory 新增 1 条

### 用例 4：概念不存在

**输入**：
- 概念：`不存在的概念`

**预期输出**：
- 跳过更新
- 输出警告信息

## 集成到 concept-bridge

```javascript
// 在 concept-bridge 中调用
const { updateMastery } = require('./scripts/update-mastery.js');

const updates = await updateMastery({
  completedChapters: ['01.md', '02.md'],
  conceptsJson: require('./courses/AI检测原理/.concepts.json'),
  conceptsDir: 'concepts/',
  courseName: 'AI检测原理'
});

console.log(generateReport(updates));
```

**返回值**：
```javascript
[
  {
    concept: '对齐',
    masteryBefore: 40,
    masteryAfter: 70,
    increment: 30,
    source: 'courses/AI检测原理/01.md'
  },
  // ...
]
```

## 未来扩展

### 1. 自适应增幅

根据学习间隔调整增幅：

```javascript
function calculateAdaptiveIncrement(learningHistory) {
  if (learningHistory.length === 0) return 30;
  
  const lastLearning = learningHistory[learningHistory.length - 1];
  const daysSinceLastLearning = daysBetween(lastLearning.date, today);
  
  // 间隔越长，复习效果越好
  if (daysSinceLastLearning >= 30) return 25;  // 一个月后复习
  if (daysSinceLastLearning >= 7) return 20;   // 一周后复习
  return 10;                                    // 短期内重复学习
}
```

### 2. 掌握度衰减

根据遗忘曲线衰减掌握度：

```javascript
function applyDecay(mastery, lastUpdated) {
  const daysSinceUpdate = daysBetween(lastUpdated, today);
  const decayRate = 0.02;  // 每天衰减 2%
  const decay = Math.floor(mastery * decayRate * daysSinceUpdate / 30);
  return Math.max(mastery - decay, 0);
}
```

### 3. 难度系数

不同难度概念增幅不同：

```javascript
function calculateIncrementByDifficulty(difficulty, learningCount) {
  const baseIncrement = [30, 20, 10][Math.min(learningCount, 2)];
  const difficultyMultiplier = {
    'easy': 1.2,
    'medium': 1.0,
    'hard': 0.8
  }[difficulty];
  
  return Math.floor(baseIncrement * difficultyMultiplier);
}
```

**当前版本不实现**，保持算法简单。
