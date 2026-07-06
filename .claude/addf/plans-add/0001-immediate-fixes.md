# 計画: 即時修正（typo・不整合・欠落ファイル）

## 実装状況: 完了（2026-03-18、2026-06-11 遡及確認）

## 動機
プロジェクトレビューで発見された不整合・typo・欠落ファイルを修正し、フレームワークの基盤を健全にする。

## 設計

### 1. `CLAUDE.repo.example.md` typo 修正
- L17: 「起かない」→「置かない」

### 2. `CLAUDE.local.example.md` 作成
- `CLAUDE.local.md` が `@CLAUDE.local.example.md` を参照しているが、ファイルが存在しない
- テンプレートとして最低限の構造を持つファイルを作成

### 3. `docs/knowhow/INDEX.md` 初期生成
- `addf-knowhow-index` スキルが参照する INDEX ファイル
- 既存の knowhow 2件（claude-md-at-mention, ignore-file-strategy）を登録

### 4. `plan.md` の移行・削除
- `plan.md` の内容はこの計画群（0001〜0006）に分解済み
- ルートから `plan.md` を削除（ADD哲学: ルートに ADD 由来ファイルを置かない）

### 5. `.gitignore` 整備
- `node_modules` を追加（現在は経験ファイル等のみ記載）

### 6. `.claudeignore` 検討
- `addfTools` のコンパイル済みバイナリは除外すべきか評価
- バイナリファイルは Claude の読解対象外なので追加する

## 影響範囲
- `CLAUDE.repo.example.md`, `CLAUDE.local.example.md`, `docs/knowhow/INDEX.md`
- `plan.md`（削除）, `.gitignore`, `.claudeignore`

## 実装完了状況
- 全6項目を実施完了（2026-03-18）
- コードレビュー指摘2件を対応済み:
  - `.claudeignore` 末尾改行欠落 → 修正
  - `add-Behavier.toml` typo → Plan 0004 に注記追加（リネームは 0004 で実施）
