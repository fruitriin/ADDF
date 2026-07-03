# Plan 0028: addf-dev の worktree ベース投機開発

## 実装状況: 一部完了（2026-07-03 フェーズ1 完了。integration 統合はフェーズ2、復帰・掃除・昇格運用はフェーズ3）

### フェーズ1 実装記録（2026-07-03）

- `[speculation]` セクション（enable=false デフォルト / max_worktrees=3）を addf-Behavior.toml に追加
- `speculate-guard.py` 新設: enable/max_worktrees の型検証（bool が int のサブクラスである罠に対応）・
  `git worktree list --porcelain` による speculative worktree 数の上限チェック。exit 3値（0/1/2）
- `addf-speculate.md` 新設（配布対象スキル）: ガード→選定→worktree 起動（`.claude` 複製必須）→
  Stage 1→Worktrees.md 記録→origin へ push（remote なしは SKIP）。`.claude` 複製は手順内の明示コピーで
  実装（WorktreeCreate フック方式は未検証のため確実側。フック化はフェーズ2以降の検討）
- addf-dev.md にアイドル分岐を追加、.gitignore ADDF ブロックに `.claude/Worktrees.md` を追加
- テスト `test-speculate-guard.sh` 10ケース（サンドボックス: 欠如=無効・型不正 ERROR・上限 WARNING・
  非 speculative worktree の除外）

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
- **`.claude` の複製は必須**（2026-07-03 オーナー決定）: `.exp.md`（経験ファイル）等の .gitignore 対象
  ファイルが大量にあり、worktree には自動複製されない。複製を欠くと投機側エージェントが経験・設定を
  失った状態で作業することになる。手段（WorktreeCreate フック自動化 or スキル手順内の明示コピー）は
  実装時判断（「残る未決事項」参照）だが、複製すること自体は要件
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
  テスト失敗の原因切り分けは feature 単位が圧倒的に楽（統合後に失敗するとどの feature が原因か二分探索になる）
- **Stage 1 でテスト失敗した feature は integration に入れない**。Worktrees.md に「テスト失敗」として記録し、
  Dashboard の「気になった点」で報告する（silent に捨てない）
- **Stage 2（レビューエージェント）は integration で一括実行する**。コストの大きいレビューを N×→1× に
  償却し、feature 間の相互作用（単体ではテスト通過でも組み合わせて壊れる）もここで捕まえる。
  Stage 2 の重さは「integration 一括時のみペルソナ並列・feature 単発時は単体」とする（2026-07-03 オーナー採用）
- integration でのみ発生した失敗（衝突・相互作用）は、原因 feature を Worktrees.md に「衝突」として記録し、
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
- **git から機械的に再構築できるのは「存在」と「昇格済み（main マージ済み）」まで**。テスト通過/失敗/衝突・
  対象概念・最終更新は git に残らないため、復元エントリは状態を「要再検証」で初期化し（次の Stage 1 実行で
  テスト通過/失敗を再判定）、対象概念はブランチ名 `speculative/<concept>` から推定、最終更新は再構築時刻とする。
  「再構築」はメタデータの完全復元ではなく**投機を見失わないこと**の保証である
- **エフェメラル実行環境（Claude Code on the Web 等）への対応**: コンテナが使い捨てのため、ローカルの
  worktree・ブランチ・Worktrees.md はセッション終了で全て失われる。これは gitignore の弱点ではなく
  「真実源をローカル git に限定した場合」の弱点なので、**サイクル末に `speculative/<concept>` ブランチを
  origin へ push する**ことを標準動作にして解決する（remote が真実源に加わる。作業成果はブランチとして残り、
  worktree ディレクトリと Worktrees.md は失われてよい使い捨てのまま）。再構築（サイクル冒頭）は
  `git branch -r --list 'origin/speculative/*'` も走査対象に含める。remote が無いローカル環境では
  push を SKIP する（欠如 = SKIP の設計原則）。integration ブランチは再生成可能なので push しない
