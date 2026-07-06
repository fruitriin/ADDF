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

### 現在のタスク: Plan 0028 フェーズ2 — integration 統合と一括ゲート

出典: `.claude/addf/plans-add/0028-worktree-speculative-dev.md` フェーズ2（1: integration 生成＋スカッシュマージ、2: Stage 2 一括レビュー・衝突記録・再生成、3: Dashboard 連携、4: サンドボックステスト）

#### サブタスクチェックリスト

- [x] `speculate-integrate.py` 新設 — integration ブランチ生成＋feature の squash 統合を決定的スクリプト化（一時 worktree で統合し main の作業ツリーを触らない。衝突 feature はスキップして key=value で報告。検出=スクリプト/解釈=エージェント原則）
- [x] `test-speculate-integrate.sh` 新設 — 18ケース全パス（2 feature 統合 / 衝突スキップと残骸なし / 再生成 / missing / empty / base 不在 ERROR / 管理外ディレクトリ保護）
- [x] `addf-speculate.md` 手順拡張 — 手順6〜8を挿入（統合→Stage 2→Dashboard 書き分け）、旧6・7は9・10に繰り下げ。「現バージョンの範囲」更新
- [x] run-all.sh 全パス（169ケース）＋関連 lint（checklist / frontmatter / template-sync）OK
- [x] addf-code-review-agent レビュー（単体）と指摘対応（Critical 0 / High 1: commit 失敗を empty と誤分類→ diff --cached --quiet で先判定し commit_failed=ERROR に分離 / Medium 2: dirty worktree の無警告破棄→WARNING 追加・手順6に exit 1 の扱い明記 / Low 3: 古い integration ブランチ蓄積→Plan フェーズ3に記録・.claude 複製不要の明記・splitlines 修正。リグレッションテスト2件追加、計22ケース）
- [x] レビュー対応後の再テスト（run-all.sh 全パス・lint-checklist / template-sync OK）
- [x] Plan 0028 実装状況（フェーズ2記録）・TODO.addf.md 更新（lint ペア6 OK）
- [x] knowhow 記録（新規 `speculative-integration-design.md`＋INDEX 追加）
- [x] Progress アーカイブ → コミット

#### 日記

##### 2026-07-03 — フェーズ2 開始
**やったこと**: Plan 0028 と現行 addf-speculate.md（フェーズ1: 単発投機まで）を読了。knowhow サブエージェントを起動済み。
**今の見立て**: 完了条件の「衝突記録まで機械検証」から、統合はエージェント手順ではなくスクリプト化が筋（speculate-guard.py と同型）。tomllib 不要なので今回の Python ガード問題は無関係。確信度 8割。
**次の自分へ**: スクリプトは squash 衝突時の後始末（`git reset --hard` + `git clean -fd`）を一時 worktree 内に閉じ込めること。main の作業ツリーには絶対に触れない設計。
**気になっていること**: integration 用一時 worktree の置き場所（`.claude/worktrees/` は .git/info/exclude 頼みでローカル限定。配布先での gitignore 状況を確認する）。

##### 2026-07-03 — フェーズ2 完了
**やったこと**: speculate-integrate.py（統合の決定的スクリプト）＋テスト22ケース＋addf-speculate.md 手順6〜8。worktree 置き場所はフェーズ1と揃えてリポジトリ外（`../<repo>-integration`）にして gitignore 問題を回避。レビュー High（commit 失敗の empty 誤分類）は「エラーコードの解釈より状態の事前判定」で修正。
**今の見立て**: フェーズ2の完了条件（統合・衝突が silent にならない・Worktrees.md 記録まで機械検証）は充足。Dashboard 反映は human-judgment 項目なので実運用で確認される。
**次の自分へ**: 残りはフェーズ3（サイクル冒頭の再構築・clean サブコマンド・昇格手順書・guides 追記）。clean には「過去日付 integration/loop-* の削除」を含めること（Plan に記録済み）。addf-contribution-agent は本体そのもののため省略（前タスクと同じ判断）。
**気になっていること**: Stage 2 のペルソナ並列レビューは実運用でまだ一度も回っていない（[speculation].enable がデフォルト false）。フェーズ3完了後に enable=true で1サイクル通し試験をする価値がある。

> 新しいタスク開始時は以下の構造で記録する:
> `### 現在のタスク: <Plan 名>` → `#### サブタスクチェックリスト` → `#### 日記`（運用ルール 3.5 の4項目書式）
