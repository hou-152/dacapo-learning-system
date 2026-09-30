# learning-navigator

DaCapo 交互式学习系统的智能导航器。

## 功能

识别用户的 5 种学习场景，推荐合适的 skill 和参数，生成可直接执行的提示词。

## 支持的场景

1. **从内容生成课程**：有文章或概念，想生成课程
2. **开始交互式学习**：有课程目录，想逐章学习
3. **学完后推荐下一步**：完成部分章节，想更新进度并获得推荐
4. **从概念查找相关内容**：有概念名，想找相关学习材料
5. **不知道该学什么**：基于当前掌握度获取推荐

## 管理的 Skills

- `course-generator`：从文章/概念生成课程
- `dbs-learning`：交互式学习
- `concept-bridge`：更新进度 + 推荐

## 文件结构

```
learning-navigator/
├── SKILL.md                          # Skill 主文件
├── scripts/
│   └── list-learning-skills.py       # 发现候选 skills
└── README.md                         # 本文件
```

## 使用方式

### 方式 1：直接调用

```bash
/learning-navigator
```

然后描述你的学习需求。

### 方式 2：带上下文调用

```
我想学《乡土中国》
/learning-navigator
```

导航器会从对话中提取信息，推荐合适的 skill。

## 验证方法

### 测试脚本

```bash
python3 scripts/list-learning-skills.py
```

预期输出（3 行）：
```
concept-bridge|基于课程学习进度...|/path/to/concept-bridge
course-generator|从深度文章或概念名...|/path/to/course-generator
dbs-learning|把课题拆成连续学习文章...|/path/to/dbs-learning
```

### 测试场景

**场景 1：从文章生成课程**
```
输入："我想学《乡土中国》这篇文章"
预期：推荐 course-generator + 文章路径参数
```

**场景 2：开始学习**
```
输入："我想开始学 AI 检测原理"
预期：推荐 dbs-learning + 课程目录路径
```

**场景 3：学完推荐**
```
输入："学完前 3 章了，下一步学什么？"
预期：推荐 concept-bridge + --chapters 01,02,03
```

**场景 4：概念查找**
```
输入："我想学'对齐'相关的内容"
预期：推荐 course-generator --concept "对齐"
```

**场景 5：不知道学什么**
```
输入："根据我的掌握度推荐吧"
预期：推荐 concept-bridge（无参数，基于掌握度）
```

## 安装位置

```
/Users/housibo/Documents/dacapo-学习仓库/.skills/learning-navigator/
```

## 对标 Skill

本 skill 对标 `/dbs`（dontbesilent 商业工具箱入口），保留其核心机制：
- 场景识别（对标模式判断）
- 候选筛选（简化为 3 个固定 skills）
- 提示词生成
- 推荐理由说明

适配差异：
- 移除版本检查（本地项目）
- 移除编号执行（无需）
- 移除隐藏款目录（无需）
- 简化为 5 种固定场景
- 固定候选清单（3 个 skills）

## 制作流程

使用 `/skill-adapter` 从 `/dbs` 适配而来。

## License

MIT
