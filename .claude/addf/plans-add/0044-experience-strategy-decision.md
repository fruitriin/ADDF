# Plan 0044: experience 運用方式の決定（Plan 0026 埋没項目 #2 の回収）

## 実装状況: 完了（2026-07-10。案A〔現行分離方式〕を実測に基づき正式採用し、addf-experience を
「@メンション書式検証」から「参照の自己整合性・書式健全性検証」に再定義。テスト・README・guides 更新済み）

> 出典: Plan 0036 ドッグフーディング検出 #2「0026 の experience 運用方式（→ 独立 Plan 0029 推奨）」— 0029 は別テーマに採番済みで後続 Plan 不在。オーナー指示「B3 = 起票と実施でよさそう」に基づき回収。

## 関連 Plan

- [Plan 0026: レビュー残課題のバックログ化](0026-review-residual-backlog.md) — 埋没項目 #2 の出典
- [Plan 0009: experience bootstrap](0009-experience-bootstrap.md) — 現行の .exp.md 運用の基礎
- [Plan 0017: 代替わり日記](0017-progress-checkpoints.md) — 同じく「経験の引き継ぎ」領域

## 目的

`.exp.md`（経験ファイル）の運用方式について、2つの案（案A: スキル本文と分離した現行方式・案B: スキル本文に埋め込む一体化方式）のどちらを正式採用するかを決定する。

## 現状の挙動

- `.exp.md` はスキル本文（`.md`）と分離した個別ファイル。gitignore 対象で、ローカル環境で蓄積される
- スキル起動時に `<スキル名>.exp` を明示的に読ませる運用（現行 addf-* スキル群）
- 課題感（Plan 0026 起票時点）: 分離しているためスキル本文の変更と exp の変更が同期しにくい・オーナーの目に触れにくい・PR レビュー対象外

## 変更内容（項目）

### 項目1: 案A/案B の実測比較（2026-07-10 実施）

`.exp.md` はローカル生成物で `.gitignore` 対象（`.claude/commands/*.exp.md`）のため git log では
追えない。ADDF 本体の実ファイルを直接調査した。

**カバレッジ**: `.claude/commands/addf-*.md`（`.exp.md` を除き16スキル）のうち、実際に `.exp.md` が
生成されているのは6スキル（addf-dev / addf-release / addf-knowhow / addf-overview / addf-speculate /
addf-knowhow-index）。残る10スキル（addf-init / addf-lint / addf-migrate / addf-mode /
addf-permission-audit / addf-plan-audit / addf-experience / addf-knowhow-filter /
addf-knowhow-network / addf-knowhow-revise）は exp 未生成。
別枠として addf-gui-test は Plan 0029 で `.claude/addf/optional/commands/` へ原本移動済み
（上記16件の母数には含めない）だが、`.exp.md` 自体は移行前からの生成物として
`.claude/commands/addf-gui-test.exp.md` に残っている（Plan 0029 の設計どおり、無効化時も
削除しない扱い）。

**更新頻度（最終更新日）**:
- 活発（直近1週間以内）: addf-release（07-07）/ addf-overview（07-07）/ addf-knowhow（07-06）/
  addf-dev（07-03）/ addf-speculate（07-03）
- 停滞（3月から更新なし・約4ヶ月）: addf-knowhow-index（03-21・上記16件の1つ）/
  addf-gui-test（03-21・上記とは別枠の exp 遺物）

**内容の質**: 活発に更新されているものは「うまくいったパターン」「注意すべき落とし穴」に加え
`addf-speculate.exp.md` は「🔀 分かれ道の目印」形式で具体的な判断根拠まで蓄積されており、
案A（分離・手動 Read）が**実際に使われているスキルでは機能している**ことを裏付ける実測が得られた。
停滞している2件（addf-knowhow-index / addf-gui-test）は、INDEX 運用が定常化した・GUI テストが
オプトイン化（Plan 0029）された、といった**利用頻度自体の低下**が原因と見られ、分離方式そのものの
欠陥（読み忘れ・乖離）を示す事例は見つからなかった。

