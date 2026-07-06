# Plan 0043: セキュリティ回収（Plan 0026 残 Critical/High + 0033 パストラバーサル Low）

## 実装状況: 未着手

> **粗々の起票**: 設計の方向性と未決事項を出す段階。実装詳細は着手時に詰める。

> 出典: オーナー指示（2026-07-06）—「B3 = 起票と実施でよさそう / C1 = 不便のない範囲で実施したい」に基づく回収計画。Plan 0036 の埋没タスク検出（#1・#7・#8）を集約する。

## 関連 Plan

- [Plan 0026: レビュー残課題のバックログ化](0026-review-residual-backlog.md) — 出典1: セキュリティ Critical/High（deny ルール・addf-init 実物レビュー・破壊的 git 対策・cp 無制限）
- [Plan 0033: ダウンストリーム実測バグの修正](0033-downstream-reported-fixes.md) — 出典2: パストラバーサル Low（@メンション解決の耐性 — 小粒だが同型テーマ）
- [Plan 0032: knowhow 鮮度棚卸し](0032-knowhow-freshness-audit.md) — cp 上書き副作用の deny ルール検討はここで「悩みどころ」として保留（B2 判断）→ 本 Plan では**cp 上書きは対象外**

## 目的

Plan 0026 のレビューで検出されたセキュリティ Critical/High を「不便のない範囲で」実施する。deny ルール・addf-init 実物レビュー・破壊的 git 対策・パストラバーサル耐性の4項目を対象にする（cp 無制限問題は Plan 0032 の deny 検討が保留のため対象外）。

## 現状の挙動

- deny ルール: allow/ask 中心の運用で、明示的な deny ルールが薄い
- addf-init: 配布ファイルの内容チェックはあるが、実物（Mach-O バイナリ・シェルスクリプト）の実物レビューは未整備（checksums 照合は Plan 0031 で導入済み — その先の中身レビュー）
- 破壊的 git: `git reset --hard`・`git clean -fdx`・`git push --force` などの実行前ガードが薄い
- パストラバーサル: @メンション解決に `..` / 絶対パス混入の防御はあるが、記事末尾に「実害は限定的」と評価済み

## 変更内容（項目）

### 項目1: deny ルール整備

- settings.json / settings.local.json の permission 設計に「破壊が主目的の操作」を明示的に deny する
- 対象候補: `rm -rf /`・`git reset --hard origin/*`（allow だが対象範囲注記）・`git push --force`（allow だが確認注記）・`chmod 777`（許可範囲を絞る）
- **「不便のない範囲」**: 実運用で使う操作は allow のまま維持し、極端な破壊操作のみ deny する。過剰な deny で運用が止まらないことを Feedback で観測しながら段階調整

### 項目2: addf-init 実物レビュー整備

- 配布ファイル（バイナリ・シェル・スクリプト）の**内容が意図どおりか**を addf-init 初回実行時にオーナーへ提示する仕組み（現状は「コピーします」だけで内容は開示されない）
- Plan 0031 の checksums 照合の**上流**として位置付ける（照合は改竄検出、実物レビューは意図の確認）
- 「不便のない範囲」: 全ファイル表示は過剰。カテゴリごとに「代表ファイル1〜2本を preview 表示 + skip 可能」の設計

### 項目3: 破壊的 git 対策

- pre-tool-use フックで破壊的 git コマンド（`reset --hard` / `clean -fdx` / `push --force*` / `branch -D` / `checkout -- .` 等）を検出し、**確認プロンプト**を挟む
- root ユーザー環境（CI 等）ではフックがない前提で、ローカル対話環境のみ対象
- addf-mode の trust=full では緩める、nervous では厳しめにする（既存 3軸モードと連動）

### 項目4: @メンション解決のパストラバーサル耐性

- Plan 0033 の Low 指摘 — @メンション展開時に `..` / 絶対パス / シンボリックリンク経由の脱出を検出
- 現状の1段展開ロジック（lint-template-sync.py detect_repo_kind() および verify-checksums.sh の同期版）を対象
- ペア7（Python⇔Bash 同期契約 lint）が既にあるため、修正はどちらも同じテスト観点で守れる

## 影響範囲

- `.claude/settings.json` / `.claude/settings.local.json`（項目1）
- `.claude/hooks/`（項目3 の新フック）
- `.claude/commands/addf-init.md`（項目2 の実物レビューステップ）
- `.claude/addf/tools/lint-template-sync.py` / `verify-checksums.sh`（項目4 — ペア7 の両側）
- テスト（4項目それぞれ）

## テスト方針

- 項目1: settings.json の deny ルールが実際に該当操作をブロックする実測（addf-permission-audit のパターン検査）
- 項目2: addf-init のドライラン実行でレビューステップが出力される確認
- 項目3: ドリフト注入 TDD（`git reset --hard HEAD~5` を試行 → 確認プロンプト発火を実測）
- 項目4: パストラバーサル注入テスト（`@../../etc/passwd` を CLAUDE.repo.md に置く → 展開結果を検証）

## 破壊的変更の許容範囲

- deny ルール追加によりダウンストリームの既存運用が壊れる可能性 → migrate ガイドで明記・段階的に導入
- 破壊的 git フックはローカル対話に限定し、CI/自動化を壊さない

## 要オーナー確認

- 項目1 の deny 対象リスト（実運用で使うものを誤って deny しないよう最終確認）
- 項目3 の破壊的 git 検出範囲（過剰な確認プロンプトは運用を阻害）

## 完了条件

- [ ] 4項目それぞれの実装とテスト
- [ ] Plan 0026 の該当 Critical/High が「対応済み」に遷移
- [ ] Plan 0033 のパストラバーサル Low が解消
- [ ] `/addf-lint` および CI（Plan 0030）全通過
- [ ] Feedback.md に「過剰 deny による運用阻害」観測が記録されていない、または段階調整の記録がある

## AI 実装時間見積もり

3〜4セッション（4項目それぞれ独立性がある。フェーズ分割 = 項目単位で並走可）
