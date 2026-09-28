---
tags: concept
category: 性能优化
inDegree: 1
---

# useCallback

React Hook，用于缓存函数引用，避免子组件不必要的重渲染。

## 核心机制

```jsx
const memoizedCallback = useCallback(() => {
  doSomething(a, b);
}, [a, b]);
```

返回一个记忆化的回调函数，只在依赖变化时更新。

## 使用场景

- 传递给子组件的回调函数
- 防止子组件不必要的重渲染
- 配合 `React.memo` 使用

## 与 useMemo 的区别

- `useMemo` 缓存**计算结果**（值）
- `useCallback` 缓存**函数引用**（函数本身）

实际上 `useCallback(fn, deps)` 等价于 `useMemo(() => fn, deps)`

## 相关概念

- [[hooks]] - 所属的 Hooks 体系
- [[useMemo]] - 类似的性能优化 Hook（缓存值）
- [[performance-optimization]] - 性能优化策略
