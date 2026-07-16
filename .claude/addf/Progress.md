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

### 現在のタスク: v0.7.0 リリースに向けた DS フィードバック対応（Plan 0059・0060）＋リリース前作業

採番 v0.7.0 はオーナー承認済み（2026-07-17）。スコープ: DS 実害系（0059・0060）＋ 0065（README）＋ドリフト検査＋ CHANGELOG → /addf-release。0061〜0063 は次リリースへ。

#### サブタスクチェックリスト

- [x] D-1: Plan 0059 実装（addf-implementer worktree 委譲 — make_sandbox 条件付き cp / todo_table_rows 両書式受理 / lock.json 下流シグナル SKIP / CI 模擬は切り出し可）
- [x] D-2: Plan 0060 実装（addf-implementer worktree 委譲 — migrate-paths / lint-residual-paths の lookbehind 境界・Issue #33）
- [x] D-3: 両 worktree の検収と main への統合（cherry-pick・worktree 掃除済み）
- [x] D-4: Stage 1 — run-all.sh・lint 一式（統合後・レビュー反映後の2回通過）
- [x] D-5: Stage 2 — 指摘反映済み（DS 丸ごと実行 FAIL 修正・M-2 排他化・L-1 アサーション・既知の限界 docstring。根治は Plan 0068 切り出し）
- [x] D-6: Plan 0065 — README/README.en にダッシュボード記載（完了・コミット済み 2026-07-17）
- [x] D-7: リリース前ドリフト検査（lint 全通過・CHANGELOG Unreleased 最終化済み）
- [ ] D-8: /addf-release で v0.7.0（Issue #30・#31・#33 返信文はオーナー確認待ち）

#### 日記

##### 2026-07-17 — Plan 0059 着手（ゴール: リリースに向けた DS フィードバック対応）
**やったこと**: /goal でダウンストリームフィードバック対応の指示を受け、優先度・若番から Plan 0059 を選定。実装は addf-implementer に worktree 委譲する判断（メインのコンテキストが 400k 超で compaction 間近のため、復帰容易性を優先）。
**今の見立て**: Plan 0059 は Issue #30・#31 に下流実測・実装済みの対処が揃っており確信度9割。項目4（CI downstream 模擬）だけ規模次第で切り出し。
**次の自分へ**: compaction 後に再開する場合 — addf-implementer の worktree ブランチ（plan-0059 系の名前）の有無を `git branch -a` で確認し、完了していれば D-2 の検収から。未完なら TaskOutput で状況確認。
**気になっていること**: このセッションで Plan 0058 関連の UI 修正が多数 main に入っている。worktree は分岐時点の main を基にするので競合は無いはずだが、統合時に generate-dashboard.py 等に触っていないか diff を確認すること。

##### 2026-07-17 — Plan 0060 実装完了（worktree）・0065 完了・0059 実行中
**やったこと**: Plan 0065（README ダッシュボード記載・日英）を完了しコミット。impl-0060 が完了報告 — worktree ブランチ worktree-agent-a35a02b1f25b8feac のコミット 018b124 に migrate-paths.py / lint-residual-paths.py の lookbehind 境界（1文字境界維持＋`(?<![A-Za-z0-9]/)` ＋自リポジトリ絶対パスの正 lookbehind 例外）と Test 13.5（12件）が入っている。run-all 全通過・Issue #33 提案準拠。ベースは古い（fc52037）が変更対象ファイルは main と同一と報告あり → cherry-pick で統合可。
**今の見立て**: 0060 は cherry-pick → main で run-all 再実行 → TODO/Plan 反映で閉じられる。0059（impl-0059）はまだ実行中。
**次の自分へ**: (1) `git cherry-pick 018b124` → run-all → lint → TODO の 0060 行を完了に・Plan 0060 ヘッダ完了化 → worktree 掃除（`git worktree remove .claude/worktrees/agent-a35a02b1f25b8feac` とブランチ削除）。(2) 0059 の完了通知が来たら同様に検収・統合。(3) その後 Stage 2（code-review + contribution-agent・DS 実測依頼）→ CHANGELOG に 0059/0060/0065 追記 → /addf-release v0.7.0（オーナー承認済み採番）。Issue #30/#31/#33 返信文はオーナー確認待ち。
**気になっていること**: コンテキスト 477k で compaction 濃厚。この日記が引き継ぎ線。impl-0060 の knowhow 候補3件（lookbehind alternation の幅独立固定・誤検知除去へのドリフト注入 TDD 適用・cwd 依存動的パターンは cwd 固定契約とセット）は完了処理で knowhow 化する。

##### 2026-07-17 — Stage 2 レビュー2体完了・指摘集約と対応方針
**やったこと**: 0059/0060 を main へ統合し Stage 1 通過。レビュー2体の指摘を集約した。
**今の見立て・対応方針**: (1) [High] 真の DS リポジトリでの test-template-sync.sh 丸ごと実行で Test 1（pair1 は .addf.md 不在時 SKIP を出さず silent に実比較へ切替わるが、テストは SKIP を期待）・Test 19（sed 注入が DS の Progress.md では no-op）が FAIL — フェーズ内修正。(2) [High 昇格・2体同根] compile_pattern の self_prefix 設計: blob/raw URL 自己参照の検出漏れ回帰＋basename 衝突誤検知 — 根治はスキーム検出設計でオーナー判断も絡むため docstring 既知の限界追記＋Plan 0068 切り出し。(3) M-2 TODO 正規表現の左優先はフェーズ内で排他化。(4) M-3 compile_pattern 同期契約の lint ペア9 新設は addf-lint 表更新義務も伴うため 0068 に同梱。(5) L-1 Test 26 post-copy ドリフトアサーション追加。
**次の自分へ**: 修正順: Test 1 → Test 19 → M-2 → L-1 → docstring → Plan 0068 起票 → Stage 1 再実行 → knowhow → CHANGELOG 微修正不要確認 → /addf-release v0.7.0（オーナー承認済み採番）。Issue #30/#31/#33 返信文はリリース報告と一緒にオーナー確認へ。
**気になっていること**: compaction 後はこのエントリーが最初の道標。修正対象: test-template-sync.sh:145-161（Test 1）・450-462（Test 19）・lint-template-sync.py:501-505（TODO_PLAN_PATH_RE）・migrate-paths.py:154-176 と lint-residual-paths.py:83-101（docstring）。

> 新しいタスク開始時は以下の構造で記録する:
> `### 現在のタスク: <Plan 名>` → `#### サブタスクチェックリスト` → `#### 日記`（運用ルール 3.5 の4項目書式）
