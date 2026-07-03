# Plan 0030: CI 品質ゲート（GitHub Actions で run-all.sh + lint 一式を自動実行）

## 実装状況: 未着手

> **粗々の起票**: 設計の方向性と未決事項を出す段階。実装詳細は着手時に詰める。

## 目的

PR・push ごとに `bash .claude/tests/run-all.sh` と lint スクリプト一式を GitHub Actions で自動実行し、
品質ゲートを「エージェントの意思」から「機械」へ移す。

## 背景

- 現在このリポジトリに CI は存在しない（`.github/workflows/` なし）。テスト・lint は
  Progress.md の品質検証ステップでエージェントが手動実行しており、実行忘れ・環境差異・
  「今回は大丈夫と判断する」失敗モードが残っている
- `docs/knowhow/ADDF/sync-lint-design.md` の教訓「意思で覚えるが3度敗北したら機械化する」の
  到達点は CI である。同 knowhow は当初から「検出 = 決定的スクリプト: 忘れない・揺らがない・**CI に乗る**」
  を設計目標に掲げており、lint 群は CI 搭載を前提に exit code 3値（0 OK / 1 ERROR / 2 WARNING）で
  設計済み。乗せる先が無いのが現状のギャップ
- 非 macOS 環境でのバイナリ実行テストは SKIP 済み（PR #15）のため、ubuntu ランナーで
  run-all.sh がそのまま動く土台はできている

## 設計の骨子

### 1. ワークフロー構成（案）

`.github/workflows/test.yml`（ubuntu-latest）:

1. `bash .claude/tests/run-all.sh` — フック・ツールテスト（非 macOS の Mach-O テストは SKIP）
2. lint スクリプト一式を個別ステップで実行（どれが落ちたか Actions 上で判別できるように）:
   - `lint-json.py` / `lint-toml.py` / `lint-frontmatter.py`
   - `lint-template-sync.py`（ペア1〜6）
   - `lint-hooks-exec.py`
   - `lint-checklist.py`
   - `sync-optional-skills.py check`

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
  `docs/guides/` に例示するか、`.claude/optional/` 機構（Plan 0029 フェーズ1）に乗せるかは未決
- CLAUDE.md からワークフローを参照しない限り lint ペア5（参照⇔コピーリスト被覆）への影響はない

## 影響範囲

- `.github/workflows/test.yml`（新規）
- `README.md`（CI バッジ・「テスト」セクションへの追記。あれば）
- `docs/guides/`（ダウンストリーム向け雛形を置く場合）

## 未決事項（粗々ゆえ）

- WARNING（exit 2）の扱い: 全 lint 一律「通す + annotation」か、lint ごとに設定するか
- Python バージョンの固定（ランナー既定の python3 で足りる見込みだが、再現性のため固定するか）
- スキルテスト（自然言語シナリオ・手動実行）は CI 対象外のまま維持する想定。
  一覧表示だけ CI ログに出すか
- push トリガーの範囲: PR のみか、main への push も含めるか
- ダウンストリーム配布形態（ガイド例示 / optional 機構 / 配布しない）

## 完了条件（暫定）

- PR 作成時に run-all.sh + lint 一式が自動実行され、ERROR で fail する
- ubuntu ランナーで macOS 専用テストが SKIP として報告される（silent truncation にしない）
- Progress.md の品質検証ステップとの関係が整理されている
  （CI があってもローカル実行ステップは残す — CI は網、ローカルは即時フィードバック）

## 関連

- `docs/knowhow/ADDF/sync-lint-design.md` — exit code 3値・SKIP 設計・「意思で覚えない」思想
- Plan 0021 / 0022 / 0024 / 0027 / 0029（sync-optional-skills check）— CI に乗せる lint 群を整備した一連の計画
- PR #15 — 非 macOS でのバイナリテスト SKIP（ubuntu ランナーの前提）
- Plan 0031 — バイナリのチェックサム照合を CI に載せる場合、本 Plan のワークフローに相乗りする
