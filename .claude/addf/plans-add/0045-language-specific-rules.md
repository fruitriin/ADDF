# Plan 0045: 言語別ルール分離パターンの導入判断（Plan 0005 埋没項目 #7 の回収）

## 実装状況: 完了（2026-07-10。実測の結果、現行の ADDF ダウンストリームでは言語別ルールによる
肥大化は観測されず、意図的な不採用として決定）

edge: derived-from 0005
edge: pruned

> 出典: Plan 0036 ドッグフーディング検出 #7「0005 の High 推奨『言語別ルール分離』後続 Plan 不在」— オーナー指示「B3 = 起票と実施でよさそう」に基づき回収。ただし埋没監査の提案は「回収計画に起こす（不要ならその旨の明記を提案）」— 実施可否も含めて判断する Plan。

## 関連 Plan

- [Plan 0005: everything claude code research](0005-everything-claude-code-research.md) — 埋没項目 #7 の出典
- [Plan 0038: 投機適性](0038-speculation-fitness.md) — 「不向き / 禁止」判定枠組み（言語別ルール分離が投機に馴染むかの判定にも使う）

### 剪定（pruned）した対象の記録

- **対象: 言語別ルール分離パターン（language-specific-rules）の CLAUDE.md/CLAUDE.repo.md への導入**
  - 理由: EnumaElish・wasurenainder ほか実測ダウンストリームで、言語別ルールによる肥大化の実害が観測されず、分離パターンを事前導入する便益がない
  - 証拠: 2026-07-10 拡大再実測（`/Users/riin/workspace/` 配下の複数ダウンストリーム — EnumaElish・wasurenainder・taskbar など — を対象に確認済み。詳細は本 Plan 項目1の実測記録）
  - 復活条件: 実運用で CLAUDE.repo.md の言語別ルールが肥大化し、可読性・保守性に実害が観測された場合

## 目的

CLAUDE.md（またはダウンストリームの CLAUDE.repo.md）に言語別ルールが増えることで肥大化する懸念に対して、言語別ルールを別ファイルに分離するパターンを**導入するかどうか**を判断する。

## 現状の挙動

- CLAUDE.md は現在フレームワーク中立の記述で、言語別ルールを持たない
- ダウンストリームは CLAUDE.repo.md に自プロジェクトの言語ルールを書く（Go・Swift・TypeScript 等）
- 埋没項目 #7 起票時点の懸念: 言語ルールが増えると CLAUDE.repo.md が肥大化する

## 変更内容（判断）

### 項目1: 実測（2026-07-10 実施・code-review 指摘を受けて2026-07-10 中に対象を拡大再実施）

**初回実測（不十分だった）**: `/Users/riin/workspace/` 配下で「`.claude/addf/` の有無」だけを
探索条件にして EnumaElish・wasurenainder の2件のみを対象にしたところ、code-review から
「探索条件が狭く、`.claude/addf/` を持たない（または古い世代の ADDF を導入した）ダウンストリームに
カスタマイズ済み `CLAUDE.repo.md` を持つプロジェクトが他に複数存在し、それらを見落としている」
という Critical 指摘を受けた。指摘どおり `find /Users/riin/workspace -maxdepth 2 -iname
"CLAUDE.repo.md"` で再探索し、対象を拡大した。

**拡大後の実測対象と行数**:

| プロジェクト | 言語/技術構成 | CLAUDE.repo.md 行数 |
|---|---|---|
| EnumaElish | Go | 75 |
| wasurenainder | TypeScript + Swift | 80 |
| summaly | TypeScript | 129 |
| MagiaMagica | Rust + Vue | 141 |
| taskbar | Node.js + Vue + Swift（Electron） | 216 |
| scrumtimerNanoda | Vue/TypeScript | 241 |

（TimeOfEve / TimeOfEve-spec-owner-checksheet は同一内容の worktree のため実質1件として扱い、
重複計上しない）

**比較対象から除外した2件**: `wardrobe-test` は `.claude/addf/` 導入済みだが、`CLAUDE.repo.md`
というファイル自体が存在せず（`CLAUDE.repo.example.md` のみ存在）、`CLAUDE.md` 本体も
`@CLAUDE.repo.md` 参照パターンを使わず独自内容へ全面書き換えされているため、CLAUDE.repo.md
パターンの比較対象にならない（初回実測では「未カスタマイズ」と誤記していたが、正しくは
「ファイル自体が存在せず運用パターンごと逸脱している」— code-review Warning 指摘により訂正）。
**SDIT** は `.claude/addf/` が存在せず ADDF 非導入（独自の単一 588行 `CLAUDE.md`）のため、
「言語別ルール肥大化」の直接比較対象にはならないと判断し除外した（この除外理由は code-review で
事実確認済み）。

**大きい2件の中身を精査した結果**:

