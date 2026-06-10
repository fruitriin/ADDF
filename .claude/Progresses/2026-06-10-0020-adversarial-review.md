# 進捗表

## 運用ルール

### タスク開始時
1. `.claude/Feedback.md` を読み、前回の改善アクションで未対応のものがあれば考慮する
2. 以下の手順で Markdown チェックリストを作成する
   1. 1ショットで作業できる範囲にサブタスクを分割する
   2. 並行作業できる粒度でさらに分割する
   3. 各サブタスクにテスト作成・統合テスト・Lint・ビルドが必要か検討し、必要なら追加する
   4. 必要に応じて 2.1〜2.3 を再帰的に適用する

### 作業中
3. サブタスク着手時に `- [x]` でチェックしていく。並列可能なタスクはコンテナオーケストレーションを利用する
4. 実装フェーズの最終サブタスク完了時、実装で得た知見を `/addf-knowhow` で記録する（既存 knowhow の更新も含む）

### エージェント起動時の共通ルール
- エージェントチーム（TeamCreate）やサブエージェント（Agent）を作成するとき、各エージェントへのプロンプトに **最初に `/addf-knowhow-index` を実行する** よう指示を含めること
- これにより各エージェントがプロジェクトの知見ベースを把握した状態で作業を開始できる

### タスク完了時 — 品質検証

4. プロジェクトのビルド・Lint・テストコマンドを実行する
   - ADD フレームワークテスト: `bash .claude/tests/run-all.sh`
   - **失敗した場合 → 実装に差し戻す**。原因分析 → 修正 → 再実行
5. `addf-code-review-agent` でコードレビューを実施する
   - 通常タスクは単体（ペルソナなし）で起動する
   - **マイルストーン・リリース直前・`mode: critical` 宣言時・unattended 自走時（unattended モードは将来バージョンで導入予定）**は、ペルソナ並列（視点ずらしレビュー）を起動する。起動前に `.claude/agents/addf-code-review-agent.md` を読み、ペルソナ定義に従うこと
   - ペルソナ並列の集約: 同一箇所・同一原因の指摘は1件にまとめてペルソナを列挙する。**2ペルソナ以上が独立に指摘した項目は重要度を1段上げる**（コンセンサス補正）
6. `addf-contribution-agent` で ADD フレームワークへのコントリビューション候補を検出する
7. レビュー指摘への対応:
   - **Critical/High**: 必ずこのフェーズ内で修正する（先送り禁止）
   - **Medium**: 原則修正。先送りする場合は独立計画を起こす
   - **Low/Info**: Plan に記録し、必要に応じて独立計画で対応
   - **バグ分離**: 発見されたバグが現在のプランと関心事が異なる場合は、修正せずに新しいプラン（`docs/plans/`）を書き起こし、`TODO.md` に追加するのみで現在のプランを完了させる
   - 修正後、ビルド・Lint・テストを再実行して通過を確認する

#### 完了処理

8. 投入されたタスクのPlanに実装完了状況を反映する
9. `.claude/Feedback.md` にPlan, TODO, Progress推進エンジンの問題の記録・改善アクションを追記する。反映済みの項目は削除する
10. `.claude/Feedback.md` にプロジェクト進行上の問題の記録・改善アクションを追記する。反映済みの項目は削除する
11. `.claude/Progresses/YYYY-MM-DD-プラン名.md` にリネームして移動し、`.claude/templates/ProgressTemplate.addf.md` から新規の Progress.md を作成する
12. Progress 推進エンジン自体に関するフィードバック・ノウハウがあれば、テンプレート（`.claude/templates/ProgressTemplate.addf.md`）の改善案を `.claude/Feedback.md` に記録する

13. コミットする

---

## タスク

### 現在のタスク: Plan 0020 — レビューエージェントの視点ずらし

#### サブタスクチェックリスト

- [x] `.claude/agents/addf-code-review-agent.md` にペルソナ機構（5種 + 集約ルール）を追加
- [x] `.claude/agents/addf-security-review-agent.md` の攻撃者プロンプトを強化
- [x] `.claude/templates/ProgressTemplate.addf.md` に発動条件付きペルソナ並列を追記（運用中 Progress.md にも同期）
- [x] `CLAUDE.repo.example.md` の品質ゲート拡張にペルソナ言及を追加
- [x] `docs/guides/agents.md` にペルソナ一覧・発動条件の解説を追加
- [x] `bash .claude/tests/run-all.sh` 通過確認（8 passed, 0 failed）
- [x] addf-code-review-agent でセルフレビュー（Critical 0 / Warning 2 / Suggestion 4 → 全対応、テスト再通過）
- [x] Plan 0020 に実装状況反映・TODO.addf.md 更新
- [x] knowhow 記録（rule-placement-execution-guarantee.md 新規、upstream-downstream-separation.md 統合）・Feedback 追記
- [ ] コミット
- 注: addf-contribution-agent はフレームワーク本体のため省略（Feedback.md 問題の記録に既載の判断に従う）

#### 日記

##### 2026-06-10 着手

**やったこと**: knowhow エージェントから関連知見を取得（ルーターパターン、upstream/downstream 分離、@メンション運用）。対象5ファイルを読了。
**今の見立て**: ペルソナは Agent ツールの prompt 経由で渡す設計が現実的（--persona= は概念表記）。エージェント定義に「ペルソナ指定があれば採用、なければ従来のバランス型」と書く。確信度 85%。
**次の自分へ**: 実装順は agent 2本 → テンプレート → ガイド。テンプレート変更時は Progress.md（運用中のコピー）との同期も確認。
**気になっていること**: ProgressTemplate と CLAUDE.repo.example.md の品質ゲート記述の重複。二重管理にならない範囲で追記する。

##### 2026-06-10 完了

**やったこと**: 5ファイル実装 → テスト通過 → 単体レビュー → Warning 2件（集約ルールの実行保証・unattended 未定義）と Suggestion を修正 → knowhow 2件記録。
**今の見立て**: Plan 0020 完了。レビューの W-1 指摘（参照では実行保証がない）は本質的で、knowhow 化した。
**次の自分へ**: 次タスクは Plan 0016（7割共有原則）が推奨順。0016 実装時、ペルソナ並列の発動条件「unattended」が実体を持つので、agent 定義の「将来バージョンで導入予定」注記を外すこと。
**気になっていること**: ペルソナ並列の実運用テストは未実施（マイルストーン時に初発動）。初回発動時の挙動は要観察。
