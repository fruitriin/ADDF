# Plan 0055: ダウンストリーム移行フィードバック（taskbar.fm・Issue #27〜#29）回収

## 実装状況: 完了（2026-07-14。3体レビュー（code-review Critical1件・Warning2件・Suggestion2件、doc-review Critical1件・Warning3件、contribution-agent 分離パターン違反なし・軽微指摘2件）を全て反映。code-review の Critical 指摘〔動的アサーションが恒真式になっていた〕は独立オラクル方式に書き換えて解消し、その過程で strip_fences 漏れの実バグを検出・修正した）

> 出典: taskbar.fm（ダウンストリームプロジェクト。`CLAUDE.repo.md` に downstream 宣言あり）で
> v0.4.0 → v0.6.2 の `/addf-migrate` を実行した際の実測フィードバック。GitHub Issue #27・#28・#29
> として報告された。

## 関連 Plan

- [Plan 0052: マイグレーション実行時耐障害性の強化](0052-migrate-runtime-hardening.md) — 同じ実測系フィードバック（Issue #26・wardrobe-test）の先行対応。本 Plan は別ダウンストリーム（taskbar.fm）からの後続フィードバック

## 目的

taskbar.fm での `/addf-migrate` 実運用で見つかった3件の設計不備を解消する:
1. downstream で実行すると原理的に必ず FAIL するテストアサーションの修正（Issue #29）
2. `*.addf.md` 除外規則の説明が曖昧で `addf-init.md` を読みに行く追加コストが発生した問題の解消（Issue #28）
3. 旧版の `addf-migrate.md` で実行を開始してしまうリスクへの事前検知の追加（Issue #27）

## 現状の挙動

### Issue #29: downstream で必ず FAIL するテスト

- `test-binary-checksums.sh` Test 15 は `$PROJECT_DIR/CLAUDE.repo.md` を実プロジェクト構成の
  まま sandbox にコピーし、「upstream 判定 → ERROR」を固定でアサートしていた。ADDF 本体
  （upstream 宣言）で実行される前提のため、downstream 宣言のプロジェクトが自身の `run-all.sh`
  経由で実行すると常に FAIL する
- `test-template-sync.sh` Test 1 も同様に、`$PROJECT_DIR` を対象に lint を実行し「pair1〜3 が
  SKIP されない」ことを固定でアサートしていた。downstream 宣言のプロジェクトでは pair1〜3 が
  正当に SKIP されるため常に FAIL する
- `make_sandbox()` が `README.en.md` を無条件 `cp` しており、英語版 README を持たない
  downstream プロジェクトでは `cp: No such file or directory` のノイズが出る

### Issue #28: `*.addf.md` 除外規則の説明が曖昧

- `addf-migrate.md` の除外規則の説明文と、`CHANGELOG.md` の v0.6.0 移行ガイドの
  `Release.addf.md` に関する注記（「`.addf.md` サフィックスは配布除外規則の判定パターンの
  ため維持」）が、「ダウンストリームにも配布してよい」という意味に読める余地を残していた

### Issue #27: 旧版の `addf-migrate.md` で開始してしまうリスク

- 旧版（v0.5.0 以前）の `addf-migrate.md` で `/addf-migrate` を開始すると、Phase 2.5
  （v0.6.0 で新設されたディレクトリ大移行）を知らないまま Phase 3 以降に進んでしまう
- `CHANGELOG.md` の `[0.6.0]` エントリに事後救済（2周目で Phase 2.5 が発動する）の案内は
  あるが、これは気づかず進めてしまうことを前提にした救済策であり、事前検知の手段がなかった

## 変更内容（項目・フェーズ）

### 項目1: test-binary-checksums.sh Test 15 の動的アサーション化

- **対象**: `.claude/addf/tests/tools/test-binary-checksums.sh`
- Test 15 の目的（「@メンション経由の種別解決が疎通しているか」の regression guard）は
  upstream/downstream いずれの宣言でも成立する。実プロジェクトが実際に宣言している種別
  （出力に含まれる `repo_kind=upstream` / `repo_kind=downstream`）に応じてアサーションを
  分岐させ、判定不能（`repo_kind=` がどちらも出ない状態）への転落だけを regression として
  検出するよう変更した。upstream/downstream 個別の分岐仕様そのものは Test 5〜8 が別途カバー
  しているため重複しない

