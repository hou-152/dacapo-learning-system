#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把本地 Markdown 文件转成飞书云文档（docx blocks API），并授权给用户。
用法: python3 feishu_upload.py <md文件> <文档标题>
凭据: openclaw.feishu.app-secret (macOS keychain) + app cli_aaad4bfe10f99bdf
"""
import json
import re
import subprocess
import sys
import urllib.request

APP_ID = "cli_aaad4bfe10f99bdf"
OWNER_OPEN_ID = "ou_eb26abfaec7510aa0ab0ae5f143ecd23"
BASE = "https://open.feishu.cn"
TENANT_HOST = "https://xcn2zcuh5uow.feishu.cn"


def get_secret():
    out = subprocess.run(
        ["security", "find-generic-password", "-s", "openclaw.feishu.app-secret", "-w"],
        capture_output=True, text=True)
    return out.stdout.strip()


def api(method, path, token, body=None):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    data = json.dumps(body).encode("utf-8") if body is not None else None
    with urllib.request.urlopen(req, data=data, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_token(secret):
    r = api("POST", "/open-apis/auth/v3/tenant_access_token/internal", "",
            {"app_id": APP_ID, "app_secret": secret})
    return r["tenant_access_token"]


INLINE_RE = re.compile(r"(\*\*.+?\*\*|\*[^*\s][^*]*?\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")

def parse_inline(s):
    """把行内 markdown 切成 text_run elements。"""
    runs = []
    for part in INLINE_RE.split(s):
        if not part:
            continue
        style = {"bold": False, "italic": False, "inline_code": False}
        content = part
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            style["bold"] = True
            content = part[2:-2]
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            style["inline_code"] = True
            content = part[1:-1]
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            style["italic"] = True
            content = part[1:-1]
        elif part.startswith("["):
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", part)
            if m:
                content = m.group(1)
                style["link"] = {"url": m.group(2)}
        run = {"text_run": {"content": content, "text_element_style": style}}
        runs.append(run)
    return runs


def text_block(runs):
    return {"block_type": 2, "text": {"elements": runs, "style": {}}}


def heading_block(level, runs):
    return {"block_type": 2 + level, "heading%d" % level: {"elements": runs, "style": {}}}


def bullet_block(runs):
    return {"block_type": 12, "bullet": {"elements": runs, "style": {}}}


def ordered_block(runs):
    return {"block_type": 13, "ordered": {"elements": runs, "style": {}}}


def quote_block(runs):
    return {"block_type": 15, "quote": {"elements": runs, "style": {}}}


def code_block(lines):
    els = [{"text_run": {"content": ln, "text_element_style": {}}} for ln in lines]
    return {"block_type": 14, "code": {"elements": els, "style": {"language": 1}}}


def divider_block():
    return {"block_type": 22, "divider": {}}


def parse_md(text):
    """逐行解析，返回 (blocks, table_fills)。
    table_fills: 表格块在 blocks 里的下标 -> 行内容（用于建表后填单元格）。"""
    blocks = []
    table_fills = {}
    lines = text.split("\n")
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        # 代码块
        if stripped.startswith("```"):
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            blocks.append(code_block(buf))
            i += 1
            continue
        # 表格
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s\-:|]+\|\s*$", lines[i + 1]):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                # 跳过 |---| 分隔行
                if not all(re.match(r"^:?-{2,}:?$", c) for c in cells):
                    rows.append(cells)
                i += 1
            ncol = len(rows[0])
            width = 630 // max(ncol, 1)
            idx = len(blocks)
            blocks.append({
                "block_type": 31,
                "table": {"property": {"row_size": len(rows), "column_size": ncol,
                                       "column_width": [width] * ncol}},
            })
            table_fills[idx] = rows
            continue
        # 分割线
        if re.match(r"^-{3,}\s*$", stripped):
            blocks.append(divider_block())
            i += 1
            continue
        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            blocks.append(heading_block(len(m.group(1)), parse_inline(m.group(2).strip())))
            i += 1
            continue
        # 引用
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").strip())
                i += 1
            blocks.append(quote_block(parse_inline(" ".join(buf))))
            continue
        # 列表
        m = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if m:
            blocks.append(bullet_block(parse_inline(m.group(2).strip())))
            i += 1
            continue
        m = re.match(r"^(\s*)\d+\.\s+(.*)$", line)
        if m:
            blocks.append(ordered_block(parse_inline(m.group(2).strip())))
            i += 1
            continue
        # 普通段落
        blocks.append(text_block(parse_inline(stripped)))
        i += 1
    return blocks, table_fills


def main():
    if len(sys.argv) != 3:
        print("用法: feishu_upload.py <md文件> <文档标题>")
        sys.exit(1)
    path, title = sys.argv[1], sys.argv[2]
    with open(path, encoding="utf-8") as f:
        text = f.read()
    blocks, table_fills = parse_md(text)
    token = get_token(get_secret())

    # 建文档
    r = api("POST", "/open-apis/docx/v1/documents", token, {"title": title})
    doc_id = r["data"]["document"]["document_id"]

    # 分批插入（每批 ≤ 50），表格建好后回填单元格
    for start in range(0, len(blocks), 50):
        chunk = blocks[start:start + 50]
        resp = api("POST", f"/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
                   token, {"children": chunk})
        created = resp["data"]["children"]
        for j, blk in enumerate(created):
            bi = start + j
            if bi not in table_fills:
                continue
            rows = table_fills[bi]
            cells = blk.get("table", {}).get("children", [])
            if not cells:
                g = api("GET", f"/open-apis/docx/v1/documents/{doc_id}/blocks/{blk['block_id']}/children",
                        token, {})
                cells = g["data"]["items"]
            ncol = len(rows[0])
            for ri, row in enumerate(rows):
                row = row + [""] * (ncol - len(row))
                for ci, content in enumerate(row):
                    pos = ri * ncol + ci
                    if pos >= len(cells):
                        continue
                    runs = parse_inline(content or " ")
                    if ri == 0:
                        for run in runs:
                            run["text_run"]["text_element_style"]["bold"] = True
                    cell_id = cells[pos]["block_id"]
                    api("POST", f"/open-apis/docx/v1/documents/{doc_id}/blocks/{cell_id}/children",
                        token, {"children": [text_block(runs)]})

    # 授权给用户
    api("POST", f"/open-apis/drive/v1/permissions/{doc_id}/members?type=docx",
        token, {"member_type": "openid", "member_id": OWNER_OPEN_ID, "perm": "full_access"})

    # 校验块数
    r = api("GET", f"/open-apis/docx/v1/documents/{doc_id}/blocks", token, {})
    print(f"TITLE={title} BLOCKS={len(r['data']['items'])}")
    print(f"URL={TENANT_HOST}/docx/{doc_id}")


if __name__ == "__main__":
    main()
