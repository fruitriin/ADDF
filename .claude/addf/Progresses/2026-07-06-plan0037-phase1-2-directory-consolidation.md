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
7. レビュー指摘への対応:
   - **Critical/High**: 必ずこのフェーズ内で修正する（先送り禁止）
   - **Medium**: 原則修正。先送りする場合は独立計画を起こす
   - **Low/Info**: Plan に記録し、必要に応じて独立計画で対応
   - **バグ分離**: 発見されたバグが現在のプランと関心事が異なる場合は、修正せずに新しいプラン（`.claude/addf/plans/`）を書き起こし、`TODO.md` に追加するのみで現在のプランを完了させる
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

### 現在のタスク: Plan 0037 — ADDF ディレクトリ大集約（フェーズ1: paths.toml とツール整備）

オーナー指示: `/addf-dev Plan37 大改造の始まりだ`（2026-07-06・オーナー同席セッション。Q2 回答「別のクリアなセッションで実施」の当該セッション）

#### サブタスクチェックリスト

- [x] 事前清算: worktree 残骸3つを処理（Plan 0046 WIP は `plan-0046-wip` ブランチに保全・他2つは clean 残骸で削除）
- [x] reconcile check 異常なし（投機在庫ゼロ・pending 0・active 0）
- [x] paths.toml（旧→新パスマップ）設計・作成
- [x] 移動スクリプト（マップ駆動 git mv・check/apply 分離）
- [x] 参照書き換えスクリプト（境界チェック付き置換）
- [x] 残存参照 lint 新設（ドリフト注入 TDD 込み）
- [x] 合成プロジェクトでの移行シミュレーションテスト（存在≠所有判定・Pages コンテンツ不可侵）
- [x] run-all.sh 組込み・Stage 1（worktree 内で run-all 全パス。run-all は glob 収集のため編集不要）
- [x] Stage 2 レビュー（ペルソナ3体並列 + contribution 配布安全性 = 4体。指摘: Critical 4件・Warning 7件・Suggestion 群）
- [x] レビュー指摘の修正（Critical 4・Warning 6・Suggestion 対応。テスト 29→51 アサーション）
- [x] main へマージ（--no-ff・15769a2）→ main で run-all 全パス
- [x] knowhow 記録（map-driven-migration-tool.md / persona-review-oneshot.md 新規・INDEX 登録）
- [x] Plan 0037 ヘッダ・完了条件・レビュー残課題を反映、TODO.addf.md 更新
- [x] フェーズ1完了コミット（25ce899）
- [x] **フェーズ2: 本体移行の一発完走**（オーナー承認 2026-07-06）: check → apply（git mv 20件・21c0b61）→ 新位置 rewrite（1709箇所/205ファイル・fb57924）→ 新構造適応修正（5205b4c）→ lint-residual-paths OK → run-all 全19スイートパス → docs/ 空確認・削除
- [x] フェーズ2差分の単体レビュー → 指摘対応（Warning: guides 相対リンク3件修正・射程外第4類型として knowhow 追記。Suggestion: settings.local.json 許可パス修正・残り2件は Plan に記録）
- [x] 完了処理（Progress アーカイブ・コミット）

フェーズ3（addf-migrate 統合・addf-init 新構造化・メジャーリリース）は別セッションで実施する。

#### 日記

##### 2026-07-06 — フェーズ2 一発完走。rewrite の射程外3類型を実測
**やったこと**: オーナー承認を得てフェーズ2実施。backup ref → git mv 20件 → 新位置 rewrite 1709箇所 → 直後の run-all で18/19スイート失敗 → 原因は全て「rewrite の射程外」（①相対階層参照 `SCRIPT_DIR/../../..` のずれ ②`os.path.join` / Swift 文字列連結の分割断片 ③テストサンドボックスの mkdir/cp 先）。3類型を系統的に修正し（Swift は再ビルド＋checksums 更新）、run-all 全パス・lint OK・docs/ 削除で明け渡し完了。knowhow（map-driven-migration-tool.md）に3類型を追記済み。
**今の見立て**: 「巻き戻し優先」教義と照らし合わせた上で続行を選んだ — 失敗は移行操作自体ではなく新構造への適応課題で、巻き戻しても道具側では直せない種類だった（相対参照は原理的にマップ外）。run-all という完了ゲートが網を張っていたおかげで全数検出できた。
**次の自分へ**: フェーズ2差分の単体レビューが返ってきたら指摘対応 → Progress をアーカイブしてこのタスクを閉じる。フェーズ3（addf-migrate のバージョン差分手順・addf-init 新構造化・CHANGELOG 移行ガイド・メジャーリリース）は新しいセッションで。paths.toml は移行後も旧→新マップを保持しているためフェーズ3にそのまま使える。
**気になっていること**: ダウンストリーム移行時も同じ3類型（特にプロジェクト独自スクリプトの相対参照・分割断片）が起きうる。フェーズ3の migrate 手順に「移行後にプロジェクト自身のテストを回す」ステップと分割断片のプリフライト grep を含めること。backup ref `refs/backup/pre-0037-migration` は残置中 — フェーズ3完了後の削除を検討。

