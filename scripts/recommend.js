#!/usr/bin/env node
/**
 * Phase 2: 桥接概念匹配 & 学习路径推荐
 *
 * 功能：
 * 1. 找到桥接概念：mastery ≥ 0.6 且 relevance ≥ 0.5
 * 2. 推荐学习路径：前置概念已掌握且能解锁更多概念
 */

const fs = require('fs');
const path = require('path');

const CONCEPTS_DIR = path.join(__dirname, '../concepts');
const PROGRESS_DIR = path.join(__dirname, '../.learning-progress');
const RELEVANCE_FILE = path.join(PROGRESS_DIR, 'concept-relevance.json');
const BRIDGE_USAGE_FILE = path.join(PROGRESS_DIR, 'bridge-usage.json');

/**
 * 加载相关度数据
 */
function loadRelevanceData() {
  if (!fs.existsSync(RELEVANCE_FILE)) {
    throw new Error('请先运行 calculate-relevance.js 生成相关度数据');
  }

  const data = JSON.parse(fs.readFileSync(RELEVANCE_FILE, 'utf8'));

  // 构建相关度查询索引
  const relevanceMap = new Map();

  data.edges.forEach(edge => {
    const key1 = `${edge.from}-${edge.to}`;
    const key2 = `${edge.to}-${edge.from}`;
    relevanceMap.set(key1, edge);
    relevanceMap.set(key2, edge);
  });

  return { metadata: data.metadata, relevanceMap };
}

/**
 * 加载桥接概念使用计数
 */
function loadBridgeUsage() {
  if (!fs.existsSync(BRIDGE_USAGE_FILE)) {
    return {};
  }
  return JSON.parse(fs.readFileSync(BRIDGE_USAGE_FILE, 'utf8'));
}

/**
 * 保存桥接概念使用计数
 */
function saveBridgeUsage(usage) {
  fs.writeFileSync(BRIDGE_USAGE_FILE, JSON.stringify(usage, null, 2));
}

/**
 * 解析概念文件
 */
