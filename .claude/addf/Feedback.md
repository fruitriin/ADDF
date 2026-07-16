# Process Feedback

開発プロセスの振り返りと改善を記録する。

## 記録方法

タスク完了時や問題発生時に、以下のいずれかのセクションに追記する。

## オーナーフィードバック

- 2026-07-11: **並行 Plan の停止依頼→スタール確認→引き継ぎ完走（v0.6.2 リリース作業中）**: 同一
  working tree で v0.6.2 のリリース準備を進めているセッションがある中、別セッションが並行して
  Plan 0053 に着手していることが判明した（`.claude/addf/knowhow/ADDF/cron-loop-worktree-race.md`
  に記録済みの並行実行競合が、今回は CHANGELOG.md の**同一セクション内**での重複という
  従来より踏み込んだ形で再発 — 詳細な対処法は同 knowhow に追記済み）。オーナーの依頼で
  `TODO.addf.md` に「Plan 0053 完了後は `/loop` を止めてほしい」という注記を残したが、その後
  20分・25分と2回間隔を空けて確認しても working tree に進捗が見られず、オーナーが「向こうは
  おそらく停止している」と判断。オーナーの指示で本セッションが Plan 0053 を引き継いで完走させ、
  そのままリリース作業に進んだ。相手セッションが実際に何だったか（cron・`/schedule`・別 VSCode
  ウィンドウの `/loop`）は `crontab`・`launchd`・`CronList`・`RemoteTrigger` を確認しても
  特定できなかった（いずれも無関係かつ無効という結果のみ判明）
- 2026-07-09: Plan 0048（検討スタブ・レビューエージェント感情フィードバック構想）は、オーナーが AI開発系勉強会で登壇した際に感想が全く来なかった実体験と、ADDF のレビューエージェント運用実績（ペルソナ並列レビューの効果・代替わり日記が感情語彙をほぼ持たない事実）を突き合わせた対話から生まれた。オーナーの立場は「エージェントに本当に感情があるかどうかの議論はどうでもよく、良いプロダクトのためという大義名分で、減点法のレビューとグリーンテストだけを報酬にしているエージェントに加点方向のフィードバックを返す仕組みを作るべき」というもの。**この構想を実装・調整する際は、Plan 0016〜0020 と同じく「エージェントの住み心地」の趣旨（責めない・強制しない・温度を保つ、称賛を強制しない）を守ること**。opt-in/opt-out や発動条件などの未解決点は Plan 0048 の「未解決の問い」を参照
- 2026-06-10: Plan 0016〜0020（迷ったときの作法・代替わり日記・knowhow ライフサイクル・分かれ道の目印・視点ずらしレビュー）は、エージェント（Fable）へのインタビューとオーナーの対話から生まれ、実装を担当したエージェント自身が「Questions.md がある家は呼吸が楽」と評した。オーナーからも「一緒に作れてよかった」と好評。これらの機能は**エージェントの住み心地のために作られたもの**であり、変更時はその趣旨（責めない・強制しない・温度を保つ）を守ること

## 問題の記録

- **cron 経由 `/loop 1h /addf-dev` の並行実行が同一 working tree に競合を起こした**（2026-07-10）:
  オーナー指示で `/loop 1h` を使い `/addf-dev`/`/addf-speculate` の自律ループを設定したところ、
  1サイクル目（Plan 0044 実装中）にバックグラウンドで発火した別サイクルが、同じ working tree に
  対して別の Plan（0049-model-allocation-policy）を無コミットのまま並行実装していた。
  `.claude/addf/plans-add/TODO.addf.md` の別々の行を両サイクルが同時に編集しており、`git status`
  の外部変更通知で発覚。行が異なったため実害（データ損失・コミット破壊）はなく、自分の変更だけを
  含む中間ファイルを作って先にコミットし、相手の保留分を working tree に復元して収束させた
  （手順の詳細は `.claude/addf/knowhow/ADDF/cron-loop-worktree-race.md`）。CLAUDE.md の
  「並列実装方針」（git worktree 隔離）は `Agent` ツール経由の委譲を想定しており、cron 発火による
  `/addf-dev` 再入はこの方針の対象外になっている構造的なギャップ。同じ行・同じ Plan 番号の選択・
  同時 `git commit` が起きれば次はもっと深刻な衝突になりうる
