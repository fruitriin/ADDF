# Plan 0028: addf-dev の worktree ベース投機開発

## 実装状況: 未着手（2026-07-03 詳細化済み — 粗々の起票から実装可能な計画に改訂）

## 目的

`/loop /addf-dev` が**アイドル**（ユーザー確認待ちで着手可能なタスクがない）になったとき、黙って止まる
のではなく、**依存関係のない直交概念を worktree で投機開発**し、統合ブランチで動作確認を一括して、
オーナーがまとめてレビュー・取捨選択できるようにする。

現状の addf-dev は「TODO から1タスク・逐次・現ブランチにコミット」。worktree は CLAUDE.md 並列実装方針で
「*1タスク内の* 並列サブタスク」向けに使われている。本 Plan はここを一段ずらし、
**アイドル時の *別々のタスク* を並列 worktree で投機する**方向に拡張する（既存 `speculative/` ブランチ・
unattended 哲学・Dashboard 資産の自然な延長）。

## 2層モデル（feature / integration）

オーナーの feature/release アナロジーをそのまま構造化する:

```
main（保護。オーナーがレビューしたものだけマージ）
 ├─ speculative/concept-A  ← worktree = feature ブランチ
 ├─ speculative/concept-B  ← worktree = feature ブランチ
 └─ speculative/concept-C  ← worktree = feature ブランチ
        ↓ 全 feature を1本に統合（スカッシュマージ）
 integration/loop-<日付>   ← ここで動作確認を「一括」
        ↓ Dashboard でオーナーがレビュー
   勝ち残りを main へ昇格
```

### Layer 1: feature worktree（投機）
- 直交概念ごとに `speculative/<concept>` ブランチの worktree。隔離・使い捨て・`.claude` 複製
  （CLAUDE.md 並列実装方針: worktree 起動後に `.claude` をコピー。
  `docs/knowhow/ADDF/claude-code-hooks.md` に WorktreeCreate フックでの自動コピー例があり、
  フック化する場合は実装時にイベントの発火を実地確認してから採用する）
- worktree 隔離下は閾値-1段（失敗を捨てられる。既存ドクトリン）

### Layer 2: integration ブランチ（動作確認一括）
- 機能は**統合＋動作確認**でありリリースではない。名前は `integration/`（`release/` は誤解を招く）
- **各 feature を integration ブランチへスカッシュマージ**する。理由:
  - 1 feature = 1コミットになり、Dashboard で「何が入ったか」が一望でき、feature 単位の revert が楽
  - 投機の細かい試行錯誤コミットが統合履歴を汚さない
- integration ブランチは**使い捨て・再生成可能**。main を汚さない

## 決定事項（旧「未決事項」の解消）

### 決定1: 品質ゲートはハイブリッド分割（Stage 1 = feature 単位 / Stage 2 = integration 一括）

- **Stage 1（ビルド・Lint・テスト）は各 feature worktree 内で実行する**。決定的スクリプトで安価であり、
  赤の原因切り分けは feature 単位が圧倒的に楽（統合後に赤が出るとどの feature が原因か二分探索になる）
- **Stage 1 赤の feature は integration に入れない**。Worktrees.md に「赤」として記録し、
  Dashboard の「気になった点」で報告する（silent に捨てない）
- **Stage 2（レビューエージェント）は integration で一括実行する**。コストの大きいレビューを N×→1× に
  償却し、feature 間の相互作用（単体では緑でも組み合わせて壊れる）もここで捕まえる
- integration でのみ発生した赤（衝突・相互作用）は、原因 feature を Worktrees.md に「衝突」として記録し、
  該当 feature を外して integration を再生成する（integration は使い捨てなので作り直しが正道）

### 決定2: 昇格は feature 単位・`speculative/` ブランチからの squash マージ

- 昇格の単位は **feature（= `speculative/<concept>` ブランチ1本）**。オーナーが Dashboard から
  「これとこれを採用」と選ぶ粒度と一致させる
- 手段は **`speculative/<concept>` → main の squash マージ**（cherry-pick や integration からの
  取り出しではなく）。integration のコミットは検証の場の産物であり履歴の源にしない。
  integration で衝突解消が入った feature は、解消を `speculative/` ブランチ側に反映してから昇格する
  （昇格対象のブランチが常に自己完結する）
- **main への反映は常にオーナー承認必須**。エージェントが自動昇格する経路は作らない
  （「本流に自動マージしない」の継承。Feedback.md オーナーフィードバックの「責めない・強制しない」と同根の、
  オーナーの主導権を守る設計）

### 決定3: 管理ドキュメント `.claude/Worktrees.md` は gitignore（git が真実源、ファイルは再構築可能なビュー）

