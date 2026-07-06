# 計画: バージョンロックファイルとマイグレーション基盤

## 実装状況: 完了（2026-03-20、2026-06-11 遡及確認）

GitHub Issue: #4

## 動機

ダウンストリームプロジェクトが ADDF をアップグレードする際、現在はマイグレーション用のアンカーがない。
どのバージョンの ADDF を使っているか不明なため、安全な差分適用ができない。
全ダウンストリームの毎回のアップグレードに恩恵があり、最も複利効果が高いインフラ基盤。

## 設計

### 1. ロックファイルの作成

`.claude/addf-lock.json` を新設:

```json
{
  "version": "0.1.0",
  "commit": "13fbd21...",
  "updated_at": "2026-03-20"
}
```

- `version`: セマンティックバージョニング（今後リリースタグを打つ前提）
- `commit`: ADDF 本体のコミットハッシュ（タグがない場合のフォールバック）
- `updated_at`: 最終更新日
- このファイルは `.gitignore` 対象外（ダウンストリームでコミットする）

### 2. マイグレーションスキル `addf-migrate`

`/addf-migrate` スキルを新設。ワークフロー:

1. `.claude/addf-lock.json` から現在のバージョン/コミットを読む
2. ADDF 本体リポジトリの latest（またはターゲットバージョン）を tmp ディレクトリにチェックアウト
3. ロックファイルのコミットと latest の差分を算出
4. `.claude/` 配下の変更をリスト表示し、ユーザーに確認
5. 承認後、変更をワーキングディレクトリに適用
6. `addf-lock.json` を更新

**除外対象**（マイグレーション対象外）:
- `.claude/Progress.md` — プロジェクト固有の進捗
- `.claude/Feedback.md` — プロジェクト固有の記録
- `*.exp.md` — ローカル経験ファイル
- `.claude/settings.local.json` — ローカル設定
- `CLAUDE.repo.md`, `CLAUDE.local.md` — プロジェクト固有設定

**マージ戦略**:
- `settings.json`: ダウンストリームの追加エントリを保持しつつ ADDF の変更をマージ
- スキル・エージェント定義: ADDF 側を優先（上書き）
- テンプレート: ADDF 側を優先

### 3. バージョニング方針

- 当面はコミットハッシュベースで運用
- リリースタグ（`v0.1.0` 等）を打ち始めたらタグベースに移行
- `addf-lock.json` は両方を保持するため、移行は透過的

## 影響範囲

- `.claude/addf-lock.json`（新規）
- `.claude/commands/addf-migrate.md`（新規スキル）
- `docs/knowhow/` — マイグレーション設計の知見

## 見積もり

AI 実装: 15-25 分

## 実装結果

### 完了した項目
- `.claude/addf-lock.json` — 初期ロックファイル作成（version, commit, updated_at, repository）
- `.claude/commands/addf-migrate.md` — 6フェーズのマイグレーションスキル（状態確認→取得→差分算出→確認→適用→完了）
- `.claude/settings.json` — `git clone`, `git -C`, `mktemp` 権限を追加

### 計画からの差分
- `repository` フィールドを `addf-lock.json` に追加（計画には未記載だったが、マイグレーション時にリポジトリ URL が必要）
- Gotchas セクションをスキルに追加（`rm -rf` 権限、CLAUDE.md マージ、URL 変更時の注意）

### 将来の設計課題
- CLAUDE.md のマージ戦略は実運用で経験を蓄積し、明確化していく必要がある
- `CLAUDE.repo.md` 側にプロジェクト固有設定を寄せる設計方針を維持すれば、CLAUDE.md マイグレーションは単純化できる

## 状態: 完了（2026-03-20）
