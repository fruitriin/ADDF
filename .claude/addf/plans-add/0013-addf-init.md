# 計画: addf-init コマンド

## 実装状況: 完了（2026-03-20、2026-06-11 遡及確認）

GitHub Issue: #3

## 動機

現在のセットアップは手動でファイルを差し替える手順が必要で、初回導入のハードルが高い。
`addf-init` コマンドを提供することで:
- `CLAUDE.repo.md` の初回生成を対話的に行える
- プロジェクト構造の整合性を検証できる
- ロックファイル（Phase 11）の初期生成も統合できる
- Codex 対応（Phase 12）の設定生成も統合できる

全新規プロジェクトのセットアップ摩擦を解消し、高い複利効果を持つ。

## 前提

- Phase 11（ロックファイル）が完了していること
- Phase 12（Codex サポート）の調査結果が出ていること

## 設計

### 1. `addf-init` スキル

`/addf-init` スキルを新設。2つのモード:

#### init モード（初回セットアップ）

```
/addf-init
```

実行内容:
1. プロジェクトの状態を確認（既に ADDF 導入済みか判定）
2. `CLAUDE.repo.md` を対話的に生成:
   - プロジェクト名
   - プロジェクト種別（ADDF 利用プロジェクト / ADDF 開発プロジェクト）
   - ビルド・Lint・テストコマンド
   - コミットログ規約
   - ターゲットエージェント（Claude Code / Codex / 両方）
3. ターゲットが Codex または両方の場合:
   - `~/.codex/config.toml` に `project_doc_fallback_filenames = ["CLAUDE.md"]` の設定を案内
   - `AGENTS.md` がリポジトリに存在することを確認（ADDF 同梱済み）
   - Codex 向け推奨設定（`approval_policy`, `sandbox_mode`）を案内
4. `CLAUDE.local.example.md` → `CLAUDE.local.md` のコピー
5. `.claude/addf-lock.json` の初期生成（Phase 11）
6. `TODO.md` の初期化（テンプレートから）
7. `docs/plans/` ディレクトリの作成
8. `docs/knowhow/INDEX.md` の初期化
9. 完了メッセージと次のステップの案内

#### check モード（構造検証）

```
/addf-init check
```

実行内容:
1. 必須ファイルの存在確認:
   - `CLAUDE.md`, `CLAUDE.repo.md`, `TODO.md`
   - `.claude/Progress.md`, `.claude/Feedback.md`
   - `.claude/addf-lock.json`
   - `.claude/settings.json`
2. ファイル間の整合性チェック:
   - `CLAUDE.md` の `@` メンションが解決可能か
   - `TODO.md` と `docs/plans/` の一致
   - `.claude/addf-lock.json` の存在と妥当性
3. 結果をレポート（OK / WARNING / ERROR）

### 2. 再生性（Idempotency）

- `addf-init` は既存ファイルを上書きしない（既存を検出したらスキップまたは確認）
- `addf-init check` は読み取り専用で副作用なし
- 何度実行しても安全

## 影響範囲

- `.claude/commands/addf-init.md`（新規スキル）
- `CLAUDE.repo.example.md` — init が参照するテンプレート元（既存、変更なし or 微修正）

## 見積もり

AI 実装: 15-20 分

## 実装結果

### 完了した項目
- `.claude/commands/addf-init.md` — init モード（対話的セットアップ）+ check モード（構造検証）

### レビューで修正した項目
- 手動導入済みプロジェクトの検出（CLAUDE.md 存在 + lock なしのケース）
- `addf-lock.json` の repository URL 取得元を `git remote get-url origin` に明確化
- check モードの commit ハッシュ形式チェック追加
- `docs/knowhow/INDEX.md` のテンプレートを実際の形式に修正

## 状態: 完了（2026-03-20）
