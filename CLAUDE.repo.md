@CLAUDE.repo.example.md

## ADDF 開発用ブートシーケンス補足

このリポジトリは ADDF 本体のため、ブートシーケンスの手順 2 では `TODO.md` に加えて以下も読む:
- @.claude/addf/plans-add/TODO.addf.md — ADDF 開発タスクバックログ
- `.claude/addf/plans-add/`: ADDF 開発の実装計画ファイル

## 保護対象ファイルの編集原則（Plan 0054 D 軸の運用）

`.claude/settings.json`・`.claude/settings.local.json`・`.claude/hooks/**`・`.ccchain.conf` を
編集するときは、**必ず Edit / Write ツールを使う**（permissions.ask の確認ダイアログを
受けるのが D 軸の設計意図）。Bash 経由（python ワンライナー・heredoc・sed -i・
リダイレクト）での書き換えは、技術的に可能でも**選ばない** — ask の迂回はガードの意味と
観測データの両方を消す（2026-07-21 オーナー指摘。ccchain の ask/deny で止まったときも
同様に、迂回せずルール調整の提案か `ccchain approve --last` の依頼で対処する）。
複数ファイル一括編集の python ワンライナーは保護対象**以外**のファイルにのみ使ってよい。
