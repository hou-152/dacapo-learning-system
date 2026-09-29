#!/usr/bin/env node
/**
 * 自动标注概念前置关系
 *
 * 策略：
 * 1. 读取概念的定义和内容
 * 2. 用启发式规则判断前置关系
 * 3. 生成 prerequisites 建议
 * 4. 输出 JSON 供人工 review
 */

const fs = require('fs');
const path = require('path');

const CONCEPTS_DIR = path.join(__dirname, '../concepts');

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
  const typeMatch = frontmatter.match(/^type:\s*(.+)$/m);

  // 提取 relatedConcepts
  const relatedMatch = frontmatter.match(/^relatedConcepts:\s*\[([^\]]*)\]/m);
  const relatedConcepts = [];
  if (relatedMatch && relatedMatch[1].trim()) {
    relatedConcepts.push(...relatedMatch[1].split(',').map(s => s.trim().replace(/"/g, '')));
  }

  // 提取现有 prerequisites
  const prereqMatch = frontmatter.match(/^prerequisites:\s*\[([^\]]*)\]/m);
  const prerequisites = [];
  if (prereqMatch && prereqMatch[1].trim()) {
    prerequisites.push(...prereqMatch[1].split(',').map(s => s.trim().replace(/"/g, '')));
  }

  // 提取定义（## 定义 章节）
  const definitionMatch = body.match(/## 定义\s*\n([\s\S]*?)(?=\n##|$)/);
  const definition = definitionMatch ? definitionMatch[1].trim() : '';

  return {
    id: path.basename(filePath, '.md'),
    name: nameMatch ? nameMatch[1].trim() : path.basename(filePath, '.md'),
    type: typeMatch ? typeMatch[1].trim() : 'concept',
    relatedConcepts: relatedConcepts,
    prerequisites: prerequisites,
    definition: definition,
    body: body,
  };
}

/**
 * 加载所有概念
 */
function loadConcepts() {
  const concepts = new Map();

  function scanDir(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        scanDir(fullPath);
      } else if (entry.name.endsWith('.md') && entry.name !== 'INDEX.md') {
        const concept = parseConcept(fullPath);
        if (concept) {
          concepts.set(concept.id, concept);
        }
      }
    }
  }

  scanDir(CONCEPTS_DIR);
  return concepts;
}

/**
 * 启发式规则：判断概念 A 是否需要先懂概念 B
 *
 * 规则：
 * 1. A 的定义中明确提到 B
 * 2. A 的定义更复杂（字数更多）
 * 3. B 是基础概念（type: theory 或被很多概念引用）
 * 4. A 和 B 有直接关联（relatedConcepts）
 */
function inferPrerequisite(conceptA, conceptB, graph) {
  let score = 0;
  const reasons = [];

  // 规则 1: A 的定义明确提到 B
  if (conceptA.definition.includes(conceptB.name) || conceptA.body.includes(conceptB.name)) {
    score += 3;
    reasons.push('定义中引用');
  }

  // 规则 2: A 更复杂（定义字数比）
  const complexityRatio = conceptA.definition.length / (conceptB.definition.length + 1);
  if (complexityRatio > 1.5) {
    score += 1;
    reasons.push('A 定义更复杂');
  }

  // 规则 3: B 是基础概念（被引用次数）
  let inDegreeB = 0;
  graph.forEach(concept => {
    if (concept.relatedConcepts.includes(conceptB.id)) {
      inDegreeB++;
    }
  });

  if (inDegreeB >= 3) {
    score += 2;
    reasons.push(`B 被 ${inDegreeB} 个概念引用（基础概念）`);
  }

  // 规则 4: A 和 B 有关联
  if (conceptA.relatedConcepts.includes(conceptB.id)) {
    score += 1;
    reasons.push('有直接关联');
  }

  // 规则 5: B 是 theory 类型
  if (conceptB.type === 'theory') {
    score += 1;
    reasons.push('B 是理论');
  }

  // 规则 6: 特定领域规则（社会学）
  const sociologyFoundations = ['差序格局', '礼治秩序', '社会学想象力'];
  if (sociologyFoundations.includes(conceptB.name) && conceptA.body.includes('社会')) {
    score += 1;
    reasons.push('B 是社会学基础概念');
  }

  // 规则 7: harness 工程基础
  const harnessFoundations = ['harness', 'context-engineering'];
  if (harnessFoundations.includes(conceptB.id) &&
      (conceptA.body.includes('harness') || conceptA.body.includes('agent'))) {
    score += 2;
    reasons.push('B 是 harness 工程基础');
  }

  return { score, reasons };
}

/**
 * 为每个概念推荐前置概念
 */
function recommendPrerequisites(graph, threshold = 3) {
  const recommendations = new Map();

  graph.forEach((conceptA, idA) => {
    const candidates = [];

    graph.forEach((conceptB, idB) => {
      // 跳过自己
      if (idA === idB) return;

      // 跳过已有的前置
      if (conceptA.prerequisites.includes(idB)) return;

      const { score, reasons } = inferPrerequisite(conceptA, conceptB, graph);

      if (score >= threshold) {
        candidates.push({
          prerequisite: idB,
          name: conceptB.name,
          score: score,
          reasons: reasons,
        });
      }
    });

    // 降序排序
    candidates.sort((a, b) => b.score - a.score);

    if (candidates.length > 0) {
      recommendations.set(idA, {
        concept: conceptA.name,
        currentPrerequisites: conceptA.prerequisites,
        recommended: candidates.slice(0, 3),  // Top 3
      });
    }
  });

  return recommendations;
}

/**
 * 主函数
 */
function main() {
  console.log('🔍 自动标注概念前置关系...\n');

  // 加载概念
  console.log('📖 加载概念...');
  const graph = loadConcepts();
  console.log(`✅ 加载完成: ${graph.size} 个概念\n`);

  // 推荐前置关系
  console.log('🤖 推断前置关系...');
  const recommendations = recommendPrerequisites(graph);
  console.log(`✅ 找到 ${recommendations.size} 个概念需要标注\n`);

  // 输出结果
  console.log('=== 推荐结果 ===\n');

  const output = [];

  recommendations.forEach((rec, conceptId) => {
    console.log(`📌 ${rec.concept}`);
    console.log(`   当前前置: ${rec.currentPrerequisites.length > 0 ? rec.currentPrerequisites.join(', ') : '无'}`);
    console.log(`   推荐添加:\n`);

    rec.recommended.forEach((r, i) => {
      console.log(`   ${i + 1}. ${r.name} (分数: ${r.score})`);
      console.log(`      原因: ${r.reasons.join(', ')}`);
    });

    console.log('');

    output.push({
      conceptId: conceptId,
      concept: rec.concept,
      currentPrerequisites: rec.currentPrerequisites,
      recommended: rec.recommended.map(r => ({
        id: r.prerequisite,
        name: r.name,
        score: r.score,
        reasons: r.reasons,
      })),
    });
  });

  // 保存到 JSON
  const outputPath = path.join(__dirname, '../.learning-progress/prerequisites-recommendations.json');
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));

  console.log(`\n📄 完整结果已保存: ${outputPath}`);
  console.log(`\n💡 下一步: 人工 review 后运行 apply-prerequisites.js 应用`);
}

main();
