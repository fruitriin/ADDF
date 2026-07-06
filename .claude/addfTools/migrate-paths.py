#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Plan 0037 パス移行 — paths.toml（単一ソース）駆動の移動＋参照書き換え

使い方（リポジトリルートで実行する）:
  uv run --python 3.11 migrate-paths.py [check]   # 既定。何も変更しない
  uv run --python 3.11 migrate-paths.py apply     # backup ref 作成 → git mv 一括実行
  uv run --python 3.11 migrate-paths.py rewrite   # 旧パス参照を新パスへ書き換え
  （uv が無ければ python3（3.11+）で直接実行する）

モード:
  check   移動対象の実在・移動先の衝突・旧パス参照の全数（ファイル数・箇所数）を
          提示するのみ。exit 0 = 実行可能 / 1 = ブロッカーあり
  apply   作業ツリーが clean であることを確認し、backup ref
          （paths.toml [meta].backup_ref）を作成してから git mv をまとめて実行する。
          コミットは**しない** — git mv コミットと参照書き換えコミットを分離できる
          ように、コミットは呼び出し側の責務とする（revert 一発で戻せる原子性）
  rewrite 全 git 追跡テキストファイルの旧パス参照を新パスに書き換える。
          apply 分のコミット後に実行する（dirty なら拒否）

境界チェック:
  `docs/plans` の置換が `docs/plans-add` に誤マッチしない等のため、長いキーから
  順に置換し、置換対象の前後が英数字・ハイフン・アンダースコアの場合は置換しない。
  この境界規則は lint-residual-paths.py の検出規則と同一に保つ（同期契約:
  lint-residual-paths.py の compile_pattern() と挙動を同期する）。

存在≠所有:
  docs/ は paths.toml の ADDF 管理サブディレクトリ単位でのみ移動する。
  docs/ 直下のその他ファイル（GitHub Pages コンテンツ等）はマップに載っておらず、
  本スクリプトは一切触れない。

