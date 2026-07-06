#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Plan 0037 パス移行 — paths.toml（単一ソース）駆動の移動＋参照書き換え

使い方（リポジトリルートで実行する。ルート以外の cwd では ERROR）:
  uv run --python 3.11 migrate-paths.py [check]   # 既定。何も変更しない
  uv run --python 3.11 migrate-paths.py apply     # backup ref 作成 → git mv 一括実行
  uv run --python 3.11 migrate-paths.py rewrite   # 旧パス参照を新パスへ書き換え
  （uv が無ければ python3（3.11+）で直接実行する）

モード:
  check   移動対象の実在・移動先の衝突・旧パス参照の全数（ファイル数・箇所数）と
          マッチ例（rewrite 前の誤爆候補の目視確認用）を提示するのみ。
          exit 0 = 実行可能 / 1 = ブロッカーあり
  apply   作業ツリーが clean であることを確認し、backup ref
          （paths.toml [meta].backup_ref）を作成してから git mv をまとめて実行する。
          既存の backup ref は上書きしない（「本当の移行前」の巻き戻し点を
          静かに失わないため ERROR で拒否する）。
          コミットは**しない** — git mv コミットと参照書き換えコミットを分離できる
          ように、コミットは呼び出し側の責務とする（revert 一発で戻せる原子性）
  rewrite 全 git 追跡テキストファイルの旧パス参照を新パスに書き換える。
          apply 分のコミット後に実行する（dirty なら拒否）。
          apply 未実施（[meta].new_root 不在）の場合も ERROR で拒否する —
          参照だけが実在しないパスへ一括で書き換わる事故を防ぐ

走査対象（check の参照数と rewrite の書き換えで共通。lint-residual-paths.py の
検査対象とも一致させる — check「0箇所」なのに lint で初めて ERROR になる不一致を
作らない）:
  全 git 追跡ファイルのうちテキストのもの。バイナリは NUL バイト検査＋
  UTF-8 デコード失敗で除外する（拡張子に依存しない — Makefile / Dockerfile /
  拡張子なしスクリプトも対象に入る）。**symlink は除外する** — git は symlink を
  blob として追跡するため、open() で辿るとリンク先（リポジトリ外でもよい）を
  読み書きしてしまう（リポジトリ外書き込みの攻撃経路になる）。

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
    '.claude/addf/addfTools/paths.toml',
    '.claude/addfTools/paths.toml',
]

# check のマッチ例表示の上限（旧パスごと）と1行の最大表示幅
SAMPLE_LIMIT = 3
SAMPLE_WIDTH = 100


