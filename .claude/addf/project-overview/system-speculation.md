# 投機開発 — Idle-time speculative development with git worktrees

> 概念単位の記録。実装がスキル/エージェント/フック/ファイルのどれであっても、
> 「アイドル時に直交概念を worktree で先行開発し、オーナーが取捨選択できる状態を作る」に関わるものをまとめている。

**オプトイン機能**: デフォルト無効。`addf-Behavior.toml` の `[speculation] enable = true` で有効化する。
ADDF 本体リポジトリでは有効化済み（`max_worktrees = 7`）。

## 構成要素

| 種別 | 名前 | 役割 |
|---|---|---|
| スキル | addf-speculate | 投機1サイクルの手順（発動ガード→再構築と掃除→窓検出→選定→worktree 起動→Stage 1→integration 統合→Stage 2→Dashboard 書き分け→push）＋ `clean` サブコマンド＋昇格手順（経路A/B）・部分昇格と持ち越し・深化ブランチ |
| ツール | .claude/addf/addfTools/speculate-guard.py | 発動ガード。`[speculation]` 設定検証と現在の worktree 数を突合し `enable/max_worktrees/active/slots` を出力（exit 0=OK / 1=ERROR / 2=上限到達） |
| ツール | .claude/addf/addfTools/speculate-integrate.py | `integration/loop-<日付>` を base から作り直し、指定 feature を1本ずつ squash 統合。衝突 feature はスキップ報告して続行。`--base` 省略時は origin の default branch を自動検出 |
| ツール | .claude/addf/addfTools/speculate-reconcile.py | check: git 実体（worktree・ローカル/リモートブランチ）の走査＋投機在庫の機械シグナル（`pending_count` / `active_count` — 窓検出の入力）。clean: 確定済みブランチの削除（Worktrees.md の「昇格済み/放棄」記録と突合し、記録がなければ ERROR で中断） |
| ファイル | .claude/addf/Worktrees.md | 投機の進行状態の記録（.gitignore 対象の実行時状態。git から再構築可能なビュー） |
| 設定 | .claude/addf/Behavior.toml [speculation] | `enable`（デフォルト false・オプトイン）/ `max_worktrees`（同時「開発中」上限。採否判断待ちは数えない） |
| ガイド | .claude/addf/guides/speculative-development.md | 2層モデル・ライフサイクル・clean 原則・投機適性の概観＋ **one-shot（一発通し切り）マーカーの意味と実施様式の単一ソース**（手順の正はスキル本文） |
| ガイド | .claude/addf/guides/pr-format.md | PR 本文規約（投機昇格 PR は投機由来の追記事項あり。→ system-distribution と共有） |
| フック連携 | /addf-dev 手順2 | アイドル検出時（着手可能タスクなし）に `enable = true` なら /addf-speculate を1サイクル実行 |
| エージェント | addf-code-review-agent（3ペルソナ並列） | 投機 Stage 2 の integration 一括レビュー（→ system-quality） |
| ファイル | .claude/addf/Dashboard.md | 「投機ブランチ（採否判断待ち）」と「気になった点」の書き分け先（→ system-planning） |
| テスト | .claude/addf/tests/tools/test-speculate-guard.sh / test-speculate-integrate.sh / test-speculate-reconcile.sh | speculate ツール3本の自動テスト（pre-commit フックで commit 失敗を注入するテスト手法を含む） |
| knowhow | .claude/addf/knowhow/ADDF/worktree-dotdir-copy.md / speculative-integration-design.md | worktree への .claude 複製の罠、squash 統合設計の知見 |

## 設計思想

「TODO に着手可能なタスクがないとき、黙って止まる代わりに、独立した概念を先行開発してオーナーがまとめてレビュー・取捨選択できる状態を作る」。CLAUDE.md「迷ったときの作法」の unattended（投機続行）を、アイドル時の能動的な開発形態にまで拡張したもの（Plan 0028）。

### 2層モデル

| 層 | ブランチ | 役割 | 寿命 |
|---|---|---|---|
| feature 層 | `speculative/<concept>` | 投機成果の単位。昇格候補として origin へ push される | 採否判断まで（昇格 or 放棄で clean） |
| 検証層 | `integration/loop-<日付>` | 複数 feature を squash 統合して相互作用を一括検証する場 | 使い捨て（push しない・毎回作り直し・2日超は clean 冒頭で自動削除） |

