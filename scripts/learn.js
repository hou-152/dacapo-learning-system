#!/usr/bin/env node
/**
 * 交互式学习引擎（支持文章入口）
 *
 * 用法：
 *   node scripts/learn.js <概念名>              # 学单个概念
 *   node scripts/learn.js --article <文章路径>  # 学一篇文章
 *
 * 流程：
 * 1. 识别输入类型（概念 or 文章）
 * 2. 文章模式：加载文章的所有概念 → 按前置关系排序 → 逐个学习
 * 3. 概念模式：直接学习单个概念
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { execSync } = require('child_process');

const CONCEPTS_DIR = path.join(__dirname, '../concepts');
const ARTICLE_INDEX_FILE = path.join(__dirname, '../.learning-progress/article-index.json');

/**
 * 加载文章索引
 */
function loadArticleIndex() {
  if (!fs.existsSync(ARTICLE_INDEX_FILE)) {
    console.log('⚠️  文章索引不存在，正在构建...');
    execSync('node scripts/build-article-index.js', { stdio: 'inherit' });
  }

  const data = JSON.parse(fs.readFileSync(ARTICLE_INDEX_FILE, 'utf8'));
  return data.articles;
}

/**
 * 查找概念文件
 */
function findConceptFile(conceptName) {
  function searchDir(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        const result = searchDir(fullPath);
        if (result) return result;
      } else if (entry.name === `${conceptName}.md`) {
        return fullPath;
      }
    }
    return null;
  }
  return searchDir(CONCEPTS_DIR);
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

  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
  const masteryMatch = frontmatter.match(/^  level:\s*([0-9.]+)$/m);

  // 提取定义
  const definitionMatch = body.match(/## 定义\s*\n([\s\S]*?)(?=\n##|$)/);
  const definition = definitionMatch ? definitionMatch[1].trim() : '';

  // 提取前置概念
  const prerequisitesMatch = frontmatter.match(/^prerequisites:\s*\[([^\]]*)\]/m);
  const prerequisites = prerequisitesMatch
    ? prerequisitesMatch[1].split(',').map(p => p.trim().replace(/['"]/g, '')).filter(p => p)
    : [];

  return {
    name: nameMatch ? nameMatch[1].trim() : path.basename(filePath, '.md'),
    currentMastery: masteryMatch ? parseFloat(masteryMatch[1]) : 0.3,
    definition: definition,
    prerequisites: prerequisites,
    fullContent: content,
    filePath: filePath,
  };
}

/**
 * 提取关键词
 */
function extractKeywords(definition) {
  const words = definition.match(/[一-龥]{2,4}/g) || [];
  return [...new Set(words)].slice(0, 10);
}

/**
 * 评估答案
 */
function evaluateAnswer(answer, keywords, minLength = 20) {
  let score = 0;
  const reasons = [];

  // 规则 1: 字数
  if (answer.length >= minLength) {
    const lengthScore = Math.min(3, Math.floor(answer.length / 30));
    score += lengthScore;
    reasons.push(`字数 ${answer.length} 字`);
  } else {
    reasons.push(`字数不足（${answer.length} < ${minLength}）`);
  }

  // 规则 2: 关键词匹配
  const matchedKeywords = keywords.filter(kw => answer.includes(kw));
  const keywordScore = Math.min(4, matchedKeywords.length);
  score += keywordScore;
  if (matchedKeywords.length > 0) {
    reasons.push(`匹配关键词: ${matchedKeywords.join(', ')}`);
  }

  // 规则 3: 有例子
  const hasExample = answer.includes('比如') || answer.includes('例如') ||
                     answer.includes('举例') || answer.includes('像');
  if (hasExample) {
    score += 3;
    reasons.push('包含例子');
  }

  return { score: Math.min(10, score), reasons };
}

/**
 * 计算最终掌握度
 */
function calculateMastery(q1Score, q2Score) {
  const avgScore = (q1Score + q2Score) / 2;
  const mastery = Math.round(avgScore / 10 * 100) / 100;
  return mastery;
}

/**
 * 更新概念文件的 mastery
 */
function updateMastery(filePath, newMastery) {
  let content = fs.readFileSync(filePath, 'utf8');

  content = content.replace(
    /^  level:\s*[0-9.]+$/m,
    `  level: ${newMastery}`
  );

  const rawScore = Math.round(newMastery * 100);
  content = content.replace(
    /^  rawScore:\s*[0-9]+$/m,
    `  rawScore: ${rawScore}`
  );

  const now = new Date().toISOString().split('T')[0];
  content = content.replace(
    /^updated:\s*.+$/m,
    `updated: ${now}`
  );

  fs.writeFileSync(filePath, content, 'utf8');
}

/**
 * 问问题
 */
async function askQuestion(rl, question) {
  return new Promise((resolve) => {
    rl.question(`\n${question}\n> `, (answer) => {
      resolve(answer.trim());
    });
  });
}

/**
 * 学习单个概念
 */
async function learnConcept(rl, conceptName) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`📖 学习概念: ${conceptName}`);
  console.log('='.repeat(60));

  const filePath = findConceptFile(conceptName);

  if (!filePath) {
    console.log(`❌ 找不到概念: ${conceptName}`);
    return null;
  }

  const concept = parseConcept(filePath);
  console.log(`\n当前掌握度: ${concept.currentMastery}`);

  const keywords = extractKeywords(concept.definition);

  // 准备问题
  const questions = [
    `📝 第 1 题: 用你自己的话，${concept.name}是什么？`,
    `📝 第 2 题: 举一个现实例子说明${concept.name}`,
  ];

  // 问题 1
  const answer1 = await askQuestion(rl, questions[0]);
  const eval1 = evaluateAnswer(answer1, keywords, 20);
  console.log(`\n✅ 评分: ${eval1.score}/10`);
  console.log(`   ${eval1.reasons.join(', ')}`);

  // 问题 2
  const answer2 = await askQuestion(rl, questions[1]);
  const eval2 = evaluateAnswer(answer2, keywords, 30);
  console.log(`\n✅ 评分: ${eval2.score}/10`);
  console.log(`   ${eval2.reasons.join(', ')}`);

  // 计算最终掌握度
  console.log(`\n${'='.repeat(60)}`);
  console.log('🎯 评估完成');
  console.log(`   第 1 题: ${eval1.score}/10`);
  console.log(`   第 2 题: ${eval2.score}/10`);

  const newMastery = calculateMastery(eval1.score, eval2.score);
  const oldMastery = concept.currentMastery;
  const delta = newMastery - oldMastery;
  const deltaStr = delta >= 0 ? `+${delta.toFixed(2)}` : delta.toFixed(2);

  console.log(`\n   综合掌握度: ${newMastery} (${deltaStr})`);

  // 更新文件
  console.log(`\n💾 更新 ${path.relative(process.cwd(), filePath)}...`);
  updateMastery(filePath, newMastery);
  console.log('✅ 已保存');

  return { concept: concept.name, newMastery, delta };
}

