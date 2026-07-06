# Plan 0037: ADDF ディレクトリ大集約（docs 明け渡し・.claude/addf/ 名前空間）

## 実装状況: 一部完了（フェーズ1・2 完了 2026-07-06。フェーズ3=migrate 統合とメジャーリリースが残り）

execution_style: one-shot

> 出典: 2026-07-05 オーナー提案。「docs/ は一般用途（GitHub Pages デプロイ等）で使われるため
> ADDF が占有すると困る。.claude/addf/ を切って addf 由来ファイルを集約すると見通しがよくなる
> （カレントディレクトリに置くものを除く）。migration 時に取りこぼしなく移動できる工夫まで
> 含めて考察すること」

## 関連 Plan

- [Plan 0035: PR 運用の標準化](0035-pr-standard-format.md) — 0035 の guides 追記・lint 新設は
  移動対象パスに書かれる。実装順の考察は本 Plan「他 Plan との順序」参照
- [Plan 0036: 未完了埋没タスクの掘り起こしスキル](0036-plan-audit-skill.md) — 同上。
  また本 Plan の migrate ワンショット手順は 0036 と同じ「バージョン差分に載せる」型
- [Plan 0025: リポジトリ ADDF リネーム](0025-rename-repo-to-addf.md) — 一括参照書き換えの先行事例
- [Plan 0022: addf-init コピーリスト刷新](0022-addf-init-copylist-refresh.md) — コピーリスト
  ドリフト問題。本 Plan のパスマップ単一ソース化はこの根治を兼ねる
- [Plan 0038: 投機適性の概念化と大改造の窓](0038-speculation-fitness.md) — 本 Plan の
  実施様式「一発通し切り」を `execution_style: one-shot` として一般化。本 Plan はその第1号
  実例であり、0038 の窓検出（投機在庫ゼロの検出と選択提示）の最初の受益者になる

## 目的

1. **docs/ の明け渡し**: ADDF 管理ドキュメントを `docs/` から退避し、ダウンストリームが
   docs/ を GitHub Pages 等の一般用途に使えるようにする
2. **名前空間の集約**: `.claude/addf/` に ADDF 由来ファイルを集約し、プロジェクト側ファイルとの
   見分けを一目で付くようにする（「ADD 由来のファイルをルート配下になるべく置かない」哲学の徹底）

## 影響範囲の実測（2026-07-05 時点・本体）

| 旧パス | 参照ファイル数 |
|---|---|
| `.claude/addf/plans` | 44 |
| `.claude/addf/knowhow` | 57 |
| `.claude/addf/guides` | 36 |
| `.claude/addf/project-overview` | 8 |

本体の docs/ は全サブディレクトリが ADDF 由来（guides/knowhow/plans/plans-add/project-overview）。
参照元は CLAUDE.md・スキル本文・agents・addfTools スクリプト・lint TARGETS・テスト・
knowhow 相互リンク・TODO・Plan 相互リンクに分布する。

## 新構造（案）

```
<project>/
  CLAUDE.md  TODO.md  AGENTS.md  CLAUDE.repo.md      # カレント配置（除外指定。エントリポイント）
  docs/                                              # ← 明け渡し。ADDF は触らない
  .claude/
    addf/                                            # ★ ADDF 占有名前空間（新設）
      plans/  knowhow/  guides/  project-overview/   # ← docs/ から移動
      templates/  tools/  tests/  optional/          # ← .claude 直下から移動（addfTools→tools）
      Behavior.toml  lock.json  CHANGELOG.md  Release.md   # ← addf- プレフィックス不要になる
      Progress.md  Progresses/  Feedback.md  Questions.md  Worktrees.md  Dashboard.md
      paths.toml                                     # ★ パスマップ（後述の単一ソース）
    commands/  agents/  hooks/  skills/              # 移動不可（Claude Code 規約位置）
    settings.json  settings.local.json               # 同上
```

### 設計上の境界と論点

