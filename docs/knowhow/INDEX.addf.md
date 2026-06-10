# Knowhow Index

> 自動生成。`/addf-knowhow-index reindex` で再生成できる。

| 鮮度 | ファイル | 要約 | キーワード |
|---|---|---|---|
| 🟡 2026-03-18 | [ADDF/claude-md-at-mention.md](ADDF/claude-md-at-mention.md) | CLAUDE.md の @FileName メンション展開の仕組みと使い分け | @展開, メンション, クオート, ネスト展開, CLAUDE.md, インライン展開, ファイル参照 |
| 🟡 2026-03-18 | [ADDF/ignore-file-strategy.md](ADDF/ignore-file-strategy.md) | .gitignore / .claudeignore / .git/info/exclude の役割分けと運用戦略 | .gitignore, .claudeignore, .git/info/exclude, respectGitignore, settings.json, Glob, Grep, ファイル除外 |
| 🟡 2026-03-19 | [ADDF/claude-code-hooks.md](ADDF/claude-code-hooks.md) | Claude Code Hooks の全イベント・exit コードフロー制御・設定方法・ADD フレームワークでの活用パターン | Hooks, PreToolUse, PostToolUse, Stop, SessionStart, exit code, ブロッキング, マッチャー, frontmatter, settings.json |
| 🟢 2026-06-10 | [ADDF/upstream-downstream-separation.md](ADDF/upstream-downstream-separation.md) | アップストリーム（ADDF）とダウンストリーム（プロジェクト）のファイル分離パターン3種 | .addf.md, ADDF/, addf-, プレフィックス, plans-add, INDEX.addf.md, ProgressTemplate, ダウンストリーム, アップストリーム |
| 🟡 2026-03-19 | [ADDF/permission-settings-pattern.md](ADDF/permission-settings-pattern.md) | 権限を3パターン（アップストリーム/ダウンストリーム/汎用）× 2プロジェクト種別で分類し settings.json / settings.local.json に配置するルール | permissions, settings.json, settings.local.json, アップストリーム, ダウンストリーム, 汎用, allow, ask |
| 🟡 2026-03-19 | [ADDF/pretooluse-block-with-rationale.md](ADDF/pretooluse-block-with-rationale.md) | PreToolUse フックで根拠提示型ブロックを行うパターン。/tmp/ 回避・CLAUDE_CODE_TMPDIR・cd 突き抜け防止等の横展開 | PreToolUse, block, reason, /tmp/, CLAUDE_CODE_TMPDIR, 権限要求, ガードフック, 根拠提示, cd突き抜け |
| 🟡 2026-03-21 | [ADDF/skill-design-patterns.md](ADDF/skill-design-patterns.md) | Anthropic 社内知見に基づくスキル設計パターン。9カテゴリ分類・Gotchas育成・段階的開示・description はトリガー条件等のベストプラクティス | スキル, skill, カテゴリ, Gotchas, Progressive Disclosure, description, config.json, オンデマンドフック, マーケットプレイス |
| 🟡 2026-03-21 | [ADDF/existing-project-install-pattern.md](ADDF/existing-project-install-pattern.md) | 既存プロジェクトへの ADDF 導入パターン。鶏と卵問題の解決、CLAUDE.md 退避戦略、干渉チェック、信頼モデル | addf-init, 既存プロジェクト, WebFetch, raw URL, CLAUDE.md 退避, 干渉チェック, 導入前レビュー, 信頼モデル, マーカーブロック |
| 🟡 2026-03-21 | [ADDF/release-skill-separation.md](ADDF/release-skill-separation.md) | リリーススキルの責務分割パターン。スキル=ルーター、設定ファイル=手順定義、exp=プロジェクト戦略 | addf-release, リリース, 責務分割, ルーター, exp, upstream, downstream, チェンジログ, publish |
| 🟢 2026-06-10 | [ADDF/rule-placement-execution-guarantee.md](ADDF/rule-placement-execution-guarantee.md) | エージェント運用ルールの配置先と実行保証。参照では実行されない、実行主体が必ず読むファイルにコア手順をインライン展開する。CLAUDE.local.md をセッション状態の保存先に使う応用も記載 | 実行保証, インライン展開, サブエージェント定義, 運用ドキュメント, ProgressTemplate, 集約ルール, 参照, メインエージェント, CLAUDE.local.md, セッション状態, addf-mode |
| 🟢 2026-06-10 | [ADDF/sync-lint-design.md](ADDF/sync-lint-design.md) | 同期 lint の設計。検出は決定的スクリプト・解釈と修復はエージェント。正規化テキスト比較、参照カバレッジ検査（ペア5）、列挙を持たない単一ソース化、ダウンストリーム配布前提の SKIP 設計、mktemp サンドボックスへのドリフト注入テスト | 同期チェック, lint-template-sync, addf-lint, テンプレート同期, ドリフト, exit code, SKIP, サンドボックス, git log ヒント, addfTools, カバレッジ, コピーリスト |
| 🟢 2026-06-10 | [ADDF/plan-status-drift-check.md](ADDF/plan-status-drift-check.md) | Plan 着手前の実態突合。TODO の「未着手」表記は信用せず git log で実装実態を検証し、実装済みなら残差分だけを新 Plan に切り出す | Plan, TODO, 未着手, 完了化, git log, 突合, ドリフト, 残差分, 二重実装 |
