# Plan 0060: migrate-paths / lint-residual-paths の誤検知根本対処 — lookbehind 境界の導入（Issue #33 回収）

## 実装状況: 一部完了（実装完了 2026-07-17 — 残は Issue #33 返信のみ〔オーナー確認待ち〕。addf-implementer worktree 実装 → main へ cherry-pick。compile_pattern に lookbehind 境界〔1文字境界維持＋(?<![A-Za-z0-9]/)＋自リポジトリ絶対パスの正 lookbehind 例外〕を両ファイル同期導入・Test 13.5〔12件・ドリフト注入 TDD〕。既知の限界〔別名 clone 先の絶対パス〕は docstring 明記で受容。run-all 全通過）

edge: absorbed-into 0068

> 出典: GitHub Issue #33（外部 URL・他プロジェクトパスへの lint/rewrite 誤検知 — 下流で
> 根本対処を実装・テスト済みの上流反映提案。次回 `/addf-migrate` で下流修正が上書き消失する
> リスクがあるため早期反映を希望）

## 関連 Plan

- [Plan 0052: migrate ランタイム強化](0052-migrate-runtime-hardening.md) — 同じ migrate-paths 系の残存パス検査を強化した先行 Plan（gitignore 旧位置パターン検知）
- [Plan 0055: taskbar.fm 移行フィードバック回収](0055-downstream-migration-feedback-taskbar.md) — 同系のダウンストリーム実測フィードバック回収の前例
- [Plan 0068: compile_pattern の URL スキーム検出設計と同期契約 lint 化](0068-residual-path-scheme-detection.md) — 本 Plan の Stage 2 レビュー残件（basename 誤検知の根治設計・同期契約 lint 化・CI downstream 模擬）の切り出し先

## 目的

`migrate-paths.py` / `lint-residual-paths.py` の `compile_pattern()` が外部 URL
（例: `https://supabase.com/docs/guides/...`）や他プロジェクトへの絶対パス言及を <!-- residual-path: allow -->
旧パス残存として誤検知しないようにし、rewrite が外部 URL を書き換えて壊す潜在バグを塞ぐ。

## 現状の挙動

- 旧パス文字列（`docs/guides` 等）を境界チェック付き単純マッチで検出するため、downstream で <!-- residual-path: allow -->
  3パターンの誤検知が実測されている（外部 URL 20件・他プロジェクト言及 3件・自己言及）
- 行マーカー `residual-path: allow` で凌げるが、配布物（Supabase 公式スキル等）は次回同期で
  上書きされ再発する
- lint と rewrite がパターンを共有しているため、rewrite 実行時に外部 URL を
  `https://supabase.com/.claude/addf/guides/x` のように書き換えて壊す潜在バグがある

## 変更内容（項目・フェーズ）

### 項目1: compile_pattern() の lookbehind 境界導入

- **対象**: `.claude/addf/addfTools/migrate-paths.py`・`lint-residual-paths.py`（両ファイル、同期契約維持）
- Issue #33 に下流実装済みのパターンが提示されている:
  - 直前が「英数字 + /」= 別パス階層の内部（外部 URL・他プロジェクト絶対パス）→ 検出しない
  - 例外: 直前が「/ + 自リポジトリのディレクトリ名 + /」→ 検出する（自リポジトリへの絶対パス参照は本物の残存でありうる）
  - 既知の限界（別名 clone された複製への絶対パス参照は検出できない）を docstring に明記する
- 自己言及パターン（説明文中のリテラル記載）は従来どおり行マーカー機構で対処（設計変更なし）

### 項目2: 回帰テストの取り込み

- **対象**: `.claude/addf/tests/tools/test-migrate-paths.sh`
- 下流の Test 13.5 相当を追加:
  - 外部 URL・他プロジェクトパスを lint が検出しない（exit 0）
  - `./` 相対の本物の残存は引き続き検出する（exit 1）
  - 自リポジトリ絶対パスの残存も検出する（exit 1）
  - rewrite が外部 URL を書き換えず（無傷）、本物の参照は書き換える

## 影響範囲

- `addfTools/` 2ファイル＋テスト1ファイル。ダウンストリーム配布対象
- 本 Plan の文書自体が旧パス文字列に言及するため、書き終えるたびに `lint-residual-paths.py` を再実行する（Feedback.md 既録の Plan 0052 教訓）

## テスト方針

- 上記回帰テスト（ドリフト注入型）＋ 既存 `test-migrate-paths.sh` 全体の通過維持
- Issue の教訓「既存テストが通ること ≠ 検出精度の劣化なし」に従い、検出漏れ側
  （自リポジトリ絶対パス）のアサーションを必ず含める

## 破壊的変更の許容範囲

なし（検出対象の縮小は誤検知の除去のみ。検出すべき残存の検出能力は回帰テストで担保）

## 要オーナー確認

なし（下流で実装・テスト・コードレビュー済みのパターンの取り込み）

## 完了条件

- [x] `compile_pattern()` が両ファイルで同一実装になっている（同期契約維持を lint またはテストで確認）
- [x] 回帰テスト（外部 URL 不検出・本物残存の検出・rewrite の外部 URL 無傷）が PASS する（Test 13.5・12件）
- [x] `bash .claude/addf/tests/run-all.sh`・`/addf-lint` 全通過
- [ ] Issue #33 へ対応内容を返信する <!-- human-judgment: 返信文はオーナー確認後に投稿する -->

## AI 実装時間見積もり

1セッション以内
