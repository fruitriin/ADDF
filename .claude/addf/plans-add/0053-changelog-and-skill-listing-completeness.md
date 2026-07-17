# Plan 0053: CHANGELOG・README スキル一覧の網羅性回収と再発防止

## 実装状況: 完了（2026-07-11。別セッションが着手・本セッションが引き継いで完走。項目1〜5を全て実装。code-review・doc-review・contribution-agentのレビュー指摘（Critical/Warning計5件）を全て反映。うち1件（Plan 0026残Critical項目の誤記）はPlan 0054として切り出しTODO最優先登録。run-all.sh・/addf-lint 全通過）

edge: absorbed-into 0054

## 関連 Plan

- [Plan 0054: settings.json / hooks 自己書き換え保護](0054-settings-self-write-protection.md) — 本 Plan の doc-review で発掘された Plan 0026 の [Critical] 誤記から派生し、独立 Plan として切り出された

> 出典: バックログ枯渇時のオーナー標準リクエスト（TODO.addf.md「タスクが無くなったら
> プロジェクトの品質を向上させる計画を追加する」）。着手時の自己調査で、working tree に
> 前サイクル由来と見られる未コミットの CHANGELOG.md／README.md／README.en.md 差分
> （Plan 0039・0049・0051・0052 分のエントリ・エージェント表2行）を発見し、同種のドリフトが
> 他にも埋没していないか機械的に確認したところ、CHANGELOG 網羅性とスキル一覧網羅性の
> 2種類の実害を確認した（詳細は「現状の挙動」参照）。

## 目的

1. `.claude/addf/CHANGELOG.md`（`/addf-migrate` がダウンストリームに変更内容を伝える唯一の窓口）に、
   完了済みだが記載漏れになっている Plan のエントリを追記し網羅性を回復する
2. README.md / README.en.md のスキル一覧に掲載漏れの `addf-plan-audit` を追加する
3. スキル一覧の掲載漏れを機械的に検出する lint（`lint-template-sync.py` ペア8）を新設し、
   同型のドリフトが再発してもチャットの外（自動チェック）で気づけるようにする

## 現状の挙動

### 実害1: working tree に未コミットの CHANGELOG／README 差分が残っていた

着手時点で `git status` に以下の未コミット差分が存在していた（前サイクルが書きかけで
コミットし忘れたと見られる）:

- `.claude/addf/CHANGELOG.md`: Plan 0039（フェーズ2）・0044・0049・0051・0052 のエントリ追加
- `README.md` / `README.en.md`: エージェント表に `addf-doc-review-agent`・`addf-implementer` の
  2行を追加

内容を検証したところ正確だったため、本 Plan の実装に引き継いでそのままコミットする
（車輪の再発明はしない）。

### 実害2: CHANGELOG に記載されていない完了 Plan が実害1以外にも存在する

`.claude/addf/CHANGELOG.md` 全文と `TODO.addf.md` の完了 Plan 一覧を突き合わせたところ、
以下の Plan が「完了・ダウンストリーム配布物に影響する変更を含む」にもかかわらず
CHANGELOG に一切記載されていないことを確認した（`grep -c "\b<番号>\b" CHANGELOG.md` で
0 件かつ本文精読で機能記述としても未掲載と確認済み）:

| Plan | 内容 | 配布物への影響 |
|---|---|---|
| 0030 | CI 品質ゲート（GitHub Actions） | `.github/workflows/`（新規） |
| 0031 | バイナリ検証可能性（チェックサム照合） | `build.sh`・`checksums.sha256`・照合テスト |
| 0032 | knowhow 鮮度監査 | `.claude/addf/knowhow/ADDF/*.md`（配布対象） |
| 0035 | PR 標準フォーマット | `.claude/addf/guides/pr-format.md`（新規） |
| 0036 | `addf-plan-audit` スキル新設 | `.claude/commands/addf-plan-audit.md`（新規） |
| 0038 | 投機適性判定・大改造の窓検出 | `addf-dev.md`・`addf-speculate.md` |
| 0041 | コンテキスト枯渇時のループ継続教義（フェーズ1・2） | `addf-dev.md`・`context-reminder.py` |

一方、以下は意図的に記載なしで問題ない（除外理由を確認済み）:

