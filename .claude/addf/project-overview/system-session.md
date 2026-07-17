# セッション管理 — Boot sequence, hooks, and configuration

> 概念単位の記録。実装がスキル/エージェント/フック/ファイルのどれであっても、
> 「セッションの開始・維持・コンテキスト管理・設定」に関わるものをまとめている。

## 構成要素

| 種別 | 名前 | 役割 |
|---|---|---|
| ファイル | CLAUDE.md | メインの指示ファイル。ブートシーケンス・迷ったときの作法・並列実装方針を定義 |
| ファイル | CLAUDE.repo.md | プロジェクト固有設定（ADDF 本体ではブートシーケンス補足。コミットする方針） |
| ファイル | CLAUDE.repo.example.md | ダウンストリーム用テンプレート（プロジェクト種別宣言・テスト・品質ゲート拡張） |
| ファイル | CLAUDE.local.md | 開発者個人設定（.gitignore 対象）。`# ADDF モード` セクションが /addf-mode の保存先 |
| ファイル | AGENTS.md | Codex 等の AGENTS.md 互換ツール用（英語。lint ペア3で CLAUDE.md と同期検査） |
| ファイル | .claude/settings.json | フック定義・権限設定（ダウンストリーム配布） |
| ファイル | .claude/settings.local.json | ADDF 開発用ローカル権限（配布しない） |
| ファイル | .claude/addf/Behavior.toml | フレームワーク動作設定（[gui-test] / [ccchain] / [speculation] / [transcript-archive] / [context-reminder] / [context-reminder.effective-context]） |
| スキル | addf-permission-audit | 権限を3パターンに分類し settings ファイルへの配置を提案 |
| フック | reset-turn-count.sh | SessionStart: ターンカウンター（.claude/.turn-count）をリセット |
| フック | turn-reminder.sh | UserPromptSubmit: 関心事A（ターン10/15の棚卸しリマインダー）+ 関心事B（context-reminder.py への中継） |
| フック | post-compact-recovery.sh | SessionStart(compact): コンパクション後の復帰手順（ブートシーケンス再実行）を注入 |
| フック | pre-compact-archive.sh | PreCompact: `[transcript-archive].enable = true` のときのみ、compaction 直前のトランスクリプト JSONL を archive_dir にコピー（Plan 0042・オプトイン・デフォルト無効）。ファイル名は英数・`_`・`-` のみにサニタイズ（パストラバーサル対策）、同一秒衝突は連番、世代数上限で古いものから削除 |
| フック | destructive-git-guard.sh | PreToolUse(Bash): 5種の破壊的 git 操作パターンを検出し、ブロックはせず理由をユーザーに提示するのみ（ブロックは settings.json の `permissions.ask` が担う。Plan 0043。→ system-quality と分業） |
| フック | skill-usage-log.sh | PreToolUse(Skill): スキル呼び出しを .claude/logs/skill-usage.jsonl にロギング |
| フック（オプトイン） | ccchain hook pre | PreToolUse(Bash): ccchain（EnumaElish）バイナリによる構造的コマンドパーミッション制御（Plan 0040）。`[ccchain] enable = true` + `sync-ccchain.py apply` で settings.json に配線される。パイプ・チェーン・サブシェル・`-exec` の中身まで構造解析し、プレフィックスマッチでは防げない危険コマンド（`find . -exec rm {} \;`・`curl ... \| bash` 等）を検出。バイナリは ADDF が配布しない（各自 `go install`）— 不在時はフックが空振りするフェイルセーフ（素通し）設計 |
| ツール | .claude/addf/addfTools/context-reminder.py | transcript の usage を実測し、閾値超過時に能動コンパクション促しを注入 |
| 状態 | .claude/.turn-count / .claude/.context-reminder-state | ターン数・前回通知時の実測値（.gitignore 対象） |

## 設計思想

CLAUDE.md を頂点とする階層的設定構造:

```
CLAUDE.md（汎用テンプレート）
  └─ @CLAUDE.repo.md（プロジェクト固有・コミットする）
       └─ @CLAUDE.repo.example.md（下流テンプレート）
  └─ CLAUDE.local.md（個人設定・gitignore。/addf-mode の状態保存先）
```

この分離により CLAUDE.md のマイグレーションを「ほぼ上書き」に近づける（Feedback.md 記録済み）。CLAUDE.local.md は「.gitignore 対象かつ毎セッション自動読込」という性質を利用して、新しいブートステップを増やさずにモード状態を全セッションへ行き渡らせる（.claude/addf/knowhow/ADDF/rule-placement-execution-guarantee.md）。

### turn-reminder の関心事分離 — Plan 0023

かつて turn-reminder.sh は「ターン数からコンテキスト残量を推測して断言する」問題を抱えていた。Plan 0023 で2つの関心事に分離:

