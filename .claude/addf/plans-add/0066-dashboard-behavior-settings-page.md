# Plan 0066: ダッシュボードに ADDF 設定（Behavior.toml）ページを追加する

## 実装状況: 未着手

owner_feedback: 不要

> 出典: オーナー発案（2026-07-16 対話セッション — Plan 0058 フェーズC 完了直後）。
> 「ADDF の設定（Behavior.toml）と取りうる設定の有効値をダッシュボードのページに
> 追加したい」。オーナー指示により Plan 0058 に含めず別 Plan として起票。

## 関連 Plan

- [0058-dashboard-html-review-ui.md](0058-dashboard-html-review-ui.md) — 追加先のダッシュボード本体（生成器・ページ構成・エスケープ規約はここが前提）

## 目的

`.claude/addf/Behavior.toml` の現在値と「各キーが取りうる有効値・意味」をダッシュボードの
1ページとして俯瞰できるようにする。現状、有効値は Behavior.toml 内のコメント・各機能の
ガイド・スキル定義に分散しており、設定を変えるときに横断参照が必要。

## 分かっていること

- 現在の Behavior.toml は 81行・セクションは `[gui-test]` `[ccchain]` `[speculation]`
  `[transcript-archive]` `[context-reminder]`（+ サブテーブル）等。有効値の説明は
  行末コメントに書かれているものと、ガイド側にしかないものが混在する
- `generate-dashboard.py` は stdlib のみ・Python 3.9 でも動く制約（決定A）。
  **tomllib は 3.11+** のため、TOML パースは (a) `tomllib` があれば使い・無ければ
  ページ生成をスキップ（注記表示）するフェイルセーフ、(b) 表示目的に限定した簡易パース
  （`bash-toml-parse-pitfalls.md` の8類型に注意）、のどちらかを選ぶ
- **有効値の単一ソースをどこに置くかが本 Plan の核心**。候補:
  - 案1: Behavior.toml の行末コメントを正とし、生成器はコメントごと表示する
    （新しい同期ペアを作らない。表現力は低い）
  - 案2: 有効値スキーマ定義（TOML/JSON）を addfTools に新設し、lint-toml がそれで
    検証・ダッシュボードがそれを表示する（表現力は高いが、**新しい同期ペアが生まれる
    ため lint 追加とセットで行う** — Feedback.md の改善アクション「新たな同期ペアが
    生まれたら lint にペアを追加」に従う）
- Plan 0057（コミットベースラインのプロファイル化）が Behavior.toml に `profile` キーを
  追加する構想を持つ — 実装順によっては有効値定義の置き場を共有できる（案2 の
  スキーマ定義は 0057 の lint 期待値表〔案a〕と同居させられる可能性）

## 変更内容（案 — Plan 詰めで確定）

- `generate-dashboard.py` に settings ページ（4ページ目）生成を追加:
  現在値テーブル（セクション別）＋ 各キーの有効値・意味 ＋ Behavior.toml 本体への参照
- `.vitepress/config.mts` のサイドバーに「設定」を追加
- テスト: 合成 Behavior.toml をサンドボックスに置き、ページ生成・tomllib 不在時の
  スキップ（欠如 = SKIP）を検証

## テスト方針

- `bash .claude/addf/tests/tools/test-generate-dashboard.sh` の拡張＋ run-all.sh 全通過
- Python 3.9（tomllib 無し）相当の経路でページがスキップされ生成全体は成功することを検証

## 破壊的変更の許容範囲

なし（ページ追加のみ。Behavior.toml 本体の書式変更はしない — 案2 を採る場合も
スキーマ定義は別ファイル）

## AI 実装時間見積もり

1サイクル（案1 なら半サイクル。案2 は lint 追加を含むため1サイクル強）