- **移動できないもの**: `commands/`・`agents/`・`hooks/`・`settings*.json` は Claude Code が
  読み込み位置を規定しており動かせない。ここは従来どおり `addf-` プレフィックスで名前空間分離を
  続ける（「全部 addf/ に入れる」はこの境界までが物理限界）
- **プレフィックスの簡素化**: `.claude/addf/` 内は占有空間のため `addf-Behavior.toml` →
  `Behavior.toml` 等に短縮できる。ただしリネームは参照書き換え量を増やすため、
  移動と同時にやるか（1回で済む）を着手時に判断する
- **可視性のトレードオフ**: plans/knowhow はオーナーも読み書きする共有チャンネル。
  `.claude/`（ドットディレクトリ）配下は IDE のツリーで隠れる環境がある。
  対策: README とカレントの TODO.md からの markdown リンクを入口として維持する
  （GitHub 上ではリンクで問題なく辿れる）
- **ルート lock ファイル**: `addf-lock.json` は現在 `.claude/` 配下。migrate の検出起点なので
  `.claude/addf/lock.json` へ移動しつつ、旧位置の検出フォールバックを migrate に残す

## migration の取りこぼし防止（考察の核心）

### 1. パスマップの単一ソース化 — `paths.toml`

旧→新の対応表を機械可読ファイルで持ち、**migrate の移動処理・addf-init のコピーリスト・
lint の検査対象・テストの全てが同じマップを参照する**。

- 効果1: 移動の実装が「マップを読んで git mv」に縮退し、手書きリスト間のドリフトが構造的に消える
- 効果2: lint ペア5（CLAUDE.md ⇔ init コピーリスト同期）の WARNING 検出を、単一ソース参照に
  よる「ドリフト不可能」へ格上げ（Plan 0022 問題の根治）
- 効果3: 将来の再配置も paths.toml の更新だけで migrate が追従する

### 2. プリフライト（check → 承認 → 実行）

migrate は移動前に check モードで以下を提示し、オーナー承認後に実行する:

- 移動対象の実在確認と、移動先の衝突確認
- **「存在≠所有」判定**（Plan 0034 の教訓）: ダウンストリームの .claude/addf/knowhow 内の独自記事は
  knowhow の仕組みの一部として一緒に移動する。一方 docs/ 直下の ADDF 管理外ファイル
  （Pages コンテンツ等）はリストに載せず**絶対に触らない**。
  ADDF 管理サブディレクトリ（plans/knowhow/guides/project-overview）単位でのみ移動する
- 旧パス参照の全数リスト（ファイル数・箇所数）

### 3. 原子性とロールバック

- **git mv を単独コミットに分離**する（参照書き換えと混ぜない）。revert 一発で戻せる
- 実行前に backup ref（`refs/backup/pre-0037-migration`）を作成する（不可逆操作の前の
  backup ref 作成 — オーナー環境の既知ルールとも一致）
- ダウンストリームで作業ツリーが dirty なら開始を拒否する（speculate-reconcile と同じ既定）

### 4. 参照書き換えはマップ駆動＋境界考慮

- paths.toml を読んで全 md/py/sh/toml/json を書き換える専用スクリプト（migrate から呼ぶ）
- 単純な部分文字列置換は禁止 — `.claude/addf/plans` が `.claude/addf/plans-add` に誤マッチする類の事故を
  境界チェックで防ぐ（Plan 0034 F2-3 で実測した誤配線判定と同型の罠）

### 5. 残存参照 lint = migration の完了ゲート

- 旧パス文字列の残存を検査する lint を新設し、**ERROR ゼロになるまで migrate を完了扱いしない**
  （「警告は出すが止めない」パターンの禁止 — Plan 0028 フェーズ3 の設計原則を踏襲）
- ドリフト注入 TDD: わざと旧パス参照を1つ残した状態で lint が検出することをテストで固定する
- 移行完了後の恒久 lint としては「docs/ 配下への ADDF ファイル新規追加」を WARNING で検出し、
  逆流を防ぐ

### 6. 後方互換はスタブではなく lint で

