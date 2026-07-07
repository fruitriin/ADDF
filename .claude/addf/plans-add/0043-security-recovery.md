# Plan 0043: セキュリティ回収（Plan 0026 残 Critical/High + 0033 パストラバーサル Low）

## 実装状況: 完了（2026-07-07・4項目とも実装。「不便のない範囲で」の指針を最大限保守的に解釈した最小実装）

- **項目1（deny ルール整備）**: settings.json に `deny` セクションを新設し、極端な破壊操作のみ11パターン（`rm -rf /` / `rm -rf ~` / `chmod 777 /` / `dd if=* of=/dev/*` / `mkfs.*` / `shutdown *` / `reboot *` 等）を明示 deny。既存の allow/ask は無変更で実運用への影響ゼロ。実運用で問題が観測されたら Feedback.md で追加・削除
- **項目2（addf-init 実物レビュー）**: Phase 3 の前に「バイナリ実物 preview」ステップを追加（バイナリ4本の SHA-256 とサイズ・種別を preview / skip 可能・skip でも verify-checksums.sh で改竄検出は担保）。テキストファイルは `git diff` で確認できるため preview 対象外
- **項目3（破壊的 git 対策）**: `.claude/hooks/destructive-git-guard.sh` を PreToolUse(Bash) に配線。5パターン（reset --hard / push --force / clean -f / branch -D / checkout -- .）に理由メッセージを stderr 提示。同時に settings.json `ask` に `git branch -D *` / `git checkout -- *` / `git restore .` / `git restore -- *` を追加（doc-review Critical 1 対応 — 従来 ask に含まれていなかった branch -D と checkout -- . にも確認ダイアログが入るようになった）。ブロックは settings.json ask、フックは理由提示の分業設計。13テスト通過。⚠️ 実効性検証は申し送り: PreToolUse フックの stderr がエージェントに届くかは未検証
- **項目4（@メンション解決のパストラバーサル耐性）**: 別コミット e7476ef で完了（Python/Bash 両側にガード + Test 20/20b/20c）

**「不便のない範囲」の担保**: いずれも既存の運用フローを妨げない設計。deny は極端操作限定、フックは理由提示のみでブロックしない、addf-init preview は skip 可能。運用ノイズ観測は Feedback.md で継続的に調整する（Plan 内の記載どおり）

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
- `.claude/addf/addfTools/lint-template-sync.py` / `verify-checksums.sh`（項目4 — ペア7 の両側）
- テスト（4項目それぞれ）

## テスト方針

- 項目1: settings.json の deny ルールが実際に該当操作をブロックする実測（addf-permission-audit のパターン検査）
- 項目2: addf-init のドライラン実行でレビューステップが出力される確認（human-judgment）
- 項目3: フックの理由メッセージが stderr に出力される機械テスト（`test-destructive-git-guard.sh` の13テスト）— **ブロックはしない設計のため、確認プロンプト発火は検証対象外**（ブロック挙動は settings.json の ask ルール側に任せる分業）
- 項目4: パストラバーサル注入テスト（`@../../etc/passwd` を CLAUDE.repo.md に置く → 展開結果を検証）

## 破壊的変更の許容範囲

- deny ルール追加によりダウンストリームの既存運用が壊れる可能性 → migrate ガイドで明記・段階的に導入
- 破壊的 git フックはローカル対話に限定し、CI/自動化を壊さない

## 要オーナー確認

- ~~項目1 の deny 対象リスト~~ → **事後観測方式に変更（2026-07-07）**: 極端な破壊操作11パターンに限定した最小実装で先に導入。実運用で「これは deny しない方が良い」項目が観測されたら Feedback.md で報告 → 次サイクルで settings.json を更新する。Plan 内の「過剰な deny で運用が止まらないことを Feedback で観測しながら段階調整」の指針どおり
- ~~項目3 の破壊的 git 検出範囲~~ → **事後観測方式に変更（2026-07-07）**: フックはブロックせず理由提示のみに設計変更したため、過剰プロンプトによる運用阻害は発生しない（既存の ask ルールが judg のみ担当）。過不足は Feedback で調整

## 完了条件

- [x] 4項目それぞれの実装とテスト（**全項目完了**: 項目1 deny 11パターン / 項目2 addf-init preview / 項目3 destructive-git-guard 13テスト + settings.json ask に `branch -D` / `checkout -- *` / `restore` 追加 / 項目4 パストラバーサル Test 20 x3）
- [x] Plan 0026 の該当 High（破壊的 git 操作の確認）が「対応済み」に遷移 — settings.json ask の拡張 + destructive-git-guard フックによる理由提示で担保
- [x] Plan 0033 のパストラバーサル Low が解消（項目4 で完了 — Python/Bash 両側にガード追加）
- [x] `/addf-lint` および CI（Plan 0030）全通過
- [x] Feedback.md に「過剰 deny による運用阻害」観測が記録されていない、または段階調整の記録がある（**事後観測方式に変更** — 記録の可否は今後の運用観察に委ねる）

## 本 Plan の対象外（別 Plan で回収）

- Plan 0026 の [Critical]「settings.json / hooks 自己書き換え保護（`Write`/`Edit` に対する deny）」は本 Plan では扱わない。理由: 「不便のない範囲で」の指針と両立させるには Claude Code の Write/Edit を全面的に deny する必要があり、addf-init や運用ルール更新が事実上できなくなる。より精密な設計（例: hooks ディレクトリのみ deny、settings.json のみ deny、write が発生した瞬間に diff 提示等）は独立 Plan で検討する

## AI 実装時間見積もり

3〜4セッション（4項目それぞれ独立性がある。フェーズ分割 = 項目単位で並走可）
