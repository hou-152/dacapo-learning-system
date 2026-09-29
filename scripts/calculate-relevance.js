#!/usr/bin/env node
/**
 * Phase 2: 四信号相关度计算引擎
 *
 * 根据 PHASE2-SPEC.md 实现：
 * - sourceOverlap (×4.0): Jaccard 相似度
 * - directLink (×3.0): 双向 1.0, 单向 0.6
 * - commonNeighbor (×1.5): Adamic-Adar 指数
 * - typeAffinity (×1.0): 同类型 1.0, 异类型 0.5
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const CONCEPTS_DIR = path.join(__dirname, '../concepts');
const OUTPUT_DIR = path.join(__dirname, '../.learning-progress');

// 权重配置（可调优）
const WEIGHTS = {
  sourceOverlap: 4.0,
  directLink: 3.0,
  commonNeighbor: 1.5,
  typeAffinity: 1.0,
};

const WEIGHT_SUM = Object.values(WEIGHTS).reduce((a, b) => a + b, 0);

/**
 * 解析概念文件的 frontmatter
 */
function parseConcept(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const match = content.match(/^---\n([\s\S]*?)\n---/);

  if (!match) return null;

  const frontmatter = match[1];
  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
  const typeMatch = frontmatter.match(/^type:\s*(.+)$/m);
  const masteryMatch = frontmatter.match(/^mastery:\s*\n\s+level:\s*([0-9.]+)/m);

  // 提取 sources（多行数组）
  const sourcesMatch = frontmatter.match(/^sources:\s*\n((?:\s+-\s+.+\n)*)/m);
  const sources = [];
  if (sourcesMatch) {
    const lines = sourcesMatch[1].trim().split('\n');
    lines.forEach(line => {
      const linkMatch = line.match(/link:\s*"(.+)"/);
      if (linkMatch) sources.push(linkMatch[1]);
    });
  }

  // 提取 relatedConcepts（单行数组）
  const relatedMatch = frontmatter.match(/^relatedConcepts:\s*\[([^\]]*)\]/m);
  const relatedConcepts = [];
  if (relatedMatch && relatedMatch[1].trim()) {
    relatedConcepts.push(...relatedMatch[1].split(',').map(s => s.trim().replace(/"/g, '')));
  }

  // 提取 prerequisites（单行数组）
  const prereqMatch = frontmatter.match(/^prerequisites:\s*\[([^\]]*)\]/m);
  const prerequisites = [];
  if (prereqMatch && prereqMatch[1].trim()) {
    prerequisites.push(...prereqMatch[1].split(',').map(s => s.trim().replace(/"/g, '')));
  }

  return {
    id: path.basename(filePath, '.md'),
    name: nameMatch ? nameMatch[1].trim() : path.basename(filePath, '.md'),
    type: typeMatch ? typeMatch[1].trim() : 'concept',
    mastery: masteryMatch ? parseFloat(masteryMatch[1]) : 0.3,
    sources: sources,
    relatedConcepts: relatedConcepts,
    prerequisites: prerequisites,
  };
}

/**
 * 归一化来源标识符
 */
function normalizeSource(source) {
  // [[文章名]] → 文章名
  if (source.startsWith('[[') && source.endsWith(']]')) {
    source = source.slice(2, -2);
  }

  // URL → domain
  if (source.startsWith('http://') || source.startsWith('https://')) {
    try {
      const url = new URL(source);
      return url.hostname.toLowerCase();
    } catch (e) {
      return source.toLowerCase();
    }
  }

  // 《书名》第X章 → 书名
  const bookMatch = source.match(/《(.+?)》/);
  if (bookMatch) {
    return bookMatch[1].toLowerCase();
  }

  return source.toLowerCase();
}

/**
 * 计算 Jaccard 相似度
 */
function calculateSourceOverlap(sourcesA, sourcesB) {
  if (sourcesA.length === 0 || sourcesB.length === 0) return 0.0;

  const normA = new Set(sourcesA.map(normalizeSource));
  const normB = new Set(sourcesB.map(normalizeSource));

  const intersection = new Set([...normA].filter(x => normB.has(x)));
  const union = new Set([...normA, ...normB]);

  return intersection.size / union.size;
}

/**
 * 计算直接链接分数
 */
function calculateDirectLink(conceptA, conceptB, graph) {
  const aToB = conceptA.relatedConcepts.includes(conceptB.id);
  const bToA = conceptB.relatedConcepts.includes(conceptA.id);

  if (aToB && bToA) return 1.0;  // 双向
  if (aToB || bToA) return 0.6;  // 单向
  return 0.0;
}

/**
 * 计算共同邻居分数（Adamic-Adar）
 */
function calculateCommonNeighbor(conceptA, conceptB, graph) {
  const neighborsA = new Set(conceptA.relatedConcepts);
  const neighborsB = new Set(conceptB.relatedConcepts);

  const common = [...neighborsA].filter(n => neighborsB.has(n));

  if (common.length === 0) return 0.0;

  // Adamic-Adar: Σ 1/log(degree(n))
  let score = 0;
  for (const neighbor of common) {
    const node = graph.get(neighbor);
    if (!node) continue;

    const degree = node.relatedConcepts.length;
    if (degree <= 1) {
      score += 1.0;  // 避免 log(1) = 0
    } else {
      score += 1.0 / Math.log(degree);
    }
  }

  // 归一化：除以共同邻居数（理论最大值 = common.length）
  return score / common.length;
}

/**
 * 计算类型亲和度
 */
function calculateTypeAffinity(conceptA, conceptB) {
  return conceptA.type === conceptB.type ? 1.0 : 0.5;
}

/**
 * 计算综合相关度
 */
function calculateRelevance(conceptA, conceptB, graph) {
  const signals = {
    sourceOverlap: calculateSourceOverlap(conceptA.sources, conceptB.sources),
    directLink: calculateDirectLink(conceptA, conceptB, graph),
    commonNeighbor: calculateCommonNeighbor(conceptA, conceptB, graph),
    typeAffinity: calculateTypeAffinity(conceptA, conceptB),
  };

  const weightedSum =
    signals.sourceOverlap * WEIGHTS.sourceOverlap +
    signals.directLink * WEIGHTS.directLink +
    signals.commonNeighbor * WEIGHTS.commonNeighbor +
    signals.typeAffinity * WEIGHTS.typeAffinity;

  const relevance = weightedSum / WEIGHT_SUM;

  return { relevance, signals };
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
 * 生成相关度矩阵
 */
function generateRelevanceMatrix(graph, threshold = 0.3) {
  const concepts = Array.from(graph.keys());
  const edges = [];

  let totalPairs = 0;
  let computedPairs = 0;

  for (let i = 0; i < concepts.length; i++) {
    for (let j = i + 1; j < concepts.length; j++) {
      totalPairs++;

      const conceptA = graph.get(concepts[i]);
      const conceptB = graph.get(concepts[j]);

      const { relevance, signals } = calculateRelevance(conceptA, conceptB, graph);

      // 稀疏矩阵：只存储相关度 > threshold 的边
      if (relevance > threshold) {
        edges.push({
          from: conceptA.id,
          to: conceptB.id,
          relevance: Math.round(relevance * 1000) / 1000,  // 保留 3 位小数
          signals: {
            sourceOverlap: Math.round(signals.sourceOverlap * 1000) / 1000,
            directLink: Math.round(signals.directLink * 1000) / 1000,
            commonNeighbor: Math.round(signals.commonNeighbor * 1000) / 1000,
            typeAffinity: Math.round(signals.typeAffinity * 1000) / 1000,
          },
        });
        computedPairs++;
      }
    }

    if ((i + 1) % 10 === 0) {
      console.log(`进度: ${i + 1}/${concepts.length} 概念`);
    }
  }

  console.log(`\n总概念对: ${totalPairs}`);
  console.log(`有效边（relevance > ${threshold}): ${computedPairs}`);
  console.log(`稀疏度: ${Math.round((1 - computedPairs / totalPairs) * 100)}%`);

  return edges;
}

/**
 * 主函数
 */
function main() {
  console.log('🚀 开始计算概念相关度...\n');

  const startTime = Date.now();

  // 1. 加载概念图
  console.log('📖 加载概念文件...');
  const graph = loadConcepts();
  console.log(`✅ 加载完成: ${graph.size} 个概念\n`);

  // 2. 生成相关度矩阵
  console.log('🔢 计算相关度矩阵...');
  const edges = generateRelevanceMatrix(graph);

  // 3. 生成输出
  const output = {
    metadata: {
      generated: new Date().toISOString(),
      conceptCount: graph.size,
      edgeCount: edges.length,
      avgRelevance: edges.length > 0
        ? Math.round(edges.reduce((sum, e) => sum + e.relevance, 0) / edges.length * 1000) / 1000
        : 0,
      weights: WEIGHTS,
    },
    edges: edges.sort((a, b) => b.relevance - a.relevance),  // 降序排序
  };

  // 4. 保存结果
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const outputPath = path.join(OUTPUT_DIR, 'concept-relevance.json');
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));

  const elapsedMs = Date.now() - startTime;

  console.log('\n=== 完成 ===');
  console.log(`耗时: ${elapsedMs}ms`);
  console.log(`输出: ${outputPath}`);
  console.log(`\nTop 5 相关概念对:`);

  edges.slice(0, 5).forEach((edge, i) => {
    console.log(`${i + 1}. ${edge.from} ↔ ${edge.to}: ${edge.relevance}`);
    console.log(`   源重叠=${edge.signals.sourceOverlap}, 直接链接=${edge.signals.directLink}, 共同邻居=${edge.signals.commonNeighbor}, 类型亲和=${edge.signals.typeAffinity}`);
  });
}

main();
