# 配布・導入 — Framework distribution, installation, and documentation

> 概念単位の記録。実装がスキル/エージェント/フック/ファイルのどれであっても、
> 「ADDF の導入・更新・リリース・ドキュメンテーション」に関わるものをまとめている。

## 構成要素

| 種別 | 名前 | 役割 |
|---|---|---|
| スキル | addf-init | 新規/既存プロジェクトへの ADDF 導入（外部起動・テンプレート・既存プロジェクトの3経路）と `check` 構造検証 |
| スキル | addf-migrate | addf-lock.json の ref（タグ）基準でフレームワークを最新版にアップグレード（6フェーズ） |
| スキル | addf-release | リリースワークフロー（upstream/downstream 自動切替） |
| スキル | addf-overview | エコシステム概要ドキュメントの生成（本ドキュメント。full/patch モード + .lock） |
| ファイル | .claude/addf-lock.json | バージョン追跡（現在 v0.3.0）。`version` / `ref` / `updated_at` / `repository` |
| ファイル | .claude/ADDF-CHANGELOG.md | フレームワーク変更履歴。migrate 時に該当バージョン間のエントリを表示 |
| ファイル | .claude/ADDF-Release.addf.md | ADDF 本体（upstream）のリリース手順定義 |
| ファイル | CONTRIBUTING.md | コントリビューションモデル（計画駆動レビュー・きっかけの記載） |
| ファイル | .gitignore の ADDF マーカーブロック | 実行時生成ファイルの除外定義（addf-init がブロックごとコピー — 列挙を持たない単一ソース化） |
| テンプレート | .claude/templates/Release.md | リリース手順テンプレート |
| ディレクトリ | docs/guides/ | セットアップ・運用ガイド群（7本） |

### docs/guides/ 一覧

| ファイル | 内容 |
|---|---|
| setup.md | ADDF 導入ガイド |
| development-process.md | 開発プロセスガイド（代替わり日記の語彙の意図もここ。lint ペア4で CLAUDE.md と同期検査） |
| skills.md | スキル一覧・使い方 |
| agents.md | エージェント一覧・使い方 |
| gui-test-setup.md | GUI テストセットアップ |
| codex-setup.md | Codex 環境セットアップ |
| migration.md | マイグレーションガイド |

## 設計思想

ADDF は「配布されるフレームワーク」であり、導入→運用→更新のライフサイクルを持つ。リポジトリは `fruitriin/ADDF`（Plan 0025 でリネーム）。

**導入パス**:
1. **新規プロジェクト**: GitHub Template から `addf-init` で初期化
2. **既存プロジェクト**: `addf-init` を外部起動（URL 検証 → tmp クローン）。既存の CLAUDE.md / AGENTS.md を統合して `CLAUDE.repo.md` に退避し、干渉チェック（Phase 2.5）・導入前レビュー（Phase 2.7: hooks/権限/CLAUDE.md への影響を明示）を経て統合する

**バージョン管理**:
- `addf-lock.json` は **ref（`vX.Y.Z` タグ名）を記録する**。旧形式（`commit` ハッシュ）はリリースプロセスの都合で実在しないハッシュになりうるため、`v<version>` タグに読み替える後方互換を addf-init / addf-migrate / addf-init check が持つ
- `addf-migrate` がロックファイルの ref と最新版の差分を算出し、対象ファイル（addf- プレフィックス・.claude 配下・guides・knowhow/ADDF/）だけを安全にアップグレード。プロジェクト固有ファイル（Progress/Feedback/.exp.md/CLAUDE.repo.md/TODO 等）はスキップ
- CLAUDE.md / CLAUDE.repo.md の分離設計により、マイグレーション時の衝突を最小化

**分離パターン（配布の前提）**: `.addf.md` サフィックス並置 / `ADDF/` サブディレクトリ隔離 / `addf-` プレフィックス識別の3パターン（docs/knowhow/ADDF/upstream-downstream-separation.md）。lint・テストは対象ファイル欠如を SKIP 扱いにしてダウンストリームでの誤 ERROR を防ぐ。

**リリース**:
- `addf-release` が upstream（ADDF 本体）と downstream（利用プロジェクト）で手順を自動切替
- 責務分割: スキル=ルーター、設定ファイル（ADDF-Release.addf.md）=手順定義、.exp.md=プロジェクト戦略（docs/knowhow/ADDF/release-skill-separation.md）
- バージョン履歴: v0.1.0（lock+migrate 基盤）→ v0.2.0（init/release・Codex 対応・guides 分離）→ v0.3.0（迷ったときの作法・日記・knowhow ライフサイクル・ペルソナレビュー・同期 lint・context-reminder）

## 主要フロー

```
導入:
  addf-init
  ├─ 外部起動 → URL 検証（https:// のみ）→ tmp クローン
  │   → 既存ファイルから自動推定 → 干渉チェック → 導入前レビュー
  │   → コピー & マージ（カテゴリ1: 無条件 / 2: マージ / 3: 生成）
  ├─ Template 経由 → lock 生成のみ（ファイルは同梱済み）
  └─ check → 必須ファイル・@メンション解決・TODO⇔plans 整合・lock 妥当性・AGENTS.md の5項目検証

更新:
  addf-migrate
  ├─ Phase 1: lock 読み込み（旧形式 commit → v<version> タグに読み替え）・クリーン確認・URL 検証
  ├─ Phase 2: 最新版クローン
  ├─ Phase 3: ref（タグ）基準で差分算出（対象/対象外の区別）
  ├─ Phase 4: 変更プレビュー + CHANGELOG 表示 → ユーザー確認
  ├─ Phase 5: 適用（settings.json ユニオンマージ、CLAUDE.md はテンプレート部分のみ更新）
  └─ Phase 6: lock 更新（ref = v<new-version>）・tmp 削除

リリース:
  addf-release
  ├─ upstream: ADDF-Release.addf.md に従う（タグ vX.Y.Z 発行 → migrate の参照先になる）
  └─ downstream: .exp.md or 対話的に戦略構築

ドキュメント化:
  addf-overview
  ├─ full: 全スキャン → 概念システム探索 → docs/project-overview/ 再生成
  └─ patch: .lock からの diff → 影響システムのみ再生成
```

## 下流でのカスタマイズ

- `CLAUDE.repo.md` でプロジェクト種別（ADDF 開発 or ADDF 利用）を宣言 — addf-release / addf-permission-audit の分岐に使われる
- `docs/guides/` にプロジェクト固有のガイドを追加可能
- `addf-release` は downstream で初回実行時に対話的にリリース戦略を構築し、.exp.md に保存
- `addf-lock.json` の `repository` を差し替えれば fork した ADDF からのマイグレーションも可能（デフォルト URL と異なる場合は警告）

## 関連するシステム

- **セッション管理**: CLAUDE.md, settings.json, hooks, Behavior.toml は配布対象でありセッション管理の構成要素でもある
- **品質ゲート**: addf-lint がフレームワーク整合性を検証（配布物の品質保証）。lint の SKIP 設計・addf-init コピーリストのカバレッジ検査（ペア5）は配布安全性のための機構
- **ノウハウ蓄積**: docs/knowhow/ADDF/ は配布・マイグレーション対象。プロジェクト固有 knowhow は対象外
- **全システム**: addf-overview が全システムを横断的にドキュメント化
