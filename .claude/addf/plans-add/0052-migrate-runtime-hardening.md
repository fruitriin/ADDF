# Plan 0052: マイグレーション実行時耐障害性の強化（Issue #26 実測回収）

## 実装状況: 完了（2026-07-11。項目1〜4を全て実装。code-review Critical1件・Warning2件・Low1件、doc-review Warning3件、contribution-agent Medium2件・Low1件を全て反映。run-all.sh・/addf-lint 全通過）

> 出典: GitHub Issue #26「v0.6.0 移行の実測レポート」。wardrobe-test（ダウンストリーム上流リポジトリ）で
> v0.5.0 → v0.6.1 の `/addf-migrate` を実施した実測報告。`migrate-paths.py check` の「rewrite 射程外候補」
> 警告は的中率が高く、実際に GUI バイナリの無限ハングを含む実害が発生した。

## 関連 Plan

- [Plan 0037: ADDF ディレクトリ集約](0037-addf-directory-consolidation.md) — 本 Plan が対象とする移行基盤（migrate-paths.py・addf-migrate.md Phase 2.5・lint-residual-paths.py）を実装した Plan。本 Plan はその実運用（初のダウンストリーム実測）で顕在化した穴を回収する

## 目的

`/addf-migrate` の v0.6.0 ディレクトリ大移行（Phase 2.5）を、初のダウンストリーム実測（Issue #26）で
判明した4つの実害・設計限界に対して補強する。特に GUI バイナリの無限ハングは CI・cron を無期限に
専有する重大度の高い実害であり、手順書の注記だけでなく機械的なガードレールを入れる。

## 現状の挙動

- `map-driven-migration-tool.md` knowhow には「rewrite の射程外 — 5類型」が既に記録されており、
  類型1（相対階層参照）・類型2（分割断片・バイナリ内含む）・類型3（書き込み先の親ディレクトリ）は
  ADDF 本体移行（Plan 0037）時点で判明済みだった。今回の Issue はこれらがダウンストリームでも
  同型で再現することを実測で裏付けたが、**類型2（GUI バイナリ）が「テスト失敗」に留まらず
  「画面収録権限ダイアログ待ちで無限ハング」という質的に異なる重さの実害になる**ことは
  未記録だった
- `addf-migrate.md` 6.3 の「ディレクトリ丸ごと移動の混在確認」は `addfTools`・`templates`・`tests`・
  `optional` の4ディレクトリのみを対象にしており、同じく丸ごと移動される `docs/guides/` が <!-- residual-path: allow -->
  対象リストに含まれていない
- `addf-migrate.md` 14.6 は `.gitignore` の **ADDF マーカーブロックのみ**を対象にしており、
  ブロック外にダウンストリームが独自に置いた旧位置ベースの ignore パターン
  （例: `.claude/Progress.md`）が新位置移動後にマッチしなくなり意図せず追跡される問題は <!-- residual-path: allow -->
  スコープ外
- `.claude/addf/tests/tools/test-binary-checksums.sh` Test 15 は実プロジェクトの `CLAUDE.repo.md` を
  `cp` するが、同ファイルを持たない構成（ダウンストリームの一部）では `cp` 自体が失敗し ERROR になる
- `.claude/addf/tests/tools/test-tools.sh` の window-info 呼び出しに `timeout` ラップがなく、
  disabled 判定が何らかの理由で失敗すると実際の GUI 情報取得処理に入り無期限にハングしうる
  （今回は移行後の旧パス参照が原因だったが、ガードレールとしては原因によらず時間で打ち切るべき）

## 変更内容（項目・フェーズ）

### 項目1: GUI バイナリ無限ハング対策（timeout ガード + 手順書注記）

- **対象**: `.claude/addf/tests/tools/test-tools.sh`
  - window-info の呼び出しに `timeout <N>s` を追加し、disabled 判定に失敗してもプロセスが
    無期限に居座らないようにする（原因によらない機械的ガードレール）。capture-window は
    本テストでは存在確認のみで実行していないため対象外（capture-window.swift にも同型の
    disabled 判定があり同種のリスクは残るが、実行箇所自体が本テストに無い）
- **対象**: `.claude/commands/addf-migrate.md` ステップ6.7（射程外4類型）
  - 類型2（分割断片）の説明に「GUI 系バイナリを含む場合は、ソース修正・再ビルド・checksums 更新に
    加えて **timeout 付きで実際に実行して確認する**」旨を明記する
- **対象**: `.claude/addf/knowhow/ADDF/map-driven-migration-tool.md`
  - 「rewrite の射程外 — 5類型」の類型2に、ダウンストリーム実測（Issue #26）で判明した
    「disabled 判定失敗 → 画面収録権限ダイアログ待ちで9時間ハング」の実害を追記する

### 項目2: `docs/guides/` の混在確認をディレクトリ丸ごと移動チェックに追加 <!-- residual-path: allow -->

- **対象**: `.claude/commands/addf-migrate.md` ステップ6.3
  - 混在確認コマンドの対象ディレクトリ一覧（`addfTools templates tests optional`）に `guides` を追加する
  - `docs/plans` 等（サブディレクトリ単位の存在≠所有判定）とは扱いが異なる理由 <!-- residual-path: allow -->
    （guides はサブディレクトリ分割がなく丸ごと移動される）を一言添える
  - 根拠: `existing-project-install-pattern.md`（干渉チェック3カテゴリ表）で
    `.claude/addf/guides/` は既に `templates`・`tests`・`optional` と同格の「無条件コピー」対象として
    扱われている。addf-init 側の分類と addf-migrate 側の混在確認対象が食い違っていたのが今回の穴
  - checklist-backing-lint 対応: 既存の混在確認コマンド（bash ループ）に対象ディレクトリを
    1つ追加するだけのため、追加後も既存の実行チェック（コードブロック）による裏付けが継続する

