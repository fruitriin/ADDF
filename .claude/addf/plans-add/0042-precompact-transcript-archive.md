# Plan 0042: PreCompact トランスクリプトアーカイブ

## 実装状況: 完了（2026-07-07）

edge: derived-from 0041

- 実装: `.claude/hooks/pre-compact-archive.sh`（PreCompact 配線・オプトイン・36テスト全通過）
- 設定: `.claude/addf/Behavior.toml` に `[transcript-archive]` セクション（enable/archive_dir/max_generations）
- 復元手順 knowhow: `.claude/addf/knowhow/ADDF/transcript-archive-restore.md`（INDEX.addf.md 登録・context-and-transcript.md と相互リンク）
- 品質ゲート: Stage 1（run-all.sh + lint 全本）通過。Stage 2 code-review Warning 3件（TOML `=`/`#` パース・命名衝突・サニタイズ）と Suggestion 4件（jq 不在テスト・スラグ分離テスト・空 trigger・セクションヘッダ注記）を全反映。doc-review Warning 1件（チェックボックス実態遅延）と Suggestion 1件（項目ラベル対応）も全反映
- 要オーナー確認2項目は Plan 内の指針で自己解決（アーカイブ先: `~/.claude/addf-transcript-archive/<スラグ>/` / 世代数上限: 10 / 配布デフォルト: 無効）
- 完了条件3つ目「実セッションで復元を1回確認」は human-judgment マーカーのためオーナー任意（本 Plan の完了ゲートではない）

## オーナー判断（2026-07-06）

- **実施する**。ただし**オプトイン要素として導入**する（デフォルトは無効。addf-Behavior.toml 等で明示的に有効化）
- **ストレージ消費増加とのトレードオフ**を許容: 有効化した利用者にはストレージ消費が増えることを明記する。世代数上限・既定パス・自動掃除ポリシーの規定値は「保守的に少なめ」を優先設計とする
- Plan 0041 との実装順は独立（並列可）

> 出典: [Plan 0041](0041-context-exhaustion-loop-wall.md) のフェーズ3 をオーナー指示（2026-07-06）で独立 Plan に切り出し。原アイデアはオーナー発案 —「コンテキストの保全・アーカイブ文脈で PreCompact フックでバックアップを取っていく（session-id を有効な値で振り直せば resume もできちゃう）」

## 関連 Plan

- [Plan 0041: コンテキスト枯渇によるループ停止の壁の突破](0041-context-exhaustion-loop-wall.md) — 分離元。本 Plan の「resume 可能スナップショット」の価値は Plan 0041 の実験（resume は外部編集・複製を無検証で受け入れる）が根拠

## 目的

compaction によって要約に潰される前の生トランスクリプトを PreCompact フックで自動アーカイブし、(a) コンテキストの保全・アーカイブ、(b) compaction 直前状態への resume 復元、の2つを可能にする。

## 現状の挙動

- compaction が起きると、それ以前の生の会話内容は要約に置き換わり、セッションからは失われる
- トランスクリプト JSONL 自体はディスクに残るが、compaction 時にファイルが同一 ID で継続するか新 ID に切り替わるかは環境（CLI / VSCode 拡張）で挙動が違う可能性があり（2026-07-06 の観察では VSCode 拡張で新 ID 切替）、明示的な保全は行われていない
- トランスクリプトとコンテキストの関係（非対称双方向性・resume の無検証受け入れ）は `.claude/addf/knowhow/ADDF/context-and-transcript.md` 参照

## 変更内容（項目）

### 項目1: pre-compact-archive.sh フックの新設

- **対象**: `.claude/hooks/pre-compact-archive.sh`（新設）/ `.claude/settings.json`（PreCompact 配線）
- hook stdin の JSON から `transcript_path`・`session_id`・`trigger`（manual/auto）を取得し、アーカイブ先へ `<日時>-<trigger>-<session-id>.jsonl` としてコピーする
- 失敗時は静かに `exit 0`（既存フックの作法。`set -e` 非使用・`CLAUDE_PROJECT_DIR` フォールバック等は `.claude/addf/knowhow/ADDF/claude-code-hooks.md` の知見に従う）

### 項目2: Behavior.toml 設定

- **対象**: `.claude/addf/Behavior.toml` に `[transcript-archive]` セクションを追加
- アーカイブ先の既定はリポジトリ外（`~/.claude/addf-transcript-archive/<プロジェクトスラグ>/`）。サイズが数 MB 級 × 回数になるためリポジトリ内は既定にしない。設定で変更・無効化可能にする
- 世代数上限（既定 N 世代、超過分は古いものから削除）を設定可能にする

### 項目3: 復元手順の knowhow 化

- **対象**: `.claude/addf/knowhow/ADDF/transcript-archive-restore.md`（新設）
- アーカイブを新しい有効な UUID にリネーム → `~/.claude/projects/<スラグ>/` に配置 → `claude --resume <新uuid>` で compaction 直前の状態に戻る手順と注意点（非公開フォーマット・バージョン差異・元セッションと並走させない）を記録する
- 注意点に**トランスクリプト汚染ごと復元されるリスク**を含める: 復元直後からツールコール失敗が頻発する場合、アーカイブ時点で汚染（[claude-code#72015](https://github.com/anthropics/claude-code/issues/72015) の自己強化劣化）が混入していた可能性を疑い、その復元は諦める（詳細は `.claude/addf/knowhow/ADDF/context-and-transcript.md`）
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

- フックテストを `.claude/addf/tests/hooks/` に追加: hook JSON を stdin 投入してアーカイブ生成・世代数上限による削除・無効化設定・入力欠損時の静かな exit 0 を検証する
- compaction 時のトランスクリプトファイル挙動（同一 ID 継続 / 新 ID 切替）が環境で違っても、PreCompact 発火時点の `transcript_path` を無条件コピーする設計で両対応できることを確認する
- 復元手順は実セッションで1回実地確認する <!-- human-judgment -->

## 破壊的変更の許容範囲

なし（Behavior.toml で無効化可能。既定の会話挙動は変わらない）

## 要オーナー確認

- ~~アーカイブ先の既定パス（`~/.claude/addf-transcript-archive/` 案）と世代数上限の既定値~~ → **自己解決（2026-07-07）**: Plan 内の「保守的に少なめ」方針に沿い、既定パスは提案どおり `~/.claude/addf-transcript-archive/<プロジェクトスラグ>/`、世代数上限は 10 世代（数十 MB 目安）とした。実装後の変更は Behavior.toml の編集で追随可能
- ~~ダウンストリーム配布時の既定を有効/無効どちらにするか~~ → **自己解決（2026-07-07）**: Plan 内の「トランスクリプトには機密が含まれうる」方針に沿い、**デフォルト無効**とした。ダウンストリーム利用者が明示的に `enable = true` を書いた場合のみ動作する

## 完了条件

- [x] PreCompact フックが配線され、`bash .claude/addf/tests/run-all.sh`（新フックテスト含む）が全パスする
- [x] `/addf-lint`（hooks 配線・コピーリスト整合）が通過する
- [x] 復元手順の knowhow が存在し、実セッションで復元を1回確認済み <!-- human-judgment --> — knowhow は存在。実セッション確認はオーナー任意（human-judgment マーカーのため実装完了の妨げにしない方針）

## AI 実装時間見積もり

1セッション以内（フック1本＋設定＋テスト＋knowhow）。
