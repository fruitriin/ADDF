# Plan 0035: PR 運用の標準化（Plan リンク本文・feature 昇格の PR 経路）

## 実装状況: 未着手

> 出典: 2026-07-05 オーナーフィードバック（PR #21 のレビュー体験から）。
> 「PR 本文に紐づく計画ファイルをリンクする作法を addf-dev / addf-speculate の標準にする。
> integration は使い捨て、レビュー完了した feature ブランチを本流に組み入れる運用にしたい」

## 目的

オーナーレビューの入口を GitHub PR に揃える。

1. PR 本文に「紐づく Plan ファイルへのリンク」を標準装備し、レビュー時に計画へ1クリックで到達できるようにする
2. 投機 feature の昇格に PR 経路を追加し、「integration は使い捨て・昇格は feature ブランチ」の現行設計（Plan 0028 フェーズ3）に GitHub レビューを接続する

## 項目1: PR 本文標準フォーマット（Plan リンク）

### 要件（オーナー指定）

- PR 本文に「対象 Plan ファイル」を必ず記載する
- リンクテキストは **「Plan <番号>: <計画タイトル（日本語）>」** とする（ファイル名やパスではなく）
- **バッククォートで囲まない**こと（コードスパン内の markdown リンクは plain text になりリンク化されない）
- リンク先は PR の **head ブランチの blob URL**（マージ前でも 404 にならない）:
  `https://github.com/<owner>/<repo>/blob/<headブランチ>/docs/plans-add/<file>.md`

### 記載例

```markdown
## 対象 Plan

- [Plan 0033: ダウンストリーム実測バグの修正](https://github.com/fruitriin/ADDF/blob/plan-0033-0028-0034-batch/docs/plans-add/0033-downstream-reported-fixes.md)
```

### 設計方針

- 規約本文は**単一ソース**に置き、addf-dev / addf-speculate の両スキルからは参照のみとする
  （2ファイルに同文を書くと同期ペアが増え、lint ペア追加が必要になる — Feedback.md の教訓に従い増殖を避ける）
- 置き場所の候補: `docs/guides/`（ダウンストリーム配布対象）または `.claude/templates/`。
  ダウンストリームでも PR を作る場面はあるため guides を第一候補とする
- 初出の実例: PR #21（https://github.com/fruitriin/ADDF/pull/21）

## 項目2: 投機 feature 昇格の PR 経路

### 現行（Plan 0028 フェーズ3）

- 昇格 = オーナーのセッション内明示承認 → ローカル main で `git merge --squash speculative/<concept>` → 昇格後テスト → Worktrees.md 更新 → clean --delete

### 変更

- オーナー承認の形に「**PR マージ**」を追加する。エージェントは `speculative/<concept>` から PR を作成して提示するまで（PR 本文は項目1のフォーマットに従い、投機の出典・integration 検証結果を記載）
- **マージはオーナーが GitHub 上で行う**。「エージェントが自動昇格する経路は作らない」原則は不変（PR 作成は昇格ではなく提案の一形態）
- PR マージ後の後始末を設計する:
  - Worktrees.md「昇格済み」更新のトリガー（次セッションのブートシーケンス or reconcile check の merged_hint 検出）
  - origin ブランチが GitHub の「マージ後ブランチ削除」で消えた場合の clean --delete 突合の扱い
  - squash マージ時のローカル追随（履歴が繋がらないため reconcile check では確定できない — 既知の制約）
- integration は現行どおり使い捨て（push しない・2日超自動削除）— **変更なし**

## 完了条件

- [ ] PR 本文フォーマット規約を単一ソースに記述し、addf-dev / addf-speculate から参照
- [ ] addf-speculate 昇格手順に PR 経路を追記（自動昇格禁止の文言は維持）
- [ ] PR マージ後の後始末（Worktrees.md 更新・clean 突合）の整合を確認
- [ ] lint（テンプレート同期・チェックリスト裏付け）全パス

## AI 実装時間見積もり

1セッション以内（ドキュメント中心。スクリプト変更は clean 突合の扱い次第で小規模）
