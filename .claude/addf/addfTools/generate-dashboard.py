#!/usr/bin/env python3
"""ADDF ローカルダッシュボード生成（Plan 0058）。

リポジトリの状態（TODO テーブル・Plan の owner_feedback フィールド・Questions.md・
Progress.md・Progresses/・git 投機ブランチ・gh PR）から、VitePress でサーブできる
3ページのダッシュボード（要フィードバック / 進行中タスク / 未実施の計画）と
プランビューア（Plan 本文コピー）を `.claude/addf/dashboard/` に生成する。

- 出力ディレクトリ全体が生成物（.gitignore 対象）。単一ソースは常にリポジトリ側
- stdlib のみ。gh 不在・未認証は空リスト＋注記のフェイルセーフ
- owner_feedback フィールド未記入の未完了 Plan は「要判断（詳細は Plan 本文参照）」に
  フォールバック表示する（完全性を生成の前提にしない）

実行: python3 .claude/addf/addfTools/generate-dashboard.py（uv run でも動く）
閲覧: npm run dashboard:dev（ADDF 本体）。package.json に dashboard:* が無い
      ダウンストリームでは `npx vitepress dev .claude/addf/dashboard` で閲覧できる
テスト用: 環境変数 ADDF_DASHBOARD_ROOT でリポジトリルートを上書きできる
        （テストがサンドボックスに合成リポジトリを作って検証するためのフック）
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# --- リポジトリ検出 -----------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
# .claude/addf/addfTools/ の3階層上。テストは ADDF_DASHBOARD_ROOT で上書きする
REPO_ROOT = Path(os.environ.get("ADDF_DASHBOARD_ROOT") or SCRIPT_DIR.parent.parent.parent).resolve()
ADDF_DIR = REPO_ROOT / ".claude" / "addf"
OUT_DIR = ADDF_DIR / "dashboard"

# upstream（ADDF 本体）は plans-add/TODO.addf.md、ダウンストリームは plans/TODO.md
if (ADDF_DIR / "plans-add" / "TODO.addf.md").exists():
    PLANS_DIR = ADDF_DIR / "plans-add"
    TODO_PATH = PLANS_DIR / "TODO.addf.md"
else:
    PLANS_DIR = ADDF_DIR / "plans"
    TODO_PATH = REPO_ROOT / "TODO.md"

QUESTIONS_PATH = ADDF_DIR / "Questions.md"
PROGRESS_PATH = ADDF_DIR / "Progress.md"
PROGRESSES_DIR = ADDF_DIR / "Progresses"

TODAY = datetime.date.today()

# --- 抽出: TODO テーブル -------------------------------------------------------

TODO_ROW_RE = re.compile(
    r"^\|\s*(?P<prio>[^|]+?)\s*\|\s*(?P<phase>[^|]+?)\s*\|\s*(?P<file>[^|]+?)\s*\|\s*(?P<state>.+?)\s*\|\s*$"
)


def parse_todo_rows():
    """TODO テーブルから (優先度, ファイルパス, 状態文字列) を返す。ヘッダ行等は除外。"""
    rows = []
    if not TODO_PATH.exists():
        return rows
    for line in TODO_PATH.read_text(encoding="utf-8").splitlines():
        m = TODO_ROW_RE.match(line)
        if not m:
            continue
        file_cell = m.group("file")
        pm = re.search(r"`([^`]+\.md)`", file_cell)
        if not pm:
            continue
        rows.append(
            {
                "prio": m.group("prio").strip("* "),
                "path": pm.group(1),
                "state": m.group("state"),
            }
        )
    return rows


# --- 抽出: Plan ヘッダ・FB フィールド ------------------------------------------

FIELD_RE = re.compile(r"^(owner_feedback|feedback_ask|feedback_since):\s*(.+?)\s*$")


def parse_plan(path: Path):
    """Plan ファイルからタイトル・実装状況・FB フィールドを抽出する。"""
    info = {
        "title": path.stem,
        "status_line": "",
        "owner_feedback": None,
        "feedback_ask": None,
        "feedback_since": None,
    }
    if not path.exists():
        return info
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# ") and info["title"] == path.stem:
            info["title"] = re.sub(r"^Plan \d+:\s*", "", line[2:]).strip()
        elif line.startswith("## 実装状況:"):
            info["status_line"] = line[len("## 実装状況:") :].strip()
        else:
            m = FIELD_RE.match(line)
            if m:
                info[m.group(1)] = m.group(2)
    return info


def wait_days(since: str):
    try:
        d = datetime.date.fromisoformat(since)
        return (TODAY - d).days
    except (ValueError, TypeError):
        return None


# --- 抽出: Questions.md --------------------------------------------------------


def parse_questions():
    """未回答 Question のリストと回答済み件数を返す。"""
    unanswered, answered = [], []
    if not QUESTIONS_PATH.exists():
        return unanswered, answered
    text = QUESTIONS_PATH.read_text(encoding="utf-8")
    sections = re.split(r"^## ", text, flags=re.M)
    for sec in sections:
        is_open = sec.startswith("未回答")
        is_closed = sec.startswith("回答済み")
        if not (is_open or is_closed):
            continue
        for qm in re.finditer(r"^### (Q\d+): (.+?)$\n(.*?)(?=^### |\Z)", sec, re.M | re.S):
            qid, title, body = qm.group(1), qm.group(2).strip(), qm.group(3)
            dm = re.search(r"投下日時:\s*(\d{4}-\d{2}-\d{2})", body)
            pm = re.search(r"Plan (\d{4})", title)
            q = {
                "id": qid,
                "title": title,
                "since": dm.group(1) if dm else None,
                "plan": pm.group(1) if pm else None,
                "body": body.strip(),
            }
            (unanswered if is_open else answered).append(q)
    return unanswered, answered


# --- 抽出: Progress.md ---------------------------------------------------------


def parse_progress():
    """現在のタスク（タイトル・チェックリスト・最新日記）を返す。無ければ None。"""
    if not PROGRESS_PATH.exists():
        return None
    text = PROGRESS_PATH.read_text(encoding="utf-8")
    tm = re.search(r"^### 現在のタスク: (.+?)$(.*)", text, re.M | re.S)
    if not tm:
        return None
    title, body = tm.group(1).strip(), tm.group(2)
    # チェックリスト集計は「#### サブタスクチェックリスト」節に限定する
    # （日記本文に例示のチェックボックス記法が書かれても誤集計しない）
    cm = re.search(r"^#### サブタスクチェックリスト$(.*?)(?=^#### |\Z)", body, re.M | re.S)
    checklist_src = cm.group(1) if cm else body
    checklist = re.findall(r"^- \[([ x])\] (.+)$", checklist_src, re.M)
    diaries = re.findall(r"^##### (.+?)$\n(.*?)(?=^##### |\Z)", body, re.M | re.S)
    latest_diary = None
    if diaries:
        head, dbody = diaries[-1]
        latest_diary = {"head": head.strip(), "body": dbody.strip()}
    return {"title": title, "checklist": checklist, "diary": latest_diary}


def recent_progresses(n=5):
    if not PROGRESSES_DIR.exists():
        return []
    files = sorted(PROGRESSES_DIR.glob("*.md"), reverse=True)
    return [f.stem for f in files[:n]]


# --- 抽出: git / gh ------------------------------------------------------------


def run_cmd(args, timeout=10):
    try:
        r = subprocess.run(
            args, cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout
        )
        return r.stdout if r.returncode == 0 else None
    except Exception:  # 非UTF-8ロケールの UnicodeDecodeError 等も含めフェイルセーフ
        return None


def speculative_branches():
    out = run_cmd(["git", "branch", "--list", "speculative/*", "--format=%(refname:short)"])
    branches = []
    for name in (out or "").split():
        cnt = run_cmd(["git", "rev-list", "--count", f"main..{name}"])
        branches.append({"name": name, "ahead": int(cnt) if cnt else None})
    return branches


def open_prs():
    """PR リストを返す。gh 不在・未認証・失敗時は None（呼び出し側で注記表示）。"""
    out = run_cmd(["gh", "pr", "list", "--state", "open", "--json", "number,title,createdAt,url"], timeout=8)
    if out is None:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


# --- ページ生成 -----------------------------------------------------------------


def esc_vue(text: str) -> str:
    """Plan 原文を VitePress（Vue コンパイル）で安全に通すエスケープ。

    コードフェンス内は不変。フェンス外では、インラインコード区間を除き
    HTML コメント以外の `<`（例: `<番号>`・`speculative/<concept>`）と
    Vue 展開 `{{` をエスケープする。Plan 原文が意図的に使う生 HTML は
    `<!-- human-judgment -->` 等のコメントのみという前提（原文の忠実表示が目的）。

    - フェンスは CommonMark 準拠で「同じ文字種・同じ長さ以上」でのみ閉じる
      （``` の中の ~~~ で誤って閉じない）
    - インラインコードは CommonMark 準拠で「同じ連長の閉じバッククォートが後に
      実在する場合のみコードスパン」とする先読みマッチング。閉じが無い単発
      バッククォートはリテラル扱いになり、以降のテキストは通常どおり
      エスケープされる（奇数バッククォート行でエスケープが免除される事故を防ぐ）。
      スパンは段落内（空行まで）なら行を跨いでよい
    """

    def esc_text(seg: str) -> str:
        seg = re.sub(r"<(?!!--)", "&lt;", seg)
        return seg.replace("{{", "&#123;&#123;")

    def esc_paragraph(para: str) -> str:
        parts = re.split(r"(`+)", para)
        out, i = [], 0
        while i < len(parts):
            p = parts[i]
            if p and p == "`" * len(p):
                # 同じ連長の閉じデリミタを先読み
                j = i + 1
                while j < len(parts):
                    q = parts[j]
                    if q and q == "`" * len(q) and len(q) == len(p):
                        break
                    j += 1
                if j < len(parts):
                    out.extend(parts[i : j + 1])  # コードスパン: 不変
                    i = j + 1
                else:
                    out.append(p)  # 閉じ無し: リテラル。後続は通常エスケープ
                    i += 1
            else:
                out.append(esc_text(p))
                i += 1
        return "".join(out)

    out_lines = []
    para_buf = []  # フェンス外の段落バッファ（インラインコードスパンは段落内で解決）
    fence_char, fence_len = None, 0

    def flush_para():
        if para_buf:
            out_lines.append(esc_paragraph("\n".join(para_buf)))
            para_buf.clear()

    for line in text.splitlines():
        fm = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fm:
            delim = fm.group(1)
            if fence_char is None:
                flush_para()
                fence_char, fence_len = delim[0], len(delim)
                out_lines.append(line)
                continue
            if delim[0] == fence_char and len(delim) >= fence_len:
                fence_char, fence_len = None, 0
                out_lines.append(line)
                continue
        if fence_char is not None:
            out_lines.append(line)
            continue
        if not line.strip():
            flush_para()
            out_lines.append(line)
            continue
        para_buf.append(line)
    flush_para()
    return "\n".join(out_lines)


