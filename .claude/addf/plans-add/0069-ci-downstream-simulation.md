# Plan 0069: CI downstream 模擬実行 — hook テスト群の DS 対応化と模擬ジョブ（検討スタブ）

## 実装状況: 未着手

owner_feedback: 不要
edge: derived-from 0068

## 関連 Plan

- [0068-residual-path-scheme-detection.md](0068-residual-path-scheme-detection.md) — 切り出し元（項目4 を実測評価の結果、規模超過で分離）
- [0059-downstream-test-environment-compat.md](0059-downstream-test-environment-compat.md) — 原案（Issue #31 提案3）

> 出典: Plan 0068 実装時の実測評価。addf-init 相当のコピーで DS 環境を合成して
> run-all.sh を実行したところ、hook テスト群7スイート（destructive-git-guard 0/13・
> pre-compact-archive 9/25・context-reminder 20/24 ほか）が upstream 特有の
> 実配線・環境前提で FAIL することが判明。「upstream 前提の暗黙仮定」欠陥クラスの
> CI 機械検出には、まず hook テスト群の DS 対応化が必要。

## 分かっていること

- 必要な作業は3層: (1) 各 hook テストの DS 対応化 or SKIP 化（7スイート）、
  (2) 合成 DS 生成の共通ヘルパ（`.github/scripts/make-fake-downstream.sh` 相当 —
  test-template-sync.sh の make_fake_downstream_project と統合可能性あり）、
  (3) `.github/workflows/test.yml` への downstream 模擬ジョブ追加
- lint 系（template-sync ペア群・genealogy・residual-paths）は既に合成 DS テストで
  カバー済み — 残る穴は hook テスト群のみ

## 着手のトリガー

- 次に downstream 起因のテスト誤 FAIL 報告（Issue）が来たとき、または
  リリース前の品質強化サイクルで余力があるとき
