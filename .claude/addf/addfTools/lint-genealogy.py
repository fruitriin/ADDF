#!/usr/bin/env python3
"""Plan 系統樹 edge 行の整合検査（Plan 0056 フェーズ1）。

Plan ファイルの `## 実装状況:` ヘッダ直後に置く `edge:` フィールド（generate-dashboard.py
が読む）と、その Plan の「関連 Plan」節の記述を突き合わせ、機械可読と人間可読の
ドリフトを検出する。

検査対象:
- edge 型: derived-from / absorbed-into / revives / blocked-by / pruned の5種（Plan 0056）
- edge 構文: 型が既知で target が型に応じた形式（数値4桁・owner/external・空）
- 対象 Plan の実在: 数値 target が対象 plans ディレクトリに存在するか
- pruned edge の必須メタデータ: 「関連 Plan」節に「理由」「証拠」「復活条件」の3語が
  それぞれ現れること（書式は自由文。ラベル文字列の存在のみを機械保証する）
- 数値 target を持つ edge の「関連 Plan」節リンク併記: 対象 Plan 番号を含む
  Markdown リンクが「関連 Plan」節に存在するか

対象ディレクトリ: .claude/addf/plans-add/ と .claude/addf/plans/ の `[0-9]*.md`。
ディレクトリ不在時は SKIP。検査対象 0 件は NOTE + exit 0（ダウンストリーム互換）。

stdlib のみ使用（tomllib / pyyaml 不要 — import ガード類型の対象外・Python 3.9 互換）。

exit code:
  0 = OK（対象 0 件・SKIP 含む）
  1 = ERROR（構文エラー・対象 Plan 不在・pruned メタデータ欠落・リンク併記漏れ）
  2 = WARNING（既知型ではあるが挙動が疑わしい・注意喚起）
"""
import glob
import os
import re
import sys

VALID_TYPES = {"derived-from", "absorbed-into", "revives", "blocked-by", "pruned"}
NUMERIC_TARGET_TYPES = {"derived-from", "absorbed-into", "revives"}
# pruned メタデータの必須ラベル（大文字小文字・全半角の揺れを吸収するため小文字化して比較）
PRUNED_META_LABELS = ["理由", "証拠", "復活条件"]

HEADER_RE = re.compile(r"^##\s*実装状況[:：]")
EDGE_RE = re.compile(r"^edge:\s*(.+?)\s*$")
PLAN_NUM_RE = re.compile(r"^(\d{4})(?!\d)")
# 「関連 Plan」節見出し（レベル2〜4）。行頭アンカーで本文中の言及を除外
RELATED_HEADING_RE = re.compile(r"^(#{2,4})\s*関連\s*Plan\s*$")
FENCE_RE = re.compile(r"^\s*(?:`{3,}|~{3,})")
# 「関連 Plan」節内で Plan 番号を含む Markdown リンク（`[Plan 0053: xxx](0053-slug.md)` 等・
# `[Plan 0053](../plans/0053.md)` の相対リンクも網羅）を検出
LINK_PLAN_NUM_RE = re.compile(r"\[[^\]]*?\b(\d{4})\b[^\]]*\]\([^)]+\)")

PLAN_DIRS = [".claude/addf/plans-add", ".claude/addf/plans"]

errors = []
warnings = []
skips = []
total_files = 0
checked_files = 0


def visible_lines(lines):
    in_code = False
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_code = not in_code
            continue
        if not in_code:
            yield i, line


def parse_edges(lines):
    """行頭 `edge:` フィールドを [(行番号1始まり, type, target, 生文字列)] で返す。

    コードフェンス内は例示として除外する。
    """
    out = []
    for i, line in visible_lines(lines):
        m = EDGE_RE.match(line)
        if not m:
            continue
        raw = m.group(1)
        parts = raw.split(None, 1)
        etype = parts[0]
        target = parts[1] if len(parts) > 1 else ""
        out.append((i + 1, etype, target.strip(), raw))
    return out


def related_section(lines):
    """「関連 Plan」節の本文（見出し行の次から、同レベル以浅の次見出しまたは `---` まで）を返す。

    見出し自体が無ければ空文字列。コードフェンス内は除外しない（本文の一部として扱う）。
    """
    start = None
    section_level = None
    for i, line in enumerate(lines):
        if start is None:
            m = RELATED_HEADING_RE.match(line)
            if m:
                start = i + 1
                section_level = len(m.group(1))
                continue
        else:
            hm = re.match(r"^(#{1,6})\s", line)
            if (hm and len(hm.group(1)) <= section_level) or line.strip() == "---":
                return "\n".join(lines[start:i])
    if start is not None:
        return "\n".join(lines[start:])
    return ""


def has_header(lines):
    """`## 実装状況:` ヘッダの有無を返す（無い旧 Plan は検査から除外する信号）。"""
    for _, line in visible_lines(lines):
        if HEADER_RE.match(line):
            return True
    return False


def _plan_num_from_target(target: str):
    m = PLAN_NUM_RE.match((target or "").lstrip())
    return m.group(1) if m else None


