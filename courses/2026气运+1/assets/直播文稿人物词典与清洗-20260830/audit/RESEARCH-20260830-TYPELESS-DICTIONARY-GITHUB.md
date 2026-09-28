# Typeless 式个人词典、人物画像与中文直播转写批量清洗：GitHub 项目调研

- 日期：2026-08-30
- 范围：只核对 GitHub 仓库、README／源码／License 和 Typeless 官方帮助文档。
- 本轮动作：只研究；未安装项目，未读取、上传或处理私密直播稿。

## 结论

1. **Typeless 本身不能当作开源项目使用。** 官方确认它有人名／专名词典、更正后自动学习和 CSV 批量导入；也声称会学习用户的用词与语气。但未在官方站点找到对应源码仓库或开源 License。GitHub 上同名仓库是第三方替代品，不是 Typeless 官方源码。[Typeless 词典说明](https://www.typeless.com/help/quickstart/history-and-dictionary)；[Typeless 个性化说明](https://www.typeless.com/help/quickstart/personalization)
2. **最像用户记忆中“喜欢／常用词＋人物画像”的项目是 [`MiaIria/style-distiller`](https://github.com/MiaIria/style-distiller)。** 它面向简体中文，明确维护 `vocabulary` 和 `persona` 画像，但它是 Claude Code Skill，不是离线 ASR 批洗引擎。
3. **没有单一成熟仓库同时完成“可信背景＋词典抽取＋中文音近纠错＋批量保真清洗＋完全离线”。** 对私密语料的最终推荐是：[`jieba`](https://github.com/fxsjy/jieba) 离线抽取词频／人名候选 → 人工或权威来源确权 → [`asr-hotword`](https://github.com/HaujetZhao/asr-hotword) 确定性批量纠错。
4. [`Stylotrace`](https://github.com/zhangyoufu-123/stylotrace) 是当前 Codex／DeepSeek Harness 环境中功能最全的画像候选，但它可自动发现宿主 API 凭据、可联网 RAG，不应未审计就读入私密原稿。

## Typeless 与开源替代品的边界

Typeless 官方词典可添加人名、项目缩写、领域词和行业术语，用户更正后会自动记住偏好拼写，并支持 CSV 导入。个性化页面声称只学习抽象模式，不保存实际消息和口述内容。这些是**厂商声明**，不是可从开源源码独立复核的结论。

因此：

- 可以把 Typeless 当作产品功能参考；
- 不应把 `jlgadgeteer/typeless`、`Smopig/typeless`、`OpenTypeless` 等同名第三方仓库当成官方开源版；
- 不能用 Typeless 的“零保留”表述为其他项目的数据处理背书。

## 候选与取舍

| 候选 | 实证能力 | 边界 | 判定 |
|---|---|---|---|
| [MiaIria/style-distiller](https://github.com/MiaIria/style-distiller) | 简体中文 7 维风格画像；`vocabulary` 记录高频词／禁用词，另有 `persona`；支持正反样本和修改差异学习。 | MIT；Python 3.10+；主要宿主为 Claude Code。档案保存在 `~/.claude/styles/`，但 README 明确会将完整样本嵌入 prompt，“档案本地”不等于“语料不出机”。 | **最像记忆中的项目**；适合风格画像，不适合私密原稿离线批洗。 |
| [zhangyoufu-123/stylotrace](https://github.com/zhangyoufu-123/stylotrace) | 从旧稿、修改、知识库和风格向量生成 `vault/persona.md`；支持长文导入／分片、`persona`、`proofread`、`doc restyle`、反 AI 审计；支持 Codex／DSH。 | MIT；完整画像和改写依赖 LLM。可自动发现宿主凭据和联网检索。 | **功能最全，但过重**；只在隔离副本和已验证本地 LLM 上试验。 |
| [HaujetZhao/asr-hotword](https://github.com/HaujetZhao/asr-hotword) | 中文拼音音素＋英文字母相似度；支持目标词、别名、上下文黑名单、实际替换和低阈值候选分离；Python API 可嵌入批处理。 | MIT；依赖 `pypinyin`、`rapidfuzz`；不自动得到正确词典，不生成人物画像。 | **核心纠错引擎**；强制替换前必须确权词典。 |
| [fxsjy/jieba](https://github.com/fxsjy/jieba) | 中文分词、自定义词典、TF-IDF／TextRank 关键词、词性标注；`nr`／`nt`／`nz` 可生成人名／机构／专名候选。 | MIT；安装后本地运行。人名标注是启发式候选，不是身份确认。 | **词典候选生成器**；需停用词、频率门槛和人工复核。 |
| [HaujetZhao/CapsWriter-Offline](https://github.com/HaujetZhao/CapsWriter-Offline) | 完全离线 ASR、文件转录、音素热词、正则替换、可选 LLM 润色。 | MIT；README 只保证 Windows 10／11，macOS 暂不支持。 | 成熟但不适用当前 Mac；用其抽出的 `asr-hotword`。 |
| [mugoosse/speak](https://github.com/mugoosse/speak) | 很像 Typeless 的本地词典：术语、音近更正、精确替换、前后两轮更正和 raw 历史。 | 当前本地引擎列表不包含中文；服务于实时听写，不是中文旧稿批处理器。 | 只借鉴词典设计。 |
| [Hiro-Inagawa/write-like-me](https://github.com/Hiro-Inagawa/write-like-me) | 约 50 项文体计量、多风格档案、校正规则。 | MIT；基础分析依赖英文功能词和通用英文基线，可选模型是 `en_core_web_sm`。 | 排除为中文主方案。 |

## 最终推荐架构

### 1. 不可变原稿层

- 保持原字节、原路径和 SHA-256；
- 只读副本，结果写入独立 `cleaned/`；
- 词典版本、每个替换、相似度、输入／输出哈希全部记账。

### 2. 候选词典层（`jieba`）

只对**已确认是目标人物发言**的文本做词频、TF-IDF／TextRank、`nr`／`nt`／`nz` 专名候选以及跨场直播覆盖率。输出 `candidate-lexicon.csv`，不直接强制替换。

词频只证明“转写文本中经常出现”，不自动证明“讲者喜欢”；人名词性不证明身份。

### 3. 确权词典层

仅将有可回溯正确词形的项提升为 `approved-hotwords.txt`：

```text
正确词 | 常见误识1 | 常见误识2 ~~~ 不应替换的上下文词
```

证据优先级：本人官方账号／官网自述 → 课件或视频字幕原图 → 多份独立转写稳定共现 → 单次模型推测。最后一类不进 approved。

### 4. 确定性纠错层（`asr-hotword`）

- 第一遍高阈值、只写新文件；
- 实际替换写 `matches.jsonl`；
- 低于替换阈值、高于候选阈值的项写 `similars.jsonl`，不替换；
- 根据误改样本增加 `~~~` 上下文黑名单；
- 抽样审核通过前，不进入语气、句式或段落改写。

### 5. 风格／人物画像层

`Stylotrace` 或 `style-distiller` 可归纳口头禅、高频虚词、断句节奏、叙事视角、常见论证方式和禁用表达。这些是**语料中的表达模式**，不是完整心理、价值观或现实背景。

“了解这个人的背景”必须另起事实层：从本人官网、官方社交账号、任职机构或原始访谈建带引用的时间线。不能从口头禅推断履历，也不能将听众发言混入讲者画像。

## 安装与运行命令（本轮未执行）

### `jieba` ＋ `asr-hotword`：推荐主路径

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install jieba pypinyin rapidfuzz

git clone https://github.com/HaujetZhao/asr-hotword.git
cd asr-hotword
python demo.py
python demo.py test_cases.txt
```

`jieba` 最小运行：

```bash
python -m jieba --pos '/' source.txt > source.pos.txt
```

Python 中可用 `jieba.analyse.extract_tags(..., withWeight=True)` 抽取 TF-IDF 关键词，用 `jieba.posseg.cut(...)` 得到人名／专名候选，用 `jieba.load_userdict(...)` 回读已确权词典。

`asr-hotword` README 公开 API：

```python
from hotword import PhonemeCorrector

pc = PhonemeCorrector(threshold=0.85, similar_threshold=0.70)
pc.update_hotwords(open("approved-hotwords.txt", encoding="utf-8").read())
result = pc.correct(text, k=10, blacklist_window=5)
print(result.text)
print(result.matches)
print(result.similars)
```

仓库没有提供“保留 raw／目录批量／diff 账本”的成品 CLI，所以全量直播稿需要另写小型包装器。

### `style-distiller`：只在允许 Claude Code 处理样本时使用

```bash
git clone https://github.com/MiaIria/style-distiller.git ~/.claude/skills/style-distiller
bash ~/.claude/skills/style-distiller/install.sh
cd ~/.claude/skills/style-distiller
python scripts/profile_stats.py
```

它不是当前 Codex 环境的直接即插即用路径；使用前要审阅 Skill 指令、安装脚本以及完整样本进 prompt 的数据边界。

### `Stylotrace`：只在隔离环境试验

仓库 README 给出：

```bash
curl -fsSL https://raw.githubusercontent.com/zhangyoufu-123/stylotrace/main/install.sh | bash -s -- --all
```

私密语料场景不建议直接管道安装。先审阅：

```bash
git clone --depth 1 https://github.com/zhangyoufu-123/stylotrace.git /tmp/stylotrace-review
cd /tmp/stylotrace-review
bash install.sh --dry-run
```

之后审阅 `install.sh`、凭据发现逻辑、默认网络请求和写入目录；确认只连本地 OpenAI-compatible 端点后，再在非真源样本上实验。

## License 与隐私风险

| 项目 | License | 主要风险 |
|---|---|---|
| `asr-hotword` | [MIT](https://github.com/HaujetZhao/asr-hotword/blob/main/LICENSE) | 热词替换具有强制性；错词典会大规模制造错误。要高阈值、黑名单、新文件输出和替换账本。 |
| `jieba` | [MIT](https://github.com/fxsjy/jieba/blob/master/LICENSE) | 词频不等于偏好，人名词性不等于身份；多讲者混合会污染画像。 |
| `style-distiller` | [MIT](https://github.com/MiaIria/style-distiller/blob/main/LICENSE) | 档案落本地，但原文会嵌入 Claude prompt；对活人风格商业仿写还有人格权／不正当竞争风险。 |
| `Stylotrace` | [MIT](https://github.com/zhangyoufu-123/stylotrace/blob/main/LICENSE) | 自动发现宿主凭据、可联网 RAG、可改写文件；功能面大，不应未审计即进入语料真源。 |
| `CapsWriter-Offline` | [MIT](https://github.com/HaujetZhao/CapsWriter-Offline/blob/master/LICENSE) | 引擎离线，但当前平台不匹配 Mac；可选 LLM 角色是另一数据边界。 |

MIT 允许使用、修改和分发，但要保留版权和许可声明；“按现状提供”不保证语料、事实和人格权安全。

## 离线批处理可行性

| 目标 | 判定 | 条件／边界 |
|---|---|---|
| 从中文直播稿抽取常用词 | **可离线** | `jieba` 分词＋停用词＋跨文档频次／频率；必须先隔离讲者，区分“常见话题词”与“偏好表达”。 |
| 抽取人名和专名候选 | **可离线** | `nr`／`nt`／`nz` 只作候选；必须回到原文与权威来源确认。 |
| 基于词典批量纠正 ASR 误识 | **可离线** | `asr-hotword` 算法本地执行；需加目录级包装器，保留 raw／diff／阈值／哈希。 |
| 自动产生可信的人物背景 | **不可仅凭转写稿** | 只能产生“语料中的自述候选”；履历、任职和时间线需独立一手来源。 |
| 完全离线生成深层人格／价值观画像 | **只能部分做** | 词法／节奏指标可离线；深层画像通常依赖 LLM，且是可错推断。本地 LLM 只解决数据出机，不解决推断真伪。 |
| 保义批量“洗稿” | **可以，必须分层** | 先专名／错别字纠错，再标点／分段；风格改写必须另存并带 diff，不与原转写真源合并。 |

## 执行验收门

1. 先从 3–5 份有明确讲者归属的文稿取样，不立即全量启动。
2. 候选词每项带频次、文档覆盖数、原文例句和讲者归属。
3. 强制替换词必须带正确词形来源；无来源项留在 candidate。
4. 首轮高阈值，随机抽样至少 100 个替换点，统计真阳性／误替换／漏替换。
5. 原文数量、输出数量、输入／输出 SHA-256 与替换账本机械对账。
6. “专名纠错 PASS”、“可读性 PASS”、“人物画像候选”和“背景事实已核实”分开出报告。

## 一手来源

- [Typeless：History & Dictionary](https://www.typeless.com/help/quickstart/history-and-dictionary)
- [Typeless：Personalization](https://www.typeless.com/help/quickstart/personalization)
- [MiaIria/style-distiller](https://github.com/MiaIria/style-distiller)
- [zhangyoufu-123/stylotrace](https://github.com/zhangyoufu-123/stylotrace)
- [Stylotrace CHANGELOG](https://github.com/zhangyoufu-123/stylotrace/blob/main/CHANGELOG.md)
- [HaujetZhao/asr-hotword](https://github.com/HaujetZhao/asr-hotword)
- [fxsjy/jieba](https://github.com/fxsjy/jieba)
- [HaujetZhao/CapsWriter-Offline](https://github.com/HaujetZhao/CapsWriter-Offline)
- [mugoosse/speak](https://github.com/mugoosse/speak)
- [Hiro-Inagawa/write-like-me](https://github.com/Hiro-Inagawa/write-like-me)