- **taskbar（216行）**: 「Documentation Structure」節で `src/main/CLAUDE.md`（Node.js メイン
  プロセス）・`src/renderer/CLAUDE.md`（Vue レンダラー）・`nativeSrc/taskbar.helper/CLAUDE.md`
  （Swift ネイティブヘルパー）へ**コンポーネント（≒言語）ごとに詳細を委譲する構造を実際に
  採用済み**だった。これは「複数言語が同居すると分割したくなる」という Plan の懸念が実際に
  顕在化した実例であり、初回実測の「肥大化の実害は現時点でゼロ件」という結論は言い過ぎだった
  （code-review Critical 指摘のとおり）。**ただし採用した分割手段は ADDF 固有の新機構ではなく、
  Claude Code が既にネイティブに持つ「ディレクトリ単位の CLAUDE.md 自動発見」機能**であり、
  `.claude/rules/<language>.md` のような ADDF 側の新設機構は使われていない
- **scrumtimerNanoda（241行）**: 全体で最大だが、内訳を見ると「コーディング規約」節はわずか
  6行のみ。大半（ディレクトリ構成54行・開発体制〔レビュー体制/ノウハウ記録〕64行・ルーティング・
  Composables・WebRTC 設計・VoiceVox 連携設計 等）は**プロジェクト固有のドメイン/アーキテクチャ
  記述**であり、Plan が対象とする「言語別ルール」の肥大化ではない。総行数の大きさと「言語ルール」
  の肥大化を同一視すべきではないという教訓が得られた
- MagiaMagica・summaly も同様に、大きい部分の主因はビルド/テストコマンドの実装詳細や
  プロジェクト規約であり、汎用的に再利用可能な「言語別ルール」としての記述はごく一部

**測定結果のまとめ（修正版）**: CLAUDE.repo.md のサイズは 75〜241 行まで幅があり、規模が
大きいプロジェクトも実在する。ただし肥大化の主因を精査すると、大半は**プロジェクト固有の
ドメイン/アーキテクチャ/開発体制の記述**であり、Plan が問題にしている「言語別ルール」
（複数プロジェクトで汎用的に再利用されうる Go/Rust/Swift 等の言語作法）そのものの肥大化は
今回精査した6件中どれも支配的要因ではなかった。**唯一の例外は taskbar**（3コンポーネント構成の
Electron アプリ）で、言語/コンポーネントごとの分割が実際に発生していたが、その解決手段は
Claude Code ネイティブの「ディレクトリ単位 CLAUDE.md 自動発見」であり、ADDF 側で新規に
`.claude/rules/<language>.md` 相当の機構を用意する必然性はここでも確認されなかった。

### 項目2: 判断（2026-07-10 決定・拡大実測を踏まえて再確認）

**実害なし（ただし根拠は精緻化） → 意図的な不採用として明記して閉じる。** 根拠:

1. 6件の実測で、CLAUDE.repo.md の肥大化はあり得るが、その主因は「言語別ルール」ではなく
   プロジェクト固有のドメイン/アーキテクチャ文書であることが判明した。Plan が対象とする
   スコープ（言語別ルールの分離）自体が、実際の肥大化要因の主戦場ではない
2. 唯一「言語/コンポーネント単位で分割したくなる」実例（taskbar）でも、ダウンストリームは
   ADDF の助けを借りずに **Claude Code ネイティブの機能（ディレクトリ単位 CLAUDE.md 自動発見）**
   だけで自発的に解決していた。ADDF が `.claude/rules/<language>.md` のような並行する新機構を
   作ると、既存のネイティブ機能と役割が重複し、「どちらに書くべきか」の判断コストが増える恐れがある
3. 分離パターンを新設する実装コスト（addf-init コピーリスト・CLAUDE.md/CLAUDE.repo.md 参照
   構造・lint 対象への影響）は、上記1・2を踏まえるとなお正当化されない（YAGNI）。ADDF の他の
   判断（例: Plan 0032 の cp 上書き deny 保留 — 「実害の実測をトリガーにする」）と同型の判断様式

**再検討のトリガー（修正版）**: 今後、①**言語別ルール自体**（プロジェクト固有のドメイン/
アーキテクチャ記述ではなく、他プロジェクトでも通用する汎用的な言語作法）の記述量が明確に
肥大化した、②Claude Code ネイティブのディレクトリ単位 CLAUDE.md 自動発見だけでは表現できない
ニーズが出た、のいずれかが `.claude/addf/Feedback.md` に観測・記録されたら、分離パターンの
設計を再検討する。

## 影響範囲

判断のみのため CLAUDE.repo.md（本体）・本 Plan の記述以外への変更なし。

## 完了条件

- [x] 実測データが記録されている（EnumaElish・wasurenainder・summaly・MagiaMagica・taskbar・
  scrumtimerNanoda の計6件〔重複worktree除く〕を実測。当初2件のみだった探索範囲は code-review
  Critical 指摘を受けて拡大済み）
- [x] 採否の判断と根拠が明記されている（不採用・YAGNI・taskbar の反証例を踏まえた根拠の精緻化・
  再検討トリガー明記）
- [x] 採用の場合は実装計画に接続されている（不採用のため対象外）

## AI 実装時間見積もり

判断 = 1セッション（実測の結果、実装作業は発生しなかった。code-review 指摘を受けた実測範囲の
拡大・再判断を含む）
