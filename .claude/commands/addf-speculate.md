---
name: addf-speculate
description: |
  アイドル時（着手可能なタスクがないとき）に、直交概念を git worktree で投機開発する。
  投機は speculative/ ブランチに隔離され、本流には自動マージされない。
  `addf-Behavior.toml` の `[speculation].enable = true` でオプトインした場合のみ動作する。
  /addf-dev がアイドルを検出したときに呼ばれるほか、手動で1サイクル実行してもよい。
user_invocable: true
---

# addf-speculate — アイドル時の worktree 投機開発（1サイクル）

TODO に着手可能なタスクがないとき、黙って止まる代わりに、独立した概念を worktree で投機開発して
オーナーがまとめてレビュー・取捨選択できる状態を作る。

## 手順

### 1. 発動ガード

```bash
uv run --python 3.11 .claude/addfTools/speculate-guard.py
```

uv が無い環境では `python3` で直接実行する（Python 3.11+ が必要。旧い Python では tomllib 欠如の ERROR となり投機は開始できない — フェイルセーフ）。

- `enable=false`（exit 0）→ **何もせず終了**し、「投機は無効（オプトインは addf-Behavior.toml の
  `[speculation].enable`）」と報告する
- exit 1（型不正等の ERROR）→ 投機せず、エラー内容をオーナーに報告する
- exit 2（上限到達 WARNING）→ 新規投機はせず、`.claude/Worktrees.md` に「上限で待機」を記録して終了する
- exit 0 かつ `enable=true` → 次へ（`slots` が今回起こせる worktree の残り枠）

### 1.5. モード確認（interactive のみ）

`CLAUDE.local.md` の `# ADDF モード`（`/addf-mode` が管理）を確認し、responsiveness が
`interactive` の場合は**投機開始前にオーナーへ一言確認する**（オーナーが目の前にいるため）。
`relaxed` / `unattended`（またはモード未設定）は確認なしで開始してよい。

### 2. 投機対象の選定

選定元の優先順位:

1. 既存の計画ファイルに記録済みの軽微な残課題（Low/Info 等。分解済み・独立性が高く・低リスク）
2. `.claude/Questions.md` の未回答質問の最有力解釈による投機
3. オーナー常設リクエスト（TODO 末尾等）から導出できる独立作業

ルール:

- **選定禁止**: オーナー指示待ちと明示された項目は投機対象にしない。**新規概念の発明は最終手段**
- **直交性の基準は「衝突ゼロ」ではなく「衝突してもエージェントが悩まず解決できる粒度か」**。
  触るファイル集合の重なりは目安であり、自明に解決できる衝突（独立セクションへの追記同士など）なら
  ナーバスにならず投機してよい。解決に悩むレベルの衝突が予想される組み合わせだけ避ける

### 3. worktree の起動

対象概念ごとに（`slots` の範囲内で）:

```bash
git worktree add ../<repo名>-spec-<concept> -b speculative/<concept>
cp -r .claude/. ../<repo名>-spec-<concept>/.claude/
```

- **`.claude` の複製は必須**。`.exp.md`（経験ファイル）等の .gitignore 対象ファイルは worktree に
  自動複製されないため、複製を欠くと投機側が経験・設定を失った状態で作業することになる
- **コピー元は必ず `.claude/.`（末尾 `/.`）と書くこと**。worktree 側には git 管理下の `.claude/` が
  既に存在するため、`cp -r .claude <dst>/.claude` と書くと既存ディレクトリの**中に**入れ子
  （`<dst>/.claude/.claude/`）を作るだけでマージされず、複製が成功したように見えて失敗する
- worktree 隔離下は判断閾値を1段下げてよい（失敗を捨てられるため。CLAUDE.md「迷ったときの作法」）

### 4. 実装と Stage 1

各 worktree 内で対象概念を実装し、**Stage 1（ビルド・Lint・テスト）を worktree 内で実行**する。

- テスト通過 → 状態「テスト通過」
- テスト失敗 → 一度は原因分析・修正を試み、それでも失敗するなら状態「テスト失敗」で打ち切る
  （投機は使い捨て。深追いしない）

### 5. Worktrees.md への記録

`.claude/Worktrees.md`（.gitignore 対象の実行時状態ファイル）に全投機を記録する。
**打ち切った投機も silent に消さず記録する**。

書式:

```markdown
# Worktrees（投機の進行状態）

| worktree パス | ブランチ | 対象概念（出典） | 状態 | 最終更新 |
|---|---|---|---|---|
| ../repo-spec-foo | speculative/foo | <出典と一行説明> | テスト通過 | YYYY-MM-DD HH:MM |
```

状態: `開発中` / `テスト通過` / `テスト失敗` / `衝突` / `統合済み` / `放棄` / `昇格済み` / `上限で待機` / `要再検証`

### 6. ブランチの退避（エフェメラル環境対策）

サイクル末に、各 `speculative/<concept>` ブランチを origin へ push する:

```bash
if git remote get-url origin >/dev/null 2>&1; then
  git push -u origin speculative/<concept>
else
  echo "SKIP: remote なし（ローカル環境）"
fi
```

- remote が無い環境では SKIP してよい（欠如 = SKIP）。remote があるのに push が失敗した場合
  （認証・reject・ネットワーク断）は SKIP 扱いにせず、失敗として報告する
- コンテナ実行（Claude Code on the Web 等）ではセッション終了で worktree もローカルブランチも
  失われるため、**push が投機を残す唯一の手段**。省略しないこと

### 7. 完了処理

呼び出し元（/addf-dev）の完了処理に合流し、**Progress.md の日記に「投機サイクルを実行した
（対象概念・結果の一行）」を記録してコミットする**。Worktrees.md は gitignore だが、
サイクルが回った事実はこの日記経由でコミット履歴に残る。

投機の採否はオーナーの判断（Dashboard / PR レビュー等）。**エージェントが speculative/ ブランチを
本流へ自動マージする経路は存在しない**。

## 現バージョンの範囲

このスキルは現在「単発投機」（選定→worktree→Stage 1→記録→push）までを提供する。
複数投機の統合ブランチでの一括動作確認・採否判断待ちの繰り越し・worktree の掃除
（`clean` サブコマンド）は将来バージョンで追加予定。

## 経験の活用

- 実行前に `addf-speculate.exp.md` が存在すれば読み、過去の経験（選定判断・直交性の見積もり精度等）を考慮する
- 実行後、新たな教訓があれば `addf-speculate.exp.md` に追記する