**規約の実態確認**: 全スキルで「経験の活用」記述はバッククォート付きファイル名 + 手動 Read 指示
（例: `` 実行前に `addf-dev.exp.md` が存在すれば読み ``）に統一されており、`@<name>.exp.md`
形式の @メンション参照は repo 内に **1件も存在しない**（`grep -rn "@[a-zA-Z0-9_-]*\.exp\.md"` で確認）。
これは Plan 0026 の指摘（「`@`展開はスキルファイルでは効かない」）と整合する。

一方、「経験の活用」の書き方には表記ゆれがあった: 3スキル（addf-knowhow / addf-overview /
addf-release）には独立した「## 経験の活用」見出しがなく、手順の一部（Phase 内の1ステップ）として
読み/書き指示が埋め込まれている。効果は同じだが検証ロジックが見出し名に依存すると見落とす。
（addf-lint はこれとは別で、`.exp.md` 参照そのものが1件も存在しない「経験活用の記述なし」スキル
— 上記カバレッジの「残る10スキル」の1つ）

**案B（本文埋め込み方式）の想定コスト**: 上記の実測から、活発に使われているスキルでは分離方式に
起因する問題（読み忘れ・スキル本文との乖離）は観測されなかった。案Bへの全面移行は 16 スキル
全書き換えのコストに対して得られる利益が実測上小さいと判断した。

### 項目2: 決定と移行手順（2026-07-10 決定）

**決定: 案A（現行分離方式）を正式採用する。** 根拠は項目1の実測（活発利用スキルでの機能実証・
@メンション形式の不使用・案B移行コストに見合う実害の不在）。

決定に伴い、Plan 0026 が案Aの一部として提案していた「掃除」（addf-experience の再定義）を実施した:

- **旧**: 「クオートされた @メンション」の検出・修正 — 該当パターンが repo に1件も存在しないため
  実質的に機能しない死んだロジックだった
- **新**: 「経験参照の自己整合性・書式健全性検証」に再定義（`.claude/commands/addf-experience.md`）
  - 自スキル名と参照ファイル名の一致チェック（自己参照ミスの検出）
  - 読み込み指示・書き込み指示の両方が揃っているかのチェック（見出し名に依存しない — 実測で判明した
    表記ゆれ4件に対応）
  - 経験活用の記述が1つもないスキルも「記述なし」として可視化（エラー扱いしない）
- テスト（`.claude/addf/tests/skills/test-addf-experience.md`）を新スコープに合わせて全面書き換え
- `README.md` / `README.en.md` / `.claude/addf/guides/skills.md` の一行説明を更新

ハイブリッド案は不採用（案Aで実害が観測されていないため、複雑さを増す理由がない）。

## 影響範囲

- `.claude/commands/addf-experience.md`（再定義）
- `.claude/addf/tests/skills/test-addf-experience.md`（新スコープに合わせ全面書き換え）
- `README.md` / `README.en.md` / `.claude/addf/guides/skills.md`（一行説明の更新）
- `.claude/addf/project-overview/*`（生成物。次回 `/addf-overview` 実行時に再生成で追随 — Plan 0029 と同型の対応）

## 未決事項

- なし（実測データで判断が確定したため、収集期間の延長やハイブリッド案の探索は不要と判断）

## 完了条件

- [x] 実測データが Plan 本文に記録されている
- [x] 案A/案B の決定と根拠が明記されている
- [x] 決定に伴う実装作業が完了している（addf-experience 再定義・テスト更新・ドキュメント更新）
- [x] `bash .claude/addf/tests/run-all.sh` と `/addf-lint` が通過する

## AI 実装時間見積もり

判断 + 実装 = 1セッション（実測時点で案Bへの移行コストが正当化されないと判明したため、
掃除範囲のみの小粒実装で完結した）
