# Plan: addf-lint にテンプレート同期チェックを追加

## Context

同期が必要なファイルペアの手動同期忘れが3度再発している（Feedback.md 改善アクション参照）:

1. `CLAUDE.md` ⇔ `AGENTS.md`（ブートシーケンス） — Plan 0012 で発見
2. `ProgressTemplate.addf.md` ⇔ 運用中 `Progress.md`（運用ルール） — Plan 0020 で発見
3. `ProgressTemplate.addf.md` ⇔ `ProgressTemplate.md`（ダウンストリーム版） — Plan 0019 で発見（0020/0016/0017 の3プラン分が未同期だった）
4. `CLAUDE.md` ⇔ `docs/guides/development-process.md`（ブートシーケンス概要） — Plan 0017 で発見

## 設計

`addf-lint` に「同期チェック」セクションを追加する。完全一致比較ではなく、**構造の対応**を検証する:

- `ProgressTemplate.addf.md` と `ProgressTemplate.md`: 運用ルールのステップ番号・見出し（3.5、4〜15）が双方に存在するか。既知の意図的差分（ADDF テストランナー行・テンプレート自己参照パス）はホワイトリスト化
- `ProgressTemplate.addf.md` と運用中 `Progress.md`: 「## 運用ルール」セクションのテキストが一致するか（タスクセクションは比較対象外）
- `CLAUDE.md` と `AGENTS.md`: ブートシーケンスの手順数（1, 1.5, 1.6, 2〜5）が対応しているか
- `CLAUDE.md` と `development-process.md`: ブートシーケンス概要の手順数が対応しているか

不一致を検出したら WARNING で報告し、どちらが新しいか（git log）をヒントとして併記する。

## 変更対象ファイル

| ファイル | 変更 |
|---|---|
| `.claude/commands/addf-lint.md` | 同期チェックセクション追加 |
| `.claude/tests/` | 同期チェックの自動テスト（可能なら） |

## 検証

1. 意図的に ProgressTemplate.md の1ステップを欠落させ、WARNING が出ることを確認
2. 意図的差分（ADDF テストランナー行）が誤検出されないことを確認