### 項目2: test-template-sync.sh Test 1 の動的アサーション化と README.en.md cp のガード

- **対象**: `.claude/addf/tests/tools/test-template-sync.sh`
- Test 1 の pair1〜3 SKIP 判定を、実際の lint 出力に `[N] SKIP` が含まれるかどうかで分岐
  させた（downstream 宣言なら SKIP されることを、upstream 宣言なら SKIP されないことを、
  それぞれ positive にアサートする）
- `make_sandbox()` の `README.en.md` cp を存在チェック付きに変更し、英語版 README を
  持たないダウンストリームでの cp エラーノイズを解消した

### 項目3: `*.addf.md` 除外規則の説明強化

- **対象**: `.claude/commands/addf-migrate.md`（Phase 3 の除外規則説明）、
  `.claude/addf/CHANGELOG.md`（`[0.6.0]` 移行ガイドの `Release.addf.md` 改名注記）
- 「`*.addf.md` は例外なく ADDF 本体専用でダウンストリームには一切配布されない」ことと、
  「`.addf.md` サフィックスは除外規則の判定パターンという意味しか持たず、"ダウンストリーム
  でも保持してよい" という意味ではない」ことを明記した。`Release.addf.md` を除外規則の
  対象例として明示的に追加した

### 項目4: `addf-migrate.md` に手順書自身の自己点検フェーズを追加

- **対象**: `.claude/commands/addf-migrate.md`
- Phase 2（最新版取得）の直後に Phase 2.4「手順書自身の自己点検」を新設した。ローカルで
  実行中の `.claude/commands/addf-migrate.md` と、Phase 2 でクローンした最新版の同ファイルを
  `diff` で比較し、差分があれば「実行中の手順書自体が古い版です」と明示的にユーザーへ伝えた
  上で、以降は最新版の記述に従うよう案内する。事後救済（2周目で気づく設計）に加えて事前検知
  を追加した

## 影響範囲

- `.claude/addf/tests/tools/test-binary-checksums.sh`・`.claude/addf/tests/tools/test-template-sync.sh`
  （lint-template-sync ペア6・8 の対象外・純粋なテストロジック変更）
- `.claude/commands/addf-migrate.md`・`.claude/addf/CHANGELOG.md`（ドキュメントのみ。
  `addf-doc-review-agent` の起動条件に該当）
- ダウンストリームへの配布: 次回 `/addf-migrate` で downstream プロジェクトに反映される

## テスト方針

- `bash .claude/addf/tests/tools/test-binary-checksums.sh`・
  `bash .claude/addf/tests/tools/test-template-sync.sh` を個別実行し、upstream 環境
  （本リポジトリ自身）で全 PASS を確認
- `bash .claude/addf/tests/run-all.sh` で全体のリグレッションがないことを確認
- downstream 分岐（`repo_kind=downstream` → SKIP/exit 0）は Test 5〜8・Test 16〜18・23
  が既にシンセティックな downstream 宣言でカバー済みのため、本 Plan の変更は「実プロジェクト
  の宣言に応じてどちらの分岐でも regression guard が機能する」ことの確認に留める
  （taskbar.fm 環境そのものでの実地検証はダウンストリーム側の次回移行時に行われる）

## 破壊的変更の許容範囲

なし

## 要オーナー確認

なし（Issue の提案内容をそのまま採用。効果は次回ダウンストリームの `/addf-migrate` 実行時に
確認できる）

## 完了条件

- [x] Test 15（test-binary-checksums.sh）が upstream 宣言実行時も引き続き PASS する
- [x] Test 1（test-template-sync.sh）が upstream 宣言実行時も引き続き PASS する
- [x] `bash .claude/addf/tests/run-all.sh` が全通過する
- [x] `/addf-lint` がセクション6・9・12で ERROR/WARNING を出さない
- [x] `addf-migrate.md` に Phase 2.4（自己点検）と `*.addf.md` 除外規則の強化説明が入っている
- [x] `.claude/addf/CHANGELOG.md` の `Release.addf.md` 改名注記が明確化されている
- [x] コードレビュー・ドキュメントレビューの指摘を反映する

## AI 実装時間見積もり

1セッション以内
