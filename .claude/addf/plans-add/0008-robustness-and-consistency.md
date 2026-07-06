# 計画: 堅牢性と一貫性の向上

## 実装状況: 完了（2026-03-19、2026-06-11 遡及確認）

## 動機

フレームワークの基本機能は整備されたが、実運用で問題になりやすい箇所がある:
- settings.json と hooks のバリデーション手段がない
- テンプレートとライブファイル（Progress.md 等）の乖離を検出できない
- スキル定義の frontmatter に構文エラーがあっても検出されない

## 設計

### 1. フレームワーク整合性チェックスキル（addf-lint）

`/addf-lint` スキルを新設し、以下を自動チェックする:
- settings.json の JSON 構文チェック
- hooks/ 内のスクリプトの実行権限チェック
- commands/ 内の全スキルの frontmatter YAML パースチェック
- addf-Behavior.toml の構文チェック
- knowhow INDEX と実ファイルの整合性チェック（INDEX に載っているが存在しないファイル、存在するが INDEX にないファイル）

### 2. テンプレート同期チェック

Progress.md の「運用ルール」セクションがテンプレートと一致しているか検証する仕組み:
- `/addf-lint` の一部として実装
- ライブファイルのルールセクションとテンプレートを比較し、乖離があれば警告

### 3. settings.json のパーミッション拡充

現在の allow/ask リストを見直し、テスト実行（`bash .claude/addf/tests/run-all.sh`）を allow に追加する。

## 影響範囲
- `.claude/commands/addf-lint.md`（新規）
- `.claude/settings.json`（軽微）

## 実装結果

- **addf-lint スキル**: `.claude/commands/addf-lint.md` に6項目のチェックを実装
- **テンプレート同期チェック**: addf-lint のチェック6として実装（Python スクリプト付き）
- **settings.json パーミッション**: テスト実行の allow は既に追加済みだったため変更なし
- **レビュー指摘対応**: CLAUDE.md の分離パターン違反を修正（ADDF 固有参照を CLAUDE.repo.md に分離）

## 状態: 完了（2026-03-19）
