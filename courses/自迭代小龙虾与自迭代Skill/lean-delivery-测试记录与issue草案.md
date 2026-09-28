# lean-delivery-skill 测试记录 + issue 草案

> 测试对象：https://github.com/daijx-ai/lean-delivery-skill @ 7e4338e（pristine 上游 clone）
> 测试人：本会话（skill-meta 审计模式）
> 日期：2026-08-25

## 一、测试矩阵（实测）

| # | 场景 | 预期 | 实测 | 判定 |
|---|---|---|---|---|
| T1 | 标准 router 七边界齐全 | pass | pass | ✓ 正常 |
| T2 | Light 行反转语义（HAS 全部边界） | fail | **pass** | ❌ 假阴性 bug |
| T3 | router 多一条未知边界（legal/regulatory） | 应被察觉 | **pass** | ❌ 盲区 bug |
| T4 | skill 行删掉 external-system | fail | fail（missing_from_skill 正确） | ✓ 正常 |
| T5 | 缺 --router | argparse 报错退出 | argparse 报错 | ✓ 正常 |
| T6 | router 无 `| **Light** |` 行 | 友好报错 | 裸 ValueError traceback | ⚠️ UX 差 |
| T7 | global-entry 缺不变量标记 | fail | fail（三条缺失标记列出） | ✓ 正常 |

## 二、issue 草案（英文，仓库语言）

---
**Title: Validator passes when Light criteria are inverted or when the router adds a new boundary**

Environment: repo @ 7e4338e, `python3 scripts/validate_light_tiering.py`, Python 3.

The validator enforces the one-way invariant "inline Light ⇒ router §0 Light". Two cases break that invariant and still exit with `pass`.

**1. Inverted semantics pass (false negative).** The skill-side matcher checks only that boundary phrases are present in the Light line, not that they are negated. A Light definition saying a Light task **HAS** all these boundaries still passes:

```bash
python3 scripts/validate_light_tiering.py \
  --skill <(printf '%s\n' 'A clearly Light task HAS confirmed product behavior and Contract, schema and persisted/shared-data, authorization and security boundary, global and cross-runtime rule, production/CI/release/deployment/runtime-configuration, local reversibility, and external-system change.') \
  --router <(printf '%s\n' '| **Light** | no confirmed product/Contract; no shared or persisted schema/data; no authorization/security boundary; no global/cross-runtime rule; no production/CI/release/deployment/runtime configuration; no irreversible action; no material external-system change |')
# => {"status": "pass", ...} — inline criterion is now the exact opposite of the contract
```

Expected: `fail`. Suggested fix: anchor the negation ("no" / "absent") per boundary, or match positive and negative variants separately and compare polarity rather than presence.

**2. New router boundaries are invisible.** `BOUNDARIES` hardcodes seven names. If router §0 Light adds an eighth boundary (e.g. legal/regulatory), `router_set` still equals the seven known names, so nothing fails even though inline Light is now weaker than router §0:

```bash
python3 scripts/validate_light_tiering.py \
  --router <(printf '%s\n' '| **Light** | no confirmed product/Contract; no shared or persisted schema/data; no authorization/security boundary; no global/cross-runtime rule; no production/CI/release/deployment/runtime configuration; no irreversible action; no material external-system change; no legal/regulatory boundary |')
# => {"status": "pass", ...}
```

Expected: at least a warning, ideally fail with "router §0 contains unclassified boundaries". Every router-side boundary addition currently widens the gap silently.

**3. Not runnable from the repo alone.** The only check script requires `--router` pointing at a file that is not in this repo, and the README canary claims ship with no runnable fixture. A router without the `| **Light** |` row raises a raw `ValueError` traceback instead of a structured result. Suggestion: add a `tests/` fixture router plus a small test matrix (canonical pass; inverted must-fail; missing-boundary must-fail; extra-boundary must-warn) so the README's evidence boundary is reproducible in CI.

Happy to send a PR for #1 and #2 if useful.
---

## 三、提交状态

- gh CLI：本机未安装（`gh: command not found`）；`~/.config/gh` 无 oauth_token；无 GH_TOKEN / GITHUB_TOKEN 环境变量。
- 结论：本会话无法直接调 GitHub API 提交。两条路：用户安装 gh 并登录后我来提交；或用户把上面 issue 草案粘贴到 https://github.com/daijx-ai/lean-delivery-skill/issues/new 提交。