def check_plan(path: str, all_plan_nums: set):
    global checked_files
    m_self = re.search(r"(?<!\d)(\d{4})(?!\d)", os.path.basename(path))
    self_num = m_self.group(1) if m_self else None
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if not has_header(lines):
        return
    edges = parse_edges(lines)
    if not edges:
        return
    checked_files += 1
    related = related_section(lines)

    for lineno, etype, target, raw in edges:
        loc = f"{path}:{lineno}"
        if etype not in VALID_TYPES:
            errors.append(
                f"ERROR: {loc} — 未知の edge 型 `{etype}`。有効: {', '.join(sorted(VALID_TYPES))}"
            )
            continue

        if etype == "pruned":
            if target:
                warnings.append(
                    f"WARNING: {loc} — pruned edge は target を取りません（`edge: pruned` のみ）: "
                    f"`{raw}`"
                )
            # 関連 Plan 節に3ラベルが全て現れることを検査
            if not related:
                errors.append(
                    f"ERROR: {loc} — pruned edge は「関連 Plan」節に理由・証拠・復活条件を"
                    "書くこと。本 Plan には「## 関連 Plan」節がありません"
                )
            else:
                missing = [lab for lab in PRUNED_META_LABELS if lab not in related]
                if missing:
                    errors.append(
                        f"ERROR: {loc} — pruned edge のメタデータが「関連 Plan」節に不足: "
                        f"{', '.join(missing)}（3項目とも必須。書式は自由文）"
                    )
            continue

        if etype == "blocked-by":
            tnorm = target.lower()
            if tnorm.startswith("owner") or tnorm.startswith("external"):
                continue  # target は静的キーワード。他検査なし
            num = _plan_num_from_target(target)
            if not num:
                errors.append(
                    f"ERROR: {loc} — blocked-by の対象を認識できません: `{raw}`"
                    "（owner / external / 4桁 Plan 番号）"
                )
                continue
            if num == self_num:
                errors.append(f"ERROR: {loc} — 自己参照エッジ（自 Plan `{num}` を対象にできません）")
                continue
            if num not in all_plan_nums:
                errors.append(
                    f"ERROR: {loc} — blocked-by が指す Plan `{num}` が plans ディレクトリに"
                    "存在しません"
                )
                continue
            if related and not any(
                m.group(1) == num for m in LINK_PLAN_NUM_RE.finditer(related)
            ):
                errors.append(
                    f"ERROR: {loc} — blocked-by `{num}` の Markdown リンクが「関連 Plan」節に"
                    "無い（機械可読 edge と人間可読リンクの併記が必要）"
                )
            elif not related:
                errors.append(
                    f"ERROR: {loc} — blocked-by `{num}` の説明が書ける「関連 Plan」節が"
                    "本 Plan にありません（見出し `## 関連 Plan` を追加してリンクを併記する）"
                )
            continue

        # derived-from / absorbed-into / revives
        num = _plan_num_from_target(target)
        if not num:
            errors.append(
                f"ERROR: {loc} — `{etype}` の対象 Plan 番号（4桁）を認識できません: `{raw}`"
            )
            continue
        if num == self_num:
            errors.append(f"ERROR: {loc} — 自己参照エッジ（自 Plan `{num}` を対象にできません）")
            continue
        if num not in all_plan_nums:
            errors.append(
                f"ERROR: {loc} — `{etype}` が指す Plan `{num}` が plans ディレクトリに存在しません"
            )
            continue
        if not related:
            errors.append(
                f"ERROR: {loc} — `{etype} {num}` の説明が書ける「関連 Plan」節が本 Plan に"
                "ありません（見出し `## 関連 Plan` を追加してリンクを併記する）"
            )
            continue
        if not any(m.group(1) == num for m in LINK_PLAN_NUM_RE.finditer(related)):
            errors.append(
                f"ERROR: {loc} — `{etype} {num}` の Markdown リンクが「関連 Plan」節に無い"
                "（機械可読 edge と人間可読リンクの併記が必要）"
            )


def main():
    global total_files
    all_plan_paths = []
    for plans_dir in PLAN_DIRS:
        if not os.path.isdir(plans_dir):
            skips.append(f"SKIP: {plans_dir} が存在しない")
            continue
        for path in sorted(glob.glob(f"{plans_dir}/[0-9]*.md")):
            total_files += 1
            all_plan_paths.append(path)

    # 全 Plan 番号の集合（対象 Plan 実在判定用）— plans-add と plans を合算
    all_nums = set()
    for path in all_plan_paths:
        m = re.search(r"(\d{4})", os.path.basename(path))
        if m:
            all_nums.add(m.group(1))

    for path in all_plan_paths:
        check_plan(path, all_nums)

    for msg in errors + warnings + skips:
        print(msg)

    if total_files == 0:
        print("NOTE: 検査対象 0 件 — リポジトリルートで実行しているか確認")
        return 0

    counts = f"検査 {checked_files} 件 / エッジ付き Plan（他は edge 無しのため対象外）"
    if errors:
        print(f"ERROR: 系統樹 edge 整合検査で {len(errors)} 件の ERROR（{counts}）")
        return 1
    if warnings:
        print(f"WARNING: 系統樹 edge 整合検査 — {len(warnings)} 件の WARNING（{counts}）")
        return 2
    print(f"OK: 系統樹 edge 整合検査通過（{counts}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
