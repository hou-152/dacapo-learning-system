---
tags: concept
category: 状态传递
inDegree: 2
---

# useContext

React Hook，用于跨组件传递数据，避免 props drilling（层层传递）。

## 核心机制

```jsx
const value = useContext(SomeContext);
```

配合 `createContext` 和 `Context.Provider` 使用。

## 优势

- 避免 props drilling（层层传递）
- 全局状态管理的轻量方案
- 适合传递主题、用户信息等跨层级数据

## 使用场景

- 主题切换
- 用户认证信息
- 语言/国际化
- 全局配置

## 相关概念

- [[hooks]] - 所属的 Hooks 体系
- [[props-drilling]] - Context 要解决的问题
