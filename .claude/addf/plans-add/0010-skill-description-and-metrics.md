# 計画: スキル description 改善 & 使用計測フック

## 実装状況: 完了（2026-03-21、2026-06-11 遡及確認）

## 動機

Anthropic 社内の知見（[skill-design-patterns.md](../knowhow/ADDF/skill-design-patterns.md)）より:
- **description フィールドはモデル向け** — セッション開始時にスキル一覧が作られ、description でトリガー判定される。「要約」ではなく「いつトリガーすべきか」を書くべき
- **計測フック** — PreToolUse フックでスキル使用をログし、人気度やトリガー不足を検出できる

現在の ADDF スキルの description は機能説明寄りで、トリガー条件が不明瞭なものがある。
また、スキルの使用頻度を把握する手段がなく、改善の優先度判断ができない。

## 設計

### 1. description フィールドの見直し

`.claude/commands/addf-*.md` の全スキルの frontmatter description を点検し、以下の基準で書き直す:

**良い description の基準:**
- 「〜のとき使う」「〜したいとき」というトリガー条件が明確
- モデルが「このリクエストにこのスキルを使うべきか？」を判断できる
- 機能の列挙ではなく、ユースケースの列挙

**対象スキル:**
- `addf-knowhow` — ノウハウ記録時
- `addf-knowhow-index` — インデックス参照・再構築時
- `addf-knowhow-filter` — Plan に関連する knowhow のフィルタリング時
- `addf-gui-test` — GUI テスト実行時
- `addf-annotate-grid` / `addf-clip-image` — 画像処理時
- `addf-experience` — 経験ファイル検証時
- `addf-dev-loop` — 自律開発ループ時
- `addf-permission-audit` — 権限監査時

### 2. スキル使用計測フック

PreToolUse フックでスキル呼び出しをログする仕組みを導入する。

**設計:**
- `.claude/hooks/skill-usage-log.sh` を新設
- PreToolUse の Skill マッチャーで発火
- ログ先: `.claude/logs/skill-usage.jsonl`（.gitignore 対象）
- ログ形式: `{"timestamp": "...", "skill": "...", "session_id": "..."}`
- `/addf-lint` または専用コマンドでログの集計・可視化

**活用:**
- 使用頻度の低いスキルの description 改善や統合の判断材料
- トリガー不足（description が不適切で呼ばれていない）の検出
- 人気スキルへの投資判断

## 影響範囲
- `.claude/commands/addf-*.md`（全 addf スキルの description 修正）
- `.claude/hooks/skill-usage-log.sh`（新規）
- `.claude/settings.json` または `.claude/settings.local.json`（フック登録）
- `.gitignore`（ログディレクトリ除外）

## 見積もり
AI 実装: 15-20 分

## 実装結果

### 完了した項目
- 9スキルの description にトリガー条件（「〜のとき使う」）を追記
- `.claude/hooks/skill-usage-log.sh` — PreToolUse フックでスキル使用を JSONL ログ
- `settings.json` に PreToolUse Skill マッチャーのフック登録
- `.gitignore` に `.claude/logs/` 追加

### 改善されなかったスキル（既にトリガー条件が明確）
- `addf-init` — 「導入するとき」「整合性を確認したいとき」が既に記載
- `addf-lint` — 「品質ゲート前、CI、設定変更後に使う」が既に記載
- `addf-migrate` — 「アップデート・バージョンアップ・マイグレーションを行いたいとき」が既に記載

## 状態: 完了（2026-03-21）
