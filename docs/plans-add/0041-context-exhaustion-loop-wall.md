# Plan 0041: コンテキスト枯渇によるループ停止の壁の突破

## 実装状況: 未着手

> 出典: オーナー指示（2026-07-06）—「コンテキスト残量が残り少ないときに記録作業に回れるのはいいとして、いよいよ記載することがなくなったときに能動的に compact できなくてループが止まっちゃう壁を突破する計画を考えてほしい」
> 同日のオーナー対話で方針確定: ペインの核心を特定し、能動コンパクション系のアイデアは死蔵（本 Plan 末尾に記録保存）、教義＋タスク運びを主軸に、副産物として PreCompact トランスクリプトアーカイブを採用。

## 関連 Plan

- [Plan 0023: turn-reminder の関心事分離と能動コンパクション](0023-turn-reminder-context-split.md) — 本 Plan の前提となる残量観測層（context-reminder.py）。本 Plan はその「観測したあと、出口がない」問題を扱う
- [Plan 0017: 代替わり日記](0017-progress-checkpoints.md) — セッション間引き継ぎの既存基盤。「compaction 越え前提のタスク運び」の思想的土台
- [Plan 0016: stop-or-go 教義](0016-stop-or-go-doctrine.md) — 「ループ中の突然死」への既存の備え。本 Plan は「突然死」ではなく「自主停止」を扱う

## 目的

/loop 自走中、コンテキスト残量が尽きかけたエージェントが作業を止めてしまう壁を取り除き、コンテキスト枯渇（と auto-compact）を跨いで自走が継続する状態にする。

## ペインの核心（オーナー確定 2026-07-06）

1. **エージェントがコンテキスト残量が少ないと作業を止めてしまい、次の投機を行えなくなる**
2. **作業を行わないと compaction も起こらず、やはり次の投機を行えない**

つまりデッドロックの原因は「compaction の手段がないこと」ではなく「エージェントが止まること」。auto-compact は作業を続けてさえいれば発動し、復帰フック（Plan 0017 の日記＋`post-compact-recovery.sh`）が受け止める準備は既に整っている。

## 現状の挙動と壁の構造

### 整備済みの機構（Plan 0017・0023）

1. **観測層**: `context-reminder.py` が実測 180k 超過で「知見記録と日記更新を済ませること。そのまま作業を継続してよい」を注入する
2. **記録層**: 日記（運用ルール 3.5）・`/addf-knowhow` で引き継ぎ情報をファイルに退避する
3. **復帰層**: `post-compact-recovery.sh` が `SessionStart(compact)` でブートシーケンス再実行を注入する。compaction が**起きさえすれば**復帰は機能する（実績あり）

### 壁

- エージェントから compaction を能動的に起こす手段は**存在しない**（2026-07 時点の Claude Code 調査で確定）:
  - `/compact` はユーザー専用スラッシュコマンド。Skill/Bash 経由で自セッションに対して呼ぶ手段なし
  - hooks の `PreCompact` は `decision: "block"`（抑止）のみで、発動させる方向の制御は不可
  - Agent SDK には compaction API があるが、Claude Code CLI には露出していない
- auto-compact は harness が「コンテキスト上限接近時」に自動発動する。context-reminder 閾値（180k）〜auto-compact 発動点の間の**グレーゾーン**で、記録を書き尽くしたエージェントは「新規着手は危険・compact 手段はない」の板挟みになり、次サイクルを予約せずループを止める（自主停止）

### 実証済みの知見: トランスクリプトの非対称双方向性（2026-07-06 実験）

トランスクリプト JSONL（`~/.claude/projects/<slug>/<session-id>.jsonl`）とセッションの関係を使い捨てセッションで実験し、以下を確認した:

- **書き込み方向**: セッション → JSONL はリアルタイム追記。ただし実行中のセッションは JSONL を読み直さないため、実行中の外部編集は現セッションに反映されない
- **読み込み方向**: `claude --resume <session-id>` 時に JSONL からコンテキストが再構築され、**外部編集・複製が無検証でそのまま反映される**（実験: 「りんご」を sed で「みかん」に置換 → resume 後のモデルは「みかん」を合言葉として回答。エントリ行削除でも resume はエラーにならなかった）
- 構造: 各エントリは `uuid`/`parentUuid` の連結リスト。`tool_use`/`tool_result` のペアリング制約がある

この性質は死蔵アイデア（後述）の根拠であると同時に、フェーズ3（トランスクリプトアーカイブ）の「アーカイブ = resume 可能なスナップショット」という価値の根拠になる。

### ループが閉じない問題（死蔵判断の決め手）

セッションの死を越えるループ（世代交代・手術 + resume）には、定義上セッションの外に発火装置が要る:

- ScheduleWakeup（/loop の心臓）・CronCreate はいずれも session-only で、セッション終了とともに消える（CronCreate は仕様に明記）
- RemoteTrigger / schedule（クラウドルーチン）は永続するが実行環境がクラウドであり、ローカルの JSONL に触れない
- 残る足場は OS レベル（launchd / systemd timer の watchdog、遺言プロセス）だが、ダウンストリーム配布物にプラットフォーム依存が入り、セットアップ・保守コストがペインに見合わない

