# Harness Engineering

围绕 Agent 建立可复现的上下文、工具、权限、验证和失败处理边界。它不替 Agent 执行任务，而是规定 Agent 在什么环境中运行、如何证明完成、失败时如何停止或恢复。

## 与 Loop Engineering 的关系

- [[Loop Engineering]] 提供持续启动、执行、验证和修复的循环。
- Harness Engineering 提供这个循环必须遵守的轨道、护栏与验收条件。
- 没有 Harness 的 Loop 容易把错误自动化；没有 Loop 的 Harness 只是一组静态约束。

## 相关课题

- [[AI工作流控制权迁移]] — 控制权从提示词迁移到循环和工程约束。
- [[Agentic Engineering 工作流]] — Harness 的具体工程实践。
- [[交互式学习]] — 学习状态也需要证据门禁与失败保护。
