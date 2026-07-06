# Plan 0032: knowhow 鮮度の棚卸し（🟡 記事の一括再検証）

## 実装状況: 完了（2026-07-06）

### 実装記録

初回の鮮度棚卸しを実施。INDEX 上の 🟡 は7件だったが、うち `ignore-file-strategy.md` は
frontmatter が既に最新（2026-07-02）で INDEX の日付だけ古かった（reindex 未実行）。実質の
再検証は6件。判定と根拠は以下:

| 記事 | 判定 | 根拠 |
|---|---|---|
| `claude-md-at-mention.md` | 妥当（🟢 復帰） | @展開・クオート除外・ネスト展開の主張が現行 CLAUDE.md → CLAUDE.repo.md → CLAUDE.repo.example.md のネスト展開で機能している |
| `ignore-file-strategy.md` | 妥当（🟢 復帰） | frontmatter が 2026-07-02 で既に更新済み。INDEX のみ再構築で 🟢 に |
| `permission-settings-pattern.md` | **一部誤り** → 訂正 | 「破壊的操作の除外基準」が cp（allow）と mv/rm/chmod（除外）で不統一だった（Plan 0026 レビュー指摘）。「破壊が主目的か副作用か」の分類に書き換え。例示 settings.json も現状追従（`mktemp` / `git clone` / `git -C` / `* --help` 等） |
| `pretooluse-block-with-rationale.md` | 妥当（🟢 復帰） | 根拠提示型ブロック・CLAUDE_CODE_TMPDIR・横展開パターンいずれも現行と整合。実装例の check-tmp.py は SDIT 側の話で本リポジトリに実物なしなのは記事の記述どおり |
| `skill-design-patterns.md` | **一部誤り** → 訂正 | 「改善の余地: 計測フックの導入」を未実装扱いしていたが `skill-usage-log.sh` が既に配線済み → 取消線で歴史保管。ADDF 独自パターン節（検出＝スクリプト・解釈＝エージェント／exit3値／同期契約 lint 化／オプトイン式）を追記 |
| `existing-project-install-pattern.md` | **一部誤り** → 訂正 | 「外部起動の判定」に「部分導入プロジェクト」ケースが欠けていた。カテゴリ1 に「`*.addf.md` 除外原則」も未反映。両方を追記 |
| `release-skill-separation.md` | 妥当（🟢 復帰） | スキル=ルーター、設定/exp=手順定義の3層構造が現行 `addf-release.md` と整合 |

副次成果:
- 新 knowhow `ADDF/knowhow-obsolescence-patterns.md` を1本作成（Plan 0032 の骨子 4「陳腐化しやすい記述パターン」）。
  未実装リスト・現物埋め込み例示・閉じた分岐図の3パターンと逃がし方を記録
- INDEX.addf.md 再構築（全 18 記事 🟢、`.knowhow-obsolescence-patterns.md` 追加）
- `sync-lint-design.md` に新 knowhow への双方向リンクを追加

Plan 化提案（深追いせず本 Plan ではやらない）:
- `permission-settings-pattern.md` の「cp の上書き副作用まで禁止したい場合の deny ルール設計」は
  独立 Plan にする価値がある。運用ノイズ増と実害率のトレードオフが論点。TODO への追加はしない
  （オーナー判断で起案可否を決めるためここに提案として残すのみ）

> **粗々の起票**: 設計の方向性と未決事項を出す段階。実装詳細は着手時に詰める。

## 目的

`.claude/addf/knowhow/INDEX.addf.md` で 🟡（last_verified が古い）となっている記事を
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

- `.claude/addf/knowhow/ADDF/*.md`（🟡 7件の本文・frontmatter）
- `.claude/addf/knowhow/INDEX.addf.md`（再生成）

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
