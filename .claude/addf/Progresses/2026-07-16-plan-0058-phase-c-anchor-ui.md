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

### 現在のタスク: Plan 0058 フェーズC — ダッシュボード自前アンカー UI・二層接続

#### サブタスクチェックリスト

- [x] C-1: Plan 0058 フェーズC 節の詳細化（コメント置き場・Questions.md 役割分担・実装方式・optional 化要否の確定 — 決定C-1〜C-7 として Plan に記載）
- [x] C-2: アンカーコメント UI — generate-dashboard.py が Layout.vue（アンカー選択・コメント入力・スレッド表示）とコメント API（Vite dev サーバーミドルウェア）を生成する
- [x] C-3: コメントの集約 — DashboardComments.json の未解決コメントと `~/.crit/reviews/` 未解決コメントをダッシュボード「要フィードバック」に表示する
- [x] C-4: ブートシーケンス配線 — CLAUDE.md 手順 1.7（未解決コメント読み込み）追加・同期ペア（AGENTS.md / development-process.md / addf-init コピーリスト）対応
- [x] C-α（オーナー追加要望）: プランビューア折りたたみ構文 — `::: details`（VitePress ネイティブ・第一推奨）＋ `<details>/<summary>` esc_vue パススルー（GitHub 表示互換）の両対応
- [x] C-5: テスト拡張 — test-generate-dashboard.sh にテーマ・API・コメント集約の検証を追加（Test 8〜11・欠如=SKIP 設計維持）
- [x] C-6: Stage 1 — run-all.sh・lint 一式の全通過
- [x] C-7: Stage 2 — 3体レビュー（code-review・doc-review・contribution-agent）と指摘反映（Critical 2/High 1/Medium 4/Low 多数を反映・Stage 1 再通過・テスト17件）
- [x] C-8: 完了処理 — knowhow（vitepress-embed-escape-pitfalls 追記＋INDEX 更新）・Feedback（並行起票の TODO 未登録）・Plan 0058/0065/TODO 反映・コミット

#### 日記

##### 2026-07-16 — フェーズC 着手（オーナー指示「アンカーポイント計画を実施する」）
**やったこと**: /addf-dev 引数でフェーズC 実施指示を受領。フェーズA 実装（generate-dashboard.py 647行・3ページ生成・esc_vue エスケープ・plans コピー）とフェーズB 実測記録（crit files モードの限界＝内部リンク不可・anchor 原文保持の踏襲方針）を読み込み、チェックリストを作成した。
**今の見立て**: 設計方針はオーナー確定済み（アンカーコメント→ファイル書き出し→次セッションのコンテキスト）。実装方式は VitePress dev サーバーの Vite プラグイン（configureServer ミドルウェア）でコメント書き出し API を持たせるのが最小構成 — 追加プロセス・追加依存なしで dashboard:dev にそのまま乗る。確信度8割。
**次の自分へ**: C-1 の Plan 詰めから。コメント置き場は `.claude/addf/DashboardComments.json`（コミット対象・Questions.md と同じ共有チャンネル扱い）で書く予定。Questions.md との分担は「方向」で分ける（Questions=エージェント発の質問、コメント=オーナー発の文脈付きフィードバック。Q への回答がコメントで来たら反映時に Questions.md へ転記して単一ソースを保つ）。
**気になっていること**: 静的ビルド（dashboard:build）ではコメント API が動かない点は仕様として明記が必要。CLAUDE.md 変更は同期ペア lint（ペア2・3・5）に引っかかりやすいので C-4 で lint-template-sync を都度回すこと。

