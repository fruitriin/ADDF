# Plan 0026: プロジェクトレビュー残課題バックログ

## 実装状況: 一部完了（2026-07-02 コード品質・ドキュメントの Medium/Low/Info 6件対応済み。2026-07-07 セキュリティ High と破壊的 git 対策は Plan 0043 で対応済み。**[Critical] settings.json/hooks 自己書き換え保護（Write/Edit の deny）は Plan 0043 対象外 — Plan 0054 として回収済み（2026-07-11 起票）**）

owner_feedback: 不要

## 目的

2026-07-02 のプロジェクト全体レビュー（コード品質・セキュリティ・ドキュメント整合の3並列レビュー
＋手動チェック）で検出され、同日のバッチ1（コミット 3481f63 / fa68df4）で**未対応**のまま残った
指摘を、追跡可能なバックログとして集約する。粒度の大きいものは独立 Plan（0027〜）に分割する。

## 背景（バッチ1で対応済みの範囲）

以下は 2026-07-02 に対応済み。本 Plan の対象外:
- 非 macOS でのバイナリテスト SKIP（コミット e873165）
- addf-lock の ref（タグ）方式化・リリース手順化
- hooks の CLAUDE_PROJECT_DIR フォールバック・skill-usage-log の exit 0
- ターンカウンターテストのサンドボックス化
- lint pair6 の表記ゆれヘッダ検出
- Plan 0025 状態同期
- ドキュメント鮮度回復（README スキル表・ロゴ・CLAUDE.repo.md 方針・CHANGELOG 誤記・project-overview 再生成）

---

## 残課題

### セキュリティ（→ 独立 Plan 0027 で対応推奨）

粒度が大きく upstream/downstream 分離の設計判断を伴うため、独立 Plan に切り出す。

- **[Critical] settings.json / hooks 自己書き換え保護がない** — `Write`/`Edit` 無条件許可 + `deny` ルール皆無。
  インジェクションが一度通ると hooks 追記 → 次セッション以降の永続 RCE。`permissions.deny` で
  `.claude/settings.json` と `.claude/hooks/**` を通常書き込みから除外する。
  **注意**: ADDF 本体開発は hooks を頻繁に編集するため、deny は配布用 `settings.json` に入れ、
  本体開発は `settings.local.json` で緩める upstream/downstream 分離が必須。
- **[Critical] addf-init の導入前レビューが実物を検証していない** — Phase 2.7 でユーザーに見せるのは
  addf-init.md にハードコードされた説明文で、実際に clone した hooks の中身ではない。悪意あるフォーク・
  typosquat の hooks がそのまま無条件コピー（カテゴリ1）される。実ファイル内容（または既知版との diff）を
  提示してから承認する設計に変更する。
- **[High] 破壊的 git 操作が確認なしで通る** — `Bash(git checkout *)` / `Bash(git branch *)` が無条件 allow。
  `git checkout .`（未コミット変更全破棄）・`git branch -D` が確認なしで実行可能。`ask` に追加するか
  allow パターンを絞る。CLAUDE.md の Git Safety Protocol と settings.json の乖離。
- **[High] `Bash(cp *)` 無制限 + Read 無制限** — `cp -r ~/.ssh .` 等で機密ファイル複製 → Read で露出の補助になる。
  `permission-settings-pattern.md` は mv/rm/chmod を破壊的として除外しているのに cp は無制限で基準が不統一。
- **[Medium] コミット済み Mach-O バイナリ4種の検証手段がない**（→ 独立 Plan 0028 推奨） — ソースとバイナリの
  一致を保証する仕組み（チェックサム・再現ビルド・CI 署名）がない。addf-init が無条件コピーする。
  CI で build.sh 生成物とのハッシュ照合を run-all.sh に追加、またはバイナリをリポジトリから外しローカルビルド必須化。

### experience 運用方式の決定（→ 独立 Plan 0029 推奨）

- **[Medium] addf-experience が死んだ検証ロジック** — 検出対象の `@*.exp.md` メンションはリポジトリに
  1件も存在せず、全17スキルは「存在すれば手動 Read」方式で統一。`@`展開はスキルファイルでは効かない
  （CLAUDE.md 専用）ことを事実確認済み。二択で整理する:
  - 案A（現状維持＋掃除）: 手動 Read を正とし、addf-experience を「exp の存在・書式健全性チェック」に再定義
  - 案B（自動注入化）: 全スキルを `` !`cat *.exp.md 2>/dev/null` `` 動的注入に寄せ、addf-experience は注入行の有無を検証
  - マイグレーション耐性は案Bが高い（手動 Read は読み忘れが起きる。注入行はスキル側で上書きされても
    upstream と同一、実体 exp は migrate 対象外で保護される）が、全17スキルへの一括変更が必要。

### コード品質（軽微・単独修正可）→ 対応済み（2026-07-02）

- ~~**[Medium] addf-dev.md の Plan 命名規則が実態と不一致**~~ → プロジェクト非依存の表現に修正、両形式を例示
- ~~**[Low] hooks に set -e 非使用の設計判断が未明記**~~ → post-compact-recovery / skill-usage-log に追加
  （reset-turn-count / turn-reminder は既存）。4フック全てが同一文言で統一された
- ~~**[Low] .gitignore に実在しないパス `.claude/skills/addf-gui-test.md`**~~ → 削除。
  Plan 0029（GUI スキル退避）は実装時に正しいパスでエントリを追加し直す
- **[Low] addf-lint の未スクリプト化項目** — **項目2（hooks 実行権限）はスクリプト化済み**（2026-07-02、
  `lint-hooks-exec.py` + テスト8件）。残る 5（INDEX 整合）・7（鮮度）・8（双方向リンク）は
  エージェント手作業のまま（規模が大きく、必要になったら別途スクリプト化する）
- ~~**[Info] addf-code-review-agent が全体監査モードを想定していない**~~ → 全体監査モードを明記

### ドキュメント（軽微）→ 対応済み（2026-07-02）

- ~~**[Low] CONTRIBUTING.md（日本語版）に英語版への相互リンクがない**~~ → 追加（README と文言統一）
- **[Info] knowhow の残る陳腐化** — `/addf-knowhow-revise` の定期棚卸し対象（継続運用。本 Plan では対応しない）

## 完了条件

- Critical/High 項目が独立 Plan（0027〜）または本 Plan 内で解消されている
- Medium 以下は本 Plan 内で対応、または独立 Plan 化して TODO に登録されている
- 対応後、run-all.sh・lint 一式が通過する

## 備考

- 元レビューの詳細（重要度・ファイル:行番号・攻撃シナリオ・修正案）はセッションログ（2026-07-02）参照。
- ①deny ルール導入 と ⑥experience 方式決定 は、オーナーが「以降続く」として次の指示を保留中。