### 項目3: `.gitignore` 旧位置パターンの見直し注記

- **対象**: `.claude/commands/addf-migrate.md` の apply 完了メッセージ相当の案内（ステップ6.4 付近）
  - apply（git mv）実行後、「`.gitignore` のブロック外に旧位置ベースの独自パターン
    （例: `.claude/Progress.md`）がないか確認する」注記を追加する <!-- residual-path: allow -->
  - checklist-backing-lint 対応: この注記はコード側では検証しきれない目視確認のため
    `<!-- human-judgment -->` マーカーを付ける（6.3・6.8 の既存の目視確認項目と同じ扱い）
- **対象**: `.claude/addf/addfTools/lint-residual-paths.py`
  - `.gitignore` 内（ADDF マーカーブロック外）に、移動済みパスの旧位置文字列が
    パターンとして残っていないかを検知する軽量チェックを追加する（WARNING 級 — `map-driven-migration-tool.md`
    が既に指摘する「git 追跡外ファイルも走査対象外で旧パスが残る」と同型の穴に対する機械的な補完。
    `sync-lint-design.md` の責務別 exit code 表に従い、受動的 lint のため配布先での誤 ERROR を避ける）

### 項目4: `test-binary-checksums.sh` Test 15 の CLAUDE.repo.md 不在フォールバック

- **対象**: `.claude/addf/tests/tools/test-binary-checksums.sh`
  - Test 15 の `cp "$PROJECT_DIR/CLAUDE.repo.md"` が失敗する場合（ファイル不在）、ERROR ではなく
    SKIP にフォールバックする（`sync-lint-design.md` の「addfTools はダウンストリーム配布を前提に
    欠如=SKIP で設計する」方針に揃える）。`CLAUDE.repo.md` は @メンションで
    `CLAUDE.repo.example.md` を参照する構造のため、後者だけが欠けている構成でも同様に SKIP
    する（片方だけのチェックだと cp 失敗を無視したまま後続の assert がスプリアスな FAIL に
    なりうる — コードレビューで検出）
  - **SKIP 乱用への注意**（`sync-lint-design.md` が引く Issue #19 の教訓）: `CLAUDE.repo.md` 不在は
    「必須ランタイムの不在」ではなく「プロジェクト構成の正当な差異」（本 Plan もダウンストリームの
    `CLAUDE.repo.md` 不在構成が実在することを Issue #26 で確認済み）であるため SKIP が妥当。
    サイレント無効化にしないよう、SKIP 時は理由（`CLAUDE.repo.md not found — skipping upstream
    classification test` 等）を出力に残す

## 影響範囲

- `.claude/commands/addf-migrate.md`（手順書。ダウンストリームへの配布対象）
- `.claude/addf/addfTools/lint-residual-paths.py`（配布対象ツール）
- `.claude/addf/tests/tools/test-tools.sh`・`test-binary-checksums.sh`（配布対象テスト）
- `.claude/addf/knowhow/ADDF/map-driven-migration-tool.md`（ADDF 由来ノウハウ。配布対象）
- 同期ペア（lint-template-sync）への影響なし（いずれも片側単独ファイルの変更）

## テスト方針

- 項目1: `test-tools.sh` に timeout 追加後、既存の disabled 判定テストが通ることを確認する
  （timeout 値は通常実行時間より十分長く、かつ CI を専有しない範囲で設定する）
- 項目3: `lint-residual-paths.py` の新チェックについて、ドリフト注入 TDD
  （`.gitignore` に旧位置パターンをわざと残した状態を作り、WARNING で検出されることを確認）
- 項目4: `CLAUDE.repo.md` を欠いたサンドボックスで Test 15 を実行し、SKIP になることを確認
- 全項目適用後、`bash .claude/addf/tests/run-all.sh` を実行し既存テストに regression がないことを確認

## 破壊的変更の許容範囲

なし（手順書注記・テストのガードレール追加・lint の検知範囲拡大のみで、既存の合格基準は変えない）

## 要オーナー確認

- 項目1の `timeout` 秒数は暫定値で実装し、実運用で不足が観測されたら Feedback.md に記録して
  調整する運用でよいか（Plan 0043 の「事後観測方式で段階調整」と同じ扱いを想定）

## 完了条件

- [x] `test-tools.sh` の window-info 呼び出しが timeout 付きになっている
- [x] `addf-migrate.md` 6.7 に GUI バイナリの再ビルド+timeout付き動作確認注記が追加されている
- [x] `map-driven-migration-tool.md` 類型2に9時間ハングの実測が追記されている
- [x] `addf-migrate.md` 6.3 の混在確認対象に `guides` が追加されている
- [x] `addf-migrate.md` に `.gitignore` 旧位置パターン見直しの注記が追加されている
- [x] `lint-residual-paths.py` が `.gitignore` 内の旧位置パターン残存を WARNING で検知する
- [x] `test-binary-checksums.sh` Test 15 が `CLAUDE.repo.md` 不在時に SKIP になる
- [x] `bash .claude/addf/tests/run-all.sh` が通過する
- [x] `/addf-lint` が通過する（同期ペア・チェックリスト裏付け含む）

## AI 実装時間見積もり

1セッション以内（4項目とも局所的な追記・小規模な条件分岐追加で完結する規模）
