# 掌握度更新规则

## 核心规则

完成课程后，仅更新课程的 `mainConcepts` 掌握度，每次增加 0.2，上限 1.0。

## 详细说明

### 更新对象

- ✅ **mainConcepts**：课程直接教授的核心概念
- ❌ **relatedConcepts**：相关但非核心的概念，不更新

### 增量规则

- **增量值**：0.2
- **上限**：1.0
- **计算**：`new_mastery = min(current_mastery + 0.2, 1.0)`

### 更新时机

课程完成时触发更新。

## masteryHistory 字段

记录每次掌握度变化的历史。

### 字段结构

```json
{
  "masteryHistory": [
    {
      "timestamp": "2026-09-30T10:30:00Z",
      "delta": 0.2,
      "source": "course_completion",
      "courseId": "course_123",
      "previousMastery": 0.4,
      "newMastery": 0.6
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| timestamp | string | ISO 8601 格式时间戳 |
| delta | number | 本次变化量（通常为 0.2） |
| source | string | 更新来源（`course_completion`） |
| courseId | string | 触发更新的课程 ID |
| previousMastery | number | 更新前的掌握度 |
| newMastery | number | 更新后的掌握度 |

## 示例

### 场景：完成课程后更新概念掌握度

**课程信息**：
- courseId: `"blockchain_basics"`
- mainConcepts: `["blockchain", "consensus"]`
- relatedConcepts: `["cryptography", "distributed_systems"]`

**更新前**：
```json
{
  "blockchain": { "mastery": 0.4 },
  "consensus": { "mastery": 0.6 },
  "cryptography": { "mastery": 0.3 },
  "distributed_systems": { "mastery": 0.5 }
}
```

**更新后**：
```json
{
  "blockchain": { 
    "mastery": 0.6,
    "masteryHistory": [{
      "timestamp": "2026-09-30T10:30:00Z",
      "delta": 0.2,
      "source": "course_completion",
      "courseId": "blockchain_basics",
      "previousMastery": 0.4,
      "newMastery": 0.6
    }]
  },
  "consensus": { 
    "mastery": 0.8,
    "masteryHistory": [{
      "timestamp": "2026-09-30T10:30:00Z",
      "delta": 0.2,
      "source": "course_completion",
      "courseId": "blockchain_basics",
      "previousMastery": 0.6,
      "newMastery": 0.8
    }]
  },
  "cryptography": { "mastery": 0.3 },
  "distributed_systems": { "mastery": 0.5 }
}
```

**关键点**：
- `blockchain` 和 `consensus` 作为 mainConcepts 被更新
- `cryptography` 和 `distributed_systems` 作为 relatedConcepts 保持不变
- 每个更新都记录了完整的历史信息

### 达到上限的情况

**更新前**：
```json
{
  "blockchain": { "mastery": 0.9 }
}
```

**完成课程后**：
```json
{
  "blockchain": { 
    "mastery": 1.0,
    "masteryHistory": [{
      "timestamp": "2026-09-30T11:00:00Z",
      "delta": 0.1,
      "source": "course_completion",
      "courseId": "advanced_blockchain",
      "previousMastery": 0.9,
      "newMastery": 1.0
    }]
  }
}
```

**说明**：实际增量为 0.1（从 0.9 到上限 1.0），记录在 `delta` 字段中。

## 设计原则

1. **简单一致**：固定增量 0.2，便于预测和理解
2. **聚焦核心**：只更新直接教授的概念，避免过度推断
3. **可追溯**：完整记录更新历史，支持回溯和分析
4. **防止溢出**：设置上限 1.0，符合掌握度语义
