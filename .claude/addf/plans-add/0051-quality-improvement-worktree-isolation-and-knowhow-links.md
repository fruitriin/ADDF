# Plan 0051: プロセス品質向上 — worktree 隔離破りの防止策と knowhow 双方向リンク解消

## 実装状況: 完了（2026-07-10）

> 出典: TODO.addf.md オーナーリクエスト「タスクが無くなったら品質向上計画を追加する」。
> 2026-07-10、cron 経由 `/loop` 自律サイクルが Plan 0040・0048 を「要確認」に切り替えて
> 静観に転じ、実行可能なバックログが尽きた時点で本セッションが起票。項目1は本セッション自身が
> 実地で踏んだ手順ミスの再発防止（推測ではなく実測に基づく）。

## 関連 Plan

- [Plan 0041: コンテキスト枯渇によるループ停止の壁の突破](0041-context-exhaustion-loop-wall.md) — 「止まらない教義」を支える無人自律運用の信頼性領域。本 Plan の項目1は同じ領域の別の穴
- knowhow: [cron-loop-worktree-race.md](../knowhow/ADDF/cron-loop-worktree-race.md) — cron 再入と working tree 競合の先行知見。本 Plan 項目1はこれと隣接するが異なる原因（後述）

## 目的

1. `isolation: "worktree"` で起動されたエージェントが、意図せず割当て worktree の外（共有
   メインチェックアウト）に対して git 操作（コミット含む）を行ってしまうリスクを、実地の
   ヒヤリハットに基づき低減する
2. `/addf-lint` セクション8が検出した knowhow 片方向リンク12件を解消する

## 現状の挙動

### 項目1が対象とする問題（実地観測・本セッションのヒヤリハット）

本セッションは `.claude/worktrees/agent-ae1a202b75030daf0` に隔離された状態で起動されたが、
状況確認のため `cd /Users/riin/workspace/AutomatonDevDriveFramework && <コマンド>` という
絶対パス cd を伴う Bash 呼び出しを実行した。Bash ツールは「作業ディレクトリはコマンド間で
持続する」ため、この一度の `cd` の後、明示的に `cd` し直さない限り**以降の全ての Bash 呼び出しが
共有メインチェックアウト側で実行され続けた**。この状態で `git commit` を実行してしまい、
本来 worktree 側のブランチに積むべきコミットが直接 main チェックアウトの `main` ブランチに
記録されるという隔離破りが発生した（内容自体は正当な記録だったため実害は限定的だったが、
本来あってはならない経路である）。

一方、`Write` ツールは worktree 隔離を検知し、共有チェックアウト側のパスへの書き込みを
明示的なエラーで拒否した（`This agent is isolated in the worktree ... Edit the worktree copy
of this file instead of the shared-checkout path.`）。**`Write`/`Edit` には隔離保護があるが、
`Bash` 経由の `git` 操作にはこの保護が効かない**という非対称性が今回の実地で判明した。

cron 経由の並行実行を扱う既存知見 `cron-loop-worktree-race.md` は「同一 working tree に対する
別セッションの再入」を扱っており、原因も対処も本件（**単一セッション内で自分自身が cd で
隔離を離脱してしまう**）とは異なる。両者は「worktree 隔離が破られる」という結果は似ているが、
原因が異なるため、既存ファイルへの追記ではなく本 Plan で新規に整理する。

### 項目2が対象とする問題

`/addf-lint` セクション8（knowhow 双方向リンク検査）が `.claude/addf/knowhow/ADDF/` 配下で
片方向リンク12件を INFO 検出している（ブロッキングではない）。`sync-lint-design.md` が
ハブノードとして多数から参照される一方、自身の「関連ノウハウ」リストに全ての参照元を
載せていないのが主因。

## 変更内容（項目）

### 項目1: worktree 隔離破りの防止策

- **対象**: `CLAUDE.md`「並列実装方針」節、および新規 knowhow 1件
- CLAUDE.md「並列実装方針」に、worktree 隔離下のエージェント自身への注意として以下を追記する:
  - 絶対パスへの `cd` を伴う Bash 呼び出しは、以降の Bash 呼び出しにも作業ディレクトリが
    持続する（ツールの一時的な状態ではない）。共有チェックアウトへの `cd` は次に明示的に
    worktree パスへ `cd` し直すまで隔離を離脱させる
  - 状態確認のために共有チェックアウト側を覗く必要がある場合は、`cd &&` を1コマンド内で
    完結させる（`cd <path> && <command1> && <command2>`）か、`git -C <path> <command>` を
    使い、作業ディレクトリ自体を動かさない