def sv(value) -> str:
    """1行の自由記述文字列（タイトル・feedback_ask・状態注記等）用の安全化。

    Plan 本文コピーと同じエスケープ規則を通す — 「本文は escape するが
    タイトル欄はしない」という非対称を作らないための共通ヘルパー。
    """
    return esc_vue(str(value)) if value is not None else ""


def chip(kind: str, label: str) -> str:
    return f'<span class="chip {kind}">{label}</span>'


def fb_chip(fb):
    if fb == "待ち":
        return chip("wait", "FB 待ち")
    if fb == "済":
        return chip("ok", "FB 済")
    if fb == "不要":
        return chip("neutral", "FB 不要")
    return chip("wait", "FB 未記入")


def days_label(since):
    d = wait_days(since)
    if d is None:
        return "—"
    return "本日" if d == 0 else f"{d}日"


def state_group(state: str) -> str:
    if state.startswith("未着手"):
        return "未着手"
    if state.startswith("要確認"):
        return "要確認"
    if state.startswith("進行中"):
        return "進行中"
    return "一部完了"


def build():
    todo_rows = parse_todo_rows()
    unanswered_qs, answered_qs = parse_questions()
    progress = parse_progress()
    branches = speculative_branches()
    prs = open_prs()

    # 未完了 Plan（完了以外）を収集
    backlog = []
    for row in todo_rows:
        if row["state"].startswith("完了"):
            continue
        plan_path = REPO_ROOT / row["path"]
        info = parse_plan(plan_path)
        num_m = re.search(r"(\d{4})", plan_path.name)
        backlog.append(
            {
                **row,
                **info,
                "num": num_m.group(1) if num_m else "????",
                "stem": plan_path.stem,
                "group": state_group(row["state"]),
            }
        )

    # 要フィードバックキュー: owner_feedback=待ち または フィールド未記入。
    # TODO 状態が「進行中」でも待ちなら載せる（進行中×判断待ちの握りつぶし防止）
    queue = []
    plan_nums_in_queue = set()
    for b in backlog:
        fb = b["owner_feedback"]
        if fb not in ("待ち", "済", "不要", None):
            print(f"WARN: Plan {b['num']} の owner_feedback が未知の値です: {fb!r}（待ち扱いにします）")
        if fb in ("済", "不要"):
            continue
        ask = b["feedback_ask"] or "要判断（詳細は Plan 本文参照）"
        queue.append({**b, "ask": ask, "days": wait_days(b["feedback_since"])})
        plan_nums_in_queue.add(b["num"])
    # Plan に紐づかない未回答 Question は独立エントリとして加える
    orphan_qs = [q for q in unanswered_qs if q["plan"] not in plan_nums_in_queue]
    queue.sort(key=lambda e: (-(e["days"] if e["days"] is not None else -1)))

    # ---- 出力ディレクトリ再生成 ----
    # 3階層決め打ちの REPO_ROOT 導出が壊れた場合に無関係のディレクトリを消さない防御
    assert OUT_DIR.name == "dashboard" and OUT_DIR.parent.name == "addf", OUT_DIR
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    (OUT_DIR / "plans").mkdir(parents=True)
    (OUT_DIR / ".vitepress" / "theme").mkdir(parents=True)

    # Plan 本文コピー（プランビューア。完了 Plan も含む — 番号リンクで辿れるように）
    plan_sidebar = []
    for f in sorted(PLANS_DIR.glob("[0-9]*.md")):
        (OUT_DIR / "plans" / f.name).write_text(
            esc_vue(f.read_text(encoding="utf-8")), encoding="utf-8"
        )
        plan_sidebar.append({"text": f.stem, "link": f"/plans/{f.stem}"})

    # ---- ページ: 要フィードバック（index.md）----
    longest = max((e["days"] for e in queue if e["days"] is not None), default=0)
    lines = [
        "---",
        "title: 要フィードバック",
        "---",
        "",
        "# 要フィードバック",
        "",
        "あなたの判断・レビュー・回答を待っているもの。待ちが長い順に並んでいます。",
        "",
        '<div class="stats">',
        f'<div class="stat hot"><div class="label">判断待ち</div><div class="value">{len(queue) + len(orphan_qs)}<small>件</small></div></div>',
        f'<div class="stat"><div class="label">投機ブランチ</div><div class="value">{len(branches)}<small>本</small></div></div>',
        f'<div class="stat"><div class="label">オープン PR</div><div class="value">{len(prs) if prs is not None else "?"}<small>件</small></div></div>',
        f'<div class="stat hot"><div class="label">最長の待ち</div><div class="value">{longest}<small>日</small></div></div>',
        "</div>",
        "",
        f"## オーナー判断待ちの Plan — {len(queue)}件",
        "",
    ]
    for e in queue:
        q_note = ""
        for q in unanswered_qs:
            if q["plan"] == e["num"]:
                q_note = f"（{q['id']} と同件）"
        lines += [
            f"::: details <span class=\"days\">{days_label(e['feedback_since'])}</span> "
            f"`{e['num']}` **{sv(e['title'])}** — {sv(e['ask'])} {fb_chip(e['owner_feedback'])}",
            "",
            f"- 状態: {sv(e['state'])}",
            f"- 待ちの起点: {e['feedback_since'] or '未記入（起点不明のため末尾に表示）'}{q_note}",
            f"- [Plan 本文を読む](/plans/{e['stem']})",
            "",
            ":::",
            "",
        ]
    if not queue:
        lines += ["> 判断待ちの Plan はありません 🎉", ""]

    if orphan_qs:
        lines += [f"## Plan に紐づかない未回答 Question — {len(orphan_qs)}件", ""]
        for q in orphan_qs:
            lines += [
                f"::: details <span class=\"days\">{days_label(q['since'])}</span> `{q['id']}` **{sv(q['title'])}**",
                "",
                esc_vue(q["body"]),
                "",
                ":::",
                "",
            ]

    lines += [f"## 投機ブランチ — {len(branches)}本", ""]
    if branches:
        for br in branches:
            ahead = br["ahead"]
            if ahead == 0:
                note = "main との差分 0 コミット（全て回収済み）— ブランチ削除の判断待ち"
            elif ahead is None:
                note = "main との差分を取得できませんでした（main ブランチの有無を確認）"
            else:
                note = f"main より {ahead} コミット先行（未回収）"
            lines.append(f"- `{br['name']}` — {note}")
    else:
        lines.append("> 投機ブランチはありません")
    lines.append("")

    lines += ["## オープン PR", ""]
    if prs is None:
        lines.append("> gh が利用できないため PR は取得できませんでした（`gh auth status` を確認）")
    elif not prs:
        lines.append("> レビュー待ちの PR はありません")
    else:
        for pr in prs:
            lines.append(f"- [#{pr['number']} {pr['title']}]({pr['url']})")
    lines.append("")

    if answered_qs:
        lines += [
            f"## 回答済み Questions アーカイブ — {len(answered_qs)}件",
            "",
        ]
        for q in answered_qs:
            lines.append(f"- `{q['id']}` {q['title']}")
        lines.append("")

    (OUT_DIR / "index.md").write_text("\n".join(lines), encoding="utf-8")

    # ---- ページ: 進行中タスク（active.md）----
    lines = ["---", "title: 進行中タスク", "---", "", "# 進行中タスク", ""]
    if progress:
        done = sum(1 for s, _ in progress["checklist"] if s == "x")
        total = len(progress["checklist"])
        lines += [
            f"## {sv(progress['title'])}",
            "",
            f"**サブタスク {done} / {total}**",
            "",
        ]
        for stat, item in progress["checklist"]:
            mark = "x" if stat == "x" else " "
            lines.append(f"- [{mark}] {esc_vue(item)}")
        lines.append("")
        if progress["diary"]:
            lines += [
                f"### 最新の日記 — {progress['diary']['head']}",
                "",
                esc_vue(progress["diary"]["body"]),
                "",
            ]
    else:
        lines += [
            "> 進行中のタスクはありません — 次の /addf-dev 起動時にバックログから選定されます",
            "",
        ]
    # TODO 上で「進行中」の Plan（Progress.md の現在タスクと並行しうる）もここに列挙する
    in_progress_plans = [b for b in backlog if b["group"] == "進行中"]
    if in_progress_plans:
        lines += [f"## 進行中の Plan（TODO より） — {len(in_progress_plans)}件", ""]
        for b in in_progress_plans:
            lines += [
                f"- `{b['num']}` [{sv(b['title'])}](/plans/{b['stem']}) "
                f"{fb_chip(b['owner_feedback'])}",
                f"  - {sv(b['state'])}",
            ]
        lines.append("")
    recents = recent_progresses()
    if recents:
        lines += [f"## 直近の完了タスク — {len(recents)}件", ""]
        for stem in recents:
            lines.append(f"- `{stem}`")
        lines.append("")
    (OUT_DIR / "active.md").write_text("\n".join(lines), encoding="utf-8")

    # ---- ページ: 未実施の計画（backlog.md）----
    lines = [
        "---",
        "title: 未実施の計画",
        "---",
        "",
        "# 未実施の計画",
        "",
        "未着手・一部完了の Plan バックログ。タイトルからプランビューアへ。",
        "",
    ]
    # 「進行中」は進行中タスクページ側に載せる（ページ名「未実施の計画」との整合）
    for group in ("未着手", "要確認", "一部完了"):
        items = [b for b in backlog if b["group"] == group]
        if not items:
            continue
        lines += [f"## {group} — {len(items)}件", ""]
        for b in items:
            lines += [
                f"- `{b['num']}` [{sv(b['title'])}](/plans/{b['stem']}) "
                f"{fb_chip(b['owner_feedback'])}",
                f"  - 優先度 {b['prio']} / {sv(b['state'])}",
            ]
        lines.append("")
    (OUT_DIR / "backlog.md").write_text("\n".join(lines), encoding="utf-8")

    # ---- VitePress 設定・テーマ ----
    sidebar_json = json.dumps(plan_sidebar, ensure_ascii=False, indent=2)
    config = f"""import {{ defineConfig }} from 'vitepress'

export default defineConfig({{
  title: 'ADDF ダッシュボード',
  description: 'ローカルレビューダッシュボード（生成物 — 編集しない）',
  lang: 'ja',
  ignoreDeadLinks: true,
  vite: {{ server: {{ port: 5180 }} }},
  themeConfig: {{
    sidebar: {{
      '/': [
        {{
          text: 'ダッシュボード',
          items: [
            {{ text: '要フィードバック', link: '/' }},
            {{ text: '進行中タスク', link: '/active' }},
            {{ text: '未実施の計画', link: '/backlog' }},
          ],
        }},
        {{ text: 'プランビューア', collapsed: true, items: {sidebar_json} }},
      ],
    }},
    outline: {{ label: 'このページ' }},
    footer: {{ message: '生成: {TODAY.isoformat()} · generate-dashboard.py（Plan 0058）' }},
  }},
}})
"""
    (OUT_DIR / ".vitepress" / "config.mts").write_text(config, encoding="utf-8")

    theme = """import DefaultTheme from 'vitepress/theme'
import './custom.css'
export default DefaultTheme
"""
    (OUT_DIR / ".vitepress" / "theme" / "index.mts").write_text(theme, encoding="utf-8")

    css = """:root {
  --chip-wait-ink: #8a5300; --chip-wait-bg: #f7ecda;
  --chip-ok-ink: #2c6b3f; --chip-ok-bg: #e5f1e8;
  --chip-neutral-ink: #5b6672; --chip-neutral-bg: #edf0ef;
}
.dark {
  --chip-wait-ink: #f0c380; --chip-wait-bg: #4a3a1c;
  --chip-ok-ink: #a3d9b0; --chip-ok-bg: #1e3a26;
  --chip-neutral-ink: #b6c0c8; --chip-neutral-bg: #333a40;
}
.chip {
  display: inline-block; font-size: 11px; line-height: 20px;
  padding: 0 8px; border-radius: 10px; white-space: nowrap; font-weight: 500;
}
.chip.wait { background: var(--chip-wait-bg); color: var(--chip-wait-ink); }
.chip.ok { background: var(--chip-ok-bg); color: var(--chip-ok-ink); }
.chip.neutral { background: var(--chip-neutral-bg); color: var(--chip-neutral-ink); }
.days {
  font-family: var(--vp-font-family-mono); font-variant-numeric: tabular-nums;
  font-weight: 600; color: var(--chip-wait-ink); margin-right: 4px;
}
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 16px 0 8px; }
.stat { border: 1px solid var(--vp-c-divider); border-radius: 8px; padding: 10px 14px; }
.stat .label { font-size: 12px; color: var(--vp-c-text-2); }
.stat .value { font-family: var(--vp-font-family-mono); font-size: 24px; font-weight: 600; }
.stat .value small { font-size: 12px; font-weight: 400; color: var(--vp-c-text-2); }
.stat.hot .value { color: var(--chip-wait-ink); }
@media (max-width: 640px) { .stats { grid-template-columns: repeat(2, 1fr); } }

/* サイドバーはページタブの代替 — 通常項目の視認性と現在ページのコントラストを上げる */
.VPSidebarItem.level-1 .text {
  color: var(--vp-c-text-1);
  font-size: 14px;
}
.VPSidebarItem.level-1.is-active > .item {
  background: var(--vp-c-brand-soft);
  border-radius: 6px;
}
.VPSidebarItem.level-1.is-active > .item .link { padding-left: 8px; }
.VPSidebarItem.level-1.is-active > .item .text {
  color: var(--vp-c-brand-1);
  font-weight: 700;
}
"""
    (OUT_DIR / ".vitepress" / "theme" / "custom.css").write_text(css, encoding="utf-8")

    n_q = len(queue) + len(orphan_qs)
    print(f"OK: dashboard generated at {OUT_DIR.relative_to(REPO_ROOT)}")
    print(
        f"    判断待ち {n_q}件 / 投機ブランチ {len(branches)}本 / "
        f"PR {'取得不可' if prs is None else str(len(prs)) + '件'} / "
        f"バックログ {len(backlog)}件 / Plan コピー {len(plan_sidebar)}件"
    )
    return 0


if __name__ == "__main__":
    sys.exit(build())
