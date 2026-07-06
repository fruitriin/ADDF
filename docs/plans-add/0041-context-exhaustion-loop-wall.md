# Plan 0041: コンテキスト枯渇によるループ停止の壁の突破

## 実装状況: 未着手

> 出典: オーナー指示（2026-07-06）—「コンテキスト残量が残り少ないときに記録作業に回れるのはいいとして、いよいよ記載することがなくなったときに能動的に compact できなくてループが止まっちゃう壁を突破する計画を考えてほしい」
> 同日のオーナー対話で方針確定: ペインの核心を特定し、能動コンパクション系のアイデアは死蔵（knowhow に記録保存）、教義＋タスク運びを主軸に。副産物の PreCompact トランスクリプトアーカイブは Plan 0042 に切り出し。

## 関連 Plan

- [Plan 0042: PreCompact トランスクリプトアーカイブ](0042-precompact-transcript-archive.md) — 本 Plan の調査から生まれた副産物の切り出し先
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

- エージェントから compaction を能動的に起こす手段は存在しない（2026-07 時点。詳細と実験結果は `docs/knowhow/ADDF/context-and-transcript.md`）
- auto-compact は harness が「コンテキスト上限接近時」に自動発動する。context-reminder 閾値（180k）〜auto-compact 発動点の間の**グレーゾーン**で、記録を書き尽くしたエージェントは「新規着手は危険・compact 手段はない」の板挟みになり、次サイクルを予約せずループを止める（自主停止）
- 検討した能動コンパクション系の代替案（トランスクリプト手術 + resume・世代交代・ループの閉じ方3案）は、原理成立を実証したうえで「ループが閉じきらない（OS レベルの外部足場が必須）」ため死蔵と決定した。アイデア・実証結果・着手トリガーは `docs/knowhow/ADDF/context-and-transcript.md` に保存

## 方針（オーナー決定 2026-07-06）

- **主軸**: compaction が起きるまで作業を止めない教義 ＋ 「ファイル差分と compaction 後コンテキストだけで復帰しやすいタスク」をどんどん進めるタスク運び（フェーズ2）
- 能動コンパクション系のアイデアは実装せず knowhow に死蔵
- 副産物の PreCompact トランスクリプトアーカイブは [Plan 0042](0042-precompact-transcript-archive.md) として独立に実施

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

## 影響範囲

- 同期ペア lint 対象: ProgressTemplate.addf.md ⇔ Progress.md・ProgressTemplate.md（フェーズ2）。変更後 `/addf-lint` セクション6を実行する
- context-reminder.py の文言変更はテスト `test-context-reminder.sh` の assertion 更新を伴う
- addf-dev.md の変更は `/addf-dev` の全ダウンストリーム利用者に波及する

## テスト方針

- フェーズ1: 実測値の根拠 transcript パスを本 Plan に記録する
- フェーズ2: `test-context-reminder.sh` に新文言の存在・安心文の残存を assert 追加。ドリフト注入 TDD に従い、旧文言に戻した状態でテストが落ちることを確認する
- 最終検証: /loop 自走でコンテキスト枯渇まで到達させ、停止せずに auto-compact 越えして次サイクルへ続くことを観測する <!-- human-judgment -->

## 破壊的変更の許容範囲

なし

## 要オーナー確認

- （解決済み 2026-07-06）能動コンパクション系の採否 → 死蔵と決定。PreCompact アーカイブ → Plan 0042 に切り出し

## 完了条件

- [ ] フェーズ1: auto-compact 発動点の実測値が `addf-Behavior.toml` コメントと本 Plan に記録されている
- [ ] フェーズ2: context-reminder.py・addf-dev.md・ProgressTemplate 系に「満杯時の出口」（止まらない教義＋compaction 耐性のタスク運び）が記載され、`bash .claude/tests/run-all.sh` と `/addf-lint`（同期ペア）が全パスする
- [ ] 実地検証: /loop 自走がコンテキスト枯渇を跨いで継続することを1回以上観測する <!-- human-judgment -->

## AI 実装時間見積もり

フェーズ1〜2 で1セッション以内。
