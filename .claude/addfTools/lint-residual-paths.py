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

移行後の恒久検査として、docs/ 配下への ADDF 管理ファイルの新規追加（逆流）を
WARNING で検出する（マップの old が docs/ で始まるディレクトリ配下に
git 追跡ファイルが再出現したケース）。

検査から除外するファイルは paths.toml の [exclusions].files（マップ定義・
移行ロジック・テストの合成フィクスチャとして旧パス文字列を正当に含むもの）。

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
    '.claude/addf/tools/paths.toml',
    '.claude/addfTools/paths.toml',
]


def compile_pattern(old):
    """境界チェック付きの検出パターン（migrate-paths.py の compile_pattern() と同一規則）"""
    return re.compile(r'(?<![A-Za-z0-9_-])' + re.escape(old) + r'(?![A-Za-z0-9_-])')


def load_map():
    for path in MAP_CANDIDATES:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return tomllib.load(f), path
    return None, None


def tracked_files():
    r = subprocess.run(['git', 'ls-files', '-z'], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return [p for p in r.stdout.split('\0') if p]


cfg, map_path = load_map()
if cfg is None:
    print(f'SKIP: paths.toml が見つからない（探索先: {", ".join(MAP_CANDIDATES)}）。'
          'リポジトリルートで実行してください')
    sys.exit(0)

new_root = cfg.get('meta', {}).get('new_root', '.claude/addf')
if not os.path.isdir(new_root):
    print(f'SKIP: 移行前のリポジトリ（{new_root}/ が存在しない）— 残存参照は検査しない')
    sys.exit(0)

files = tracked_files()
if files is None:
    print('SKIP: git リポジトリ外のため検査できない')
    sys.exit(0)

all_entries = cfg.get('dirs', []) + cfg.get('files', []) + cfg.get('dynamic', [])
excluded = set(cfg.get('exclusions', {}).get('files', []))
# 長いキー優先＋境界チェックで、docs/plans-add の残存が docs/plans と二重報告されない
patterns = sorted(((compile_pattern(e['old']), e['old']) for e in all_entries),
                  key=lambda p: len(p[1]), reverse=True)

errors = []
warnings = []

for path in files:
    if path in excluded:
        continue
    try:
        with open(path, encoding='utf-8') as f:
            lines = f.read().splitlines()
    except (UnicodeDecodeError, OSError):
        continue  # バイナリ等は対象外
    for lineno, line in enumerate(lines, 1):
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

if errors:
    print(f'ERROR: 旧パス参照が {len(errors)} 箇所残存。'
          'migrate-paths.py rewrite で書き換えるか手動で解消するまで移行は完了しない')
    sys.exit(1)
if warnings:
    sys.exit(2)
print('OK: 旧パス残存なし（逆流もなし）')