- このリポジトリ自体がADDフレームワーク本体のため、`addf-contribution-agent` の検出結果（アップストリームコントリビューション候補）はそのまま自身に適用済み。フレームワーク本体での `addf-contribution-agent` の有用性は限定的。ただし**「ダウンストリーム配布時の安全性」観点の指摘は本体でも有効**（Plan 0021 で lint スクリプトの配布時誤 ERROR を検出し、フェーズ内で SKIP 設計に修正できた。Plan 0058 でも「実リポジトリ固有コンテンツ依存テストの DS 誤 FAIL」を Critical として実測検出した）
- **「実リポジトリ固有コンテンツ依存のテストアサーション」が同型のまま再発した**（2026-07-16
  Plan 0058）: Issue #29 / Plan 0055 で「downstream で必ず FAIL する固定アサーション」を
  直した5日後に、ダッシュボード生成テストの初版が「実在 Plan がたまたま含む文字列への
  grep」「Plan 1件以上の前提」という同じ欠陥クラスを再生産した。レビュー網（contribution-agent
  の DS サンドボックス実測）は機能した。対処は合成フィクスチャの drift-injection 方式
  （`.claude/addf/knowhow/ADDF/sync-lint-design.md` の「動的アサーション化」節に一般化を追記済み）。
  **テスト新設時の自問「このアサーションは Plan が0件の空のダウンストリームリポジトリでも
  成立するか？」を習慣化する**
- **並行セッションが Plan 0059〜0064 を起票・コミットしたが TODO.addf.md 未登録のままだった**
  （2026-07-16 Plan 0058 フェーズC 実施中）: 本セッションの作業中に別セッションのコミット
  （13de93f）が main に入った。行レベルの衝突・実害はなし（cron-loop-worktree-race の
  緩い再発形）。ダッシュボード再生成の「Plan コピー 58→64件」の増分で気づき、本セッションが
  TODO 登録を代行した。**Plan 起票コミットには TODO 行の追加まで含める**（起票と登録を
  分けるとこの形のドリフトが生まれる。lint ペア6 が最後の網になるが、発見が次の lint
  実行まで遅延する）

## 改善アクション

