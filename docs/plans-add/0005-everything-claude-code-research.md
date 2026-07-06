# 計画: Everything Claude Code 調査・取り込み

## 実装状況: 完了（2026-03-18、2026-06-11 遡及確認）

## 意図的完了の明記（2026-07-06・Plan 0036 埋没監査 #6 の回収）

- 「hooks 活用」の High 推奨は**実装済み**として閉じる（Plan 0021〜0023 で hooks 群を導入・現在 CI/pre-commit/context-reminder 等で稼働中）
- 「言語別ルール分離」の High 推奨は Plan 0045 に回収（判断 Plan として起案）


## 動機
`plan.md` #7 のオーナーリクエスト。外部リポジトリ https://github.com/affaan-m/everything-claude-code/ から ADD フレームワークに取り込めるプラクティスを調査する。

## 設計

### 1. リポジトリ調査
- README・ドキュメントの精読
- ディレクトリ構造・設定ファイルの分析
- CLAUDE.md の書き方、スキル構成、ワークフローパターンの抽出

### 2. 比較分析
- ADD フレームワークの現状と比較
- 既に ADD に存在する機能 vs 新たに取り込める機能を整理

### 3. 改善提案
- 取り込むべきプラクティスを優先度付きでリストアップ
- 必要に応じて新たな Plan を起こす

## 調査結果

### 比較対象
- [everything-claude-code](https://github.com/affaan-m/everything-claude-code/) — 108+ スキル・25+ エージェント・57+ コマンドのプラグインシステム
- [claude-code](https://github.com/anthropics/claude-code) — Anthropic 公式 CLI

### ADD に既にある機能（ECC と共通）
- コードレビュー・セキュリティレビューエージェント
- git worktree を活用した並列実装
- Plan 駆動の開発ワークフロー
- ノウハウ蓄積（knowhow/）
- GUI テスト機能

### ADD にない機能（ECC から取り込み候補）

| 優先度 | 機能 | ECC での実装 | ADD への適用案 |
|---|---|---|---|
| High | **Hooks 活用** | PreToolUse/PostToolUse/Stop で自動検証・セッション状態管理 | hooks/ ディレクトリを導入し、コミット前自動検証・セッション開始時の状態復元を実装 |
| High | **言語別ルール分離** | rules/ ディレクトリで言語別にガイドライン分離 | CLAUDE.md が肥大化した場合の分割パターンとして docs/rules/ を提供 |
| Medium | **Continuous Learning** | instinct 抽出 → 信頼度スコア → skill 進化 | 現在の .exp.md パターンを拡張し、経験の信頼度・頻度を記録する仕組みを検討 |
| Medium | **コンテキスト最適化** | strategic compaction シグナル + iterative retrieval | knowhow-filter の改善版として、コンテキスト使用量に応じた圧縮提案を組み込む |
| Low | **TDD カバレッジ要件** | 80%カバレッジ最低要件をルールに明記 | プロジェクト別のカバレッジ要件を CLAUDE.repo.md に設定可能にする |
| Low | **DAG オーケストレーション** | 複雑な依存グラフでのタスク実行 | 現在の worktree 並列に依存関係グラフを追加 |

### 取り込まないもの
- マーケットプレース・プラグインシステム — ADD のスコープ外（シンプルさ優先）
- 多言語対応（中国語翻訳等） — 日英で十分
- PM2 サービスライフサイクル — ADD の対象外

## 影響範囲
- 調査結果に基づき、以下の追加 Plan を起こすことを推奨:
  - hooks 活用（High）
  - 言語別ルール分離パターン（High）

## 実装完了状況
- 調査・比較分析・改善提案を完了（2026-03-18）
