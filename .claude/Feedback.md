# Process Feedback

開発プロセスの振り返りと改善を記録する。

## 記録方法

タスク完了時や問題発生時に、以下のいずれかのセクションに追記する。

## オーナーフィードバック

## 問題の記録

- このリポジトリ自体がADDフレームワーク本体のため、`addf-contribution-agent` の検出結果（アップストリームコントリビューション候補）はそのまま自身に適用済み。フレームワーク本体での `addf-contribution-agent` の有用性は限定的

## 改善アクション

- ADD フレームワーク開発の計画は `docs/plans-add/`、knowhow index は `INDEX.addf.md` で管理する（`docs/plans/` と `INDEX.md` はダウンストリームプロジェクト用）
- CLAUDE.md はダウンストリームテンプレートとして汎用性を保つこと。ADDF 固有の参照（TODO.addf.md 等）は CLAUDE.repo.md に置く（Plan 0008 で発見・修正済み）
- `/dev-loop` スキルのブートシーケンスが `TODO.md` を参照するが、ADDF 本体では `docs/plans-add/TODO.addf.md` が正。`/addf-dev` 側は CLAUDE.md のブートシーケンスに従うので問題ないが、汎用 `/dev-loop` 使用時は注意
- CLAUDE.md のマイグレーション戦略: `CLAUDE.repo.md` にプロジェクト固有設定を寄せる設計方針を維持することで、CLAUDE.md のマイグレーションを単純な上書きに近づける。この方針を崩すとマイグレーション実装が複雑化する（Plan 0011 レビューで発見）
- AGENTS.md と CLAUDE.md の同期管理: AGENTS.md のブートシーケンスは CLAUDE.md と同期を保つ必要がある。CLAUDE.md 更新時に AGENTS.md も確認すること。将来的には addf-lint にチェックを追加する価値がある（Plan 0012 レビューで発見）
- ProgressTemplate.addf.md と運用中 Progress.md の同期管理: テンプレートの運用ルールを変更したら、運用中の Progress.md のルールセクションにも同じ変更を手動同期すること。AGENTS.md 同期と同種の再発パターンであり、addf-lint へのチェック追加候補（Plan 0020 レビューで発見）
- docs/guides/development-process.md は CLAUDE.md ブートシーケンスの「第三のコピー」: Plan 0016 の変更が未反映というドリフトが Plan 0017 で発覚。ブートシーケンス・品質ゲートを変更したら development-process.md も確認すること。ガイド側は「正は CLAUDE.md/ProgressTemplate、ここは概要のみ」と明記して詳細の重複を避ける方針に変更済み（Plan 0017 で対応）
- addf-dev.md がテンプレートのステップ番号を直接参照していた（「ステップ 8〜13」が旧番号のまま残留）。番号参照はセクション名併記にする（Plan 0017 レビューで発見・修正済み）

## 完了済み

- ~~Plan 0004 実施時に `add-Behavier.toml` を `addf-Behavior.toml` にリネームする~~ → Plan 0004 で実施済み
