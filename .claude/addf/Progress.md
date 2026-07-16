# 進捗表

## 運用ルール

### タスク開始時
1. `.claude/addf/Feedback.md` を読み、前回の改善アクションで未対応のものがあれば考慮する
2. 以下の手順で Markdown チェックリストを作成する
   1. 1ショットで作業できる範囲にサブタスクを分割する
   2. 並行作業できる粒度でさらに分割する
   3. 各サブタスクにテスト作成・統合テスト・Lint・ビルドが必要か検討し、必要なら追加する
   4. 必要に応じて 2.1〜2.3 を再帰的に適用する

### 作業中
3. サブタスク着手時に `- [x]` でチェックしていく。並列可能なタスクはコンテナオーケストレーションを利用する
   - Plan の曖昧さで確信が持てないときは CLAUDE.md「迷ったときの作法（7割共有原則）」に従う（閾値割れなら `.claude/addf/Questions.md` に質問を置いてタスクを切り替える）
   - 長大なタスクでは、サブタスク完了時点でブランチ `checkpoint/<phase>-<N>` を切ってよい。別方針を試すときは checkpoint から `alt/` を分岐する
3.5. **日記を書く（代替わり引き継ぎ）**（「3.5」は後続の番号参照を壊さないための意図的な枝番）: resume・compaction・`/loop` の次イテレーションで起きる「小さな代替わり」のたびに、次の代の自分（同僚でもあり、寝て起きたあとの自分でもある）が状況に入れるよう、タスクの「#### 日記」セクションにエントリーを書く
   - **書くタイミング**: サブタスク完了時 / 重要な判断をした直後 / 計画を変更したとき / コンテキストが長くなり compaction を予感したとき
   - **書式（4項目）**（時刻 HH:MM は省略可）:
     ```
     ##### YYYY-MM-DD HH:MM — <出来事の一行>
     **やったこと**: <完了した作業と判断の要約>
     **今の見立て**: <現状認識。確信度があれば記す>
     **次の自分へ**: <次に着手すべきこと・先に確認すべきこと>
     **気になっていること**: <未解決の不確実性・前提・違和感。なければ「なし」>
     ```
   - 「日記」という語彙の意図（「遺書」を使わない理由）は `.claude/addf/guides/development-process.md` 参照
   - ブランチ checkpoint が「何がコミットされたか（事実）」を残すのに対し、日記は「なぜそうしたか・次に何を考えていたか（文脈）」を残す。両方で前任者の靴に履き替えられる
   - 日記の自動生成フックは導入しない。書くこと自体が思考の整理であり、次の自分への手紙として人格を持って書く
   - **コンテキスト満杯時の指針**（Plan 0041 の「満杯時の出口」教義）: コンテキスト残量が少ないことを理由にループを止めない・タスク着手を控えない。auto-compact は harness が上限接近時に自動発動し、`post-compact-recovery.sh` と日記が受け止める。エージェントの仕事は止まらないこと。残量少時は**復帰容易性の高いタスク**（進捗がファイル差分に現れる・サブタスクの刻みが小さい）を優先し、**未コミットの大きな途中状態を長時間抱える one-shot 級タスクは残量少時に着手しない**。進捗の外部化（こまめなコミット・チェックリスト更新・日記）を通常より密に刻む
4. 実装フェーズの最終サブタスク完了時、以下の知見を `/addf-knowhow` で記録する（既存 knowhow の更新も含む）:
   - **コーディング知見**: 実装中に発見した再利用可能なパターン、落とし穴、技術的判断とその根拠
   - **分かれ道の目印**: 差し戻し・やり直し・想定外の判断が発生したサブタスクがあれば、使用したスキルの `.exp.md`「🔀 分かれ道の目印」にも追記する（書式: `.claude/addf/templates/ExperienceTemplate.md`。失敗の告白ではなく、意思決定が枝分かれしたポイントと次に同じ分岐に立ったときの選び方を道標として書く）

### エージェント起動時の共通ルール
- エージェントチーム（TeamCreate）やサブエージェント（Agent）を作成するとき、各エージェントへのプロンプトに **最初に `/addf-knowhow-index` を実行する** よう指示を含めること
- これにより各エージェントがプロジェクトの知見ベースを把握した状態で作業を開始できる

### タスク完了時 — 品質検証

4. プロジェクトのビルド・Lint・テストコマンドを実行する
   - ADD フレームワークテスト: `bash .claude/addf/tests/run-all.sh`
   - **失敗した場合 → 実装に差し戻す**。原因分析 → 修正 → 再実行
