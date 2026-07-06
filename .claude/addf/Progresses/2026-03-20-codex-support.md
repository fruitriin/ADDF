# 進捗表

## タスク: Phase 12 — Codex サポート

Plan: `docs/plans-add/0012-codex-support.md`

### 調査
- [x] Codex の AGENTS.md 仕様調査
- [x] Codex Skills（`.agents/skills/`）仕様調査
- [x] Codex の Hooks / Permissions / Sandbox 調査
- [x] symlink 戦略・project_doc_fallback_filenames 調査
- [x] 既存のデュアルエージェント運用事例調査

### 実装
- [x] 互換性マッピング表の確定 & Plan 更新
- [x] `AGENTS.md` 作成（Codex 互換ブートシーケンス）
- [x] `docs/guides/codex-setup.md` 作成（詳細セットアップガイド）
- [x] `addf-init` Plan（0013）に Codex オプションを追記
- [x] `addf-migrate` 対象に AGENTS.md を追加

### 品質検証
- [x] `bash .claude/tests/run-all.sh` 実行 — 全テスト通過
- [x] `addf-code-review-agent` でコードレビュー
- [x] `addf-contribution-agent` でコントリビューション検出
- [x] レビュー指摘への対応（fallback 動作説明修正、ブートシーケンス補完、ADDF 開発推奨明記）

### 完了処理
- [x] Plan に実装完了状況を反映
- [x] Feedback.md 更新（AGENTS.md/CLAUDE.md 同期管理の改善アクション追記）
- [x] Progress.md アーカイブ + 新規作成
- [x] コミット
