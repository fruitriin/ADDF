# Plan: 既存プロジェクトへの ADDF 組み込み

## 実装状況: 完了（2026-06-10 確認）

本計画の内容はコミット `b971d97`（2026-03-21「[機能] 既存プロジェクトへの ADDF 導入機能を追加（Phase 15）」）で実装済み。
外部起動セクション・干渉チェック（Phase 2.5）・導入前レビュー（Phase 2.7）・マージ戦略・README コピペプロンプト（日英）が全て `addf-init.md` に反映されている。
実装は計画より進化しており、URL の `https://` 限定検証、既存ファイルからのプロジェクト情報自動推定、既存 CLAUDE.md/AGENTS.md の CLAUDE.repo.md への退避ロジックが追加されている。

TODO 上「未着手」のまま残っていたが、2026-06-10 の突合確認で実装済みと判明し完了化した。
突合で見つかった残差分（コピーリストの鮮度ドリフト等）は `docs/plans-add/0022-addf-init-copylist-refresh.md` に切り出した。

## Context

現在の ADDF 導入フローは GitHub Template からの新規リポジトリ作成が前提。既に開発が進んでいるプロジェクトに ADDF を後から導入する方法がない。

ADDF はスキルの集合ではなく、**CLAUDE.md でプロジェクト全体の開発プロセスを規定するエコシステム**。hooks で任意コマンドを実行し、settings.json で権限を変更し、CLAUDE.md でエージェントの振る舞い全体を支配する。プラグインマーケットプレイスの「1スキルをインストール」とは信頼モデルが根本的に異なる。

## 起動方法の設計（鶏と卵問題の解決）

既存プロジェクトには `addf-init.md` スキルが存在しない。

**解決策: ブートストラッププロンプト + raw URL**

README にコピペ用プロンプトを記載。Claude が raw.githubusercontent.com 経由で `addf-init.md` を取得し、その指示に従って導入する。GitHub の通常の markdown preview は WebFetch で取得できないため、raw URL に誘導する。

### README への記載

```markdown
## 既存プロジェクトへの導入

Claude Code で以下のプロンプトを実行してください:

https://raw.githubusercontent.com/fruitriin/ADDF/main/.claude/commands/addf-init.md を取得し、
このプロジェクトに ADDF フレームワークを導入してください。
ADDF リポジトリ: https://github.com/fruitriin/ADDF
```

### フロー

1. Claude が raw URL から `addf-init.md` を WebFetch
2. `addf-init.md` の「外部起動セクション」を読む
3. ADDF リポジトリを tmp にクローン（ファイルコピー元として必要）
4. tmp のファイル群を参照しながら、ワーキングディレクトリにセットアップ
5. 外部起動 = 必ず「ADDF 利用プロジェクト」（ダウンストリーム）として扱う

### addf-init.md への「外部起動」セクション

スキル冒頭（frontmatter 直後）に記載。Claude が WebFetch 経由で読んだときに:
- ADDF リポジトリの clone が必要であることを認識
- ワーキングディレクトリを導入先とする
- 種別を「ADDF 利用プロジェクト」に固定

## 方針: `/addf-init` の拡張

新スキルは作らない。`/addf-init` に既存プロジェクト対応を追加する。

## 設計

### Phase 0: 外部起動の検出（新設）

addf-init.md の冒頭に「外部起動セクション」を設ける:

```
## 外部からの起動（既存プロジェクトへの導入）

このスキルが tmp ディレクトリやクローン先から読まれている場合:
- 現在のワーキングディレクトリ（ユーザーのプロジェクト）を導入先とする
- プロジェクト種別は「ADDF 利用プロジェクト」（ダウンストリーム）に固定する
- Phase 1 の状態判定から続行する
```

### Phase 1: 状態判定（拡張）

```
.claude/addf-lock.json あり → 導入済み（終了）
.claude/ or CLAUDE.md あり but lock なし → 既存プロジェクト導入モード
何もなし → 新規セットアップモード
```

外部起動の場合は種別を「ADDF 利用プロジェクト」に固定（ヒアリングで選択肢を出さない）。

### Phase 2: 対話的セットアップ

ヒアリング内容:
- プロジェクト名（デフォルト: リポジトリ名）
- ~~プロジェクト種別~~ → 外部起動なら自動で「ADDF 利用プロジェクト」
- ビルド・Lint・テストコマンド（任意）
- コミットログ規約（デフォルト: 日本語）
- ターゲットエージェント（Claude Code / Codex / 両方）

### Phase 2.5: 干渉チェック（新設）

既存プロジェクトのファイル・ディレクトリ構造を検査し、ADDF ファイルとの干渉を報告する:

