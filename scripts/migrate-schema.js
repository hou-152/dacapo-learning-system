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
 * 解析 markdown
 */
function parseFrontmatter(content) {
  content = content.replace(/\r\n/g, '\n');
  const match = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!match) return null;

  const frontmatterRaw = match[1];
  const body = match[2];

  // 手动提取关键字段
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
    },
    body
  };
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

  yaml += `prerequisites: []\n`;
  yaml += `derivedConcepts: []\n`;
  yaml += `relatedConcepts: []\n`;
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
    throw new Error('Cannot parse frontmatter');
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

  const files = fs.readdirSync(CONCEPTS_DIR)
    .filter(f => f.endsWith('.md') && f !== 'INDEX.md')
    .map(f => path.join(CONCEPTS_DIR, f));

  stats.total = files.length;
  console.log(`找到 ${stats.total} 个概念文件\n`);

  const results = [];

  for (const filePath of files) {
    try {
      const result = migrateConcept(filePath);
      results.push(result);

      if (!DRY_RUN) {
        fs.writeFileSync(filePath, result.newContent, 'utf8');
      }

      stats.success++;
      console.log(`✅ ${path.basename(filePath)}`);
    } catch (e) {
      stats.errors.push({ file: filePath, error: e.message });
      console.log(`❌ ${path.basename(filePath)}: ${e.message}`);
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
      console.log(`${path.basename(file)}: ${error}`);
    });
  }

  const report = {
    timestamp: new Date().toISOString(),
    mode: DRY_RUN ? 'dry-run' : 'live',
    stats,
    samples: results.slice(0, 2).map(r => ({
      file: path.basename(r.filePath),
      oldMastery: r.old.mastery,
      oldTags: r.old.tags,
    })),
  };

  const reportPath = path.join(__dirname, `../MIGRATION_REPORT_${Date.now()}.json`);
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`\n📄 迁移报告: ${reportPath}`);

  if (DRY_RUN) {
    console.log('\n💡 这是 DRY RUN，未实际修改');
    console.log('   移除 --dry-run 执行真实迁移');
  } else {
    console.log('\n✅ 迁移完成！备份: concepts.backup.*');
  }
}

runMigration();
