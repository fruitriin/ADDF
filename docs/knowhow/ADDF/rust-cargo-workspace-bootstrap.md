---
title: Rust Cargo Workspace ブートストラップ
created: 2026-06-11
last_verified: 2026-06-11
depends_on: []
status: active
---

# Rust Cargo Workspace ブートストラップ

> 出典: MagiaMagica (コード可視化ツール) Phase 1.0 で確立

ADDF 利用 Rust プロジェクトで cargo workspace を立ち上げるときの定型パターン。

## 採用する workspace 構造

```
<repo_root>/
├── Cargo.toml            # [workspace]
├── rustfmt.toml
├── LICENSE
├── README.md             # README 整備フェーズで充実させる
├── crates/
│   ├── <name>-core/      # コアロジック
│   ├── <name>-<adapter>/ # 言語アダプタ等の周辺クレート
│   └── <name>-cli/       # CLI バイナリ
└── fixtures/             # テスト・README 共用のサンプル入力
```

`<product>/` のような中間ディレクトリは作らず**リポジトリルート直下**に置く。リポジトリ自身が単一製品の場合は冗長なネストを避ける。後続の `cargo install --path crates/<name>-cli` 等の表記も整合する。

## workspace.package で共通化するフィールド

```toml
[workspace.package]
version = "0.1.0"
edition = "2024"
rust-version = "1.94"        # 当時の stable に追従
license = "MIT"
repository = "https://github.com/<owner>/<repo>"
authors = ["<owner>"]
keywords = ["..."]
categories = ["..."]
# readme は最初の README 整備フェーズで追加
```

各クレートでは `version.workspace = true` のように継承する。`readme` は MVP では未指定にし、README を実際に書くフェーズで追加する。

## workspace.lints での clippy 一括設定

```toml
[workspace.lints.rust]
unsafe_code = "deny"        # 必要なクレートのみ局所的に allow で上書き
missing_docs = "allow"

[workspace.lints.clippy]
all = { level = "warn", priority = -1 }
pedantic = { level = "warn", priority = -1 }
missing_errors_doc = "allow"
missing_panics_doc = "allow"
module_name_repetitions = "allow"
doc_markdown = "allow"       # 固有名詞・カタカナを多用するプロジェクトで必須
```

各クレートに `[lints] workspace = true` を1行入れるだけで全クレートに伝播する。

### `doc_markdown` を allow する判断

clippy pedantic の `doc_markdown` は CamelCase の単語にバッククォートを要求する。日本語コメントやプロジェクト固有の固有名詞 (製品名・ドメイン語彙の CamelCase) を多用するプロジェクトでは警告が大量発生するため最初から allow にしておくのが現実的。意図を `#` コメントとして workspace.lints に残しておく。

## crates.io publish 準備の最低ライン

publish を将来する前提なら、ローカル開発時点で以下を満たしておく:

1. 全クレートに `description` / `license` / `repository` を記入 (workspace.package で継承可)
2. path 依存にも **明示的な version を併記** する。これが無いと `cargo publish --dry-run` がエラーになる:
   ```toml
   my-core = { path = "../my-core", version = "0.1.0" }
   ```
3. `keywords` / `categories` も入れておく (後付け忘れ防止)
4. 名前衝突がないか `cargo search` で確認

## `.gitignore` に追加するエントリ

Rust 標準:
```
target/
**/*.rs.bk
```

ADDF 利用プロジェクトの場合は別途 `.claude/` 配下の ADDF ブロックも必要 (ADDF 初期化で自動挿入される)。

## Cargo.lock の扱い

bin クレートを含む workspace では `Cargo.lock` を **コミットする**。これにより再現可能ビルドが保証される (cargo の公式推奨)。ライブラリのみの workspace では好み。

## CLAUDE.repo.md のビルド・Lint・テスト記述

実装フェーズに入ったら未設定プレースホルダーを実コマンドに差し替える:

```bash
# ビルド
cargo build --workspace

# Lint
cargo clippy --workspace --all-targets -- -D warnings
cargo fmt --check

# テスト
cargo test --workspace
```

品質ゲート Stage 1 で上記すべてを通すこと。`-D warnings` を CI/品質ゲートで使うのが習慣。

## スモークテストの粒度

ワークスペース立ち上げ時点では「ビルドが通る」「`cargo test` が 0 件で終わらない」ことを保証するために、各クレートに**少なくとも1つの自明なテスト**を置く。`crate_name()` を assert する程度で十分。フェーズが進むにつれ意味のあるテストに置き換える。

## レビューで頻出する指摘 (立ち上げフェーズで観測)

- `workspace.package.readme = "README.md"` を宣言すると、README が無い段階で `cargo publish --dry-run` がエラー。README を後送りにする場合は readme フィールド自体を未指定にする
- path 依存に version 未指定 → publish 不可
- `unsafe_code` は `warn` ではなく `deny` のほうが事故防止になる (Rust 慣習)
- `rustfmt.toml` にデフォルト値 (`use_small_heuristics = "Default"` 等) を書くと意図がノイズになる

## 関連する落とし穴 (計画書との突き合わせ)

- 計画書に書かれた依存バージョンは執筆時点の値であり、実装時には世代がずれていることが多い。`cargo add --dry-run` で実値を確認し、**計画書側を実値で上書きする**運用にする