**integration は検証の場であって履歴の源にしない**。integration 上で衝突解消が入っても、解消は必ず feature 側に反映する（昇格対象のブランチが常に自己完結する）。Stage 2（レビュー・相互作用テスト）を N 回→1回に償却するのが integration の目的。

### 投機適性と Plan 化フォールバック — Plan 0038

すべての概念が投機に向くわけではない。選定時に適性を判定し、**迷ったら不向き側に倒す**: 不向き/禁止と判定した概念は捨てずに `execution_style: one-shot` マーカー付き Plan として起案する（Plan 化フォールバック。TODO の状態注記にも one-shot を併記し、silent に捨てない）。one-shot = 一発通し切りの実施様式で、定義の単一ソースは guides/speculative-development.md。

### 大改造の窓 — Plan 0038（手順 1.8）

投機在庫がゼロになった瞬間は one-shot 大改造の事前清算条件が自然に満たされている**窓**である。サイクル冒頭（次の投機を始める前）に「在庫ゼロ（reconcile の `pending_count=0` / `active_count=0` を含む機械シグナル）∧ one-shot マーカー付き未着手 Plan の存在」を判定し、成立していればオーナーへ実施可否を提示する。relaxed/unattended では Questions.md に窓エントリを置いて**そのサイクルの新規投機を開始しない**（窓を保って待つ）。窓保持カウンタが3以上になったら保持を解除して投機を再開する（自走を無期限に止めない — 質問自体は有効なまま）。**one-shot Plan の実施は常にオーナーの明示応答が起点**であり、窓の検出は提案まで。ADDF 本体では Plan 0037（ディレクトリ大集約）がこの窓検出で提案され、オーナー同席の別セッションで実施された。

### 昇格の2経路と部分昇格 — Plan 0035

- **経路A（ローカル squash マージ）**: オーナーが Dashboard / Worktrees.md / open PR から選んで承認 → feature 側で衝突解消を自己完結 → main へ squash マージ
- **経路B（PR 経路）**: relaxed / unattended の基本形。**Stage 2 通過済みの feature のみ** pr-format.md 規約で PR を作成し（PR 作成は昇格ではなく提案の一形態）、**マージはオーナーが GitHub 上で行う**。Worktrees.md に PR 番号を注記する
- **部分昇格と持ち越し**: 複数 feature のうち一部だけ昇格し、残りは持ち越せる。数サイクル直らないものは **Pending**（持ち越しの保留 — ブランチと PR は存在したまま「いつかやる」に落とす）へ
- **深化ブランチ（投機の系譜）**: 採否判断待ちの有望な投機をさらに掘る子投機 `speculative/<concept>--deep-<sub>`。Worktrees.md の「対象概念（出典）」列に親を明記する

### 安全設計（自動マージ経路の不在）

- **昇格 = `speculative/<concept>` → `main` の squash マージ。常にオーナーの明示承認が起点**（このセッションでの直接指示・AskUserQuestion への回答・Questions.md の Answer・GitHub 上での PR マージのいずれか）。Dashboard 掲載や PR オープンからの経過時間・無応答を承認とみなすことは明文で禁止されている
- 破壊的 git 操作（reset --hard・ブランチ作り直し）は専用 worktree に閉じ込め、メインの作業ツリーには触れない
- `clean --delete` は削除前に Worktrees.md の「昇格済み/放棄」記載と突合し、記録がなければ何も消さずに ERROR で中断する（不可逆操作のガード。「検出=スクリプト/解釈=エージェント」原則の意図的な例外）
- 判断待ちブランチは保護される（`--delete` 指定のないものは消えない）。未コミット変更のある worktree は既定で削除拒否
- squash マージは履歴が繋がらないため `merged_hint` はヒントに留まる — 削除の根拠は Worktrees.md の記録に置く

### git を真実源とする状態管理

Worktrees.md は「git から再構築可能なビュー」。サイクル冒頭の reconcile（check）で git 実体と突合し、実体があるのに記載がなければ「要再検証」で復元、記載があるのに実体がなければ「放棄（実体なし）」へ更新する（行を silent に消さない）。状態語彙: 開発中 / テスト通過 / テスト失敗 / 衝突 / 統合済み / 放棄 / 昇格済み / 上限で待機 / 要再検証。

### worktree 複製の作法

feature worktree には `.claude` の複製が必須（`.exp.md` 等の .gitignore 対象は自動複製されないため）。コピー元は必ず `.claude/.`（末尾 `/.`）と書く（入れ子事故防止）。`.venv` / `node_modules` / `__pycache__` は relocatable でないため複製後に除去し、worktree 側で再構築する（Issue #18 の教訓）。integration worktree への複製は不要（実装の場ではないため）。