- ADD フレームワーク開発の計画は `.claude/addf/plans-add/`、knowhow index は `INDEX.addf.md` で管理する（`.claude/addf/plans/` と `INDEX.md` はダウンストリームプロジェクト用）
- CLAUDE.md はダウンストリームテンプレートとして汎用性を保つこと。ADDF 固有の参照（TODO.addf.md 等）は CLAUDE.repo.md に置く（Plan 0008 で発見・修正済み）
- `/dev-loop` スキルのブートシーケンスが `TODO.md` を参照するが、ADDF 本体では `.claude/addf/plans-add/TODO.addf.md` が正。`/addf-dev` 側は CLAUDE.md のブートシーケンスに従うので問題ないが、汎用 `/dev-loop` 使用時は注意
- CLAUDE.md のマイグレーション戦略: `CLAUDE.repo.md` にプロジェクト固有設定を寄せる設計方針を維持することで、CLAUDE.md のマイグレーションを単純な上書きに近づける。この方針を崩すとマイグレーション実装が複雑化する（Plan 0011 レビューで発見）
- 同期ファイルペア（CLAUDE.md ⇔ AGENTS.md / ProgressTemplate.addf.md ⇔ Progress.md・ProgressTemplate.md / CLAUDE.md ⇔ development-process.md / CLAUDE.md ⇔ addf-init コピーリスト / TODO ⇔ Plan 実装状況ヘッダ）のドリフトは Plan 0021・0022・0024 で lint 化済み（`lint-template-sync.py` ペア1〜6、テストは `run-all.sh` に組み込み）。同期対象を変更したら `/addf-lint` のセクション6を実行して確認する。**新たな同期ペアが生まれたら lint にペアを追加し、addf-lint.md セクション6の表も同時に更新すること**（ペア5追加時に表の更新が漏れた実績あり。意思で覚えず機械化する — 詳細は `.claude/addf/knowhow/ADDF/sync-lint-design.md`）
- CLAUDE.md に新しい `.claude/` 配下ファイルへの参照を追加するときは、addf-init のコピーリスト（または .gitignore ADDF ブロック）への追加もセットで行う。漏れは lint ペア5が WARNING で検出する（Plan 0022）
- addf-dev.md がテンプレートのステップ番号を直接参照していた（「ステップ 8〜13」が旧番号のまま残留）。番号参照はセクション名併記にする（Plan 0017 レビューで発見・修正済み）
- 手順書（Release.addf / addf-init / addf-migrate / ProgressTemplate 系）に「確認/検証」ステップを追加するときは、実行チェック（コードブロック・コマンド）か `<!-- human-judgment -->` マーカーの裏付けを添える。裏付け漏れは `/addf-lint` セクション9（lint-checklist.py・WARNING のみ）が検出する。新しい手順書を検査対象にする場合は lint の TARGETS に追加する（Plan 0027）
- lint スクリプトを新設したら、**その lint が生まれるきっかけになった当のケースを、裏付けを剥がした状態で再現テストする**（Plan 0027 レビューで「メタ lint 自身が flagship 項目の裏付け喪失を検出できない」High 2件を検出。ドリフト注入 TDD — 詳細は `.claude/addf/knowhow/ADDF/checklist-backing-lint.md`）
- 変更が `.claude/addf/plans-add/` 配下のみ（＝ダウンストリーム配布対象外のドキュメントのみ）のタスクでは、`addf-contribution-agent` は検出対象がないためスキップしてよい（2026-07-03 の品質向上プラン起案タスクで適用。コード・配布ファイルに触れる場合は従来どおり実行する）
- Python 3.11+ の stdlib（`tomllib` 等）**または PEP 723 サードパーティ依存（pyyaml 等）**を使う addfTools スクリプトを新設したら、(1) import ガード（責務別の3類型: lint=SKIP / 実行前ゲート=フェイルセーフ ERROR / 変更系=ERROR。`.claude/addf/knowhow/ADDF/sync-lint-design.md` 参照）、(2) テストの uv フォールバック、(3) 手順書の「uv が無ければ python3 直接実行」注記（サードパーティ依存は入手方法 `pip install ...` まで）、の3点をセットで入れる。テストだけに uv フォールバックを入れると手順書経由の実行者が罠に落ちる（2026-07-03 tomllib 修正の教訓。同日の投機サイクルレビューで lint-frontmatter.py の pyyaml が同型の穴と判明し類型を拡張）