- Plan 0024: 0.3.0 セクションに「Plan 0021, 0022, 0024」としてまとめ記載済み
- Plan 0034: 0.5.0 セクションに Issue 番号（#18/#20）ベースの機能記述として実質記載済み
  （Plan 番号を明示する現行の記法が定着する前の世代のため書式が異なるだけ）
- Plan 0026: 高優先度の残課題（破壊的 git 操作対策）は Plan 0043 で対応済みだが、
  [Critical]「settings.json / hooks 自己書き換え保護（Write/Edit への deny）」は
  Plan 0043 本文（92行目）で明示的にスコープ外とされ、独立 Plan は未作成のまま残っている
  （doc-review で誤記を指摘・訂正 — 旧記述「Plan 0043 に吸収済み」は事実誤り）。
  この Critical 項目は本 Plan の主題外のため、TODO.addf.md に別 Plan 起票が必要な
  最優先項目として追記した（Progress 運用ルール7）
- Plan 0040・0048: 未着手/要確認のため対象外
- Plan 0045: Plan 本文に「判断のみのため変更なし」と明記済み

### 実害3: README のスキル一覧に `addf-plan-audit` が掲載されていない

`.claude/commands/addf-*.md`（`*.exp.md` を除く。ユーザー起動可能スキルの一覧）と
README.md / README.en.md のスキルテーブル（メイン表＋「その他のスキル」表）を突き合わせたところ、
`addf-plan-audit`（Plan 0036 で新設）のみが両ファイルのどちらのテーブルにも掲載されていなかった
（他のスキル・`.exp.md` は全て正しく除外／掲載されていることを確認済み）。

## 変更内容（項目・フェーズ）

### 項目1: CHANGELOG.md の記載漏れ回収

- **対象**: `.claude/addf/CHANGELOG.md`
- `[Unreleased]` セクションに以下を追記する（前サイクルの未コミット差分を引き継いで完成させる）:
  - 実害1で確認済みの Plan 0039・0049・0051・0052 のエントリ（そのまま採用）
  - 実害2で確認した Plan 0030・0031・0032・0035・0036・0038・0041 の新規エントリ
    （既存の書式・粒度に合わせ、各エントリに `（Plan NNNN）` を明記する）

### 項目2: README スキル一覧の記載漏れ回収

- **対象**: `README.md` / `README.en.md`
- working tree にあった未コミットのエージェント表2行（`addf-doc-review-agent` /
  `addf-implementer`）をそのまま引き継ぐ
- 「その他のスキル」テーブルに `addf-plan-audit` の行を追加する（`addf-knowhow-revise` 等の
  棚卸し系スキルと同格の扱い）

### 項目3: README スキル一覧の網羅性 lint（ペア8）新設

- **対象**: `.claude/addf/addfTools/lint-template-sync.py`
- `.claude/commands/addf-*.md`（`*.exp.md` を除く）を列挙し、README.md / README.en.md の
  スキルテーブル（`**addf-xxx**` 形式の太字マーカー）に全て掲載されているかを検査する
  `check_pair8()` を新設する。WARNING 級（掲載形式は将来変わりうるため ERROR にはしない）
- upstream 限定（downstream は独自 README を持つため対象外。`repo_kind != 'upstream'` で SKIP）
- スコープを意図的に「スキル（`.claude/commands/`）」のみに絞る。エージェント
  （`.claude/agents/`）は命名規則が不均一（`addf-implementer` は `-agent` 接尾辞を持たない、
  `addf-ui-test-agent` は README 側にのみ存在するプレースホルダ等）で自動判定の誤検知
  リスクが高いため対象外とする（`.claude/addf/knowhow/ADDF/checklist-backing-lint.md` の
  「裏付けの弱いチェックは追加しない」方針に沿う判断）。エージェント表の網羅性は当面
  人間判断のままとし、必要になれば別 Plan で改めて検討する

### 項目4: addf-lint.md セクション6の表・docstring 更新

- **対象**: `.claude/commands/addf-lint.md`
- セクション6の表に「8. README スキルテーブル ⇔ `.claude/commands/addf-*.md`」の行を追加し、
  「同期が必要な7つのファイルペア」を「8つの」に更新する（Feedback.md 記載の
  「新たな同期ペアが生まれたら lint にペアを追加し、addf-lint.md セクション6の表も
  同時に更新すること」を遵守）