exit code: 0 = OK / 1 = ERROR（拒否・失敗）
"""
import os
import re
import shutil
import subprocess
import sys

try:
    import tomllib
except ModuleNotFoundError:
    # 変更系スクリプトのため ERROR 類型（実行できていないのに成功を装わない）
    print(f'ERROR: tomllib がありません（Python {sys.version.split()[0]}）。'
          '`uv run --python 3.11` または Python 3.11+ で実行してください')
    sys.exit(1)

# paths.toml の探索先（移行後の新位置を優先し、移行前の旧位置にフォールバック）
MAP_CANDIDATES = [
    '.claude/addf/tools/paths.toml',
    '.claude/addfTools/paths.toml',
]

# rewrite / check の参照走査対象とするテキストファイル（拡張子・基底名）
TEXT_SUFFIXES = ('.md', '.markdown', '.py', '.sh', '.bash', '.toml', '.json',
                 '.yml', '.yaml', '.txt', '.html', '.css', '.js', '.ts',
                 '.swift', '.example')
TEXT_BASENAMES = {'.gitignore', '.gitattributes', '.claudeignore', '.editorconfig'}


def load_map():
    """paths.toml を読み、(設定 dict, 読み込み元パス) を返す。無ければ ERROR 終了"""
    for path in MAP_CANDIDATES:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                cfg = tomllib.load(f)
            return cfg, path
    print(f'ERROR: paths.toml が見つかりません（探索先: {", ".join(MAP_CANDIDATES)}）。'
          'リポジトリルートで実行してください')
    sys.exit(1)


def entries(cfg):
    """dirs → files → dynamic の順で (entry, kind) を返す"""
    for e in cfg.get('dirs', []):
        yield e, 'dir'
    for e in cfg.get('files', []):
        yield e, 'file'
    for e in cfg.get('dynamic', []):
        yield e, 'dynamic'


def compile_pattern(old):
    """境界チェック付きの置換パターン。

    前後が英数字・ハイフン・アンダースコアなら別トークンの一部とみなして
    マッチしない（`docs/plans` が `docs/plans-add` や `docs/plans-addendum` の
    内部に誤マッチしない）。`/`・`@`・バッククオート・行頭行末は境界として許容する。
    """
    return re.compile(r'(?<![A-Za-z0-9_-])' + re.escape(old) + r'(?![A-Za-z0-9_-])')


def sorted_replacements(cfg):
    """(pattern, old, new) を old の長い順に返す（長いキー優先の置換順序）"""
    reps = [(compile_pattern(e['old']), e['old'], e['new'])
            for e, _ in entries(cfg)]
    return sorted(reps, key=lambda r: len(r[1]), reverse=True)


def run_git(*args, check=False):
    r = subprocess.run(['git', *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f'ERROR: git {" ".join(args)} が失敗: {r.stderr.strip()}')
        sys.exit(1)
    return r


def tracked_files():
    r = run_git('ls-files', '-z', check=True)
    return [p for p in r.stdout.split('\0') if p]


def is_text_candidate(path):
    base = os.path.basename(path)
    return base in TEXT_BASENAMES or path.endswith(TEXT_SUFFIXES)


def rewrite_targets(cfg):
    excluded = set(cfg.get('exclusions', {}).get('files', []))
    return [p for p in tracked_files()
            if is_text_candidate(p) and p not in excluded]


def is_tracked(path):
    """path（ファイルまたはディレクトリ）配下に git 追跡ファイルがあるか"""
    r = run_git('ls-files', '--', path)
    return bool(r.stdout.strip())


def preflight(cfg):
    """移動計画を検査し (moves, skips, infos, problems) を返す。

    moves    = 実行する移動 [(old, new, kind)]
    skips    = optional で旧パスが無いエントリ（明示出力する — silent 無効化の禁止）
    infos    = 旧パスが無く新パスが有る（移行済みとみなす）
    problems = ブロッカー（衝突・必須エントリの欠如）
    """
    moves, skips, infos, problems = [], [], [], []
    for e, kind in entries(cfg):
        old, new = e['old'], e['new']
        optional = e.get('optional', True)
        old_exists = os.path.lexists(old)
        new_exists = os.path.lexists(new)
        if old_exists and new_exists:
            problems.append(f'衝突: {new} が既に存在する（{old} の移動先）')
        elif old_exists:
            moves.append((old, new, kind))
        elif new_exists:
            infos.append(f'移行済み: {old} → {new}（旧パスなし・新パスあり）')
        elif optional:
            skips.append(f'SKIP: {old} は存在しない（optional — このプロジェクトには無い）')
        else:
            problems.append(f'必須エントリ欠如: {old} も {new} も存在しない'
                            '（ADDF プロジェクトのルートで実行しているか確認する）')
    return moves, skips, infos, problems


def count_references(cfg):
    """旧パス参照の全数を数える。{old: (ファイル数, 箇所数)} を返す"""
    reps = sorted_replacements(cfg)
    counts = {old: [set(), 0] for _, old, _ in reps}
    for path in rewrite_targets(cfg):
        try:
            with open(path, encoding='utf-8') as f:
                text = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        # 長いキー優先: マッチ済み範囲を消し込みながら数える（docs/plans-add の
        # 参照を docs/plans の参照として二重計上しない）
        for pattern, old, _ in reps:
            def _blank(m):
                counts[old][0].add(path)
                counts[old][1] += 1
                return '\0' * len(m.group(0))
            text = pattern.sub(_blank, text)
    return {old: (len(files), n) for old, (files, n) in counts.items()}


def mode_check(cfg, map_path):
    print(f'マップ: {map_path}')
    moves, skips, infos, problems = preflight(cfg)
    print('\n--- 移動計画 ---')
    for old, new, kind in moves:
        print(f'MOVE ({kind}): {old} → {new}')
    for line in skips + infos:
        print(line)
    for line in problems:
        print(f'ERROR: {line}')
    print('\n--- 旧パス参照の全数（git 追跡テキストファイル・除外リスト適用後）---')
    total_refs = 0
    for old, (nfiles, nrefs) in count_references(cfg).items():
        total_refs += nrefs
        if nrefs:
            print(f'{old}: {nfiles} ファイル / {nrefs} 箇所')
    print(f'参照合計: {total_refs} 箇所（`rewrite` で書き換える）')
    if problems:
        print('\nERROR: ブロッカーがあります。解消してから apply してください')
        sys.exit(1)
    print(f'\nOK: 移動 {len(moves)} 件・スキップ {len(skips)} 件。'
          '`apply` で実行できます（何も変更していません）')


def ensure_clean_tree(hint):
    r = run_git('status', '--porcelain', check=True)
    if r.stdout.strip():
        print(f'ERROR: 作業ツリーが dirty です。{hint}')
        print(r.stdout.rstrip())
        sys.exit(1)


def mode_apply(cfg, map_path):
    ensure_clean_tree('コミットまたは退避してから apply してください')
    moves, skips, infos, problems = preflight(cfg)
    for line in problems:
        print(f'ERROR: {line}')
    if problems:
        sys.exit(1)
    if not moves:
        print('ERROR: 移動対象がありません（既に移行済みの可能性があります）')
        sys.exit(1)

    backup_ref = cfg.get('meta', {}).get('backup_ref', 'refs/backup/pre-0037-migration')
    run_git('update-ref', backup_ref, 'HEAD', check=True)
    print(f'backup ref 作成: {backup_ref} → HEAD')

    for line in skips + infos:
        print(line)
    for old, new, kind in moves:
        os.makedirs(os.path.dirname(new), exist_ok=True)
        if is_tracked(old):
            run_git('mv', old, new, check=True)
            print(f'git mv ({kind}): {old} → {new}')
        else:
            # 動的生成ファイル等の git 未追跡はファイルシステム移動
            shutil.move(old, new)
            print(f'mv ({kind}, 未追跡): {old} → {new}')

    print(f'\n完了: {len(moves)} 件を移動しました。**ここでコミットしてください**'
          '（git mv 単独のコミット — 参照書き換えと混ぜない）。'
          '続けて `migrate-paths.py rewrite` で参照を書き換え、別コミットにします。'
          f'巻き戻す場合: git reset --hard {backup_ref}')


def mode_rewrite(cfg, map_path):
    ensure_clean_tree('apply（git mv）分を先にコミットしてから rewrite してください')
    reps = sorted_replacements(cfg)
    changed_files = 0
    total = 0
    for path in rewrite_targets(cfg):
        try:
            with open(path, encoding='utf-8') as f:
                text = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        new_text = text
        n_file = 0
        for pattern, old, new in reps:
            new_text, n = pattern.subn(new, new_text)
            n_file += n
        if n_file:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_text)
            changed_files += 1
            total += n_file
    print(f'完了: {changed_files} ファイル / {total} 箇所を書き換えました。'
          'ここでコミットし、lint-residual-paths.py で残存ゼロを確認してください')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if mode not in ('check', 'apply', 'rewrite'):
        print(f'ERROR: 不明なモード: {mode}（check / apply / rewrite）')
        sys.exit(1)
    cfg, map_path = load_map()
    if mode == 'check':
        mode_check(cfg, map_path)
    elif mode == 'apply':
        mode_apply(cfg, map_path)
    else:
        mode_rewrite(cfg, map_path)


if __name__ == '__main__':
    main()
