---
name: service-template-与-golden-path
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
relatedConcepts: ["架构约束的确定性执行", "ai-友好度作为选型标准", "rigor-的搬迁"]

patterns: []

theoryGrounding: null

studyCount: 0
lastStudied: null
studySessions: []
---

# service template 与 golden path

## 定义

作者用来类比 harness 未来形态的现成实践：service template 帮团队沿 golden path 实例化新服务；她设想团队从一组 harness 里按应用拓扑挑一个开工，也预判了同样的 forking 与同步难题。

## 为什么重要

golden path 是组织内被推荐的默认路线——照它走，脚手架、规范、工具链都是现成的。harness 若走上这条路，好处是新项目开局即有护栏，坏处是老问题会照搬过来：每个团队都把模板改成自己的样子，上游更新就再也合不回去。

## 前置概念

无

## 出现文章

- [[01-Martin-Fowler-harness-engineering]]

## 相关概念

- [[架构约束的确定性执行]]
- [[ai-友好度作为选型标准]]
- [[rigor-的搬迁]]
