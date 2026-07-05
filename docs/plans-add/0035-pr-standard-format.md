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

### 昇格の定義を明文化する（2026-07-05 オーナー指摘）

「昇格」が**何から何への遷移か**を guides に図解で明記する。現行ドキュメントはスキル本文の
手順に埋まっており、「integration → main」と誤読する余地がある。

- 正確な定義: **昇格 = `speculative/<concept>` → `main`**。integration は検証の場であって
  昇格の経路に入らない（履歴の源にしない — 衝突解消も feature 側に反映する現行原則の帰結）
- ライフサイクル全体を1枚で示す:
  `選定 → speculative/<concept>＋worktree（開発中）→ Stage 1（テスト通過）→
  integration で相互作用検証（統合済み・使い捨て）→ origin push＋Dashboard（採否判断待ち）→
  オーナー承認（PR マージ or squash マージ）→ main（昇格済み）→ clean（後始末）`
  ※ Pending / 要再検証 / 放棄 への分岐も同じ図に載せる
- 置き場所: **Plan 0028 フェーズ3-4 の guides 追記（投機運用ガイド）と統合して単一ソース化**する。
  addf-speculate.md からは参照のみ（同期ペアを増やさない）

### 部分昇格と持ち越し（2026-07-05 オーナー判断）

N 本の投機のうち通った分だけ先に本流へ入れ、残りは次サイクルで直す運用を明文化する
（例: 3本中2本を昇格、1本は次回 integration までに修正）。integration ごと all-or-nothing に
マージしない — 1本の不備が他を人質に取らない。

- **持ち越し feature の再検証**: 本流に昇格があったら、持ち越し中の feature は状態「要再検証」に
  落とす。次サイクルで新しい main に **rebase → `git push --force-with-lease`** で
  speculative ブランチを更新し、Stage 1 から再検証する（open PR がある場合は同じ PR が
  そのまま更新され、持ち越しの文脈が保たれる）
- **滞留の出口 — Pending 状態（新設）**: 数サイクル経っても直らない持ち越し feature は
  「放棄」ではなく **「Pending」**（いつかやる）に落とす:
  - Pending はアクティブな投機スロットを**占有しない**（スロットは開け、新しい投機を妨げない）
  - Pending の worktree は削除してよい（ブランチと PR は残す。再開時に worktree を作り直す）
  - Pending 在庫は **5本まで**許容。6本以上になったら Dashboard / Questions でオーナーに
    整理（再開 or 放棄）を提案する
  - Worktrees.md の状態一覧に「Pending」を追加する（既存の「上限で待機」は開始前キュー、
    「Pending」は持ち越し保留 — 意味の違いをスキル本文に明記して混同を防ぐ）

## 完了条件

- [ ] PR 本文フォーマット規約を単一ソースに記述し、addf-dev / addf-speculate から参照
- [ ] addf-speculate 昇格手順に PR 経路を追記（自動昇格禁止の文言は維持）
- [ ] 昇格の定義（speculative/<concept> → main。integration は経路外）とライフサイクル図を
      guides に明記（Plan 0028 フェーズ3-4 の投機運用ガイドと統合。実装順の依存:
      0028 3-4 を先に実施するか、本 Plan で guides 追記ごと引き取るかを着手時に決める）
- [ ] 部分昇格＋持ち越し運用を addf-speculate に追記（要再検証→rebase＋force-with-lease、
      Pending 状態の新設・スロット非占有・在庫上限5・6本以上でオーナーへ整理提案）
- [ ] PR マージ後の後始末（Worktrees.md 更新・clean 突合）の整合を確認
      （Pending の worktree 削除と clean の突合も含む）
- [ ] lint（テンプレート同期・チェックリスト裏付け）全パス

## AI 実装時間見積もり

1セッション以内（ドキュメント中心。スクリプト変更は clean 突合の扱い次第で小規模）