- 実行時状態ファイルとして **.gitignore ADDF ブロックに追加**する（Dashboard.md と同じ扱い。
  `docs/knowhow/ADDF/ignore-file-strategy.md` の役割分けに従う）
- クラッシュ復帰の懸念（gitignore だと worktree を辿れない）は、**コミットで守るのではなく
  再構築手順で守る**: `git worktree list` + `git branch --list 'speculative/*'` が常に真実源であり、
  Worktrees.md はそこから再構築できるビューと位置づける（`docs/knowhow/ADDF/sync-lint-design.md` の
  「列挙を持たない単一ソース化」の応用。状態の二重管理によるドリフトを構造的に排除する）
- **git から機械的に再構築できるのは「存在」と「昇格済み（main マージ済み）」まで**。緑/赤/衝突・対象概念・
  最終更新は git に残らないため、復元エントリは状態を「要再検証」で初期化し（次の Stage 1 実行で緑/赤を
  再判定）、対象概念はブランチ名 `speculative/<concept>` から推定、最終更新は再構築時刻とする。
  「再構築」はメタデータの完全復元ではなく**投機を見失わないこと**の保証である
- 再構築ステップは `/addf-speculate` のサイクル冒頭に置く（後述の決定4・5）。
  git 側に実体があるのに Worktrees.md に記載がないエントリは「復元」、逆は「掃除候補」として扱う
- 記録内容: worktree パス / `speculative/` ブランチ名 / 対象概念（出典: Plan・Questions 番号等）/
  状態（開発中・緑・赤・衝突・統合済み・放棄・昇格済み）/ 最終更新。書式は addf-speculate.md 内に定義する
  （example ファイルは増やさない。書式定義を実行主体が必ず読むスキル本文に置く —
  `docs/knowhow/ADDF/rule-placement-execution-guarantee.md`「参照では実行されない」）

### 決定4: スキルは `addf-speculate` に分離し、addf-dev にはアイドル分岐1行だけ足す

- 投機の手順一式（選定→worktree 起動→Stage 1→統合→Stage 2→Dashboard 記録→掃除）は
  **新スキル `.claude/commands/addf-speculate.md`** に置く
- `addf-dev.md` の「2. タスク選択」に分岐を1つ追加する:
  「選べる未着手タスクがない場合、`addf-Behavior.toml` の `[speculation].enable` が true なら
  `/addf-speculate` を1サイクル実行して完了とする。false なら従来どおり（オーナーに確認 / 停止）」
- **投機サイクルも addf-dev の「4. 完了処理」を経由する**（ステップ3〜5をスキップしない）:
  Progress.md の日記に「投機サイクルを実行した（対象概念・結果の一行）」を記録してコミットする。
  Worktrees.md / Dashboard.md は gitignore の実行時ファイルだが、**サイクルが回った事実は
  Progress.md 経由でコミット履歴に残る**（`git branch` 以外に投機の痕跡がなくなる事態を防ぐ。
  「silent に捨てない」の適用）。ノウハウ蓄積・Feedback 記録は投機内容に応じて通常どおり
- 根拠: アイドル判定という**発動条件**は実行主体（addf-dev）が必ず読む本文にインラインで置き、
  **重い手順**は発動時にだけ読まれる別スキルに隔離する（rule-placement-execution-guarantee）。
  addf-dev の「1タスク実施」という意味論も保たれる（投機1サイクル = そのループ回の1タスク）
- `addf-speculate` は `addf-` プレフィックスの配布対象スキル。本文に ADDF 内部の計画番号を書かない
  （upstream-downstream-separation の配布ルール）

### 決定5: 掃除は「サイクル冒頭の整合 + 明示サブコマンド」。フック自動掃除はしない

- `/addf-speculate` サイクル冒頭の再構築ステップ（決定3）が、「昇格済み・放棄」状態の worktree を
  検出して削除する（`git worktree remove` + マージ済みブランチの削除。**未マージの実体があるブランチは
  消さない** — 削除するのは worktree ディレクトリと統合済み/昇格済みブランチのみ）
- 手動契機として `/addf-speculate clean` サブコマンドを設ける（オーナーが今すぐ片付けたいとき）
- セッション終了フック等での自動掃除は**採用しない**。オーナーの意図しないタイミングでの状態変更を避ける
  （Plan 0029 の「フック自動はオーナーの意図しない配置変更が起きうる」と同じ判断）

## `addf-Behavior.toml` — `[speculation]` セクション

```toml
[speculation]
# true でアイドル時投機を有効化（デフォルト無効＝オプトイン）
enable = false
# 同時 speculative worktree の上限（worktree は 200-500ms＋ディスクのコストがある）
max_worktrees = 3
```

