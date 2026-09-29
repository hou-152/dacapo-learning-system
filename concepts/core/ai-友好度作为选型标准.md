---
name: ai-友好度作为选型标准
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
relatedConcepts: ["service-template-与-golden-path", "无手打代码", "跨模型迁移"]

patterns: []

theoryGrounding: null

studyCount: 0
lastStudied: null
studySessions: []
---

# AI 友好度（AI-friendliness）作为选型标准

## 定义

作者对技术栈收敛的预判：当写代码变成 steering its generation，开发者在细节层面的口味变得不重要，接口的小怪癖不再烦人，团队可能优先选「有好 harness 可用」的栈。同时她保留了一句反向判断——what's good for humans is good for AI。

## 为什么重要

过去选框架看「我用着顺不顺手」，以后可能要多问一句「agent 用着顺不顺手、有没有现成护栏」。有意思的是这两个标准并不对立：清晰的接口对人好，对模型同样好。

## 前置概念

无

## 出现文章

- [[01-Martin-Fowler-harness-engineering]]

## 相关概念

- [[service-template-与-golden-path]]
- [[无手打代码]]
- [[跨模型迁移]]
