# ADDF Release — アップストリームリリース設定

> このファイルは ADDF 本体（upstream）のリリース時に `/addf-release` が参照する。
> ダウンストリームプロジェクトでは使用しない。
> 各セクションは `/addf-release` スキルの対応する Phase から呼び出される。

## プレリリースチェック

1. `bash .claude/tests/run-all.sh` が全て通過すること
2. `/addf-lint` が全チェック通過すること
3. `docs/plans-add/TODO.addf.md` に未完了の Critical タスクがないこと

## バージョン更新対象ファイル

| ファイル | 更新内容 |
|---|---|
| `.claude/addf-lock.json` | `version`, `ref`（`vX.Y.Z` タグ名）, `updated_at` を更新 |
| `.claude/ADDF-CHANGELOG.md` | 新バージョンのエントリを先頭に追加 |

> **`ref` はタグ名であってコミットハッシュではない**: lock ファイルはリリースコミット自身に
> 含まれるため、そのコミットのハッシュを lock に書くことは自己参照で原理的に不可能
> （v0.2.0 / v0.3.0 で実在しないハッシュが記録される事故が実際に起きた）。
> タグ名なら「lock 更新 → コミット → タグ付け」の順で矛盾なく一致させられる。

## チェンジログの書式

Keep a Changelog 形式（https://keepachangelog.com/）に準拠。日本語で記述:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### 追加
- 新機能の説明

### 変更
- 既存機能の変更

### 修正
- バグ修正

### 削除
- 削除された機能
```

## Publish 手順

1. `addf-lock.json` を更新: `version` を `X.Y.Z`、`ref` を `vX.Y.Z`、`updated_at` を今日の日付にする
2. リリースコミットを作成: `[リリース] vX.Y.Z`（lock 更新を含める）
3. タグを作成: `git tag vX.Y.Z`（`ref` に書いたタグ名と完全一致させる）
4. push: `git push && git push --tags`
5. GitHub Release を作成: `gh release create vX.Y.Z --generate-notes` を提案

## リリース後

- `git tag -l vX.Y.Z` でタグが存在し、`addf-lock.json` の `ref` と一致していることを確認
- `git ls-remote --tags origin vX.Y.Z` でタグが push されていることを確認
- ダウンストリームプロジェクトが `/addf-migrate` で新バージョンを取得できることを検証（任意）