```
╔══════════════════════════════════════════════╗
║  ADDF 干渉チェック                            ║
╚══════════════════════════════════════════════╝

■ 競合なし（そのままコピー）
  .claude/commands/     — 存在しない（新規作成）
  .claude/agents/       — 存在しない（新規作成）
  .claude/hooks/        — 存在しない（新規作成）
  docs/guides/          — 存在しない（新規作成）

■ マージが必要
  .gitignore            — 既存あり → ADDF エントリを追加
  .claude/settings.json — 既存あり → hooks/permissions をマージ

■ 要確認
  CLAUDE.md             — 既存あり → ADDF ブートシーケンスを先頭に挿入
  CONTRIBUTING.md       — 既存あり → 上書きするかスキップするか選択

■ 新規作成
  TODO.md, CLAUDE.repo.md, .claude/Progress.md, ...
```

### Phase 2.7: 導入前レビュー（セキュリティ）

ADDF が追加する hooks、権限変更、CLAUDE.md への影響を明示表示。ユーザーの承認を得る。

```
ADDF はプロジェクトの開発プロセス全体を規定するフレームワークです。
以下の変更が行われます:

■ Hooks（セッション中に自動実行されるコマンド）
  + SessionStart: reset-turn-count.sh → ターンカウンターリセット
  + UserPromptSubmit: turn-reminder.sh → ターンリマインダー
  + PreToolUse (Skill): skill-usage-log.sh → スキル使用ログ

■ 権限変更（settings.json）
  allow に追加: Read, Edit, Write, Agent, Skill, Bash(git *), ...
  ask に追加: Bash(git push *), Bash(git reset --hard *), ...

■ CLAUDE.md
  + ブートシーケンス（Feedback → TODO → Progress 自動読み込み）
  + 開発プロセス定義（計画駆動、品質ゲート）

続行しますか？
```

### Phase 3: ファイルコピー & マージ

ADDF リポジトリ（tmp）から対象プロジェクトへファイルをコピー。

**カテゴリ1: 無条件コピー**（衝突リスクなし）
- `.claude/commands/addf-*.md` — スキル定義
- `.claude/agents/addf-*.md` — エージェント定義
- `.claude/hooks/*.sh` — フック
- `.claude/templates/` — テンプレート
- `.claude/addfTools/` — ツール群
- `.claude/tests/` — テストスイート
- `.claude/addf-Behavior.toml`
- `.claude/ADDF-CHANGELOG.md`, `.claude/ADDF-Release.addf.md`
- `CLAUDE.repo.example.md`, `CLAUDE.local.example.md`
- `AGENTS.md`
- `.claudeignore`
- `docs/knowhow/ADDF/`, `docs/knowhow/INDEX.addf.md`
- `docs/guides/`

**カテゴリ2: インテリジェントマージ**
- **`.claude/settings.json`**: 既存 hooks/permissions に ADDF エントリをユニオン追加。削除しない。結果を表示して確認
- **`.gitignore`**: ADDF エントリをマーカーブロック付きで追加
  ```
  # --- ADDF Framework (do not remove) ---
  .claude/commands/*.exp.md
  .claude/.turn-count
  .claude/logs/
  CLAUDE.local.md
  CLAUDE.repo.md
  # --- /ADDF Framework ---
  ```
- **`CLAUDE.md`**: 既存なし → ADDF テンプレートをコピー。既存あり → ADDF ブートシーケンスを先頭に挿入、既存内容を保持。マージ結果を表示して確認
- **`CONTRIBUTING.md`**: 既存があればユーザーに確認（上書き / スキップ / マージ）

**カテゴリ3: プロジェクト固有（ダウンストリーム体裁で生成）**
- `CLAUDE.repo.md` — 「ADDF 利用プロジェクト」として生成
- `CLAUDE.local.md` — テンプレートからコピー
- `TODO.md` — 初期テンプレート
- `docs/plans/` — ディレクトリ作成
- `docs/knowhow/INDEX.md` — インデックス初期化
- `.claude/Progress.md` — テンプレートから生成
- `.claude/Feedback.md` — 初期テンプレート
- `.claude/addf-lock.json` — ADDF クローン元のコミットハッシュで生成

### Phase 4: 完了レポート & tmp 削除

```
╔══════════════════════════════════════╗
║  ADDF Setup Complete                 ║
╚══════════════════════════════════════╝

コピー: 35 ファイル
マージ: .gitignore, .claude/settings.json, CLAUDE.md
生成:   CLAUDE.repo.md, TODO.md, Progress.md, ...
スキップ: CONTRIBUTING.md（既存保持）

次のステップ:
1. CLAUDE.repo.md を確認・カスタマイズしてください
2. docs/plans/ に計画ファイルを作成してください
3. `/addf-dev` で開発を開始できます
```

## 変更対象ファイル

| ファイル | 変更 |
|---|---|
| `.claude/commands/addf-init.md` | Phase 0（外部起動）、Phase 2.5（干渉チェック）、Phase 2.7（レビュー）、Phase 3 拡張 |
| `.gitignore` | マーカーブロック形式に移行 |
| `README.md` / `README.en.md` | 「既存プロジェクトへの導入」セクション追加 |
| `CLAUDE.md` | （変更なし — マージ先のみ） |

## 検証

1. `bash .claude/tests/run-all.sh` が通過すること
2. `/addf-init check` で構造検証が通ること
