---
tags: concept
category: 状态管理
inDegree: 3
---

# useState

React Hook，用于在函数组件中管理状态。

## 核心机制

```jsx
const [state, setState] = useState(initialValue);
```

- 返回一对值：当前状态和更新函数
- 初始值只在首次渲染时使用
- 更新函数触发组件重新渲染

## 使用场景

- 表单输入
- 开关状态
- 计数器
- 用户交互状态

## 多状态管理

可以在一个组件中多次调用 `useState`，每个状态独立管理。

## 相关概念

- [[hooks]] - 所属的 Hooks 体系
- [[useReducer]] - 复杂状态的替代方案
- [[component-rerender]] - 状态更新触发重新渲染
