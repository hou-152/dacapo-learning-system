# Bridge 说明生成规则

## 数据来源

从 `recommend.js` 的两个命令输出中提取：

### 1. bridge 命令输出

```bash
node recommend.js bridge <概念ID>
```

输出格式：
```
Top 3 桥接概念:

1. [桥接概念名称]
   掌握度: 0.8, 相关度: 0.7, 使用次数: 2
   桥接分数: 0.267
```

### 2. path 命令输出

```bash
node recommend.js path
```

输出格式：
```
Top 5 推荐:

1. [目标概念名称]
   当前掌握度: 0.3
   解锁潜力: 3 个新概念
   最佳桥接: [桥接概念名称]
   推荐分数: 0.367
```

## 生成规则

### 基础格式

从 bridge 命令输出生成：

```
你掌握了【{桥接概念名称}】(mastery {掌握度})，它可以帮助理解【{目标概念名称}】(relevance {相关度})
```

### 完整说明格式

```
你掌握了【{桥接概念名称}】(mastery {掌握度})，它可以帮助理解【{目标概念名称}】(relevance {相关度})

📊 桥接指标：
- 桥接分数 (bridgeScore): {桥接分数}
- 使用次数 (usageCount): {使用次数}

💡 学习价值：
- 解锁潜力 (unlockPotential): 掌握后可解锁 {数量} 个新概念
- 推荐分数 (recommendScore): {推荐分数}
```

## 字段说明

### 桥接概念相关

| 字段 | 说明 | 取值范围 |
|------|------|----------|
| mastery | 桥接概念的掌握度 | 0.0-1.0，≥0.6 才能作为桥接 |
| relevance | 桥接概念与目标概念的相关度 | 0.0-1.0，≥0.5 才能作为桥接 |
| bridgeScore | 桥接分数 = mastery × relevance / (1 + usageCount) | 数值越高越优先 |
| usageCount | 该概念已被使用作为桥接的次数 | 次数越多，bridgeScore 会降低 |

### 目标概念相关

| 字段 | 说明 | 取值范围 |
|------|------|----------|
| unlockPotential | 掌握该概念后能解锁的新概念数量 | 整数，数值越大价值越高 |
| recommendScore | 推荐分数 = bestBridgeScore + unlockPotential × 0.1 | 综合推荐优先级 |

## 实际示例

### 示例 1：单个桥接说明

输入数据（来自 bridge 命令）：
```
1. Transformer 架构
   掌握度: 0.8, 相关度: 0.7, 使用次数: 1
   桥接分数: 0.280
```

目标概念：BERT

生成说明：
```
你掌握了【Transformer 架构】(mastery 0.8)，它可以帮助理解【BERT】(relevance 0.7)

📊 桥接指标：
- 桥接分数 (bridgeScore): 0.280
- 使用次数 (usageCount): 1
```

### 示例 2：完整学习路径说明

输入数据（来自 path 命令）：
```
1. BERT
   当前掌握度: 0.3
   解锁潜力: 3 个新概念
   最佳桥接: Transformer 架构
   推荐分数: 0.580
```

结合 bridge 数据生成完整说明：
```
你掌握了【Transformer 架构】(mastery 0.8)，它可以帮助理解【BERT】(relevance 0.7)

📊 桥接指标：
- 桥接分数 (bridgeScore): 0.280
- 使用次数 (usageCount): 1

💡 学习价值：
- 解锁潜力 (unlockPotential): 掌握后可解锁 3 个新概念
- 推荐分数 (recommendScore): 0.580

推荐优先学习 BERT，当前掌握度仅 0.3，提升空间大。
```

## 使用场景

### 场景 1：查找单个概念的桥接

```bash
# 1. 运行 bridge 命令
node recommend.js bridge bert

# 2. 从输出提取数据生成说明
# 适用于：用户想了解如何学习某个特定概念
```

### 场景 2：获取整体学习路径

```bash
# 1. 运行 path 命令
node recommend.js path

# 2. 为每个推荐生成完整说明
# 适用于：用户想知道接下来应该学什么
```

## 注意事项

1. **数据新鲜度**：说明基于当前的 mastery 数据，概念掌握度变化后需重新生成
2. **桥接条件**：只有 mastery ≥ 0.6 且 relevance ≥ 0.5 的概念才能作为桥接
3. **使用次数影响**：每次使用某概念作为桥接后，应更新 bridge-usage.json，避免重复推荐
4. **解锁潜力计算**：基于前置概念依赖关系，只统计"学习该概念后立即解锁"的概念数

## 数据文件位置

- 相关度数据：`.learning-progress/concept-relevance.json`
- 桥接使用计数：`.learning-progress/bridge-usage.json`
- 概念定义：`concepts/**/*.md` (frontmatter 中的 mastery 和 prerequisites)
