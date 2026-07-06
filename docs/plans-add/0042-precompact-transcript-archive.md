# Plan 0042: PreCompact トランスクリプトアーカイブ

## 実装状況: 未着手

> 出典: [Plan 0041](0041-context-exhaustion-loop-wall.md) のフェーズ3 をオーナー指示（2026-07-06）で独立 Plan に切り出し。原アイデアはオーナー発案 —「コンテキストの保全・アーカイブ文脈で PreCompact フックでバックアップを取っていく（session-id を有効な値で振り直せば resume もできちゃう）」

## 関連 Plan

- [Plan 0041: コンテキスト枯渇によるループ停止の壁の突破](0041-context-exhaustion-loop-wall.md) — 分離元。本 Plan の「resume 可能スナップショット」の価値は Plan 0041 の実験（resume は外部編集・複製を無検証で受け入れる）が根拠

## 目的

compaction によって要約に潰される前の生トランスクリプトを PreCompact フックで自動アーカイブし、(a) コンテキストの保全・アーカイブ、(b) compaction 直前状態への resume 復元、の2つを可能にする。

## 現状の挙動

- compaction が起きると、それ以前の生の会話内容は要約に置き換わり、セッションからは失われる
- トランスクリプト JSONL 自体はディスクに残るが、compaction 時にファイルが同一 ID で継続するか新 ID に切り替わるかは環境（CLI / VSCode 拡張）で挙動が違う可能性があり（2026-07-06 の観察では VSCode 拡張で新 ID 切替）、明示的な保全は行われていない
- トランスクリプトとコンテキストの関係（非対称双方向性・resume の無検証受け入れ）は `docs/knowhow/ADDF/context-and-transcript.md` 参照

## 変更内容（項目）

### 項目1: pre-compact-archive.sh フックの新設

- **対象**: `.claude/hooks/pre-compact-archive.sh`（新設）/ `.claude/settings.json`（PreCompact 配線）
- hook stdin の JSON から `transcript_path`・`session_id`・`trigger`（manual/auto）を取得し、アーカイブ先へ `<日時>-<trigger>-<session-id>.jsonl` としてコピーする
- 失敗時は静かに `exit 0`（既存フックの作法。`set -e` 非使用・`CLAUDE_PROJECT_DIR` フォールバック等は `docs/knowhow/ADDF/claude-code-hooks.md` の知見に従う）

### 項目2: Behavior.toml 設定

- **対象**: `.claude/addf-Behavior.toml` に `[transcript-archive]` セクションを追加
- アーカイブ先の既定はリポジトリ外（`~/.claude/addf-transcript-archive/<プロジェクトスラグ>/`）。サイズが数 MB 級 × 回数になるためリポジトリ内は既定にしない。設定で変更・無効化可能にする
- 世代数上限（既定 N 世代、超過分は古いものから削除）を設定可能にする

### 項目3: 復元手順の knowhow 化

- **対象**: `docs/knowhow/ADDF/transcript-archive-restore.md`（新設）
- アーカイブを新しい有効な UUID にリネーム → `~/.claude/projects/<スラグ>/` に配置 → `claude --resume <新uuid>` で compaction 直前の状態に戻る手順と注意点（非公開フォーマット・バージョン差異・元セッションと並走させない）を記録する
- `context-and-transcript.md` と相互リンクする

### 項目4: lint・配布の整備

- `lint-hooks-wiring.py` が新フックの配線を検出することを確認する
- addf-init コピーリストへの追加（lint ペア5）
- アーカイブ先がリポジトリ外のため `.gitignore` 追加は不要なことを確認する

## 影響範囲

- 新フックはダウンストリーム配布対象（addf-init コピーリスト・hooks 配線 lint）
- settings.json の hooks 配線変更（配布テンプレート）
- ユーザーのホームディレクトリ（`~/.claude/addf-transcript-archive/`）にディスク消費が発生する — 世代数上限で抑制

## テスト方針

- フックテストを `.claude/tests/hooks/` に追加: hook JSON を stdin 投入してアーカイブ生成・世代数上限による削除・無効化設定・入力欠損時の静かな exit 0 を検証する
- compaction 時のトランスクリプトファイル挙動（同一 ID 継続 / 新 ID 切替）が環境で違っても、PreCompact 発火時点の `transcript_path` を無条件コピーする設計で両対応できることを確認する
- 復元手順は実セッションで1回実地確認する <!-- human-judgment -->

## 破壊的変更の許容範囲

なし（Behavior.toml で無効化可能。既定の会話挙動は変わらない）

## 要オーナー確認

- アーカイブ先の既定パス（`~/.claude/addf-transcript-archive/` 案）と世代数上限の既定値
- ダウンストリーム配布時の既定を有効/無効どちらにするか（トランスクリプトには機密が含まれうるため、配布先では明示オプトインの方が安全かもしれない）

## 完了条件

- [ ] PreCompact フックが配線され、`bash .claude/tests/run-all.sh`（新フックテスト含む）が全パスする
- [ ] `/addf-lint`（hooks 配線・コピーリスト整合）が通過する
- [ ] 復元手順の knowhow が存在し、実セッションで復元を1回確認済み <!-- human-judgment -->

## AI 実装時間見積もり

1セッション以内（フック1本＋設定＋テスト＋knowhow）。
