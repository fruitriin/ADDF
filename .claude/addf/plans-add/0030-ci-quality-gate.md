# Plan 0030: CI 品質ゲート（GitHub Actions で run-all.sh + lint 一式を自動実行）

## 実装状況: 一部完了（実装・CI 実地検証済み 2026-07-05。branch protection の要否のみオーナー判断待ち）

owner_feedback: 待ち
feedback_ask: main への branch protection（PR 必須化）を有効にするか
feedback_since: 2026-07-05

> 実装完了・CI 実地検証済み（2026-07-05）: (1) 緑実行=run 28745383490 (2) ERROR 注入 fail=
> 使い捨て PR #23 で failure 確認 (3) WARNING annotation=ペア6警告の黄色表示を確認
> (4) ubuntu で macOS 専用テストが「3 skipped」と明示計上。副産物: 初回 CI が
> test-speculate-integrate.sh の git user 未設定依存（ローカルでは検出不能の環境差異）を
> 初日に検出し修正（92b2264）— CI の存在意義の即日実証。
> 残る完了条件は branch protection の要否（オーナー判断）のみ。

## 目的

PR・push ごとに `bash .claude/addf/tests/run-all.sh` と lint スクリプト一式を GitHub Actions で自動実行し、
品質ゲートを「エージェントの意思」から「機械」へ移す。

## 背景

- 現在このリポジトリに CI は存在しない（`.github/workflows/` なし）。テスト・lint は
  Progress.md の品質検証ステップでエージェントが手動実行しており、実行忘れ・環境差異・
  「今回は大丈夫と判断する」失敗モードが残っている
- `.claude/addf/knowhow/ADDF/sync-lint-design.md` の教訓「意思で覚えるが3度敗北したら機械化する」の
  到達点は CI である。同 knowhow は当初から「検出 = 決定的スクリプト: 忘れない・揺らがない・**CI に乗る**」
  を設計目標に掲げており、lint 群は CI 搭載を前提に exit code 3値（0 OK / 1 ERROR / 2 WARNING）で
  設計済み。乗せる先が無いのが現状のギャップ
- 非 macOS 環境でのバイナリ実行テストは SKIP 済み（PR #15）のため、ubuntu ランナーで
  run-all.sh がそのまま動く土台はできている

## 設計の骨子

### 1. ワークフロー構成（案）

`.github/workflows/test.yml`（ubuntu-latest）:

1. `bash .claude/addf/tests/run-all.sh` — フック・ツールテスト（非 macOS の Mach-O テストは SKIP）
2. lint スクリプト一式（9本）を個別ステップで実行（どれが落ちたか Actions 上で判別できるように）:
   - `lint-json.py` / `lint-toml.py` / `lint-frontmatter.py`
   - `lint-template-sync.py`（ペア1〜6）
   - `lint-hooks-exec.py` / `lint-hooks-wiring.py`
   - `lint-checklist.py` / `lint-plan-status.py`
   - `sync-optional-skills.py`（引数なし = チェックモード。`apply` 指定時のみ変更系になるため CI では引数を付けない）

### 2. exit code 3値の CI マッピング

- `1 = ERROR` → ジョブ失敗（マージブロック）
- `2 = WARNING のみ` → ジョブは通す。ただし GitHub Actions の
  [workflow command](`::warning::`) で annotation を出し、PR 上で可視化する（案）
- WARNING を落とすか通すかは lint ごとに性質が違う可能性があるため、着手時に各 lint の
  WARNING 項目を棚卸しして決める

### 3. アップストリーム / ダウンストリーム分離

- `.github/workflows/` は **ADDF 本体固有**とし、addf-init のコピーリスト対象外とする
  （ダウンストリームの CI 事情はプロジェクトごとに異なるため押し付けない）
- ダウンストリームが同じゲートを欲しい場合に向けて、ワークフローの雛形を
  `.claude/addf/guides/` に例示するか、`.claude/addf/optional/` 機構（Plan 0029 フェーズ1）に乗せるかは未決
- CLAUDE.md からワークフローを参照しない限り lint ペア5（参照⇔コピーリスト被覆）への影響はない

## 影響範囲

- `.github/workflows/test.yml`（新規）
- `.github/scripts/run-lint.sh`（新規 — exit code 3値マッピングの共通ラッパー）
- `README.md` / `README.en.md`（CI バッジ）
- `.claude/addf/guides/setup.md`（「実運用の参考」に1行追記）

## 未決事項の決定（2026-07-05 実装時）

1. **WARNING（exit 2）の扱い** — **全 lint 一律「通す + `::warning::` annotation」**とする。
   根拠: lint 側が既に ERROR / WARNING の重要度を設計済み（sync-lint-design.md の exit code 3値）であり、
   CI が lint ごとに重要度を上書きする二重管理を持ち込まない。個別設定（特定 lint の WARNING を
   fail に昇格する等）は「annotation が見過ごされて実害が出た」実績が出てから検討する。
   実装は共通ラッパー `.github/scripts/run-lint.sh`（9ステップ×同一分岐のため `run:` 内に
   複製せず切り出した）
2. **Python バージョンの固定** — **uv（astral-sh/setup-uv）+ `uv run --python 3.11` で固定**する。
   根拠: ローカルの `/addf-lint` と同一コマンドになり再現性が揃う。PEP 723 のサードパーティ依存
   （lint-frontmatter.py の pyyaml）も uv が自動解決する。ランナー既定の python3 は
   イメージ更新でバージョンが動く（ドリフト源）。setup-uv はメジャー浮動タグを提供しないため
   完全バージョン（v8.3.0）で pin した