- **enable の型検証**: 文字列 `"false"` が truthy 判定される事故を防ぐため、bool 型でなければ ERROR にする
  （`sync-optional-skills.py` の enable 型検証と同じパターン — `docs/knowhow/ADDF/optional-skill-optin.md`）。
  検証の置き場所は addf-speculate 実行時のガード（読み取り時に検証）とし、lint-toml.py は構文チェックのみの
  現状を維持する（スキーマ検証を lint-toml に足すかは Plan 0029 フェーズ2の environments スキーマ導入と
  合わせて判断する — 単独で先行させない）
- キーは最小限から始める（選定元の優先順位・命名規則などは addf-speculate.md 本文の手順として持ち、
  設定に昇格させるのは実運用で必要になってから）
- 上限到達時は新規投機を止め、Worktrees.md と Dashboard の「気になった点」に「上限で待機」と記録する
  （silent truncation 回避）

## トリガーとモード整合

- **アイドル判定**（addf-dev 側）: TODO に未着手がない、または残る未着手が全て
  「要確認（質問投下済み）」「オーナー指示待ち」である
- **発動条件は `[speculation].enable = true` のみ**（設定自体が明示オプトインなので、responsiveness との
  二重ゲートにはしない）。ただし responsiveness が `interactive` のセッションではオーナーが目の前にいるため、
  投機開始前に一言確認する（relaxed / unattended は確認なしで開始してよい）
- `speculative/` ブランチ命名は既存（unattended 閾値割れ隔離）と統一。「本流に自動マージしない」を継承
- **昇格は計画レビュー文化の延長**。Dashboard への書き分けは既存2セクションの役割に合わせて一本化する:
  - 「投機ブランチ（採否判断待ち）」= **緑の feature のみ**（integration の動作確認まで通過し、
    オーナーの採否判断を待つもの）
  - 「気になった点」= 赤・衝突・上限待機（採否判断の対象ではなく、知らせる価値のある観察。決定1と整合）

## 直交概念の選定

worktree が衝突を防ぐのは作業が本当に独立しているときだけ。

- **選定元の優先順位**（2026-07-03 の現状に合わせて更新）:
  1. 既存 Plan に記録済みの Low/Info 残課題（例: Plan 0029 フェーズ1の L1/L3。分解済み・独立性高・低リスク）
  2. `.claude/Questions.md` の未回答質問の最有力解釈による投機（unattended ドクトリンそのもの）
  3. オーナー常設リクエスト（TODO 末尾）から導出できる独立作業
- **選定禁止**: オーナー指示待ちと明示された項目（現時点では Plan 0026 のセキュリティ残課題等）は
  投機対象にしない。**新規概念の発明は最終手段**（望まれない投機を避ける）
- **直交性ヒューリスティック**: 「触るであろうファイル集合が重ならない」を Plan から見積もる。予測が外れたら
  integration の衝突で回収（統合は直交性予測の答え合わせの場でもある）

## 実装フェーズ分割

### フェーズ1: 骨格（単発投機が回る）
1. `addf-Behavior.toml` に `[speculation]` セクション追加（デフォルト disable）
2. `.claude/commands/addf-speculate.md` 新設: 選定→worktree 起動（`.claude` 複製込み）→実装→Stage 1→
   Worktrees.md 記録、まで（integration は後続フェーズ）。enable 型検証ガード・上限チェックを含む
3. `addf-dev.md` にアイドル分岐を追加（決定4の1行）
4. `.gitignore` ADDF ブロックに `.claude/Worktrees.md` を追加
5. addf-init コピーリストへの追加作業は**不要**（カテゴリ1が `.claude/commands/addf-*.md` のグロブ列挙のため
   自動カバーされる）。CLAUDE.md / development-process.md / AGENTS.md へ言及を足す場合のみ、
   ペア5の被覆確認と同期ペア1〜4の再確認を同フェーズで行う
6. テスト: mktemp サンドボックスの fake git リポジトリで「enable=false で発動しない / 型不正 ERROR /
   上限到達で待機記録 / worktree 作成と Worktrees.md 記録の整合」の状態別ふるまいを検証するシェルテスト
   （`.claude/tests/tools/` 配下。mktemp サンドボックス + fake リポジトリの手法は sync-lint-design の
   テスト作法を転用する）

### フェーズ2: integration 統合と一括ゲート
1. integration ブランチ生成（`integration/loop-<日付>`）と feature のスカッシュマージ手順
2. Stage 2 一括レビュー・衝突/相互作用の記録と integration 再生成の手順
3. Dashboard.md 生成との連携（緑は「投機ブランチ（採否判断待ち）」、赤/衝突/上限待機は「気になった点」
   — 「トリガーとモード整合」の書き分けに従う）
