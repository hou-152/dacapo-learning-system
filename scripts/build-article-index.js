#!/usr/bin/env node
/**
 * 构建反向索引：文章 → 概念列表
 *
 * 输入：concepts 目录下所有 .md 文件中的 articleLinks
 * 输出：.learning-progress/article-index.json
 *
 * 数据结构：
 * {
 *   "乡土中国": {
 *     "concepts": ["差序格局", "礼治秩序", ...],
 *     "author": "费孝通",
 *     "conceptCount": 10
 *   }
 * }
 */

const fs = require('fs');
const path = require('path');

const CONCEPTS_DIR = path.join(__dirname, '../concepts');
const OUTPUT_FILE = path.join(__dirname, '../.learning-progress/article-index.json');

/**
 * 递归扫描概念文件
 */
function scanConcepts(dir, results = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);

    if (entry.isDirectory()) {
      scanConcepts(fullPath, results);
    } else if (entry.name.endsWith('.md')) {
      results.push(fullPath);
    }
  }

  return results;
}

/**
 * 解析概念文件
 */
function parseConcept(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)/);

  if (!match) return null;

  const frontmatter = match[1];
  const body = match[2];

  // 提取 name
  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
  const name = nameMatch ? nameMatch[1].trim() : path.basename(filePath, '.md');

  // 提取 type
  const typeMatch = frontmatter.match(/^type:\s*(.+)$/m);
  const type = typeMatch ? typeMatch[1].trim() : 'unknown';

  // 提取 mastery
  const masteryMatch = frontmatter.match(/^  level:\s*([0-9.]+)$/m);
  const mastery = masteryMatch ? parseFloat(masteryMatch[1]) : 0.3;

  // 提取文章来源（从 body 的 ## 来源 部分）
  const articleLinks = [];
  const sourceMatch = body.match(/## 来源\s*\n((?:.*\n)*?)(?=\n##|$)/);

  if (sourceMatch) {
    const sourceText = sourceMatch[1];

    // 提取 [[链接]] 格式
    const wikiLinks = sourceText.match(/\[\[([^\]]+)\]\]/g);
    if (wikiLinks) {
      for (const link of wikiLinks) {
        const cleaned = link.replace(/[\[\]]/g, '');
        articleLinks.push(cleaned);
      }
    }
  }

  // 也尝试从 frontmatter 的 articleLinks 提取（向后兼容）
  const articleLinksMatch = frontmatter.match(/^articleLinks:\s*\n((?:  - .+\n)*)/m);
  if (articleLinksMatch) {
    const lines = articleLinksMatch[1].split('\n').filter(line => line.trim());
    for (const line of lines) {
      const linkMatch = line.match(/^\s*-\s*(.+)$/);
      if (linkMatch) {
        articleLinks.push(linkMatch[1].trim());
      }
    }
  }

  return {
    name,
    articleLinks,
    type,
    mastery,
    filePath: path.relative(process.cwd(), filePath),
  };
}

/**
 * 从文章链接中提取作者和标题
 *
 * 支持格式：
 * - "费孝通 - 乡土中国"
 * - "《乡土中国》- 费孝通"
 * - "乡土中国"
 */
function parseArticleLink(link) {
  // 去除书名号
  link = link.replace(/[《》【】]/g, '');

  // 尝试匹配 "作者 - 标题" 或 "标题 - 作者"
  const dashMatch = link.match(/^(.+?)\s*[-—]\s*(.+)$/);

  if (dashMatch) {
    const [, part1, part2] = dashMatch;

    // 判断哪个是作者（通常是人名，2-4 字）
    if (/^[一-龥]{2,4}$/.test(part1.trim())) {
      return { author: part1.trim(), title: part2.trim() };
    } else if (/^[一-龥]{2,4}$/.test(part2.trim())) {
      return { author: part2.trim(), title: part1.trim() };
    }

    // 无法判断，假设第一个是标题
    return { author: null, title: part1.trim() };
  }

  // 没有分隔符，整个就是标题
  return { author: null, title: link.trim() };
}

/**
 * 构建反向索引
 */
function buildArticleIndex() {
  console.log('📚 构建文章反向索引...\n');

  // 扫描所有概念文件
  const conceptFiles = scanConcepts(CONCEPTS_DIR);
  console.log(`找到 ${conceptFiles.length} 个概念文件\n`);

  const articleIndex = {};
  const authorIndex = {};
  let processedCount = 0;
  let skippedCount = 0;

  for (const filePath of conceptFiles) {
    const concept = parseConcept(filePath);

    if (!concept) {
      skippedCount++;
      continue;
    }

    processedCount++;

    // 处理每个文章链接
    for (const link of concept.articleLinks) {
      const { author, title } = parseArticleLink(link);

      // 初始化文章条目
      if (!articleIndex[title]) {
        articleIndex[title] = {
          title,
          author: author || '未知',
          concepts: [],
          conceptCount: 0,
        };
      }

      // 更新作者信息（优先使用明确标注的作者）
      if (author && articleIndex[title].author === '未知') {
        articleIndex[title].author = author;
      }

      // 添加概念
      articleIndex[title].concepts.push({
        name: concept.name,
        type: concept.type,
        mastery: concept.mastery,
        filePath: concept.filePath,
      });
      articleIndex[title].conceptCount++;

      // 构建作者索引
      const authorName = author || '未知';
      if (!authorIndex[authorName]) {
        authorIndex[authorName] = {
          name: authorName,
          articles: new Set(),
          conceptCount: 0,
        };
      }
      authorIndex[authorName].articles.add(title);
      authorIndex[authorName].conceptCount++;
    }
  }

  // 转换 Set 为 Array
  for (const author in authorIndex) {
    authorIndex[author].articles = Array.from(authorIndex[author].articles);
  }

  console.log(`✅ 处理了 ${processedCount} 个概念`);
  console.log(`⏭️  跳过了 ${skippedCount} 个（无 frontmatter）\n`);

  // 统计
  const articleCount = Object.keys(articleIndex).length;
  const authorCount = Object.keys(authorIndex).filter(a => a !== '未知').length;

  console.log(`📖 文章总数: ${articleCount}`);
  console.log(`👤 作者总数: ${authorCount}\n`);

  // 显示前 10 篇文章
  console.log('前 10 篇文章:');
  const topArticles = Object.values(articleIndex)
    .sort((a, b) => b.conceptCount - a.conceptCount)
    .slice(0, 10);

  for (const article of topArticles) {
    console.log(`  - ${article.title} (${article.author}) - ${article.conceptCount} 个概念`);
  }

  // 保存结果
  const outputDir = path.dirname(OUTPUT_FILE);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const output = {
    articles: articleIndex,
    authors: authorIndex,
    stats: {
      articleCount,
      authorCount,
      conceptCount: processedCount,
      generatedAt: new Date().toISOString(),
    },
  };

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2), 'utf8');
  console.log(`\n💾 已保存到: ${path.relative(process.cwd(), OUTPUT_FILE)}`);
}

// 执行
buildArticleIndex();