## 方針（オーナー決定 2026-07-06）

- **主軸**: compaction が起きるまで作業を止めない教義 ＋ 「ファイル差分と compaction 後コンテキストだけで復帰しやすいタスク」をどんどん進めるタスク運び（フェーズ2）
- **能動コンパクション系（手術 + resume・世代交代）は死蔵**: アイデアと実証結果を本 Plan 末尾に保存し、実装しない
- **副産物を採用**: PreCompact フックによるトランスクリプトアーカイブ（コンテキスト保全 ＋ resume 可能スナップショット）は面白く、コストも小さいので実装する（フェーズ3）

## 変更内容（フェーズ）

### フェーズ1: auto-compact 発動点の実測（軽量）

- **対象**: 調査のみ（成果物は `addf-Behavior.toml` へのコメント追記と本 Plan への追記）
- auto-compact が実際に発動したセッションのトランスクリプトから発動時トークン数を実測し、グレーゾーン（context-reminder 閾値 180k 〜発動点）の幅を定量化する
- 可能なら 1M variant セッションの実効劣化目安も観測し、`[context-reminder.effective-context]` の Fable 系の値を埋める（Plan 0023 の残課題の回収）
- 停止事例の解剖は行わない（ペインの核心はオーナー確定済みのため省略）

### フェーズ2: 「満杯時の出口」教義 — 止まらないこと ＋ compaction 耐性のタスク運び

- **対象**: `.claude/addfTools/context-reminder.py` / `.claude/commands/addf-dev.md` / `.claude/templates/ProgressTemplate.md`・`ProgressTemplate.addf.md`（同期ペア lint 対象）
- context-reminder の注入文言に「記録が尽きたあと」の行動指針を追加する:
  - 「記録が済んでいるなら、そのまま作業を続行してよい。compaction を起こすのは harness の仕事であり、復帰フックと日記が受け止める準備は整っている。エージェントの仕事は**止まらないこと**である」
- addf-dev.md のステップ5（ループ継続）に「コンテキスト満杯時の出口」を追記する:
  - コンテキスト満杯を理由にループを止めない・タスク着手を控えない
  - 残量が少ないときは**復帰容易性の高いタスクを優先する**: 進捗がファイル差分（コミット・Progress.md チェックリスト・日記）に現れるタスク、サブタスクの刻みが小さいタスク。compaction を跨いでも「ファイル差分 ＋ 圧縮済みコンテキスト」だけで次の代が続きから入れる
  - 逆に、未コミットの大きな途中状態を長時間抱えるタスク（one-shot 級）には残量少時に着手しない
  - 進捗の外部化（こまめなコミット・チェックリスト更新・日記）を通常より密に刻む
- ProgressTemplate の運用ルール 3.5 直後に同旨を追加する（テンプレート同期 lint のペア対象確認を忘れない）
- 文言は Plan 0023 の教訓（根拠なき状態断言が早期切り上げを誘発する）を踏襲し、観測事実＋行動指針＋安心文の3点セットを守る

### フェーズ3: PreCompact トランスクリプトアーカイブフック

- **対象**: `.claude/hooks/pre-compact-archive.sh`（新設）/ `.claude/settings.json`（PreCompact 配線）/ `.claude/addf-Behavior.toml` / `docs/knowhow/ADDF/`（復元手順）
- PreCompact フックで、compaction によって失われる直前の生トランスクリプトをアーカイブする:
  - hook stdin の JSON から `transcript_path`・`session_id`・`trigger`（manual/auto）を取得し、アーカイブ先へ `<日時>-<trigger>-<session-id>.jsonl` としてコピーする
  - アーカイブ先の既定はリポジトリ外（`~/.claude/addf-transcript-archive/<プロジェクトスラグ>/`）とし、`addf-Behavior.toml` の `[transcript-archive]` で変更・無効化できるようにする（サイズが数 MB 級になるためリポジトリ内は既定にしない）
  - 世代数上限（既定 N 世代、超過分は古いものから削除）を Behavior.toml で設定可能にする
  - 失敗時は静かに `exit 0`（既存フックの作法。`set -e` 非使用・`CLAUDE_PROJECT_DIR` フォールバック等は `claude-code-hooks.md` の知見に従う）
- **アーカイブの二重の価値**:
  - (a) コンテキスト保全: compaction で要約に潰される前の生ログのタイムマシン（会話ログアーカイブ運用とも親和）
  - (b) **resume 可能スナップショット**: アーカイブを新しい session-id（有効な UUID）にリネームして `~/.claude/projects/<slug>/` に置けば、`claude --resume <新uuid>` で compaction 直前の状態に戻れる（上記実証より。resume は複製を無検証で受け入れる）
