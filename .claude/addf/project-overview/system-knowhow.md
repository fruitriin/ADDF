# ノウハウ蓄積 — Implementation knowledge management

> 概念単位の記録。実装がスキル/エージェント/フック/ファイルのどれであっても、
> 「実装知見の記録・検索・活用・経年管理」に関わるものをまとめている。

## 構成要素

| 種別 | 名前 | 役割 |
|---|---|---|
| スキル | addf-knowhow | 実装知見を .claude/addf/knowhow/ に記録（重複チェック・自己ブラッシュアップ・分かれ道の目印の記録提案付き） |
| スキル | addf-knowhow-index | インデックスの参照・再構築。鮮度判定（🟢/🟡/🔴）のしきい値定義の唯一の場所 |
| スキル | addf-knowhow-filter | Plan 内容に基づく関連ノウハウのフィルタリング（context: fork） |
| スキル | addf-knowhow-revise | 🔴 stale / needs-review のノウハウを意味的に再検証し、訂正・superseded/retired 遷移・訂正履歴を記録 |
| スキル | addf-knowhow-network | 記事間を GFM リンクで相互接続し wiki 化。双方向リンク担保・📜 プレフィックス・INDEX ハブサマリ |
| スキル | addf-experience | .exp.md ファイルの @メンション書式検証・修正 |
| エージェント | addf-knowhow-agent | ブートシーケンス Step 5 で Plan に関連する knowhow を抽出（Haiku）。ライフサイクルフィルタ内蔵 |
| ディレクトリ | .claude/addf/knowhow/ADDF/ | ADDF 由来ノウハウ（現在17件。投機開発・オプトインスキル・チェックリスト裏付け・計画詰めの知見が近況で追加） |
| ファイル | .claude/addf/knowhow/INDEX.addf.md | ADDF 用ノウハウインデックス（鮮度タグ付き） |
| ファイル | .claude/addf/knowhow/INDEX.md | ダウンストリーム用ノウハウインデックス |
| ファイル | .claude/addf/knowhow/CLAUDE.md | 読み方の作法（タイトルで推測せず本文で判断する） |
| テンプレート | .claude/addf/templates/ExperienceTemplate.md | .exp.md のテンプレート（✅ うまくいったパターン / 🔀 分かれ道の目印 / 🤔 判断が分かれた事例） |
| フック | turn-reminder.sh（関心事A） | ターン10/15で知見の定期棚卸し（/addf-knowhow・日記）を促す（※セッション管理と共有） |

## 設計思想

ADDF の第二の柱。「同じ失敗を繰り返さない、同じ発見を再発見しない」ための知識蓄積システム。

二層構造を持つ:
- **knowhow（プロジェクト知見）**: `.claude/addf/knowhow/` に蓄積。タスク完了時に3観点（コーディング・品質ゲート・タスク総括）で記録。全エージェントが参照可能
- **experience（スキル経験）**: `.exp.md` ファイル（.gitignore 対象のローカル資産）。スキル単位の「うまくいったパターン / 分かれ道の目印 / 判断が分かれた事例」

### ライフサイクル管理 — Plan 0018

古いノウハウは静かに嘘になる。各 knowhow はフロントマター（`created` / `last_verified` / `depends_on` / `status`）を持ち、INDEX 再構築時に鮮度を機械判定する:

- 🟢 fresh: last_verified が60日以内 / 🟡 aging: 60〜180日 / 🔴 stale: 180日超・依存切れ・needs-review
- status の語彙は `active` / `superseded`（後継に引き継がれた。`superseded_by:` 併記）/ `retired`（棚上げ。削除はしない）/ `needs-review`。**`deprecated` は使わない**（過去のエージェントの仕事への敬意）

3スキルの分業: `reindex`（機械的な鮮度マーク）→ `revise`（意味的な再検証・訂正履歴）→ `network`（構造的な相互リンク wiki 化）。addf-knowhow-agent は superseded を後継に差し替え、stale には「📜 鮮度低下」を併記して返す。

### 分かれ道の目印 — Plan 0019

差し戻し・やり直し・想定外の判断が発生したら、.exp.md の「🔀 分かれ道の目印」に**意思決定の分岐点**として記録する。分岐の種類を必ず付ける: **[計画で防げた]**（計画時の確認目印を書く）/ **[作って分かった]**（失敗ではなく健全な探索コスト）。失敗の告白ではなく道標を立てる。目印ゼロは健全な状態でありうるため記録は強制しない。

INDEX は候補発見の地図であり中身の代わりではない（.claude/addf/knowhow/CLAUDE.md）。knowhow-filter / knowhow-agent は「タイトルで推測せず本文で判断する」作法に従う。ADDF 本体では `INDEX.addf.md`、ダウンストリームでは `INDEX.md` を使う分離パターンにより、フレームワーク知見とプロジェクト知見が混在しない。

## 主要フロー

```
タスク開始時:
  Plan 特定 → addf-knowhow-agent → 関連 knowhow をコンテキストに注入
  （superseded は後継に差し替え、stale は鮮度低下を注記）

実装中:
  addf-knowhow-filter で追加の知見を検索
  turn-reminder（10/15ターン）が棚卸しを促す

タスク完了時:
  /addf-knowhow で新たな知見を記録
  ├─ Phase 1: 既存 knowhow スキャン（重複チェック・統合優先）
  ├─ Phase 2: 記録（フロントマター必須のテンプレート）
  ├─ Phase 3: 自己ブラッシュアップ（正確性・完全性・簡潔性・実用性）
  └─ Phase 4: 分かれ道の目印の記録提案（.exp.md 🔀 セクションへ）

定期メンテナンス:
  /addf-knowhow-index reindex → INDEX 再構築 + 鮮度レポート
  /addf-knowhow-revise → stale/needs-review の再検証・訂正・superseded/retired 遷移
  /addf-knowhow-network → 相互リンク wiki 化・ハブサマリ更新
  /addf-experience → .exp.md の @メンション書式検証
  （revise → network の順で回すと整合性が高い）
```

## 下流でのカスタマイズ

- `.claude/addf/knowhow/` にプロジェクト固有の知見を蓄積（`INDEX.md` で管理）
- ADDF 由来の知見は `.claude/addf/knowhow/ADDF/` サブディレクトリに分離される（addf-migrate の上書き対象）
- ExperienceTemplate.md を編集してスキル経験の記録フォーマットを変更可能
- 鮮度しきい値の定義は addf-knowhow-index に一元化されており、変更は1箇所で済む

## 関連するシステム

- **計画駆動**: ブートシーケンス Step 5 で knowhow-agent が起動。タスク完了時に3観点で knowhow 記録。日記アーカイブは後日 knowhow 化の原資料
- **品質ゲート**: レビューで得た知見が knowhow に蓄積される。addf-lint の項目5・7・8（INDEX 整合・鮮度・双方向リンク）が knowhow の健全性を機械検査する
- **セッション管理**: turn-reminder.sh（関心事A）が定期棚卸しを、context-reminder.py がコンパクション前の知見記録を促す
- **投機開発**: worktree 複製・squash 統合の設計知見（worktree-dotdir-copy / speculative-integration-design）が knowhow に蓄積され、addf-speculate の .exp.md と往復する
