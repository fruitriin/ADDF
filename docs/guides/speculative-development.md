# 投機開発ガイド（worktree speculative development）

アイドル時（着手可能なタスクがないとき）に、直交する概念を git worktree で先行開発する仕組みの概観。
手順の詳細はスキル本文 [`.claude/commands/addf-speculate.md`](../../.claude/commands/addf-speculate.md) が正。
このガイドは全体像の把握用で、コマンドや判定基準はスキル本文を参照すること。

## オプトイン

投機はデフォルト無効。`.claude/addf-Behavior.toml` で明示的に有効化する:

```toml
[speculation]
enable = true      # デフォルトは false。有効化する場合はこのように true を書く（オプトイン）
max_worktrees = 7  # 同時に「開発中」にできる speculative worktree の上限（採否判断待ちのブランチは数えない）
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
  → speculative/<concept> ＋ worktree            （開発中）
  → Stage 1: 個別テスト                          （テスト通過／テスト失敗 → 打ち切り）
  → integration で相互作用検証・レビュー          （統合済み — 検証のみ）
  → origin push ＋ Dashboard / PR                （採否判断待ち）
      │
      │  （注記）有望なら子投機を分岐 …… speculative/<concept>--deep-<sub>（深化ブランチ）
      │          親が放棄 → 深化も放棄（運命連帯）
      │          親が昇格 → 新 main に繰り上げ rebase して独立の投機に繰り上がり
      │
      │  ――― ここから採否判断の4帰結 ―――
      │
      ├─ オーナー承認（PR マージ or squash マージ or プロンプト指示）
      │    → main（昇格済み）→ clean で後始末（worktree・ブランチ削除）
      ├─ 本流に昇格があった持ち越し →（要再検証）
      │    → 新 main に rebase → push --force-with-lease → Stage 1 から再検証
      │      （open PR は同じ PR がそのまま更新される）
      ├─ 数サイクル直らない持ち越し →（Pending — いつかやる）
      │    → スロット非占有・worktree 削除可・ブランチと PR は残す・在庫上限5本
      └─ 不採用 →（放棄）→ clean --delete で削除
```

**昇格 = `speculative/<concept>` → `main`**。integration は昇格の経路に入らない
（PR 経路でも同じ — PR の head は `speculative/<concept>` であり、integration ブランチから
PR を作らない）。
昇格は常にオーナーの明示承認が起点であり、エージェントが自動で本流へマージする経路は存在しない。
PR の作成は昇格ではなく提案の一形態で、マージはオーナーが GitHub 上で行うか、
オーナーからのプロンプト指示で行う。

進行状態は `.claude/Worktrees.md` に記録され、`/addf-speculate` の reconcile（check）で
実態（worktree・ローカル/origin ブランチ）との突合ができる。

## 掃除（clean）の原則

**integration の過去分は常に自動削除・speculative ブランチは明示指定制。**

- `integration/loop-*` は使い捨てのため、2日以上前のものは `clean` の冒頭で自動削除される
- `speculative/<concept>` の削除は `clean --delete` の明示指定のみ。削除前に Worktrees.md の
  「昇格済み / 放棄」記載と突合され、記録がなければ ERROR で止まる（不可逆操作のガード）

## 発展的な運用（実装済みの概観）

いずれも詳細な手順・判断基準はスキル本文が正。ここでは概観のみ:

- **昇格の PR 経路**: エージェントは `speculative/<concept>` から PR を作成して提示するまで
  （PR 本文は [`docs/guides/pr-format.md`](pr-format.md) に従い、投機の出典と integration
  検証結果を記載する）。マージはオーナーが GitHub 上で行うか、プロンプト指示で行う。
  承認チャネルはループのモードに連動する（interactive=プロンプト指示が自然 /
  relaxed・unattended=PR を作って待つのが基本形）
- **部分昇格と持ち越し**: N 本中通った分だけ先に昇格し、残りは持ち越す（1本の不備が他を
  人質に取らない）。本流に昇格があったら持ち越しは「要再検証」に落ち、次サイクルで
  新 main に rebase → `push --force-with-lease` → Stage 1 から再検証する
- **Pending**: 数サイクル直らない持ち越しの保留置き場（「放棄」ではなく「いつかやる」）。
  スロット非占有・worktree 削除可（ブランチと PR は残す）・在庫上限5本
  （6本以上で Dashboard / Questions からオーナーに整理を提案）
- **深化ブランチ**: 有望な親投機の成果を前提にした子投機 `speculative/<concept>--deep-<sub>`。
  親と運命連帯し（親放棄→共倒れ・親昇格→新 main に rebase して独立に繰り上がり）、
  通常スロットを1つ消費・2世代までが目安

投機適性の判定（向くタスク／向かないタスク）は ADDF 上流で設計中
（上流リポジトリの Plan 0038）。実装され次第このガイドへ反映される。
