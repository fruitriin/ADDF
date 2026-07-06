#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""残存参照 lint — Plan 0037 移行の完了ゲート

paths.toml（単一ソース）の旧パスが git 追跡ファイルに残存していないかを検査する。
ERROR ゼロになるまで移行を完了扱いしない（「警告は出すが止めない」の禁止）。

移行前のリポジトリでは検査しない: 新構造（[meta].new_root = .claude/addf/）の
存在を検出条件にし、移行前は SKIP を明示出力する（ダウンストリーム配布時の
誤 ERROR 防止。SKIP は silent にしない — 環境起因で検査しなかったことの可視化）。
注意: new_root の存在は「apply が完走した」ことまでは保証しない。旧パス残存の
ERROR には部分適用（apply/rewrite の途中失敗）の可能性の注記を添える。

移行後の恒久検査として、docs/ 配下への ADDF 管理ファイルの新規追加（逆流）を
WARNING で検出する（マップの old が docs/ で始まるディレクトリ配下に
git 追跡ファイルが再出現したケース）。

検査から除外するファイルは paths.toml の [rewrite_exclusions].files（マップ定義・
移行ロジック・テストの合成フィクスチャとして旧パス文字列が本質的に大量にある
道具・テストのみ）。移行手順書・移行ガイド等のドキュメントはファイル除外しない —
正当な旧パス言及行に行内マーカー `residual-path: allow` を付けて行単位で除外する
（ファイル丸ごと除外はそのファイル全体が本 lint の永久盲点になるため）。

走査対象は migrate-paths.py の check / rewrite と一致させる（check「0箇所」なのに
lint で初めて ERROR になる不一致を作らない）: 全 git 追跡ファイルのうちテキストの
もの。バイナリは NUL バイト検査＋ UTF-8 デコード失敗で除外し、**symlink は除外**
する（git は symlink を blob 追跡するため、open() で辿るとリンク先 —
リポジトリ外でもよい — を読んでしまう）。

境界チェックは migrate-paths.py と同一規則
（同期契約: migrate-paths.py の compile_pattern() と挙動を同期する）:
前後が英数字・ハイフン・アンダースコアならマッチしない
（`docs/plans-add` の残存を `docs/plans` の残存として誤検出・二重検出しない）。

