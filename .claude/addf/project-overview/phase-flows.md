# フェーズ進行スキル一覧

> 毎回の実行時に全スキルをスキャンして自動生成。対象リストは決め打ちしない。
> 検出基準: Phase/Step 番号付き構造、または3ステップ以上の手順フローを持つスキル。
> 生成日: 2026-07-07

## 検出結果: 18本（うちオプトイン 3本）

全スキル 19本（常設 16本 + オプトイン 3本）中、非該当は addf-mode の1本。

| スキル | フェーズ数 | 概要 |
|---|---|---|
| addf-dev | 5 steps | コンテキスト読込→タスク選択（アイドル時は /addf-speculate へ分岐）→実装→完了処理→ループ継続（コンテキスト満杯時の出口込み） |
| addf-speculate | 10 steps + 枝番 1.5/1.7/1.8 + clean + 昇格2経路 + 部分昇格/Pending + 深化ブランチ | 発動ガード→再構築と掃除→窓検出→選定（投機適性判定）→worktree 起動→Stage 1→記録→integration 統合→Stage 2→Dashboard→push→完了 |
| addf-init | 4 phases + 枝番 2.5/2.7 ×3経路 + 部分導入正規化 + check | 状態確認→情報収集→干渉チェック→導入前レビュー→コピー&マージ→完了 |
| addf-migrate | 6 phases + 枝番 2.5/7.5/14.5/14.6/16.5 | 状態確認（部分導入検出込み）→最新取得→ディレクトリ大移行（v0.6.0 ワンショット）→差分算出→プレビュー→適用→完了（lock 更新・plan-audit ワンショット案内） |
| addf-overview | 8 steps (full) + 4 steps (patch) | 経験読込→データ収集→フロー検出→システム発見→生成→経験記録→.lock→報告 |
| addf-plan-audit | 3層走査 + 5 steps | 層1構造検査→層2意味読解→層3TODO突合→処置3択の提案→検出一覧の永続化 |
| addf-release | 4 steps | プロジェクト種別判定→手順ロード→実行→経験更新 |
| addf-permission-audit | 11 steps | ノウハウ読込→種別判定→権限収集→分類→配置→出力→構文検証→レビュー→適用→確認 |
| addf-lint | 12 checks | JSON構文→hooks権限→frontmatter→TOML→INDEX整合→テンプレート同期（7ペア）→knowhow鮮度→双方向リンク→チェックリスト裏付け→オプショナルスキル同期→hooks配線→Plan状態整合 |
| addf-knowhow | 4 phases | 調査→記録→自己ブラッシュアップ→分かれ道の目印の記録提案 |
| addf-knowhow-filter | 5 steps | Plan読込→knowhow走査→関連判定→結果出力→（該当なし報告） |
| addf-knowhow-index | 2モード（reindex は番号付き手順） | インデックス参照 / 再構築＋鮮度レポート |
| addf-knowhow-revise | 4 steps | 対象特定→再検証（妥当/訂正/superseded/retired）→訂正履歴→reindex・報告 |
| addf-knowhow-network | 5 steps | 関連性抽出→関連セクション生成→双方向リンク担保→ハブサマリ→報告 |
| addf-experience | 4 phases | スキャン→判定→修正→検証 |
| addf-gui-test（オプトイン） | 7 steps | シナリオ読込→Behavior確認→前提条件→手順実行→期待結果比較→クリーンアップ→レポート |
| addf-annotate-grid（オプトイン） | 5 steps | 引数解析→ツールビルド→グリッド描画→出力→次ステップ案内 |
| addf-clip-image（オプトイン） | 5 steps | 引数解析→ツールビルド→領域切出し→出力→確認 |

**非該当**: addf-mode（引数なし/ありの2分岐のみで通し番号のフェーズ進行ではない）