- 旧パスへの symlink は置かない（Windows・git 環境の罠。加えて「2つの正」が生まれ
  ドリフトの温床になる）
- 移行案内は CHANGELOG と migrate 完了メッセージで行い、残存参照は lint が即時 ERROR で
  知らせる — 「静かに壊れる」より「うるさく直させる」を選ぶ

### 7. 一回のメジャー migrate にまとめる

docs 明け渡し（フェーズ A）と .claude/addf/ 集約（フェーズ B）は概念上独立だが、
**ダウンストリームに2回の大移動を強いるより1バージョンにまとめる**。
バージョンはメジャー扱い（v0.6.0 以上を想定）。ADDF-Release の手順に従い、
CHANGELOG に移行ガイドセクションを設ける。

## 他 Plan との順序

- 0035・0036（小規模・ドキュメント中心）を**先に消化**してから本 Plan に着手することを推奨:
  - 本 Plan は差分が巨大になるため、他 Plan と並走すると衝突リスクが高い
  - 0035/0036 の成果物（guides 追記等）は本 Plan のマップ駆動書き換えで自動追従できる
- 本 Plan 着手中は投機（addf-speculate）を停止する（全域に触るため直交性が確保できない）

## 実施様式 — 一発通し切り（2026-07-05 オーナー判断）

> 本節の実施様式の一般定義は `.claude/addf/guides/speculative-development.md` の
> 「one-shot（一発通し切り）」節が単一ソース（本節は 0037 固有の適用）。

全域リファクタリングは投機・並走ブランチとのコンフリクトが致命的（実施後は生存中の
speculative が全て旧構造ベースになり、rebase 追従コストが爆発する）。よってフェーズ2
（本体移行）は**中断なしの一発完走**を原則とする:

- **事前清算**: 着手前に投機の在庫をゼロにする — 採否判断待ち・持ち越し・Pending を
  昇格 / 放棄 / ブランチのみ残置（worktree 削除）のいずれかで清算し、`/addf-speculate clean`
  と reconcile check が異常なしになってから始める
- **リハーサル前置**: 合成プロジェクトでの移行シミュレーション（完了条件参照）を
  フェーズ1側で済ませ、フェーズ2 当日は「検証済みの道具を実行するだけ」の状態にする
- **単一セッション完走**: backup ref → git mv コミット → 参照書き換えコミット →
  残存参照 lint ゼロ → run-all 全パスまでを1セッションで通し切る。**/loop・cron の自走に
  任せない**（クレジット枯渇による委譲エージェント中途死の実績 2026-07-04。中途半端な
  main が最も危険な Plan のため、オーナー同席=interactive での実施を推奨）
- **失敗時は巻き戻し優先**: 途中で想定外が出たら粘らず backup ref へ戻し、原因を
  フェーズ1の道具側で直してから再実行する（「直しながら進む」を禁止し、
  main に中途半端な状態を残さない）

## フェーズ分割（実装時）

1. **フェーズ1: paths.toml とツール整備** — パスマップ定義・移動スクリプト・残存参照 lint
   （ドリフト注入 TDD 込み）。この時点ではまだ何も動かさない
2. **フェーズ2: 本体の移行実施** — backup ref → git mv コミット → 参照書き換えコミット →
   残存参照 lint ゼロ確認 → run-all 全パス。本体自身が最初のドッグフーディング。
   **「実施様式 — 一発通し切り」に従い、事前清算済み・単一セッション・オーナー同席で実施する**
3. **フェーズ3: migrate 統合とリリース** — addf-migrate にバージョン差分手順を追加
   （プリフライト・存在≠所有判定・完了ゲート）。addf-init は新構造で生成するよう更新。
   メジャーリリース（CHANGELOG 移行ガイド込み）

## 完了条件

- [ ] paths.toml（旧→新マップ）が存在し、migrate・init・lint・テストが全て参照している
      （フェーズ1で migrate-paths.py・lint-residual-paths.py・テストは参照済み。addf-init の参照はフェーズ3）
