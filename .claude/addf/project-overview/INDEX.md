# ADDF エコシステム概要 — インデックス

> 生成日: 2026-07-05 | コミット: 683d0942 [ドキュメント] 投機運用ガイドを追加（Plan 0028 フェーズ3-4）

AutomatonDevDrive Framework (ADDF) — AI コーディングエージェントのためのリポジトリ構成フレームワーク。
計画駆動・ノウハウ蓄積・品質ゲートの三本柱で、エージェントの自律的な開発を支える。
v0.4.0 世代では「投機開発（worktree speculative development）」「オプトインスキル機構（GUI テスト一式の退避+有効化コピー）」「チェックリスト裏付け lint」「hooks 配線 lint」「部分導入からの正規化」「upstream/downstream 判定の明示シグナル化」が加わった。

概念システム別に分類したドキュメント群。実装種別（スキル/エージェント/フック）では分けていない。

## 概念システム一覧

| ファイル | システム | 主な構成要素 |
|---|---|---|
| [system-planning.md](system-planning.md) | 計画駆動 | addf-dev, addf-mode, TODO.md, Progress.md（日記）, Questions.md, Dashboard.md, docs/plans/ |
| [system-knowhow.md](system-knowhow.md) | ノウハウ蓄積 | addf-knowhow, addf-knowhow-index, addf-knowhow-filter, addf-knowhow-revise, addf-knowhow-network, addf-knowhow-agent, addf-experience |
| [system-quality.md](system-quality.md) | 品質ゲート | addf-code-review-agent（5ペルソナ）, addf-security-review-agent, addf-contribution-agent, addf-lint（11項目）, lint-*.py 7本, run-all.sh |
| [system-session.md](system-session.md) | セッション管理 | CLAUDE.md Boot Sequence, hooks（4本）, context-reminder.py, settings.json, addf-Behavior.toml, addf-permission-audit |
| [system-distribution.md](system-distribution.md) | 配布・導入 | addf-init（部分導入正規化含む）, addf-migrate, addf-release, addf-overview, addf-lock.json（ref 形式）, sync-optional-skills.py, docs/guides/ |
| [system-speculation.md](system-speculation.md) | 投機開発（**新設**） | addf-speculate, speculate-guard/integrate/reconcile.py, Worktrees.md, [speculation] オプトイン, speculative/・integration/ の2層ブランチ |
| [system-visual-testing.md](system-visual-testing.md) | 視覚テスト（**オプトイン**） | addf-gui-test, addf-annotate-grid, addf-clip-image, addf-ui-test-agent（.claude/optional/ 原本 + [gui-test] enable で有効化。デフォルト無効）, addfTools Swift 群 |

## 補完ドキュメント

| ファイル | 内容 |
|---|---|
| [claude-md-deps.md](claude-md-deps.md) | CLAUDE.md 依存グラフ・Boot Sequence |
| [phase-flows.md](phase-flows.md) | フェーズ進行スキル一覧（自動検出） |
| [interactions.md](interactions.md) | システム間相互作用アスキーアート |

## 全要素カウント

- スキル: 18本 = 常設15本（.claude/commands/）+ オプトイン3本（.claude/optional/commands/ の GUI 系 — [gui-test] enable = true + sync-optional-skills.py apply で有効化。ADDF 本体では現在無効）
- エージェント定義: 5体 = 常設4体（.claude/agents/）+ オプトイン1体（addf-ui-test-agent — GUI オプトインに含まれる）
- フックスクリプト: 4本（+ フックから呼ばれる addfTools/context-reminder.py）
- addfTools スクリプト: lint 7本・speculate 3本・sync-optional-skills・context-reminder・Swift ツール4種（+ build.sh / check-screen-recording.sh）
- ガイドドキュメント: 8本（docs/guides/。speculative-development.md が新規）
- ノウハウ: 17件（docs/knowhow/ADDF/。ほかに読み方の作法 CLAUDE.md、INDEX.addf.md / INDEX.md）
- ADDF 開発計画: 38本（docs/plans-add/。0026/0028/0029/0033 は一部完了、0030〜0032・0035〜0038 は未着手/起案段階 — 状態の正は TODO.addf.md と lint ペア6）
- テンプレート: 4本（ExperienceTemplate, ProgressTemplate, ProgressTemplate.addf, Release）
- フレームワークテスト: フック3 + ツール11（自動） + スキルシナリオ8（手動）
- 概念システム: 7（Step 3 で探索的に再検証。前回6 → 投機開発を新設）
