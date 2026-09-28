---
tags: concept
category: 副作用处理
inDegree: 4
---

# useEffect

React Hook，用于处理副作用（side effects），如数据获取、订阅、DOM 操作等。

## 核心机制

```jsx
useEffect(() => {
  // 副作用逻辑
  return () => {
    // 清理函数（可选）
  };
}, [dependencies]);
```

## 依赖数组的三种模式

1. **无依赖数组**：每次渲染都执行
2. **空依赖数组 `[]`**：仅在挂载时执行一次
3. **指定依赖 `[dep1, dep2]`**：依赖变化时重新执行

## 清理机制

返回的清理函数在以下时机执行：
- 组件卸载时
- 依赖变化导致 effect 重新执行前

这是避免内存泄漏的重要机制（如清理定时器、取消订阅）。

## 使用场景

- API 请求
- 订阅/取消订阅
- 定时器管理
- DOM 事件监听

## 相关概念

- [[hooks]] - 所属的 Hooks 体系
- [[dependency-array]] - 依赖数组控制执行时机
- [[cleanup-function]] - 清理函数防止内存泄漏
- [[component-lifecycle]] - 对应 class 组件的生命周期
