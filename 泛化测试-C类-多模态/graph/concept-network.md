# React Hooks 概念网络

```mermaid
graph TB
    hooks[Hooks<br/>核心机制]
    useState[useState<br/>状态管理]
    useEffect[useEffect<br/>副作用处理]
    useContext[useContext<br/>跨组件传递]
    useReducer[useReducer<br/>复杂状态]
    useRef[useRef<br/>持久化引用]
    useMemo[useMemo<br/>缓存计算]
    useCallback[useCallback<br/>缓存函数]
    
    depArray[dependency-array<br/>依赖数组]
    cleanup[cleanup-function<br/>清理函数]
    rerender[component-rerender<br/>组件重渲染]
    propsDrilling[props-drilling<br/>Props 层层传递]
    perfOptim[performance-optimization<br/>性能优化]
    
    hooks -->|状态管理| useState
    hooks -->|副作用处理| useEffect
    hooks -->|跨组件传递| useContext
    hooks -->|复杂状态| useReducer
    hooks -->|持久化引用| useRef
    hooks -->|性能优化| useMemo
    hooks -->|性能优化| useCallback
    
    useEffect -->|控制执行时机| depArray
    useEffect -->|防止内存泄漏| cleanup
    
    useState -->|触发| rerender
    useReducer -->|替代方案| useState
    
    useContext -->|解决问题| propsDrilling
    
    useRef -.->|不触发| rerender
    
    useMemo -->|属于| perfOptim
    useCallback -->|属于| perfOptim
    useCallback -.->|类似| useMemo
    
    classDef hub fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    classDef core fill:#4ecdc4,stroke:#087f5b,stroke-width:2px
    classDef support fill:#95e1d3,stroke:#087f5b,stroke-width:1px
    
    class hooks hub
    class useState,useEffect,useContext core
    class useReducer,useRef,useMemo,useCallback,depArray,cleanup,rerender,propsDrilling,perfOptim support
```

## 网络分析

### Hub 概念（inDegree >= 3）

**hooks**（inDegree: 7）
- 核心 Hub 节点
- 连接所有 React Hooks API
- 是整个系统的入口概念

### 核心概念层

**useState**（inDegree: 3）
- 最常用的状态管理 Hook
- 与 useReducer、component-rerender 关联

**useEffect**（inDegree: 4）
- 副作用处理的核心
- 依赖 dependency-array 和 cleanup-function

**useContext**（inDegree: 2）
- 解决 props-drilling 问题
- 轻量级状态管理方案

### 性能优化层

**useMemo** 和 **useCallback**
- 都属于性能优化策略
- 两者功能相似（缓存值 vs 缓存函数）

### 特殊机制

**useRef**（inDegree: 2）
- 不触发重新渲染的特殊机制
- DOM 引用和可变值存储

**useReducer**（inDegree: 2）
- 复杂状态管理
- useState 的增强版

## 概念关系类型

- **实线箭头**：主要关系（从属、依赖）
- **虚线箭头**：对比关系（类似、替代、相反）

## 网络特点

1. **清晰的层次结构**：Hub → 核心 API → 支持概念
2. **语义化关系标签**：不只是"依赖"，有明确语义
3. **适度复杂度**：13 个节点，20+ 条边，可读性良好
