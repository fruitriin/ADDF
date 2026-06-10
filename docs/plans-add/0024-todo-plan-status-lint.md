# Plan: TODO⇔Plan 状態同期の lint 化 — 「信用ベース」運用への転換

## 実装状況: 完了（2026-06-11、PR #11 に同梱）

## Context

Plan 0015 のドリフト事件（3ヶ月「未着手」表記のまま実は実装済み）への対処として、
knowhow `plan-status-drift-check.md` が「Plan 着手前に毎回 git log で突合せよ。
『未着手』表記は信用するな」という**読む側が毎回疑う**設計を導入した。

オーナーの設計方針（2026-06-11 対話）はこれと逆向き:
**「疑いをかけるのは一瞬にして、基本的には信用するベースにしたい。
たとえば自分のタスクが完了したときについでにチェックするくらい」**。

そこで Feedback.md の確立済み原理「意思で覚えず機械化する」を適用し、
疑う仕事を機械（lint）に移して、エージェントは表を信用してよい状態を作る。

## 実装内容

### 1. lint ペア6: TODO 状態 ⇔ Plan `## 実装状況:` ヘッダ（WARNING）

`lint-template-sync.py` に追加。対象は2系統:
- `docs/plans-add/TODO.addf.md` ⇔ `docs/plans-add/*.md`（ADDF 本体）
- `TODO.md` ⇔ `docs/plans/*.md`（ダウンストリーム）

検出するドリフト:
- **状態の矛盾**: TODO が「完了」なのに Plan ヘッダが「未着手」、またはその逆。
  明確な矛盾のみ WARNING にする（「進行中」等の中間状態は flag しない — 誤検出より見逃しを許容する信用ベースの精神）
- **TODO が指す Plan ファイルの不在**（WARNING）
- **Plan ファイルの TODO 登録漏れ**（WARNING。起案したのに TODO に載せ忘れたケース）

寛容設計（ペア5の流儀を踏襲）:
- `## 実装状況:` ヘッダが無い Plan は検査対象外（古い Plan 0001〜0014 等。ドリフトではない）
- TODO ファイルが無い系統は SKIP（ダウンストリームに plans-add は無い）

### 2. 「完了時についで」の頻度は run-all.sh 組み込みで自動実現

`test-template-sync.sh` の Test 1（実リポジトリで OK）が品質ゲートの
`bash .claude/tests/run-all.sh` で毎タスク完了時に走るため、
オーナーの希望する頻度（自分のタスク完了時についで）がそのまま実現される。
着手時に確かめたいときは `/addf-lint` を任意実行すればよい。

### 3. knowhow を信用ベースに改訂

`plan-status-drift-check.md` を改訂: 「毎回疑え」→「表は基本信用してよい
（lint ペア6が守っている）。疑うのは lint が WARNING を出したときと、
長期間『未着手』のまま滞留している Plan を拾うときだけ」。

## 変更対象ファイル

| ファイル | 変更 |
|---|---|
| `.claude/addfTools/lint-template-sync.py` | ペア6追加 |
| `.claude/tests/tools/test-template-sync.sh` | ペア6のテスト追加 |
| `.claude/commands/addf-lint.md` | セクション6の表を更新（ペア5欠落の既存ドリフト修正含む） |
| `docs/knowhow/ADDF/plan-status-drift-check.md` | 信用ベースへ改訂 |
| `.claude/Feedback.md` | ペア言及を1〜6に更新 |

## 検証

1. `bash .claude/tests/run-all.sh` 通過
2. ペア6テスト: 矛盾検出 / 登録漏れ検出 / ヘッダ無し Plan のスキップ / TODO 不在系統の SKIP

## 備考

addf-lint.md セクション6の表がペア4までで止まっていた（Plan 0022 でペア5を
実装した際のドキュメント更新漏れ）。本計画で修正。「lint にペアを足したら
addf-lint.md の表も更新する」が新たな同期点になるが、これは lint スクリプトの
docstring と表の2箇所更新で済む軽さなので機械化はせず、本備考を目印とする。
