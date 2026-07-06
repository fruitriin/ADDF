# Plan 0033: ダウンストリーム実測バグの修正（upstream/downstream 判定の統一ほか）

## 実装状況: 完了（2026-07-03 項目1〜3、2026-07-05 項目4=PlanTemplate は Plan 0035 フェーズA で実施）

### 項目4 実装記録（2026-07-05・Plan 0035 フェーズA で実施）

- `.claude/addf/templates/PlanTemplate.md` 新設: 収束8構造（実装状況 / 目的 / 現状の挙動 / 変更内容 /
  影響範囲 / テスト方針 / 破壊的変更の許容範囲 / 要オーナー確認）＋関連 Plan・完了条件を加えた
  標準テンプレートと、検討スタブ用の簡略 variant（分かっていること / 未解決の問い / 着手のトリガー）。
  「AI 実装時間見積もり」は提案どおり任意セクション
- CLAUDE.md 骨格プランニング手順・addf-init コピーリスト（`.claude/addf/templates/` エントリの例示）から参照

### 項目1〜3 実装記録（2026-07-03）

- `detect_repo_kind()` 新設: 一次=CLAUDE.repo.md の太字宣言（正規表現 `\*\*ADDF (開発|利用)プロジェクト\*\*`。
  部分文字列の誤爆対策・両ヒットは判定不能→lock へ委譲）、フォールバック=addf-lock.json の存在、
  どちらも無ければ None（旧来判定に委ねるが ERROR は WARNING に格下げ＋シグナル整備の促し）
- ペア1/2/3 をダウンストリームで SKIP（可視化表示付き — 本体誤判定時のフェイルセーフ）
- addf-init / addf-migrate の配布から `*.addf.md` を除外（根治策）。migrate に旧配布残留の検出ステップ 7.5 追加
- addf-knowhow-index の INDEX 選択を種別宣言一次に修正、knowhow「存在≠所有」追記
- ペルソナ並列レビュー3体（skeptic/attacker/newcomer）で Critical 2件（自然文での宣言誤爆・
  None フォールバックの旧バグ回帰。いずれも実測再現）を検出しフェーズ内修正。回帰テスト 53 ケース全パス

> 出典: ダウンストリームプロジェクト（イヴの時間シリーズ）の ADDF 運用初日に実測・検証された
> バグ報告3件＋機能提案1件。元は持ち込みファイル「19-ADDF上流コントリビューション.md」
> （v0.4.0 リリース時に受領。オーナー方針「Issue 起票相当として ADDF 側で実装」に従い本計画に正規化）。
> ダウンストリーム側に再現記録（lint 出力・`addf-knowhow-index.exp.md`）あり。

## 目的

ADDF 配布を受けたダウンストリームで**構造的に誤検知・誤誘導する**判定ロジックを修正する。
共通根因は「ファイルの**存在**で upstream/downstream を判定している」こと — 配布によって
`.addf.md` や `INDEX.addf.md` はダウンストリームにも物理存在するため、存在は所有の証明にならない。
所有判定は明示シグナル（`addf-lock.json` / `CLAUDE.repo.md` の種別宣言）で行う。

## 項目

### 項目1: lint-template-sync の upstream/downstream 判定を addf-lock.json ベースに統一（バグ・最優先）

- **対象**: `.claude/addf/tools/lint-template-sync.py`（ペア1 / ペア3）、`.claude/commands/addf-init.md`
- **問題**: ペア1 が `ProgressTemplate.addf.md` の存在で「ADDF 本体」と判定するが、addf-init は
  `.claude/addf/templates/` を丸ごと（`.addf.md` 含む）コピーするため、**全ダウンストリームで誤検知**する。
  ペア3 も、ダウンストリームが独自の `AGENTS.md` を持つケース（実例: Misskey 由来）で
  「ブートシーケンス見出しなし」ERROR を誤報する
- **修正**: `.claude/addf/lock.json` の存在を一次シグナルにする（addf-init / addf-migrate と同じ判定に統一）。
  lock あり → ダウンストリーム確定 → ペア1 は `ProgressTemplate.md` を正、ペア3 は SKIP
- **根治策（併せて実施）**: addf-init のカテゴリ1コピーから `*.addf.md` を除外し、
  ダウンストリームに `.addf.md` を物理的に置かない（分離規約に合わせる）
