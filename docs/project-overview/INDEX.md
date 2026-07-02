# ADDF エコシステム概要 — インデックス

> 生成日: 2026-07-02 | コミット: e8731659 [テスト] 非 macOS 環境ではバイナリ実行テストを SKIP する

AutomatonDevDrive Framework (ADDF) — AI コーディングエージェントのためのリポジトリ構成フレームワーク。
計画駆動・ノウハウ蓄積・品質ゲートの三本柱で、エージェントの自律的な開発を支える。
v0.3.0 で「迷ったときの作法（7割共有原則）」「代替わり日記」「knowhow ライフサイクル管理」「視点ずらしレビュー」「テンプレート同期 lint」「実測ベース能動コンパクション促し」が加わった。

概念システム別に分類したドキュメント群。実装種別（スキル/エージェント/フック）では分けていない。

## 概念システム一覧

| ファイル | システム | 主な構成要素 |
|---|---|---|
| [system-planning.md](system-planning.md) | 計画駆動 | addf-dev, addf-mode, TODO.md, Progress.md（日記）, Questions.md, Dashboard.md, docs/plans/ |
| [system-knowhow.md](system-knowhow.md) | ノウハウ蓄積 | addf-knowhow, addf-knowhow-index, addf-knowhow-filter, addf-knowhow-revise, addf-knowhow-network, addf-knowhow-agent, addf-experience |
| [system-quality.md](system-quality.md) | 品質ゲート | addf-code-review-agent（5ペルソナ）, addf-security-review-agent, addf-contribution-agent, addf-lint（8項目）, lint-template-sync.py |
| [system-session.md](system-session.md) | セッション管理 | CLAUDE.md Boot Sequence, hooks（4本）, context-reminder.py, settings.json, addf-Behavior.toml, addf-permission-audit |
| [system-distribution.md](system-distribution.md) | 配布・導入 | addf-init, addf-migrate, addf-release, addf-overview, addf-lock.json（ref 形式）, docs/guides/ |
| [system-visual-testing.md](system-visual-testing.md) | 視覚テスト | addf-gui-test, addf-annotate-grid, addf-clip-image, addf-ui-test-agent, addfTools/ |

## 補完ドキュメント

| ファイル | 内容 |
|---|---|
| [claude-md-deps.md](claude-md-deps.md) | CLAUDE.md 依存グラフ・Boot Sequence |
| [phase-flows.md](phase-flows.md) | フェーズ進行スキル一覧（自動検出） |
| [interactions.md](interactions.md) | システム間相互作用アスキーアート |

## 全要素カウント

- スキル: 17本（うち .exp.md あり: 0本 — .exp.md は .gitignore 対象のローカル経験ファイル）
- エージェント定義: 5体
- フックスクリプト: 4本（+ フックから呼ばれる addfTools/context-reminder.py）
- ガイドドキュメント: 7本（docs/guides/）
- ノウハウ: 12件（docs/knowhow/ADDF/。ほかに読み方の作法 CLAUDE.md、INDEX.addf.md / INDEX.md）
- ADDF 開発計画: 25本（docs/plans-add/、全て完了）
- テンプレート: 4本（ExperienceTemplate, ProgressTemplate, ProgressTemplate.addf, Release）
- フレームワークテスト: フック3 + ツール2（自動） + スキルシナリオ8（手動）
- 概念システム: 6（Step 3 で探索的に再検証。前回と同じ6分類を維持）
