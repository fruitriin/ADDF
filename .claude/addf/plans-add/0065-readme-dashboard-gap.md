# Plan 0065: README にローカルダッシュボード機能の記載を追加する

## 実装状況: 完了（2026-07-17。README.md / README.en.md の特徴セクションにローカルダッシュボード＋アンカーコメントの項目を追加。v0.7.0 リリース前作業として実施）

> 出典: Plan 0058 フェーズC の doc-review が検出（README.md / README.en.md に
> `npm run dashboard:dev` を含むローカルダッシュボード機能が一切登場しない）。
> Plan 0058 の主題（アンカー UI 実装）から外れるため Progress 運用ルール7 に従い切り出し。
> Plan 0050（README ドキュメントテーブルギャップ）と同種の乖離回収。

## 関連 Plan

- [0058-dashboard-html-review-ui.md](0058-dashboard-html-review-ui.md) — 検出元（フェーズC doc-review Info 指摘）
- [0050-readme-docs-table-gap.md](0050-readme-docs-table-gap.md) — 同種の README 乖離回収の前例

## 目的

Plan 0058 で実装したローカルダッシュボード（生成・閲覧・アンカーコメント）が
README 系に記載されておらず、新規利用者・ダウンストリーム導入者が機能の存在を
発見できない。README の機能一覧・使い方に最小限の記載を追加する。

## 変更内容

- `README.md` / `README.en.md`: 特徴・使い方セクションにローカルダッシュボードの
  項目を追加（`python3 .claude/addf/addfTools/generate-dashboard.py` → 閲覧
  `npm run dashboard:dev`（本体）/ `npx vitepress dev .claude/addf/dashboard`（DS）、
  アンカーコメント → ブートシーケンス 1.7 の流れを2〜3行で）
- 記載粒度は既存の特徴列挙と揃える（詳細はガイドに委ねる）

## 影響範囲

- README.md / README.en.md のみ（lint-template-sync ペア8 はスキルテーブルの検査のため干渉しない）

## テスト方針

- `/addf-lint` 通過（特にペア8）。日英の記載内容一致を目視確認 <!-- human-judgment -->

## 破壊的変更の許容範囲

なし

## AI 実装時間見積もり

1サイクル未満（軽量ドキュメントタスク）
