---
tags: concept
category: 状态管理
inDegree: 2
---

# useReducer

React Hook，用于管理复杂状态逻辑，是 `useState` 的替代方案。

## 核心机制

```jsx
const [state, dispatch] = useReducer(reducer, initialState);
```

通过 dispatch action 来更新状态，类似 Redux 模式。

## 适用场景

- 状态逻辑复杂
- 多个子状态相互依赖
- 需要可预测的状态更新
- 购物车、表单验证等场景

## Reducer 函数

```jsx
function reducer(state, action) {
  switch (action.type) {
    case 'ACTION_TYPE':
      return newState;
    default:
      return state;
  }
}
```

## 相关概念

- [[hooks]] - 所属的 Hooks 体系
- [[useState]] - 简单状态的替代方案
- [[redux-pattern]] - 借鉴的设计模式
