# Plan 0039: ADDF ドキュメント Web（VitePress）とドキュメントドリフト対策

## 実装状況: 未着手

> 出典: オーナー指示（2026-07-06）。EnumaElish（`~/workspace/EnumaElish`）の VitePress ドキュメントサイトを参考に、ADDF のドキュメント Web を構築する。あわせて EnumaElish で実績のあるドキュメントドリフト対策（`addf-doc-review-agent`）を本体へ逆輸入する。

## 関連 Plan

- [Plan 0037: ADDF ディレクトリ集約](0037-addf-directory-consolidation.md) — `docs/` 明け渡し・`.claude/addf/` 集約で docs 配下の構造が大きく変わる。**本 Plan のサイト構築（フェーズ2以降）は 0037 の後に着手する**（パス張り替えの手戻り防止）。ドリフト対策エージェントの取り込み（フェーズ1）は独立しており先行してよい
- [Plan 0003: 英語ドキュメント](0003-english-docs.md) — 日英2ロケール構成の前提となる既存英訳資産
- [Plan 0040: EnumaElish (ccchain) オプトイン統合](0040-ccchain-optin.md) — 同じく EnumaElish 由来の取り込み。本 Plan はドキュメント基盤、0040 はツール統合で独立

## 目的

1. ADDF の利用者向けドキュメント（セットアップ・ガイド・スキル/エージェントリファレンス）を VitePress で Web 公開し、README 偏重の現状から「読める入口」を作る
2. ドキュメントと実装の乖離（ドリフト）を品質ゲートで検出する仕組みを導入する

## 現状の挙動

- ADDF のドキュメントは `README.md` / `README.en.md` / `docs/guides/`（9本・日本語のみ）/ `docs/project-overview/`（addf-overview 生成物）に分散しており、Web 上の入口がない
- ドキュメントドリフトの検出は lint（テンプレート同期ペア1〜6）でファイル間同期のみカバー。**実装とドキュメントの意味的乖離**（機能追加の記載漏れ・廃止機能の残留・日英乖離）を見る仕組みがない
- 参考実装（EnumaElish）には両方が既にある:
  - VitePress ^1.6.4 / `docs/.vitepress/config.mts` / guide+reference 構成 / root=en + `ja/` ロケール / local search / GitHub Pages（`deploy-docs.yml`: push to main → build → deploy-pages）
  - `.claude/agents/addf-doc-review-agent.md` — 品質ゲート用ドキュメントレビューエージェント。3観点（①実装との乖離 ②モチベーション vs 実装事実の混同 ③日英同期）で検査する。ダウンストリームで独立に生まれた成果物であり、アップストリーム取り込みの好例

## 変更内容（フェーズ）

### フェーズ1: ドキュメントドリフト対策の逆輸入（0037 と独立・先行可）

- **対象**: `.claude/agents/addf-doc-review-agent.md`（新設）、`.claude/templates/ProgressTemplate.addf.md`・`ProgressTemplate.md`（品質ゲートへの組み込み）、`CLAUDE.md` ⇔ addf-init コピーリスト
- EnumaElish 版をベースに汎用化する。EnumaElish 固有の検証手順（`printUsage()` ⇔ `switch command` 突合、`internal/` `cmd/` 参照）は「プロジェクト固有チェックの書き方」の例示に降格し、本体版は汎用観点（①②③）＋「ダウンストリームで固有チェックを追記せよ」の構造にする
- 品質ゲートへの組み込み位置は Progress 運用ルールのステップ5（コードレビュー）と並列、**ドキュメントに触れた変更のときのみ起動**（毎タスク全読みはコスト過剰）
- ダウンストリーム配布対象に含める（addf-init コピーリスト・lint ペア5 の整合を確認する）

### フェーズ2: VitePress サイト骨格（0037 完了後）

- **対象**: `package.json`（新設: vitepress devDependency + docs:dev/build/preview スクリプト）、`docs/.vitepress/config.mts`、`docs/index.md`
- EnumaElish の config.mts を雛形にする。ADDF は日本語が正のため **root=ja / `en/` サブロケール**を第一候補とする（EnumaElish と逆。要オーナー確認）
- 掲載対象: セットアップ（`docs/guides/setup.md` 系）・開発プロセス・スキル/エージェント一覧・マイグレーションガイド。`docs/plans-add/`（開発ログ）と `docs/knowhow/`（内部知見）は**掲載しない**
- `base:` はリポジトリ名に合わせる（GitHub Pages プロジェクトサイト想定）
- `node_modules/` `.vitepress/dist/` `.vitepress/cache/` の .gitignore 追加

### フェーズ3: 公開 CI と既存ガイドの再編

- **対象**: `.github/workflows/deploy-docs.yml`（新設）、`docs/guides/` の各ガイド
- EnumaElish の deploy-docs.yml をほぼ流用（Node 22 / npm ci / upload-pages-artifact / deploy-pages。ADDF は package-lock.json 新設に伴い cache: npm が有効）
- 既存 Plan 0030 の CI（品質ゲート）と workflow を分離したまま並置する
- ガイドの見出し・導線をサイドバー構成に合わせて微調整する（内容の書き直しはしない — ドリフト対策はフェーズ1のエージェントが担う）

### フェーズ4（任意・後続）: 英語ロケールの拡充

- `docs/guides/` の英訳は現状存在しない。README.en.md の水準で主要ガイドのみ英訳し、`en/` ロケールに配置する。全訳はしない（ドリフト表面積が倍になるため、需要が見えるまで最小限）

## 影響範囲

- 新規ファイルが主で既存機能への破壊なし。ただし:
  - addf-init コピーリスト（フェーズ1のエージェント追加）— lint ペア5 対象
  - ProgressTemplate 同期ペア（品質ゲート手順の追記）— lint ペア対象。`/addf-lint` セクション6で確認
  - `package.json` 新設により Node エコシステムがリポジトリに入る（ダウンストリームには配布しない — ADDF 本体のドキュメント基盤）

## テスト方針

- フェーズ1: ドリフト注入 TDD（Feedback.md の教訓に従い、実在した乖離パターン — 例: 実装済み機能の「未実装」注記残留 — を意図的に作ってエージェントが検出することを確認する）
- フェーズ2〜3: `npm run docs:build` がリンク切れなしで通ること（`ignoreDeadLinks` は EnumaElish と異なり**有効化しない**。ドリフト検出の一部としてデッドリンクを拾う）。deploy-docs.yml は push 後に Pages 反映を実地確認

## 破壊的変更の許容範囲

なし（既存ファイルの移動はしない。移動は 0037 の管轄）

## 要オーナー確認

- root ロケールを ja にするか en にするか（提案: ja。ADDF の正文は日本語）
- GitHub Pages の有効化（リポジトリ Settings → Pages → GitHub Actions ソース）はオーナー操作が必要
- フェーズ4（英訳拡充）の要否

## 完了条件

- [ ] addf-doc-review-agent が本体に存在し、ドリフト注入テストで3観点の検出が確認できる
- [ ] `bash .claude/tests/run-all.sh` と `/addf-lint` が全通過（同期ペア・コピーリスト整合を含む）
- [ ] `npm run docs:build` が成功し、GitHub Pages でサイトが閲覧できる <!-- human-judgment -->
- [ ] 品質ゲート手順（ProgressTemplate）にドキュメントレビューの起動条件が明文化されている

## AI 実装時間見積もり

フェーズ1: 1セッション。フェーズ2＋3: 1セッション（0037 完了後）。フェーズ4: 需要確認後に別途
