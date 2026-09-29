# Phase 2: 概念关系图谱计算系统

## 实现状态

✅ **四信号相关度计算引擎** (`scripts/calculate-relevance.js`)
- sourceOverlap (×4.0): Jaccard 相似度
- directLink (×3.0): 双向 1.0, 单向 0.6
- commonNeighbor (×1.5): Adamic-Adar 指数
- typeAffinity (×1.0): 同类型 1.0, 异类型 0.5

✅ **桥接概念匹配 & 学习路径推荐** (`scripts/recommend.js`)
- 桥接概念：mastery ≥ 0.6 且 relevance ≥ 0.5
- 学习路径：前置概念已解锁 + 解锁潜力排序

✅ **数据层统一** (已完成于 main 分支)
- 78 个概念迁移到新 Schema
- relatedConcepts 和 prerequisites 字段已填充

## 使用方法

### 1. 计算概念相关度

```bash
node scripts/calculate-relevance.js
```

输出：`.learning-progress/concept-relevance.json`

**当前结果**：
- 78 个概念
- 127 条有效边（relevance > 0.3）
- 稀疏度 96%
- 平均相关度 0.129
- 耗时 6ms

**Top 3 相关概念对**：
1. harness ↔ 拓扑作为新抽象层: 0.986
2. harness ↔ 架构约束的确定性执行: 0.986
3. 拓扑作为新抽象层 ↔ 架构约束的确定性执行: 0.986

### 2. 查找桥接概念

```bash
node scripts/recommend.js bridge <概念ID>
```

示例：
```bash
node scripts/recommend.js bridge 差序格局
```

输出 Top 3 桥接概念（已掌握且高度相关）。

### 3. 推荐学习路径

```bash
node scripts/recommend.js path
```

输出 Top 5 推荐概念（已解锁且解锁潜力高）。

## 性能指标

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 单概念对计算 | < 1ms | ~0.002ms | ✅ |
| 全量计算 (78 概念) | < 500ms | 6ms | ✅ |
| 稀疏矩阵存储 | > 80% | 96% | ✅ |

## 数据结构

### 相关度数据 (`.learning-progress/concept-relevance.json`)

```json
{
  "metadata": {
    "generated": "2026-09-29T21:49:15.391Z",
    "conceptCount": 78,
    "edgeCount": 127,
    "avgRelevance": 0.129,
    "weights": {
      "sourceOverlap": 4,
      "directLink": 3,
      "commonNeighbor": 1.5,
      "typeAffinity": 1
    }
  },
  "edges": [
    {
      "from": "harness",
      "to": "拓扑作为新抽象层",
      "relevance": 0.986,
      "signals": {
        "sourceOverlap": 1,
        "directLink": 1,
        "commonNeighbor": 0.91,
        "typeAffinity": 1
      }
    }
  ]
}
```

### 桥接使用计数 (`.learning-progress/bridge-usage.json`)

```json
{
  "反身性": 3,
  "差序格局": 1
}
```

每次选择桥接概念后，增加其使用计数，避免重复使用同一概念。

## 算法细节

### 四信号权重设计

**核心原则**（用户强调）：
> "来源可溯是全网络的枢纽。权重最高的信号（×4.0）恰恰是来源重叠而非直接链接，等于宣称同源比互链更能说明相关性。"

| 信号 | 权重 | 含义 | 计算方法 |
|------|------|------|----------|
| sourceOverlap | 4.0 | 同源性 | Jaccard(sources_A, sources_B) |
| directLink | 3.0 | 显式关联 | 双向 1.0 / 单向 0.6 / 无 0.0 |
| commonNeighbor | 1.5 | 隐式关联 | Adamic-Adar / 共同邻居数 |
| typeAffinity | 1.0 | 类型一致性 | 同类型 1.0 / 异类型 0.5 |

综合相关度 = (∑ signal × weight) / ∑ weight

### 桥接概念评分

```
bridgeScore = (mastery × relevance) / (1 + usageCount)
```

- 优先推荐掌握度高的概念
- 优先推荐相关度高的概念
- 惩罚重复使用的概念

### 学习路径推荐

```
recommendScore = bestBridgeScore + unlockPotential × 0.1
```

- 主要依据桥接概念质量
- 解锁潜力作为次要因素

## 当前限制

1. **掌握度数据缺失**：所有概念 mastery = 0.3（迁移时的默认值）
   - 影响：桥接概念匹配和路径推荐无实质输出
   - 解决：需要真实学习进度数据

2. **prerequisites 数据稀疏**：大部分概念 prerequisites = []
   - 影响：解锁状态计算和解锁潜力计算效果有限
   - 解决：需要人工标注前置概念关系

3. **无增量编译**：每次全量重算
   - 影响：当前规模下性能足够（6ms），未来扩展到 1000+ 概念时需优化
   - 解决：实现 SHA256 变更检测和依赖传播

## 下一步

### Phase 2.1: 增量编译机制
- 变更检测（SHA256 哈希）
- 依赖传播（受影响概念对）
- 冷启动 vs 增量更新策略

### Phase 2.2: 可视化
- 使用 vis-network 生成交互式网络图
- 边粗细反映相关度强弱
- 节点颜色反映掌握度

### Phase 2.3: 数据补全
- 补全 prerequisites 标注（人工 + 半自动）
- 导入真实学习进度（从 masteryHistory）
- 验证推荐算法效果

## 技术栈

- **语言**：Node.js (标准库)
- **依赖**：零（纯标准库实现）
- **数据格式**：JSON
- **性能**：O(N²) 全量计算，未来 O(Δ×N) 增量更新

## 参考

- 规格文档：`PHASE2-SPEC.md`
- 算法实现决策：`/tmp/algorithm-implementation-decisions.md`
- 测试策略：`/tmp/testing-strategy.md`
