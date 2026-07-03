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

### 1.7. 再構築と掃除（サイクル冒頭）

git を真実源として、`.claude/Worktrees.md`（git から再構築可能なビュー）との整合を取る:

```bash
python3 .claude/addfTools/speculate-reconcile.py
```

（tomllib 不要のためシステム python3 でそのまま動く。`rm -rf` された stale worktree の
`git worktree prune` も内部で実行される）

出力（key=value）と Worktrees.md を突合する。キーごとの見方:

| 出力キー | 見方と Worktrees.md への反映 |
|---|---|
| `branch=<b> worktree=… origin=… merged_hint=…` | speculative ブランチごとの機械的事実。表に行が無ければ**復元**（下記）。行があるのに実体が無ければ「放棄（実体なし）」等へ更新 |
| `speculative_worktree=<branch>:<path>` | 生きている投機 worktree。表のパス列と突合し、ずれていれば表を実体に合わせる |
| `integration_past=…` | **2日以上前**の integration（前日分までは日付またぎ対策の猶予で `integration_today=` 側に出る）。`clean` サブコマンドの冒頭で自動削除される |
| `detached_worktree=<path>` | どのブランチにも属さない worktree。どの走査にも乗らず放置すると永久残骸になる — 由来を確認し、不要なら `git worktree remove <path>` で外し、表に該当行があれば「放棄（実体なし）」等へ更新する |

- **git 実体があるのに Worktrees.md に記載がない**（`branch=` 行にあるのに表にない、
  またはファイル自体が失われた）→ **復元**: 状態「要再検証」で行を追加する。対象概念は
  ブランチ名 `speculative/<concept>` から推定し、最終更新は再構築時刻とする
  （テスト通過/失敗は git に残らないため次の Stage 1 で再判定する。再構築はメタデータの
  完全復元ではなく**投機を見失わないこと**の保証）。復元行の状態値は手順5の列挙の
  いずれかを使う（丸括弧は任意の注記 — 例「放棄（実体なし）」）。「対象概念（出典）」列が
  分からなければ「不明（再構築）」でよい
- **Worktrees.md に記載があるのに git 実体がない** → 掃除候補: 状態を「放棄（実体なし）」等に
  更新する（行を silent に消さない）
- `merged_hint=yes` は「main に取り込み済みの可能性」の**ヒント**にすぎない。squash マージは
  履歴が繋がらないためスクリプトでは確定できない — **正規フロー（squash 昇格）で main に
  取り込まれたブランチは恒常的に `merged_hint=no` のまま**になる（壊れているのではなく、
  履歴が繋がらないため検出できないだけ）。確定は Worktrees.md の「昇格済み」記録と
  突き合わせて判断する
