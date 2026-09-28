# 清理方案（激进版）

## 一、直接删除（移到 .trash/）

### 空目录（0B）
```bash
mv 02-课程真源/ .trash/2026-09-28_02-课程真源/
mv 03-知识入口与概念/ .trash/2026-09-28_03-知识入口与概念/
```

### 测试目录（12K-88K，临时测试内容）
```bash
mv AI实战营-从Demo到产品/ .trash/2026-09-28_AI实战营-从Demo到产品/
mv AI实战营-前沿速递/ .trash/2026-09-28_AI实战营-前沿速递/
mv 泛化测试-A类-陌生领域/ .trash/2026-09-28_泛化测试-A类-陌生领域/
mv 泛化测试-B类-低结构化/ .trash/2026-09-28_泛化测试-B类-低结构化/
mv 泛化测试-C类-多模态/ .trash/2026-09-28_泛化测试-C类-多模态/
mv 泛化测试-直播稿/ .trash/2026-09-28_泛化测试-直播稿/
```

### 小碎片目录（16K-28K）
```bash
mv articles/ .trash/2026-09-28_articles/
mv raw-sources/ .trash/2026-09-28_raw-sources/
mv graph/ .trash/2026-09-28_graph/
```

### Logseq 遗留目录
```bash
cd courses/
mv backups/ ../.trash/2026-09-28_courses-backups/
mv "backups 2/" ../.trash/2026-09-28_courses-backups-2/
mv journals/ ../.trash/2026-09-28_courses-journals/
mv logseq/ ../.trash/2026-09-28_courses-logseq/
mv pages/ ../.trash/2026-09-28_courses-pages/
```

## 二、清理后的结构

```
dacapo-学习仓库/
├── courses/          # 86M - 47 个课程（干净）
├── concepts/         # 240K - 47 个概念
├── scripts/          # 300K - Python 工具
├── user-feedback/    # 2.8M - 用户数据
└── .trash/           # 所有删除内容（30 天后清理）
```

**简单、清晰、可恢复**。

## 三、执行？

这个方案：
- ✅ 删除所有空目录和测试碎片
- ✅ 只保留 4 个核心目录
- ✅ 所有删除内容在 .trash/ 中保留 30 天
- ✅ 可以一次性执行完

**同意就执行，不同意就调整。**
