# DaCapo Learn v2.0.0 - 智能路由系统

**发布日期**: 2026-09-28  
**重大更新**: 从简单关键词路由升级为智能意图识别 + 历史上下文检索 + 内容编排

---

## 📦 下载

- **Skills 包**: `dacapo-v2.0.0-intelligent-routing.tar.gz` (74KB)
- **文档包**: `dacapo-v2.0.0-docs.tar.gz` (37KB)

## 🎯 核心升级

### 1. 智能路由系统（dacapo-main）
**从关键词匹配 → 意图识别引擎**

- **5 种意图自动识别**:
  - `learn` — 学习概念（带历史上下文）
  - `status` — 查看学习进度
  - `discover` — 探索概念关联
  - `visualize` — 可视化图谱
  - `suggest` — 获取学习推荐

- **历史上下文检索**: 自动调用 dacapo-wiki 获取已学概念的掌握度、依赖关系、跨项目关联

- **智能推荐**: 输出"推荐 skill + 理由 + 可发送的提示词"

### 2. 内容编排引擎（dacapo-learning）
**从简单执行 → 模糊愿望变具体任务**

- **接收历史上下文**: 来自 dacapo-wiki 的 JSON 结构化数据
- **4 种编排模式**:
  1. 理论理解型 — 强调概念本质和边界
  2. 实战应用型 — 强调项目中应用
  3. 工具掌握型 — 强调具体工具使用
  4. 体系构建型 — 系统掌握整个领域

- **JTBD 任务框架**: 情境 → 进展 → 结果（参考 dbs-jtbd）
- **目标拆解**: 前置依赖检查 + Hub 概念识别 + 验收标准（参考 dbs-goal）

### 3. JSON 接口（dacapo-wiki）
**从人类可读 → 可调用接口**

- **新增参数**: `--format json`
- **结构化输出**: 
  ```json
  {
    "target": {
      "name": "概念名称",
      "mastery": 0.75,  // null = 未学习
      "definition": "...",
      "dependencies": [...]
    },
    "suggestions": [
      {
        "concept": {...},
        "type": "dependency|downstream|hub|semantic",
        "similarity": 0.85,
        "reason": "推荐理由"
      }
    ]
  }
  ```

- **向后兼容**: 默认仍为人类可读格式

---

## 🎨 对标 dbs 形态

| 特性 | v1.0.0 | v2.0.0 |
|------|--------|--------|
| 统一入口 | ❌ 需要指定 skill | ✅ `/dacapo` 搞定一切 |
| 智能路由 | ❌ 关键词匹配 | ✅ 5 种意图识别 |
| 直接执行 | ❌ 需要复制粘贴 | ✅ 自动调用 skill |
| 上下文记忆 | ❌ 每次从零开始 | ✅ 检索已学概念 |
| 内容编排 | ❌ 直接执行学习 | ✅ 先编排后执行 |

---

## 📚 新增文档

### 核心文档
- `INTELLIGENT-ROUTING-UPGRADE.md` — 完整升级报告
- `VERSION.md` — 版本历史

### References（渐进式加载）
- `dacapo-main/references/intent-patterns.md` — 意图识别示例库
- `dacapo-main/references/context-routing.md` — 路由规则（7.9KB）
- `dacapo-main/references/detailed-instructions.md` — 详细执行指令（8.6KB）
- `dacapo-learning/references/learning-patterns.md` — 4 种编排模式
- `dacapo-wiki/INTEGRATION.md` — 集成指南

### 测试
- `test-intelligent-routing.sh` — 集成测试
- `test-end-to-end.sh` — 端到端用户流程测试

---

## ✅ 测试验证

### 场景 1: 学习已有概念
```
用户: 我想深入学习 harness 这个概念
系统: ✓ 检测到意图 learn
     ✓ 获取历史上下文（掌握度 null，发现跨项目关联 deepseek-harness）
     ✓ 编排学习路径（理论理解型）
```