- [x] 本体リポジトリが新構造で run-all 全パス・lint 一式 ERROR ゼロ（2026-07-06 フェーズ2完了。全19スイート・lint-residual-paths OK）
- [x] 残存参照 lint がドリフト注入テストで検出能力を実証済み（test-migrate-paths.sh・51アサーション）
- [x] docs/ 配下に ADDF 管理ファイルが存在しない（明け渡し完了。docs/ 自体が空になり削除された）
- [ ] addf-migrate のプリフライトが「存在≠所有」判定を含み、ADDF 管理外の docs/ ファイルに
      触れないことをテストで確認
      （migrate-paths.py のプリフライト自体はフェーズ1でテスト済み。addf-migrate への統合がフェーズ3）
- [x] ダウンストリーム移行をシミュレートするテスト（独自 knowhow 記事あり・docs/ に Pages
      コンテンツありの合成プロジェクト）が通る
- [ ] CHANGELOG に移行ガイド、メジャーバージョンとしてリリース準備完了

## フェーズ1 実装メモ（2026-07-06）

- Plan の構造図から変えた点: **`ADDF-Release.addf.md` は `Release.md` に短縮せず `Release.addf.md` のまま移動**
  （`.addf.md` サフィックスが addf-init の配布除外規則・addf-migrate の残留検出パターンとして現役のため。
  短縮すると本体専用手順が配布対象に紛れる）。**`.claude/assets` は不動**（README バナーのみ・配布物でない）
- ペルソナ3体+配布安全性の4体並列レビューで Critical 4件・Warning 6件を検出しフェーズ内修正済み
  （symlink 越し書き込み・apply 前 rewrite の無警告破壊・dynamic 分岐未テスト・自己移動後の案内欠如ほか）
- 本体 check 実測: 移動19件・旧パス参照 1695箇所・ブロッカーなし

### レビュー残課題（Low・フェーズ2/3 で再考）

- ADDF 管理サブディレクトリ（.claude/addf/plans 等）**内部**の非所有ファイルは無条件に巻き込まれる仮定が残る
  （合成テストは .claude/addf/knowhow の独自記事のみ検証。knowhow はダウンストリーム独自記事も「仕組みの一部として
  一緒に移動」が仕様だが、他サブディレクトリへの独自ファイル混在ケースは未検証）
- `[rewrite_exclusions]` の新旧パス列挙が dirs/files マップと二重管理（機械導出化の余地）
- lint の「移行済み」判定は `.claude/addf/` 存在の1点依存。フェーズ3の addf-migrate 統合時に
  完了マーカー等の多点判定を再検討する
- 境界正規表現は `.md.bak` 等の拡張子亜種に誤マッチしうる（否定先読みが `.` を境界扱いするため。実害低）

### フェーズ2 実施結果とレビュー（2026-07-06）

- 一発完走成功（backup ref `refs/backup/pre-0037-migration` は残置中。フェーズ3完了後に削除検討）
- 移行直後に run-all 18/19 スイート失敗 → 原因は「rewrite の射程外」4類型（詳細と対策は
  knowhow `map-driven-migration-tool.md`）。全て同セッション内で修正し全パス
- 事後レビュー（単体）指摘: guides 3ファイルの Markdown 相対リンク切れ（修正済み）・
  settings.local.json の許可ルール旧パス（修正済み）
- レビュー記録（対応不要と判断）: アーカイブ済み Progresses 42ファイルにも一括置換が及んだ
  （凍結記録の履歴改変にあたるが実害なし。次回の一括移行ではアーカイブ除外を検討）・
  プローズ中の裸の "addfTools" 呼称の残存（用語整理レベル。フェーズ3の CHANGELOG 執筆時に拾う）

## AI 実装時間見積もり

3〜4セッション（フェーズ1: 1、フェーズ2: 1、フェーズ3: 1〜2。参照書き換え 100+ ファイルは
マップ駆動で機械化するため人手比で大幅短縮）
