---
tags: concept
category: 核心机制
inDegree: 7
---

# Hooks

React 16.8 引入的新特性，允许在函数组件中使用 state 和其他 React 特性，无需编写 class 组件。

## 核心价值

- 让函数组件拥有与 class 组件同等的能力
- 代码更简洁、逻辑更清晰
- 更好的代码复用（通过自定义 Hook）

## 三大规则

1. **只在顶层调用**：不要在循环、条件或嵌套函数中调用
2. **只在 React 函数中调用**：函数组件或自定义 Hook 中
3. **命名规范**：自定义 Hook 必须以 `use` 开头

## 相关概念

- [[useState]] - 状态管理
- [[useEffect]] - 副作用处理
- [[useContext]] - 跨组件传递
- [[useReducer]] - 复杂状态管理
- [[useRef]] - 持久化引用
- [[useMemo]] - 性能优化
- [[useCallback]] - 性能优化
