# CLAUDE.md 依存グラフ・Boot Sequence

> 生成日: 2026-07-05（CLAUDE.md・AGENTS.md・settings.json は前回生成時から変更なし — 内容は再検証済み）

## CLAUDE.md と CLAUDE.repo.md の関係

```
CLAUDE.md（汎用テンプレート — マイグレーション時に上書き可能）
│
├─ @CLAUDE.repo.md（プロジェクト固有設定 — コミットする方針）
│    └─ @CLAUDE.repo.example.md（ダウンストリーム用テンプレート）
│         └─ ADDF 本体では: ブートシーケンス補足
│              @.claude/addf/plans-add/TODO.addf.md
│
├─ CLAUDE.local.md（開発者個人設定 — .gitignore 対象）
│    ├─ @CLAUDE.local.example.md
│    └─ 「# ADDF モード」セクション（/addf-mode の保存先）
│
└─ AGENTS.md（Codex 互換 — CLAUDE.md を参照しつつ独立。lint ペア3で同期検査）
```

**設計方針**: CLAUDE.repo.md にプロジェクト固有設定を寄せることで、CLAUDE.md のマイグレーションを単純な上書きに近づける。この方針を崩すとマイグレーション実装が複雑化する（Feedback.md 記録済み）。CLAUDE.repo.md はリポジトリにコミットする（チーム共有・マイグレーション対象外）。

## Boot Sequence

CLAUDE.md で定義されるブートシーケンス:

```
セッション開始
│
├─ [Hook] reset-turn-count.sh → .turn-count = 0
├─ [Hook] post-compact-recovery.sh（compact 時のみ）
│
▼
Step 1: @.claude/addf/Feedback.md を読む
│       └─ 未対応の改善アクションを確認
│  Step 1.5: @.claude/addf/Questions.md を読む
│       └─ オーナーの新しい回答があれば Plan に反映し「回答済み」へ移す
│  Step 1.6: .claude/addf/Dashboard.md が存在すれば冒頭で提示
│       └─ unattended 自走の差分まとめ。オーナー応答確認後に削除
│
Step 2: @TODO.md を読む
│       └─ タスクバックログと優先度を把握
│       └─ [ADDF 本体のみ] @.claude/addf/plans-add/TODO.addf.md も読む
│
Step 3: @.claude/addf/Progress.md を読む
│       └─ 進行中タスクがあれば継続
│       └─ 「日記」セクションがあれば末尾3エントリーを読み、
│          前任者の状況・判断・気にしていたことを把握してから着手
│
Step 4: TODO に未完了タスクがない場合
│       ├─ .claude/addf/plans/ に計画ファイルがない（プロジェクト初回）
│       │   → 骨格プランニング（走査 → ヒアリング（A: 質問形式 / B: フリーフォーム）
│       │     → 初動計画 2〜3本を .claude/addf/plans/ に作成 → TODO 登録
│       │     → CLAUDE.repo.md 未作成なら生成 → オーナーに優先度確認）
│       └─ 計画ファイルがある → オーナーに次のタスクを確認
│
Step 5: Plan 特定後、knowhow サブエージェントを起動
        ├─ Plan ファイルの内容をサブエージェントに渡す
        ├─ .claude/addf/knowhow/ を走査
        └─ 関連 knowhow のパスと要約をメインコンテキストに返す
```

## 迷ったときの作法（7割共有原則）— CLAUDE.md 本文に常駐

Plan の曖昧さに遭遇したら「この方向で進めて Plan の意図と合致する確信度」を見積もり、独立した3軸で進む/止まる/問うを決める:

| 軸 | 値 | 意味 |
|---|---|---|
| A: 信頼性 trust | nervous(5割) / normal(7割・デフォルト) / full(9割) | 閾値そのものを決める |
| B: 応答性 responsiveness | interactive（即時質問）/ relaxed（Questions.md に置いて別タスクへ・デフォルト）/ unattended（質問を置き speculative/ ブランチで投機続行） | 閾値割れ時の行動 |
| C: 完成イメージ確度 image_clarity | specific(-1段) / balanced(±0・デフォルト) / vague(+1段) | 閾値を補正 |

- モードは Plan フロントマターまたは `/addf-mode` で宣言（保存先は CLAUDE.local.md）
- worktree 隔離下は閾値を1段下げてよい。checkpoint/<phase>-<N> ブランチ・alt/ 分岐を許可
- unattended の情報伝達は `dashboard_report`（Dashboard.md 提示）/ `uncertainty_notify`（外部通知）の2フラグで制御

## CLAUDE.md が参照する外部ファイル依存グラフ

```
CLAUDE.md
├─ @.claude/addf/Feedback.md ................ 改善アクション記録
├─ @.claude/addf/Questions.md ............... 非同期質問箱（1.5）
├─ .claude/addf/Dashboard.md ................ unattended 差分まとめ（1.6・実行時生成、.gitignore）
├─ .claude/addf/Dashboard.example.md ........ Dashboard 書式の参照元
├─ .claude/addf/Questions.example.md ........ Questions 書式（Q例）の参照元
├─ @TODO.md ............................ タスクバックログ
├─ @.claude/addf/Progress.md ................ 現在のタスク進捗（運用ルール・日記書式）
├─ @CLAUDE.repo.md ..................... プロジェクト固有設定
│    └─ @CLAUDE.repo.example.md
│         └─ @.claude/addf/plans-add/TODO.addf.md（ADDF 本体のみ）
├─ .claude/addf/plans/ ......................... 実装計画ファイル群
├─ .claude/addf/knowhow/ ....................... ノウハウ蓄積
└─ CLAUDE.repo.md 経由で CONTRIBUTING.md の計画駆動モデルに接続
```

CLAUDE.md が参照する `.claude/` 配下ファイルは addf-init のコピーリスト（または .gitignore の ADDF ブロック）でカバーされている必要があり、漏れは lint ペア5（WARNING）が検出する。

## settings.json のフック定義

| イベント | フック | トリガー条件 | 動作 |
|---|---|---|---|
| SessionStart | reset-turn-count.sh | 常時 | .turn-count を 0 にリセット |
| SessionStart | post-compact-recovery.sh | compact 時のみ | 復帰ガイダンス（ブートシーケンス再実行手順）を注入 |
| UserPromptSubmit | turn-reminder.sh | 常時 | 関心事A: ターンカウント（10/15 で棚卸しリマインダー）。関心事B: stdin の hook JSON を context-reminder.py に中継 |
| PreToolUse | skill-usage-log.sh | Skill マッチ時 | スキル使用を .claude/logs/skill-usage.jsonl にロギング |

全フックは `CLAUDE_PROJECT_DIR` 未設定時にカレントディレクトリへフォールバックし（未設定だと `/.claude/...` に展開されて静かに失敗するため）、失敗してもセッションを妨げず exit 0 で抜ける設計。

## 権限設定構造

| ファイル | 配布対象 | 内容 |
|---|---|---|
| .claude/settings.json | ダウンストリームにも配布 | フック定義 + 汎用権限（Read/Edit/git/gh 読み取り系/テストランナー/addfTools lint）。破壊的操作（git push, reset --hard, clean）は ask |
| .claude/settings.local.json | ADDF 開発のみ | ADDF 開発固有の権限（配布しない。addf-permission-audit で分類。フック定義は持たない — 配線は lint 項目11が突合） |