**前回（2026-07-05 生成）からの変更**: addf-plan-audit を新規掲載（v0.6.0 で新設 — 3層走査のフェーズ進行あり）。addf-lint は 11→12 チェック（Plan 状態整合を追加）、テンプレート同期は 6→7 ペア。addf-migrate に Phase 2.5（ディレクトリ大移行）・16.5（plan-audit ワンショット案内）等の枝番が追加。addf-speculate に手順 1.8（大改造の窓検出）・昇格2経路（A: プロンプト / B: PR）・部分昇格と持ち越し（Pending）・深化ブランチが追加。パス表記は全面的に `.claude/addf/` 集約後の新構造。

**参考**: オプトインエージェント addf-ui-test-agent（`.claude/addf/optional/agents/`）はエージェント定義のため本一覧のカウント対象外。

---

## addf-dev

> TODO.md から未実施タスクを1つ選んで実装・品質検証・コミットまで完遂する。

1. コンテキスト読み込み（Feedback → TODO → Progress）
2. タスク選択（優先1: 複利効果 / 優先2: 若番。アイドル時: `[speculation].enable = true` なら /addf-speculate を1サイクル実行して手順4へ、false ならオーナーに確認）
3. 実装（CLAUDE.md ブートシーケンス + 2段階品質ゲート。日記（代替わり引き継ぎ）を書く。閾値割れは relaxed: Questions.md へ / unattended: speculative/ で投機続行 / worktree 下は閾値1段下げ可。Stage 構成はダウンストリームの Progress.md 運用ルール側が正）
4. 完了処理（Progress 運用ルールの「ノウハウ蓄積」「フィードバック記録」「アーカイブとコミット」= ステップ 9〜15。PR 本文は guides/pr-format.md 規約）
5. ループ継続（/loop が次サイクルを自動スケジュール。コンテキスト満杯時の出口: 残量少でもループを止めず、復帰容易性の高いタスクを優先・one-shot 級は着手しない・進捗外部化を密に刻む）

---

## addf-speculate

> アイドル時（着手可能なタスクがないとき）に、直交概念を git worktree で投機開発する。`[speculation].enable = true` のオプトイン時のみ動作。

