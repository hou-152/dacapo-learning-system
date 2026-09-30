# GitHub 仓库统一管理清单

**更新日期**：2026-09-30  
**账号**：hou-152  
**总仓库数**：36

---

## 🎯 核心项目（按主题分类）

### 1. 学习系统（DaCapo Learning）

| 仓库 | 状态 | 最后更新 | 说明 |
|------|------|----------|------|
| **dacapo-learning-system** | public | 2026-09-30 | ✅ v1.0.0 发布 - 交互式学习系统（course-generator + dbs-learning + concept-bridge） |
| dacapo-learning-coordinator | public | 2026-09-27 | 学习协调器 |
| dacapo-learning-mvp | private | 2026-09-27 | MVP 版本 |
| learning-note-concept-skills | public | 2026-06-07 | 学习笔记概念技能 |

**建议**：
- dacapo-learning-system 为主仓库，其他可以考虑归档或合并

### 2. Skills 与 Agents

| 仓库 | 状态 | 最后更新 | 说明 |
|------|------|----------|------|
| agents-skills | private | 2026-09-30 | Agents 技能集合 |
| skill-adapter | public | 2026-09-30 | Skill 适配器 |
| qiuzhi-skills | public | 2026-09-26 | 求知技能 |
| right-size-agents | public | 2026-09-17 | Right-size agents |

### 3. 健身与生活方式

| 仓库 | 状态 | 最后更新 | 说明 |
|------|------|----------|------|
| fitness-family | public | 2026-09-26 | 健身家庭 |
| fitness-coach | public | 2026-09-11 | 健身教练 |
| lifestyle-body-recomposition | public | 2026-09-11 | 生活方式身体重组 |
| diet-plan | public | 2026-09-11 | 饮食计划 |
| carb-protein-quota-card | public | 2026-06-02 | 碳水蛋白配额卡片 |

**建议**：
- 可以整合到一个 fitness-lifestyle 仓库

### 4. 内容工程

| 仓库 | 状态 | 最后更新 | 说明 |
|------|------|----------|------|
| content-engine | public | 2026-06-17 | 内容引擎 |
| publication-engineering-workflow | public | 2026-07-02 | 出版工程工作流 |
| code-video-course | private | 2026-09-21 | 代码视频课程 |
| shuchenglin-content-assets | private | 2026-07-02 | 书城林内容资产 |

### 5. AI 与知识库

| 仓库 | 状态 | 最后更新 | 说明 |
|------|------|----------|------|
| ai-native-helpdesk | public | 2026-08-23 | AI 原生服务台 |
| ai-native-knowledge-base | public | 2026-08-21 | AI 原生知识库 |
| ai-neican | private | 2026-09-04 | AI 内参 |
| context-harness-atlas-site | public | 2026-09-03 | Context harness 图谱站点 |

### 6. 个人项目

| 仓库 | 状态 | 最后更新 | 说明 |
|------|------|----------|------|
| personal-homepage | public | 2026-09-17 | 个人主页 |
| hou-152.github.io | public | 2026-09-12 | GitHub Pages |
| entp-manual | private | 2026-09-05 | ENTP 手册 |
| entp-manual-web | public | 2026-09-05 | ENTP 手册网页版 |

### 7. 工具与实验

| 仓库 | 状态 | 最后更新 | 说明 |
|------|------|----------|------|
| chatroom-replay-archaeologist | public | 2026-09-24 | 聊天室回放考古学家 |
| zhisuoqi-135 | public | 2026-09-17 | 知所趣 135 |
| zhisuoqi-135-src | public | 2026-09-15 | 知所趣 135 源码 |
| lobster-daily | public | 2026-08-11 | Lobster 日报 |
| wechat-relationship-corpus-skill | public | 2026-06-02 | 微信关系语料库技能 |

### 8. 存档与工作空间

| 仓库 | 状态 | 最后更新 | 说明 |
|------|------|----------|------|
| meta-builder-2.0 | private | 2026-09-29 | Meta builder 2.0 |
| liaotian-workspace | private | 2026-09-04 | 聊天工作空间 |
| wechat-thought-incubation-agent | private | 2026-07-02 | 微信思想孵化代理 |
| logseq-all | private | 2026-07-02 | Logseq 全部 |
| soul-flight | private | 2026-06-09 | Soul flight |
| jiaoliu-chat-export-2026-06-02-to-2026-06-23 | public | 2026-07-02 | 交流聊天导出 |
| hou-152 | private | 2026-05-18 | 个人仓库 |

---

## 📊 统计

### 按可见性
- **Public**: 23 个
- **Private**: 13 个

### 按活跃度
- **近 7 天活跃**: 3 个
- **近 30 天活跃**: 7 个
- **超过 3 个月未更新**: 26 个

---

## 🔄 整合建议

### 高优先级整合

1. **学习系统整合**
   - 主仓库：dacapo-learning-system (v1.0.0)
   - 考虑归档：dacapo-learning-coordinator, dacapo-learning-mvp
   - 行动：在主仓库 README 中说明其他仓库的归档状态

2. **健身系列整合**
   - 创建：fitness-lifestyle（统一仓库）
   - 整合：fitness-family, fitness-coach, lifestyle-body-recomposition, diet-plan
   - 保留：carb-protein-quota-card（独立工具）

3. **Skills 系列整合**
   - 主仓库：agents-skills (private)
   - 考虑合并：qiuzhi-skills, skill-adapter
   - 或者创建：awesome-skills（公开的 skills 集合）

### 中优先级整合

4. **内容工程整合**
   - 创建：content-engineering（统一仓库）
   - 整合：content-engine, publication-engineering-workflow

5. **AI 工具整合**
   - 创建：ai-toolkit
   - 整合：ai-native-helpdesk, ai-native-knowledge-base

### 归档候选

需要评估是否仍在使用，考虑归档：
- zhisuoqi-135 系列（2 个仓库）
- jiaoliu-chat-export-*（存档数据）
- 超过 6 个月未更新的实验性项目

---

## 📝 下一步行动

### 立即执行

1. **为主要项目添加 Release**
   - [ ] dacapo-learning-system ✅ v1.0.0 已发布
   - [ ] skill-adapter
   - [ ] fitness-family
   - [ ] ai-native-helpdesk

2. **创建统一 README**
   - [ ] 在 hou-152 profile 仓库添加项目索引
   - [ ] 说明各仓库的关系和状态

3. **归档决策**
   - [ ] 评估 3 个月以上未更新的项目
   - [ ] 标记 deprecated 或 archived

### 持续维护

4. **定期清理**
   - 每季度评估一次仓库活跃度
   - 归档不再维护的项目
   - 更新主索引文档

5. **版本管理规范**
   - 主要项目使用语义化版本（v1.0.0）
   - 定期打 tag 和创建 release
   - 维护 CHANGELOG.md

---

## 🔗 快速链接

- **Profile**: https://github.com/hou-152
- **最新项目**: https://github.com/hou-152/dacapo-learning-system
- **Stars**: (待统计)
- **Followers**: (待统计)

---

**维护者**: hou-152  
**文档版本**: 1.0  
**下次更新**: 2027-01-01
