# Plan 0059: downstream テスト環境適合 — upstream 前提テストの SKIP 化と書式受理（Issue #30・#31 回収）

## 実装状況: 未着手

owner_feedback: 不要

> 出典: GitHub Issue #30（test-template-sync.sh の make_sandbox() が ProgressTemplate.addf.md を
> 無条件 cp して downstream で必ず失敗する — MagiaMagica 実測）・Issue #31（v0.6.1 移行後の
> downstream で 2 テストスイート失敗と lint ペア6 誤検出 — 下流で対処実装・テスト済みの上流反映提案）

## 関連 Plan

- [Plan 0055: taskbar.fm 移行フィードバック回収](0055-downstream-migration-feedback-taskbar.md) — Issue #29（同じ「downstream で必ず FAIL」欠陥クラス）の先行対応。本 Plan はその残存同型（#30）と別ダウンストリームからの追加報告（#31）の回収
- [Plan 0052: migrate ランタイム強化](0052-migrate-runtime-hardening.md) — Test 15 の SKIP フォールバック（wardrobe-test 由来）の先行対応。#31 現象2 と突き合わせて残作業を確定する

## 目的

正当な downstream プロジェクトで `bash .claude/addf/tests/run-all.sh` と `lint-template-sync.py` が
誤 FAIL / 誤 WARNING を出さない状態にし、addf-migrate の完了ゲート（Phase 2.5 ステップ6.7）を
downstream でも機能させる。

## 現状の挙動

1. **Issue #30**: `test-template-sync.sh` の `make_sandbox()` が
   `ProgressTemplate.addf.md`（`*.addf.md` = 本体専用・downstream 非配布）を無条件 `cp` するため、
   downstream で `make_sandbox()` を呼ぶ全テストが連鎖失敗する。直前行の `README.en.md` は
   Issue #29 対応で条件付き cp 化済みなのに、直後の行だけ同型の見落としとして残った
2. **Issue #31 現象1**: `lint-template-sync.py` の `todo_table_rows()` がバックティック書式
   `` `path` `` のみ受理し、downstream で広く使われる markdown リンク書式 `[title](path)` を
   受理しない → 全 Plan が「TODO 登録漏れ」WARNING 誤検出（ペア6）。下流では Plan 0006 →
   migrate 上書き失効 → Plan 0009 再適用と、3度目の適合作業になっている
3. **Issue #31 現象2・3**: `test-binary-checksums.sh` Test 15（upstream 判定期待のハードコード）と
   `test-template-sync.sh` Test 1（pair2/3 が SKIP されない主張）・Test 19（実 Progress.md 内容
   依存）が downstream で原理的に FAIL する

## 変更内容（項目・フェーズ）

### 項目1: make_sandbox() の条件付き cp 化（Issue #30）

- **対象**: `.claude/addf/tests/tools/test-template-sync.sh`
- `ProgressTemplate.addf.md` を `README.en.md` と同じ存在チェック付き cp にする（Issue #30 の修正案どおり）
- Issue #31 の下流対処にある「不在時は `ProgressTemplate.md` を疑似コピーして upstream 環境を
  シミュレート」方式も比較検討し、テストの検査能力を落とさない方を採る

### 項目2: todo_table_rows() の両書式受理（Issue #31 現象1）

- **対象**: `.claude/addf/addfTools/lint-template-sync.py`
- `TODO_PLAN_PATH_RE` をバックティック書式と markdown リンク書式の両対応にする
  （Issue に下流実装済みの正規表現と `m.group(1) or m.group(2)` パターンが提示済み。破壊的変更なし）
- 回帰テストを追加する（下流では Test 11.5 / 11.6 として実装済み — 同等のものを取り込む）

### 項目3: `.claude/addf/lock.json` を下流シグナルとする SKIP パターン（Issue #31 現象2・3）

- **対象**: `test-binary-checksums.sh` Test 15 / `test-template-sync.sh` Test 1・19
- lock.json の存在（= 配布された downstream 環境）で upstream 前提ケースを SKIP に格下げする
- Plan 0052 で導入済みの Test 15 SKIP フォールバックとの重複・差分を確認し、残る穴のみ塞ぐ

### 項目4（検討）: CI での「配布状態を模した downstream 環境」テスト実行

- **対象**: `.github/workflows/`（Plan 0030 の CI 品質ゲート）
- Issue #31 提案3。同欠陥クラス（upstream 前提の暗黙仮定）の再発を CI で機械検出する。
  addf-init 相当のコピーを CI 内で行い run-all.sh を回す構成を検討。規模が大きければ
  別 Plan に切り出してよい

## 影響範囲

- テストインフラのみ（`lint-template-sync.py` の受理拡張は非破壊）。ダウンストリーム配布対象ファイルのため addf-contribution-agent の検査対象
- Feedback.md の教訓「このアサーションは Plan が0件の空のダウンストリームリポジトリでも成立するか？」の適用対象そのもの

## テスト方針

- ドリフト注入: downstream を模したサンドボックス（`*.addf.md` 不在・lock.json あり・markdown リンク書式 TODO）で run-all.sh 相当を実行し、FAIL しないことを検証する
- 既存テストの upstream 環境での通過を維持する（検出能力の劣化がないこと）

## 破壊的変更の許容範囲

なし（受理書式の拡張と SKIP 格下げのみ）

## 要オーナー確認

なし（Issue に下流実測・実装済みの対処が揃っており方針は明確）

## 完了条件

- [ ] downstream 模擬サンドボックスで `test-template-sync.sh`・`test-binary-checksums.sh` が FAIL しない（新規回帰テストで機械検証）
- [ ] markdown リンク書式の TODO 行がペア6で誤検出されない回帰テストが PASS する
- [ ] upstream（本体リポジトリ）での `bash .claude/addf/tests/run-all.sh` 全通過を維持する
- [ ] Issue #30・#31 へ対応内容を返信する <!-- human-judgment: 返信文はオーナー確認後に投稿する -->

## AI 実装時間見積もり

1セッション以内（項目4を切り出す場合）
