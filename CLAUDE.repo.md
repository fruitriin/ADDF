@CLAUDE.repo.example.md

## ADDF 開発用ブートシーケンス補足

このリポジトリは ADDF 本体のため、ブートシーケンスの手順 2 では `TODO.md` に加えて以下も読む:
- @.claude/addf/plans-add/TODO.addf.md — ADDF 開発タスクバックログ
- `.claude/addf/plans-add/`: ADDF 開発の実装計画ファイル

## ファイル編集とコマンドの選び方（Plan 0054 D 軸の運用・2026-07-21 オーナー方針）

- **保護対象**（`.claude/settings.json`・`.claude/settings.local.json`・`.claude/hooks/**`・
  `.ccchain.conf`）の編集は**必ず Edit / Write ツールを使う** — permissions.ask の
  確認ダイアログを受けるのが D 軸の設計意図。Bash 経由の書き換えは技術的に可能でも選ばない
  （ask の迂回はガードの意味と観測データの両方を消す）
- **それ以外も、素朴なコマンドとツールを優先する**: 単発の編集は Edit ツール、テキスト処理は
  sed / awk / grep 等の素のコマンドで書く。**python ヒアドキュメントの長塊を常用しない** —
  auto モードの分類器にも確認ダイアログを読む人間にも不透明で、脳死 Accept を誘発する。
  旧 ccchain の dynamic deny を避ける目的で python に逃げていた経緯があるが、現在は
  for ループ解析（v0.2.1+）・sed/awk allow・rm 緩和が揃っており、素朴なコマンドは普通に通る。
  python スクリプトは「本当に複雑な一括処理」に限定し、その場合も何をするか一言添える
- ccchain の ask / deny で止まったときは迂回せず、ルール調整の提案か
  `ccchain approve --last` の依頼で対処する