- `integration_past=`（2日以上前）の integration ブランチが残っていれば、後述の
  `clean` サブコマンドで掃除する（または掃除をオーナーに案内する）

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
# .venv / node_modules / __pycache__ 等は relocatable でないため除外する（コピー先で再構築）
find ../<repo名>-spec-<concept>/.claude \( -name .venv -o -name venv -o -name node_modules -o -name __pycache__ \) \( -type d -o -type l \) -prune -exec rm -rf {} +
# git 追跡下のファイルまで消えた場合（依存をあえてコミットしている構成）は復元する
git -C ../<repo名>-spec-<concept> checkout -- .claude 2>/dev/null || true
```

- **`.claude` の複製は必須**。`.exp.md`（経験ファイル）等の .gitignore 対象ファイルは worktree に
  自動複製されないため、複製を欠くと投機側が経験・設定を失った状態で作業することになる
- **コピー元は必ず `.claude/.`（末尾 `/.`）と書くこと**。worktree 側には git 管理下の `.claude/` が
  既に存在するため、`cp -r .claude <dst>/.claude` と書くと既存ディレクトリの**中に**入れ子
  （`<dst>/.claude/.claude/`）を作るだけでマージされず、複製が成功したように見えて失敗する
- **`.venv` / `venv` / `node_modules` / `__pycache__` は複製後に必ず除去すること**（上記の `find`。
  シンボリックリンクの場合も対象）。venv は作成時の絶対パスを埋め込むため relocatable でなく、
  **コピーしても壊れている**（MCP サーバー等の依存を `.claude` 配下に持つ構成では毎サイクル必発 —
  Issue #18）。壊れたコピーを残すより、除外して worktree 側で再構築する方が安全
- **`find` の後の `git checkout -- .claude` を省略しないこと**。除去は名前ベースのため、依存を
  あえて git 追跡下にコミットしている構成では追跡ファイルまで消える — checkout が worktree の
  ブランチから復元する（該当ファイルが無ければ何もしない）
- worktree 隔離下は判断閾値を1段下げてよい（失敗を捨てられるため。CLAUDE.md「迷ったときの作法」）

### 4. 実装と Stage 1

`.claude` 配下に MCP サーバー等の依存を持つ構成では、**Stage 1 の前に必ず再構築**
（`uv sync` / `bun install` 等）を実行する（手順3の複製は venv 等を除外している。
マニフェストは git 管理下または複製対象のため worktree 側に届いている）。

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

### 6. integration 統合（テスト通過の feature が1件以上あるとき）

テスト通過の feature（今サイクルの新規と、前サイクルから採否判断待ちで繰り越したものの両方）を
1本の integration ブランチに squash 統合し、動作確認を一括する:

```bash
python3 .claude/addfTools/speculate-integrate.py speculative/<concept1> speculative/<concept2> ...
```

（tomllib 不要のためシステム python3（3.6+）でそのまま動く。uv 不要）

`--base` は省略時、origin の default branch を自動検出する（remote なし・未設定なら NOTE を出して
`main` フォールバック。検出名のローカルブランチが無ければ `origin/<name>` を起点にする）。
スクリプトは `integration/loop-<日付>` ブランチを base から**作り直し**（使い捨て・再生成可能）、
専用 worktree（`../<リポジトリ名>-integration`）の中だけで統合する。メインの作業ツリーには触れない。
なお integration worktree への `.claude` 複製は**不要**（feature worktree と違い実装作業の場ではなく、
Stage 2 の実行主体はメインツリー側のエージェントで、テスト一式も git 管理下にあるため）。

- exit 1（ERROR: base 不在・worktree の置き先が塞がっている・commit フック拒否等）→ 統合を中断し、
  エラー内容をオーナーに報告する（`commit_failed=` は差分の握り潰しを防ぐための ERROR — empty と混同しない）
- exit 0 / 2 → 以下の出力（key=value）を解釈して Worktrees.md へ反映する:

- `integrated=` — 統合成功。状態「統合済み」にして Stage 2 へ
- `conflicted=` — squash 時に衝突した feature（スクリプトが巻き戻し済み）。直交性の基準で判断する:
  - **悩まず解決できる衝突**（独立セクションへの追記同士など）→ `speculative/<concept>` ブランチ側で
    base を取り込んで解消し（昇格対象のブランチが常に自己完結するように、解消は必ず feature 側に置く）、
    スクリプトを再実行する
  - **解決に悩むレベルの衝突** → 状態「衝突」で integration から外し、残りでスクリプトを再実行する
    （integration は作り直しが正道）。silent に捨てず、Dashboard の「気になった点」で報告する
- `missing=` — ブランチが存在しない（Worktrees.md の記載と git 実体のずれ）。記録を突き合わせて訂正する
- `empty=` — base との差分が無い（既に本流へ取り込み済み等）。状態を確認して「昇格済み」等に訂正する

### 7. Stage 2 — integration 一括ゲート

integration worktree の中で一括の動作確認とレビューを行う（コストの大きい Stage 2 を N 回→1回に償却する）:

1. **相互作用テスト**: integration worktree 内でプロジェクトのテスト一式（Stage 1 と同じコマンド）を実行する。
   単体では通過した feature も、組み合わせて壊れることがある
   - 失敗したら原因 feature を特定し（feature を外して再統合すると二分探索できる）、
     該当 feature を状態「衝突」で外して integration を作り直す
2. **一括レビュー**: `addf-code-review-agent` を**ペルソナ並列（視点ずらしレビュー）**で起動する。
   起動前に `.claude/agents/addf-code-review-agent.md` を読み、ペルソナ定義と集約ルールに従うこと。
   レビュー対象は `git diff main...integration/loop-<日付>` の全差分
3. 指摘は **feature 単位に帰属**させて Worktrees.md に記録する。Critical/High は該当 feature の
   worktree で修正して Stage 1 からやり直す（ただし投機は使い捨て — 深追いするより
   状態「テスト失敗」で打ち切ってよい）

レビューまで終えたら integration worktree は削除してよい（`git worktree remove ../<リポジトリ名>-integration`）。
integration **ブランチ**は使い捨てのため origin へ push しない（次サイクルで作り直す）。

### 8. Dashboard への書き分け

unattended 自走（`dashboard_report: true`）では `.claude/Dashboard.md`（書式: `.claude/Dashboard.example.md`）に
結果を書き分ける。基準は「オーナーの採否判断の対象かどうか」:

- **「投機ブランチ（採否判断待ち）」**: integration の動作確認（手順7「Stage 2」）まで通過した feature のみ。
  前サイクルからの判断待ちも繰り越し再掲する
- **「気になった点」**: テスト失敗・衝突・上限待機。採否判断の対象ではないが、知らせる価値のある観察
  （silent に捨てない）

### 9. ブランチの退避（エフェメラル環境対策）

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

### 10. 完了処理

呼び出し元（/addf-dev）の完了処理に合流し、**Progress.md の日記に「投機サイクルを実行した
（対象概念・結果の一行）」を記録してコミットする**。Worktrees.md は gitignore だが、
サイクルが回った事実はこの日記経由でコミット履歴に残る。

cron / `/loop` 等から /addf-dev を**経由せず単独実行**された場合は、Progress.md の日記への記録と
コミットのみ行えばよい（品質検証〜アーカイブを含むフルの完了処理は /addf-dev 経由時に呼び出し元が担う）。
**呼び出し文脈が不明な場合も、日記への記録とコミットは最低限実施する**（サイクルが回った事実を
コミット履歴に残すことが投機の追跡可能性の下限）。

投機の採否はオーナーの判断（Dashboard / PR レビュー等）。**エージェントが speculative/ ブランチを
本流へ自動マージする経路は存在しない**。

## サブコマンド: clean（`/addf-speculate clean`）

**掃除の原則: integration の過去分は常に自動削除・speculative ブランチは明示指定制。**
`clean` は実行の冒頭で、**2日以上前**の `integration/loop-*` ブランチとその worktree を
自動削除する（当日・前日分は日付またぎ対策の猶予で残る。integration は使い捨てのため
記録との突合は不要。残したい場合のみ `--keep-integrations` でオプトアウトする）。

オーナーが今すぐ片付けたいとき、またはサイクル冒頭（手順 1.7「再構築と掃除」）で
`integration_past=` を検出したときの明示的な掃除手順:

1. 状態を走査する:

   ```bash
   python3 .claude/addfTools/speculate-reconcile.py
   ```

2. `.claude/Worktrees.md` で状態が「昇格済み」「放棄」のブランチを確認する
   （スクリプトの `merged_hint` はヒントにすぎない — 削除の根拠は Worktrees.md の記録に置く）
3. 確定済みブランチを明示指定して削除する:

   ```bash
   python3 .claude/addfTools/speculate-reconcile.py clean --delete speculative/<concept> [--delete ...]
   ```

   - `--delete` は**削除専用**であり、main への統合（昇格）は一切しない（昇格は後述の
     「昇格手順」で行う — オーナー承認必須）
   - スクリプトは削除前に `.claude/Worktrees.md` の記録と突合し、対象の状態が「昇格済み」
     「放棄」でなければ**何も消さずに ERROR で中断する**（記録なし・ファイルなしも同様。
     不可逆な削除だけは記録との突合をスクリプトが強制する — 「検出=スクリプト/解釈=エージェント」
     の意図的な例外。突合を承知でスキップするなら `--force-delete`）
   - 指定ブランチは worktree（あれば）→ ローカルブランチ → origin 側（remote があれば。
     無ければ SKIP）の順で削除される。**ローカル側の削除が完了しなかった場合、origin 側には
     触れない**（`kept=origin:<branch>` で報告される。退避先の origin が最後まで残るように、
     ローカルの失敗を解消してから再実行する）
   - **未コミット変更のある worktree は既定で削除拒否**（`kept=` + WARNING。`--delete` 対象・
     過去 integration とも）。破棄してよいと確認できたときのみ `--force-delete` を付ける
   - **判断待ちブランチは保護される**: `--delete` 指定のない speculative ブランチは消えない
     （`kept=` で報告される）。ブランチを残して worktree ディレクトリだけ外したいときは
     `--prune-worktrees` を付ける（未コミット変更のある worktree は外さず WARNING になる）
4. `removed=` / `kept=` の出力を Worktrees.md に反映する: 削除したブランチの行を落とす
   （履歴を残したい場合は状態「掃除済み」の注記に更新する）。exit 2 なら内容をオーナーに
   報告する — `WARNING:` は実害系（削除失敗・dirty 破棄・origin 保護）、`NOTE:` は
   指定ミス系（speculative/ 以外の指定・指定ブランチ不在）

## 昇格手順（オーナー承認必須）

`speculative/<concept>` を main へ取り込む手順。**エージェントが自動昇格する経路は作らない** —
この手順は必ずオーナーの明示承認から始まる。

**エージェントは、オーナーの明示的な応答（このセッションでの直接指示、または AskUserQuestion への
回答）なしにステップ3以降（squash マージ）を実行してはならない。Dashboard 掲載からの経過時間や
無応答を承認とみなすことを禁止する。**

1. オーナーが Dashboard / Worktrees.md の採否判断待ち一覧から昇格する feature を選び、承認する
   <!-- human-judgment: 昇格の承認はオーナーのみが行う。エージェントは提案までにとどめる -->
2. integration で衝突解消が入った feature は、その解消を `speculative/<concept>` ブランチ側に
   反映してから昇格する（昇格対象のブランチが常に自己完結する — integration のコミットは
   検証の場の産物であり、履歴の源にしない）
3. main 上で squash マージしてコミットする:

   ```bash
   git checkout main
   git merge --squash speculative/<concept>
   git commit   # プロジェクトのコミットログ規約に従って要約を書く
   ```

4. 昇格後テストとして、プロジェクトの Stage 1（ビルド・Lint・テスト）と同じコマンドを main 上で
   実行する。失敗したら squash コミットを revert し、原因を feature ブランチ側で直してから
   再昇格する（main に壊れた状態を残さない）
5. `.claude/Worktrees.md` の該当行を状態「昇格済み」に更新する
6. `/addf-speculate clean`（`clean --delete speculative/<concept>`）で後始末する
   （worktree・ローカルブランチ・origin 側の残骸が消える。スクリプトはステップ5で
   記録した「昇格済み」と突合してから削除する — 記録の更新を飛ばすと ERROR になる）

## 現バージョンの範囲

このスキルは投機サイクルの全段階を提供する: 発動ガード→再構築と掃除（手順 1.7）→選定→
worktree 起動→Stage 1→integration 統合→Stage 2→Dashboard 書き分け→push、および
`clean` サブコマンドと昇格手順。
昇格（`speculative/<concept>` → main の squash マージ）は**常にオーナー承認必須**であり、
エージェントが本流へ自動マージする経路は存在しない。

## 経験の活用

- 実行前に `addf-speculate.exp.md` が存在すれば読み、過去の経験（選定判断・直交性の見積もり精度等）を考慮する
- 実行後、新たな教訓があれば `addf-speculate.exp.md` に追記する