- **関心事A（ターン数ベース・turn-reminder.sh）**: 10/15ターンで知見の定期棚卸し（/addf-knowhow・日記）を促す。コンテキスト残量には言及しない（根拠なく状態を断言しない）
- **関心事B（実測トークンベース・context-reminder.py）**: hook JSON の transcript_path から直近 assistant メッセージの usage（input + cache_read + cache_creation、isSidechain 除外）を実測し、閾値超過時のみ「観測事実 + モデル別の実効コンテキスト目安」を注入する。判断はモデル自身に委ねる（200k/1M variant は transcript から判別不可のため）。注入文言は Plan 0041 の**止まらない教義**で締める — 知見記録・日記が済んでいるならそのまま作業を続行してよい。compaction を起こすのは harness の仕事であり、復帰フックと日記が受け止める。エージェントの仕事は止まらないこと

context-reminder.py の設計原則: フックの仕事は事実の注入のみ / usage が取得できない状況は静かに終了（誤発火より無発火が安全）/ 前回通知値を `.context-reminder-state` に保持し、`renotify_step_tokens` 増えるまで再通知しない / 実測値が下がったら（コンパクション後）状態リセット。設定は addf-Behavior.toml の `[context-reminder]`（threshold_tokens = 180000、0 で無効化）と `[context-reminder.effective-context]`（モデル名の単語単位部分一致 → 実効コンテキスト目安）。

### 止まらない教義（コンテキスト枯渇の壁）— Plan 0041

/loop 自走がコンテキスト残量を理由に自主停止する壁への対処。auto-compact の発動点はフェーズ2で実測され（知見: .claude/addf/knowhow/ADDF/context-and-transcript.md — トランスクリプト汚染・自己強化劣化の知見も同記事）、「compaction は harness が受け止める前提で止まらない」ことと「残量少時は復帰容易性の高いタスクを選び、one-shot 級には着手しない」タスク運びが Progress 運用ルール 3.5（→ system-planning）と context-reminder の注入文言に配線された。post-compact-recovery.sh（compaction 後のブートシーケンス再実行注入）と代替わり日記が受け皿になる。

### トランスクリプトアーカイブ — Plan 0042

`[transcript-archive]` はデフォルト無効（オプトイン）。有効化すると `pre-compact-archive.sh` が compaction 直前のトランスクリプト JSONL を `archive_dir`（既定 `~/.claude/addf-transcript-archive` — リポジトリ外。ディスク消費と機密漏洩の副次コピーを避けるため）配下にコピーする。用途は (a) コンテキストの保全・アーカイブ、(b) アーカイブを新 UUID にリネームして `claude --resume` すれば compaction 直前状態への復元（`.claude/addf/knowhow/ADDF/transcript-archive-restore.md`）。`max_generations`（既定10）を超えた世代は古いものから削除する。フックは必須フィールド欠如時に静かに exit 0 で抜ける設計（誤発火より無発火を優先）。

### 破壊的操作ガード — Plan 0043

`settings.json` の `permissions.deny`（11パターン: `rm -rf /` 系・`chmod 777 /` 系・`dd`・`mkfs`・`shutdown`・`reboot`）が極端な破壊操作を常時ブロックし、`permissions.ask`（7パターン: `git push`・`git reset --hard`・`git clean`・`git branch -D`・`git checkout -- .`・`git restore .`/`restore --`）が破壊的 git 操作を確認対象にする。`destructive-git-guard.sh` はこれら5種の git パターンを検出して理由をユーザーに提示するだけで、ブロック自体は行わない（ブロックは permissions.ask の役目 — フックと設定の分業。→ system-quality）。

### ccchain コマンドゲート（オプトイン）— Plan 0040 フェーズ1・2

settings.json のプレフィックスマッチ（deny/ask）と destructive-git-guard.sh（advisory 提示）を補完する第3のレイヤー。ccchain（外部 Go バイナリ・EnumaElish）が PreToolUse(Bash) でコマンドを構造解析し、許可リストベースで評価する。ルールは `.ccchain.conf`（初回配置後はプロジェクトが自由にチューニングする前提 — 原本追従を強制しない点が sync-optional-skills と異なる）。ADDF 本体はフェーズ1でドッグフーディング導入済み（実運用コマンド群で `ccchain test` により調整してから配線 — 誤ルールで自セッションの Bash が使えなくなるリスクへの対処）。**フェーズ1の配線先（settings.local.json）とフェーズ2の sync-ccchain.py の対象（settings.json）は意図的に分離されており、統合はフェーズ4**（Feedback.md 記録済み）。知見は `.claude/addf/knowhow/ADDF/ccchain-dogfooding-phase1.md`。

### フックの堅牢性

