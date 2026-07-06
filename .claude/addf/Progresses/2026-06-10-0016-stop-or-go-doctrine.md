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
4. 実装フェーズの最終サブタスク完了時、以下の知見を `/addf-knowhow` で記録する（既存 knowhow の更新も含む）:
   - **コーディング知見**: 実装中に発見した再利用可能なパターン、落とし穴、技術的判断とその根拠

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

### 現在のタスク: Plan 0016 — 迷ったときの作法（7割共有原則）

#### サブタスクチェックリスト

- [x] `CLAUDE.md` に「迷ったときの作法」セクション追加 + ブートシーケンス 1.5/1.6（Questions/Dashboard）追加
- [x] `AGENTS.md` ブートシーケンス同期（70% rule の言及も追加）
- [x] `.claude/addf/Questions.example.md` / `.claude/addf/Questions.md` 新規作成
- [x] `.claude/addf/Dashboard.example.md` 新規作成 + `.gitignore` に `.claude/addf/Dashboard.md` 追加
- [x] `.claude/commands/addf-mode.md` 新規スキル（モード状態は CLAUDE.local.md に保存）
- [x] `.claude/commands/addf-dev.md` にスキップフラグ・worktree 閾値の参照追加
- [x] `.claude/commands/addf-init.md` に Questions.md 生成・check 項目追加
- [x] ProgressTemplate/Progress.md に判断ルール参照追加・「unattended は将来導入予定」注記を5ファイルから除去
- [x] `bash .claude/addf/tests/run-all.sh` + @メンション整合確認（全解決）
- [x] addf-code-review-agent でセルフレビュー（Critical 1 / Warning 4 / Suggestion 4 → S-1 以外対応、S-1 は Plan に先送り記録）
- [x] Plan 0016 反映・TODO.addf.md 更新・knowhow 統合（実行保証 knowhow に CLAUDE.local.md 応用を追記）
- [ ] コミット

##### 2026-06-10 完了（ループ2回目）

**やったこと**: doctrine 実装一式 → レビュー → C-1（サブステップ実行順）と W 群を修正 → Plan ステータス反映時に `## Context` 見出しを誤って消し、レビュー前に自分で気づいて復元。
**今の見立て**: Plan 0016 完了。`/addf-mode` の状態保存先を CLAUDE.local.md にした判断は knowhow 化済み。
**次の自分へ**: 次は Plan 0017（代替わり日記）。この日記形式自体が 0017 のドッグフーディングなので、実装時は運用実績2タスク分を反映できる。0017 完了時、ProgressTemplate に日記セクションの規約を足し、この日記の書き味（4項目構成）をテンプレ化すること。
**気になっていること**: Edit ツールで見出し付きブロックを置換するとき、old_string の末尾に見出しを含めると消えやすい。次回は status 挿入を「見出しの直後に追記」する形にする。

#### 日記

##### 2026-06-10 着手（ループ2回目）

**やったこと**: knowhow 取得（@メンション運用・実行保証・分離パターンが該当）。CLAUDE.md/AGENTS.md/addf-dev/addf-init/gitignore を読了。
**今の見立て**: モード状態の保存先が Plan 未指定だった。CLAUDE.local.md（gitignore 済み・毎セッション自動読込）に「ADDF モード」セクションを書く設計にする — 新規ブートステップ不要で実行保証が高い。確信度 80%。
**次の自分へ**: ブート手順の番号は 1.5/1.6 の挿入式（CLAUDE.repo.md が「手順 2」を参照しているため繰り下げ禁止）。
**気になっていること**: CLAUDE.md の肥大化。doctrine はコンパクト版に絞り、詳細は example ファイルに逃がす。
