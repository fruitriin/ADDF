# Plan: knowhow の賞味期限 — 最終検証日と依存前提

## 実装状況: 完了（2026-06-10、2026-06-11 遡及確認）

> **状態: 実装完了（2026-06-10）**
> - 既存10ファイルにフロントマター一括付与（created/last_verified は git log 由来）。INDEX に鮮度マーク列（初期状態: 🟢2 / 🟡8）
> - addf-knowhow-index（鮮度判定・📜棚・鮮度レポート）、addf-knowhow（フロントマター生成・last_verified 更新）、addf-knowhow-agent（ライフサイクルフィルタ）を拡張
> - 新スキル2本: `/addf-knowhow-revise`（意味的再検証・訂正履歴・superseded/retired 遷移）、`/addf-knowhow-network`（GFM 相互リンク wiki 化・双方向担保・ハブサマリ）
> - addf-lint にチェック 7（鮮度・WARNING 止まり）・8（双方向リンク）追加
> - レビュー指摘（Critical 0 / Warning 3 / Suggestion 5）対応: needs-review を 🔴 扱いに統一、しきい値定義を index に単一化、retired への片方向リンク例外を明示
> - 計画との差分: `verified_against` フィールドはマイグレーションでは付与せず（任意フィールド。新規作成時のみ）。depends_on の初期値は空配列（不正確な依存の混入を避け、revise の初回実行で精査）

## Context

ADDF は `.claude/addf/knowhow/` にノウハウを蓄積する設計だが、ノウハウは溜まるほど価値が出る一方で、古い知見は静かに嘘になる。
依存ライブラリのバージョン変更、API の仕様変更、内部設計の刷新などで「過去は正しかったが今は誤り」になった knowhow を、後続エージェントが古文書として信じる事故は時間問題で起きる。

Fable からの一次フィードバック:

> 各 knowhow に「最終検証日」と「依存している前提」を書く欄があって、
> reindex 時に矛盾や古さを検出できると、未来の私が古文書を信じて事故るのを防げる。

## 設計

### 1. knowhow フロントマター拡張

各 knowhow ファイルの先頭に YAML フロントマターを必須化する:

```yaml
---
title: モデル定義時の型整合パターン
created: 2026-04-12
last_verified: 2026-06-10
verified_against:
  - claude-opus-4-7
  - claude-sonnet-4-6
depends_on:
  - skill: addf-dev
  - file: .claude/addf/templates/ProgressTemplate.addf.md
  - library: zod >=3.22
status: active  # active | superseded | retired | needs-review
superseded_by:   # status: superseded のときのみ。後継ノウハウへの相対パス
  - ../knowhow/ADDF/new-type-pattern.md
---

# モデル定義時の型整合パターン
...
```

**status の語彙について**: ノウハウは過去のエージェント（≒ 同僚）が残してくれた仕事。
「deprecated（使うな）」と烙印を押すのではなく、

- `superseded` — 次の世代に引き継がれた（後継への敬意）
- `retired` — 現役を退いた（お疲れさま、棚に上げる）

の二語を使い分ける。意味的には「現役で参照しない」だが、温度は穏やかに保つ。

### 2. フィールド定義

| フィールド | 必須 | 意味 |
|---|---|---|
| `title` | ✓ | knowhow の見出し |
| `created` | ✓ | 初回記録日 |
| `last_verified` | ✓ | 最後に「現在も妥当」と検証された日 |
| `verified_against` | 任意 | 検証時のモデル・環境 |
| `depends_on` | 任意 | 依存するスキル・ファイル・ライブラリ・前提 |
| `status` | ✓ | `active` / `superseded`（後継あり） / `retired`（後継なしで棚上げ） / `needs-review` |
| `superseded_by` | `superseded` 時必須 | 後継ノウハウへの相対パス（配列） |

### 3. `/addf-knowhow-index` の拡張

`addf-knowhow-index reindex` 時に以下を実行:

1. 全 knowhow のフロントマターをパース
2. `last_verified` から N 日経過したものを `needs-review` 候補としてレポート
3. `depends_on` に列挙されたファイルが存在しないものをレポート
4. INDEX に「鮮度マーク」を追加（例: 🟢 fresh / 🟡 aging / 🔴 stale）

```
.claude/addf/knowhow/INDEX.addf.md

| 🟢 | モデル定義時の型整合パターン | 2026-06-10 verified |
| 🟡 | UI テストのアサーション設計 | 2026-03-05 verified (90日経過) |
| 🔴 | Codex 起動時の権限処理 | 2025-12-01 verified (依存ファイル削除済み) |
```

しきい値:
- 🟢 fresh: 60 日以内
- 🟡 aging: 60〜180 日
- 🔴 stale: 180 日超 or 依存欠落

### 4. `/addf-knowhow` 実行時の挙動

新規 knowhow 作成時、フロントマターを自動生成:

```yaml
---
title: <ユーザー指定 or 自動推定>
created: <今日>
last_verified: <今日>
verified_against:
  - <現在のモデル ID>
depends_on: []  # ユーザーが手動で埋める
status: active
---
```

既存 knowhow を更新する場合は `last_verified` を今日に更新する。

### 5. ブートシーケンス連携

`addf-knowhow-filter` サブエージェントが knowhow を要約してメインに返すとき:

- `status: retired` のものは原則返さない（参照したい歴史的文脈がある場合のみ明示要求）
- `status: superseded` のものは返さず、代わりに `superseded_by` の後継ノウハウを返す
- `🔴 stale` のものは要約に「📜 鮮度低下: 最終検証 YYYY-MM-DD」を併記
- `🟢 fresh` を優先

### 6. 別建てスキル: `/addf-knowhow-revise`（誤り訂正）