- `lint-template-sync.py` の docstring 冒頭コメントにもペア8の説明を追加する

### 項目5: テスト追加

- **対象**: `.claude/addf/tests/tools/test-template-sync.sh`
- `make_sandbox()` に README.md / README.en.md と `.claude/commands/addf-*.md` の複製を追加する
- 新規テスト（ドリフト注入 TDD）:
  - 新しいコマンドファイルを追加して README に掲載がない状態 → ペア8 WARNING
  - README からスキル1行を削除した状態 → ペア8 WARNING
  - downstream 判定（`CLAUDE.repo.md` 種別宣言）で SKIP になること
- 実リポジトリに対する Test 1（`OK: 同期チェック通過` を要求）が、項目1・2 のドキュメント
  修正後も exit 0 のまま通ることを確認する（先に項目1・2 を適用しないと Test 1 が
  自己言及的に失敗するため、実装順序は 1→2→3→4→5 を推奨）

## 影響範囲

- `.claude/addf/CHANGELOG.md`（配布対象外だが `/addf-migrate` が参照する重要ドキュメント）
- `README.md` / `README.en.md`（配布対象外・プロジェクトのトップページ）
- `.claude/addf/addfTools/lint-template-sync.py`（配布対象ツール）
- `.claude/commands/addf-lint.md`（配布対象手順書）
- `.claude/addf/tests/tools/test-template-sync.sh`（配布対象テスト）
- 同期ペアの追加のため、addf-lint.md セクション6の表と docstring の両方を更新すること
  （lint ペア5 の対象ではないが、Feedback.md の申し送りに従いセットで扱う）

## テスト方針

- 項目3・5: ドリフト注入 TDD（新規スキル追加・既存掲載削除の両方で WARNING を確認）
- 項目1・2 適用後、`bash .claude/addf/tests/run-all.sh` を実行し既存テストに regression が
  ないことを確認する
- `uv run --python 3.11 .claude/addf/addfTools/lint-template-sync.py` を実リポジトリに対して
  実行し、ペア8 が WARNING を出さない（掲載漏れが解消されている）ことを確認する

## 破壊的変更の許容範囲

なし（ドキュメント追記・lint 検査範囲の追加のみ。既存の合格基準は変えない）

## 要オーナー確認

- CHANGELOG の完全自動網羅性チェック（例: 完了 Plan は必ず CHANGELOG に触れているか）は
  「配布物に影響するか」の判断が Plan ごとに人間的な判断を要する（本 Plan の実害2の表でも
  Plan 0026・0040・0045・0048 を除外判断している）ため、本 Plan では自動 lint 化を見送り、
  一度きりの手動回収に留めた。将来また同種の記載漏れが発生するようなら、
  Progress 完了時チェックリストへの `<!-- human-judgment -->` 注意書き追加や、
  「Plan 本文に配布物への影響が明記されているのに CHANGELOG に該当 Plan 番号がない」
  ような限定的ヒューリスティックでの半自動検出を再検討してよいか <!-- human-judgment -->

## 完了条件

- [x] CHANGELOG.md に Plan 0030・0031・0032・0035・0036・0038・0039・0041・0044・0049・0051・0052
      のエントリが揃っている
- [x] README.md / README.en.md に `addf-doc-review-agent`・`addf-implementer`・
      `addf-plan-audit` が掲載されている
- [x] `lint-template-sync.py` にペア8（README スキルテーブル網羅性）が実装されている
- [x] `addf-lint.md` セクション6の表と docstring が「8つのペア」に更新されている
- [x] `test-template-sync.sh` にペア8のドリフト注入テストが追加され全パスする
- [x] `bash .claude/addf/tests/run-all.sh` が通過する
- [x] `/addf-lint`（`lint-template-sync.py` 含む）が実リポジトリに対して WARNING 0 件で通過する

## AI 実装時間見積もり

1セッション以内（ドキュメント追記5〜6件・lint 関数1個新設・テスト追加という局所的な作業の組み合わせで完結する規模）
