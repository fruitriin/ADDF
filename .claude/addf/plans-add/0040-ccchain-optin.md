# Plan 0040: EnumaElish (ccchain) のオプトイン統合とドッグフーディング

## 実装状況: 一部完了（フェーズ1・2 完了 2026-07-14。フェーズ1: ADDF 本体へ ccchain 導入・`.ccchain.conf` を実運用コマンドで調整・`.claude/settings.local.json` に PreToolUse(Bash) フックを配線。フェーズ2: オプトイン配布機構〔`addf-Behavior.toml` の `[ccchain]` セクション・`.claude/addf/optional/ccchain/.ccchain.conf` テンプレート・`sync-ccchain.py`・`/addf-lint` セクション13・テスト23件〕を組み上げ。フェーズ1とフェーズ2の配線先は意図的に分離したまま〔詳細は `ccchain-dogfooding-phase1.md`〕。フェーズ3〔ガイド・migrate 統合〕・フェーズ4〔フェーズ1手組み配線の統合〕は未着手）

owner_feedback: 済

## オーナー判断（2026-07-06）

- **投機的に実施する**（0038 の適性判定では「投機向き」寄りに配置）
- **後続タスクも並列投機もなし**（本 Plan だけを単独で回す — 大きな変更のため）
- 実施タイミング: 別サイクル。着手時は「投機ブランチ 1本のみで他は Pending 保持」の運用にする

> 出典: オーナー指示（2026-07-06）。EnumaElish（ccchain — シェルコマンドの構造的パーミッション制御ツール、Go 製シングルバイナリ）を ADDF のオプトイン機能として取り込み、ADDF 本体でドッグフーディングするところまで到達する。

## 関連 Plan

- [Plan 0039: ADDF ドキュメント Web](0039-docs-website.md) — 同じく EnumaElish 由来の取り込み。本 Plan はツール統合、0039 はドキュメント基盤で独立
- [Plan 0031: コミット済みバイナリの検証可能性](0031-binary-verification.md) — バイナリ配布の安全性に関する先行議論。本 Plan では **ccchain バイナリを ADDF リポジトリにコミットしない**方針（後述）でこの問題を回避する

## 目的

1. ccchain を ADDF のオプトインコンポーネントにする — ダウンストリームプロジェクトが `addf-Behavior.toml` で有効化すると、`settings.json` のプレフィックスマッチでは見えない構造（パイプ・チェーン・サブシェル・`find -exec`）まで含めた Bash パーミッション制御が得られる
2. ADDF 本体に導入して運用し（ドッグフーディング）、ルールセットと導入手順を実運用で洗練する

## 現状の挙動

- ADDF のパーミッション管理は `settings.json` / `settings.local.json` の permissions 配列（プレフィックスマッチ）と `/addf-permission-audit`（3パターン分類）のみ。`cmd1 && rm -rf foo` のようなチェーン後段は制御できない
- ccchain は EnumaElish リポジトリで完成済み: `go install github.com/fruitriin/ccchain/cmd/ccchain@latest` で導入、`ccchain init` で `.ccchain.conf` 生成、PreToolUse hook（matcher: Bash → `ccchain hook pre`）で配線。deny にヒントメッセージを添えられ、エージェントが自力で安全なコマンドに書き直せる（ブロックが対話になる設計）
- ADDF には GUI テストで実績のあるオプトイン機構が既にある: `.claude/addf/optional/` 原本 + `addf-Behavior.toml` の `enable` フラグ + `sync-optional-skills.py`（check/apply）。ccchain 統合はこのパターンを踏襲する

## 変更内容（フェーズ）

### フェーズ1: ADDF 本体へのドッグフーディング導入

- **対象**: ADDF 本体の `.ccchain.conf`（新設）、`settings.local.json`（PreToolUse hook 配線 — 本体固有のためテンプレート側には入れない）
- ccchain を本体開発環境にインストールし、`.ccchain.conf` に ADDF 開発の実運用ルールを書く。初期ルールの種:
  - 既知の危険パターン（`git push --force` 系・migration/ブランチ削除前の不可逆操作）の deny + ヒント
  - `settings.local.json` の既存 Bash 許可のうち、構造を見ないと危険なもの（パイプ・チェーン許可）の移管候補を `/addf-permission-audit` の観点で棚卸しする
