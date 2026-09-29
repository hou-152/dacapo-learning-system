#!/usr/bin/env node
/**
 * 应用前置关系标注
 *
 * 人工 review 后的结果
 */

const fs = require('fs');
const path = require('path');

const CONCEPTS_DIR = path.join(__dirname, '../concepts');

// 人工 review 后的前置关系（断开循环，保留合理依赖）
const APPROVED_PREREQUISITES = {
  // harness 工程体系
  'harness': [],  // 基础概念，无前置
  'context-engineering': [],  // 基础方法，无前置
  'ai-友好度作为选型标准': ['harness'],
  'service-template-与-golden-path': ['harness'],
  'rigor-的搬迁': ['context-engineering', 'harness'],
  '功能与行为验证的缺口': ['harness'],
  '卡住即信号': ['harness'],
  '垃圾回收型-agent': ['harness'],
  '拓扑作为新抽象层': ['harness'],
  '架构约束的确定性执行': ['harness'],
  '无手打代码': ['harness'],
  '解空间收窄': ['harness'],
  '熵与腐化': [],

  // 社会学体系
  '差序格局': [],  // 基础概念
  '礼治秩序': ['差序格局'],
  '承认政治': [],  // 独立概念
  '社会分层': ['差序格局'],
  '社会学想象力': [],  // 基础方法论
  '理性化铁笼': ['差序格局', '礼治秩序'],
  '人性三分法': [],
  '人情期货': ['差序格局'],
  '先赋vs自致': ['社会分层'],
  '公私界碑': ['差序格局'],
  '再生产': ['社会分层'],
  '婚礼产品发布会': ['差序格局'],
  '彩礼异化': ['差序格局'],
  '承认与狂热': ['承认政治'],
  '现代长老': ['差序格局'],
  '结构紧张': [],
  '铁笼囚徒困境': ['理性化铁笼'],
  '面子估值': ['差序格局'],
};

/**
 * 查找概念文件
 */
function findConceptFile(conceptId) {
  function searchDir(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        const result = searchDir(fullPath);
        if (result) return result;
      } else if (entry.name === `${conceptId}.md`) {
        return fullPath;
      }
    }
    return null;
  }
  return searchDir(CONCEPTS_DIR);
}

/**
 * 更新概念文件的 prerequisites
 */
function updatePrerequisites(conceptId, prerequisites) {
  const filePath = findConceptFile(conceptId);
  if (!filePath) {
    console.log(`⚠️  找不到文件: ${conceptId}`);
    return false;
  }

  let content = fs.readFileSync(filePath, 'utf8');

  // 替换 prerequisites 行
  const prereqArray = prerequisites.map(p => `"${p}"`).join(', ');
  const newLine = `prerequisites: [${prereqArray}]`;

  content = content.replace(/^prerequisites:\s*\[([^\]]*)\]/m, newLine);

  fs.writeFileSync(filePath, content, 'utf8');
  return true;
}

/**
 * 主函数
 */
function main() {
  console.log('🚀 应用前置关系标注...\n');

  let updated = 0;
  let skipped = 0;

  Object.entries(APPROVED_PREREQUISITES).forEach(([conceptId, prerequisites]) => {
    const success = updatePrerequisites(conceptId, prerequisites);

    if (success) {
      updated++;
      const prereqStr = prerequisites.length > 0 ? prerequisites.join(', ') : '无';
      console.log(`✅ ${conceptId}: ${prereqStr}`);
    } else {
      skipped++;
    }
  });

  console.log(`\n=== 完成 ===`);
  console.log(`更新: ${updated}`);
  console.log(`跳过: ${skipped}`);
  console.log(`\n💡 重新运行 calculate-relevance.js 和 recommend.js 验证效果`);
}

main();
