# DaCapo 自适应学习系统

让学习上瘾的复利式知识管理系统。

---

## 🚀 快速开始

### 方式 1：命令行启动（推荐）

在任意终端窗口输入：

```bash
dacapo              # 打开学习中心
dacapo-network      # 打开概念网络图
dacapo-progress     # 打开进度仪表盘
dacapo-refresh      # 刷新学习数据
```

首次使用需要重新加载 shell：`source ~/.zshrc`

### 方式 2：浏览器直接打开

```bash
open ~/Documents/dacapo-学习仓库/dashboard/index.html
```

或双击 `dashboard/index.html` 文件。

---

## 📊 当前学习状态

- **已掌握概念**: 18 个
- **平均掌握度**: 65.3%
- **概念关联**: 243 条
- **复利指数**: 1599.7

### 优秀掌握 (≥80%)
- 差序格局 90%
- 礼治秩序 90%
- 人情期货 90%
- 面子估值 85%
- 现代长老 80%

---

## 🎯 核心功能

### 1. 即时反馈系统
学完概念后 3 秒内生成：
- 📊 反馈类型分析（深度理解、判断标准、应用导向等 5 种类型）
- 🎉 新掌握的概念列表
- 🕸️ Mermaid 概念关联网络图
- 💡 下一步学习建议

### 2. 概念网络可视化
- 交互式 Mermaid 图谱
- 颜色编码掌握度（绿色=优秀，蓝色=良好，橙色=学习中）
- 显示概念依赖关系
- 可视化网络扩张过程

### 3. 学习进度追踪
- 实时仪表盘
- 掌握度分布统计
- 按类别分组展示
- 复利指数计算

---

## 📚 使用流程

### 学习新课程

1. 使用 dbs-learning 学习文章课程
2. 在文章末尾写学习反馈
3. 运行增强脚本添加即时反馈：

```bash
cd ~/Documents/dacapo-学习仓库
python3 scripts/enhance_dbs_learning.py \
    ~/Documents/dbskill-learning/课程名/01.md \
    概念1 概念2 概念3
```

4. 刷新数据并查看可视化：

```bash
dacapo-refresh
dacapo
```

### 查看单个概念的即时反馈

```bash
cd ~/Documents/dacapo-学习仓库
python3 scripts/instant_feedback.py "概念名"
```

### 批量增强已有课程

```bash
cd ~/Documents/dacapo-学习仓库
./scripts/batch_enhance_sociology.sh
```

---

## 🛠️ 技术架构

### 核心脚本

| 脚本 | 功能 |
|------|------|
| `extract_sociology_concepts.py` | 从课程中提取概念，创建概念文件 |
| `enhance_dbs_learning.py` | 为文章添加 DaCapo 即时反馈 |
| `update_mastery_from_concepts.py` | 从概念文件同步掌握度到 mastery.json |
| `instant_feedback.py` | 生成单个概念的即时反馈 |
| `progress_tracker.py` | 生成实时学习进度仪表盘 |

### 数据结构

```
dacapo-学习仓库/
├── concepts/              # 概念库（每个概念一个 .md 文件）
├── .learning-progress/    # 学习数据
│   ├── mastery.json      # 概念掌握度
│   ├── timeline.json     # 学习时间线
│   └── dashboard-realtime.md  # 实时仪表盘
├── dashboard/            # 可视化页面（持久化）
│   ├── index.html       # 学习中心首页
│   ├── network.html     # 概念网络图
│   └── progress.html    # 学习进度仪表盘
└── scripts/             # 核心脚本
```

### 概念文件格式

```markdown
---
tags: concept, sociology-core
firstAppearance: "[[社会学七书共读/02.md]]"
mastery: 0.90
lastStudied: 2026-09-30
studyCount: 1
---

# 差序格局

## 定义

以自我为中心的同心圆社交网络，圈内人情、圈外规则

## 相关概念

- [[礼治秩序]]
- [[社会分层]]
```

---

## 🎮 成瘾机制

### 即时反馈
学完概念 → 3 秒内看到掌握度、网络图、解锁新概念

### 可视化进展
每次学习 → 看到网络扩张、复利指数上升

### 复利效应
关联越多 → 复利指数增长越快 → 量化学习的「滚雪球效应」

---

## 📈 复利指数计算

```
复利指数 = (已学概念数 × 平均掌握度 × 关联密度) × 100

关联密度 = 总关联数 / (已学概念数 × (已学概念数 - 1))
```

当前数据：
```
18 × 0.653 × 0.752 × 100 = 1599.7
```

---

## 🔄 数据同步

### 概念文件 → mastery.json

```bash
python3 scripts/update_mastery_from_concepts.py
```

### 刷新仪表盘

```bash
python3 scripts/progress_tracker.py
```

### 一键刷新

```bash
dacapo-refresh
```

---

## 🎨 可视化样式

- 深色主题（护眼）
- 渐变色强调
- 响应式布局
- 实时数据加载

---

## 📝 已完成课程

### 社会学七书共读（9 篇）

- 01 - 米尔斯与社会学想象力
- 02 - 差序格局与圈子文化
- 03 - 人情与面子：礼治秩序
- 04-09 - 社会分层、承认政治、理性化铁笼等

**提取概念**: 18 个（9 个用户自创 + 9 个社会学核心）

---

## 🚧 下一步计划

### Phase 2: 高级可视化

- [ ] 概念网络 3D 交互图
- [ ] 学习曲线时间线
- [ ] 间隔复习调度
- [ ] 知识资产统计

### Phase 3: 自动化集成

- [ ] 将增强脚本集成到 dbs-learning skill
- [ ] 学完文章自动生成即时反馈
- [ ] 自动提取概念并入库
- [ ] 实时推送学习通知

---

## 🤝 与其他系统集成

### dbs-learning (文章学习)

DaCapo 提供即时反馈和可视化，dbs-learning 提供课程内容和反馈收集。

### 概念库 (concepts/)

所有概念统一管理，frontmatter 记录掌握度和学习历史。

---

## 📖 使用示例

### 完整学习流程

```bash
# 1. 学习新课程（在 dbs-learning 中）
cd ~/Documents/dbskill-learning/新课程/
# 阅读 01.md，在文章末尾写反馈

# 2. 添加即时反馈
cd ~/Documents/dacapo-学习仓库
python3 scripts/enhance_dbs_learning.py \
    ~/Documents/dbskill-learning/新课程/01.md \
    概念A 概念B

# 3. 查看结果
open ~/Documents/dbskill-learning/新课程/01.md
# 滚动到文章末尾，看到完整的 DaCapo 即时反馈

# 4. 刷新仪表盘
dacapo-refresh

# 5. 打开可视化
dacapo
```

---

## 🎓 设计理念

### 即时反馈
学习不是存钱，是看钱增长。每学完一个概念，立刻看到网络扩张。

### 进度可见
掌握度分布、复利指数、概念网络——学习进展一目了然。

### 自适应调整
基于反馈类型和掌握度，推荐下一步学习方向。

### 上下文节省
轻量索引 + 按需加载，不占用大量 token。

---

## 📞 快捷命令总结

```bash
dacapo              # 打开学习中心
dacapo-network      # 概念网络图
dacapo-progress     # 学习进度仪表盘
dacapo-refresh      # 刷新数据
```

首次使用：`source ~/.zshrc`

---

**让学习像滚雪球一样，越滚越大，越滚越快。**
