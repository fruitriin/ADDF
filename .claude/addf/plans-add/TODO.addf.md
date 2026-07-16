# TODO (ADDF)

`.claude/addf/plans-add/` の完了状態・優先度をトラックする。
計画ファイルと TODO が一致しなければ TODO を編集する。

## 現在のフェーズ: v0.6.2 リリース済み（2026-07-11）。Plan 0040 フェーズ1・2（ccchain 導入・オプトイン配布機構）完了（2026-07-14）。フェーズ3〔ガイド・migrate統合〕・フェーズ4〔統合〕は未着手。Plan 0055（taskbar.fm Issue #27〜#29回収）完了（2026-07-14）。Plan 0054（検討スタブ）は最優先で未着手。Plan 0056（検討スタブ・Plan 系統樹）・Plan 0057（検討スタブ・コミットベースラインのプロファイル化）起票（2026-07-16）。Plan 0058（Dashboard HTML 化と crit.md 連携）はフェーズA・B・C 完了（2026-07-16。アンカーコメント UI 実装済み・オーナーのブラウザ動線確認待ち）。Plan 0059〜0064（オープン Issue 回収）・0065（README ダッシュボード記載）起票（2026-07-16）。Plan 0048 は要確認で静観中（Q6投下済み）

## バックログ

| 優先度 | Phase | 計画ファイル | 状態 |
|---|---|---|---|
| 1 | 1 | `.claude/addf/plans-add/0001-immediate-fixes.md` | 完了 |
| 2 | 2 | `.claude/addf/plans-add/0002-readme-and-skill-docs.md` | 完了 |
| 3 | 3 | `.claude/addf/plans-add/0003-english-docs.md` | 完了 |
| 4 | 4 | `.claude/addf/plans-add/0004-gui-test-cross-platform.md` | 完了 |
| 5 | 5 | `.claude/addf/plans-add/0005-everything-claude-code-research.md` | 完了 |
| 6 | 6 | `.claude/addf/plans-add/0006-skill-quality.md` | 完了 |
| 7 | 7 | `.claude/addf/plans-add/0007-testing-and-rename.md` | 完了 |
| 8 | 8 | `.claude/addf/plans-add/0008-robustness-and-consistency.md` | 完了 |
| 9 | 9 | `.claude/addf/plans-add/0009-experience-bootstrap.md` | 完了 |
| 10 | 10 | `.claude/addf/plans-add/0010-skill-description-and-metrics.md` | 完了 |
| 11 | 11 | `.claude/addf/plans-add/0011-version-lockfile-and-migration.md` | 完了 |
| 12 | 12 | `.claude/addf/plans-add/0012-codex-support.md` | 完了 |
| 13 | 13 | `.claude/addf/plans-add/0013-addf-init.md` | 完了 |
| 14 | 14 | `.claude/addf/plans-add/0014-readme-simplification.md` | 完了 |
| 15 | 15 | `.claude/addf/plans-add/0015-existing-project-install.md` | 完了 |
| 16 | 16 | `.claude/addf/plans-add/0016-stop-or-go-doctrine.md` | 完了 |
| 17 | 17 | `.claude/addf/plans-add/0017-progress-checkpoints.md`（代替わり日記） | 完了 |
| 18 | 18 | `.claude/addf/plans-add/0018-knowhow-expiry.md` | 完了 |
| 19 | 19 | `.claude/addf/plans-add/0019-failure-experience.md` | 完了 |
| 20 | 20 | `.claude/addf/plans-add/0020-adversarial-review.md` | 完了 |
| 21 | 21 | `.claude/addf/plans-add/0021-template-sync-lint.md` | 完了 |
| 22 | 22 | `.claude/addf/plans-add/0022-addf-init-copylist-refresh.md` | 完了 |
| 23 | 23 | `.claude/addf/plans-add/0023-turn-reminder-context-split.md` | 完了 |
| 24 | 24 | `.claude/addf/plans-add/0024-todo-plan-status-lint.md` | 完了 |
| 25 | 25 | `.claude/addf/plans-add/0025-rename-repo-to-addf.md` | 完了 |
| 1 | 26 | `.claude/addf/plans-add/0026-review-residual-backlog.md` | 一部完了（セキュリティ High・破壊的 git 対策は Plan 0043 で対応済み。[Critical] settings.json/hooks 自己書き換え保護は Plan 0054 として回収済み〔2026-07-11 起票〕） |
| 2 | 27 | `.claude/addf/plans-add/0027-executable-checklist-doctrine.md` | 完了 |
| 3 | 28 | `.claude/addf/plans-add/0028-worktree-speculative-dev.md` | 完了 |
| 4 | 29 | `.claude/addf/plans-add/0029-gui-test-environment-matrix.md` | 一部完了（フェーズ1 完了。環境マトリクスはフェーズ2以降） |
| 5 | 30 | `.claude/addf/plans-add/0030-ci-quality-gate.md` | 一部完了（実装・CI 実地検証済み。branch protection の要否のみオーナー判断待ち） |
| 6 | 31 | `.claude/addf/plans-add/0031-binary-verification.md` | 完了 |
| 7 | 32 | `.claude/addf/plans-add/0032-knowhow-freshness-audit.md` | 完了 |
| 4 | 33 | `.claude/addf/plans-add/0033-downstream-reported-fixes.md` | 完了（項目4=PlanTemplate は Plan 0035 フェーズA で実施） |
| 5 | 34 | `.claude/addf/plans-add/0034-downstream-feedback-fixes.md` | 完了 |
| 3 | 35 | `.claude/addf/plans-add/0035-pr-standard-format.md` | 完了（フェーズA・B・C。2026-07-05） |
| 3 | 36 | `.claude/addf/plans-add/0036-plan-audit-skill.md` | 完了（2026-07-05。/addf-plan-audit 新設・migrate ワンショット統合。ドッグフーディング検出10件は処置提案としてオーナー判断待ち） |
| **1** | 37 | `.claude/addf/plans-add/0037-addf-directory-consolidation.md` | 完了（フェーズ1〜3・v0.6.0 メジャーリリース 2026-07-06。オーナー同席の単一セッションで完走） |
| 3 | 38 | `.claude/addf/plans-add/0038-speculation-fitness.md` | 完了（2026-07-05。投機適性3区分・Plan 化フォールバック・one-shot 定義の guides 単一ソース化・窓検出（手順 1.8）・reconcile check に pending_count 追加） |
| 5 | 39 | `.claude/addf/plans-add/0039-docs-website.md` | 一部完了（フェーズ1=addf-doc-review-agent 逆輸入・フェーズ2=VitePressサイト骨格 完了 2026-07-10。フェーズ3=GitHub Pages公開はオーナー操作待ち） |
| 4 | 40 | `.claude/addf/plans-add/0040-ccchain-optin.md` | 一部完了（フェーズ1・2 完了 2026-07-14。フェーズ1: オーナー対話セッションで直接着手指示・Q5解消。ADDF本体へccchain導入、`.ccchain.conf`を実運用コマンドで調整〔git reset --hard等の破壊的操作をask化・bash/uv run/gh読み取り系をallow化〕、settings.local.jsonにPreToolUse(Bash)フック配線。フェーズ2: `[ccchain]`オプトイン・`sync-ccchain.py`・`optional/ccchain/`テンプレート・`/addf-lint`セクション13・テスト23件を新設。フェーズ1/2の配線先は意図的に分離〔統合はフェーズ4〕。フェーズ3〔ガイド・migrate統合〕は未着手） |
| **2** | 41 | `.claude/addf/plans-add/0041-context-exhaustion-loop-wall.md` | 一部完了（フェーズ1・2 完了 2026-07-06。実地検証は別サイクル。止まらない教義＋compaction 耐性のタスク運びを配線） |
| 3 | 42 | `.claude/addf/plans-add/0042-precompact-transcript-archive.md` | 完了（2026-07-07。PreCompact フック・[transcript-archive] 設定・復元手順 knowhow・36テスト。code-review Warning 3件と Suggestion 4件、doc-review 指摘を全反映） |
| 3 | 43 | `.claude/addf/plans-add/0043-security-recovery.md` | 完了（2026-07-07。4項目とも最小実装: 項目1 deny 11パターン・項目2 addf-init preview・項目3 destructive-git-guard フック 13テスト・項目4 パストラバーサル Test 20 x3。事後観測方式で段階調整） |
| 5 | 44 | `.claude/addf/plans-add/0044-experience-strategy-decision.md` | 完了（2026-07-10。実測に基づき案A〔現行分離方式〕採用・addf-experience を「参照の自己整合性・書式健全性検証」に再定義） |
| 6 | 45 | `.claude/addf/plans-add/0045-language-specific-rules.md` | 完了（2026-07-10。EnumaElish・wasurenainder を実測し肥大化の実害ゼロを確認、意図的な不採用として決定） |
| 3 | 46 | `.claude/addf/plans-add/0046-delegation-prohibition-boundary.md` | 完了（2026-07-07。DelegationRules.md 新設・境界緩和・lint-template-sync 検査境界明文化＋Test 4b） |
| 3 | 47 | `.claude/addf/plans-add/0047-change-route-criteria-and-followup-granularity.md` | 完了（2026-07-07。変更ルート判断表新設・運用ルール7 主題軸化・同期ペア3面通過・doc-review Warning 3件と Suggestion 2件全反映） |
| 6 | 48 | `.claude/addf/plans-add/0048-review-agent-emotional-feedback.md`（検討スタブ） | 要確認（質問投下済み・Q6 2026-07-10）。着手トリガーは満たすが、美学レイヤーの設計判断が「良い塩梅」を要する性質のため、無人ループでの独断実装を避け小規模プロトタイプの進め方をオーナーに確認中 |
| 4 | 49 | `.claude/addf/plans-add/0049-model-allocation-policy.md` | 完了（2026-07-07 worktree で実装 → 2026-07-10 main へ回収・採番を 0048→0049 に変更。ダウンストリーム wasurenainder 実運用構想の逆輸入。addf-implementer エージェント新設・model-allocation.md ガイド・CLAUDE.repo.example.md プレースホルダ節） |
| 7 | 50 | `.claude/addf/plans-add/0050-readme-docs-table-gap.md` | 完了（2026-07-10。README.md/README.en.md に skills.md・model-allocation.md の行を追加） |
| 2 | 51 | `.claude/addf/plans-add/0051-quality-improvement-worktree-isolation-and-knowhow-links.md` | 完了（2026-07-10。CLAUDE.md「並列実装方針」に worktree 隔離破り〔cd 永続〕の注意事項を追記、knowhow `worktree-isolation-cd-persistence.md` 新設、`cron-loop-worktree-race.md` との相互参照、knowhow 一方向リンク12件+新設分2件＝計14件を解消。doc-review 指摘の重複記載を修正済み） |
| **2** | 52 | `.claude/addf/plans-add/0052-migrate-runtime-hardening.md` | 完了（2026-07-11。Issue #26〔wardrobe-test での v0.6.1 移行実測レポート〕回収。項目1〜4を全て実装（GUIバイナリtimeoutガード・guides混在確認・gitignore旧位置パターン検知・Test15 SKIPフォールバック）。3体レビュー（code-review Critical1/Warning2/Low1・doc-review Warning3・contribution-agent Medium2/Low1）を全て反映。run-all.sh・/addf-lint 全通過） |
| 2 | 53 | `.claude/addf/plans-add/0053-changelog-and-skill-listing-completeness.md` | 完了（2026-07-11。別セッションが着手・本セッションが引き継いで完走。CHANGELOG記載漏れ〔Plan 0030・0031・0032・0035・0036・0038・0039・0041・0044・0049・0051・0052〕の回収・READMEスキル一覧の掲載漏れ〔addf-plan-audit〕解消・lint-template-sync.py ペア8新設。3体レビュー指摘計5件を反映、うち1件はPlan 0054として切り出し） |
| **1** | 54 | `.claude/addf/plans-add/0054-settings-self-write-protection.md`（検討スタブ） | 未着手（2026-07-11 起票。Plan 0053 の doc-review で Plan 0026 の [Critical]「settings.json/hooks 自己書き換え保護」が Plan 0043 で明示的にスコープ外とされたまま独立 Plan 未作成で放置されていたことが判明。Progress 運用ルール7〔主題外Critical最優先切り出し〕に従い起票。設計方向性はオーナー判断待ち） |
| 3 | 56 | `.claude/addf/plans-add/0056-plan-genealogy-tree.md`（検討スタブ） | 未着手（2026-07-16 起票。オーナー発案。未完了タスクロードマップを積み上げ式から系統樹表現へ — 剪定・派生・復活をエッジ型で一級データ化し、TODO テーブルを真実源としたまま Mermaid 派生ビューを生成する構想。クリティカルパス〔オーナー判断待ちの可視化〕はオーナー好感触あり。エッジ記録先・初期スコープはオーナー判断待ち） |
| 3 | 57 | `.claude/addf/plans-add/0057-commit-baseline-profiles.md`（検討スタブ） | 未着手（2026-07-16 起票。オーナー発案。`.gitignore` ADDF ブロック〔何をコミットし何を ignore するか〕を Behavior.toml のプロファイル宣言〔upstream/team/personal 想定〕で切り替える構想。きっかけは .exp.md のコミット要否が開発形態で変わる整理と Claude Code Web 可搬性。exp 先行切り出しはせず1本で扱うことをオーナー決定済み。プロファイル粒度・デフォルト値はオーナー判断待ち） |
| **1** | 58 | `.claude/addf/plans-add/0058-dashboard-html-review-ui.md` | 一部完了（フェーズA・B・C 完了 2026-07-16。A: ダッシュボード実装・オーナー実物確認済み。B: crit ドッグフーディング一周実測。C: アンカーコメント UI〔Layout.vue＋/api/comments・DashboardComments.json・crit 集約・ブートシーケンス 1.7・折りたたみ構文2系統〕、3体レビュー Critical 2〔crit 型ガード=2体独立指摘・details 閉じ忘れフォールバック〕/High 1〔API 直列化〕等を反映、テスト17件全通過。残: オーナーのブラウザ動線確認のみ〔owner_feedback: 待ち〕。README 記載は Plan 0065 に切り出し） |
| 4 | 59 | `.claude/addf/plans-add/0059-downstream-test-environment-compat.md` | 未着手（2026-07-16 起票。Issue #30・#31 回収 — upstream 前提テストの SKIP 化と書式受理） |
| 4 | 60 | `.claude/addf/plans-add/0060-migrate-paths-lookbehind-boundary.md` | 未着手（2026-07-16 起票。Issue #33 回収 — migrate-paths / lint-residual-paths の lookbehind 境界導入） |
| 5 | 61 | `.claude/addf/plans-add/0061-test-architecture-guide.md` | 未着手（2026-07-16 起票。Issue #32・#6 回収 — テスト設計ガイド新設） |
| 5 | 62 | `.claude/addf/plans-add/0062-speculation-feedback-proposals.md` | 未着手（2026-07-16 起票。Issue #24・#25 回収 — 投機サイクル完走フィードバックの未回収提案棚卸し） |
| 6 | 63 | `.claude/addf/plans-add/0063-feedback-md-format.md` | 未着手（2026-07-16 起票。Issue #5 回収 — Feedback.md 記入フォーマットと knowhow 振り分け基準） |
| 6 | 64 | `.claude/addf/plans-add/0064-plan-numbering-self-cleaning.md`（検討スタブ） | 未着手（2026-07-16 起票。Issue #7 回収 — Plan 採番・残存コメントの自浄機構） |
| 7 | 65 | `.claude/addf/plans-add/0065-readme-dashboard-gap.md` | 未着手（2026-07-16 起票。Plan 0058 フェーズC の doc-review 検出 — README にローカルダッシュボード機能の記載が無い。Plan 0050 と同種の乖離回収） |
| 2 | 55 | `.claude/addf/plans-add/0055-downstream-migration-feedback-taskbar.md` | 完了（2026-07-14。GitHub Issue #27〔addf-migrate自己点検〕・#28〔*.addf.md除外規則の説明強化〕・#29〔downstreamで必ずFAILするテストの動的アサーション化〕をtaskbar.fmからのフィードバックとして回収。3体レビュー（code-review Critical1件・doc-review Critical1件等）を反映、Critical指摘の反映過程でテストヘルパーのstrip_fences漏れという実バグも検出・修正。run-all.sh・/addf-lint 全通過） |

オーナーリクエスト:
タスクが無くなったら以下に取り組んでください
- プロジェクトの品質を向上させる計画を追加する

---

## アーカイブ

| Phase | 計画ファイル | 状態 |
|---|---|---|