5. `addf-code-review-agent` でコードレビューを実施する
   - 通常タスクは単体（ペルソナなし）で起動する
   - **マイルストーン・リリース直前・`mode: critical` 宣言時・unattended 自走時（`/addf-mode unattended`）**は、ペルソナ並列（視点ずらしレビュー）を起動する。起動前に `.claude/agents/addf-code-review-agent.md` を読み、ペルソナ定義に従うこと
   - ペルソナ並列の集約: 同一箇所・同一原因の指摘は1件にまとめてペルソナを列挙する。**2ペルソナ以上が独立に指摘した項目は重要度を1段上げる**（コンセンサス補正）
   - **ドキュメント変更を含むタスクでは `addf-doc-review-agent` も起動する**（ドキュメントドリフト検出）。起動条件: `git diff` に `*.md` 変更・`docs/` 配下変更・`.claude/commands/` や `.claude/agents/` の定義変更のいずれかが含まれる場合。起動判断はメインエージェント側で行い、条件を満たさなければスキップしてよい。エージェントの詳細は `.claude/agents/addf-doc-review-agent.md` を参照。**コードレビューと並列でよい**（両者は変更差分の別観点を見るため独立実行できる。集約は起動側で行う）
6. `addf-contribution-agent` で ADD フレームワークへのコントリビューション候補を検出する
7. レビュー指摘・発見への対応（**一次軸: 主題との関係 / 二次軸: クリティカル度**）:
   - **主題に沿うもの → このフェーズ内で対応する**（クリティカル度は問わない）:
     - Plan の意図の延長にある修正・追加・改善は、修正範囲が広くても同一 Plan 内でやりきる
     - レビュー指摘（Critical/High/Medium/Low/Info いずれも）が Plan の主題内なら、
       Critical/High は必修正・Medium 以下は原則修正の順で対応する
   - **主題から外れるもの → 別 Plan に切り出す**（「ついでに見つけてしまった何か」）:
     - 発見されたバグ・改善余地の関心事が現在の Plan と異なるなら、修正せずに新しい
       Plan（`.claude/addf/plans/`）を書き起こして `TODO.md` に追加し、現在の Plan を完了させる
     - **切り出した Plan の優先度はクリティカル度で決める**（二次軸）: 主題外の Critical/High は
       TODO 優先度最上位に置き、次タスクで即着手する（「フェーズ内先送り禁止」の安全性は
       粒度変更後も維持される）
   - **判定に迷ったら「主題外」に倒し、切り出し先の Plan に主題内で扱えなかった理由を残す**
     （後から統合したくなったら次サイクルで判断すればよい）
   - **切り出した Plan の実装ルート**は次サイクルの `/addf-dev` で
     `変更ルート判断表`（`.claude/addf/guides/speculative-development.md` の「変更ルート判断」節）
     に従う（本ルールは「切り出すか否か」、変更ルート判断表は「どう実装するか」の別軸）
   - 修正後、ビルド・Lint・テストを再実行して通過を確認する
8. 品質ゲートで得た知見を `/addf-knowhow` で記録する:
   - **品質ゲート知見**: レビューエージェントが検出したパターン（セキュリティ、コード品質、分離パターン違反等）のうち、他のタスクでも再発しうるもの

#### ノウハウ蓄積

9. 投入されたタスクのPlanに実装完了状況を反映する
10. タスク全体の総括知見を `/addf-knowhow` で記録する:
    - **タスク総括**: 計画と実装のギャップ、想定外だった点、次回同種タスクへの教訓。コーディング・品質ゲートで既に記録した知見と重複しないこと

#### フィードバック記録

11. `.claude/addf/Feedback.md` にPlan, TODO, Progress推進エンジンの問題の記録・改善アクションを追記する。反映済みの項目は削除する
12. `.claude/addf/Feedback.md` にプロジェクト進行上の問題の記録・改善アクションを追記する。反映済みの項目は削除する
13. Progress 推進エンジン自体に関するフィードバック・ノウハウがあれば、テンプレート（`.claude/addf/templates/ProgressTemplate.addf.md`）の改善案を `.claude/addf/Feedback.md` に記録する

#### アーカイブとコミット

14. `.claude/addf/Progresses/YYYY-MM-DD-プラン名.md` にリネームして移動し、`.claude/addf/templates/ProgressTemplate.addf.md` から新規の Progress.md を作成する
15. コミットする

---

## タスク

### 現在のタスク: Plan 0058 — Dashboard の HTML 化とブラウザレビュー UI（フェーズA）

#### サブタスクチェックリスト

- [x] Plan 0058 を標準テンプレートに昇格（フェーズA/B/C・FB フィールド仕様確定）
- [x] PlanTemplate.md に owner_feedback / feedback_ask / feedback_since の書式を追記
- [x] 未完了 Plan 11件（0026/0029/0030/0039/0040/0041/0048/0054/0056/0057/0058）に遡及付与
  - 値は TODO 転記ではなく Plan 本文・Questions.md と突合して決めた（待ち6・済4・不要1）
- [x] generate-dashboard.py 実装（stdlib のみ・フォールバック付き）
- [x] package.json（dashboard:sync / dashboard:dev / dashboard:build）・
      .gitignore（dashboard/ 生成物）・VitePress config 生成（port 5180 明示）