## 主要フロー

```
/addf-dev がアイドル検出（または手動 /addf-speculate）
  │
  ├─ 1. speculate-guard.py（enable? 上限? → slots 算出）
  ├─ 1.5 interactive モードならオーナーへ一言確認
  ├─ 1.7 speculate-reconcile.py で Worktrees.md と git 実体を突合（復元・掃除候補検出。
  │      pending_count / active_count の機械シグナルも出力）
  ├─ 1.8 大改造の窓検出（在庫ゼロ ∧ one-shot Plan あり → 実施提案。
  │      relaxed/unattended は窓を保って待機、窓保持カウント3で解除）
  │
  ├─ 2. 投機対象の選定（投機適性を判定 — 不向き/禁止は one-shot Plan 化して捨てない）
  │     優先: 計画済みの軽微な残課題 > Questions.md の最有力解釈 > オーナー常設リクエスト
  │         （採否判断待ちの有望な投機の深化 — 子投機 — も選定対象）
  │     禁止: オーナー指示待ち項目。新規概念の発明は最終手段
  │     直交性 =「衝突ゼロ」ではなく「衝突してもエージェントが悩まず解決できる粒度」
  │
  ├─ 3. worktree 起動（speculative/<concept> + .claude/. 複製 + venv 等除去）
  ├─ 4. 実装 + Stage 1（worktree 内。失敗は深追いせず打ち切り — 投機は使い捨て）
  ├─ 5. Worktrees.md へ記録（打ち切りも silent に消さない）
  │
  ├─ 6. speculate-integrate.py で integration/loop-<日付> に squash 統合
  │     conflicted → 悩まない衝突は feature 側で解消して再実行 / 悩む衝突は外す
  ├─ 7. Stage 2 一括ゲート（相互作用テスト + code-review 3ペルソナ並列。指摘は feature 単位に帰属）
  │
  ├─ 8. Dashboard 書き分け（採否判断待ち / 気になった点）
  ├─ 9. speculative/* を origin へ push（エフェメラル環境では push が投機を残す唯一の手段）
  └─ 10. Progress.md の日記に記録してコミット（サイクルが回った事実を履歴に残す）

（オーナーの明示承認後）
昇格・経路A: feature 側で衝突解消を自己完結 → main へ squash マージ → 昇格後テスト
  → 失敗なら revert して feature 側で修正 → Worktrees.md「昇格済み」→ clean --delete で後始末
昇格・経路B: Stage 2 通過済み feature から PR 作成（pr-format.md 規約）→ Worktrees.md に
  PR 番号注記 → オーナーが GitHub 上でマージ → 「昇格済み」→ clean --delete
（部分昇格可。残りは持ち越し or Pending へ。有望な判断待ちは --deep- 子投機で深化できる）
```

## 下流でのカスタマイズ

- `addf-Behavior.toml` の `[speculation] enable = true` でオプトイン、`max_worktrees` で並行数を調整
- 投機対象の選定元（残課題・Questions.md・常設リクエスト・深化候補）はプロジェクトの運用に従う
- 昇格経路は responsiveness モードで選ぶ（interactive → 経路A も可 / relaxed・unattended → PR 経路が基本形）
- 大改造の窓で提案される one-shot Plan の実施判断は常にオーナー（エージェントは検出と提案まで）

## 関連するシステム

- **計画駆動**: /addf-dev のアイドル検出が発動点。結果は Dashboard.md（unattended 情報伝達）と Progress.md 日記に残る。「迷ったときの作法」の unattended 投機続行と同じ speculative/ ブランチ隔離を使う。投機不適合の概念は one-shot マーカー付き Plan として計画駆動へフォールバックし、大改造の窓が実施タイミングを提案する
- **品質ゲート**: Stage 1 を worktree 単位で、Stage 2（ペルソナ並列レビュー）を integration で一括実行する
- **セッション管理**: [speculation] 設定は addf-Behavior.toml（Behavior 設定の共有）。モード確認（1.5）は CLAUDE.local.md の /addf-mode 状態を参照
- **配布・導入**: speculate-*.py は addfTools として配布対象。ガード類型は「実行前ゲート=フェイルセーフ ERROR」（Python 3.11 tomllib 欠如時は投機を開始しない）