##### 2026-07-06 — コンパクション明け・事前清算完了、フェーズ1着手
**やったこと**: コンパクション後復帰。worktree 残骸3つを清算（agent-a22ce… に Plan 0046 の未コミット実装が dirty で残っていたため `plan-0046-wip` ブランチにコミット保全。agent-abd0…（Plan 0031 squash 済み）と mystifying-jepsen（PR #16 マージ済み）は clean のため worktree 削除・ブランチ残置）。reconcile check 異常なし。knowhow 抽出済み（sync-lint-design / checklist-backing-lint / existing-project-install-pattern が中核）。
**今の見立て**: Plan 0037 着手条件（在庫ゼロ・清算済み）成立。プレフィックス簡素化（addf-Behavior.toml → Behavior.toml 等）は Plan の構造図がリネーム後の名前を明記しているため移動と同時に実施する（参照書き換え1回で済む。確信度8割）。
**次の自分へ**: フェーズ1の道具（paths.toml・移動/書き換えスクリプト・残存参照 lint・合成プロジェクトテスト）を worktree 隔離エージェントに委譲する。完了したらレビュー→main マージ→Stage 1/2。フェーズ2はオーナー確認後。
**気になっていること**: ADDF-Release.addf.md → Release.md のリネームは .addf.md サフィックス判定ロジック（addf-init コピー除外・lint）に影響する可能性。委譲エージェントに調査を指示する。Plan 0046 の実装（DelegationRules.md）は main 未マージのため、委譲プロンプトの禁止事項は直書きする。

##### 2026-07-06 — フェーズ1 実装完了・4体レビュー完了・修正依頼中
**やったこと**: worktree（ブランチ `worktree-agent-a3809c64131a9d17f`）でフェーズ1の道具4点が完成（paths.toml / migrate-paths.py / lint-residual-paths.py / test-migrate-paths.sh 29アサーション・run-all 全パス）。実装エージェントの判断: Release.addf.md は `.addf.md` 配布除外規則が現役のためリネームせず維持・`.claude/assets` は不動・Worktrees.md は dynamic 分類。本体 check 実測: 移動19件・旧パス参照1695箇所・ブロッカーなし。マイルストーン級としてペルソナ3体（skeptic/attacker/newcomer）+ contribution の4体並列レビューを実施。
**今の見立て**: レビューで Critical 4件（①symlink 越しリポジトリ外書き込み ②apply 前 rewrite の無警告破壊 ③dynamic/shutil.move 分岐未テスト ④apply 後の新パス未案内=2ペルソナ独立指摘でコンセンサス昇格）、Warning 7件（backup ref 上書き・走査対象不一致・空ディレクトリ自己ロック・実行位置未検証・部分適用識別不能・check コンテキスト表示なし・衝突回復手順なし）。attacker は全て実再現済み。one-shot 本番前に見つかるべきものが見つかった — ペルソナ並列の価値が出た。
**次の自分へ**: 実装エージェント（agentId a3809c64131a9d17f）に SendMessage で修正依頼済み。完了通知が来たら: 修正確認 → worktree で run-all → main へマージ（squash せず履歴ごと merge --no-ff か、意味単位が保たれていれば ff でも可）→ main で run-all 再実行 → 完了処理（knowhow 記録・Feedback・Progress アーカイブ・コミット）。フェーズ2はオーナーに開始確認してから（一発通し切り・同席実施）。
**気になっていること**: レビュー見送り2件（.claude/addf/plans 内非所有ファイル巻き込みの仮定・exclusions 二重管理）は Plan 0037 の「レビュー残課題」として記録すること。skeptic の「移行済み判定の1点依存」はフェーズ3（migrate 統合）でも再考の余地。

##### 2026-07-06 — フェーズ1 完了・マージ済み。フェーズ2 はオーナー確認待ち
**やったこと**: レビュー指摘の修正完了（Critical 4・Warning 6・Suggestion。テスト 29→51 アサーション・攻撃再現をテストに固定）。main へ --no-ff マージ（15769a2）し main で run-all 全パス。worktree/ブランチ削除済み。knowhow 2記事新規（map-driven-migration-tool / persona-review-oneshot）＋INDEX 登録。Plan 0037 に実装メモ・レビュー残課題を記録、TODO.addf.md 更新。
**今の見立て**: フェーズ1 完了条件は全て満たした（道具・テスト・lint SKIP 動作・ドリフト注入実証）。フェーズ2（本体移行 one-shot）は道具が検証済みで「実行するだけ」の状態。本体 check 実測: 移動19件・参照1695箇所・ブロッカーなし。
**次の自分へ**: フェーズ2 開始はオーナーの明示確認を取ってから（Plan の「オーナー同席・単一セッション完走」要件）。実行手順: (1) `python3 .claude/addf/tools/migrate-paths.py check` で最終確認 → (2) `apply` → git mv コミット → (3) **新位置** `.claude/addf/tools/migrate-paths.py rewrite` → 参照書き換えコミット → (4) `.claude/addf/tools/lint-residual-paths.py` ERROR ゼロ → (5) `bash .claude/addf/tests/run-all.sh` 全パス。失敗時は `git reset --hard refs/backup/pre-0037-migration` で巻き戻し、道具を直してから再実行（直しながら進むの禁止）。
**気になっていること**: フェーズ2 実施中は投機停止（Plan 明記）。rewrite は Progress.md 内の旧パス文字列も書き換えるため、書き換え後の Progress.md の記述が新パスになるのは正常。ベース名のみの参照（パスなし言及）は rewrite 対象外なので目視確認が要る。
