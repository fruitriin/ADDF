---
title: CLI の git 連携と CI しきい値の定型
created: 2026-06-11
last_verified: 2026-06-11
depends_on: []
status: active
---

# CLI の git 連携と CI しきい値の定型

> 出典: MagiaMagica (コード可視化ツール) Phase 3.3 (CI 統合) で確立

解析系 CLI に「リビジョン比較モード」と「PR 自動コメント + 最小しきい値判定」を足すときの定型。

## 発見した知見

### 1. git サブプロセスは専用モジュールに閉じ込める

git バイナリへの依存は `gitio.rs` のような専用モジュールに隔離し、外には
`show_file_at(rev, file)` / `changed_rs_files(rev, cwd)` / `repo_root(cwd)` の
意味単位だけを公開する (POSD 情報隠蔽)。実行形は `git -C <dir> <args>` +
失敗時は stderr を含むユーザー向けエラーに統一する。

- パス解決は `ls-files --full-name` で「現在のインデックス上のリポジトリ相対パス」に
  正規化してから `git show REV:path` する。**リネームを跨ぐ比較は追わない**と
  ドキュメントに明記する (暗黙の挙動にしない)
- git 管理外のファイルは「git add 済みのファイルのみ比較できます」の案内エラー

### 2. 複数系統の入力は入口で正規化する

「ファイル2つ」と「--git <REV> + 作業ツリー」の2系統は、入口で
`DiffSources { source, label }` ペアに正規化すると後段が出自を意識しない。
label に `"REV:path"` を入れておくとエラー文脈が保たれる。

clap 側: 第2位置引数を `Option<PathBuf>` 化 + `--git` に `conflicts_with = "after"`。
両方 None は `bail!` で「どちらかを指定してください」と案内する。

### 3. CI の fail 判定は最小主義 + 対象の列挙

fail 条件は限定列挙にする (例: 「unsafe 操作の新規追加」のみ)。
判定は before/after のメトリクス比較 (増加したら違反)、
新規追加分は単体のメトリクスで判定する。exit code は `anyhow::bail!` で返し、
**違反した関数名をエラーメッセージに列挙する** (どこを直せばよいか一目で分かる)。

### 4. changed コマンド (変更対象の列挙)

`git diff --name-only REV -- '*.rs'` → ファイルごとに before/after の関数集合を
突き合わせ → 両方に居る関数は diff して**空なら出さない** (「変更されたものだけ」)。
出力は after の出現順 → before のみの関数 (削除) の順で決定論的。

- 解析できないファイル (構文エラー等) は**警告して飛ばす** — CI を解析失敗で
  落とさない。ビルドの成否は別ジョブの責務 (関心の分離)

### 5. ワークフロー YAML は薄く、ロジックはスクリプトへ

CI ロジックは `scripts/<name>-report.sh` のようなスクリプトに置き、環境変数で
バイナリを差し替え可能にする (ローカルは `cargo run -q -p <cli> --`、
CI は `target/debug/<bin>`)。**CI とローカルで同一コマンドが動く** =
デバッグ可能性の要件。

- sticky comment は本文先頭のマーカー (`<!-- marker -->`) を
  `gh api ... --jq 'select(.body | startswith(...))'` で検索し、
  既存があれば PATCH・なければ POST に分岐
- 生成物 (SVG 等) はパス区切りを `__` 等に潰したファイル名で artifact に積む
  (コメントへの画像インライン埋め込みは初期スコープ外にしてよい)

### 6. git 連携の統合テスト

一時ディレクトリに `git init` して「v1 をコミット → v2 を作業ツリーに置く」
fixture 関数 (`init_git_fixture(name)`) を1つ用意し、diff / changed / fail の
各テストが**名前付きサブディレクトリ**で独立に使う (並列実行で干渉しない)。
`git config user.email/name` をテスト内で設定する (CI 環境にグローバル設定がない)。

## 注意点・制約

- `git show REV:path` の path は REV 時点の path。リネームされたファイルは
  「新規追加 + 削除」として見える (初期フェーズでは許容)
- `changed` は作業ツリーと REV の比較 (`git diff REV`)。CI の pull_request イベントは
  merge commit をチェックアウトするため、`origin/<base_ref>` との比較で PR の差分になる
- ワークフローの `fetch-depth: 0` を忘れるとベースリビジョンが無くて git show が失敗する
- jq に依存する (GitHub ランナーには同梱。ローカルは要インストール)

## 参照

- diff エンジン本体の定型は `structural-diff-pattern.md` を参照
- サブコマンド追加の一般形は `clap-cli-integration-pattern.md` を参照
