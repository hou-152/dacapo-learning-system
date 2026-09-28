# dacapo 学习仓库

这是一个独立的 Obsidian 仓库，专门用于 dacapo 交互式学习。

## 目录结构

```
dacapo-学习仓库/
├── articles/           # 学习文章（按序号命名）
│   ├── 01-*.md
│   └── 02-*.md
├── concepts/           # 概念库（全局，每个概念一个文件）
│   ├── harness.md
│   └── context-engineering.md
├── graph/
│   ├── local/         # 局部概念网络（每篇文章独立）
│   │   ├── 01-concept-network.md
│   │   └── 02-concept-network.md
│   └── global/        # 全局 Hub 网络（只显示核心概念）
│       └── hub-concepts.md
└── raw-sources/       # 原始材料

## 设计理念

### 局部网络 + 全局 Hub

- **局部网络**：每篇文章提取完整的概念关系（丰富语义）
- **全局 Hub**：只显示 inDegree >= 3 的核心概念（避免熵增）

### 学习流程

1. 读完一篇文章
2. 自动生成本文的概念网络（`graph/local/NN-concept-network.md`）
3. 更新全局 Hub 网络（`graph/global/hub-concepts.md`）
4. 在 Obsidian 中查看：
   - 看本文网络 → 理解本文的概念关系
   - 看全局 Hub → 理解整个系列的核心概念

## 在 Obsidian 中打开

```bash
open -a Obsidian ~/Documents/dacapo-学习仓库/
```

## 生成时间

2026-09-28
