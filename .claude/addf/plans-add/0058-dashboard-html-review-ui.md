# Plan 0058: Dashboard の HTML 化とブラウザレビュー UI

## 実装状況: 一部完了（フェーズA・B 完了 2026-07-16。A: ダッシュボード実装＋3体レビュー Critical 3件反映＋オーナー実物確認済み〔サイドバー化を反映〕。B: crit ドッグフーディング一周〔files モード差分ゼロ起動・コメント→Finish→reply→再接続のループ実測・review.json スキーマ確認〕。フェーズC〔ダッシュボード自前アンカー UI・二層接続・配布〕は未着手 — 設計方針は確定済みで次サイクルの Plan 詰めで扱う。`/crit` プラグイン導入は保留）

owner_feedback: 済

> 出典: オーナー発案（2026-07-16 対話セッション）。Dashboard を md から HTML にしたい。
> VitePress 的な markdown to html がベースで、折りたたみ・画像・ページ切り替えで
> 「レビューの詰まり解消」「進行中のタスク」を見やすくし、差分ビューアも欲しい。
> さらに https://crit.md/ の仕組み（またはその模倣）に乗ってコメントできるととてもよい。
> 検討スタブとして起票 → 同日中に対話でオーナー判断が出揃い、叩き（HTML モック）合意・
> 優先着手指示（「レビューのボトルネック感がヤバい」）を受けて標準テンプレートに昇格。

## 目的

オーナーのレビュー・判断待ちがボトルネックになっている状態を解消するため、
リポジトリの状態から「オーナー判断待ちキュー」を俯瞰できるローカル HTML ダッシュボードを
生成する。1機能分の詳細レビュー（差分・行コメント）は crit に委ね、ダッシュボードは
俯瞰とプランビューアに徹する二層構造とする。

## 確定済みのオーナー判断（2026-07-16 対話セッション）

- **二層構造**: ミクロ層（1機能分の確認）= crit をそのまま採用 / マクロ層（俯瞰）=
  VitePress 自作で「ダッシュボード＋プランビューア」の2本柱
- **インスタンス**: ローカル専用の別インスタンス。公開サイト（`docs/.vitepress`・
  Plan 0039）とは目的が完全に異なるため分離
- **ページ構成は3ページ**: ①要フィードバック（投機ブランチ・PR・FB 未実施 Plan・
  未回答 Questions を統合した判断待ちキュー。待ちが長い順。Plan に紐づく Question は
  Plan 行にマージ）②進行中タスク（Progress.md の現在タスク・チェックリスト・日記）
  ③未実施の計画（バックログ ＝ プランビューアへの入口）
- **FB 判定は明示フィールド方式**: 状態管理エリアに「オーナーフィードバック有無」等の
  フィールドを追加する（自由文からの推測検出はしない）
- **叩き（HTML モック）合意済み**。追加要件: **Plan 本文ビューアは実運用版では実際に動く**
  （モックではボタンのみだった）
- **過去 Plan への遡及付与**も承認済み
- 剪定した案（復活条件付き）: A =「crit 単独」は俯瞰と個別確認の目的の違いで不成立。
  B =「VitePress 単独自作」はコメント・diff 基盤の自作コストが crit 採用で不要になるため
  不成立。復活条件: crit が俯瞰機能を持てば A、crit が使えない環境要件が出れば B を再検討

## 変更内容（フェーズ）

### フェーズA: ダッシュボード本体（本セッションで実施）

**項目1: FB フィールド仕様の確定とテンプレート反映**

- **対象**: `.claude/addf/templates/PlanTemplate.md`
- `## 実装状況:` ヘッダ直後の行頭 key: value 行として定義（`execution_style: one-shot` と
  同じ前例・grep 行頭一致で拾える形式）:
  - `owner_feedback: 待ち | 済 | 不要` — オーナーの集中フィードバックの有無
  - `feedback_ask: <必要な判断の一行>` — 「待ち」のときに書く（ダッシュボードの
    キュー行にそのまま表示される）
  - `feedback_since: YYYY-MM-DD` — 待ちの起点（待ち日数の計算に使う）
- 未完了 Plan（未着手・一部完了・要確認）のみ対象。完了 Plan には付けない

**項目2: 未完了 Plan への遡及付与**

- **対象**: 0026 / 0029 / 0030 / 0039 / 0040 / 0041 / 0048 / 0054 / 0056 / 0057 / 0058
- `plan-status-drift-check.md` の遡及付与作法に従い、TODO の転記ではなく Plan 本文・
  Questions.md と突合して値を決める（一回だけ全部疑い、以後は信用ベース）

**項目3: 生成スクリプト**

- **対象**: `.claude/addf/addfTools/generate-dashboard.py`（新設・stdlib のみ・
  PEP 723 サードパーティ依存なし）