- `.claude/addf/knowhow/ADDF/` に新規 knowhow（例: `worktree-isolation-cd-persistence.md`）を
  追加し、本事象（`Write`/`Edit` には隔離保護があるが `Bash` の `cd` 永続にはない非対称性、
  再発防止策）を記録する。`/addf-knowhow` で重複チェックの上、`cron-loop-worktree-race.md` との
  相互参照リンクも張る
- 完了条件は「明記の追加」までとし、Bash ツール自体へのガード実装（hook 等での強制）は
  スコープ外とする（既存の `destructive-git-guard.sh` のような PreToolUse hook で
  worktree 外パスへの `cd`/`git` を検知・警告する案は「未解決の問い」として本 Plan には
  含めず、必要性が繰り返し観測されたら別 Plan で検討する）

### 項目2: knowhow 双方向リンク12件の解消

- **対象**: `.claude/addf/knowhow/ADDF/` 配下（lint 出力より）
  - `optional-skill-optin.md` → `checklist-backing-lint.md`
  - `skill-design-patterns.md` → `checklist-backing-lint.md` / `optional-skill-optin.md`
  - `existing-project-install-pattern.md` → `upstream-downstream-separation.md` / `sync-lint-design.md`
  - `plan-refinement-pattern.md` → `sync-lint-design.md` / `checklist-backing-lint.md`
  - `speculative-integration-design.md` → `sync-lint-design.md` / `worktree-dotdir-copy.md` / `optional-skill-optin.md`
  - `worktree-dotdir-copy.md` → `optional-skill-optin.md` / `sync-lint-design.md`
- `/addf-knowhow-network` を実行し、`sync-lint-design.md` 側（ハブノード）を中心に逆方向リンクを補完する
- 実行後 `/addf-lint` セクション8を再実行し、INFO 件数が12件から減少したことを確認する

## 影響範囲

- `CLAUDE.md`（「並列実装方針」節への注意事項追記。ダウンストリーム配布テンプレートのため
  文言は汎用的に保つ）
- `.claude/addf/knowhow/ADDF/`（新規 knowhow 1件 + 双方向リンク12件の追記）
- `.claude/addf/knowhow/INDEX.addf.md`（reindex で追随）
- 同期ペア（CLAUDE.md ⇔ development-process.md 等）に影響しうるため、変更後は
  `/addf-lint` セクション6（テンプレート同期）を確認する

## テスト方針

- `bash .claude/addf/tests/run-all.sh` を再実行し全通過を確認する
- `/addf-lint` を再実行し、セクション8の INFO 件数が12件から減少していることを確認する
  （0件化を必須にはしない — 新規 knowhow 追加で新たな片方向リンクが生じた場合は次サイクルで対応）
- 項目1はコードではなくドキュメント変更のため、`addf-doc-review-agent` の起動条件
  （`*.md` 変更）に該当する。品質ゲートで起動すること

## 破壊的変更の許容範囲

なし（ドキュメント注記追加と knowhow リンク補完のみ。既存の挙動・スキル・フックへの変更なし）

## 要オーナー確認

なし。ただし本 Plan 自体が「worktree 隔離下のエージェントが隔離を破って main に直接コミットした」
という手順ミスの事後報告を兼ねる。当該コミット（`main` ブランチ、Q5・Q6 の質問投下記録）は
内容自体に問題がないため取り消していない。オーナーが確認し、必要なら別途対応する
（<!-- human-judgment --> 実害の有無・要 revert かどうかの最終判断はオーナーに委ねる）

## 完了条件

- [x] CLAUDE.md「並列実装方針」に worktree 隔離破り（cd 永続）への注意事項が追記されている
- [x] 本事象を記録した knowhow エントリが `.claude/addf/knowhow/ADDF/` に追加され、
  `cron-loop-worktree-race.md` との相互参照リンクが張られている
- [x] lint セクション8の INFO 検出件数が12件から0件に減少している（Plan 記載の対象12件に加え、
  新設 knowhow との相互参照2件（`cron-loop-worktree-race.md` ⇔ `worktree-isolation-cd-persistence.md`・
  `cron-loop-worktree-race.md` → `sync-lint-design.md`）を計14件のリンク行として反映。うち
  `cron-loop-worktree-race.md` → `sync-lint-design.md` は旧「## 参照」節との重複を避けるため
  「## 関連ノウハウ」節に一本化した。`/addf-knowhow-network` スキルは呼ばず直接編集で対応。
  `addf-code-review-agent` によりスクリプト突合で検証済み）
- [x] `bash .claude/addf/tests/run-all.sh` と `/addf-lint` が通過する

## AI 実装時間見積もり

1セッション以内（ドキュメント注記追加 + knowhow 1件新設 + リンク補完12件 + lint/テスト再実行）
