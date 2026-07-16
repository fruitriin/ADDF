# Plan 0058: Dashboard の HTML 化とブラウザレビュー UI

## 実装状況: 一部完了（フェーズA・B・C 完了 2026-07-16。A: ダッシュボード実装＋オーナー実物確認済み。B: crit ドッグフーディング一周実測。C: アンカーコメント UI〔Layout.vue＋/api/comments Vite プラグイン〕・DashboardComments.json・crit 未解決コメント集約・ブートシーケンス 1.7 配線・折りたたみ構文2系統〔::: details 推奨＋details/summary パススルー〕・3体レビュー反映〔Critical 2/High 1/Medium 4 ほか〕・テスト17件全通過。オーナー動線確認済み 2026-07-16〔コメント13件が UI 経由で往復。追加フィードバックで draft モデル・送信待ちスタック一覧・ガイダンスモーダルを実装〕。`/crit` プラグイン導入は保留）

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
  - **2026-07-17 改訂（オーナー要望）**: ①と③を1ページに統合（③は別ページだと
    気づかない・「フィードバックが済むと着手可能が増える」を同一ページで見せる）。
    計画リストは「✅ 着手可能 / ⏳ フィードバック待ち」でグループ化し、stats に
    着手可能タイルを追加。あわせてサイトタイトルを固定「ADDF ダッシュボード」から
    リポジトリ名（`REPO_ROOT.name` + ダッシュボード）に変更 — DS で複数ダッシュボードを
    開いたときの識別のため
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

### フェーズC: ダッシュボード自前アンカー UI・二層接続（2026-07-16 詰め・実施）

- **オーナー構想（2026-07-16 フェーズA 実物確認時）**: ダッシュボード上に適宜
  アンカーポイントを作り、その場でコメントを入れられるようにする。入れたコメントは
  ファイルに書き出し、次のターン（セッション）にコンテキストとして渡す —
  crit 的な非同期レビューループをダッシュボード自体に持たせる方向。
  フェーズB 実測（crit ビューアで VitePress 内部リンクが辿れない＝俯瞰→詳細の導線が
  機能しない）により「ダッシュボードに自前実装」で確定

**フェーズC の決定事項（plan-refinement-pattern の未決→決定+根拠 変換）**

- **決定C-1: コメント書き出しは VitePress dev サーバーの Vite プラグインで実装する**。
  `generate-dashboard.py` が `.vitepress/config.mts` に `configureServer` ミドルウェア
  （`/api/comments` の GET/POST/PATCH、node:fs で JSON 読み書き）を生成する。
  根拠: `dashboard:dev` にそのまま乗り、追加プロセス・追加依存・追加ポートが不要。
  crit 本体流用は「ビューアが crit 側に切り替わる」というフェーズB で実測した欠点を
  再導入するため不採用。静的ビルド（`dashboard:build`）ではコメント投稿は動かない
  （読み取り表示のみ）— レビューは `dashboard:dev` で行う運用を仕様として明記する
- **決定C-2: コメント置き場は `.claude/addf/DashboardComments.json`（コミット対象）**。
  根拠: Questions.md と同じ「オーナーとの共有チャンネル」であり、リポジトリ内に
  置くことでセッション・マシンを跨いで次ターンのコンテキストに渡せる（crit の
  `~/.crit/reviews/` はホーム配下のため可搬性がない）。スキーマは crit の review.json を
  模倣: `comments[]` に `id / page / source_path / anchor`（対象ブロックの原文テキスト —
  再生成で行番号がずれても原文一致で位置を復元する。フェーズB 実測の踏襲）
  `/ anchor_occurrence`（同一原文ブロックが複数あるときの出現番号・0始まり — レビュー M1 対応）
  `/ body / author / created_at / status ("unresolved"|"resolved") / resolution / replies[]`
- **決定C-3: Questions.md との役割分担は「方向」で分ける**（二重チャンネル化の回避）。
  Questions.md ＝ エージェント発の構造化質問（正は常にこちら）。
  DashboardComments.json ＝ オーナー発の文脈付きフィードバック（ページ上の任意箇所）。
  オーナーのコメントが未回答 Question への回答に相当する場合、エージェントは反映時に
  Questions.md の Answer 欄へ転記してからコメントを resolved 化する（単一ソース維持）
- **決定C-4: エージェントへの受け渡しはブートシーケンス手順 1.7 として配線する**。
  「`.claude/addf/DashboardComments.json` に `status: "unresolved"` のコメントがあれば
  読み、対応する（対応後に `status: "resolved"` と `resolution` を書き込む）」。
  1.6（Dashboard.md）が unattended 自走の差分まとめであるのに対し、1.7 は
  オーナー発フィードバックの受信箱 — どちらも「セッション冒頭にオーナーの声を聞く」枠
- **決定C-5: 二層接続 — crit 未解決コメントの集約は generate-dashboard.py に追加する**。
  `~/.crit/reviews/*/review.json` を走査し、unresolved コメントの件数・対象ファイルを
  「要フィードバック」ページに表示する（crit 不在・ディレクトリ無しは非表示の
  フェイルセーフ）。ダッシュボードコメントの unresolved も同様に統計へ加える