- **回帰テスト**: `test-template-sync.sh` に「addf-lock.json ありダウンストリームで `.addf.md` /
  独自 `AGENTS.md` が存在するケース」を追加（mktemp サンドボックス＋ドリフト注入）

### 項目2: addf-knowhow-index の INDEX 選択を種別宣言ベースに（バグ）

- **対象**: `.claude/commands/addf-knowhow-index.md`（「インデックスファイルの選択」節）
- **問題**: 「`INDEX.addf.md` が存在すればそちらを優先」は、配布を受けた全ダウンストリームが
  両 INDEX を持つため**恒常的に誤誘導**する（エッジケースではなく設計欠陥）
- **修正**: `CLAUDE.repo.md` のプロジェクト種別宣言（「ADDF 開発プロジェクト」/「ADDF 利用プロジェクト」）を
  一次根拠、`addf-lock.json` の存在をフォールバックにする

### 項目3: sync-lint-design.md へ「存在≠所有」の教訓を追記（知見）

- **対象**: `.claude/addf/knowhow/ADDF/sync-lint-design.md`
- **内容**: 「欠如 = SKIP」原則の逆ケースを明文化 — ① `.addf.md` はダウンストリームに物理存在しうる
  （存在≠所有）② ADDF 配布ファイル名はダウンストリームの同名無関係ファイルと衝突しうる。
  所有判定は明示シグナル（addf-lock.json 等）で行う

### 項目4: PlanTemplate.md の新規追加（機能提案・優先度低）

- **対象**: `.claude/addf/templates/PlanTemplate.md`（新規）、CLAUDE.md 骨格プランニング手順・addf-init からの参照
- **背景**: ダウンストリームで独立起草された計画8本が同一構造に収束した実績
  （実装状況 / 目的 / 現状の挙動 / 変更内容 / 影響範囲 / テスト方針 / 破壊的変更の許容範囲 / 要オーナー確認）。
  ProgressTemplate はあるのに Plan のテンプレートが無い
- **提案**: 上記構造の標準テンプレート＋検討スタブ用の簡略 variant（分かっていること / 未解決の問い /
  着手のトリガー）。「AI 実装の見積もり」欄はオーナー個人設定由来のため任意セクション
- 実装時は項目1〜3 と切り離してよい（バグ修正を先行させる）

## レビューで先送りした Low

- **@メンション解決のパストラバーサル耐性**: `lint-template-sync.py` の
  `_repo_declaration_lines()` は CLAUDE.repo.md の `@xxx.md` 行を無検証で開くため、
  `@../outside.md` のような参照でリポジトリ外のファイルを読みうる（lint は読み取りのみ・
  再帰1段のため実害は限定的）。対応する場合は `os.path.realpath` で解決先が
  リポジトリ配下に閉じることを確認してから開く

## 影響範囲

- `.claude/addf/tools/lint-template-sync.py` / `.claude/commands/addf-init.md` /
  `.claude/commands/addf-knowhow-index.md` / `.claude/addf/knowhow/ADDF/sync-lint-design.md` /
  `.claude/addf/templates/`（項目4）
- addf-init コピーリスト変更（項目1 根治策）は lint ペア5 への影響を確認する
- ダウンストリームは次回 `/addf-migrate` で追従する

## 完了条件

- ダウンストリーム構成（addf-lock.json あり・`.addf.md` あり・独自 AGENTS.md あり）で
  lint-template-sync が誤検知しない — `test-template-sync.sh` の新規回帰ケースが PASS
- addf-knowhow-index が種別宣言に従って INDEX を選択する — スキル本文の記述更新
  <!-- human-judgment: ダウンストリーム実環境での再現解消はダウンストリーム側の /addf-migrate 後に確認 -->
- 項目3 の knowhow 追記が INDEX.addf.md に反映されている（`/addf-knowhow-index reindex` 相当の整合）

## 関連 Plan

- [Plan 0035: PR 運用の標準化](0035-pr-standard-format.md) — 項目4（PlanTemplate.md 新規追加）に
  0035 項目3の Plan 相互リンク規約が依存する。項目4 は 0035 フェーズA で引き取り実施済み（2026-07-05）
