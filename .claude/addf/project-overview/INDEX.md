# ADDF エコシステム概要 — インデックス

> 生成日: 2026-07-07（full） | コミット: 6fab36db [修正] 旧名 ADDF-Release.addf.md の残存参照を Release.addf.md に統一

AutomatonDevDrive Framework (ADDF) — AI コーディングエージェントのためのリポジトリ構成フレームワーク。
計画駆動・ノウハウ蓄積・品質ゲートの三本柱で、エージェントの自律的な開発を支える。
v0.4.0 世代では「投機開発（worktree speculative development）」「オプトインスキル機構（GUI テスト一式の退避+有効化コピー）」「チェックリスト裏付け lint」「hooks 配線 lint」「部分導入からの正規化」「upstream/downstream 判定の明示シグナル化」が加わった。
v0.6.0（2026-07-06 リリース）では「**ディレクトリ大集約**（docs/ 明け渡し・`.claude/addf/` 占有名前空間・paths.toml 単一ソースの移行ツール群・addf-migrate Phase 2.5）」「ドキュメントレビューエージェント」「Plan 棚卸し（plan-audit・誤完了防止 lint）」「CI 品質ゲート」「バイナリ検証」「投機の昇格 PR 経路・投機適性・大改造の窓」「止まらない教義（コンテキスト枯渇の壁）」が加わった。

概念システム別に分類したドキュメント群。実装種別（スキル/エージェント/フック）では分けていない。

## 概念システム一覧

| ファイル | システム | 主な構成要素 |
|---|---|---|
| [system-planning.md](system-planning.md) | 計画駆動 | addf-dev, addf-mode, addf-plan-audit, TODO.md, Progress.md（日記）, Questions.md, Dashboard.md, PlanTemplate（one-shot マーカー）, .claude/addf/plans/ |
| [system-knowhow.md](system-knowhow.md) | ノウハウ蓄積 | addf-knowhow, addf-knowhow-index, addf-knowhow-filter, addf-knowhow-revise, addf-knowhow-network, addf-knowhow-agent, addf-experience |
| [system-quality.md](system-quality.md) | 品質ゲート | addf-code-review-agent（5ペルソナ）, addf-security-review-agent, addf-contribution-agent, addf-doc-review-agent, addf-lint（12項目）, lint-*.py 9本, run-all.sh, CI（test.yml） |
| [system-session.md](system-session.md) | セッション管理 | CLAUDE.md Boot Sequence, hooks（4本）, context-reminder.py, settings.json, addf-Behavior.toml, addf-permission-audit |
| [system-distribution.md](system-distribution.md) | 配布・導入 | addf-init（部分導入正規化含む）, addf-migrate（Phase 2.5 大移行）, addf-release, addf-overview, lock.json（ref 形式）, paths.toml＋migrate-paths.py＋lint-residual-paths.py, sync-optional-skills.py, .claude/addf/guides/ |
| [system-speculation.md](system-speculation.md) | 投機開発 | addf-speculate, speculate-guard/integrate/reconcile.py, Worktrees.md, [speculation] オプトイン, speculative/・integration/ の2層ブランチ, 昇格 PR 経路・投機適性・大改造の窓 |
| [system-visual-testing.md](system-visual-testing.md) | 視覚テスト（**オプトイン**） | addf-gui-test, addf-annotate-grid, addf-clip-image, addf-ui-test-agent（.claude/addf/optional/ 原本 + [gui-test] enable で有効化。デフォルト無効）, addfTools Swift 群 |

## 補完ドキュメント

| ファイル | 内容 |
|---|---|
| [claude-md-deps.md](claude-md-deps.md) | CLAUDE.md 依存グラフ・Boot Sequence |
| [phase-flows.md](phase-flows.md) | フェーズ進行スキル一覧（自動検出） |
| [interactions.md](interactions.md) | システム間相互作用アスキーアート |

## 全要素カウント

- スキル: 19本 = 常設16本（.claude/commands/。addf-plan-audit が新規）+ オプトイン3本（.claude/addf/optional/commands/ の GUI 系 — [gui-test] enable = true + sync-optional-skills.py apply で有効化。ADDF 本体では現在無効）
- エージェント定義: 6体 = 常設5体（.claude/agents/。addf-doc-review-agent が新規）+ オプトイン1体（addf-ui-test-agent — GUI オプトインに含まれる）
- フックスクリプト: 4本（+ フックから呼ばれる addfTools/context-reminder.py）
- addfTools スクリプト: lint 9本（plan-status・residual-paths が新規）・speculate 3本・migrate-paths＋paths.toml・verify-checksums＋checksums.sha256・sync-optional-skills・context-reminder・Swift ツール4種（+ build.sh / check-screen-recording.sh）
- ガイドドキュメント: 9本（.claude/addf/guides/。pr-format.md が新規）
- ノウハウ: 21件（.claude/addf/knowhow/ADDF/。ほかに読み方の作法 CLAUDE.md、INDEX.addf.md / INDEX.md）
- ADDF 開発計画: 47本（.claude/addf/plans-add/。状態の正は TODO.addf.md と lint ペア6）
- テンプレート: 5本（ExperienceTemplate, PlanTemplate, ProgressTemplate, ProgressTemplate.addf, Release）
- フレームワークテスト: フック3 + ツール16（自動） + スキルシナリオ8（手動）+ CI（test.yml が PR/push ごとに自動実行）
- 概念システム: 7（2026-07-07 full 実行でゼロベース再検証し維持。境界候補 — 移行・パス管理の独立化 / context-reminder 単独化 / 同期契約 lint 独立化 — はいずれも昇格見送り）
