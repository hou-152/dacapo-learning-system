# navigation-logic.md - 学习导航核心逻辑

## 一、输入分析

### 用户意图分类

用户可能表达的学习意图：

1. **从内容生成课程**
   - "我想学《乡土中国》" → 提取：书名/文章
   - "把这篇文章变成课程" → 提取：文章路径
   - "围绕某个概念设计课程" → 提取：概念名

2. **开始学习**
   - "我想学这个课程" → 提取：课程路径
   - "继续学习" → 提取：课程上下文
   - "带我系统学习某主题" → 判断是否已有课程

3. **学完推荐**
   - "我学完这个课程了" → 提取：课程路径
   - "推荐我下一步学什么" → 基于掌握度
   - "更新我的学习进度" → 提取：完成章节

4. **从概念查找**
   - "这个概念有什么课程" → 提取：概念名
   - "围绕某概念找资料" → 提取：概念名

5. **不知道学什么**
   - "根据我的掌握度推荐" → 无明确输入
   - "给我推荐学习路径" → 无明确输入

### 关键信息提取

从用户输入中提取：

- **材料类型**：文章路径、课程路径、概念名、无
- **学习阶段**：准备学、正在学、学完了
- **明确意图**：生成、学习、推荐、查找
- **上下文**：当前对话中提到的路径、概念、进度

## 二、判断逻辑流程图

```
用户输入
    ↓
提取关键信息
    ↓
判断材料类型
    ├─ 有文章路径？
    │   ├─ 是 → 【场景 1】course-generator + 文章路径
    │   └─ 否 → 继续判断
    ├─ 有课程路径？
    │   ├─ 是 → 判断学习阶段
    │   │   ├─ 准备学/正在学 → 【场景 2】dbs-learning + 课程路径
    │   │   └─ 学完了 → 【场景 3】concept-bridge + 课程路径 + 章节
    │   └─ 否 → 继续判断
    ├─ 有概念名？
    │   ├─ 是 → 判断意图
    │   │   ├─ 想生成课程 → 【场景 4】course-generator --concept
    │   │   └─ 想查找内容 → 【场景 4】course-generator --concept
    │   └─ 否 → 继续判断
    └─ 什么都没有？
        └─ 是 → 【场景 5】concept-bridge（基于掌握度推荐）
```

## 三、场景判断矩阵

| 判断维度 | 场景 1 | 场景 2 | 场景 3 | 场景 4 | 场景 5 |
|---------|--------|--------|--------|--------|--------|
| **输入材料** | 文章路径/标题 | 课程路径 | 课程路径 | 概念名 | 无 |
| **学习阶段** | 准备 | 开始/进行中 | 完成 | 准备 | 不确定 |
| **用户意图** | 生成课程 | 交互学习 | 推荐下一步 | 查找/生成 | 推荐 |
| **推荐 Skill** | course-generator | dbs-learning | concept-bridge | course-generator | concept-bridge |
| **必需参数** | 文章路径 | 课程路径 | 课程路径 + 章节 | 概念名 | 无 |

## 四、具体判断规则

### 规则 1：从内容生成课程（优先级最高）

**触发条件**（满足任一即触发）：
- 提到具体文章路径（如 `/path/to/article.md`）
- 提到书名或文章标题（如"《乡土中国》"）
- 明确说"把...变成课程"
- 明确说"生成课程"或"课程大纲"

**推荐**：`course-generator`

**参数**：
- 有路径 → `/course-generator <文章路径>`
- 只有标题 → 询问文章路径

**前置检查**：
- 文章是否存在
- 文章是否 ≥ 3000 字

### 规则 2：开始交互式学习

**触发条件**（满足任一即触发）：
- 提到课程路径且意图是"学习"
- 说"继续学习"或"下一篇"
- 说"带我学"或"系统学习"

**推荐**：`dbs-learning`

**参数**：
- 有课程路径 → `/dbs-learning <课程路径>`
- 只有主题名 → 先推荐用 `course-generator` 生成课程

**前置检查**：
- 课程目录是否存在
- 是否有 `00-学习计划.md`

### 规则 3：学完后推荐下一步

**触发条件**（满足任一即触发）：
- 明确说"学完了"或"完成了"
- 说"推荐下一步"且有课程上下文
- 说"更新进度"

**推荐**：`concept-bridge`

**参数**：
- 有明确章节 → `/concept-bridge <课程路径> --chapters 01,02,03`
- 整个课程完成 → `/concept-bridge <课程路径> --all`

**必需信息**：
- 课程路径
- 已完成章节（如果没有就询问）

### 规则 4：从概念查找内容

**触发条件**（满足任一即触发）：
- 提到概念名且没有文章路径
- 说"这个概念有什么课程"
- 说"围绕某概念"

**推荐**：`course-generator --concept`

**参数**：
- `/course-generator --concept "概念名"`

**前置检查**：
- 概念是否在概念库中
- 是否有足够的相关概念（≥ 5 个）

### 规则 5：不知道学什么（兜底规则）

**触发条件**（满足任一即触发）：
- 没有明确材料和目标
- 说"推荐"但没有上下文
- 说"不知道学什么"

**推荐**：`concept-bridge`（无参数）

**说明**：
- 基于概念库掌握度推荐
- 需要用户之前至少完成过一些课程
- 如果是首次使用，引导用户选择感兴趣的主题

## 五、决策树实现伪代码

