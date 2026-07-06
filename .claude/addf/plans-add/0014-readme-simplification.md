# 計画: README のセットアップ簡素化

## 実装状況: 完了（2026-03-21、2026-06-11 遡及確認）

GitHub Issue: #2

## 動機

人間の認知力は任意項目を必須と勘違いする。
現在の README はセットアップ手順・スキル一覧・エージェント一覧・開発プロセス・ディレクトリ構成が
1ファイルに詰め込まれており、初見の読者にとって情報過多。
発展的な内容を別ページに分離することで、必須手順の明確化と認知負荷の低減を図る。

## 前提

- Phase 11-13 が完了していること（README が最終状態を反映するため）

## 設計

### 1. README.md のスリム化

README に残す内容（必須情報のみ）:
- プロジェクト概要（1-2 文）
- 特徴（箇条書き、現状維持）
- **クイックスタート**（最小限の手順）:
  1. クローン
  2. `/addf-init`（Phase 13）を実行
  3. 計画を書いて `/loop 1h /addf-dev-loop`
- リンク集（詳細ドキュメントへの誘導）

### 2. 分離先ドキュメント

以下を `.claude/addf/guides/` に分離:

| ファイル | 内容 |
|---|---|
| `.claude/addf/guides/setup.md` | 詳細セットアップ（設定の役割、手動セットアップ手順、ディレクトリ構成） |
| `.claude/addf/guides/skills.md` | スキル一覧と使い方 |
| `.claude/addf/guides/agents.md` | エージェント一覧と起動タイミング |
| `.claude/addf/guides/development-process.md` | 開発プロセスの詳細（ブートシーケンス、品質ゲート、並列実装） |
| `.claude/addf/guides/migration.md` | バージョンアップ手順（Phase 11 の `/addf-migrate` の使い方） |
| `.claude/addf/guides/codex.md` | Codex ユーザー向けガイド（Phase 12 の結果） |

### 3. 英語版（README.en.md）も同様に更新

日本語版と同じ構造に揃える。

### 4. 分離の基準

- **README に残す**: 「5分以内に動かせる」ために必要な情報
- **分離する**: 「もっと詳しく知りたい」人向けの情報
- 迷ったら分離する（README は短いほど良い）

## 影響範囲

- `README.md`（大幅縮小）
- `README.en.md`（大幅縮小）
- `.claude/addf/guides/`（新規、複数ファイル）

## 見積もり

AI 実装: 15-20 分

## 実装結果

### 完了した項目
- `README.md` — 174行→65行にスリム化（クイックスタート + ドキュメントリンク集）
- `README.en.md` — 163行→65行にスリム化（同構造）
- `.claude/addf/guides/setup.md` — 詳細セットアップ（手動セットアップ、設定役割、ディレクトリ構成）
- `.claude/addf/guides/skills.md` — スキル一覧（addf-init, addf-migrate 等の新スキルも含む）
- `.claude/addf/guides/agents.md` — エージェント一覧と品質ゲート
- `.claude/addf/guides/development-process.md` — 開発プロセスの詳細
- `.claude/addf/guides/migration.md` — バージョンアップ手順
- 既存の `.claude/addf/guides/codex-setup.md` と `.claude/addf/guides/gui-test-setup.md` はそのまま活用

### 設計判断
- README のクイックスタートは `/addf-init` を中核に据えた（手動ファイル差し替え → 自動初期化）
- clone URL を `your-org` → 実際のリポジトリ URL に更新
- ディレクトリ構成の `.claude/skills/` を `.claude/commands/` に修正（実態に合わせた）

## 状態: 完了（2026-03-21）