4. テスト: 2 feature の統合、片方衝突時の記録と再生成をサンドボックスで検証

### フェーズ3: 復帰・掃除・昇格運用
1. サイクル冒頭の再構築ステップ（git 実体 → Worktrees.md 復元・掃除候補検出）
2. `/addf-speculate clean` サブコマンド
3. 昇格手順の文書化（squash マージ・衝突解消の feature 側反映・昇格後の状態遷移）
4. `docs/guides/` への運用ガイド追記と `/addf-overview` 再生成

## 影響範囲

- `.claude/addf-Behavior.toml`（`[speculation]` 追加）
- `.claude/commands/addf-speculate.md`（新規・配布対象）
- `.claude/commands/addf-dev.md`（アイドル分岐1行）
- `.gitignore` ADDF ブロック（`.claude/Worktrees.md`）
- `/addf-init` コピーリスト（addf-speculate.md。ペア5被覆）
- `.claude/tests/tools/`（サンドボックステスト追加）
- `docs/guides/development-process.md` ほか同期ペア対象（addf-dev の手順変更が及ぶ場合 — 変更したら
  Feedback.md のルールに従い `/addf-lint` セクション6で確認）
- Dashboard.example.md（既存の「投機ブランチ」セクションで足りる見込み。不足があればフェーズ2で拡張）

## 残る未決事項（オーナー判断・実装時判断）

- **WorktreeCreate フックによる `.claude` 自動コピーの採否**: knowhow に記録はあるが、フックイベントの
  発火は実装時に実地確認してから。確認できなければ addf-speculate.md の手順内で明示コピーする（確実側に倒す）
- **integration での Stage 2 の重さ**: unattended 自走時はペルソナ並列が既定（ProgressTemplate）だが、
  投機サイクルごとに毎回ペルソナ並列はコスト過大の可能性。integration 一括時のみペルソナ並列・
  feature 単発時は単体、を暫定とし、実運用のコストを見て調整する
- **選定元の優先順位を設定に昇格させるか**: 最小スキーマで開始し、プロジェクトごとに変えたい実需が
  出てから `[speculation]` にキーを足す（YAGNI）

## 完了条件

各条件に検証手段を併記する（実行チェックの裏付け — Plan 0027 のドクトリン）:

- アイドル時に直交概念を worktree で投機開発できる
  — サンドボックステスト（フェーズ1-6）が enable 時の worktree 作成・記録を PASS
- 投機は enable=false で一切発動しない（ダウンストリーム配布時の安全性）
  — 同テストの disable ケースが PASS。`bash .claude/tests/run-all.sh` に組み込まれている
- integration ブランチでスカッシュ統合＋動作確認一括ができ、衝突が silent にならない
  — フェーズ2-4 のテストが PASS（衝突 feature の Worktrees.md への記録まで機械検証）。
  Dashboard への反映はエージェントの自然文生成のため機械検証できない
  <!-- human-judgment: Dashboard の「気になった点」に赤・衝突・上限待機が載っていることを目視確認 -->
- 進行中 worktree が管理ドキュメントで追え、クラッシュ後も git 実体から再構築できる
  — フェーズ3-1 の再構築をサンドボックスで検証（Worktrees.md を消して復元されること）
- 投機上限が `addf-Behavior.toml` で設定でき、上限到達が記録される — フェーズ1-6 のテストが PASS
- 投機は本流に自動マージされず、昇格は squash マージ手順書に従いオーナー承認で行う
  — 手順書に `<!-- human-judgment -->` 相当の承認ステップが明記されている（lint-checklist の対象に
    する場合は TARGETS 追加もセットで）

## 関連

- CLAUDE.md「並列実装方針」— worktree 利用ルール。本 Plan はこれを「タスク間並列」へ拡張
- CLAUDE.md「迷ったときの作法（7割共有原則）」— 3軸・unattended・speculative/ ブランチ・Dashboard
- `docs/knowhow/ADDF/rule-placement-execution-guarantee.md` — 決定3・4の配置根拠
- `docs/knowhow/ADDF/sync-lint-design.md` — 列挙を持たない単一ソース化（決定3）・サンドボックステスト作法
- `docs/knowhow/ADDF/optional-skill-optin.md` — enable 型検証・オプトイン設計の前例
- `docs/knowhow/ADDF/ignore-file-strategy.md` — Worktrees.md の gitignore 判断
- `docs/knowhow/ADDF/claude-code-hooks.md` — WorktreeCreate フック（採否は実装時確認）
- `docs/knowhow/ADDF/upstream-downstream-separation.md` — 配布スキルの記述ルール
- Plan 0029 — Behavior.toml スキーマ拡張・オプトイン機構の並走 Plan（lint-toml スキーマ検証の判断を共有）
