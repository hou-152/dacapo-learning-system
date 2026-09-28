---
tags: concept
category: 持久化引用
inDegree: 2
---

# useRef

React Hook，用于创建持久化引用，在组件生命周期内保持不变。

## 核心特点

- 修改 `.current` 不触发重新渲染
- 在组件生命周期内保持不变
- 返回一个可变的 ref 对象

## 两大用途

### 1. DOM 引用

获取并操作 DOM 节点：

```jsx
const inputRef = useRef(null);
inputRef.current.focus();
```

### 2. 保存可变值

存储不需要触发渲染的值（如定时器 ID）：

```jsx
const intervalRef = useRef(null);
intervalRef.current = setInterval(...);
```

## 相关概念

- [[hooks]] - 所属的 Hooks 体系
- [[component-rerender]] - useRef 不触发重新渲染