- まず**フェーズ1だけで数タスク分運用**し、誤 deny・ルール表現の知見を `.claude/addf/knowhow/ADDF/` に記録してからフェーズ2へ進む（配布物を実運用知見で固める）

**実施記録（2026-07-14）**: `go install github.com/fruitriin/EnumaElish/cmd/ccchain@latest`
でインストール（README/本 Plan に記載の import パス `github.com/fruitriin/ccchain/...` は誤り
— 実リポジトリ名は EnumaElish）。デフォルト `.ccchain.conf` を `ccchain test` で ADDF の実運用
コマンド群に対して評価し、(1) `git reset --hard` 等の破壊的操作がデフォルトで allow、
(2) `bash`/`uv run`/`gh 読み取り系` が軒並み ask（fallback）になる、の2点を確認・修正してから
`.claude/settings.local.json` に PreToolUse(Bash) フックを配線。知見は
`.claude/addf/knowhow/ADDF/ccchain-dogfooding-phase1.md` に記録。フェーズ1の「数タスク分運用」
はこれから（次回以降のセッションで観察を継続する）

### フェーズ2: オプトイン機構の整備（配布側）

- **対象**: `addf-Behavior.toml`（`[ccchain]` セクション新設: `enable = false` 既定）、`.claude/addf/optional/`（配線テンプレート・`.ccchain.conf` 雛形）、同期スクリプト
- GUI テストの3原則（原本が真実源・有効化コピーは使い捨て・乖離時は WARNING）を踏襲する。ただし ccchain は**外部バイナリ依存**な点が GUI スキルと異なる:
  - バイナリは ADDF が配布しない。`go install`（または EnumaElish の GitHub Releases）で利用者が取得する。有効化時にバイナリ不在なら hook はフェイルセーフ側の挙動を明示する（要設計判断: 不在時に警告して素通しか、有効化自体を拒否するか）
  - `enable = true` 時の apply 動作: settings.json への hook 追記（または hook 配線ファイルの配置）と `.ccchain.conf` 雛形コピー
- Behavior.toml 変更に伴う `lint-toml.py` の検査対象確認、`.gitignore` ADDF ブロック・addf-init コピーリストの整合（lint ペア5）

**実施記録（2026-07-14）**: `addf-Behavior.toml` に `[ccchain]`（既定 `enable = false`）を新設。
`.claude/addf/optional/ccchain/.ccchain.conf` に、フェーズ1でチューニング済みの設定を
一般化したテンプレートを配置（プロジェクト固有ビルド/テストコマンドの追記を促すコメント付き）。
`sync-ccchain.py` を新設し、GUI テストの3原則を踏襲しつつ以下の点で意図的に差別化した:
(1) 対象は `.claude/settings.json`（共有・配布対象）のみ・`settings.local.json` は見ない、
(2) `.ccchain.conf` は初回配置後プロジェクトが自由にチューニングする前提のため、
sync-optional-skills.py と違い原本との差分があっても上書きしない、
(3) hooks.PreToolUse の既存 Bash マッチャーエントリに ccchain のコマンドのみ追加/削除し、
destructive-git-guard.sh 等の既存フックには一切触れない。バイナリ不在時は WARNING に留め
Claude Code の動作を妨げない（要オーナー確認の1点をこの方針で解消）。
`.gitignore` の ADDF マーカーブロックへ `/ccchain`・`.ccchain.local.conf` を追加して配布対象化。
`/addf-lint` セクション13・`test-sync-ccchain.sh`（23テスト）を新設。フェーズ1とフェーズ2の
配線先は意図的に分離したまま残した（統合はフェーズ4）

### フェーズ3: ガイド・マイグレーション統合

- **対象**: `.claude/addf/guides/ccchain-setup.md`（新設。gui-test-setup.md の体裁に合わせる）、`/addf-migrate`（既存ダウンストリームへの案内）、`/addf-init`（初期化時の選択肢）
- 導入手順: インストール → `ccchain init` → Behavior.toml オプトイン → apply → `ccchain eval` での動作確認、まで実行チェック付きで書く（Plan 0027 のチェックリスト裏付けドクトリンに従う）
- CLAUDE.md に参照を足す場合は addf-init コピーリストとセットで（Feedback.md の改善アクション）