3. **スキルテスト** — **CI 対象外のまま維持**する。run-all.sh が既に
   「▶ Skill Tests (manual)」セクションで一覧をログ表示するため、追加実装なしで
   「一覧表示だけ CI ログに出す」が満たされる
4. **push トリガーの範囲** — **pull_request + main への push の両方**とする。
   根拠: このリポジトリは main 直 push 運用が主のため、PR のみでは大半の変更がゲートを通らない
5. **ダウンストリーム配布形態** — **配布しない**（addf-init のコピーリストに `.github/` が
   含まれないことを確認済み — 変更不要）。ガイド例示は `.claude/addf/guides/setup.md` の
   「実運用の参考」への1行（本体の test.yml を雛形として参照できる旨）に留める。
   optional 機構には乗せない — CI 事情はプロジェクトごとに異なり、押し付けない方針を維持する
6. **fetch-depth: 0（全履歴取得）** — lint-template-sync の WARNING に最終更新日ヒント
   （git log）を併記するため。浅い clone だと日付ヒントが欠落する
7. **setup-uv の pin（v8.3.0）** — メジャー浮動タグが提供されないため完全バージョンで pin する。
   更新方針: リリース時（/addf-release）に最新バージョンを確認して更新する

## ゲートの実態と branch protection（要オーナー確認）

- **現状この CI は merge を止めない**。main の branch protection が未設定のため、実態は
  「事後検知ネット + PR チェック表示」であり、赤 ✗ が出ても push / merge は物理的に
  ブロックされない（「ゲート」という名前より弱い — 正直化のため明記）
- 真の「ゲート」にするには、main の branch protection で `test` を
  **required status check** に設定する必要がある。これはリポジトリ設定の変更 =
  **オーナー判断**（main 直 push 運用との相性・緊急時のバイパス手段も含めて判断する）
- main への直 push の WARNING annotation は PR 画面が無く目に入りにくい。当面は
  **Actions タブを能動的に確認する運用**とし、見過ごしによる実害が出たら
  WARNING の fail 昇格を検討する（未決事項1の方針と整合）


## branch protection 判断（オーナー・2026-07-06）

**方針**: workflow 化（現状）は良い。branch protection 化は**保留 — 実測ベースで段階的に判断**する。

考察軸（オーナー指示）:

1. **protection されたときに直しきれるかどうか**: main 直 push 運用の下で、CI が誤検知や環境差異で fail した場合、直しきれる粒度か？（今回 test-speculate-integrate.sh が git config ローカル要件で fail した実例あり — こういう「非本質的 fail」でも main への直 push がブロックされる）
2. **直せないときにブロッカーにならないか**: リリース直前などで「今すぐ緊急 push したい」場合に、CI が長時間 fail 状態だとブロッカーになる懸念。バイパス手段（--no-verify 相当）を lint と同様に用意するか
3. **恒常的にブロッカーなら警告のみのブロックなしに格下げ可能か**: GitHub Actions の required check は「必ず fail をブロック」だが、Rulesets の non-blocking mode（GitHub Enterprise 提供機能・Public リポジトリでは範囲限定）や、「ブランチルール = allow admin bypass」設定で運用可能性を上げられる

**判断基準（当面）**: 
- CI が緑を安定して維持できる期間（1〜2週間）を実測する
- その間に「非本質的 fail」の頻度・回復時間を観察する
- 落ち着いていれば required check 化を検討。頻繁に fail が非本質的原因なら「警告のみ」運用（Rulesets の non-blocking を使うか、branch protection を諦めて Actions Annotations のみに留めるか）

**次アクション**: 実測期間を経て再判断（本 Plan の Q として残す方針。実測記録は Feedback.md の該当セクションで蓄積）

## 完了条件

- [x] 初回 CI 実行の確認（2026-07-05 実施）:
  (1) 緑の実行を確認する — run 28745383490 success
  (2) **意図的に ERROR を注入した使い捨てブランチを push し、fail することを確認する** — PR #23 で failure・「lint が ERROR を報告しました」annotation を確認、検証後 PR クローズ・ブランチ削除済み
  (3) ダミー WARNING を注入して `::warning::` annotation の表示を確認する — 同 PR でペア6 WARNING の黄色 annotation を確認
  (4) ubuntu ランナーで macOS 専用テストが SKIP としてログの Results 行に計上されることを確認する — 「Test 2-4: SKIP」「Results: 5 passed, 0 failed, 3 skipped」を確認
- [x] オーナーが branch protection の要否を判断する（2026-07-06: 実測期間を経て再判断・上記「branch protection 判断」節参照） <!-- human-judgment -->
- [x] Progress.md の品質検証ステップとの関係が整理されている
  （CI があってもローカル実行ステップは残す — CI は網、ローカルは即時フィードバック。
  Progress.md 側の変更は不要と判断）

## 関連

- `.claude/addf/knowhow/ADDF/sync-lint-design.md` — exit code 3値・SKIP 設計・「意思で覚えない」思想
- Plan 0021 / 0022 / 0024 / 0027 / 0029（sync-optional-skills check）— CI に乗せる lint 群を整備した一連の計画
- PR #15 — 非 macOS でのバイナリテスト SKIP（ubuntu ランナーの前提）
- Plan 0031 — バイナリのチェックサム照合を CI に載せる場合、本 Plan のワークフローに相乗りする