def run_git(*args, check=False):
    r = subprocess.run(['git', *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f'ERROR: git {" ".join(args)} が失敗: {r.stderr.strip()}')
        sys.exit(1)
    return r


def ensure_repo_root():
    """cwd が git リポジトリのルートであることを検証する（相対パス前提の誤動作防止）"""
    r = run_git('rev-parse', '--show-toplevel')
    if r.returncode != 0:
        print('ERROR: git リポジトリ内で実行してください')
        sys.exit(1)
    top = os.path.realpath(r.stdout.strip())
    cwd = os.path.realpath(os.getcwd())
    if top != cwd:
        print(f'ERROR: リポジトリルートで実行してください（cwd: {cwd} / ルート: {top}）')
        sys.exit(1)


def entries(cfg):
    """dirs → files → dynamic の順で (entry, kind) を返す"""
    for e in cfg.get('dirs', []):
        yield e, 'dir'
    for e in cfg.get('files', []):
        yield e, 'file'
    for e in cfg.get('dynamic', []):
        yield e, 'dynamic'


def validate_map(cfg):
    """マップの軽量整合チェック: immovable と移動エントリの old が重複していないこと"""
    olds = {e['old'] for e, _ in entries(cfg)}
    immovable = set(cfg.get('immovable', {}).get('paths', []))
    dup = sorted(olds & immovable)
    if dup:
        print(f'ERROR: paths.toml の不整合 — immovable と移動エントリ（old）が重複: {dup}')
        sys.exit(1)


def load_map():
    """paths.toml を読み、(設定 dict, 読み込み元パス) を返す。無ければ ERROR 終了"""
    for path in MAP_CANDIDATES:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                cfg = tomllib.load(f)
            validate_map(cfg)
            return cfg, path
    print(f'ERROR: paths.toml が見つかりません（探索先: {", ".join(MAP_CANDIDATES)}）。'
          'リポジトリルートで実行してください')
    sys.exit(1)


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


def tracked_files():
    r = run_git('ls-files', '-z', check=True)
    return [p for p in r.stdout.split('\0') if p]


def read_text(path):
    """走査対象なら中身のテキストを、対象外なら None を返す。

    - symlink は除外: git は symlink を blob 追跡するため、open() で辿ると
      リンク先（リポジトリ外でもよい）を読み書きしてしまう
    - バイナリは NUL バイト検査＋ UTF-8 デコード失敗で除外（拡張子に依存しない）
    """
    if os.path.islink(path) or not os.path.isfile(path):
        return None
    try:
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


def scan_targets(cfg):
    """(path, text) を返すイテレータ。除外リスト（rewrite_exclusions）適用済み"""
    excluded = set(cfg.get('rewrite_exclusions', {}).get('files', []))
    for path in tracked_files():
        if path in excluded:
            continue
        text = read_text(path)
        if text is not None:
            yield path, text


def is_tracked(path):
    """path（ファイルまたはディレクトリ）配下に git 追跡ファイルがあるか"""
    r = run_git('ls-files', '--', path)
    return bool(r.stdout.strip())


def _is_empty_dir(path):
    return os.path.isdir(path) and not os.path.islink(path) and not os.listdir(path)


def preflight(cfg):
    """移動計画を検査し (moves, skips, infos, problems) を返す。

    moves    = 実行する移動 [(old, new, kind)]
    skips    = optional で旧パスが無いエントリ（明示出力する — silent 無効化の禁止）
    infos    = 旧パスが無く新パスが有る（移行済みとみなす）
    problems = ブロッカー（衝突・必須エントリの欠如）

    移動先が**空ディレクトリ**の場合は衝突扱いしない（apply 途中クラッシュで
    残った空の中間ディレクトリは git 的に clean のまま preflight を永久ブロック
    しうる。apply が rmdir してから移動する）。
    """
    moves, skips, infos, problems = [], [], [], []
    for e, kind in entries(cfg):
        old, new = e['old'], e['new']
        optional = e.get('optional', True)
        old_exists = os.path.lexists(old)
        new_exists = os.path.lexists(new)
        if old_exists and new_exists and not _is_empty_dir(new):
            problems.append(
                f'衝突: {new} が既に存在する（{old} の移動先）。中身を確認し、'
                '以前の移行途中の残骸で不要なら削除（必要ならリネームで退避）してから再実行する')
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


def scan_references(cfg):
    """旧パス参照の全数とマッチ例を集計する。

    {old: {'files': set, 'count': int, 'samples': [(path, lineno, line)]}}
    長いキー優先＋マッチ済み範囲の消し込みで、docs/plans-add の参照を
    docs/plans の参照として二重計上しない。
    """
    reps = sorted_replacements(cfg)
    stats = {old: {'files': set(), 'count': 0, 'samples': []} for _, old, _ in reps}
    for path, text in scan_targets(cfg):
        for lineno, line in enumerate(text.splitlines(), 1):
            remaining = line
            for pattern, old, _ in reps:
                n = len(pattern.findall(remaining))
                if not n:
                    continue
                s = stats[old]
                s['files'].add(path)
                s['count'] += n
                if len(s['samples']) < SAMPLE_LIMIT:
                    s['samples'].append((path, lineno, line.strip()))
                remaining = pattern.sub(lambda m: '\0' * len(m.group(0)), remaining)
    return stats


def migrated_tool_dir(cfg):
    """移行後のツールディレクトリ（addfTools エントリの new）を返す"""
    for e in cfg.get('dirs', []):
        if e['old'] == '.claude/addfTools':
            return e['new']
    return '.claude/addfTools'


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
    print(f'（マッチ例は旧パスごとに先頭 {SAMPLE_LIMIT} 件。rewrite 前の誤爆候補の目視確認用）')
    total_refs = 0
    for old, s in scan_references(cfg).items():
        if not s['count']:
            continue
        total_refs += s['count']
        print(f'{old}: {len(s["files"])} ファイル / {s["count"]} 箇所')
        for path, lineno, line in s['samples']:
            if len(line) > SAMPLE_WIDTH:
                line = line[:SAMPLE_WIDTH] + '…'
            print(f'    例: {path}:{lineno}: {line}')
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
    if run_git('show-ref', '--verify', '--quiet', backup_ref).returncode == 0:
        print(f'ERROR: backup ref {backup_ref} が既に存在します（以前の apply の巻き戻し点）。\n'
              '「本当の移行前」の巻き戻し点を静かに失わないため、上書きしません。\n'
              f'  以前の移行を巻き戻してやり直す場合: git reset --hard {backup_ref}\n'
              f'  この ref が不要と確認できた場合のみ: git update-ref -d {backup_ref} '
              'を実行してから apply をやり直してください')
        sys.exit(1)
    run_git('update-ref', backup_ref, 'HEAD', check=True)
    print(f'backup ref 作成: {backup_ref} → HEAD')

    for line in skips + infos:
        print(line)
    for old, new, kind in moves:
        os.makedirs(os.path.dirname(new), exist_ok=True)
        if _is_empty_dir(new):
            # 途中クラッシュ等で残った空ディレクトリは衝突ではない（preflight と対。
            # rmdir しないと git mv / shutil.move がディレクトリ内へ移動してしまう）
            os.rmdir(new)
        if is_tracked(old):
            run_git('mv', old, new, check=True)
            print(f'git mv ({kind}): {old} → {new}')
        else:
            # 動的生成ファイル等の git 未追跡はファイルシステム移動
            shutil.move(old, new)
            print(f'mv ({kind}, 未追跡): {old} → {new}')

    tools_dir = migrated_tool_dir(cfg)
    print(f'\n完了: {len(moves)} 件を移動しました。**ここでコミットしてください**'
          '（git mv 単独のコミット — 参照書き換えと混ぜない。例: git add -A && git commit）\n'
          '続けて参照書き換えを別コミットにします。**ツール自身も移動済みのため新パスで実行**:\n'
          f'  uv run --python 3.11 {tools_dir}/migrate-paths.py rewrite\n'
          f'  （uv が無ければ: python3 {tools_dir}/migrate-paths.py rewrite）\n'
          f'巻き戻す場合: git reset --hard {backup_ref}')


def mode_rewrite(cfg, map_path):
    new_root = cfg.get('meta', {}).get('new_root', '.claude/addf')
    if not os.path.isdir(new_root):
        print(f'ERROR: {new_root}/ が存在しません。apply（git mv）を先に実行してください'
              '（apply 前に rewrite すると、参照だけが実在しないパスへ一括で書き換わる）')
        sys.exit(1)
    ensure_clean_tree('apply（git mv）分を先にコミットしてから rewrite してください')
    reps = sorted_replacements(cfg)
    changed_files = 0
    total = 0
    for path, text in scan_targets(cfg):
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
    tools_dir = migrated_tool_dir(cfg)
    print(f'完了: {changed_files} ファイル / {total} 箇所を書き換えました。'
          'ここでコミットし、残存ゼロを確認してください:\n'
          f'  uv run --python 3.11 {tools_dir}/lint-residual-paths.py\n'
          f'  （uv が無ければ: python3 {tools_dir}/lint-residual-paths.py）\n'
          '\n'
          '注意: 以下は rewrite の書き換え対象外です。移行後に手動確認してください（lint も検出できません）:\n'
          '  - git 追跡外のファイル（.claude/settings.local.json の許可ルール等）に残る旧パス\n'
          '  - 相対階層参照（SCRIPT_DIR/../.. 等）・os.path.join / 文字列連結で組み立てるパス断片\n'
          '  - Markdown の相対リンク（../../ 等。ファイルの階層が変わるとずれる）\n'
          '  - コンパイル済みバイナリ内のパス（ソース修正＋再ビルドが必要）\n'
          '  確認後、プロジェクト自身のテストを一度回すことを推奨します')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if mode not in ('check', 'apply', 'rewrite'):
        print(f'ERROR: 不明なモード: {mode}（check / apply / rewrite）')
        sys.exit(1)
    ensure_repo_root()
    cfg, map_path = load_map()
    if mode == 'check':
        mode_check(cfg, map_path)
    elif mode == 'apply':
        mode_apply(cfg, map_path)
    else:
        mode_rewrite(cfg, map_path)


if __name__ == '__main__':
    main()
