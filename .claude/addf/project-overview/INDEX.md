# ADDF エコシステム概要 — インデックス

> 生成日: 2026-07-11（full）/ 2026-07-17（patch — v0.7.0 リリース前の鮮度更新） | コミット: 0fc990a [進捗] v0.7.0 リリース準備 — Plan 0059/0060 knowhow 記録・README ccchain 記載補完

AutomatonDevDrive Framework (ADDF) — AI コーディングエージェントのためのリポジトリ構成フレームワーク。
計画駆動・ノウハウ蓄積・品質ゲートの三本柱で、エージェントの自律的な開発を支える。

v0.4.0 世代では「投機開発（worktree speculative development）」「オプトインスキル機構（GUI テスト一式の退避+有効化コピー）」「チェックリスト裏付け lint」「hooks 配線 lint」「部分導入からの正規化」「upstream/downstream 判定の明示シグナル化」が加わった。
v0.6.0（2026-07-06 リリース）では「**ディレクトリ大集約**（docs/ 明け渡し・`.claude/addf/` 占有名前空間・paths.toml 単一ソースの移行ツール群・addf-migrate Phase 2.5）」「ドキュメントレビューエージェント」「Plan 棚卸し（plan-audit・誤完了防止 lint）」「CI 品質ゲート」「バイナリ検証」「投機の昇格 PR 経路・投機適性・大改造の窓」「止まらない教義（コンテキスト枯渇の壁）」が加わった。
v0.6.1（2026-07-07 lock 更新以降）では「**トランスクリプトアーカイブ**（PreCompact フック・オプトイン）」「**破壊的操作ガード**（deny 11パターン・ask 拡張・destructive-git-guard.sh）」「**モデル配分ポリシー**（addf-implementer エージェント・DelegationRules.md・model-allocation.md ガイド）」「**VitePress ドキュメントサイト骨格**（docs/・sync-docs.mjs）」「**マイグレーション実行時耐障害性強化**（GitHub Issue #26 実測回収）」が加わった。
v0.6.2（2026-07-11 リリース）では「CHANGELOG・README 網羅性回収と lint ペア8 新設（Plan 0053）」が加わった。
v0.7.0 準備世代（2026-07-17 時点・Unreleased 最終化済み）では「**ローカル HTML ダッシュボードとアンカーコメント・レビューループ**（generate-dashboard.py・DashboardComments.json・ブートシーケンス手順 1.7・crit.md 二層接続 — Plan 0058）」「**ccchain コマンドゲートのオプトイン配布**（[ccchain]・sync-ccchain.py・optional/ccchain/・lint セクション13 — Plan 0040 フェーズ1・2）」「**downstream 環境適合の回収**（migrate 手順書自己点検 Phase 2.4・make_sandbox 疑似コピー・compile_pattern lookbehind 境界 — Issue #27〜#31・#33 = Plan 0055/0059/0060）」が加わった。

概念システム別に分類したドキュメント群。実装種別（スキル/エージェント/フック）では分けていない。

## 概念システム一覧