##### 2026-07-16 — C-1〜C-4 完了・オーナー追加要望（折りたたみ構文）取り込み
**やったこと**: Plan 0058 フェーズC を決定C-1〜C-7 として詰め、実装した。(1) config.mts に Vite プラグイン `/api/comments`（GET/POST/PATCH・書き込み先 DashboardComments.json 固定・source_path はサーバー側導出）、(2) Layout.vue（ホバー💬ボタン・パネル・anchor 原文一致バッジ・orphan 表示）、(3) crit `~/.crit/reviews/` 集約（ADDF_CRIT_REVIEWS_DIR で上書き可）、(4) ブートシーケンス 1.7 配線＋同期ペア3面（AGENTS/development-process/addf-init）。curl で API 全パス（GET/POST/PATCH reply/resolve/404/400）実測済み・vitepress build 通過。作業中にオーナーから折りたたみ構文の要望があり、`::: details` 推奨＋ `<details>/<summary>` の esc_vue パススルーで両対応した。
**今の見立て**: ビルド時に発覚した「インラインコード内 `{{.go_template}}` が Vue interpolation で爆発する」問題は code_inline レンダラの v-pre 化で解決（esc_vue のコードスパン不変ポリシーはそのまま）。これは knowhow `vitepress-embed-escape-pitfalls.md` への追記対象。
**次の自分へ**: C-5 テスト拡張（合成 DashboardComments/crit fixtures・details パススルー・Layout.vue 存在）→ Stage 1 → Stage 2 レビュー3体。PlanTemplate.md に折りたたみ構文の書き方を一言追記するか検討（doc-review に見てもらう）。
**気になっていること**: DashboardComments.json はコミット対象（共有チャンネル）— .gitignore に入れない。エージェントが resolved 化した後のアーカイブ方針（肥大化対策）は未決 — 当面は resolved も残す（履歴）。レビューで意見が出たら Plan に追記。

##### 2026-07-16 — Stage 2 レビュー2/3体完了（code-review 待ち）
**やったこと**: contribution-agent と doc-review の結果を受領。contribution: [Critical] parse_crit_reviews の型ガード不足（files 値が list だと AttributeError で生成全体クラッシュ — DS 実測で再現済み）/[High] その回帰テスト欠如/[Medium] 1.7 の存在ゲート文言と addf-migrate 補完経路。doc-review: [Medium] DashboardComments.json にダミーデータ dc_existing1 残存（並走レビューエージェントの実測書き込みと推定）/[Low] 命名3種の紛らわしさ/[Info] テスト番号非単調・README 未記載（Plan 0050 型の切り出し推奨）。
**今の見立て**: Critical は isinstance ガード追加＋合成フィクスチャで確実に直せる。1.7 文言は「が存在し、〜あれば」に揃える。addf-migrate 補完は主題内（フェーズC の配線の一部）として対応。README 記載は主題外 → 別 Plan 切り出し。
**次の自分へ**: code-review 完了後に3体集約 → 一括反映 → Stage 1 再実行 → knowhow（vitepress-embed-escape-pitfalls に code_inline v-pre 追記・命名3種の判別も）→ DashboardComments.json を `{"comments": []}` にリセットしてからコミット。
**気になっていること**: コンテキスト残量が観測 181k — compaction を跨ぐ可能性。この日記が引き継ぎ線。反映作業は generate-dashboard.py:206 付近（parse_crit_reviews）とテスト・CLAUDE.md 1.7・addf-migrate.md が対象。

##### 2026-07-16 — フェーズC 完走（レビュー反映・テスト17件・完了処理）
**やったこと**: 3体レビューの指摘を全反映した。Critical 2（crit 型ガード・details 閉じ忘れフォールバック）・High 1（API Promise キュー直列化）・Medium 4（occurrence・ホバー残留・1.7 存在ゲート・migrate 補完）・Low/Info（scrollX・td/th・except 拡大・テスト番号振り直し・ダミーデータリセット・port 環境変数化）。テストは 17件全通過（API スモーク Test 12 は vitepress dev 実起動 + curl）。README 記載は Plan 0065 に切り出し。並行セッション起票の Plan 0059〜0064 の TODO 未登録を発見し登録を代行（Feedback 記録済み）。knowhow は vitepress-embed-escape-pitfalls.md にフェーズC 節を追記。
**今の見立て**: フェーズC は実装完了。Plan 0058 の残りはオーナーのブラウザ動線確認のみ（owner_feedback: 待ち に設定・ダッシュボードのキューに載る）。
**次の自分へ**: オーナー確認で UI の使用感フィードバックが来たら反映する。resolved コメントの肥大化対策（アーカイブ方針）は未決のまま — 実運用で肥大化が観測されたら Plan 化する。
**気になっていること**: config port が CLI --port より優先される仕様は他の VitePress 利用箇所（公開 docs サイト）には影響しないか未確認（あちらは port 指定なしのため実害はないはず）。

> 新しいタスク開始時は以下の構造で記録する:
> `### 現在のタスク: <Plan 名>` → `#### サブタスクチェックリスト` → `#### 日記`（運用ルール 3.5 の4項目書式）
