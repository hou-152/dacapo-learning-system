---
tags: concept
category: 性能优化
inDegree: 1
---

# useMemo

React Hook，用于缓存计算结果，避免每次渲染都重新计算昂贵的值。

## 核心机制

```jsx
const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
```

只在依赖变化时重新计算，其他时候返回缓存值。

## 使用场景

- 昂贵的计算（如大数据过滤、排序）
- 复杂的数据转换
- 避免不必要的重新计算

## 注意事项

不要过度使用 `useMemo`，只在真正有性能问题时使用。

## 相关概念

- [[hooks]] - 所属的 Hooks 体系
- [[useCallback]] - 类似的性能优化 Hook（缓存函数）
- [[performance-optimization]] - 性能优化策略
