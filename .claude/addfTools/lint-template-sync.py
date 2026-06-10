#!/usr/bin/env python3
"""テンプレート同期チェック — 同期が必要なファイルペアのドリフトを検出する

ペア1: ProgressTemplate.addf.md ⇔ 運用中 Progress.md（運用ルールのテキスト包含・ERROR）
       ダウンストリーム（.addf.md 版がない場合）は ProgressTemplate.md を正として比較する
ペア2: ProgressTemplate.addf.md ⇔ ProgressTemplate.md（正規化した運用ルールの相互比較・WARNING）
ペア3: CLAUDE.md ⇔ AGENTS.md（ブートシーケンス手順番号の対応・WARNING）
ペア4: CLAUDE.md ⇔ docs/guides/development-process.md（ブートシーケンス概要手順番号の対応・WARNING）

ペア5: CLAUDE.md ⇔ addf-init.md コピーリスト（参照ファイルのカバレッジ・WARNING）
       CLAUDE.md が参照する .claude/ 配下のファイルが、addf-init の Phase 3
       コピーリスト（グロブ・ディレクトリ含む）または .gitignore の ADDF マーカー
       ブロック（実行時生成ファイル）でカバーされているかを検査する。
       カバー漏れは外部起動導入したダウンストリームでの参照切れになる。

ペア2〜5 は片方のファイルが存在しない場合 SKIP する（ADDF 本体固有ファイルは
ダウンストリームプロジェクトに存在しないため、欠如はドリフトではない）。

不一致の WARNING には git log による最終更新日ヒントを併記する
（どちらが新しいか＝どちらを正として同期すべきかの判断材料）。

exit code: 0 = 全一致 / 1 = ERROR あり / 2 = WARNING のみ
"""
import fnmatch
import os
import re
import subprocess
import sys
from collections import Counter

errors = []
warnings = []
skips = []


def extract_section(path, header_prefix):
    """header_prefix で始まる見出し行から、次の `## ` 見出しまたは水平線 `---` までの行リストを返す"""
    with open(path) as f:
        lines = f.read().splitlines()
    out, in_section, in_code = [], False, False
    for line in lines:
        if not in_section:
            if line.startswith(header_prefix):
                in_section = True
            continue
        if line.startswith('```'):
            in_code = not in_code
        if not in_code and (line.startswith('## ') or line.strip() == '---'):
            break
        out.append(line)
    return out if in_section else None


