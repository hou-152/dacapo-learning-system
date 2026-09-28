# 13 概念复习图 · Prompt Plan

- 课题：社会学基本概念（吉登斯《社会学基本概念》第二版）
- 日期：2026-08-18
- 状态：本机无文生图通道（无 imagegen skill / 无图像 API key），当前两张图由本地 PIL 脚本 `gen_review_cards.py` 按 Guizang 风格近似生成。下面的 prompt 为未来接入 imagegen 时的渲染版，可直接用。

## 13 概念清单（主题一 7 + 主题二 6）

| # | 概念 | 英文 | 状态 | 一句话 |
|---|---|---|---|---|
| 01 | 社会 | Society | 已学 02 | 有边界：共享文化制度、相互依赖、代代延续 |
| 02 | 结构 / 能动 | Structure / Agency | 已学 02 | 结构是行动的中介，也是行动的结果 |
| 03 | 理性化 | Rationalization | 已学 04 | 可计算、可预测、效率至上；铁笼与去魅 |
| 04 | 话语 | Discourse | 已学 05 | 说话塑造现实；说法分配责任 |
| 05 | 全球化 | Globalization | 待学 | 世界范围的联系越来越紧密 |
| 06 | 现代性 | Modernity | 待学 | 工业化、理性化塑造的社会形态 |
| 07 | 后现代性 | Postmodernity | 待学 | 对宏大叙事的怀疑与多元并存 |
| 08 | 理想类型 | Ideal Type | 已学 06 | 概念是量尺，现实总在偏离它 |
| 09 | 反身性 | Reflexivity | 已学 07 | 观察者把自己也放进画面 |
| 10 | 社会建构论 | Social Constructionism | 已学 08 | 现实靠共识、制度、日常重复建出来 |
| 11 | 定性 / 定量 | Qual / Quant | 待学 | 深度理解 vs 数字测量 |
| 12 | 唯实论 | Realism | 待学 | 现实独立于我们对它的说法存在 |
| 13 | 科学 | Science | 待学 | 用系统方法生产可靠知识 |

## 图 1：13 概念总览图

- 概念：13 概念总览（复习挂图）
- 视觉结构：两栏网格卡片墙（左列主题一 7 卡，右列主题二 6 卡），蓝条 = 已学，灰条 = 待学
- 输出：`13概念总览图.png`（1600x1000，PIL 生成）
- 箭头含义：无箭头
- 渲染版 prompt：

```text
Use case: stylized-concept
Asset type: wide horizontal 1.9:1 labeled material illustration for study review wall
Primary request: A two-column grid of 13 small physical index cards pinned on an off-white studio wall. Left column has 7 cards titled 社会, 结构/能动, 理性化, 话语, 全球化, 现代性, 后现代性; right column has 6 cards titled 理想类型, 反身性, 社会建构论, 定性/定量, 唯实论, 科学. Cards on the left column and the first three on the right have a small vivid blue edge tab, the remaining six have a gray edge tab. Each card shows only its title and one short caption line, no other text.
Chinese labels: use the 13 titles above as printed card titles, short and horizontal, high contrast, away from edges.
Style/medium: clean Swiss editorial 3D vector-like illustration, off-white background, black ink lines, refined gray surfaces, one vivid IKB blue accent (#002FA7).
Composition/framing: wide horizontal 1.9:1, subject fills width, centered vertically, generous safe margins, full subject visible, no crop.
Lighting/mood: crisp studio light, calm analytical mood.
Constraints: no extra words, no English, no logo, no watermark, no poster frame, no decorative blobs, no gradient background.
```

## 图 2：已学 7 概念关系网络图

- 概念：结构/能动（轴心）、社会、理性化、话语、社会建构论、理想类型、反身性
- 视觉结构：Hub-and-spoke（中心轴心 + 左侧来源 + 右侧三个派生）+ 底部工具层（layer）
- 箭头含义（每条一个）：社会→结构/能动 = 规则+资源；结构/能动→理性化 = 高密度形态；→话语 = 语言层；→社会建构论 = 三种建法；工具层→结构/能动（虚线）= 怎么测量自己
- 输出：`概念关系网络图.png`（1600x1000，PIL 生成）
- 渲染版 prompt：

```text
Use case: stylized-concept
Asset type: wide horizontal 1.9:1 labeled material illustration for sociology concept map
Primary request: A hub-and-spoke concept map as small physical cards on an off-white studio table. Center card 结构/能动. Left card 社会 points to the center with a blue arrow labeled 规则+资源. The center points right to three cards 理性化 (top, label 高密度形态), 话语 (middle, label 语言层), 社会建构论 (bottom, label 三种建法). Below the left area a dashed-outline tray titled 研究工具箱 holds two cards 理想类型 and 反身性, with a dashed blue arrow from the tray up to the center card labeled 怎么测量自己. Every arrow has exactly one meaning.
Chinese labels: 结构/能动, 社会, 理性化, 话语, 社会建构论, 理想类型, 反身性, 研究工具箱, 规则+资源, 高密度形态, 语言层, 三种建法, 怎么测量自己.
Style/medium: clean Swiss editorial 3D vector-like illustration, off-white background, black ink lines, refined gray surfaces, one vivid IKB blue accent (#002FA7).
Composition/framing: wide horizontal 1.9:1, subject fills width, centered vertically, generous safe margins, full subject visible, no crop.
Lighting/mood: crisp studio light, calm analytical mood.
Constraints: no extra words, no English, no logo, no watermark, no decorative blobs, no gradient background.
```

