# 計画: Codex サポート

## 実装状況: 完了（2026-03-20、2026-06-11 遡及確認）

GitHub Issue: #1

## 動機

Codex（OpenAI のコーディングエージェント）を主に使っているが ADDF を試したいというユーザー層が存在する。
ADDF は現在 Claude Code 固有の機能（Hooks、Skills、Agents、settings.json）に強く依存しており、
Codex ユーザーがそのまま利用することはできない。
マルチエージェント対応により、ADDF の受益者が増え、他の改善（init、README、knowhow）の複利効果も増大する。

## 前提調査（完了）

### 調査結果: Codex ↔ Claude Code 互換性マッピング

| ADDF 機能 | Claude Code | Codex | 互換性 | 対応方針 |
|---|---|---|---|---|
| 指示ファイル | `CLAUDE.md`（`@` メンション展開） | `AGENTS.md` + fallback | **高** | `AGENTS.md` 同梱 + fallback 設定案内 |
| スキル | `.claude/commands/*.md` | `.agents/skills/*/SKILL.md` | **中** | ドキュメントで移植手順を案内 |
| エージェント | `.claude/agents/*.md` | `[agents]` in config.toml | **低** | 手動実行を案内 |
| Hooks | settings.json（5イベント） | 限定的（SessionStart, Stop） | **低** | 代替なし、制限事項として明記 |
| 権限管理 | settings.json permissions | config.toml approval_policy | **低** | Codex 設定テンプレートを提供 |
| ファイル除外 | `.claudeignore` | sandbox 設定 | **低** | 制限事項として明記 |
| GUI テスト | addfTools (Swift) | N/A | **なし** | sandbox 環境では不可 |
| ノウハウ管理 | knowhow/ + スキル | knowhow/ 直接参照 | **高** | Markdown ベース、エージェント非依存 |
| 品質ゲート | エージェント並列起動 | 手動実行 | **低** | 手動実行手順を案内 |
| 計画駆動開発 | Plan → TODO → Progress | 同左 | **高** | Markdown ベース、エージェント非依存 |

### 互換戦略の調査結果

1. **project_doc_fallback_filenames**: Codex の `~/.codex/config.toml` で `CLAUDE.md` をフォールバックに設定可能
2. **symlink**: `AGENTS.md` → `CLAUDE.md` のシンボリックリンクも可能だが、ツール固有のカスタマイズができなくなる
3. **ADDF の採用方針**: 別ファイルとして `AGENTS.md`（簡潔版）と `CLAUDE.md`（フル版）を提供

## 採用した設計方針: B案（ドキュメント対応）+ C案要素

### 理由

- ADDF のコアワークフロー（計画駆動、ノウハウ蓄積、進捗管理）は Markdown ベースで**エージェント非依存**
- Claude Code 固有機能（Hooks、Skills 自動発見、Agents 並列起動）の完全互換は保守コストが高すぎる
- Codex ユーザーは ADDF のコアワークフローだけでも十分価値がある
- `addf-init`（Phase 13）で Codex 向け初期設定を生成する拡張点を残す

### 実装内容

1. **`AGENTS.md`**: リポジトリルートに配置。Codex 向けの簡潔なブートシーケンスと機能互換性の案内
2. **`docs/guides/codex-setup.md`**: 詳細なセットアップガイド（fallback 設定、スキル移植手順、制限事項）
3. **Phase 13（addf-init）への入力**: Codex ユーザー向けの初期設定生成オプション

## 影響範囲

- `AGENTS.md`（新規）
- `docs/guides/codex-setup.md`（新規）
- `docs/plans-add/0013-addf-init.md`（Codex オプション追記）

## 見積もり

調査: 10 分（完了）
実装: 15 分

## 実装結果

### 完了した項目
- `AGENTS.md` — Codex 向けブートシーケンス + 機能互換性マッピング
- `docs/guides/codex-setup.md` — 詳細セットアップガイド（fallback 設定、スキル移植、デュアル運用）
- 互換性マッピング表の確定

### 主な設計判断
- ADDF のコアは Markdown ベースでエージェント非依存 → Codex でもそのまま利用可能
- Claude Code 固有機能の完全互換は追求しない（保守コスト vs 価値）
- `AGENTS.md` と `CLAUDE.md` は別ファイルとして管理（ツール固有のカスタマイズ余地を残す）

## 状態: 完了（2026-03-20）