def last_commit_date(path):
    try:
        r = subprocess.run(
            ['git', 'log', '-1', '--format=%cs', '--', path],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return '不明'
        return r.stdout.strip() or '未コミット'
    except Exception:
        return '不明'


def git_hint(path_a, path_b):
    return (f'    ヒント(最終更新): {path_a} = {last_commit_date(path_a)} / '
            f'{path_b} = {last_commit_date(path_b)}')


def check_pair1():
    """テンプレートの運用ルールが Progress.md に全て含まれているか（ERROR）"""
    tmpl_path = '.claude/templates/ProgressTemplate.addf.md'
    if not os.path.exists(tmpl_path):  # ダウンストリームでは無印版が正
        tmpl_path = '.claude/templates/ProgressTemplate.md'
    prog_path = '.claude/Progress.md'
    if not os.path.exists(tmpl_path) or not os.path.exists(prog_path):
        skips.append(f'[1] SKIP: {tmpl_path} または {prog_path} が存在しない')
        return
    tmpl = extract_section(tmpl_path, '## 運用ルール')
    prog = extract_section(prog_path, '## 運用ルール')
    if tmpl is None or prog is None:
        errors.append(f'[1] ERROR: {tmpl_path} または {prog_path} に「## 運用ルール」が見つからない')
        return
    prog_text = '\n'.join(prog)
    missing = [s for s in (line.strip() for line in tmpl) if s and s not in prog_text]
    if missing:
        msg = [f'[1] ERROR: {prog_path} の運用ルールがテンプレート（{tmpl_path}）と乖離（テンプレートを正として同期する）:']
        msg += [f'    MISSING: {m}' for m in missing]
        errors.append('\n'.join(msg))


def check_pair2():
    """ProgressTemplate.addf.md ⇔ ProgressTemplate.md の運用ルールを正規化して相互比較（WARNING）"""
    addf_path = '.claude/templates/ProgressTemplate.addf.md'
    down_path = '.claude/templates/ProgressTemplate.md'
    if not os.path.exists(addf_path) or not os.path.exists(down_path):
        skips.append(f'[2] SKIP: {addf_path} がない（ダウンストリームでは対象外）')
        return
    addf = extract_section(addf_path, '## 運用ルール')
    down = extract_section(down_path, '## 運用ルール')
    if addf is None or down is None:
        errors.append(f'[2] ERROR: {addf_path} または {down_path} に「## 運用ルール」が見つからない')
        return

    # ペア2専用ホワイトリスト: ADDF 版にのみ存在してよい意図的差分（strip 済みで比較）
    whitelist_addf_only = {
        '- ADD フレームワークテスト: `bash .claude/tests/run-all.sh`',
    }

    def normalize(lines, is_addf):
        out = []
        for line in lines:
            s = line.strip()
            if not s:
                continue
            if is_addf and s in whitelist_addf_only:
                continue
            # テンプレート自己参照パスは意図的差分のため正規化して比較する
            out.append(s.replace('ProgressTemplate.addf.md', 'ProgressTemplate.md'))
        return out

    addf_count = Counter(normalize(addf, True))
    down_count = Counter(normalize(down, False))
    only_addf = list((addf_count - down_count).elements())
    only_down = list((down_count - addf_count).elements())
    if only_addf or only_down:
        msg = [f'[2] WARNING: {addf_path} と {down_path} の運用ルールが乖離:']
        msg += [f'    ADDF版のみ: {s}' for s in only_addf]
        msg += [f'    ダウンストリーム版のみ: {s}' for s in only_down]
        msg.append(git_hint(addf_path, down_path))
        warnings.append('\n'.join(msg))


def boot_steps(path, header_prefix):
    """ブートシーケンスの手順番号列を抽出する（トップレベル: `N. ` / 枝番: `- N.M. `）"""
    section = extract_section(path, header_prefix)
    if section is None:
        return None
    steps = []
    for line in section:
        m = re.match(r'(\d+)\.\s', line)  # 行頭アンカーで入れ子リストを除外
        if m:
            steps.append(m.group(1))
            continue
        m = re.match(r'\s*-\s*(\d+\.\d+)\.\s', line)
        if m:
            steps.append(m.group(1))
    return steps


def check_boot_pair(pair_no, base, base_header, other, other_header, label):
    if not os.path.exists(base) or not os.path.exists(other):
        missing = base if not os.path.exists(base) else other
        skips.append(f'[{pair_no}] SKIP: {missing} が存在しない')
        return
    base_steps = boot_steps(base, base_header)
    other_steps = boot_steps(other, other_header)
    if base_steps is None or other_steps is None:
        missing = base if base_steps is None else other
        errors.append(f'[{pair_no}] ERROR: {missing} にブートシーケンス見出しが見つからない')
        return
    if base_steps != other_steps:
        warnings.append(
            f'[{pair_no}] WARNING: {label} の手順番号が対応していない:\n'
            f'    {base} = {", ".join(base_steps)}\n'
            f'    {other} = {", ".join(other_steps)}\n'
            + git_hint(base, other)
        )


def claude_md_references(path):
    """CLAUDE.md が @メンション/バッククオートで参照する .claude/ 配下のファイルパスを返す

    コードブロック内は例示パスの可能性があるため除外する。
    検査対象を CLAUDE.md に限定するのは意図的: CLAUDE.repo.example.md や
    テンプレート群が参照するファイルは `.claude/templates/` 等のディレクトリ丸ごと
    コピーでカバーされるため、参照切れの主リスクは CLAUDE.md 直下参照に集中する。
    """
    with open(path) as f:
        lines = f.read().splitlines()
    refs = set()
    in_code = False
    for line in lines:
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        # @.claude/Feedback.md 形式（@メンション）
        refs.update(re.findall(r'@(\.claude/[^\s`]+\.\w+)', line))
        # `.claude/Questions.md` 形式（バッククオート内・拡張子付きファイルのみ）
        refs.update(re.findall(r'`(\.claude/[^\s`]+\.\w+)`', line))
    return sorted(refs)


def gitignore_addf_block(path):
    """マーカーブロック `# --- ADDF Framework ---` 〜 `# --- /ADDF Framework ---` 内のエントリを返す"""
    if not os.path.exists(path):
        return []
    with open(path) as f:
        lines = f.read().splitlines()
    out, in_block = [], False
    for line in lines:
        s = line.strip()
        if s.startswith('# --- /ADDF Framework'):  # 重複ブロックにも対応するため break しない
            in_block = False
            continue
        if s.startswith('# --- ADDF Framework'):
            in_block = True
            continue
        if in_block and s and not s.startswith('#'):
            out.append(s)
    return out


def check_pair5():
    """CLAUDE.md が参照する .claude/ 配下ファイルが addf-init コピーリストでカバーされているか（WARNING）"""
    claude_path = 'CLAUDE.md'
    init_path = '.claude/commands/addf-init.md'
    if not os.path.exists(claude_path) or not os.path.exists(init_path):
        missing = claude_path if not os.path.exists(claude_path) else init_path
        skips.append(f'[5] SKIP: {missing} が存在しない')
        return
    refs = claude_md_references(claude_path)
    with open(init_path) as f:
        init_text = f.read()
    # addf-init.md 本文中のバッククオートパス（コピーリストのエントリ。グロブ・ディレクトリ含む）
    # `.claude/` 単体（Phase 1 の状態判定で言及されるルート）はコピーエントリではないため除外
    init_entries = set(re.findall(r'`(\.claude/[^\s`]+)`', init_text)) - {'.claude/'}
    # .gitignore の ADDF マーカーブロック（実行時生成ファイルはコピー対象外として正当）
    ignore_entries = gitignore_addf_block('.gitignore')

    def covered(ref):
        if ref in init_entries:
            return True
        for entry in init_entries:
            if entry.endswith('/') and ref.startswith(entry):  # ディレクトリ丸ごとコピー
                return True
            if '*' in entry and fnmatch.fnmatch(ref, entry):  # グロブ指定
                return True
        for entry in ignore_entries:
            if entry.endswith('/') and ref.startswith(entry):
                return True
            if fnmatch.fnmatch(ref, entry):
                return True
        return False

    uncovered = [r for r in refs if not covered(r)]
    if uncovered:
        msg = [f'[5] WARNING: {claude_path} が参照する以下のファイルが {init_path} の'
               f'コピーリスト・.gitignore ADDF ブロックのいずれでもカバーされていない'
               f'（外部起動導入したダウンストリームで参照切れになる）:']
        msg += [f'    UNCOVERED: {r}' for r in uncovered]
        msg.append(git_hint(claude_path, init_path))
        warnings.append('\n'.join(msg))


check_pair1()
check_pair2()
check_boot_pair(3, 'CLAUDE.md', '## ブートシーケンス',
                'AGENTS.md', '## Boot Sequence',
                'CLAUDE.md ⇔ AGENTS.md ブートシーケンス')
check_boot_pair(4, 'CLAUDE.md', '## ブートシーケンス',
                'docs/guides/development-process.md', '## ブートシーケンス',
                'CLAUDE.md ⇔ development-process.md ブートシーケンス概要')
check_pair5()

for msg in errors + warnings + skips:
    print(msg)

if errors:
    sys.exit(1)
if warnings:
    sys.exit(2)
print('OK: 同期チェック通過 (1: Progress.md / 2: ProgressTemplate / 3: AGENTS.md / 4: development-process.md / 5: addf-init コピーリスト)')