## 单概念卡模板（未来按需渲染，每张一卡）

```text
Use case: stylized-concept
Asset type: square 1:1 labeled material illustration for study flashcard
Primary request: One small physical card on an off-white studio table representing [概念名]. [视觉结构：一句关系 + 3-5 个可见标签].
Chinese labels: 3-5 short labels, printed callouts, horizontal, high contrast, away from edges.
Style/medium: clean Swiss editorial 3D vector-like illustration, off-white background, black ink lines, refined gray surfaces, one vivid IKB blue accent (#002FA7).
Constraints: no extra words, no English, no logo, no watermark, no decorative blobs.
```

已学 7 概念的卡片标签集（未来逐张渲染时用）：

| 概念 | 视觉结构 | 标签（3-5 个） |
|---|---|---|
| 社会 | Layer stack | 领土边界 / 共享文化 / 相互依赖 / 代代延续 |
| 结构 / 能动 | Feedback system（互相构成） | 规则 / 资源 / 行动 / 再生产 |
| 理性化 | Pipeline（可计算化） | 可计算 / 可预测 / 效率 / 铁笼 |
| 话语 | Causal mechanism（说法→制度） | 说法 / 责任 / 制度 / 资格 |
| 理想类型 | Comparison（量尺与偏离） | 纯形态 / 现实案例 / 偏离 |
| 反身性 | Before/after（放进画面） | 观察者 / 被观察者 / 概念回流 |
| 社会建构论 | Pipeline（三种建法） | 命名 / 制度化 / 日常重复 |

## 拒绝记录

- v1 网络图：概念卡副文用 `d.text` 渲染 `\n` 会失效、三个箭头标签压卡片 → 修复换行渲染 + 标签位置后重出。
- 总览图未发生拒绝。

## 图 3：概念三层网络图（12 已学概念）

- 概念：12 个已学概念（工具层：社会学的想象力、理想类型、反身性；结构层：社会、结构/能动、理性化、话语、社会建构论；人层：社会化、风险、异化、可持续发展）
- 视觉结构：Layer stack（三层横带）+ 层内箭头；实线 = 派生/构成，虚线 = 相邻或视角供给
- 箭头含义：社会→结构/能动 = 规则与资源；结构/能动→理性化 = 高密度形态；→话语 = 语言层；→社会建构论 = 日常重复；话语→社会建构论 = 命名；社会建构论→风险 = 分配；理性化→异化 = 铁笼之后；风险→可持续发展 = 代价分配
- 输出：`概念三层网络图.png`（1600x1000，PIL 生成）
- 渲染版 prompt：

```text
Use case: stylized-concept
Asset type: wide horizontal 1.9:1 labeled material illustration for sociology concept map
Primary request: Three horizontal layers of small physical cards on an off-white studio wall. Top layer labeled 工具层 holds three cards 社会学的想象力, 理想类型, 反身性. Middle layer labeled 结构层 holds five cards 社会 (left top), 结构/能动 (center top), and below them 理性化, 话语, 社会建构论. Bottom layer labeled 人层 holds four cards 社会化, 风险, 异化, 可持续发展. Blue arrows: 社会 to 结构/能动 labeled 规则与资源; 结构/能动 to 理性化 labeled 高密度形态; to 话语 labeled 语言层; to 社会建构论 labeled 日常重复; 话语 to 社会建构论 labeled 命名; 社会建构论 down to 风险 labeled 分配; 风险 to 可持续发展 labeled 代价分配. One dashed blue arrow from 理性化 to 异化 labeled 铁笼之后. Every arrow has exactly one meaning.
Chinese labels: 工具层, 结构层, 人层, 社会学的想象力, 理想类型, 反身性, 社会, 结构/能动, 理性化, 话语, 社会建构论, 社会化, 风险, 异化, 可持续发展, 规则与资源, 高密度形态, 语言层, 日常重复, 命名, 分配, 铁笼之后, 代价分配.
Style/medium: clean Swiss editorial 3D vector-like illustration, off-white background, black ink lines, refined gray surfaces, one vivid IKB blue accent (#002FA7).
Composition/framing: wide horizontal 1.9:1, subject fills width, centered vertically, generous safe margins, full subject visible, no crop.
Lighting/mood: crisp studio light, calm analytical mood.
Constraints: no extra words, no English, no logo, no watermark, no decorative blobs, no gradient background.
```

## 更新记录

- 2026-08-18：总览图进度行更新（01-12）；新增图 3「概念三层网络图」。工具层的三条虚线边（变焦/量尺/镜子）未在 PIL 版画出，仅存在于 12.md Mermaid 图与渲染版 prompt。
