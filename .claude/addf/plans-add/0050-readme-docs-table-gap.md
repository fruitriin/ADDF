# Plan 0050: README.md「ドキュメント」テーブルの掲載漏れ修正（Plan 0039 doc-review 由来）

## 実装状況: 未着手

> 出典: Plan 0039 フェーズ2（VitePress サイト骨格）の doc-review Warning。VitePress サイトの
> サイドバー（`.claude/addf/guides/` 全10ファイルを機械的に掲載）と突き合わせたところ、
> README.md（および README.en.md）の「ドキュメント」テーブルが2件不足していることが判明した。
> Plan 0039 の主題（VitePress サイト構築）とは無関係の既存ドリフトのため、独立 Plan として切り出す
> （Progress.md 運用ルール7「主題から外れるもの→別 Plan に切り出す」）。

## 関連 Plan

- [Plan 0039: ADDF ドキュメント Web](0039-docs-website.md) — 出典。フェーズ2完了時の doc-review で発見

## 目的

README.md / README.en.md の「ドキュメント」テーブルに、既存だが掲載されていない2ガイドへの
リンクを追加し、実際のガイド一覧（`.claude/addf/guides/`）との乖離を解消する。

## 現状の挙動

README.md の「ドキュメント」テーブルは8ガイド（setup / agents / development-process /
migration / speculative-development / pr-format / codex-setup / gui-test-setup）のみを掲載し、
以下の2件が欠落している:

- `.claude/addf/guides/skills.md`（フレームワークスキル一覧。Plan 0037 のディレクトリ集約で
  現在のパスへ移動済み）
- `.claude/addf/guides/model-allocation.md`（モデル配分ガイド。Plan 0049 で新設）

## 変更内容

- README.md の「ドキュメント」テーブルに上記2行を追加する
- README.en.md（英語版）にも対応する行を追加する（lint-template-sync の日英同期ペア対象か要確認）

## 影響範囲

- README.md / README.en.md のみ

## テスト方針

- 手動確認（テーブルの表示・リンク切れがないこと）
- `/addf-lint` の該当同期ペアがあれば通過を確認

## 完了条件

- [ ] README.md に2行追加されている
- [ ] README.en.md に対応する2行が追加されている
- [ ] `bash .claude/addf/tests/run-all.sh` が通過する

## AI 実装時間見積もり

1セッション未満（数分の軽微な修正）
