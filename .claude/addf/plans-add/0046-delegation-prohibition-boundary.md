# Plan 0046: 委譲プロンプトの禁止事項の境界緩和と共通テンプレート化

## 実装状況: 完了（2026-07-07）

edge: derived-from 0041

- 項目1（境界緩和）: DelegationRules.md の「Progress.md の境界」節で「`## タスク` 以降は触らない・`## 運用ルール` 節はテンプレートに合わせて同期してよい」を明記
- 項目2（DelegationRules.md 新設）: `.claude/addf/templates/DelegationRules.md` 新設。5項目（Progress.md 境界・git 操作・単一ソース・スコープ・ノウハウ記録）を含む。末尾に「プロジェクト固有ルール」節を用意（ダウンストリーム追記枠）。addf-dev.md / addf-speculate.md から参照追加
- 項目3（境界の明文化・機械保証）: lint-template-sync.py の check_pair1 docstring に検査境界を明文化。test-template-sync.sh に Test 4b（タスク欄変更で誤検知しない）を追加してドリフト注入 TDD
- CHANGELOG に [Unreleased] エントリ追記
- 品質ゲート Stage 1: run-all.sh + lint-template-sync 通過（Test 4b 含む全パス）

> 出典: 2026-07-06 サイクル13（Plan 0041 実装時）に発生した「委譲エージェントが同期ペア対象の Progress.md 運用ルール節を触れず、親エージェントが手動で reproduce する運用ノイズ」への対応。オーナー判断 (b) 採用。

## 関連 Plan

- [Plan 0041: コンテキスト枯渇によるループ停止の壁の突破](0041-context-exhaustion-loop-wall.md) — 本 Plan の出典事例（ProgressTemplate 側追記で ペア1 sync 失敗が発生 → 親が3ステップで解消）
- [Plan 0035: PR 運用の標準化](0035-pr-standard-format.md) — テンプレート化の設計思想（単一ソース参照）

## 目的

委譲エージェント（Agent tool 経由の worktree 実装）に渡す禁止事項を、論理的な境界（「タスクコンテキスト vs 同期ペア対象」）に合わせて緩和し、同期ペア発火時の運用ノイズを削減する。

## 現状の挙動

- 委譲プロンプトで一律に「Progress.md を触らない」を禁止事項に置いてきた
- しかし Progress.md には2つの領域がある:
  - **運用ルール節**（`# 進捗表`〜`## タスク` の直前）: ProgressTemplate.addf.md との同期ペア1 対象
  - **タスク欄**（`## タスク` 以降）: 親エージェントが管理する進行中日記・チェックリスト
- テンプレートを変更する委譲タスク（今回の Plan 0041 のように ProgressTemplate に追記するもの）では、委譲側で Progress.md 運用ルール節を触れないため、ペア1 sync 失敗が発生 → 親が `stash → merge → 手動追記 → コミット` の3ステップで解消
- ADDF 的にテンプレート変更は頻発する（7ペア中 2つが Progress.md 経由・今後も増える見込み）ため、この運用ノイズが繰り返される

## 変更内容（項目）

### 項目1: 禁止事項の境界緩和

- 委譲プロンプトの禁止事項を「Progress.md を触らない」から「**Progress.md の `## タスク` 以降**は触らない。**運用ルール節はテンプレートに合わせて同期してよい**（ペア1 の要求どおり）」に変更
- 委譲エージェントは ProgressTemplate.addf.md と Progress.md の運用ルール節を同一差分で更新可能に

### 項目2: 委譲プロンプト禁止事項の共通テンプレート化

- 毎回書き直している委譲プロンプトの共通部分（Progress.md 境界・git commit/push 禁止・「単一ソース維持」等）を `.claude/addf/templates/DelegationRules.md` 等に単一ソース化
- 委譲時は `@DelegationRules.md` メンションで参照する（Plan 0035 の pr-format.md と同じ設計思想）
- ダウンストリームでも同じ禁止事項テンプレートが使えるよう配布対象に含める

### 項目3: lint-template-sync ペア1 の検査範囲確認と明文化

- 現行のペア1 が実際に「運用ルール節のみを同期対象」としているか実装確認
- 未確認の場合は明文化（コメントで契約明示）＋ドリフト注入テストで境界を機械保証

## 影響範囲

- `.claude/addf/templates/DelegationRules.md`（新設）
- 委譲プロンプトを持つスキル: `.claude/commands/addf-dev.md`・`addf-speculate.md`（参照方法の明示）
- `.claude/addf/addfTools/lint-template-sync.py`（ペア1 の検査範囲コメント）
- addf-init コピーリスト（新テンプレート配布）

## テスト方針

- ドリフト注入 TDD: Progress.md のタスク欄変更 → ペア1 通過（対象外）/ 運用ルール節変更 → ペア1 検出

## 未決事項

- ~~DelegationRules.md の粒度~~ → **決定（2026-07-07）**: 汎用禁止事項を5項目にまとめる構造（Progress.md 境界・git 操作・単一ソース・スコープ・ノウハウ記録）。Progress.md 境界特化ではなく汎用委譲ルールとして機能する
- ~~ダウンストリーム配布時のプロジェクト固有追記~~ → **決定（2026-07-07）**: 「本体版＋追記枠」設計を採用。末尾に「プロジェクト固有ルール」節を用意し、`<!-- addf-migrate は共通禁止事項のみ更新する -->` の注記でマイグレーション境界を明示

## 完了条件

- [x] DelegationRules.md 新設・addf-dev/addf-speculate から参照
- [x] 委譲プロンプトの Progress.md 禁止事項が境界緩和されている
- [x] lint-template-sync ペア1 の検査範囲が明文化されている
- [x] `bash .claude/addf/tests/run-all.sh` と `/addf-lint` 全通過

## AI 実装時間見積もり

1セッション以内（軽量。ドキュメント中心）
