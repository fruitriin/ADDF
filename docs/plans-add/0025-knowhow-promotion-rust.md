# Plan: MagiaMagica からの Rust 系 knowhow 一括昇格

## 実装状況: 完了（2026-06-11）

## きっかけ

- 元となったプロンプト/会話: MagiaMagica（コード可視化ツール）Phase 1〜4 の開発で蓄積した knowhow の一括昇格。オーナー指示（2026-06-11）
- アイデアの出典: MagiaMagica の `.claude/Feedback.md` に Phase 1.0〜3.4 を通じて積まれた「ADDF 昇格候補」の記録（Phase 3 完了の節目で一括判断する方針だったもの）
- 関連Issue: なし

## 動機

MagiaMagica の `docs/knowhow/` には、Rust プロジェクト全般（cargo workspace / syn / SVG 生成 / clap CLI / 構造 diff / git CI 連携 / 最小 dev-server）に通用する知見が蓄積されたが、ダウンストリームのプロジェクト固有文書に置かれたままでは他の ADDF 利用プロジェクトから参照できない。汎用部分を ADDF 本体の `docs/knowhow/ADDF/` に昇格し、次の Rust プロジェクト立ち上げ時に流用可能にする。

あわせて、knowhow 記録スキル自体の運用で得られた「分割 vs 統合」等の判断パターンを `addf-knowhow.md` のチェックリストに還元する。

## 設計

### 1. knowhow 7本の昇格（`docs/knowhow/ADDF/` に新規作成）

| # | ファイル | 内容 | 確立フェーズ（出典） |
|---|---|---|---|
| 1 | `rust-cargo-workspace-bootstrap.md` | cargo workspace 立ち上げの定型（workspace.package / lints 一括 / publish 準備） | Phase 1.0 |
| 2 | `syn-visitor-patterns.md` | syn::Visit の定型（1関心1visitor / 再帰展開ビルダ / call site 抽出 / 近似データフロー / impl 索引） | Phase 1.2〜4.0 |
| 3 | `svg-deterministic-rendering.md` | 決定論的 SVG 生成（raw string の罠 / 固定桁 / insta / qlmanage 目視） | Phase 1.6 |
| 4 | `clap-cli-integration-pattern.md` | clap 4 derive CLI 統合（予約語フラグ / conflicts_with / assert_cmd / エラー責務分担） | Phase 1.7 |
| 5 | `structural-diff-pattern.md` | ID 非依存の構造 diff（構造キーマッチング / 貪欲対応 / overlay 強調チャネル独立） | Phase 3.1〜3.2 |
| 6 | `git-ci-integration-pattern.md` | CLI の git 連携と CI しきい値（gitio 隔離 / 薄い YAML + 再現スクリプト / sticky comment / init_git_fixture） | Phase 3.3 |
| 7 | `minimal-dev-server-pattern.md` | 同期スレッドモデルの最小 dev-server（tiny_http + SSE、SSE チャンク経路禁止の訂正を含む最新版） | Phase 2.1〜4.0.5 |

汎用化方針:

- frontmatter（title / created / last_verified / depends_on / status）を ADDF 規約に合わせて付与
- 冒頭に「> 出典: MagiaMagica (コード可視化ツール) Phase X.Y で確立」を1行残す（アイデアの系譜追跡）
- プロジェクト固有の語彙・参照（ファンタジー語彙の型名、spec 節番号、`crates/` のパス）は一般的な言い回しに置換するか、具体例として括弧書きで簡潔に残す
- 「プロジェクトへの適用」「参照」のプロジェクト内パスは削除し、構成の定型として一般化できるものは「適用例」として本文に吸収
- 技術的内容（パターン・落とし穴・コード断片・根拠）は削らない — 汎用化は語彙の置換であって要約ではない
- `minimal-dev-server-pattern.md` は Phase 4.0.5 の SSE 訂正（チャンク経路禁止 → `into_writer` + flush）を含む最新版を正とする

### 2. addf-knowhow.md チェックリスト追記

「Phase 3: 自己ブラッシュアップ」の確認項目の後ろに「知見記録の判断パターン（実例由来）」として5例を追記:

1. 統合先ファイルの冒頭メタコメント（確立フェーズ等）も実態に合わせて更新する。INDEX は reindex を待たず手動同期してよい
2. 関心が別なら新規ファイル、検索性を失わない統合なら既存ファイルに追記（分割 vs 統合の判断軸）
3. 1つの知見セットでも関心が分かれるなら複数の既存ファイルへセクション分配してよい
4. ストリーミング機能（SSE 等）の knowhow には「実際にストリームを読むテスト」を受け入れ基準として含める
5. 後続フェーズで削除予定のコードは単独ファイルに隔離し「捨てる前提」と冒頭に明記する（Temporary Isolation Pattern）

### 3. INDEX.addf.md 更新

新規7ファイルを既存形式（鮮度 🟢 2026-06-11 / ファイル / 要約 / キーワード）で追記。要約とキーワードは MagiaMagica 側 INDEX.md の該当行を汎用化して流用。

## 影響範囲

- `docs/knowhow/ADDF/` — 新規7ファイル
- `docs/knowhow/INDEX.addf.md` — 7行追記
- `.claude/commands/addf-knowhow.md` — Phase 3 に判断パターン5例を追記
- `docs/plans-add/TODO.addf.md` — 本 Plan の登録
- 既存コード・スキルの動作変更はなし（ドキュメントのみ）

## 実装結果メモ

- 計画番号は当初 0024 を予定していたが、`0024-todo-plan-status-lint.md` が既に存在したため 0025 に採番した
