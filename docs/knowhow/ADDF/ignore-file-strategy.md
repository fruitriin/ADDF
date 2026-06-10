---
title: ignore ファイルの運用戦略
created: 2026-03-18
last_verified: 2026-03-18
depends_on: []
status: active
---

# ignore ファイルの運用戦略

## 発見した知見

### 3種類の ignore の役割

| ファイル | 目的 | スコープ | コミット |
|---|---|---|---|
| `.gitignore` | git に追跡させないファイル | 全コントリビューター共有 | する |
| `.claudeignore` | Claude Code に見せないファイル | 全コントリビューター共有 | する |
| `.git/info/exclude` | ローカル専用の git 除外 | 個人環境のみ | しない |

### Claude Code と .gitignore の関係
- `.gitignore` 対象ファイルでも、パスを直接指定した Read/Edit は**ブロックされない**
- `.gitignore` が影響するのは Glob/Grep の検索対象と `@` ファイルピッカーの表示
- `respectGitignore` 設定で制御可能（デフォルト: `true`）

### respectGitignore の設定

```json
{
  "respectGitignore": false
}
```

- **保存先の優先順位**: `.claude/settings.local.json`（ローカル） > `.claude/settings.json`（プロジェクト） > `~/.claude/settings.json`（グローバル）
- `/config` の filepicker から設定すると、**マシングローバル**（`~/.claude/projects/` 配下のプロジェクト設定）に保存される
- プロジェクト全体で共有したい場合は `.claude/settings.json` に書く

## プロジェクトへの適用

### .gitignore に書くもの（git 除外、Claude はアクセス可能）
- `CLAUDE.local.md` — ローカル環境固有の CLAUDE 設定
- `CLAUDE.repo.md` — コミットしないが @展開で読まれる設定
- `.claude/skills/*.exp.md` — スキルの経験蓄積ファイル
- ビルド成果物、`node_modules/` 等

### .claudeignore に書くもの（Claude に見せない）
- 巨大なデータファイル、ログ
- 機密情報（credentials 等）
- Claude のコンテキストを汚すだけで参照不要なファイル

### .git/info/exclude に書くもの（個人ローカル）
- 個人のエディタ設定、デバッグ用スクリプト
- 一時的な実験ファイル
- `.gitignore` を汚したくない個人的な除外

## 注意点・制約
- `.claudeignore` は `.gitignore` と同じ書式
- `.git/info/exclude` は clone 時に他の人には見えない
- `respectGitignore: false` にすると**全ての** gitignore 対象が Glob/Grep に出るため、`node_modules/` 等も検索対象になる

## 参照
- Claude Code 設定ドキュメント
- `git help gitignore`