- B2（cp 上書き副作用の deny ルール Plan 起案・2026-07-06 オーナー判断）: **保留**。「悩みどころ・環境によるノイズは増えてほしくない」との判断。今後、cp の上書きで実害が観測されたら再検討する（実害の実測をトリガーにする）
- フックで Behavior.toml を読む場合、Python 依存を避けるため bash+awk の簡易パースを選ぶことが正当な選択肢だが、8種の落とし穴（`=` 切り捨て・コメント除去のクオート無視・ヘッダ行末コメント・jq `//` の空文字列素通し・ファイル名サニタイズ不足・秒精度衝突・フォールバック経路のテスト漏れ・macOS bash 3.2 の set -u × basename 相互作用）を伴う。Plan 0042 の code-review が実サンドボックス試行で全て発見し、対策込みで `.claude/addf/knowhow/ADDF/bash-toml-parse-pitfalls.md` に類型化した。次に同型のフックを書くときは同ファイルを参照する
- Plan 実装時、Progress.md のチェックボックスをサブタスク完了と同期して更新する運用を徹底する（doc-review Warning: 実装済みなのに `- [ ]` のまま残ると、代替わり日記を跨いだ次の代の判断を誤らせるリスク。Plan 0042 レビューで指摘）。日記が「文脈」を残すのに対し、チェックボックスは「事実」を残す — 両方が実態と一致していることが引き継ぎ条件
- lint-template-sync ペア1（Progress.md ⇔ ProgressTemplate.addf.md）は**厳密なテキスト一致**を要求する ERROR 級検査。Progress.md を新規生成するときは `head -N` で切らず、**テンプレ全文を完全コピー**すること（`cp .claude/addf/templates/ProgressTemplate.addf.md .claude/addf/Progress.md`）。行数固定は本体側の追記でズレる（Plan 0047 完了処理で `head -84` を使い MISSING エラーが出た教訓）
- 運用ルールで新規に参照リンクを追加する場合、テンプレ側と Progress.md 側で相対パスが異なる（`../guides/...` vs `guides/...`）と ERROR ペア1に引っかかる。**リンク書式は避け、パス直書きの参照文字列に統一**すると同期を維持できる（Plan 0047 の変更ルート判断表参照で実践。「[text](path)」ではなく「`変更ルート判断表`（`.claude/addf/guides/speculative-development.md` の「変更ルート判断」節）」形式）
- CLAUDE.repo.example.md の「品質ゲート拡張」セクション（Stage 1/2 分割の任意採用テンプレ）に、`ProgressTemplate.addf.md` の運用ルール7と重複した対応方針の記述が独立に存在した。lint-template-sync ペアの追跡対象外だったため Plan 0047 で更新時に取り残された（doc-review が発見）。今後同種のセクション追加時は、運用ルールへの参照に留めることで単一ソース化を保つ
- 「実測してから判断する」型 Plan（0044・0045）で、code-review が2件連続で実測データの不備（0044: 算術誤り／0045: 探索条件が狭く反証事例〔taskbar〕を見落とし）を独立に発見した。**実測ベース判断 Plan では、実装者自身の自己レビューでは探索条件のバイアスに気づきにくい**ため、code-review 依頼時に「実測データの数字・除外判断の妥当性を実物と突き合わせて検証してほしい」と明示的に頼むと有効（詳細: `.claude/addf/knowhow/ADDF/measurement-sampling-bias.md`）
- Plan の `## 実装状況:` ヘッダを複数行に分割すると、`lint-plan-status.py` の正規表現が行単位マッチのため値が途中で切り詰められる（ATX見出しは1行で完結する仕様と衝突）。今回はたまたま判定結果に影響しなかったが、doc-review が Plan 0039 で発見。**ヘッダは必ず1行で書く**（Plan 0039 対応で修正済み）
- doc-review が「本 diff の変更対象ではないが、今回の変更（VitePress サイト公開）で既存のドリフトが可視化された」パターン（README.md のドキュメントテーブルが実際のガイド一覧より2件少なかった）を発見した。**主題外のため Plan 0050 として切り出し**、Progress.md 運用ルール7の「判定に迷ったら主題外に倒す」を実践した一例
- knowhow の片方向リンクを lint（セクション8）に基づいて解消する際、**「## 参照」節（Plan・ツール等への参照）と「## 関連ノウハウ」節（peer knowhow への相互参照。lint の検査対象はこちらのみ）の役割が混在しているファイルがあると、逆方向リンクを新設した直後に同じリンク先が両節に重複して現れる**ことがある（Plan 0051 の doc-review で検出。`cron-loop-worktree-race.md` に新規 knowhow との相互参照を追加した際、既存の「## 参照」節に同一リンクが既にあった）。対応: 重複を検出したら「## 関連ノウハウ」側を正とし「## 参照」側の同一リンクは削除する（lint が検査するのは「## 関連ノウハウ」のみのため、そちらに一本化する）
- knowhow の一方向リンク解消 Plan を起票する時点の「N件」という数え上げは、**その時点で存在するファイル間の走査に限られる**。新設 knowhow ファイル自身が持つ相互参照（新設ファイル→既存ファイル／既存ファイル→新設ファイルの追記）は、Plan 起票時にはまだ存在しないため数に含まれない。実装後の実際の追加行数は「Plan 記載件数 + 新設ファイルとの相互参照分」になりうる（Plan 0051: 記載12件 + 新設分2件 = 実装差分14件）。完了条件の数値は「lint 検出件数（0件化）」を主張の軸にし、追加行数は別途正確に数えて併記すると齟齬がない
- `lint-residual-paths.py` に新しい残存パス検査（今回は `.gitignore` グロブパターンの非対称検知）を追加するタスクでは、**その検査対象そのものを説明するために書く Plan 本文・Progress.md 日記・knowhow への追記自身が、新設した検査に引っかかる**（Plan 0052 で3回連続発生: Plan 本文2箇所・Progress.md 日記1箇所・knowhow 2箇所、計5箇所で `residual-path: allow` マーカー漏れの ERROR が出た）。対応: 同種の lint 強化タスクでは、実装完了後だけでなく**自分が書いた Plan/Progress/knowhow の文章を書き終えるたびに** `lint-residual-paths.py` を再実行する（最終確認まで溜めない）。レビューエージェント3体（code-review・doc-review・contribution-agent）が独立にこの漏れの一部を指摘したのも実測（詳細: `.claude/addf/knowhow/ADDF/persona-review-oneshot.md` の追記）