- **決定C-6: `optional/` テンプレート化はしない**。
  根拠: ダッシュボード一式は `generate-dashboard.py` の生成物であり、addfTools ＋ tests の
  通常配布に既に乗っている。ccchain のような外部バイナリ・ホスト側設定を持たず、
  使わないダウンストリームでは単に実行しなければよい（optional 機構の保守負担の方が大きい）。
  復活条件: ダウンストリームから「配布から除外したい」フィードバックが実際に来たら再検討
- **決定C-7: アンカー UI はテーマ Layout（`.vitepress/theme/Layout.vue` を生成）で実装する**。
  本文ブロック要素（p / li / 見出し / テーブル行 / pre）のホバーで「💬」ボタンを出し、
  クリックでコメント入力ポップオーバー → POST。既存コメントは anchor 原文一致で
  該当ブロックにバッジ表示（クリックでスレッド・返信・resolve）。原文一致しない
  コメント（orphan — 再生成で本文が変わった等）はページ末尾に一覧表示して握りつぶさない
- **決定C-9: コメントは GitHub PR レビュー型の draft モデルにする**（2026-07-16
  オーナー実物確認フィードバック）。投稿は `status: "draft"` で即ファイル保存
  （リロード耐性）されるが、画面右上の「レビューを送信」で `unresolved` に確定するまで
  エージェントの読み取り・キュー集約の対象にしない — 全体を見回して訂正できる。
  draft はパネルで「取り下げ」可能。送信後はモーダルで「Claude Code に
  『ダッシュボードのコメントに対応して』とプロンプトしてね」というガイダンス
  （コピー用ボタン付き）を表示する。次セッションのブートシーケンス 1.7 でも自動で読まれる
- **決定C-8: プランビューアの折りたたみ構文は2系統をサポートする**（2026-07-16
  オーナー追加要望「人間の注意資源配分をやりやすく」）。第一推奨は VitePress ネイティブの
  `::: details 見出し`（パーサー追加ゼロ・Plan 原文でも GitHub 上でも邪魔にならない）。
  GitHub 表示でも折りたたみたい場合は `<details>/<summary>` — `esc_vue()` の生 HTML
  パススルー対象に追加した（ペアで書く前提。閉じ忘れは Vue コンパイルエラー）。
  書き方は PlanTemplate.md にコメントで案内。また実ビルドで発覚した「インラインコード内の
  `{{.go_template}}` が Vue interpolation として解釈されビルドが落ちる」問題は、
  `markdown.config` の `code_inline` レンダラ差し替え（v-pre 付与）で解決した

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
- [x] `npm run dashboard:dev` でダッシュボードが閲覧でき、プランビューアで Plan 本文が読める（2026-07-16 オーナー確認「読めてる！」dc_mrnll3egcfnd） <!-- human-judgment -->
- [x] `bash .claude/addf/tests/run-all.sh` 全通過
- [x] lint 一式（plan-status / residual-paths / template-sync / checklist / json / toml / frontmatter）全通過

フェーズC:

- [x] `dashboard:dev` 起動中に `/api/comments` の GET/POST/PATCH（reply・resolve・404・400）が動作する（curl 実測済み）
- [x] コメントが `.claude/addf/DashboardComments.json` に書き出され、再生成後の「要フィードバック」ページに未解決分が表示される
- [x] `~/.crit/reviews/` の未解決コメントが「要フィードバック」ページに集約される（実物1件で確認）
- [x] CLAUDE.md ブートシーケンス 1.7 が配線され、同期ペア lint（3/4/5）が通過する
- [x] `<details>/<summary>` と `::: details` がプランビューアで折りたたみとして機能し、インラインコード内 `{{...}}` でビルドが落ちない（vitepress build 通過）
- [x] ブラウザでアンカーコメントの一連の流れ（ホバー→コメント→バッジ→resolve）をオーナーが確認する（2026-07-16 実運用で確認済み — 13件のコメントが UI 経由で往復。dc_mrnlnuvc57ns） <!-- human-judgment -->

### フェーズC Stage 2 レビュー反映記録（2026-07-16・3体並列）

- [Critical×2体] `parse_crit_reviews()` の型ガード不足（crit スキーマドリフトで生成全体クラッシュ・
  両体が DS/合成サンドボックスで独立に実測再現）→ isinstance ガード追加＋ Test 10
- [Critical] `<details>` 閉じ忘れで vitepress build 全体クラッシュ（code-review が実測）→
  `_collapse_tags_status()` のバランスチェックで不均衡時は全エスケープへフォールバック＋ WARN ＋ Test 9
- [High] `/api/comments` の read-modify-write 競合でコメント消失 → Promise キューで直列化
- [Medium] anchor 同文重複の誤マッチ → `anchor_occurrence` フィールド新設（クライアント算出・サーバー保存）
- [Medium] ホバーボタンが余白で残留 → ブロック外で非表示化。[Low] scrollX・tr→td/th・except 拡大も反映
- [Medium] ブートシーケンス 1.7 の存在ゲート文言（3ファイル）・addf-migrate に DashboardComments.json 補完を追記
- [Medium] レビュー実測で混入したダミーコメントをコミット前にリセット
- [Info] README のダッシュボード機能未記載 → 主題外・Plan 0065 に切り出し
- ポート注意: config.mts の port 指定は CLI `--port` より優先される。テスト・別ポート起動は
  `ADDF_DASHBOARD_PORT` で上書きする（Test 12 実装時に発見）

## AI 実装時間見積もり

フェーズA は1セッション以内
