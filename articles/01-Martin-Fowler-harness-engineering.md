# 第 01 篇：Martin Fowler 为「harness 工程」站台

> 原文：Harness Engineering - martinfowler.com

## 📊 前置概念检查

本文引入的核心概念：
- [[harness]] — 待学习
- [[context-engineering]] — 待学习
- [[无手打代码]] — 待学习

## 核心观点

这是一篇一线技术领导者对 OpenAI「Harness engineering」的近距离评点。作者 Birgitta 是 Thoughtworks 的 Distinguished Engineer，她认可 [[harness]] 这个词——用来指代「我们用来把 AI agent 管住的那一整套工具与实践」。

OpenAI 团队的实验本身足够硬：以 [[无手打代码]]（no manually typed code at all）作为 forcing function，逼自己造出一套用 AI agent 维护大型应用的 [[harness]]；五个月后做出一个真实产品，代码量已超过 100 万行。

## harness 由什么构成

作者把 OpenAI 的 [[harness]] 组件归成三类：

1. **[[context-engineering]]**：代码库里持续增强的知识库，加上让 agent 能取到动态上下文的通道
2. **[[架构约束的确定性执行]]**：由确定性的自定义 linter 和结构性测试来强制执行
3. **[[垃圾回收型-agent]]**：周期性运行，专门找文档不一致与架构约束违规，对抗 [[熵与腐化]]

关键的生长机制是 [[卡住即信号]]：agent 卡住不算失败，算信号；缺的工具、护栏、文档补回代码库。

## 核心洞察

作者指出 [[harness]] 的一个结构性缺口：[[功能与行为验证的缺口]] — 现有措施都在提升内部质量，但功能对不对，仍无人接管。

更深层的交换关系：要更高的 AI 自治，靠的是 [[解空间收窄]] — 固定的架构模式、强制的边界。这会推动技术栈收敛，[[ai-友好度作为选型标准]] 成为新的考量。

全文最大的一问：如果我们普遍学会 harness 代码库的设计模式，[[拓扑作为新抽象层]] 会不会成为现实，而不是自然语言本身。

## 结论

[[rigor-的搬迁]]：严谨没有消失，它只是从「一行行把代码写对」搬到了「把环境、反馈和控制设计对」。

OpenAI 团队自述：「Our most difficult challenges now center on designing environments, feedback loops, and control systems.」

## 本文引入的概念

- [[harness]]
- [[无手打代码]]
- [[context-engineering]]
- [[架构约束的确定性执行]]
- [[垃圾回收型-agent]]
- [[熵与腐化]]
- [[卡住即信号]]
- [[功能与行为验证的缺口]]
- [[service-template-与-golden-path]]
- [[解空间收窄]]
- [[ai-友好度作为选型标准]]
- [[拓扑作为新抽象层]]
- [[rigor-的搬迁]]

## 下一步

继续阅读 AI 内参 Harness 系列，观察概念网络的成长。