### 场景 2: 学习新概念
```
用户: 我想学习量子计算
系统: ✓ 检测到意图 learn
     ✓ 概念不存在（掌握度 null）
     ✓ 从零编排路径（体系构建型）
```

### 场景 3: 查看进度
```
用户: 查看我的学习进度
系统: ✓ 检测到意图 status
     ✓ 统计：13 个概念，学习率 0%
```

### 场景 4: 探索关联
```
用户: 发现与 harness 相关的概念
系统: ✓ 检测到意图 discover
     ✓ 返回跨项目草蛇灰线（harness ↔ deepseek-harness）
```

---

## 🏗️ 架构设计

### 参考模式
- **skill-creator**: 渐进式加载（SKILL.md < 500 行，详细内容到 references/）
- **dbs-goal**: 目标拆解、前置依赖检查、验收标准
- **dbs-jtbd**: 任务陈述框架（情境/进展/结果）
- **dbs 主入口**: 统一路由、智能判断、直接执行

### 数据流
```
用户输入
  ↓
dacapo-main（意图识别）
  ↓
dacapo-wiki（上下文检索，仅 learn 意图）
  ↓
dacapo-learning（内容编排）
  ↓
交互式学习（执行）
```

---

## 🚀 开发统计

**模式**: worktree + 多 agent  
**编排**: fable5.1（任务拆解）  
**执行**: opus5.5 subagents（3 个并行）

| Agent | 任务 | 用时 | Tokens |
|-------|------|------|--------|
| 1 | dacapo-learning 编排 | 6 分钟 | 92K |
| 2 | dacapo-main 路由 | 8.5 分钟 | 99K |
| 3 | dacapo-wiki 接口 | ~8 分钟 | ~90K |

**总用时**: ~30 分钟（并行执行）  
**总 Tokens**: ~281K

---

## 📥 安装

### 解压 Skills
```bash
cd ~/.openclaw-autoclaw/skills
tar -xzf dacapo-v2.0.0-intelligent-routing.tar.gz
```

### 解压文档
```bash
cd ~/Documents/交互式学习
tar -xzf dacapo-v2.0.0-docs.tar.gz
```

### 测试
```bash
cd ~/Documents/交互式学习
bash test-end-to-end.sh
```

---

## 🔄 从 v1.0.0 升级

v2.0.0 完全向后兼容 v1.0.0。直接覆盖 skills 目录即可：

```bash
# 备份旧版本（可选）
cp -r ~/.openclaw-autoclaw/skills/dacapo-* ~/backup/

# 解压新版本（会覆盖同名文件）
cd ~/.openclaw-autoclaw/skills
tar -xzf dacapo-v2.0.0-intelligent-routing.tar.gz
```

---

## 🎯 核心价值

### v1.0.0 继承
- ✅ 复利式学习（2.4x 效果提升）
- ✅ 跨项目草蛇灰线
- ✅ Obsidian frontmatter 状态记录

### v2.0.0 新增
- ✅ 智能意图识别（5 种意图）
- ✅ 历史上下文检索（自动获取已学概念）
- ✅ 内容编排能力（模糊愿望 → 具体任务）
- ✅ 统一入口体验（对标 dbs）

---

## 📝 已知限制

1. **dacapo-wiki 命令**: 当前只支持 `context`，`search`/`explore` 命令待实现
2. **掌握度记录**: 部分概念的 mastery 字段为 null（需要手动更新 frontmatter）
3. **推荐算法**: 权重配置暂未开放调整接口

---

## 🛣️ 未来计划

### v2.1.0（短期）
- 实现 dacapo-wiki 的 `explore` 命令
- 添加更多意图识别示例
- 优化推荐算法权重

### v3.0.0（中期）
- 实时学习进度追踪
- 学习路径可视化
- 多人协作学习支持

---

**发布者**: DaCapo Team  
**技术支持**: 提交 issue 到项目仓库  
**许可证**: 见 LICENSE 文件