- データ抽出（全て決定論）:
  - TODO テーブル（`plans-add/TODO.addf.md` / `plans/TODO.md` 自動判別）→ 状態・優先度
  - Plan ヘッダ＋FB フィールド（行頭一致）→ キュー行・待ち日数
  - `Questions.md` → 未回答（Plan 紐づきは Plan 行へマージ）・回答済みアーカイブ
  - `Progress.md` → 現在タスク・チェックリスト・日記（最新1エントリー）
  - `Progresses/` ファイル名 → 直近の完了タスク
  - `git branch --list 'speculative/*'` ＋ `git log main..<br>` → 投機ブランチと未回収差分
  - `gh pr list --json`（gh 不在・未認証なら空リスト＋注記のフェイルセーフ）
- 出力: `.claude/addf/dashboard/`（**全体が生成物・gitignore 対象**）に
  3ページの md ＋ `plans/` 配下へ Plan 本文コピー（プランビューア）＋
  `.vitepress/config.mts` を生成。単一ソースは常にリポジトリ側
  （`docs-site-single-source-sync.md` の「ビルド時生成」パターン）
- **フォールバック**: FB フィールド未記入の Plan は「要判断（詳細は Plan 本文参照）」
  表示で壊れない。完全性を生成の前提にしない
- **ページ間の役割分担の仕様**（Stage 2 レビューで確定）:
  - 要フィードバックキューは `owner_feedback: 済 / 不要` のみ除外する。TODO 状態が
    「進行中」でも待ちなら載せる（進行中×判断待ちの握りつぶし防止 — doc-review 指摘）
  - 「未実施の計画」ページは未着手・要確認・一部完了のみ。「進行中」の Plan は
    進行中タスクページ側に「進行中の Plan（TODO より）」として FB チップ付きで列挙する
  - `feedback_since` 欠落のキュー行は待ち日数「—」でキュー末尾に置く（起点不明を
    最長待ちと誤認させない意図的な仕様）
  - `owner_feedback` に未知の値（誤記）があれば生成時に WARN を出力し待ち扱いにする

**項目4: VitePress 配線**

- **対象**: `package.json`（`dashboard:dev` / `dashboard:build` スクリプト追加）・
  `.gitignore`（ADDF ブロックに `.claude/addf/dashboard/` 追加）
- ポートは 4747（magia serve）と衝突しない値を config で明示指定する
- プランビューアの Plan 間相対リンクは同ディレクトリコピーでそのまま解決する。
  ダッシュボードは `ignoreDeadLinks: true`（Plan 原文由来のリポジトリ内パス参照は
  サイト外のため。公開サイト〔0039〕の false 方針とは用途が異なる — 俯瞰用ローカル
  ビューであり、ドリフト検査は lint 群の仕事）

**項目5: テスト**

- **対象**: `.claude/addf/tests/tools/test-generate-dashboard.sh`（run-all.sh に自動発見される）
- 生成実行 → 3ページの存在・Plan コピーの存在・FB フィールドパース結果を検証
- 「欠如 = SKIP」設計: python3/uv 不在は SKIP、node 不在なら vitepress ビルド検証は SKIP
  （ダウンストリーム配布で誤 FAIL しない）

### フェーズB: crit ドッグフーディング（別途・オーナー同席）

- `brew install crit` → `crit <file>` で Plan・差分の行コメント運用を試す
- 外部バイナリ導入のため Plan 0040 フェーズ1 と同じ運び（一段階ずつ明示確認）

### crit ワークフロー調査結果（2026-07-16・GitHub tomasz-tomczyk/crit の README / docs/agent-prompts.md / docs/agent-hooks.md）

- **レビュー対象は4モード**: `files`（`crit plan.md` — **git 差分不要**・単体 md を
  markdown-it でレンダリングして行コメント可）/ `diff`（引数なし `crit` — git 変更の
  自動検出。**差分が無ければ対象なし**）/ `live`（URL プロキシ）/ `preview`。
  「差分がないと何も出ない」のは diff モードの性質で、files モードは差分不要
- **ワークフローの組み方はフック機構**（レビュー終了時に発火・モード別バリアントあり）:
  - **エージェントプロンプト**（`prompts`）: `on_finish_unresolved` / `on_finish_approved` で
    ユーザー定義プロンプトをエージェントに注入。Go text/template 変数
    （`{{.review_path}}`=レビュー JSON パス・`{{.comments_unresolved_json}}`・
    `{{.next_round_cmd}}` 等）。プロンプトは by reference（diff をインライン化しない —
    ファイルアクセスできる agentic CLI が前提）
  - **コマンドフック**（`hooks`）: 同名イベントでシェルスクリプト実行（LLM なしの決定的
    副作用用）。env（`CRIT_REVIEW_PATH`・`CRIT_UNRESOLVED_COUNT` 等）+ stdin JSON を受ける。
    出力はエージェントに届かない
  - 設定は5階層（プロジェクト `.crit.config.json` → グローバル → `.crit/prompts/` 慣例
    ファイル → ビルトイン）。プロジェクト由来は初回信頼確認あり
- **Send to Agent**: コメント本文・引用・パス・行範囲を `agent_cmd` の stdin に渡し、
  stdout をスレッド返信として自動投稿。スレッドはライブ化し会話履歴ごとエージェントに渡る