オーナー指針:

> ノウハウINDEXの再構築と別に、ノウハウの誤り訂正とネットワーク化のスキルを作るのがよさそう。

`addf-knowhow-index reindex` は機械的な鮮度チェックに留め、**意味的な誤りの訂正**は別スキルに分離する。

**`/addf-knowhow-revise`** の役割:

- `needs-review` / `🔴 stale` のノウハウを1つずつ開く
- 該当ノウハウが依存するファイル・ライブラリ・設計の現状を読み直す
- ノウハウの主張が現在も妥当か検証する:
  - 妥当 → `last_verified` を更新するのみ
  - 部分的に誤り → 該当箇所を訂正し、訂正履歴を末尾に追記
  - 後継が存在する → `status: superseded`、`superseded_by` に後継パスを記載
  - 後継なしで参照不要になった → `status: retired`（棚上げ。棚卸の歴史として保管）
- 訂正後、フロントマターの `last_verified` を更新

訂正履歴のフォーマット:

```markdown
---
## 訂正履歴

### 2026-06-10
- 「zod の coerce は v3.20 以降」と書いていたが、v3.22 以降が正。訂正済み
- 依存ライブラリ列を更新
```

### 7. 別建てスキル: `/addf-knowhow-network`（相互リンク wiki 化）

オーナー指針:

> ネットワーク化は GitHub flavored markdown link style で、記事同士で相互リンクを作って wiki を作るんだ。

ノウハウは単独で読まれるよりも、関連ノウハウへ辿れることで価値が増す。
**`/addf-knowhow-network`** は記事同士を GFM リンクで結び、knowhow 全体を wiki として育てる。

**実装方針**:

1. 全 knowhow を読み込み、概念・キーワード・依存対象を抽出
2. 関連性を推定（同じスキル、同じファイル群、同じドメインに言及している等）
3. 各 knowhow の末尾に `## 関連ノウハウ` セクションを生成・更新:

```markdown
## 関連ノウハウ

- [モデル定義時の型整合パターン](../knowhow/ADDF/model-type-consistency.md) — 本記事と同じく zod に依存
- [テストヘルパーの注入ポイント](../knowhow/ADDF/test-helper-injection.md) — モデル定義時に参照される
- [📜 Superseded: 旧型変換ロジック](../knowhow/ADDF/old-type-coercion.md) — 本記事に引き継がれた先輩ノウハウ
- [📜 Retired: 初期 zod 採用検討メモ](../knowhow/ADDF/zod-adoption-memo.md) — 採用判断完了で棚上げ
```

4. 双方向リンクを担保する（A から B にリンクするなら B からも A にリンクする）
5. `status: superseded` / `retired` のノウハウへは `📜 Superseded:` / `📜 Retired:` プレフィックスを付ける
6. `INDEX.addf.md` にネットワークサマリ（リンク数の多いハブノウハウのトップ N）を追加

**運用フロー**:

```
/addf-knowhow-index reindex   # 鮮度マークの更新（機械的）
/addf-knowhow-revise           # 古いノウハウを再検証・訂正（意味的）
/addf-knowhow-network          # 相互リンクを張り直し wiki 化（構造的）
```

3つはそれぞれ独立に実行できるが、`revise → network` の順で回すと整合性が高い。

### 8. 鮮度通知（任意）

`addf-lint` または `addf-knowhow-index reindex` 実行時、stale が一定数を超えたら警告を表示:

```
📜 鮮度低下した knowhow が 5 件あります:
  - .claude/addf/knowhow/ADDF/codex-startup.md (2025-12-01)
  - .claude/addf/knowhow/ADDF/old-pattern.md (依存ファイル欠落)
  ...

`/addf-knowhow review` で再検証してください。
```

`/addf-knowhow review` は本 Plan では追加スキルとして定義しない（必要なら後続 Plan）。

## 変更対象ファイル

| ファイル | 変更 |
|---|---|
| `.claude/commands/addf-knowhow.md` | フロントマター生成ロジック追加 |
| `.claude/commands/addf-knowhow-index.md` | フロントマターパース・鮮度判定・INDEX 拡張 |
| `.claude/commands/addf-knowhow-revise.md` | 新規スキル: 古いノウハウの再検証・訂正 |
| `.claude/commands/addf-knowhow-network.md` | 新規スキル: 相互リンクで wiki 化 |
| `.claude/agents/addf-knowhow-agent.md` | status / 鮮度ベースのフィルタリング、関連ノウハウへの追跡 |
| `.claude/commands/addf-lint.md` | 鮮度警告チェック、双方向リンク欠落チェック追加 |
| 既存 knowhow ファイル | フロントマター追記（一括マイグレーション） |
| `.claude/addf/knowhow/INDEX.addf.md` | 鮮度マーク列・ハブノウハウサマリの追加 |

## マイグレーション

既存 knowhow へのフロントマター追加は一括スクリプトで実行する:

```bash
# 各ファイルに以下を挿入（last_verified は git log の最終更新日）
for f in .claude/addf/knowhow/**/*.md; do
  ...
done
```

スクリプトは Plan 実装時に作成し、適用後にコミット。

## 検証

1. `bash .claude/addf/tests/run-all.sh` 通過
2. `/addf-knowhow-index reindex` で鮮度マークが INDEX に反映されることを確認
3. 故意に `last_verified` を 200 日前に書き換え、stale としてマークされることを確認
4. `depends_on` で存在しないファイルを指定し、依存欠落として検出されることを確認

## メモ

- フロントマターは markdown プレビューで邪魔になる場合があるが、INDEX 経由の参照が主のため許容
- 「鮮度」は機械判定の補助。最終判断は人 or エージェントの再検証