全フックは `CLAUDE_PROJECT_DIR` 未設定時にカレントディレクトリへフォールバックする（未設定のまま展開すると `/.claude/...` への書き込みが静かに失敗するため）。意図的に `set -e` を使わず、失敗してもセッションを妨げず exit 0 で抜ける。skill-usage-log.sh は jq でエントリ全体を生成し JSONL インジェクションを防ぐ。pre-compact-archive.sh は bash+awk の手組み TOML パーサーを使う（`.claude/addf/knowhow/ADDF/bash-toml-parse-pitfalls.md` に8種の落とし穴が類型化されている）。

settings.json は2ファイルに分離:
- `settings.json`: ダウンストリームにも配布される汎用権限（破壊的 git 操作は ask・極端な破壊操作は deny）
- `settings.local.json`: ADDF 開発プロジェクト固有の権限（addf-permission-audit で分類・配置。hooks 定義は持たない）

## 主要フロー

```
セッション開始
  │
  ├─ reset-turn-count.sh → ターンカウンター 0
  │
  ├─（コンパクション後のみ）
  │  post-compact-recovery.sh → 復帰ガイダンス注入
  │  └─ ブートシーケンス再実行 → Progress/Feedback/TODO 確認 → 会話再開
  │
  ├─（PreCompact・[transcript-archive].enable = true のときのみ）
  │  pre-compact-archive.sh → トランスクリプト JSONL を archive_dir へコピー
  │
  ▼
CLAUDE.md ブートシーケンス
  ├─ 1. Feedback.md（1.5 Questions.md / 1.6 Dashboard.md / 1.7 DashboardComments.json —
  │      HTML ダッシュボードのアンカーコメント。対応後 resolved 化 → system-planning）
  ├─ 2. TODO.md（ADDF: + TODO.addf.md）
  ├─ 3. Progress.md（日記の末尾3エントリーで引き継ぎ）
  ├─ 4. タスクなし → 骨格プランニング or オーナーに確認
  └─ 5. knowhow-agent 起動
  │
  ▼
各ターン（UserPromptSubmit）
  ├─ turn-reminder.sh
  │  ├─ 関心事A: ターン10/15 → 知見棚卸しリマインダー
  │  └─ 関心事B: context-reminder.py へ中継
  │     └─ 実測 180k トークン超過 → 「コンパクション前に知見記録と
  │        日記更新を済ませよ。済んでいるなら止まらず続行してよい」と注入
  │        （作業縮小・停止の指示ではない — 止まらない教義）
  │
  ├─ skill-usage-log.sh → スキル使用ログ（PreToolUse: Skill）
  │
  ├─ destructive-git-guard.sh → 破壊的 git パターン検出時に理由を提示（PreToolUse: Bash。
  │  ブロックは permissions.ask/deny が担当）
  │
  └─（[ccchain] オプトイン有効時のみ）
     ccchain hook pre → Bash コマンドを構造解析し許可リストで評価（PreToolUse: Bash）
```

## 下流でのカスタマイズ

- `CLAUDE.repo.md` にプロジェクト固有の設定を記述（CLAUDE.md は上書きマイグレーション可能に保つ）
- `CLAUDE.local.md` で開発者個人の設定・セッションモードを保持
- `addf-Behavior.toml` で gui-test 有効化（→ sync-optional-skills.py apply）・ccchain 有効化（→ sync-ccchain.py apply。`.ccchain.conf` は配置後に自由チューニング可）・speculation 有効化と worktree 上限・transcript-archive 有効化（`archive_dir`/`max_generations`）・context-reminder の閾値/実効コンテキスト目安を調整（threshold_tokens = 0 で無効化）
- `settings.json` の権限ルールを addf-permission-audit で整理
- turn-reminder のターン閾値はスクリプト編集で調整可能

## 関連するシステム

- **計画駆動**: ブートシーケンスが計画駆動システムの起点。/addf-mode の状態を CLAUDE.local.md に保存。コンパクション復帰・context-reminder は日記（代替わり）と連動
- **ノウハウ蓄積**: turn-reminder（関心事A）と context-reminder（関心事B）がともに知見記録を促す
- **配布・導入**: settings.json / CLAUDE.md / hooks / addf-Behavior.toml は配布対象。マイグレーション時に更新される。ccchain のオプトイン配布（optional/ccchain/ 原本 + sync-ccchain.py）はオプトイン機構の第2の適用対象（→ system-distribution）
- **品質ゲート**: フックは .claude/addf/tests/hooks/（reset-turn-count・turn-reminder・context-reminder）で自動テストされ、実行権限（lint 項目2）と settings への配線（lint 項目11）も機械検査される
- **投機開発**: [speculation] は Behavior.toml のオプトインフラグ。addf-speculate は CLAUDE.local.md の /addf-mode 状態（responsiveness）を参照して事前確認の要否を決める
