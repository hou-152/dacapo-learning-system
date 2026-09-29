---
name: 垃圾回收型-agent
type: concept
tags:
  - concept
created: 2026-09-29
updated: 2026-09-29

sources:
  - link: "[[01-Martin-Fowler-harness-engineering]]"
  - link: "[[01-Martin-Fowler-harness-engineering]]"

mastery:
  level: 0.3
  rawScore: 30
  decay:
    lastReviewed: 2026-09-29
    halfLife: 30

masteryHistory: []

prerequisites: ["harness"]
derivedConcepts: []
relatedConcepts: ["卡住即信号", "显影与退役判据", "熵与腐化"]

patterns: []

theoryGrounding: null

studyCount: 0
lastStudied: null
studySessions: []
---

# 「垃圾回收」型 agent

## 定义

harness 的第三类组件，周期性运行的 agent，专找文档不一致与架构约束违规，用作者的话说是在 fighting entropy and decay。

## 为什么重要

软件不会自己变好，只会自己变乱。这类 agent 相当于给代码库雇了个巡道工：不产出新功能，只在后台不断把跑偏的地方拨回来，让熵增的速度慢于修复的速度。

## 前置概念

无

## 出现文章

- [[01-Martin-Fowler-harness-engineering]]

## 相关概念

- [[卡住即信号]]
- [[显影与退役判据]]
- [[熵与腐化]]