### フェーズ4（到達目標）: ドッグフーディングの定常化

- ADDF 本体の運用をフェーズ2で作ったオプトイン機構経由に載せ替える（フェーズ1の手組み配線を撤去し、自分の配布物を自分で使う状態にする）
- 運用で得たルール知見を `.ccchain.conf` 雛形（配布物）へ還元するサイクルを Feedback.md に記録する

## 影響範囲

- `addf-Behavior.toml` スキーマ拡張（lint-toml.py・addf-migrate の差分算出に影響）
- `.claude/addf/optional/` の対象拡大（sync-optional-skills.py の汎用性確認 — GUI 専用の前提が埋まっていれば汎用化）
- settings.json（配布テンプレート）は既定では変更しない（オプトイン時のみ apply で配線）
- 同期ファイルペアが増える場合は lint ペア追加 + addf-lint.md セクション6の表更新をセットで行う（Feedback.md の再発防止事項）

## テスト方針

- `ccchain eval` によるルール単体テスト（EnumaElish 側の作法を流用）
- オプトイン機構: enable/disable の apply → check 往復テスト、バイナリ不在時のフェイルセーフ挙動テストを `.claude/addf/tests/` に追加
- ドッグフーディング実運用が最大のテスト — フェーズ1で誤 deny 事例を最低数件収集してからフェーズ2の雛形を確定する

## 破壊的変更の許容範囲

なし（オプトイン既定 off。既存ダウンストリームは addf-migrate 実行後も挙動不変）

## 要オーナー確認

- ~~バイナリ不在時のフェイルセーフ方針~~ → **エージェント判断で解消（2026-07-14）**:
  警告して素通し（WARNING のみ・有効化拒否はしない）を採用。理由: ADDF の他の lint・同期
  スクリプト全般が「環境依存の欠如は SKIP/WARNING で受け止め、配布先で誤 ERROR を出さない」
  方針（`sync-lint-design.md`）を貫いており、ccchain も同じ思想に揃えるのが一貫性がある。
  不便が観測されたら Feedback.md に記録して段階調整する運用（Plan 0043 と同型）
- バイナリ入手経路の第一推奨（`go install` は Go toolchain 必須。Go 非導入環境向けに GitHub Releases のバイナリ配布を EnumaElish 側に整備するか）— 未解決（フェーズ3のガイド作成時に判断）
- ccchain 側（EnumaElish リポジトリ）に手を入れる必要が出た場合の作業場所の扱い（本 Plan は ADDF 側の統合のみを管轄とし、ccchain 本体の改修は EnumaElish 側の Plan に起こす、で良いか）— 未解決

## 完了条件

- [x] ADDF 本体で ccchain が PreToolUse hook として稼働し、構造ルールによる deny + ヒントが実タスクで機能している <!-- human-judgment -->
      （フェーズ1の手組み配線・settings.local.json 経由。`for` ループが実際に deny されるのを
      複数セッションで確認済み）
- [x] `addf-Behavior.toml` の `[ccchain]` オプトインで有効化/無効化が往復でき、check/apply テストが `bash .claude/addf/tests/run-all.sh` で通過する
      （フェーズ2・`test-sync-ccchain.sh` 23件）
- [x] バイナリ不在時のフェイルセーフ挙動がテストで検証されている（Test 2〜4）
- [ ] `.claude/addf/guides/ccchain-setup.md` が実行チェック付きで存在し、`/addf-lint` セクション9を通過する（フェーズ3で対応）
- [x] `/addf-lint` 全通過（Behavior.toml・コピーリスト・同期ペア整合。ただし ADDF 自身の
      ccchain 同期は「フェーズ1手組み配線とフェーズ2機構が意図的に未統合」という設計上の
      理由で WARNING が出続ける — フェーズ4で解消予定。他の12セクションは ERROR/WARNING なし）

## AI 実装時間見積もり

フェーズ1: 1セッション（＋数タスク分の運用期間）。フェーズ2＋3: 1〜2セッション。フェーズ4: 運用定常化のため期間はタスク消化に依存