| ファイル | システム | 主な構成要素 |
|---|---|---|
| [system-planning.md](system-planning.md) | 計画駆動 | addf-dev, addf-mode, addf-plan-audit, addf-implementer, DelegationRules.md, TODO.md, Progress.md（日記）, Questions.md, Dashboard.md, generate-dashboard.py＋DashboardComments.json（ローカルダッシュボード・アンカーコメント）, PlanTemplate（one-shot マーカー・owner_feedback フィールド）, .claude/addf/plans/ |
| [system-knowhow.md](system-knowhow.md) | ノウハウ蓄積 | addf-knowhow, addf-knowhow-index, addf-knowhow-filter, addf-knowhow-revise, addf-knowhow-network, addf-knowhow-agent, addf-experience |
| [system-quality.md](system-quality.md) | 品質ゲート | addf-code-review-agent（5ペルソナ）, addf-security-review-agent, addf-contribution-agent, addf-doc-review-agent, addf-lint（13項目・sync 8ペア）, lint-*.py 9本, run-all.sh, CI（test.yml）, destructive-git-guard.sh（deny/ask との分業） |
| [system-session.md](system-session.md) | セッション管理 | CLAUDE.md Boot Sequence（1.7 アンカーコメント読み取り新設）, hooks（6本＋ccchain オプトイン）, context-reminder.py, settings.json（deny/ask 拡張）, addf-Behavior.toml（[ccchain] 新設）, addf-permission-audit |
| [system-distribution.md](system-distribution.md) | 配布・導入 | addf-init（部分導入正規化含む）, addf-migrate（Phase 2.4 手順書自己点検・Phase 2.5 大移行・実行時耐障害性強化）, addf-release, addf-overview, lock.json（ref 形式・v0.6.2）, paths.toml＋migrate-paths.py＋lint-residual-paths.py（lookbehind 境界）, sync-optional-skills.py＋sync-ccchain.py, .claude/addf/guides/, docs/（VitePress サイト骨格） |
| [system-speculation.md](system-speculation.md) | 投機開発 | addf-speculate, speculate-guard/integrate/reconcile.py, Worktrees.md, [speculation] オプトイン, speculative/・integration/ の2層ブランチ, 昇格 PR 経路・投機適性・大改造の窓 |
| [system-visual-testing.md](system-visual-testing.md) | 視覚テスト（**オプトイン**） | addf-gui-test, addf-annotate-grid, addf-clip-image, addf-ui-test-agent（.claude/addf/optional/ 原本 + [gui-test] enable で有効化。デフォルト無効）, addfTools Swift 群 |

## 補完ドキュメント

| ファイル | 内容 |
|---|---|
| [claude-md-deps.md](claude-md-deps.md) | CLAUDE.md 依存グラフ・Boot Sequence・並列実装方針 |
| [phase-flows.md](phase-flows.md) | フェーズ進行スキル一覧（自動検出） |
| [interactions.md](interactions.md) | システム間相互作用アスキーアート |

## 全要素カウント

- スキル: 19本 = 常設16本（.claude/commands/）+ オプトイン3本（.claude/addf/optional/commands/ の GUI 系 — [gui-test] enable = true + sync-optional-skills.py apply で有効化。ADDF 本体では現在無効）。前回 full（2026-07-07）から本数の変化なし
- エージェント定義: 7体 = 常設6体（.claude/agents/。addf-implementer が新規 — Plan 0049）+ オプトイン1体（addf-ui-test-agent — GUI オプトインに含まれる）
- フックスクリプト: 6本（reset-turn-count・post-compact-recovery・pre-compact-archive・turn-reminder・skill-usage-log・destructive-git-guard）+ フックから呼ばれる addfTools/context-reminder.py + オプトイン配線の ccchain hook pre（外部バイナリ・[ccchain] 有効時のみ）
- addfTools スクリプト: lint 9本・speculate 3本・migrate-paths＋paths.toml・verify-checksums＋checksums.sha256・sync-optional-skills・sync-ccchain〔新規 — Plan 0040〕・generate-dashboard〔新規 — Plan 0058〕・context-reminder・Swift ツール4種（+ build.sh / check-screen-recording.sh）= 計30ファイル
- ガイドドキュメント: 10本（.claude/addf/guides/）
- ノウハウ: 29件（.claude/addf/knowhow/ADDF/。ccchain-dogfooding-phase1・vitepress-embed-escape-pitfalls が新規。ほかに読み方の作法 CLAUDE.md、INDEX.addf.md / INDEX.md）
- ADDF 開発計画: 68本（.claude/addf/plans-add/。状態の正は TODO.addf.md と lint ペア6）
- テンプレート: 6本（DelegationRules, ExperienceTemplate, PlanTemplate〔owner_feedback フィールド追加 — Plan 0058〕, ProgressTemplate, ProgressTemplate.addf, Release）
- フレームワークテスト: フック5（自動）+ ツール19（自動。test-generate-dashboard〔drift-injection 方式〕・test-sync-ccchain が新規）+ スキルシナリオ8（手動）+ CI（test.yml が PR/push ごとに自動実行）
- 概念システム: 7（2026-07-11 full 実行でゼロベース再検証し維持。2026-07-17 patch では新規要素〔generate-dashboard.py/DashboardComments.json → 計画駆動、sync-ccchain.py/optional/ccchain/ → 配布・導入＋セッション管理〕を既存システムへマッピングした — 境界の再探索は patch のためしていない。オプトイン対象が GUI 以外に増えたため「オプトイン機構」の独立システム昇格は次回 full の再検討事項）
