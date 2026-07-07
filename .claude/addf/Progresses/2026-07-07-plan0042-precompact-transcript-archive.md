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

### 現在のタスク: Plan 0042 PreCompact トランスクリプトアーカイブ

実施承認済み（2026-07-06）・オプトイン・デフォルト無効。フック1本+設定+テスト+knowhow のスコープ。

要オーナー確認2項目は Plan 内の指針で自己解決:
- アーカイブ先: `~/.claude/addf-transcript-archive/<プロジェクトスラグ>/`（Plan 提案どおり）
- 世代数上限: **10 世代**（「保守的に少なめ」の方針。1セッション数 MB × 10 = 数十 MB 目安）
- ダウンストリーム配布時: **デフォルト無効**（機密含みうる方針）

#### サブタスクチェックリスト

Plan の項目対応: 項目1（フック本体 + settings.json 配線）／項目2（Behavior.toml）／項目3（knowhow）／項目4（lint・配布整備の**確認**）

- [x] 項目1a: `.claude/hooks/pre-compact-archive.sh` 新設
- [x] 項目1b: `.claude/settings.json` に PreCompact 配線追加
- [x] 項目2: `.claude/addf/Behavior.toml` に `[transcript-archive]` セクション追加
- [x] フックテスト `.claude/addf/tests/hooks/test-pre-compact-archive.sh` 新設（25テスト全通過）
- [x] 項目3: `.claude/addf/knowhow/ADDF/transcript-archive-restore.md` 新設・context-and-transcript.md と相互リンク・INDEX 登録
- [x] 品質ゲート Stage 1: run-all.sh + lint スクリプト全本（項目4 の確認を兼ねる — 新フックが5フック目として lint-hooks-wiring で検出・addf-init コピーリストは `.claude/hooks/*.sh` 一括対象のため追記不要）
- [ ] 品質ゲート Stage 2: code-review + doc-review 並列（doc-review 完了・code-review 継続中）
- [ ] 完了処理: Plan/TODO/knowhow/Feedback/Progresses/コミット

#### 日記

##### 2026-07-07 — タスク開始
**やったこと**: Plan 0042 選定（若番・オプトイン・実装承認済み・スコープ明快）。knowhow-agent で claude-code-hooks / context-and-transcript / sync-lint-design / optional-skill-optin / existing-project-install-pattern / permission-settings-pattern の6本を関連ノウハウとして取得。settings.json・Behavior.toml・既存フック3本の構造確認。addf-init コピーリストは `.claude/hooks/*.sh` 一括対象のため個別追記不要と確認。
**今の見立て**: 実装は素直（既存フック post-compact-recovery / skill-usage-log のパターンを踏襲）。要オーナー確認2項目は Plan の指針（保守的・機密デフォルト無効）で自己解決可能。確信度 8割超。
**次の自分へ**: 項目1（フック本体）から着手。設計原則 — CLAUDE_PROJECT_DIR フォールバック / `set -e` 非使用 / 失敗時 `exit 0` / stdin JSON パースは jq 使用（skill-usage-log.sh のパターン）。世代掃除は ls -t | tail で古い順削除。
**気になっていること**: プロジェクトスラグの算出方法（cwd 由来 or session-id ハッシュ）。既存の Claude Code 慣習に合わせるなら cwd を sanitize したもの（`~/.claude/projects/` と同じ流儀）。fail-safe に cwd base で行く。

##### 2026-07-07 — 実装完了・Stage 1 通過・doc-review 反映
**やったこと**: 項目1（フック本体）〜項目3（knowhow）を実装。フックは TOML パースを bash+awk の簡易実装で（Python 依存を避けるため。設定は3項目のみで書式リスクは小さい）。jq 不在時は sed フォールバック付き。テスト12ケース（内 assert が 25 発）全通過。Stage 1（run-all.sh + lint 全本）通過。doc-review が Warning 1・Suggestion 2 で完了 — チェックボックス実態遅延と項目ラベルの Plan 対応を指摘され、両方反映（Plan 対応を「項目1a/1b」形式に明示）。プロンプトインジェクションが tool 結果に混入していたが doc-review が検知して無視・報告してくれた。
**今の見立て**: 実装スコープはほぼ完了。code-review 待ちだが、フックの堅牢性・TOML パース脆弱性・命名衝突・パストラバーサル観点で軽度指摘が来る可能性はある（テストが網羅していない境界ケース）。Plan 0042 の完了条件の3つ目「復元手順を実セッションで1回確認」は human-judgment マーカー付きなので、実施はオーナー任意で完了処理は進められる。
**次の自分へ**: code-review の指摘が届いたら Critical/High は即修正。完了処理では Plan 0042 の「実装状況」ヘッダを完了に、「要オーナー確認」に自己解決の記録を残す（doc-review の申し送り）。TODO.addf.md を「完了」に更新、Progresses/ にアーカイブ、Feedback.md に「TOML の bash 簡易パース」パターンを追記。
**気になっていること**: コンテキスト実測 266k で opus 目安 200k を超過。auto-compact が発動する可能性を意識しつつ、完了処理まで走り切る（止まらない教義）。code-review が長引いたら、そのメッセージ間で日記を書き足して次の代に引き継げるようにしておく。
