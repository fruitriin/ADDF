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

### 現在のタスク: Plan 0052（マイグレーション実行時耐障害性の強化 — Issue #26 実測回収）

#### サブタスクチェックリスト

- [x] 項目1a: `test-tools.sh` の window-info 呼び出しに `timeout` ガードを追加（capture-window は本テストで未実行のため対象外）
- [x] 項目1b: `addf-migrate.md` 6.7（射程外4類型・類型2）に GUI バイナリの再ビルド+timeout付き動作確認注記を追加
- [x] 項目1c: `map-driven-migration-tool.md` 類型2に9時間ハングの実測（Issue #26）を追記
- [x] 項目2: `addf-migrate.md` 6.3 の混在確認対象ディレクトリに `guides` を追加
- [x] 項目3a: `addf-migrate.md` に `.gitignore` 旧位置パターン見直しの `<!-- human-judgment -->` 注記を追加
- [x] 項目3b: `lint-residual-paths.py` に `.gitignore` 内旧位置パターン残存検知（WARNING）を追加
- [x] 項目4: `test-binary-checksums.sh` Test 15 の `CLAUDE.repo.md` 不在時 SKIP フォールバック
- [x] テスト: 項目3bのドリフト注入TDD（.gitignoreに旧位置パターンを仕込みWARNING検出を確認）
- [x] テスト: 項目4のCLAUDE.repo.md不在サンドボックスでSKIP確認
- [x] テスト: `bash .claude/addf/tests/run-all.sh` 通過確認
- [x] `/addf-lint` 通過確認
- [x] コードレビュー（addf-code-review-agent）実施 — 完了。Critical1件（Progress.mdのresidual-path markerの漏れ）・Warning2件（gitignore_like_matchのアンカー情報喪失／リテラルパターンでERROR・WARNING重複）・Low1件（.gitignore読み込みのsymlinkガード欠如）
- [x] ドキュメントレビュー（addf-doc-review-agent）実施（*.md変更あり）— 完了。Warning3件（addf-migrate.md 6.3と Phase5 step14の記述不一致／Progress.mdのcapture-window表現が実装と不一致／Progress.mdのguides混在確認行のmarker漏れ） <!-- residual-path: allow -->・Suggestion1件（knowhowのlast_verified未更新は完了処理で対応予定）
- [x] コントリビューション検出（addf-contribution-agent）実施 — 完了。Medium2件（gitignore_like_matchの末尾スラッシュ盲点／test-binary-checksums.sh Test15のCLAUDE.repo.example.md不在ケース未考慮）・Low1件（run_with_timeoutのPID再利用理論上レース。実害小のため対応見送り、コメントで留意点を明記のみ）
- [x] レビュー指摘対応 — 全指摘を反映済み: (1) Progress.md:120にresidual-path markerを追加（3エージェント共通でCritical/Warning検出）、(2) addf-migrate.md Phase5 step14にtemplates/optional/guidesを追加して6.3の記述と整合、(3) capture-window記述をPlan・Progress.mdから削除し実装（window-info単体）に合わせた、(4) gitignore_like_matchにアンカー（先頭/のみ）判定を追加、(5) リテラルパターン（ワイルドカードなし）はERROR側に任せWARNING側から除外して重複解消、(6) .gitignore読み込みをread_text()に統一しsymlinkガードを継承、(7) test-binary-checksums.sh Test15のガード条件にCLAUDE.repo.example.md不在も追加、(8) test-migrate-paths.shに末尾スラッシュパターンのテストケースを追加。run_with_timeoutのPID再理論上レースはLow/Info・実害僅少のため対応見送り。再実行でrun-all.sh・addf-lint全通過確認済み
- [x] ノウハウ記録（コーディング知見・品質ゲート知見・タスク総括） — `map-driven-migration-tool.md`（gitignore_like_match の設計知見）・`persona-review-oneshot.md`（異種エージェント間コンセンサス）・`addf-dev.exp.md`（Plan文言と実装事実の乖離）に反映
- [x] Feedback.md 更新 — residual-path系lint強化タスクでの自己言及ドリフトの教訓を追加
- [ ] Progress アーカイブ・コミット

