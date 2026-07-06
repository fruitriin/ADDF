# Plan: addf-lint にテンプレート同期チェックを追加

## 実装状況: 完了（2026-06-10、2026-06-11 遡及確認）

## Context

同期が必要なファイルペアの手動同期忘れが3度再発している（Feedback.md 改善アクション参照）:

1. `CLAUDE.md` ⇔ `AGENTS.md`（ブートシーケンス） — Plan 0012 で発見
2. `ProgressTemplate.addf.md` ⇔ 運用中 `Progress.md`（運用ルール） — Plan 0020 で発見
3. `ProgressTemplate.addf.md` ⇔ `ProgressTemplate.md`（ダウンストリーム版） — Plan 0019 で発見（0020/0016/0017 の3プラン分が未同期だった）
4. `CLAUDE.md` ⇔ `.claude/addf/guides/development-process.md`（ブートシーケンス概要） — Plan 0017 で発見

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
| `.claude/addf/tests/` | 同期チェックの自動テスト（可能なら） |

## 検証

1. 意図的に ProgressTemplate.md の1ステップを欠落させ、WARNING が出ることを確認
2. 意図的差分（ADDF テストランナー行）が誤検出されないことを確認

## 実装結果（2026-06-10 完了）

- `.claude/addf/tools/lint-template-sync.py` を4ペア対応に拡張。exit code 3値（0=OK / 1=ERROR / 2=WARNING のみ）。WARNING に git log 最終更新日ヒントを併記
- `.claude/addf/tests/tools/test-template-sync.sh` 新規作成（6テスト16アサーション、mktemp サンドボックスにドリフトを注入して検証）。`run-all.sh` に自動組み込み
- `.claude/commands/addf-lint.md` セクション6を4ペア表に更新、結果報告を ✓/⚠/✗ の3値化

### 設計からの変更点

- **ペア2は「構造対応」ではなく「正規化テキスト比較」を採用**: 過去3度のドリフト（Plan 0016/0017/0019）は全て既存ステップ内のサブ項目・文言の差分であり、ステップ番号比較では捕捉できないため。意図的差分はホワイトリスト + パス正規化（`.addf.md`→`.md`）で吸収。構造比較は言語が異なるペア3・4（手順番号列の対応）でのみ使用
- **ダウンストリーム配布対応を追加**（コントリビューション検出エージェントの指摘）: ADDF 本体固有ファイル（`.addf.md` 版・AGENTS.md 等）が存在しないペアは SKIP、ペア1は `ProgressTemplate.md` へフォールバック。ダウンストリームで `/addf-lint` を実行しても誤 ERROR にならない

### レビュー対応

Critical/High なし。Warning 2件（git リポジトリ外での誤メッセージ・Counter 未使用による重複行の過小報告）と Suggestion 5件は全てフェーズ内で修正済み。

### 知見

`.claude/addf/knowhow/ADDF/sync-lint-design.md` に記録（検出はツール・解釈と修復はエージェント / サンドボックス注入テスト / SKIP 設計）。
