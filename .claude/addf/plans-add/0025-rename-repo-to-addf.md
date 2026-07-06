# Plan 0025: リポジトリ名を ADDF に変更

## 実装状況: 完了（2026-07-02。フェーズ1は v0.3.0 リリースに同梱、フェーズ3・4はオーナー実施済み、フェーズ5検証済み）

## 目的

GitHub リポジトリ名を `AutomatonDevDriveFramework` → `ADDF` に変更し、全参照を更新する。

## 背景

- 正式名称 "AutomatonDevDrive Framework" は長い。略称 "ADDF" が定着しているため、リポジトリ名も合わせる
- GitHub はリネーム時に旧 URL → 新 URL のリダイレクトを自動設定する
- ただし `raw.githubusercontent.com` のリダイレクト保証が弱く、ダウンストリームの `addf-init` fetch が壊れる可能性がある
- 旧名で新リポジトリを作るとリダイレクトは消える

## 変更対象

### フェーズ 1: リポジトリ内の URL 置換（コミット → push）

GitHub リネーム**前に** main にマージしておく。リネーム直後から新 URL が有効になるようにする。

| ファイル | 行 | 変更内容 |
|---|---|---|
| `README.md:50` | `raw.githubusercontent.com/.../AutomatonDevDriveFramework/...` → `.../ADDF/...` |
| `README.md:52` | `github.com/fruitriin/AutomatonDevDriveFramework` → `.../ADDF` |
| `README.en.md:46` | 同上（raw URL） |
| `README.en.md:48` | 同上（repo URL） |
| `.claude/addf/lock.json:5` | `repository` URL |
| `.claude/commands/addf-init.md:17` | デフォルト URL |
| `.claude/commands/addf-migrate.md:33` | デフォルト URL |
| `.claude/addf/tests/skills/test-addf-init-external.md:23,25` | テスト内の URL |
| `.claude/addf/plans-add/0015-existing-project-install.md:33,35` | 計画内の URL（アーカイブだが正確性のため） |
| `.claude/addf/guides/setup.md:3` | "Use this template" リンク |

### フェーズ 2: テキスト上の名前表記（任意）

「AutomatonDevDrive Framework」という正式名称はそのまま残す。リポジトリ名の変更であって、プロジェクト名の変更ではない。以下のファイルは**変更しない**:

- `README.md:5`, `README.md:133` — タイトルと正式名称の記載
- `README.en.md:1`, `README.en.md:129` — 同上（英語版）
- `AGENTS.md:1` — ヘッダー
- `CLAUDE.repo.example.md` — テンプレート内の名称・哲学の説明
- `.claude/agents/addf-contribution-agent.md` — エージェントの説明文
- `.claude/commands/addf-overview.md` — overview テンプレート
- `.claude/addf/project-overview/INDEX.md` — 概要文
- `.claude/addf/guides/codex-setup.md` — ガイド文

### フェーズ 3: GitHub 上でリネーム実行

1. GitHub Settings → Repository name を `ADDF` に変更
2. 手動操作（オーナーが実行）

### フェーズ 4: ローカル環境の更新

```bash
git remote set-url origin https://github.com/fruitriin/ADDF.git
```

### フェーズ 5: 検証

- [x] `git push` / `git pull` が新 URL で動作する（2026-07-02 確認）
- [x] `raw.githubusercontent.com/fruitriin/ADDF/main/.claude/commands/addf-init.md` がアクセスできる（2026-07-02、HTTP 200 確認）
- [x] 旧 URL `github.com/fruitriin/AutomatonDevDriveFramework` がリダイレクトされる（サンドボックスのプロキシ制約で直接検証不可。GitHub のリネーム時自動リダイレクトの標準挙動に依拠。オーナーのブラウザで随時確認可）
- [x] README のロゴ画像が表示される（2026-07-02、raw URL HTTP 200 確認）

## ダウンストリーム影響

- 既存ダウンストリームの `addf-lock.json` には旧 URL が記録されている
  - GitHub リダイレクトが効いている間は `addf-migrate` が動作する
  - 次回 `addf-migrate` 実行時に新 URL に更新される（`addf-migrate` が lockfile を書き換えるため）
- ダウンストリームが `raw.githubusercontent.com` から `addf-init.md` を fetch する場合、旧 URL でもリダイレクトされる（旧名で新リポジトリを作らない限り）

## リスク

- **低**: 旧名で新リポジトリを作るとリダイレクトが壊れる → 作らないこと
- **低**: ダウンストリームの lockfile 旧 URL → リダイレクトで猶予あり、`addf-migrate` で自動更新
