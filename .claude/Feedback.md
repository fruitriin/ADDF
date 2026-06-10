# Process Feedback

開発プロセスの振り返りと改善を記録する。

## 記録方法

タスク完了時や問題発生時に、以下のいずれかのセクションに追記する。

## オーナーフィードバック

- 2026-06-10: Plan 0016〜0020（迷ったときの作法・代替わり日記・knowhow ライフサイクル・分かれ道の目印・視点ずらしレビュー）は、エージェント（Fable）へのインタビューとオーナーの対話から生まれ、実装を担当したエージェント自身が「Questions.md がある家は呼吸が楽」と評した。オーナーからも「一緒に作れてよかった」と好評。これらの機能は**エージェントの住み心地のために作られたもの**であり、変更時はその趣旨（責めない・強制しない・温度を保つ）を守ること

## 問題の記録

- このリポジトリ自体がADDフレームワーク本体のため、`addf-contribution-agent` の検出結果（アップストリームコントリビューション候補）はそのまま自身に適用済み。フレームワーク本体での `addf-contribution-agent` の有用性は限定的。ただし**「ダウンストリーム配布時の安全性」観点の指摘は本体でも有効**（Plan 0021 で lint スクリプトの配布時誤 ERROR を検出し、フェーズ内で SKIP 設計に修正できた）

## 改善アクション

- ADD フレームワーク開発の計画は `docs/plans-add/`、knowhow index は `INDEX.addf.md` で管理する（`docs/plans/` と `INDEX.md` はダウンストリームプロジェクト用）
- CLAUDE.md はダウンストリームテンプレートとして汎用性を保つこと。ADDF 固有の参照（TODO.addf.md 等）は CLAUDE.repo.md に置く（Plan 0008 で発見・修正済み）
- `/dev-loop` スキルのブートシーケンスが `TODO.md` を参照するが、ADDF 本体では `docs/plans-add/TODO.addf.md` が正。`/addf-dev` 側は CLAUDE.md のブートシーケンスに従うので問題ないが、汎用 `/dev-loop` 使用時は注意
- CLAUDE.md のマイグレーション戦略: `CLAUDE.repo.md` にプロジェクト固有設定を寄せる設計方針を維持することで、CLAUDE.md のマイグレーションを単純な上書きに近づける。この方針を崩すとマイグレーション実装が複雑化する（Plan 0011 レビューで発見）
- 同期ファイルペア（CLAUDE.md ⇔ AGENTS.md / ProgressTemplate.addf.md ⇔ Progress.md・ProgressTemplate.md / CLAUDE.md ⇔ development-process.md / CLAUDE.md ⇔ addf-init コピーリスト）のドリフトは Plan 0021・0022 で lint 化済み（`lint-template-sync.py` ペア1〜5、テストは `run-all.sh` に組み込み）。同期対象を変更したら `/addf-lint` のセクション6を実行して確認する。**新たな同期ペアが生まれたら lint にペアを追加すること**（意思で覚えず機械化する — 詳細は `docs/knowhow/ADDF/sync-lint-design.md`）
- CLAUDE.md に新しい `.claude/` 配下ファイルへの参照を追加するときは、addf-init のコピーリスト（または .gitignore ADDF ブロック）への追加もセットで行う。漏れは lint ペア5が WARNING で検出する（Plan 0022）
- addf-dev.md がテンプレートのステップ番号を直接参照していた（「ステップ 8〜13」が旧番号のまま残留）。番号参照はセクション名併記にする（Plan 0017 レビューで発見・修正済み）

## 完了済み

- ~~Plan 0004 実施時に `add-Behavier.toml` を `addf-Behavior.toml` にリネームする~~ → Plan 0004 で実施済み
