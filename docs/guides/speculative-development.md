# 投機開発ガイド（worktree speculative development）

アイドル時（着手可能なタスクがないとき）に、直交する概念を git worktree で先行開発する仕組みの概観。
手順の詳細はスキル本文 [`.claude/commands/addf-speculate.md`](../../.claude/commands/addf-speculate.md) が正。
このガイドは全体像の把握用で、コマンドや判定基準はスキル本文を参照すること。

## オプトイン

投機はデフォルト無効。`.claude/addf-Behavior.toml` で明示的に有効化する:

```toml
[speculation]
enable = true      # デフォルト false（オプトイン）
max_worktrees = 7  # 同時に「開発中」にできる speculative worktree の上限
```

`/addf-dev` がアイドルを検出したときに `/addf-speculate` が呼ばれるほか、手動で1サイクル実行してもよい。

## 2層モデル

投機は役割の異なる2種類のブランチで運用する:

| 層 | ブランチ | 役割 | 寿命 |
|---|---|---|---|
| feature 層 | `speculative/<concept>` | 投機成果の単位。昇格候補として origin へ push される | 採否判断まで（昇格 or 放棄で clean） |
| 検証層 | `integration/loop-<日付>` | 複数 feature を squash 統合して相互作用を一括検証する場 | 使い捨て（push しない・毎回作り直し・2日超は自動削除） |

**integration は検証の場であって、履歴の源にしない。** integration 上で衝突解消が入った場合も、
解消は必ず feature 側に反映する（昇格対象のブランチが常に自己完結する）。

## ライフサイクル

```
直交概念の選定
  → speculative/<concept> ＋ worktree     （開発中）
  → Stage 1: 個別テスト                   （テスト通過）
  → integration で相互作用検証・レビュー   （統合済み — 検証のみ）
  → origin push ＋ Dashboard 掲載         （採否判断待ち）
  → オーナー承認                          （昇格へ）／不採用（放棄）
  → main へ squash マージ                 （昇格済み）
  → clean で後始末                        （worktree・ブランチ削除）
```

**昇格 = `speculative/<concept>` → `main`**。integration は昇格の経路に入らない。
昇格は常にオーナーの明示承認が起点であり、エージェントが自動で本流へマージする経路は存在しない。

進行状態は `.claude/Worktrees.md` に記録され、`/addf-speculate` の reconcile（check）で
実態（worktree・ローカル/origin ブランチ）との突合ができる。

## 掃除（clean）の原則

**integration の過去分は常に自動削除・speculative ブランチは明示指定制。**

- `integration/loop-*` は使い捨てのため、2日以上前のものは `clean` の冒頭で自動削除される
- `speculative/<concept>` の削除は `clean --delete` の明示指定のみ。削除前に Worktrees.md の
  「昇格済み / 放棄」記載と突合され、記録がなければ ERROR で止まる（不可逆操作のガード）

## 発展的な運用（上流で設計中）

部分昇格（N 本中通った分だけ先に昇格）・持ち越しの rebase 追従・Pending 状態・深化ブランチ・
昇格の PR 経路・投機適性の判定（向くタスク／向かないタスク）は ADDF 上流で設計中
（上流リポジトリの Plan 0035 / 0038）。実装され次第このガイドへ反映される。