- 1: 発動ガード（speculate-guard.py — enable/型不正/上限。exit 0/1/2）
- 1.5: モード確認（interactive のみ開始前にオーナーへ一言確認）
- 1.7: 再構築と掃除（speculate-reconcile.py で Worktrees.md と git 実体を突合。復元・掃除候補・detached worktree 検出）
- 1.8: 大改造の窓検出（在庫ゼロ（speculative_worktree 空 + pending_count=0 + active_count=0）× one-shot マーカー付き未着手 Plan → オーナーへ実施提案。窓保持カウント3で解除。無応答を承認とみなす自動着手は禁止）
- 2: 投機対象の選定（計画済み残課題 > Questions.md 最有力解釈 > 常設リクエスト。投機適性判定（向き/不向き/禁止）— 不適合は捨てずに Plan 化フォールバック）
- 3: worktree の起動（speculative/&lt;concept&gt; + `.claude/.` 複製 + venv/node_modules 除去 + checkout 復元）
- 4: 実装と Stage 1（worktree 内。依存再構築→ビルド・Lint・テスト。失敗は深追いせず打ち切り）
- 5: Worktrees.md への記録（状態: 開発中/テスト通過/テスト失敗/衝突/統合済み/放棄/昇格済み/上限で待機/要再検証/Pending）
- 6: integration 統合（speculate-integrate.py で integration/loop-&lt;日付&gt; に squash 統合。conflicted は feature 側で解消 or 外す。integrated/conflicted/missing/empty/commit_failed を解釈）
- 7: Stage 2 — integration 一括ゲート（相互作用テスト + code-review ペルソナ並列。指摘は feature 単位に帰属）
- 8: Dashboard への書き分け（投機ブランチ（採否判断待ち） / 気になった点）
- 9: ブランチの退避（speculative/* を origin へ push — エフェメラル環境対策）
- 10: 完了処理（Progress.md 日記に記録してコミット。単独実行時も日記とコミットは最低限実施）

サブコマンド `clean`: 2日以上前の integration/loop-* 自動削除＋ `--delete` 明示指定の speculative 削除（Worktrees.md の「昇格済み/放棄」記録と突合、なければ ERROR。dirty は既定拒否）。
昇格手順（オーナー承認必須・自動マージ経路なし）: 経路A（プロンプト指示 → A-1〜A-8: 承認→衝突解消の自己完結→squash マージ→昇格後テスト→記録更新→深化の順序制約→clean→持ち越し要再検証） / 経路B（PR 経路 → B-1〜B-3: Stage 2 通過 feature のみ PR 作成→PR 番号注記→マージ待ち。マージ後 後-1〜後-5）。
部分昇格と持ち越し: 通った分だけ先に昇格・残りは「要再検証」→再検証。滞留は「Pending」（在庫5本まで）。
深化ブランチ: `speculative/<concept>--deep-<sub>`。親の採否に運命連帯（放棄連鎖 / 昇格時は --onto 繰り上げ rebase）。2世代まで。

---

## addf-init

> ADDF プロジェクトの初期セットアップまたは構造検証を行う。引数なしで初期化、`check` で構造検証。

**外部からの起動（既存プロジェクトへの導入）**: URL 検証（https:// のみ）→ tmp クローン → 導入先=cwd・種別は「ADDF 利用プロジェクト」固定 → 既存ファイルから自動推定 → init モード Phase 1 へ
**部分導入からの正規化**: lock 不在＋ADDF 由来ファイル存在のプロジェクトを正規状態へ。カテゴリ1を「安全一括上書き」（addf- プレフィックス等で所有識別・差分ゼロのみ一括承認）と「個別確認必須」（hooks / AGENTS.md / Behavior.toml — 存在≠所有）の2群で読み替え。完了時に lock 生成・/addf-plan-audit 初回実行を案内
**init モード**:
- Phase 1: 状態確認（lock 有無で導入済み / Template 経由 / 部分導入 / 既存プロジェクト / 新規を判別）
- Phase 2: セットアップ情報の収集（外部起動: 自動推定+確認 / Template 経由: 対話）
- Phase 2.5: 干渉チェック（競合なし / マージが必要 / 要確認 / 新規作成に分類。Template 経由はスキップ）
- Phase 2.7: 導入前レビュー（hooks・権限変更・CLAUDE.md への影響を明示して確認）
- Phase 3: ファイルコピー & マージ（カテゴリ1: 無条件コピー（`*.addf.md` は除外規則） / カテゴリ2: インテリジェントマージ（settings.json ユニオン・.gitignore マーカーブロック・CLAUDE.md 退避） / カテゴリ3: プロジェクト固有ファイル生成（lock は ref = クローン元タグ））
- Phase 4: 完了（レポート・tmp 削除）
**check モード**（読み取り専用）: 必須ファイル → @メンション解決 → TODO⇔plans 整合 → lock 妥当性（ref 形式） → AGENTS.md 存在 → Hooks 配線 の6項目

---

## addf-migrate

> ADDF フレームワークを最新版にアップグレードする。lock.json のバージョンと最新版の差分を算出し、安全にマイグレーションする。

- Phase 1: 状態確認（lock の ref 読込 — 旧位置 `.claude/addf-lock.json` フォールバック・旧形式 commit は v&lt;version&gt; タグ読み替え。git clean 確認・URL 検証。lock 不在＋ADDF ファイル検出 → 部分導入の初期正規化モードを提案） <!-- residual-path: allow -->
- Phase 2: 最新版の取得（mktemp + depth 1 クローン）
- Phase 2.5: ディレクトリ大移行（v0.6.0 新構造・ワンショット。構造の差分で発動。枝番 6.1〜6.10: 発動判定→道具の導入→check プリフライト→apply（git mv）単独コミット→rewrite 別コミット→残存参照ゼロ確認→ビルド・テスト（rewrite 射程外4類型の露見点）→射程外の手動確認→失敗時 backup ref 巻き戻し→新構造で続行）
- Phase 3: 差分算出（対象: addf- 系・templates・addfTools・tests・guides・knowhow/ADDF 等 / 対象外: Progress・Feedback・.exp.md・CLAUDE.repo.md 等。7.5: 旧配布 `*.addf.md` 残留検出）
- Phase 4: 変更の確認（カテゴリ別プレビュー + CHANGELOG 抽出表示 → 承認）
- Phase 5: 適用（settings.json マージ、addf- ファイル上書き（ADDF 由来のみ — 独自ファイル保護）、CLAUDE.md はテンプレート部分のみ、.exp.md リネーム案内。14.5: オプショナルスキル同期。14.6: .gitignore ADDF マーカーブロックの検査付き置換）
- Phase 6: 完了（lock 更新（ref = v&lt;new-version&gt;）、tmp 削除。16.5: 差分に addf-plan-audit.md が新規追加されていたら /addf-plan-audit のワンショット実行を案内。完了レポート）

---

## addf-overview

> CLAUDE.md・スキル・フック・エージェントのエコシステムを網羅的に記録し、project-overview/ に静的ドキュメントとして出力する。概念システム別に分類。

**full モード**:
- Step 0: 前回の経験を読む（.exp.md）
- Step 1: 全データ収集（A: プロジェクト構造 / B: スキル全件 / C: エージェント全件 / D: フック全件 / E: 主要ファイル / F: コミット情報）
- Step 2: フェーズフロー自動検出（全スキャン・決め打ち禁止）
- Step 3: 概念システムの探索的発見（フラット列挙→クラスタリング→命名→前回差分確認→残余チェック）
- Step 4: ドキュメント生成（INDEX / system-* / phase-flows / interactions / claude-md-deps）
- Step 5: 経験の記録（.exp.md へ実行記録を追記）
- Step 6: .lock 更新（HASH|COMMIT_MSG|DATE）
- Step 7: 完了報告

**patch モード**:
- P1: .lock を読み差分取得
- P2: 変更ファイルを概念システムにマッピング（.exp.md の分類基準。不能なら full を要求）
- P3: 影響するシステムだけ再生成（phase-flows / interactions は更新しない）
- P4: 経験の記録 + .lock 更新 + 完了報告

---

## addf-plan-audit

> 「完了扱いだが未完了タスクが残っている計画」（埋没）を掘り起こす棚卸しスキル。3層で Plan を走査し、処置3択を提案する。完了状態の変更・回収計画の採否はオーナー判断。

1. 層1: 構造検査（lint-plan-status.py の実行。ERROR/WARNING を取り込み。SKIP された旧書式 Plan は lint の死角 — 層2 へ全件引き継ぐ）
2. 層2: 意味的パターン（エージェントの読解。(a) 層1 SKIP 一覧の全件読解 / (b) grep 候補収集（先送り・残課題・別途 等）→ 全文読解。後続 Plan の実在と相互リンク・番号ずれ・関連 Plan セクションの風化・ヘッダ注記と本文の食い違いを判定。該当行番号と引用を記録）
3. 層3: TODO との突合（lint-template-sync.py ペア6の結果 + ペア6が見ない粒度（状態注記の食い違い・現在のフェーズ行・アーカイブ残存）をエージェントが読む）
4. 検出結果の報告と処置の提案（3択: 回収計画に起こす / ヘッダを一部完了に訂正 / 意図的な完了と明記して閉じる）
5. 検出一覧の永続化（トリガー Plan の実装記録に追記、または監査記録 Plan を新設して TODO 登録。検出0件でも「0件 — 3層とも整合」を明記報告）

---

## addf-release

> プロジェクトのリリースを実行する。upstream（ADDF 本体）と downstream で自動的に手順を切り替える。

1. プロジェクト種別の判定（CLAUDE.repo.md の「ADDF 開発プロジェクト」宣言 → upstream / それ以外 → downstream）
2. リリース手順の読み込み（upstream: `.claude/addf/Release.addf.md` 必須 + .exp.md / downstream: .exp.md（リリース戦略の定義元）。無ければ対話ヒアリングで新規作成）
3. リリース手順の実行（読み込んだ手順を上から順に実行）
4. 経験の更新（.exp.md へ追記）

---

## addf-permission-audit

> セッション中の権限要求を3パターン（アップストリーム/ダウンストリーム/汎用）に分類し、適切な settings ファイルへの追加を提案する。

1. ノウハウ読み込み（permission-settings-pattern.md）
2. プロジェクト種別の判定
3. 現在の権限設定を読み込み（settings.json / settings.local.json）
4. セッション中の権限要求を収集
5. 各権限を分類（アップストリーム / ダウンストリーム / 汎用）
6. 配置先を決定（プロジェクト種別 × パターンのマトリクス）
7. 出力（監査結果の表）
8. 構文チェック（`:*` 非推奨 → ` *`）
9. コントリビューションレビュー（addf-contribution-agent で分離パターン検証）
10. apply モード（指定時のみ自動編集）
11. ユーザー確認（コミットしない。承認後のみコミット）

---

## addf-lint

> ADDF フレームワークの整合性チェック（12項目）。品質ゲート前・CI・設定変更後に使う。

1. JSON 構文チェック（lint-json.py）
2. Hooks 実行権限チェック（lint-hooks-exec.py）
3. スキル Frontmatter チェック（lint-frontmatter.py: name, description）
4. addf-Behavior.toml 構文チェック（lint-toml.py）
5. Knowhow INDEX 整合性チェック（INDEX ⇔ 実ファイルの相互存在）
6. テンプレート同期チェック（lint-template-sync.py: 7ペア。exit 0/1/2 = 一致/ERROR/WARNING。upstream/downstream 判定は明示シグナル — 存在≠所有）
7. Knowhow 鮮度チェック（フロントマター有無・🔴 stale・depends_on 切れ → WARNING 止まり）
8. Knowhow 双方向リンクチェック（リンク切れ WARNING・片方向 INFO → /addf-knowhow-network 案内）
9. チェックリスト裏付け検査（lint-checklist.py: 確認/検証ステップの実行チェック or human-judgment マーカー → WARNING のみ）
10. オプショナルスキル同期チェック（sync-optional-skills.py: [gui-test] enable と有効化コピーの整合・孤児検出。exit 0/1/2）
11. Hooks 配線チェック（lint-hooks-wiring.py: hooks ファイル ⇔ settings.json の配線突合。settings.local.json 経由は NOTE、`# hooks-wiring: indirect` エスケープハッチあり）
12. Plan 状態整合チェック（lint-plan-status.py: 完了ヘッダ × 未チェック `- [ ]` 残存の矛盾検出。表記ゆれ状態ヘッダは WARNING、旧書式 Plan は明示 SKIP）

---

## addf-knowhow

> 実装知見を .claude/addf/knowhow/ に記録する。重複チェック・統合と自己ブラッシュアップステップを含む。

- Phase 1: 調査（既存 knowhow 全読み、関連があれば追記・統合を新規作成より優先）
- Phase 2: 記録（フロントマター必須: title / created / last_verified / depends_on / status。`deprecated` は使わない — superseded / retired）
- Phase 3: 自己ブラッシュアップ（正確性・完全性・簡潔性・実用性の4観点で再読・修正。exp へ教訓追記）
- Phase 4: 分かれ道の目印の記録提案（差し戻し・Critical/High 指摘・やり直し・軌道修正があれば関係スキルの .exp.md「🔀 分かれ道の目印」への追記を提案。[計画で防げた] / [作って分かった] を判定。目印ゼロは健全な状態でありうる — 強制しない）

---

## addf-knowhow-filter

> Plan ファイルの内容を受け取り、knowhow から関連するノウハウのパスと要約だけを返す。

1. Plan ファイルを読む
2. .claude/addf/knowhow/ 内の全 .md を読む（INDEX と CLAUDE.md を除く）
3. Plan の実装に必要または有用なノウハウを判定（タイトルで推測せず本文で判断）
4. 結果を返す（パス・要約・関連理由）
5. 関連なしなら「関連するノウハウはありません」

---

## addf-knowhow-index

> knowhow インデックスの参照・再構築（ADDF 本体: INDEX.addf.md / ダウンストリーム: INDEX.md — 種別宣言で判定・存在≠所有）。

- 引数なし: インデックスを読み内容をそのまま返す
- reindex: 1. 全ファイル読み込み → 2. パス・一行要約・キーワード・フロントマター抽出 → 3. 鮮度判定（🟢 fresh 60日以内 / 🟡 aging 60〜180日 / 🔴 stale 180日超 or depends_on 切れ or needs-review — しきい値の定義箇所はここが唯一）→ 4. INDEX 書き出し（superseded/retired は 📜 棚に分離）→ 5. トピック領域グルーピング → 6. 鮮度レポート（stale があれば /addf-knowhow-revise を案内）

---

## addf-knowhow-revise

> 鮮度低下（🔴 stale / needs-review）したノウハウを意味的に再検証・訂正する。

1. 対象の特定（INDEX の 🔴 stale / needs-review。引数でファイル指定可）
2. 再検証（1ファイルずつ: 主張・前提・依存を把握 → 依存先の現状を読み直し → 妥当: last_verified 更新のみ / 部分的に誤り: 訂正＋訂正履歴 / 後継あり: superseded / 参照不要: retired（削除はしない））
3. 訂正履歴の書式（日付・誤り→訂正・根拠）
4. 完了処理（reindex 実行 → 訂正・遷移件数を報告）

---

## addf-knowhow-network

> knowhow 記事同士を GFM リンクで相互接続し、知見ベースを wiki として育てる。

1. 関連性の抽出（概念・キーワード・depends_on から記事間の関連を推定）
2. 関連ノウハウセクションの生成・更新（📜 Superseded / Retired プレフィックス付き）
3. 双方向リンクの担保（retired への片方向は例外、superseded → 後継は双方向必須）
4. ハブサマリ（INDEX 末尾に被リンク数トップ3〜5 — revise の優先対象）
5. 完了処理（追加リンク数・双方向欠落の修正件数を報告）

---

## addf-experience

> スキルの経験ファイル（.exp.md）の @メンション書式を検証・修正する。

- Phase 1: スキャン（.claude/commands/ と .claude/addf/optional/ 配下の全 .md から .exp.md 参照行を抽出・分類）
- Phase 2: 判定（展開すべき（クオート不要） / リテラルで正しい / コードブロック内は変更不要）
- Phase 3: 修正（クオート除去 + 一覧表で報告）
- Phase 4: 検証（再スキャンで意図しない変更がないか確認）

---

## addf-gui-test（オプトイン）

> GUI テストシナリオを実行する（`[gui-test] enable = true` + sync-optional-skills.py apply で有効化された場合のみ配置）。

1. シナリオファイルを読む（引数なしなら一覧表示）
2. Behavior.toml 確認（gui-test.enable / machine — mac 以外は未実装として終了）
3. 前提条件の確認（ツールビルド状態 → 必要なら build.sh）
4. シナリオの手順に従ってテスト実行（一時ファイルは tmp/ へ — /tmp/ 使用禁止）
5. 期待結果と実際の結果を比較
6. クリーンアップを実行
7. 結果を報告（成功/失敗 + 詳細）

---

## addf-annotate-grid / addf-clip-image（オプトイン）

> PNG 画像へのグリッド線・座標ラベル描画 / 指定領域の切り出し（GUI オプトイン有効時のみ配置）。

共通フロー:
1. 引数解析（画像パス・オプション。なしなら使い方表示）
2. ツールビルド確認（未ビルドなら build.sh）
3. 出力パス決定（省略時 tmp/annotated-* / tmp/clip-*）
4. 処理実行（annotate: --divide/--every、clip: --rect/--grid-cell/--grid-range）
5. 結果報告（Read で画像表示。annotate は clip への連携（--grid-cell / --rect）を案内）

典型連携: /addf-gui-test 撮影 → /addf-annotate-grid で座標系確立 → /addf-clip-image で注目領域切り出し（clip は元画像に対して実行）。
