# Plan 0026: プロジェクトレビュー残課題バックログ

## 実装状況: 未着手

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

### コード品質（軽微・単独修正可）

- **[Medium] addf-dev.md の Plan 命名規則が実態と不一致** — 「`phaseX.Y-*.md`」形式前提の記述だが
  実際は4桁連番（`0001-`）。プロジェクト非依存の表現にするか、両形式あり得ることを明記する。
- **[Low] hooks に set -e 非使用の設計判断が未明記** — 4フックとも意図的に `set -e` を使わない
  （フォールバック優先）が、コメントがないため次の編集者が安易に追加して壊すリスク。冒頭コメントで一言添える。
- **[Low] .gitignore に実在しないパス `.claude/skills/addf-gui-test.md`** — Plan 0014 のリネーム残骸。
  実体は `.claude/commands/addf-gui-test.md`。削除する。
- **[Low] addf-lint の未スクリプト化項目** — 8項目中 2（hooks 実行権限）・5（INDEX 整合）・7（鮮度）・
  8（双方向リンク）はエージェント手作業。特に2は `os.access(path, os.X_OK)` で数行。手検査依存は見落としの温床
  （pair6 表記ゆれ穴と同じパターン）なのでスクリプト化候補。
- **[Info] addf-code-review-agent が全体監査モードを想定していない** — 手順が「git diff」前提。
  addf-overview のような定期棚卸し用途向けに whole-repo audit モードを明記すると指示のブレを防げる。

### ドキュメント（軽微）

- **[Low] CONTRIBUTING.md（日本語版）に英語版への相互リンクがない** — en → ja はあるが逆がない。
- **[Info] knowhow の残る陳腐化** — バッチ1で ignore-file-strategy.md は訂正済み。他の 🟡 aging ファイルは
  `/addf-knowhow-revise` の定期棚卸し対象。

## 完了条件

- Critical/High 項目が独立 Plan（0027〜）または本 Plan 内で解消されている
- Medium 以下は本 Plan 内で対応、または独立 Plan 化して TODO に登録されている
- 対応後、run-all.sh・lint 一式が通過する

## 備考

- 元レビューの詳細（重要度・ファイル:行番号・攻撃シナリオ・修正案）はセッションログ（2026-07-02）参照。
- ①deny ルール導入 と ⑥experience 方式決定 は、オーナーが「以降続く」として次の指示を保留中。