- Plan 0040 フェーズ1（ccchain 導入）で、`lint-residual-paths.py`（Plan 0037・0052 で強化した
  残存パス検査）が**外部リポジトリ（EnumaElish）の `docs/knowhow/ccchain-dogfooding.md` という <!-- residual-path: allow -->
  パスへの言及**にも誤反応した。ADDF は `docs/knowhow` → `.claude/addf/knowhow` に移行済みのため、 <!-- residual-path: allow -->
  他リポジトリの同名パスへの言及もリテラル一致で引っかかる。Plan 0052 で発見した「自分の
  Plan/Progress/knowhow への追記が自分の新設 lint に引っかかる」パターンの亜種として、
  **外部プロジェクトの旧構造由来のパス名（`docs/knowhow`・`docs/plans` 等の一般的な命名）に <!-- residual-path: allow -->
  言及する knowhow を書く際も同様の誤検知が起きうる**ことが分かった。対応は同じ
  （`residual-path: allow` マーカーを都度追加し、コミット前に `lint-residual-paths.py` を通す）
- ccchain 導入（Plan 0040）で、対話セッション中の「やってみたいな」という一言だけでは、
  auto mode の権限フィルタが (1) 外部リポジトリのコード取得・ビルド（`go install`）、
  (2) 自己ゲート的なフック配線（PreToolUse(Bash) への追加）を許可しなかった。
  いずれも `AskUserQuestion` で一段階ずつ明示確認を取ることで解消した。**「試してみたい」という
  カジュアルな着手指示は、外部コード実行や自己変更を伴うステップの許可としては扱われない**
  （cron 自律ループでの懸念〔Q5〕とは別に、対話セッションでも同様の慎重さが必要という実例）

- `/addf-lint` を fork 実行するエージェントは、メインセッションの会話コンテキスト（直前の
  判断・設計意図）を持たずファイルの現在状態だけから再構築するため、**意図的な設計上の
  非対称・分離**（今回は Plan 0040 フェーズ1〔settings.local.json 配線〕とフェーズ2
  〔settings.json 限定の sync-ccchain.py〕を意図的に未統合のままにした判断）を「矛盾」
  「バグ」として報告してくることがある。これ自体は forked エージェントの正しい振る舞い
  （文脈を持たないなら指摘するのが安全側）だが、**設計上意図的な非対称は、その場しのぎで
  終わらせず knowhow に明記しておく**ことで、次に fork 実行された lint がまた同じ「発見」を
  報告して人間の確認コストを消費するのを防げる（今回は `ccchain-dogfooding-phase1.md` に
  「フェーズ1とフェーズ2の配線先は意図的に別ファイル」を追記して対応）

## 完了済み

- ~~Plan 0004 実施時に `add-Behavier.toml` を `addf-Behavior.toml` にリネームする~~ → Plan 0004 で実施済み
