# Plan 0062: 投機サイクル完走フィードバックの未回収提案の棚卸しと回収（Issue #24・#25）

## 実装状況: 未着手

owner_feedback: 不要

> 出典: GitHub Issue #24（イヴの時間・Fable 5 エージェントの投機ライフサイクル完走
> フィードバック）・Issue #25（EnumaElish/ccchain・Opus 4.7 エージェントの 9 PR 到達
> フィードバック）。いずれも感想部分に加えて具体提案を含むが、Plan 化されずに残っていた
> （#18/#19/#20 は Plan 0034、#27〜#29 は Plan 0055 で回収済みなのに対し、この2件は未回収）

## 関連 Plan

- [Plan 0034: ダウンストリーム実働フィードバック対応](0034-downstream-feedback-fixes.md) — 同型のフィードバック Issue 回収の前例（Issue #18/#19/#20）
- [Plan 0038: 投機適性](0038-speculation-fitness.md) — 投機の選定・状態管理まわりの先行整備

## 目的

2件のフィードバック Issue に含まれる具体提案を棚卸しし、未回収のものを回収する
（回収済みのものは確認して Issue 返信で報告する）。

## 現状の挙動（起票時点の棚卸し — 着手時に再確認する）

**Issue #24 の提案4件:**

1. `speculate-reconcile.py` の base 検出が `origin/HEAD` 設定済みでも `main` を返す
   （integrate 側は v0.5.0 で自動検出化済みなのに別実装）→ **未回収**（現物確認済み:
   `--base` は `default='main'` の固定デフォルトのまま）
2. GitHub PR 経由の昇格パス（`gh pr merge` → pull → Worktrees 更新 → clean、
   `--delete-branch` 併用時の origin 削除空振り WARNING）の手順記載 → **概ね回収済みに見える**
   （`speculative-development.md` に PR 経路の記述あり）— 空白が残っていないか着手時に精査
3. 状態語彙「PR 化・オーナー判断待ち」の追加 → **回収済みに見える**（同ガイドに
   「origin push ＋ Dashboard / PR（採否判断待ち）」あり）— 同上
4. 「対象なしで終わってよい」（種切れサイクルは健全）のスキル本文への明文化 → **未回収の可能性**

**Issue #25 の提案6件:**

1. Explicit マップ経由のフィールド単位マージ設計を `addf-Behavior.toml` のマージにも横展開 → **未回収**（採否検討から）
2. 「悩まず解決できる衝突（独立追記同士）は integration worktree 内で手動 squash → Edit →
   commit で解消してよい」という上位フローの手順書記載 → **未回収の可能性**
3. unattended でも不可逆な judgment call は明示確認を優先する一文をスキル本文へ → **部分回収**
   （投機禁止条件に「不可逆」はあるが、「曖昧なオーナー指示の解釈確認」の文脈は未記載の可能性）
4. 投機選定時のチェック軸に「同じ Markdown ファイルの同じセクションを編集していないか」を追加
   （AST 層干渉の教訓の Markdown 版。共有チャンネル系ファイルで起きやすい）→ **未回収の可能性**
5. docs-only 投機でも Stage 2 は 3 ペルソナ並列で走らせる価値がある → **既定でカバーの可能性**
   （投機の Stage 2 はペルソナ並列が既定）— 「docs-only なら軽く」への予防的一文の要否のみ判断
6. `clean --delete` の突合検査が origin-only ブランチに対応していて助かった → 感想（対応不要）

## 変更内容（項目・フェーズ）

### 項目1: 棚卸しの確定

- 上記の「〜に見える」「〜の可能性」を現物（`speculate-reconcile.py`・
  `addf-speculate.md`・`speculative-development.md`）と突き合わせ、回収要否を確定する

### 項目2: 未回収分の実装

- **対象**: `.claude/addf/addfTools/speculate-reconcile.py`（base 自動検出を integrate 側と揃える＋回帰テスト）
- **対象**: `.claude/commands/addf-speculate.md`・`.claude/addf/guides/speculative-development.md`
  （明文化系: 対象なし終了の健全性・衝突手動解消の上位フロー・不可逆判断の明示確認・
  Markdown セクション干渉チェック軸）
- Explicit マップ横展開（#25 提案1）は規模・効果を見て採否判断し、大きければ検討スタブに分離する

### 項目3: Issue 返信

- #24・#25 へ、回収済み項目（いつ・どの Plan で対応済みか）と本 Plan での対応内容を返信する

## 影響範囲

- addfTools 1本＋スキル・ガイドの文言追加。ダウンストリーム配布対象
- 「お便り」部分（感想）は Feedback.md オーナーフィードバック欄の性格に近い — 必要なら要点のみ記録

## テスト方針

- base 自動検出は回帰テスト追加（`origin/HEAD` 設定済みリポジトリを模したフィクスチャ）
- 文言系は addf-doc-review-agent と `/addf-lint`（チェックリスト裏付け・同期ペア）で検証

## 破壊的変更の許容範囲

なし（base 検出のデフォルト挙動変更は `--base` 明示指定で従来動作を維持できる形にする）

## 要オーナー確認

なし（棚卸し確定後、判断が必要な項目が出たら Questions.md へ）

## 完了条件

- [ ] 棚卸し表の全項目が「回収済み確認 / 本 Plan で実装 / 分離 / 対応不要」のいずれかに確定している
- [ ] 未回収と確定した項目の実装とテストが `bash .claude/addf/tests/run-all.sh`・`/addf-lint` で全通過
- [ ] Issue #24・#25 へ返信する <!-- human-judgment: 返信文はオーナー確認後に投稿する -->

## AI 実装時間見積もり

1〜2セッション（棚卸し確定の結果次第）
