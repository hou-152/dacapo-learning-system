# 直播文稿人物词典与清洗（2026-08-30）

这是一套本地、可追溯的姜禹直播文稿处理包：原稿、全量 V1 清洗稿、人物背景与表达画像、Typeless 式词典、替换账本和对抗性审计放在同一个入口下。

## 先看什么

1. 人物背景与说话人边界：`profile/人物背景与表达画像.md`
2. 喜欢／常用表达候选：`dictionary/常用词与口头禅.md`
3. 可执行纠错词典：`dictionary/approved-hotwords.txt`
4. 全量清洗稿：`cleaned/`
5. 对抗性审计：`audit/ADVERSARIAL-AUDIT.md`

## 目录

| 路径 | 用途 |
| --- | --- |
| `raw/` | 从源 ZIP 解出的 32 份原稿；不覆盖、不改写。 |
| `cleaned/` | 32 份 V1 清洗稿；只做经确权的专名、地名、术语和固定表达纠错。 |
| `profile/` | 人物背景、表达风格、价值张力与说话人污染说明。 |
| `dictionary/` | 强制纠错词典、Typeless 风格 JSON、候选 CSV 和人类阅读版。 |
| `audit/` | 源清单、词频证据、引擎参数、替换账本、逐文件哈希和研究报告。 |
| `tools/` | 本轮提取、统计、纠错、审计与 dbs-learning 回放脚本。 |

## 清洗边界

- 已做：高置信词形纠错，32／32 份另存；2,515 次替换、128 种实际替换类型。
- 未做：删除口头禅、语义重写、自动改口合并、说话人切分、外部事实补写。
- 明确未使用：`transcript-cleaner`。
- 隐私：所有原文只在本机处理，没有发送到 GitHub 项目、LLM API 或其他外部服务。

## 可复算

```bash
/private/tmp/corpus-clean-venv-20260830/bin/python '交互式学习真源/02-课程真源/2026气运+1/assets/直播文稿人物词典与清洗-20260830/tools/batch_asr_hotword.py' \
  --engine-dir /private/tmp/asr-hotword-20260830 \
  --input-dir '交互式学习真源/02-课程真源/2026气运+1/assets/直播文稿人物词典与清洗-20260830/raw' \
  --output-dir /private/tmp/replay-cleaned \
  --hotwords '交互式学习真源/02-课程真源/2026气运+1/assets/直播文稿人物词典与清洗-20260830/dictionary/approved-hotwords.txt' \
  --ledger /private/tmp/replay-ledger.jsonl \
  --manifest /private/tmp/replay-manifest.json \
  --threshold 0.97 --similar-threshold 0.90
```

上面的 `/private/tmp` 虚拟环境和 GitHub clone 是本轮执行快照，不是持久依赖；重跑前需按审计报告记录的 commit 重新建立环境。

研究依据见 `audit/RESEARCH-20260830-TYPELESS-DICTIONARY-GITHUB.md`。该报告区分了 Typeless 官方产品、第三方复刻和本轮实际执行组件。
