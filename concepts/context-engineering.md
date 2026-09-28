---
tags: concept
inDegree: 1
firstAppearance: "[[01-Martin-Fowler-harness-engineering]]"
---

# context engineering（上下文工程）

## 定义

作者归纳的 harness 三类组件之首：代码库内部持续增强的知识库，加上让 agent 取到动态上下文的通道——可观测性数据、浏览器导航。文末她进一步指出，上下文工程不只是策展知识库，代码设计本身就是上下文的一大部分。

## 为什么重要

agent 干得好不好，很大程度取决于它此刻知道什么。上下文工程就是有计划地安排「它该知道什么、从哪里知道」：静态的写进代码库，动态的开一条实时通道。而最深的一层是：代码写成什么样，本身就在告诉 agent 这个系统该怎么运转。

## 前置概念

无

## 出现文章

- [[01-Martin-Fowler-harness-engineering]]
