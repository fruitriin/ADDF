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

### 現在のタスク: Plan 0022 — addf-init コピーリストの鮮度回復と機械化

モード: normal × relaxed × balanced（デフォルト）

#### サブタスクチェックリスト

- [x] 1. `addf-init.md` 修正: カテゴリ1へ `Questions.example.md`/`Dashboard.example.md` 追加、Progress.md 生成元を `ProgressTemplate.md` と明記、.gitignore マージブロック例は「クローン元を正とする」方式に変更（列挙の陳腐化を構造的に排除）
- [x] 2. `lint-template-sync.py` にペア5（CLAUDE.md 参照 ⇔ addf-init コピーリストのカバレッジ検査）を追加
- [x] 3. `test-template-sync.sh` にペア5のテストを追加（テスト7: カバー漏れ検出 / テスト8: 欠如時 SKIP。21 PASS）
- [x] 4. E2E 自然言語シナリオ `.claude/addf/tests/skills/test-addf-init-external.md` を作成
- [x] 5. Plan 0022 の変更対象ファイル表のパス誤り訂正（lint の実体は `.claude/addf/addfTools/`）
- [x] 6. Stage 1: `bash .claude/addf/tests/run-all.sh` — 全自動テスト通過
- [x] 7. Stage 2: addf-code-review-agent 完了（Critical/High なし・W2件・S5件・I2件）。addf-contribution-agent（配布安全性）完了（Critical/High なし・Medium 2件・Low 2件）
- [x] 8. レビュー指摘対応: W1（コードブロック内の誤抽出を除外）・W2（マーカーブロック読み取りを break→フラグ折り）・S2（テスト8の意図コメント）・S5（クローン元 `<tmp>/addf-source/.gitignore` の明示）・I1（検査対象を CLAUDE.md に限定する意図を docstring 化）対応。S1/S3/S4/I2 は Plan に記録予定 → Stage 1 再実行 21 PASS
- [x] 9. 完了処理: knowhow 記録（sync-lint-design.md へペア5設計・正規表現の罠・単一ソース化を追記 / plan-status-drift-check.md 新規 / INDEX 更新）・Plan 0022 完了反映・Feedback 更新（同期ペア5追記）・アーカイブ・コミット

#### 日記

##### 2026-06-10 — タスク開始: 調査で見えた追加ドリフト
**やったこと**: Plan 0022 を選択（唯一の未着手）。knowhow エージェントで関連知見4本を取得し、lint-template-sync.py・test-template-sync.sh・既存スキルシナリオ形式を読了
**今の見立て**: Plan 記載の4項目に加え、addf-init.md 内の .gitignore マージブロック例が本体 .gitignore とドリフトしている（`.claude/addf/Dashboard.md`・`.claude/skills/addf-gui-test.md` 欠落）のを発見。同根の鮮度問題なので本タスクで一緒に直す。ペア5の検査は「CLAUDE.md の `.claude/` 配下参照を抽出 → addf-init.md 本文（グロブ解釈込み）or .gitignore マーカーブロックでカバーされるか」方式。lint を先に書けば現状のドリフトが WARNING で再現でき、TDD で進められる
**次の自分へ**: ペア5実装時、ダウンストリームでは CLAUDE.md と addf-init.md が両方存在すれば検査可能（片方欠如で SKIP）。exit code 3値と git ヒントの既存規約を守ること
**気になっていること**: Plan の変更対象表に `.claude/addf/tests/lint-template-sync.py` と書いたが実体は `.claude/addf/addfTools/`。Plan 側を訂正する（サブタスク5）

##### 2026-06-10 — 実装完了、Stage 2 へ
**やったこと**: サブタスク1〜6完了。TDD で進め、ペア5 lint が現状ドリフト（example 2ファイル）を正しく WARNING 検出 → addf-init.md 修正で GREEN を確認。.gitignore ブロック例はハードコード列挙をやめ「クローン元の同ブロックをコピーする」指示に変更（リスト陳腐化の構造的排除 — Plan 案 b の発想をここに適用）
**今の見立て**: ペア5の正規表現は「バッククオート内の `.claude/` 始まりパス」抽出。Phase 1 の状態判定にある `.claude/` ルート単体表記が全カバー扱いになる罠を踏んだ（`[^\s`]*` → `[^\s`]+` で解決）。確信度高
**次の自分へ**: Stage 2（code review + contribution agent 並列）→ 指摘対応 → 完了処理（knowhow 記録は「ペア5の設計」「`.claude/` ルート単体の罠」を sync-lint-design.md への追記が適切か検討）
**気になっていること**: ペア5は CLAUDE.md のみ検査対象。CLAUDE.repo.example.md や Progress テンプレートが参照するファイル（ExperienceTemplate.md 等）は templates/ 丸ごとコピーでカバーされるため今回は対象外としたが、将来参照元が増えたら検査対象ファイルの追加を検討

##### 2026-06-10 — レビュー指摘対応、PR 作成へ
**やったこと**: code-review の W1/W2/S2/S5/I1 を修正し Stage 1 再実行（21 PASS）。オーナー指示で PR 作成に着手
**今の見立て**: 残る Suggestion（S1: gitignore 末尾スラッシュなしディレクトリ指定の検出漏れ可能性 / S3: テスト6がテスト1通過前提 / S4: E2E のスキームチェック検証の注意 / I2: .gitignore なし環境のテスト未整備）は Low/Info 相当。Plan 0022 の完了記録に注記する
**次の自分へ**: addf-contribution-agent（配布安全性）がまだ実行中。完了通知が来たら指摘を確認し、必要なら本ブランチに追加コミット。その後 knowhow 記録（sync-lint-design.md への追記: ペア5設計・`.claude/` ルート単体の罠・コードブロック除外）→ Plan 反映 → Feedback 更新（同期ペア5の追記）→ アーカイブ
**気になっていること**: PR マージは配布安全性検査の結果確認後が望ましい

##### 2026-06-10 — 配布安全性検査の指摘対応とタスク完了
**やったこと**: セッション境界で配布安全性エージェントの追跡が失われたため、コミット済み diff を対象に再起動して回収。指摘（Medium 2・Low 2、Critical/High なし）に対応: .gitignore 欠如時の挙動をテスト9で仕様固定化、テスト1の本体前提を明文化、ペア5 WARNING 文言にオーナー向け解釈補助を追加。23 PASS。knowhow 記録・Plan/TODO/Feedback 反映を完了
**今の見立て**: Plan 0022 は完了。PR #11 にレビュー対応コミットを積んだ状態。マージはオーナー判断待ち
**次の自分へ**: PR #11 がマージされたら main で `bash .claude/addf/tests/run-all.sh` を一度回して環境差がないことを確認するとよい。未着手 Plan はゼロ — 次タスクはオーナーリクエスト「プロジェクトの品質を向上させる計画を追加する」に従い新計画の起案から
**気になっていること**: バックグラウンドエージェントはセッションをまたぐと TaskOutput で回収できない。長時間レビューは同セッション内で回収するか、コミット済み diff を対象にすること（addf-dev.exp.md に記録）

> 新しいタスク開始時は以下の構造で記録する:
> `### 現在のタスク: <Plan 名>` → `#### サブタスクチェックリスト` → `#### 日記`（運用ルール 3.5 の4項目書式）