/**
 * 按前置关系排序概念（拓扑排序）
 */
function topologicalSort(concepts) {
  const conceptMap = new Map(concepts.map(c => [c.name, c]));
  const sorted = [];
  const visited = new Set();
  const visiting = new Set();

  function visit(conceptName) {
    if (visited.has(conceptName)) return;
    if (visiting.has(conceptName)) {
      // 循环依赖，跳过
      return;
    }

    visiting.add(conceptName);

    const concept = conceptMap.get(conceptName);
    if (concept) {
      for (const prereq of concept.prerequisites) {
        if (conceptMap.has(prereq)) {
          visit(prereq);
        }
      }
    }

    visiting.delete(conceptName);
    visited.add(conceptName);
    if (concept) {
      sorted.push(concept);
    }
  }

  for (const concept of concepts) {
    visit(concept.name);
  }

  return sorted;
}

/**
 * 学习一篇文章
 */
async function learnArticle(rl, articlePath) {
  console.log('🎓 交互式学习引擎 - 文章模式\n');

  // 加载文章索引
  const articles = loadArticleIndex();

  // 查找文章
  const article = articles[articlePath];

  if (!article) {
    console.log(`❌ 找不到文章: ${articlePath}`);
    console.log('\n可用文章:');
    for (const title of Object.keys(articles).slice(0, 10)) {
      console.log(`  - ${title}`);
    }
    return;
  }

  console.log(`📚 文章: ${article.title}`);
  console.log(`👤 作者: ${article.author}`);
  console.log(`📖 包含 ${article.conceptCount} 个概念\n`);

  // 加载概念详情
  const concepts = [];
  for (const conceptInfo of article.concepts) {
    const filePath = findConceptFile(conceptInfo.name);
    if (filePath) {
      const concept = parseConcept(filePath);
      if (concept) {
        concepts.push(concept);
      }
    }
  }

  if (concepts.length === 0) {
    console.log('❌ 无法加载概念文件');
    return;
  }

  // 按前置关系排序
  const sortedConcepts = topologicalSort(concepts);

  console.log('📋 学习路径（按前置关系排序）:');
  sortedConcepts.forEach((c, i) => {
    const status = c.currentMastery >= 0.6 ? '✅' : '⏳';
    console.log(`  ${i + 1}. ${status} ${c.name} (掌握度: ${c.currentMastery})`);
  });

  console.log('\n准备开始学习...');
  const confirm = await askQuestion(rl, '按 Enter 继续，输入 q 退出');

  if (confirm.toLowerCase() === 'q') {
    console.log('👋 已取消');
    return;
  }

  // 逐个学习
  const results = [];

  for (let i = 0; i < sortedConcepts.length; i++) {
    const concept = sortedConcepts[i];

    // 跳过已掌握的概念
    if (concept.currentMastery >= 0.6) {
      console.log(`\n⏭️  跳过 ${concept.name}（已掌握）`);
      continue;
    }

    const result = await learnConcept(rl, concept.name);
    if (result) {
      results.push(result);
    }

    // 询问是否继续
    if (i < sortedConcepts.length - 1) {
      const continueAnswer = await askQuestion(rl, '\n按 Enter 继续下一个，输入 q 退出');
      if (continueAnswer.toLowerCase() === 'q') {
        console.log('\n👋 暂停学习');
        break;
      }
    }
  }

  // 总结
  console.log(`\n${'='.repeat(60)}`);
  console.log('🎉 学习完成！');
  console.log(`\n📊 本次学习了 ${results.length} 个概念:`);

  for (const result of results) {
    const emoji = result.delta > 0 ? '📈' : result.delta < 0 ? '📉' : '➡️';
    const deltaStr = result.delta >= 0 ? `+${result.delta.toFixed(2)}` : result.delta.toFixed(2);
    console.log(`  ${emoji} ${result.concept}: ${result.newMastery} (${deltaStr})`);
  }

  // 重新计算相关度和推荐
  console.log('\n🔄 重新计算概念网络...');
  execSync('node scripts/calculate-relevance.js', { stdio: 'inherit' });

  console.log('\n🚀 推荐下一步学习:\n');
  execSync('node scripts/recommend.js path', { stdio: 'inherit' });
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('用法:');
    console.log('  node scripts/learn.js <概念名>              # 学单个概念');
    console.log('  node scripts/learn.js --article <文章路径>  # 学一篇文章');
    console.log('\n示例:');
    console.log('  node scripts/learn.js 差序格局');
    console.log('  node scripts/learn.js --article "社会学七书共读/03.md"');
    process.exit(1);
  }

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  try {
    if (args[0] === '--article') {
      if (args.length < 2) {
        console.log('❌ 缺少文章路径');
        process.exit(1);
      }
      await learnArticle(rl, args[1]);
    } else {
      // 概念模式
      console.log('🎓 交互式学习引擎\n');
      const result = await learnConcept(rl, args[0]);

      if (result) {
        // 重新计算相关度
        console.log('\n🔄 重新计算概念网络...');
        execSync('node scripts/calculate-relevance.js', { stdio: 'inherit' });

        // 推荐下一步
        console.log('\n🚀 推荐下一步学习:\n');
        execSync('node scripts/recommend.js path', { stdio: 'inherit' });

        console.log(`\n${'='.repeat(60)}`);
        console.log('🎉 学习完成！');

        if (result.delta > 0) {
          console.log(`\n💪 掌握度提升了 ${(result.delta * 100).toFixed(0)}%！`);
        }
      }
    }
  } finally {
    rl.close();
  }
}

main().catch(err => {
  console.error('❌ 错误:', err.message);
  process.exit(1);
});