- [x] テスト test-generate-dashboard.sh（欠如 = SKIP 設計・7 PASS）
- [x] 動作確認: 生成実行 + npm run dashboard:build 通過（ブラウザ目視はオーナー確認と併合）
- [ ] Stage 1: bash .claude/addf/tests/run-all.sh・/addf-lint
- [x] Stage 2: code-review + doc-review + contribution-agent 並列（3体完了）
- [x] レビュー指摘対応（Critical 3・Warning 7・Suggestion/Low 多数を集約対応）
  - contribution Critical: テストの実リポジトリ固有コンテンツ依存 → drift-injection 化
  - code C1: 奇数バッククォートでエスケープ免除 → 先読みマッチング方式に書き換え
  - code C2: title/ask/state の未エスケープ挿入 → sv() ヘルパーで全挿入点を統一
  - doc W2: 進行中×待ちの握りつぶし → キュー除外は済/不要のみに変更
- [ ] Stage 1 再実行 → 完了処理（knowhow・Feedback・Progress アーカイブ・コミット）

#### 日記

##### 2026-07-16 — フェーズA 着手（検討スタブから昇格）

**やったこと**: 検討スタブ 0058 を標準テンプレートに昇格。オーナー判断は同日の対話で
全て出揃った（二層構造・ローカル別インスタンス・3ページ・FB 明示フィールド・叩き合意・
「Plan 本文ビューアは実運用で動く」）。knowhow 4本（docs-site-single-source-sync /
sync-lint-design / plan-status-drift-check / ignore-file-strategy）を確認済み。
**今の見立て**: 生成は全ソース決定論で可能（確信度9割）。唯一の設計リスクは
FB フィールドの書式が将来の lint（ペア6拡張や 0056 系統樹）と噛み合うか — 行頭
key: value の execution_style 前例に従えば安全側。
**次の自分へ**: PlanTemplate 追記 → 遡及付与 → スクリプトの順。遡及付与の値は
Progress.md のこのチェックリスト直下ではなく各 Plan と Questions.md を見て決めること。
**気になっていること**: dashboard/ を丸ごと gitignore すると lint-residual-paths の
gitignore 非対称検知に引っかからないか（Plan 0052 の新設検査）。.gitignore 編集時に
lint を即実行して確認する。

##### 2026-07-16 — 実装完了・品質ゲートへ

**やったこと**: 遡及付与11件（0040 の複数行ヘッダ違反も1行化）→ generate-dashboard.py
（stdlib のみ・約450行）→ package.json / .gitignore 配線 → テスト7件 → 実ビルド通過。
実装中に2つのバグを実測検出: (1) タイトル抽出の正規表現が line[2:] 適用後なのに
`^# Plan` を期待（重複表示）、(2) Vue コンパイルが裸の `<concept>`（英字開始）で死ぬ —
エスケープ方針を「HTML コメント以外の `<` は全て &lt;」に強化して解決。
**今の見立て**: フェーズA の実装は完了。Stage 1（run-all.sh・lint）→ Stage 2
（code-review + doc-review 並列）が残り。
**次の自分へ**: Stage 2 のレビュー依頼時、esc_vue のインラインコード分割
（バッククォート split の偶奇）と Questions パースの正規表現を重点的に見てもらうこと。
**気になっていること**: gh pr list のタイムアウト10秒が cron 無人実行時に遅い可能性。
実測で問題が出たら短縮する。

##### 2026-07-16 — contribution-agent が Critical 検出（DS 誤 FAIL の再発）

**やったこと**: Stage 2 レビュー3体を並列起動。contribution-agent が完了し Critical 1件:
test-generate-dashboard.sh の Test 3（Plan 1件以上）・Test 5 後半（&lt;concept の実在証拠）が
**実リポジトリの固有コンテンツ依存**で、ダウンストリームでは必ず FAIL（サンドボックス実測済み。
Issue #29 / Plan 0055 と同型の再発）。他: Medium = DS への閲覧手順案内なし /
Low = PlanTemplate の Plan 0058 番号露出・Dashboard.md と dashboard/ の命名紛らわしさ。
**今の見立て**: 修正方針は決定 — generate-dashboard.py に env var `ADDF_DASHBOARD_ROOT` で
ルート上書きを追加し、テストは mktemp サンドボックスに合成 Plan（裸の <concept> 入り・
DS 構成 plans/+TODO.md）を作って検証する drift-injection 方式へ書き換え。
**次の自分へ**: code-review / doc-review の2体がまだ実行中。結果が来たら同一箇所の指摘を
集約してから修正すること（exp の教訓: 指摘単位の分割委譲は衝突する）。
**気になっていること**: コンテキスト使用 255k 超の観測あり。compaction が来ても
このチェックリストと日記で復帰できる状態を維持する。