exit code: 0 = OK / SKIP、1 = ERROR（旧パス残存）、2 = WARNING のみ（逆流）
"""
import os
import re
import subprocess
import sys

try:
    import tomllib
except ModuleNotFoundError:
    # 受動的 lint のため欠如は SKIP（配布先で誤 ERROR を出さない）
    print(f'SKIP: tomllib がありません（Python {sys.version.split()[0]}）。'
          '`uv run --python 3.11` または Python 3.11+ で実行してください')
    sys.exit(0)

# paths.toml の探索先（移行後の新位置を優先し、移行前の旧位置にフォールバック）
MAP_CANDIDATES = [
    '.claude/addf/addfTools/paths.toml',
    '.claude/addfTools/paths.toml',
]

# 行単位の除外マーカー（コメント形式は問わない — 行内一致で判定。
# 同期契約: migrate-paths.py の EXCLUSION_MARKER と同一に保つ）
EXCLUSION_MARKER = 'residual-path: allow'

# 走査するテキストファイルのサイズ上限。超過は読み込まずスキップし件数付きで案内する
# （同期契約: migrate-paths.py の MAX_TEXT_BYTES と同一に保つ — 走査対象集合の一致）
MAX_TEXT_BYTES = 5 * 1024 * 1024
SIZE_SKIPPED = set()


def compile_pattern(old):
    """境界チェック付きの検出パターン（migrate-paths.py の compile_pattern() と同一規則）"""
    return re.compile(r'(?<![A-Za-z0-9_-])' + re.escape(old) + r'(?![A-Za-z0-9_-])')


def load_map():
    for path in MAP_CANDIDATES:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return tomllib.load(f), path
    return None, None


def read_text(path):
    """走査対象なら中身のテキストを、対象外（symlink・バイナリ等）なら None を返す
    （migrate-paths.py の read_text() と同一規則 — 走査対象の同期契約）"""
    if os.path.islink(path) or not os.path.isfile(path):
        return None
    try:
        if os.path.getsize(path) > MAX_TEXT_BYTES:
            SIZE_SKIPPED.add(path)
            return None
        with open(path, 'rb') as f:
            data = f.read()
    except OSError:
        return None
    if b'\0' in data:
        return None
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return None


# cwd 検証: 相対パス前提のため、git リポジトリ内ではルート以外の実行を ERROR にする。
# git リポジトリ外は従来どおり SKIP（配布先で誤 ERROR を出さない受動 lint の原則）
_top = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                      capture_output=True, text=True)
if _top.returncode != 0:
    print('SKIP: git リポジトリ外のため検査できない')
    sys.exit(0)
if os.path.realpath(_top.stdout.strip()) != os.path.realpath(os.getcwd()):
    print(f'ERROR: リポジトリルートで実行してください'
          f'（cwd: {os.path.realpath(os.getcwd())} / ルート: {os.path.realpath(_top.stdout.strip())}）')
    sys.exit(1)

cfg, map_path = load_map()
if cfg is None:
    print(f'SKIP: paths.toml が見つからない（探索先: {", ".join(MAP_CANDIDATES)}）')
    sys.exit(0)

new_root = cfg.get('meta', {}).get('new_root', '.claude/addf')
if not os.path.isdir(new_root):
    print(f'SKIP: 移行前のリポジトリ（{new_root}/ が存在しない）— 残存参照は検査しない')
    sys.exit(0)

r = subprocess.run(['git', 'ls-files', '-z'], capture_output=True, text=True)
if r.returncode != 0:
    print('SKIP: git ls-files が失敗したため検査できない')
    sys.exit(0)
files = [p for p in r.stdout.split('\0') if p]

all_entries = cfg.get('dirs', []) + cfg.get('files', []) + cfg.get('dynamic', [])
excluded = set(cfg.get('rewrite_exclusions', {}).get('files', []))
# 長いキー優先＋境界チェックで、docs/plans-add の残存が docs/plans と二重報告されない
patterns = sorted(((compile_pattern(e['old']), e['old']) for e in all_entries),
                  key=lambda p: len(p[1]), reverse=True)

errors = []
warnings = []

for path in files:
    if path in excluded:
        continue
    text = read_text(path)
    if text is None:
        continue  # symlink・バイナリ等は対象外
    for lineno, line in enumerate(text.splitlines(), 1):
        if EXCLUSION_MARKER in line:
            continue  # 行単位マーカー（正当な旧パス言及行）は検査しない
        remaining = line
        for pattern, old in patterns:
            if pattern.search(remaining):
                errors.append(f'{path}:{lineno}: 旧パス `{old}` が残存')
                # 長いキーでマッチした範囲を消し込み、短いキーでの二重報告を防ぐ
                remaining = pattern.sub('\0' * len(old), remaining)

# 逆流検査: docs/ 配下の ADDF 管理ディレクトリに git 追跡ファイルが再出現していないか
docs_prefixes = [e['old'] for e in cfg.get('dirs', []) if e['old'].startswith('docs/')]
for path in files:
    for prefix in docs_prefixes:
        if path.startswith(prefix + '/'):
            warnings.append(f'WARNING: docs/ 配下への逆流 — {path} は移行済みの '
                            f'{prefix} 配下に新規追加されている（{new_root} 側に置く）')

for msg in errors + warnings:
    print(msg)

if SIZE_SKIPPED:
    print(f'注意: サイズ上限（{MAX_TEXT_BYTES // (1024 * 1024)}MB）超過のため '
          f'{len(SIZE_SKIPPED)} ファイルを検査せずスキップしました。'
          '旧パス参照が残っていないか手動で確認してください:')
    for p in sorted(SIZE_SKIPPED):
        print(f'    {p}')

if errors:
    print(f'ERROR: 旧パス参照が {len(errors)} 箇所残存。'
          'migrate-paths.py rewrite で書き換えるか手動で解消するまで移行は完了しない')
    print('注記: apply/rewrite が未完了の可能性があります。'
          'migrate-paths.py check で移動残・参照残を確認してください')
    sys.exit(1)
if warnings:
    sys.exit(2)
print('OK: 旧パス残存なし（逆流もなし）')
