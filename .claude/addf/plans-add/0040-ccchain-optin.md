# Plan 0040: EnumaElish (ccchain) のオプトイン統合とドッグフーディング

## 実装状況: 一部完了（フェーズ1 完了 2026-07-14。ADDF 本体へ ccchain 導入・`.ccchain.conf` を
実運用コマンドで調整・`.claude/settings.local.json` に PreToolUse(Bash) フックを配線。
フェーズ2〔オプトイン配布機構〕は「数タスク分運用してから」の設計のため未着手）

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

- バイナリ入手経路の第一推奨（`go install` は Go toolchain 必須。Go 非導入環境向けに GitHub Releases のバイナリ配布を EnumaElish 側に整備するか）
- バイナリ不在時のフェイルセーフ方針(警告して素通し / 有効化拒否)
- ccchain 側（EnumaElish リポジトリ）に手を入れる必要が出た場合の作業場所の扱い（本 Plan は ADDF 側の統合のみを管轄とし、ccchain 本体の改修は EnumaElish 側の Plan に起こす、で良いか）

## 完了条件

- [ ] ADDF 本体で ccchain が PreToolUse hook として稼働し、構造ルールによる deny + ヒントが実タスクで機能している <!-- human-judgment -->
- [ ] `addf-Behavior.toml` の `[ccchain]` オプトインで有効化/無効化が往復でき、check/apply テストが `bash .claude/addf/tests/run-all.sh` で通過する
- [ ] バイナリ不在時のフェイルセーフ挙動がテストで検証されている
- [ ] `.claude/addf/guides/ccchain-setup.md` が実行チェック付きで存在し、`/addf-lint` セクション9を通過する
- [ ] `/addf-lint` 全通過（Behavior.toml・コピーリスト・同期ペア整合）

## AI 実装時間見積もり

フェーズ1: 1セッション（＋数タスク分の運用期間）。フェーズ2＋3: 1〜2セッション。フェーズ4: 運用定常化のため期間はタスク消化に依存