- **コメント取得 CLI**: `crit comments --json` / 追加は `crit comment <file>:<line> '...'`
- **オーナー構想への含意**: 「コメント→ファイル→次ターンのコンテキスト」のプロトコル部分は
  crit の files モード＋`on_finish` フック（コメント JSON をリポジトリ内に書き出し→
  ブートシーケンスで読む）で組める。**自前実装が必要なのは「VitePress ページ上の
  アンカーコメント UI」のみ**（crit は自分のビューアで開くため、ダッシュボードの
  レンダリング〔チップ・統計・サイドバー〕上には コメントできない）

### フェーズB 実測記録（2026-07-16・オーナー同席ドッグフーディング）

- `crit .claude/addf/dashboard/index.md`（files モード）: **差分ゼロでも起動・行コメント
  できることを実測確認**。daemon 方式（デタッチ起動・`crit status` で接続情報）
- **レビューループの実物を一周観測**: オーナーがブラウザで行コメント → Finish →
  未解決コメントの JSON ＋「`crit comment --reply-to` で返信し `crit --session <id>` で
  再接続せよ」というエージェント向け指示がセッションに届く。レビューファイルは
  `~/.crit/reviews/<session>/review.json`（ファイル別に comments 配列。各コメントは
  id / start_line / end_line / body / **anchor**〔対象行の原文〕/ author / scope /
  review_round / タイムスタンプ）。**anchor に行の原文を保持する設計は、生成し直しで
  行番号がずれるダッシュボード md との相性が良い**（自前実装でも踏襲すべき）
- **オーナーの初コメントが files モードの限界の実測になった**:
  「リンク先が Crit で開かれてないのでこっちは見れないあたりがやっぱり不便感ある」
  （index.md の `[Plan 本文を読む](/plans/...)` リンク — VitePress の内部リンクは
  crit ビューアでは辿れない）。**ダッシュボードの俯瞰→詳細の導線（3ページ・
  プランビューア）は crit files モードでは機能しない**ことがオーナー実感として確定。
  フェーズC の「ダッシュボード上のコメントは自前 UI（VitePress 側）が必要」を補強

### フェーズC: 二層接続・配布（フェーズB 後に判断）

- crit レビューファイル（`~/.crit/reviews/`）の未解決コメントをダッシュボードの
  キューに集約・ブートシーケンス 1.6 との整合・`optional/` テンプレート化の要否
- **オーナー構想（2026-07-16 フェーズA 実物確認時）**: ダッシュボード上に適宜
  アンカーポイントを作り、その場でコメントを入れられるようにする。入れたコメントは
  ファイルに書き出し、次のターン（セッション）にコンテキストとして渡す —
  crit 的な非同期レビューループをダッシュボード自体に持たせる方向。
  静的 VitePress ではコメントの書き出しに小さなローカルサーバ（または crit 本体の
  流用）が必要になるため、フェーズB の crit 試用結果を見て
  「crit をそのまま使う（ダッシュボードからの誘導のみ）／ダッシュボードに自前実装」を
  判断する。自前実装する場合、コメントの置き場は Questions.md の Answer 欄との
  役割分担を先に決めること（二重チャンネル化を避ける）

## 影響範囲

- `.claude/addf/templates/PlanTemplate.md`（フィールド書式追記 — 同期ペア対象外を確認済み。
  doc-review 対象）
- 未完了 Plan 11件（ヘッダ直後へのフィールド行追加のみ・本文不変）
- `package.json` / `.gitignore`（本体固有基盤。ダウンストリーム配布は addfTools・tests のみ）
- `lint-plan-status.py` は `## 実装状況:` 行のみ検査するため干渉しない

## テスト方針

- 上記フェーズA 項目5 のシェルテスト＋ `bash .claude/addf/tests/run-all.sh` 全通過
- `npm run dashboard:build` の実ビルド通過（node がある本体環境での手動確認）
- 生成された HTML をブラウザで開き、3ページ・プランビューア・待ち日数表示を目視確認 <!-- human-judgment -->

## 破壊的変更の許容範囲

なし（既存ファイルへの変更はフィールド行の追加とテンプレート追記のみ）

## 要オーナー確認

- フェーズA 完了時にダッシュボードの実物を確認してもらう（叩きとの乖離チェック）<!-- human-judgment -->

## 完了条件

- [x] PlanTemplate.md に FB フィールド書式が記載されている
- [x] 未完了 Plan 11件に owner_feedback フィールドが付与されている
- [x] `python3 .claude/addf/addfTools/generate-dashboard.py` が dashboard/ を生成する
- [ ] `npm run dashboard:dev` でダッシュボードが閲覧でき、プランビューアで Plan 本文が読める <!-- human-judgment -->
- [x] `bash .claude/addf/tests/run-all.sh` 全通過
- [x] lint 一式（plan-status / residual-paths / template-sync / checklist / json / toml / frontmatter）全通過

## AI 実装時間見積もり

フェーズA は1セッション以内