function parseConcept(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const match = content.match(/^---\n([\s\S]*?)\n---/);

  if (!match) return null;

  const frontmatter = match[1];
  const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
  const typeMatch = frontmatter.match(/^type:\s*(.+)$/m);
  const masteryMatch = frontmatter.match(/^mastery:\s*\n\s+level:\s*([0-9.]+)/m);

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
    prerequisites: prerequisites,
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
 * 查询两个概念的相关度
 */
function getRelevance(conceptA, conceptB, relevanceMap) {
  const key = `${conceptA}-${conceptB}`;
  const edge = relevanceMap.get(key);
  return edge ? edge.relevance : 0;
}

/**
 * 查找桥接概念
 */
function findBridgeConcepts(targetConceptId, concepts, relevanceMap, bridgeUsage) {
  const bridges = [];

  concepts.forEach((concept, conceptId) => {
    // 过滤：已掌握（mastery ≥ 0.6）
    if (concept.mastery < 0.6) return;

    // 过滤：与目标概念高度相关（relevance ≥ 0.5）
    const relevance = getRelevance(conceptId, targetConceptId, relevanceMap);
    if (relevance < 0.5) return;

    // 计算 bridgeScore = mastery × relevance / (1 + usageCount)
    const usageCount = bridgeUsage[conceptId] || 0;
    const bridgeScore = (concept.mastery * relevance) / (1 + usageCount);

    bridges.push({
      conceptId: conceptId,
      name: concept.name,
      mastery: concept.mastery,
      relevance: relevance,
      usageCount: usageCount,
      bridgeScore: Math.round(bridgeScore * 1000) / 1000,
    });
  });

  // 降序排序
  bridges.sort((a, b) => b.bridgeScore - a.bridgeScore);

  return bridges.slice(0, 3);  // Top 3
}

/**
 * 检查概念是否已解锁
 */
function isUnlocked(concept, concepts) {
  const prerequisites = concept.prerequisites || [];

  // 无前置概念 = 已解锁
  if (prerequisites.length === 0) return true;

  // 所有前置概念掌握度 ≥ 60%
  return prerequisites.every(preId => {
    const preConcept = concepts.get(preId);
    return preConcept && preConcept.mastery >= 0.6;
  });
}

/**
 * 计算解锁潜力（解锁该概念后能解锁多少新概念）
 */
function calculateUnlockPotential(conceptId, concepts) {
  let unlockCount = 0;

  concepts.forEach(concept => {
    const prerequisites = concept.prerequisites || [];

    // 当前未解锁
    if (!prerequisites.includes(conceptId)) return;
    if (concept.mastery >= 0.6) return;  // 已掌握

    // 模拟掌握 conceptId 后是否解锁
    const wouldUnlock = prerequisites.every(preId => {
      if (preId === conceptId) return true;  // 假设已掌握
      const preConcept = concepts.get(preId);
      return preConcept && preConcept.mastery >= 0.6;
    });

    if (wouldUnlock) unlockCount++;
  });

  return unlockCount;
}

/**
 * 推荐学习路径
 */
function recommendLearningPath(concepts, relevanceMap, bridgeUsage) {
  const recommendations = [];

  concepts.forEach((concept, conceptId) => {
    // 过滤：已掌握（跳过）
    if (concept.mastery >= 0.6) return;

    // 过滤：未解锁（前置概念未满足）
    if (!isUnlocked(concept, concepts)) return;

    // 计算推荐分数
    const unlockPotential = calculateUnlockPotential(conceptId, concepts);

    // 找到最佳桥接概念
    const bridges = findBridgeConcepts(conceptId, concepts, relevanceMap, bridgeUsage);
    const bestBridgeScore = bridges.length > 0 ? bridges[0].bridgeScore : 0;

    const recommendScore = bestBridgeScore + unlockPotential * 0.1;  // 解锁潜力权重较低

    recommendations.push({
      conceptId: conceptId,
      name: concept.name,
      mastery: concept.mastery,
      unlockPotential: unlockPotential,
      bestBridge: bridges.length > 0 ? bridges[0].name : null,
      recommendScore: Math.round(recommendScore * 1000) / 1000,
    });
  });

  // 降序排序
  recommendations.sort((a, b) => b.recommendScore - a.recommendScore);

  return recommendations.slice(0, 5);  // Top 5
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  console.log('🚀 桥接概念匹配 & 学习路径推荐\n');

  // 加载数据
  console.log('📖 加载数据...');
  const { metadata, relevanceMap } = loadRelevanceData();
  const concepts = loadConcepts();
  const bridgeUsage = loadBridgeUsage();
  console.log(`✅ 加载完成: ${concepts.size} 个概念, ${metadata.edgeCount} 条边\n`);

  if (command === 'bridge') {
    // 查找桥接概念
    const targetId = args[1];
    if (!targetId) {
      console.error('用法: node recommend.js bridge <概念ID>');
      process.exit(1);
    }

    const targetConcept = concepts.get(targetId);
    if (!targetConcept) {
      console.error(`❌ 概念不存在: ${targetId}`);
      process.exit(1);
    }

    console.log(`🔍 查找桥接概念: ${targetConcept.name}\n`);
    const bridges = findBridgeConcepts(targetId, concepts, relevanceMap, bridgeUsage);

    if (bridges.length === 0) {
      console.log('未找到符合条件的桥接概念（mastery ≥ 0.6 且 relevance ≥ 0.5）');
    } else {
      console.log('Top 3 桥接概念:\n');
      bridges.forEach((bridge, i) => {
        console.log(`${i + 1}. ${bridge.name}`);
        console.log(`   掌握度: ${bridge.mastery}, 相关度: ${bridge.relevance}, 使用次数: ${bridge.usageCount}`);
        console.log(`   桥接分数: ${bridge.bridgeScore}`);
      });
    }

  } else if (command === 'path') {
    // 推荐学习路径
    console.log('🎯 推荐学习路径\n');
    const recommendations = recommendLearningPath(concepts, relevanceMap, bridgeUsage);

    if (recommendations.length === 0) {
      console.log('未找到可推荐的概念（所有概念已掌握或未解锁）');
    } else {
      console.log('Top 5 推荐:\n');
      recommendations.forEach((rec, i) => {
        console.log(`${i + 1}. ${rec.name}`);
        console.log(`   当前掌握度: ${rec.mastery}`);
        console.log(`   解锁潜力: ${rec.unlockPotential} 个新概念`);
        console.log(`   最佳桥接: ${rec.bestBridge || '无'}`);
        console.log(`   推荐分数: ${rec.recommendScore}\n`);
      });
    }

  } else {
    console.log('用法:');
    console.log('  node recommend.js bridge <概念ID>  - 查找桥接概念');
    console.log('  node recommend.js path             - 推荐学习路径');
  }
}

main();