- 復元手順（リネーム・配置・resume・注意点）を knowhow 記事 `docs/knowhow/ADDF/transcript-archive-restore.md` として記録する
- lint・配布の整備: `lint-hooks-wiring.py` の検出確認、addf-init コピーリストへの追加（lint ペア5）、`.gitignore` は対象外（アーカイブ先がリポジトリ外のため不要なことを確認）
- 検証事項: compaction 時にトランスクリプトファイルが同一 ID 継続か新 ID 切替かは環境（CLI / VSCode 拡張）で挙動が違う可能性がある（2026-07-06 の観察では VSCode 拡張で新 ID 切替）。PreCompact 発火時点の `transcript_path` を無条件でコピーする設計なら どちらでも保全できるはずだが、フックテストで両経路を確認する

## 死蔵アイデア（実装しない・記録として保存）

> 2026-07-06 オーナー決定: アイデアは良いがループが閉じきっていない（外部足場が必須）ため実装しない。着手のトリガー: unattended 常時自走の需要が高まり、OS レベルの足場（launchd/systemd）のセットアップコストを払う価値が出たとき。

- **トランスクリプト手術 + resume（能動的・選択的 compaction）**: セッション終了 → JSONL バックアップ → 古い `tool_result` の content をプレースホルダに置換して間引き → 同一 session-id で resume。auto-compact と違い何を残すか選べ、残した部分は無劣化。原理成立は実証済み（上記実験）。安全な手術は「エントリ削除」より「content 置換」（`tool_use`/`tool_result` ペアと uuid チェーンを保つ。Anthropic API のサーバー側 context editing と同じ発想）
- **世代交代（generational handoff）**: 記録完了後に次世代セッションを起動して正常終了する。実装案: (A) セッション内 Bash から `claude -p` 起動 / (B) 外部ループスクリプト `addf-loop.sh` によるセッション連鎖 / (C) 手術 + resume の連鎖
- **ループの閉じ方3案の評価**: (1) 遺言プロセス（nohup で死後発火）— エージェント主導だが1回切れたら静かに死ぬ / (2) launchd・systemd のステートレス watchdog — 自己修復的で堅いがプラットフォーム依存が配布物に入る / (3) ハイブリッド（遺言＋watchdog 保険）
- **燃料投下（意図的なコンテキスト消費で auto-compact を誘発）**: 200k セッションではフェーズ2の教義で足り、1M セッションでは数十万トークンを捨てることになる。どちらも割に合わず不採用
- **実行中セッションの JSONL 直接編集**: 実行中は読み直されないため効果がない（実証済み）。効くのは resume 経由のみ

## 影響範囲

- 同期ペア lint 対象: ProgressTemplate.addf.md ⇔ Progress.md・ProgressTemplate.md(フェーズ2)。変更後 `/addf-lint` セクション6を実行する
- context-reminder.py の文言変更はテスト `test-context-reminder.sh` の assertion 更新を伴う
- フェーズ3の新フックはダウンストリーム配布対象（addf-init コピーリスト・hooks 配線 lint）
- addf-dev.md の変更は `/addf-dev` の全ダウンストリーム利用者に波及する

## テスト方針

- フェーズ1: 実測値の根拠 transcript パスを本 Plan に記録する
- フェーズ2: `test-context-reminder.sh` に新文言の存在・安心文の残存を assert 追加。ドリフト注入 TDD に従い、旧文言に戻した状態でテストが落ちることを確認する
- フェーズ3: フックテストを `.claude/tests/hooks/` に追加（hook JSON を stdin 投入してアーカイブ生成・世代数上限・無効化設定・失敗時 exit 0 を検証）。復元手順は実セッションで1回実地確認する <!-- human-judgment -->
- 最終検証: /loop 自走でコンテキスト枯渇まで到達させ、停止せずに auto-compact 越えして次サイクルへ続くことを観測する <!-- human-judgment -->

## 破壊的変更の許容範囲

なし（フェーズ3のアーカイブは Behavior.toml で無効化可能。既定の会話挙動は変わらない）

## 要オーナー確認

- フェーズ3のアーカイブ先の既定（`~/.claude/addf-transcript-archive/` 案）と世代数上限の既定値
- （解決済み 2026-07-06）能動コンパクション系の採否 → 死蔵と決定

## 完了条件

- [ ] フェーズ1: auto-compact 発動点の実測値が `addf-Behavior.toml` コメントと本 Plan に記録されている
- [ ] フェーズ2: context-reminder.py・addf-dev.md・ProgressTemplate 系に「満杯時の出口」（止まらない教義＋compaction 耐性のタスク運び）が記載され、`bash .claude/tests/run-all.sh` と `/addf-lint`（同期ペア）が全パスする
- [ ] フェーズ3: PreCompact アーカイブフックが配線され、フックテストがパスし、復元手順の knowhow が存在する
- [ ] 実地検証: /loop 自走がコンテキスト枯渇を跨いで継続することを1回以上観測する <!-- human-judgment -->

## AI 実装時間見積もり

フェーズ1〜3 まとめて1セッション（フェーズ1は調査、2は文言と教義、3はフック1本＋テスト＋knowhow）。
