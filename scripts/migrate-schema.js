#!/usr/bin/env node
/**
 * Schema 迁移脚本（简化版，直接正则提取）
 */

const fs = require('fs');
const path = require('path');

const CONCEPTS_DIR = path.join(__dirname, '../concepts');
const DRY_RUN = process.argv.includes('--dry-run');

const stats = { total: 0, success: 0, skipped: 0, errors: [] };

/**
 * 提取 frontmatter 字段（正则方式）
 */
function extractField(frontmatter, fieldName) {
  const regex = new RegExp(`^${fieldName}:\\s*(.+)$`, 'm');
  const match = frontmatter.match(regex);
  return match ? match[1].trim() : null;
}

/**
 * 从 Markdown body 提取 wikilink（[[概念名]]）
 */
function extractWikilinks(text) {
  const matches = text.match(/\[\[([^\]]+)\]\]/g);
  if (!matches) return [];
  return matches.map(m => m.slice(2, -2).trim());
}

/**
 * 检测是否为旧格式（有 ## 相关概念 等 Markdown 章节）
 */
function isOldFormat(body) {
  return /^## (相关概念|出现文章|前置概念)/m.test(body);
}

/**
 * 解析旧格式（Markdown 章节）
 */
function parseOldFormat(frontmatterRaw, body) {
  const tags = extractField(frontmatterRaw, 'tags');
  const firstAppearance = extractField(frontmatterRaw, 'firstAppearance');

  // 从 body 提取 ## 相关概念（修正：用 (?:.*\n)* 明确匹配多行）
  const relatedMatch = body.match(/## 相关概念\n((?:.*\n)*?)(?=\n##|$)/);
  const relatedConcepts = relatedMatch ? extractWikilinks(relatedMatch[1]) : [];

  // 从 body 提取 ## 前置概念
  const prereqMatch = body.match(/## 前置概念\n((?:.*\n)*?)(?=\n##|$)/);
  const prerequisites = prereqMatch ? extractWikilinks(prereqMatch[1]) : [];

  // 从 body 提取 ## 出现文章（作为额外来源）
  const articlesMatch = body.match(/## 出现文章\n((?:.*\n)*?)(?=\n##|$)/);
  const articleLinks = articlesMatch ? extractWikilinks(articlesMatch[1]) : [];

  return {
    frontmatter: {
      tags: tags ? tags.replace(/"/g, '') : null,
      firstAppearance: firstAppearance ? firstAppearance.replace(/"/g, '') : null,
      mastery: 0.3, // 旧格式默认初始掌握度
      lastStudied: null,
      studyCount: 0,
      relatedConcepts,
      prerequisites,
      articleLinks,
    },
    body
  };
}

/**
 * 解析新格式（已有 mastery、studyCount 等字段）
 */
function parseNewFormat(frontmatterRaw, body) {
  const tags = extractField(frontmatterRaw, 'tags');
  const firstAppearance = extractField(frontmatterRaw, 'firstAppearance');
  const mastery = extractField(frontmatterRaw, 'mastery');
  const lastStudied = extractField(frontmatterRaw, 'lastStudied');
  const studyCount = extractField(frontmatterRaw, 'studyCount');

  return {
    frontmatter: {
      tags: tags ? tags.replace(/"/g, '') : null,
      firstAppearance: firstAppearance ? firstAppearance.replace(/"/g, '') : null,
      mastery: mastery ? parseFloat(mastery) : 0,
      lastStudied: lastStudied ? lastStudied.replace(/"/g, '') : null,
      studyCount: studyCount ? parseInt(studyCount) : 0,
      relatedConcepts: [],
      prerequisites: [],
      articleLinks: [],
    },
    body
  };
}

/**
 * 解析 markdown（自动检测格式）
 */
function parseFrontmatter(content) {
  content = content.replace(/\r\n/g, '\n');
  const match = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!match) return null;

  const frontmatterRaw = match[1];
  const body = match[2];

  // 检测格式并分别处理
  if (isOldFormat(body)) {
    return parseOldFormat(frontmatterRaw, body);
  } else {
    return parseNewFormat(frontmatterRaw, body);
  }
}

/**
 * 生成新 frontmatter（手工拼接）
 */
function generateFrontmatter(name, old) {
  const today = new Date().toISOString().split('T')[0];
  const tags = old.tags ? old.tags.split(',').map(t => t.trim()) : [];
  const type = tags.some(t => t.includes('theory')) ? 'theory' : 'concept';

  let yaml = '';
  yaml += `name: ${name}\n`;
  yaml += `type: ${type}\n`;
  yaml += `tags:\n`;
  tags.forEach(tag => yaml += `  - ${tag}\n`);
  yaml += `created: ${today}\n`;
  yaml += `updated: ${today}\n`;
  yaml += `\n`;

  yaml += `sources:\n`;
  if (old.firstAppearance) {
    yaml += `  - link: "${old.firstAppearance}"\n`;
  }
  // 从 body 提取的文章链接也加入 sources
  if (old.articleLinks && old.articleLinks.length > 0) {
    old.articleLinks.forEach(link => {
      if (link !== old.firstAppearance) { // 避免重复
        yaml += `  - link: "[[${link}]]"\n`;
      }
    });
  }
  yaml += `\n`;

  yaml += `mastery:\n`;
  yaml += `  level: ${old.mastery || 0}\n`;
  yaml += `  rawScore: ${Math.round((old.mastery || 0) * 100)}\n`;
  yaml += `  decay:\n`;
  yaml += `    lastReviewed: ${old.lastStudied || today}\n`;
  yaml += `    halfLife: 30\n`;
  yaml += `\n`;

  yaml += `masteryHistory: []\n`;
  yaml += `\n`;

  // 从 body 提取的前置概念
  yaml += `prerequisites: [${old.prerequisites.map(p => `"${p}"`).join(', ')}]\n`;
  yaml += `derivedConcepts: []\n`;
  // 从 body 提取的相关概念
  yaml += `relatedConcepts: [${old.relatedConcepts.map(c => `"${c}"`).join(', ')}]\n`;
  yaml += `\n`;

  yaml += `patterns: []\n`;
  yaml += `\n`;

  yaml += `theoryGrounding: null\n`;
  yaml += `\n`;

  yaml += `studyCount: ${old.studyCount || 0}\n`;
  yaml += `lastStudied: ${old.lastStudied || 'null'}\n`;
  yaml += `studySessions: []\n`;

  return yaml;
}

/**
 * 迁移单个文件
 */
function migrateConcept(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const parsed = parseFrontmatter(content);

  if (!parsed) {
    return null; // 跳过无 frontmatter 文件
  }

  const { frontmatter: old, body } = parsed;
  const name = path.basename(filePath, '.md');

  const newFrontmatter = generateFrontmatter(name, old);
  const newContent = `---\n${newFrontmatter}---\n${body}`;

  return { filePath, newContent, old };
}

/**
 * 执行迁移
 */
function runMigration() {
  console.log('🚀 开始迁移 Schema...\n');
  console.log(`模式: ${DRY_RUN ? 'DRY RUN（不写入）' : 'LIVE（写入）'}\n`);

  // 扫描 concepts/ 及其子目录
  const files = [];
  function scanDir(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        scanDir(fullPath);
      } else if (entry.name.endsWith('.md') && entry.name !== 'INDEX.md') {
        files.push(fullPath);
      }
    }
  }
  scanDir(CONCEPTS_DIR);

  stats.total = files.length;
  console.log(`找到 ${stats.total} 个概念文件\n`);

  const results = [];

  for (const filePath of files) {
    try {
      const result = migrateConcept(filePath);

      if (!result) {
        stats.skipped++;
        const relPath = path.relative(CONCEPTS_DIR, filePath);
        console.log(`⊘ ${relPath} (无 frontmatter，跳过)`);
        continue;
      }

      results.push(result);

      if (!DRY_RUN) {
        fs.writeFileSync(filePath, result.newContent, 'utf8');
      }

      stats.success++;
      const relPath = path.relative(CONCEPTS_DIR, filePath);
      console.log(`✅ ${relPath}`);
    } catch (e) {
      stats.errors.push({ file: filePath, error: e.message });
      const relPath = path.relative(CONCEPTS_DIR, filePath);
      console.log(`❌ ${relPath}: ${e.message}`);
    }
  }

  console.log('\n=== 迁移统计 ===');
  console.log(`总计: ${stats.total}`);
  console.log(`成功: ${stats.success}`);
  console.log(`跳过: ${stats.skipped}`);
  console.log(`错误: ${stats.errors.length}`);

  if (stats.errors.length > 0) {
    console.log('\n=== 错误详情 ===');
    stats.errors.forEach(({ file, error }) => {
      console.log(`${path.relative(CONCEPTS_DIR, file)}: ${error}`);
    });
  }

  const report = {
    timestamp: new Date().toISOString(),
    mode: DRY_RUN ? 'dry-run' : 'live',
    stats,
    samples: results.slice(0, 3).map(r => ({
      file: path.relative(CONCEPTS_DIR, r.filePath),
      oldMastery: r.old.mastery,
      oldTags: r.old.tags,
      extractedRelated: r.old.relatedConcepts ? r.old.relatedConcepts.length : 0,
      extractedPrereq: r.old.prerequisites ? r.old.prerequisites.length : 0,
    })),
  };

  const reportPath = path.join(__dirname, `../MIGRATION_REPORT_${Date.now()}.json`);
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`\n📄 迁移报告: ${reportPath}`);

  if (DRY_RUN) {
    console.log('\n💡 这是 DRY RUN，未实际修改');
    console.log('   移除 --dry-run 执行真实迁移');
  } else {
    console.log('\n✅ 迁移完成！');
  }
}

runMigration();
