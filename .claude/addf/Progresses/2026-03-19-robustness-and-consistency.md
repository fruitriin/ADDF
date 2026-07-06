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

## タスク: Plan 0008 — 堅牢性と一貫性の向上

### 1. addf-lint スキル作成
- [x] `.claude/commands/addf-lint.md` を作成
  - JSON 構文チェック (settings.json, settings.local.json)
  - hooks/ 実行権限チェック
  - commands/ frontmatter YAML パースチェック
  - addf-Behavior.toml 構文チェック
  - knowhow INDEX と実ファイルの整合性チェック

### 2. テンプレート同期チェック（addf-lint の一部）
- [x] Progress.md の運用ルールセクションとテンプレートの比較ロジック

### 3. settings.json パーミッション拡充
- [x] テスト実行の allow 確認（既に追加済みか確認）

### 4. テスト
- [x] `bash .claude/tests/run-all.sh` 通過確認

### 5. 品質検証
- [x] addf-code-review-agent
- [x] addf-contribution-agent
  - CLAUDE.md 分離パターン違反を修正（ブートシーケンスを汎用に戻し、ADDF 固有参照は CLAUDE.repo.md に移動）
  - W2: addf-lint チェック6にテンプレート同期の具体的コードを追加
  - W3: TODO.addf.md のパスをフルパスに修正
