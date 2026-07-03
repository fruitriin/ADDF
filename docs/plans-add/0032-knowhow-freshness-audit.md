# Plan 0032: knowhow 鮮度の棚卸し（🟡 記事の一括再検証）

## 実装状況: 未着手

> **粗々の起票**: 設計の方向性と未決事項を出す段階。実装詳細は着手時に詰める。

## 目的

`docs/knowhow/INDEX.addf.md` で 🟡（last_verified が古い）となっている記事を
`/addf-knowhow-revise` で一括再検証し、知見ベースの信頼性を回復する。

## 背景

- 2026-07-03 時点で INDEX.addf.md の 🟡 記事は7件（いずれも last_verified が 2026-03）:
  - `claude-md-at-mention.md`（@メンション展開）
  - `ignore-file-strategy.md`（ignore ファイル戦略）
  - `permission-settings-pattern.md`（権限3パターン分類）
  - `pretooluse-block-with-rationale.md`（根拠提示型ブロック）
  - `skill-design-patterns.md`（スキル設計パターン）
  - `existing-project-install-pattern.md`（既存プロジェクト導入）
  - `release-skill-separation.md`（リリーススキル責務分割）
- この間にリポジトリは大きく動いている（Plan 0016〜0029: リネーム・optional 機構・lint 群・
  権限監査の運用実績）。特に `permission-settings-pattern.md` は 0026 レビューで
  「mv/rm/chmod を破壊的として除外しているのに cp は無制限で基準が不統一」と本文の前提に
  疑義が付いており、再検証の必要性が具体化している
- 0026 の Info 指摘「knowhow の残る陳腐化は /addf-knowhow-revise の定期棚卸し対象（継続運用）」の
  初回実施を、計画として明示的に確保する

## 進め方の骨子

1. `/addf-knowhow-index reindex` で鮮度レポートを最新化する
2. 🟡 各記事に `/addf-knowhow-revise` を適用する:
   - 本文の事実主張を現在のリポジトリ・Claude Code の挙動と突合する
   - 正しい → `last_verified` 更新（🟢 復帰）
   - 一部誤り → 訂正 + 訂正履歴を記録
   - 役目を終えた → superseded / retired 遷移（📜 プレフィックス、`/addf-knowhow-network` の作法）
3. 訂正が相互リンク・INDEX サマリに波及する場合は `/addf-knowhow-network` で整合を取る
4. 棚卸しで得た「陳腐化しやすい記述パターン」があれば knowhow 化する
   （例: 外部ツールの挙動依存は日付とバージョンを併記する等）

## 影響範囲

- `docs/knowhow/ADDF/*.md`（🟡 7件の本文・frontmatter）
- `docs/knowhow/INDEX.addf.md`（再生成）

## 未決事項（粗々ゆえ）

- 7件を1タスクでやるか、2〜3件ずつ分割するか（1記事の検証が重い場合は分割）
- 検証で「Claude Code 本体の挙動確認」が必要な項目（@メンション展開等）の確認手段
  （実験用ミニセッション / ドキュメント照合）
- 定期棚卸しの周期を仕組み化するか（addf-lint セクション7が鮮度警告を出す現行運用で
  十分かの評価を含む）

## 完了条件（暫定）

- INDEX.addf.md の 🟡 記事が 🟢（再検証済み）または 📜（superseded/retired）に遷移している
- 訂正した記事に訂正履歴が残っている
- `/addf-knowhow-index reindex` 後の INDEX が整合している（addf-lint セクション5・7・8 の観点）

## 関連

- `/addf-knowhow-revise` / `/addf-knowhow-network` / `/addf-knowhow-index` — 本 Plan の実行手段
- Plan 0018（knowhow-expiry）— 鮮度機構そのものの導入計画
- Plan 0026 — Info 指摘「knowhow の残る陳腐化」の出典
