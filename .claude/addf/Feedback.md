# Process Feedback

開発プロセスの振り返りと改善を記録する。

## 記録方法

タスク完了時や問題発生時に、以下のいずれかのセクションに追記する。

## オーナーフィードバック

- 2026-06-10: Plan 0016〜0020（迷ったときの作法・代替わり日記・knowhow ライフサイクル・分かれ道の目印・視点ずらしレビュー）は、エージェント（Fable）へのインタビューとオーナーの対話から生まれ、実装を担当したエージェント自身が「Questions.md がある家は呼吸が楽」と評した。オーナーからも「一緒に作れてよかった」と好評。これらの機能は**エージェントの住み心地のために作られたもの**であり、変更時はその趣旨（責めない・強制しない・温度を保つ）を守ること

## 問題の記録

- このリポジトリ自体がADDフレームワーク本体のため、`addf-contribution-agent` の検出結果（アップストリームコントリビューション候補）はそのまま自身に適用済み。フレームワーク本体での `addf-contribution-agent` の有用性は限定的。ただし**「ダウンストリーム配布時の安全性」観点の指摘は本体でも有効**（Plan 0021 で lint スクリプトの配布時誤 ERROR を検出し、フェーズ内で SKIP 設計に修正できた）

## 改善アクション

- ADD フレームワーク開発の計画は `.claude/addf/plans-add/`、knowhow index は `INDEX.addf.md` で管理する（`.claude/addf/plans/` と `INDEX.md` はダウンストリームプロジェクト用）
- CLAUDE.md はダウンストリームテンプレートとして汎用性を保つこと。ADDF 固有の参照（TODO.addf.md 等）は CLAUDE.repo.md に置く（Plan 0008 で発見・修正済み）
- `/dev-loop` スキルのブートシーケンスが `TODO.md` を参照するが、ADDF 本体では `.claude/addf/plans-add/TODO.addf.md` が正。`/addf-dev` 側は CLAUDE.md のブートシーケンスに従うので問題ないが、汎用 `/dev-loop` 使用時は注意
- CLAUDE.md のマイグレーション戦略: `CLAUDE.repo.md` にプロジェクト固有設定を寄せる設計方針を維持することで、CLAUDE.md のマイグレーションを単純な上書きに近づける。この方針を崩すとマイグレーション実装が複雑化する（Plan 0011 レビューで発見）
- 同期ファイルペア（CLAUDE.md ⇔ AGENTS.md / ProgressTemplate.addf.md ⇔ Progress.md・ProgressTemplate.md / CLAUDE.md ⇔ development-process.md / CLAUDE.md ⇔ addf-init コピーリスト / TODO ⇔ Plan 実装状況ヘッダ）のドリフトは Plan 0021・0022・0024 で lint 化済み（`lint-template-sync.py` ペア1〜6、テストは `run-all.sh` に組み込み）。同期対象を変更したら `/addf-lint` のセクション6を実行して確認する。**新たな同期ペアが生まれたら lint にペアを追加し、addf-lint.md セクション6の表も同時に更新すること**（ペア5追加時に表の更新が漏れた実績あり。意思で覚えず機械化する — 詳細は `.claude/addf/knowhow/ADDF/sync-lint-design.md`）
- CLAUDE.md に新しい `.claude/` 配下ファイルへの参照を追加するときは、addf-init のコピーリスト（または .gitignore ADDF ブロック）への追加もセットで行う。漏れは lint ペア5が WARNING で検出する（Plan 0022）
- addf-dev.md がテンプレートのステップ番号を直接参照していた（「ステップ 8〜13」が旧番号のまま残留）。番号参照はセクション名併記にする（Plan 0017 レビューで発見・修正済み）
- 手順書（Release.addf / addf-init / addf-migrate / ProgressTemplate 系）に「確認/検証」ステップを追加するときは、実行チェック（コードブロック・コマンド）か `<!-- human-judgment -->` マーカーの裏付けを添える。裏付け漏れは `/addf-lint` セクション9（lint-checklist.py・WARNING のみ）が検出する。新しい手順書を検査対象にする場合は lint の TARGETS に追加する（Plan 0027）
- lint スクリプトを新設したら、**その lint が生まれるきっかけになった当のケースを、裏付けを剥がした状態で再現テストする**（Plan 0027 レビューで「メタ lint 自身が flagship 項目の裏付け喪失を検出できない」High 2件を検出。ドリフト注入 TDD — 詳細は `.claude/addf/knowhow/ADDF/checklist-backing-lint.md`）
- 変更が `.claude/addf/plans-add/` 配下のみ（＝ダウンストリーム配布対象外のドキュメントのみ）のタスクでは、`addf-contribution-agent` は検出対象がないためスキップしてよい（2026-07-03 の品質向上プラン起案タスクで適用。コード・配布ファイルに触れる場合は従来どおり実行する）
- Python 3.11+ の stdlib（`tomllib` 等）**または PEP 723 サードパーティ依存（pyyaml 等）**を使う addfTools スクリプトを新設したら、(1) import ガード（責務別の3類型: lint=SKIP / 実行前ゲート=フェイルセーフ ERROR / 変更系=ERROR。`.claude/addf/knowhow/ADDF/sync-lint-design.md` 参照）、(2) テストの uv フォールバック、(3) 手順書の「uv が無ければ python3 直接実行」注記（サードパーティ依存は入手方法 `pip install ...` まで）、の3点をセットで入れる。テストだけに uv フォールバックを入れると手順書経由の実行者が罠に落ちる（2026-07-03 tomllib 修正の教訓。同日の投機サイクルレビューで lint-frontmatter.py の pyyaml が同型の穴と判明し類型を拡張）

- B2（cp 上書き副作用の deny ルール Plan 起案・2026-07-06 オーナー判断）: **保留**。「悩みどころ・環境によるノイズは増えてほしくない」との判断。今後、cp の上書きで実害が観測されたら再検討する（実害の実測をトリガーにする）
- フックで Behavior.toml を読む場合、Python 依存を避けるため bash+awk の簡易パースを選ぶことが正当な選択肢だが、8種の落とし穴（`=` 切り捨て・コメント除去のクオート無視・ヘッダ行末コメント・jq `//` の空文字列素通し・ファイル名サニタイズ不足・秒精度衝突・フォールバック経路のテスト漏れ・macOS bash 3.2 の set -u × basename 相互作用）を伴う。Plan 0042 の code-review が実サンドボックス試行で全て発見し、対策込みで `.claude/addf/knowhow/ADDF/bash-toml-parse-pitfalls.md` に類型化した。次に同型のフックを書くときは同ファイルを参照する
- Plan 実装時、Progress.md のチェックボックスをサブタスク完了と同期して更新する運用を徹底する（doc-review Warning: 実装済みなのに `- [ ]` のまま残ると、代替わり日記を跨いだ次の代の判断を誤らせるリスク。Plan 0042 レビューで指摘）。日記が「文脈」を残すのに対し、チェックボックスは「事実」を残す — 両方が実態と一致していることが引き継ぎ条件

## 完了済み

- ~~Plan 0004 実施時に `add-Behavier.toml` を `addf-Behavior.toml` にリネームする~~ → Plan 0004 で実施済み