- 再構築ステップは `/addf-speculate` のサイクル冒頭に置く（後述の決定4・5）。
  git 側に実体があるのに Worktrees.md に記載がないエントリは「復元」、逆は「掃除候補」として扱う
- 記録内容: worktree パス / `speculative/` ブランチ名 / 対象概念（出典: Plan・Questions 番号等）/
  状態（開発中・テスト通過・テスト失敗・衝突・統合済み・放棄・昇格済み）/ 最終更新。書式は addf-speculate.md 内に定義する
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
- **採否判断待ちの feature が残る状態でも、clean・次サイクルの投機は止めない**:
  - 判断待ち（テスト通過・Dashboard 掲載済み）の feature **ブランチ**は clean・再構築の削除対象にしない（保護）。
    worktree **ディレクトリ**は掃除してよい（ブランチが真実源。再開時は worktree を張り直す）
  - 次サイクルでは判断待ちを Dashboard に**繰り越し再掲**し、新規のテスト通過分と合わせて integration を
    再生成して一括確認する（integration は毎サイクル作り直すので、繰り越しの混在は自然に扱える）
  - 上限（max_worktrees）は「開発中」の worktree にのみ適用し、判断待ちブランチは数えない
- origin へ push 済みの `speculative/` ブランチは、昇格済み・放棄が確定した時点でローカルと合わせて
  origin からも削除する（リモートに投機の残骸を溜めない）
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
  設定に昇格させるのは実運用で必要になってから。2026-07-03 オーナー承認）
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
  - 「投機ブランチ（採否判断待ち）」= **テスト通過の feature のみ**（integration の動作確認まで通過し、
    オーナーの採否判断を待つもの）
  - 「気になった点」= テスト失敗・衝突・上限待機（採否判断の対象ではなく、知らせる価値のある観察。決定1と整合）

## 直交概念の選定

worktree が衝突を防ぐのは作業が本当に独立しているときだけ。

- **選定元の優先順位**（2026-07-03 の現状に合わせて更新）:
  1. 既存 Plan に記録済みの Low/Info 残課題（例: Plan 0029 フェーズ1の L1/L3。分解済み・独立性高・低リスク）
  2. `.claude/Questions.md` の未回答質問の最有力解釈による投機（unattended ドクトリンそのもの）
  3. オーナー常設リクエスト（TODO 末尾）から導出できる独立作業
- **選定禁止**: オーナー指示待ちと明示された項目（現時点では Plan 0026 のセキュリティ残課題等）は
  投機対象にしない。**新規概念の発明は最終手段**（望まれない投機を避ける）
- **直交性ヒューリスティック**: 求める基準は「衝突ゼロ」ではなく**「衝突してもエージェントが悩まず解決
  できる粒度か」**（2026-07-03 オーナー方針）。「触るであろうファイル集合が重ならない」は目安であり、
  多少重なっても自明に解決できる衝突（独立セクションへの追記同士など）ならナーバスにならず投機してよい。
  解決に悩むレベルの衝突が出たときだけ、該当 feature を「衝突」として外す（決定1の既存フロー。
  統合は直交性予測の答え合わせの場でもある）

## 実装フェーズ分割

### フェーズ1: 骨格（単発投機が回る）
1. `addf-Behavior.toml` に `[speculation]` セクション追加（デフォルト disable）
2. `.claude/commands/addf-speculate.md` 新設: 選定→worktree 起動（`.claude` 複製込み）→実装→Stage 1→
   Worktrees.md 記録→サイクル末に `speculative/` ブランチを origin へ push（remote なければ SKIP）、
   まで（integration は後続フェーズ）。enable 型検証ガード・上限チェックを含む
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
3. Dashboard.md 生成との連携（テスト通過は「投機ブランチ（採否判断待ち）」、テスト失敗/衝突/上限待機は
   「気になった点」— 「トリガーとモード整合」の書き分けに従う）