#### 日記

##### 2026-07-11 — 実装4項目完了、run-all.sh 全通過
**やったこと**: Plan 0052 の項目1〜4を全て実装した。項目1: test-tools.sh に timeout ガード
（GNU coreutils 無い環境向けの手動 kill フォールバック付き）、addf-migrate.md 6.7・
map-driven-migration-tool.md へ9時間ハングの実測を追記。項目2: addf-migrate.md 6.3 の
混在確認対象に docs/guides を追加（existing-project-install-pattern.md の分類との整合を根拠に）。 <!-- residual-path: allow -->
項目3: apply 完了時の .gitignore 見直し注記（human-judgment）＋ lint-residual-paths.py に
.gitignore 内グロブパターンの非対称検知を追加。単純 fnmatch だと `*` が `/` を跨いでマッチし
本来検出すべき非対称を見逃すことに気づき、セグメント単位マッチ（gitignore_like_match）に
書き直した。test-migrate-paths.sh に Test 14.6（ドリフト注入 TDD）を追加、73件全通過。
項目4: test-binary-checksums.sh Test 15 を CLAUDE.repo.md 不在時 SKIP にフォールバック
（実際に CLAUDE.repo.md を退避して SKIP 経路も確認済み）。
**今の見立て**: run-all.sh は全自動テスト通過。lint-checklist.py が項目1の GUI バイナリ注記を
「裏付けなし確認ステップ」として一度 WARNING（exit 2）を出したため human-judgment マーカーを追加して解消した
（この lint 自体が今回の変更を的確に検出したのは良い実測）。/addf-lint 本体・コードレビュー・
doc-review・contribution-agent はこれから。
**次の自分へ**: `/addf-lint` を実行 → 通過を確認したらレビューエージェント群（addf-code-review-agent
単体・addf-doc-review-agent〔*.md変更あり〕・addf-contribution-agent）を起動する。指摘対応後、
ノウハウ記録（コーディング知見・品質ゲート知見・タスク総括）→ Feedback.md → Progress アーカイブ →
コミットの順で完了処理に入る。GitHub Issue #26 へのクローズ・コメントは外部発信のため、
コミット後にオーナーへ確認してから行う。
**気になっていること**: なし（設計判断は全て Plan 0052 本文と knowhow に根拠を残した）

##### 2026-07-11 — レビュー3体完了・全指摘反映・完了処理直前
**やったこと**: 3体のレビューエージェント（code-review・doc-review・contribution-agent）が完了し、
Critical1件・Warning5件・Medium2件・Low2件・Suggestion1件を検出した。全て反映: Progress.md の
guides混在確認箇所の marker漏れ（3体が独立検出。異種エージェント間コンセンサスとして knowhow に記録）、
addf-migrate.md Phase5 step14 の記述不一致、capture-window の文言不一致（Plan・Progress.md から
削除）、`gitignore_like_match` のアンカー情報喪失・リテラルパターン重複・末尾スラッシュ盲点（3件とも
コード修正）、`.gitignore` 読み込みの symlink ガード欠如（read_text() 再利用で解消）、
test-binary-checksums.sh Test15 の CLAUDE.repo.example.md 不在ケース。反映後、自分自身の追記
（Plan本文・Progress日記・knowhow）が新設 lint に3回連続で引っかかる自己言及ドリフトが発生し、
その都度 marker を追加して解消した（Feedback.md に教訓を記録済み）。run_with_timeout の PID
再利用理論上レースのみ Low/Info・実害僅少のため対応見送り（コメントで留意点は明記済み）。
**今の見立て**: run-all.sh・/addf-lint とも最終確認済みで全通過。ノウハウ記録・Feedback.md 更新も
完了。残るは Progress アーカイブとコミットのみ。
**次の自分へ**: `.claude/addf/Progresses/2026-07-11-plan-0052-migrate-runtime-hardening.md` に
リネーム移動し、`ProgressTemplate.addf.md` から新規 Progress.md を作成してからコミットする。
GitHub Issue #26 へのクローズ・コメントは外部発信のため、コミット後にオーナーへ確認してから行う。
**気になっていること**: なし