```python
def navigate(user_input, context):
    """
    导航核心逻辑
    
    Args:
        user_input: 用户输入文本
        context: 当前对话上下文
    
    Returns:
        推荐结果（skill 名称 + 参数 + 理由）
    """
    
    # 提取关键信息
    article_path = extract_article_path(user_input, context)
    course_path = extract_course_path(user_input, context)
    concept_name = extract_concept(user_input)
    learning_stage = detect_stage(user_input)  # "start", "ongoing", "completed", "unknown"
    
    # 规则 1：从内容生成课程
    if article_path or is_requesting_course_generation(user_input):
        if article_path:
            return recommend(
                skill="course-generator",
                params=[article_path],
                reason="你有明确的学习材料（文章），course-generator 会提取核心概念并生成课程"
            )
        else:
            return ask_for_article_path()
    
    # 规则 2：开始交互式学习
    if course_path and learning_stage in ["start", "ongoing"]:
        if course_exists(course_path):
            return recommend(
                skill="dbs-learning",
                params=[course_path],
                reason="你已有课程目录，dbs-learning 会逐章推进并根据反馈调整"
            )
        else:
            return error("课程目录不存在，请先用 course-generator 生成")
    
    # 规则 3：学完后推荐
    if (course_path and learning_stage == "completed") or is_requesting_recommendation(user_input):
        if course_path:
            chapters = extract_chapters(user_input, context)
            if not chapters:
                chapters = ask_for_chapters()
            
            return recommend(
                skill="concept-bridge",
                params=[course_path, f"--chapters {chapters}"],
                reason="你已完成部分章节，concept-bridge 会更新掌握度并推荐下一步"
            )
        # 没有课程上下文，走规则 5
    
    # 规则 4：从概念查找
    if concept_name and not article_path:
        if concept_exists(concept_name):
            return recommend(
                skill="course-generator",
                params=[f"--concept \"{concept_name}\""],
                reason=f"你有明确的概念名，course-generator 会从概念库查找相关概念并生成课程"
            )
        else:
            return suggest_find_article(concept_name)
    
    # 规则 5：不知道学什么（兜底）
    if has_learning_history():
        return recommend(
            skill="concept-bridge",
            params=[],
            reason="基于你当前的概念掌握度，concept-bridge 会推荐掌握度较低但有基础的学习路径"
        )
    else:
        return suggest_choose_topic()
```

## 六、输出格式规范

推荐输出必须包含：

1. **推荐 Skill**：明确的 skill 名称
2. **选择理由**：一句话说明为什么推荐这个 skill
3. **可执行提示词**：用户可以直接复制执行的命令

示例：

```markdown
推荐：`/course-generator`

选择理由：你有明确的学习材料（文章），course-generator 会提取核心概念，规划章节安排，生成完整课程框架。

可直接执行的提示词：

> 使用 `/course-generator /Users/housibo/Documents/dacapo-学习仓库/articles/乡土中国.md`。
> 从这篇文章提取核心概念，生成结构化课程目录。
> 输出包含主页、章节文件、学习计划和概念关联元数据。
```

## 七、边界情况处理

### 情况 1：多个任务

用户说："我想学 A 和 B"

**处理**：
- 让用户确定当前优先目标
- 保留其余任务供后续处理
- 每次只推荐 1 个 skill

### 情况 2：任务已完成

用户的学习任务已经完成，且没有提出新目标

**处理**：
- 直接说明已完成
- 不制造下一步
- 除非用户明确要求推荐

### 情况 3：不清楚场景

无法判断属于哪种场景

**处理**：
- 列出可能的场景
- 询问用户的真实意图
- 提供每种场景的示例

### 情况 4：前置依赖缺失

某些场景需要前置条件

**处理**：
- 场景 2（交互学习）需要先有课程 → 推荐先用 `course-generator`
- 场景 5（基于掌握度推荐）需要概念库有数据 → 推荐先完成一些课程

### 情况 5：信息不完整

推荐 skill 需要的参数缺失

**处理**：
- 只问 1 个问题
- 提供示例格式
- 说明为什么需要这个信息

## 八、质量自检清单

在输出推荐前检查：

- [ ] 场景判断准确（符合用户真实意图）
- [ ] 推荐 skill 有明确理由
- [ ] 参数完整且格式正确
- [ ] 提示词可以直接执行
- [ ] 没有遗漏必需信息的询问
- [ ] 输出符合格式规范

## 九、与其他 Skills 的协作

### 与 course-generator 的关系

- learning-navigator 只推荐，不执行生成
- 生成完成后，用户可能回来继续学习 → 推荐 `dbs-learning`

### 与 dbs-learning 的关系

- learning-navigator 判断是否需要先生成课程
- 学习过程中不介入（由 dbs-learning 处理反馈）

### 与 concept-bridge 的关系

- learning-navigator 判断用户是否完成学习
- 提取已完成章节信息传给 concept-bridge
- 推荐结果由 concept-bridge 生成，learning-navigator 不重复计算

## 十、典型对话流程示例

### 示例 1：从无到有学习新主题

```
用户：我想学《乡土中国》
导航器：[判断：有文章标题，无路径] → 询问文章路径
用户：/path/to/乡土中国.md
导航器：[规则 1] → 推荐 course-generator
用户：（执行后）现在想开始学
导航器：[规则 2] → 推荐 dbs-learning
```

### 示例 2：学习进行中

```
用户：继续学习 AI 检测原理
导航器：[判断：有课程上下文，阶段=进行中] → 推荐 dbs-learning
```

### 示例 3：学完推荐

```
用户：我学完了 AI 检测原理的前 3 章
导航器：[规则 3] → 推荐 concept-bridge + --chapters 01,02,03
```

### 示例 4：从概念开始

```
用户：我想学习"对齐"这个概念
导航器：[判断：有概念名，无文章] → 推荐 course-generator --concept
```

### 示例 5：不知道学什么

```
用户：推荐我下一步学什么
导航器：[判断：无上下文，无材料] → 推荐 concept-bridge（基于掌握度）
```