4. テスト: 2 feature の統合、片方衝突時の記録と再生成をサンドボックスで検証

### フェーズ3: 復帰・掃除・昇格運用
1. サイクル冒頭の再構築ステップ（git 実体 → Worktrees.md 復元・掃除候補検出）。
   `git worktree prune` もここで実行する — フェーズ1の speculate-guard.py は読み取り専用のため、
   `rm -rf` で消された stale worktree が prune まで active にカウントされ続ける既知の制約がある
2. `/addf-speculate clean` サブコマンド（判断待ちブランチの保護・origin 側の確定済みブランチ削除を含む）
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

## 残る未決事項（実装時判断）

2026-07-03 のオーナーレビューで大半が解消された（Stage 2 の重さ → 決定1 に採用 /
選定元の設定昇格 → YAGNI 承認 / `.claude` 複製 → 必須要件化）。残りは1件:

- **`.claude` 複製の実現手段**（複製自体は必須 — Layer 1 参照）: WorktreeCreate フックによる自動コピー
  （`docs/knowhow/ADDF/claude-code-hooks.md` に例あり）か、addf-speculate.md の手順内の明示コピーか。
  フックイベントの発火を実装時に実地確認し、確認できなければ手順内明示コピーに倒す（確実側）。
  フック採用時も、フック未導入環境へのフォールバックとして手順内コピーを残すのが安全

## 拡張アイデア（2026-07-03 オーナーレビュー由来。本 Plan のスコープ外・将来検討）

- **深さの投機**: 横（別概念）に広げるだけでなく、やりきった投機から分派する深さ方向の投機
  （フェーズ1 を投機しきったら続けてフェーズ2 を投機する・依存関係のある次の Plan に着手してみる）。
  ブランチ構造は `speculative/<concept>-<次段>` のような分派で現行機構のまま表現できる見込み。
  実運用で横の投機が枯れる状況が観測されたら、本 Plan の後続フェーズまたは独立 Plan として起案する
- **MVP バリエーション実験**: 1つの Plan に対して複数バリエーションを worktree で並列実装し、
  動作だけ比較してもらう実験形式。本スキルの趣旨（統合ブランチで一括動作確認）とは軸が異なるため、
  必要になったら**別スキル・別 Plan** として起案する（worktree 基盤・Worktrees.md・Dashboard 報告の
  機構は共用できる）

## 完了条件

各条件に検証手段を併記する（実行チェックの裏付け — Plan 0027 のドクトリン）:

- アイドル時に直交概念を worktree で投機開発できる
  — サンドボックステスト（フェーズ1-6）が enable 時の worktree 作成・記録を PASS
- 投機は enable=false で一切発動しない（ダウンストリーム配布時の安全性）
  — 同テストの disable ケースが PASS。`bash .claude/tests/run-all.sh` に組み込まれている
- integration ブランチでスカッシュ統合＋動作確認一括ができ、衝突が silent にならない
  — フェーズ2-4 のテストが PASS（衝突 feature の Worktrees.md への記録まで機械検証）。
  Dashboard への反映はエージェントの自然文生成のため機械検証できない
  <!-- human-judgment: Dashboard の「気になった点」にテスト失敗・衝突・上限待機が載っていることを目視確認 -->
- 進行中 worktree が管理ドキュメントで追え、クラッシュ後も git 実体から再構築できる
  — フェーズ3-1 の再構築をサンドボックスで検証（Worktrees.md を消して復元されること）
- 投機上限が `addf-Behavior.toml` で設定でき、上限到達が記録される — フェーズ1-6 のテストが PASS
- エフェメラル実行環境でも投機がセッション終了で失われない — サンドボックスに bare リポジトリを
  origin として設定し、サイクル末 push（remote なしでは SKIP）をテストで検証
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
