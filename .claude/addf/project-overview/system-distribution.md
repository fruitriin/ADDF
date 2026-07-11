# 配布・導入 — Framework distribution, installation, and documentation

> 概念単位の記録。実装がスキル/エージェント/フック/ファイルのどれであっても、
> 「ADDF の導入・更新・リリース・ドキュメンテーション」に関わるものをまとめている。

## 構成要素

| 種別 | 名前 | 役割 |
|---|---|---|
| スキル | addf-init | 新規/既存プロジェクトへの ADDF 導入（外部起動・テンプレート・既存プロジェクトの3経路）＋「部分導入からの正規化」＋ `check` 構造検証 |
| スキル | addf-migrate | addf-lock.json の ref（タグ）基準でフレームワークを最新版にアップグレード（6フェーズ＋Phase 2.5 ディレクトリ大移行ワンショット）。lock 不在＋ADDF ファイル検出時は部分導入正規化へ誘導 |
| スキル | addf-release | リリースワークフロー（upstream/downstream 自動切替） |
| スキル | addf-overview | エコシステム概要ドキュメントの生成（本ドキュメント。full/patch モード + .lock） |
| ツール | .claude/addf/addfTools/sync-optional-skills.py | オプトインスキル機構の同期（check / apply）。.claude/addf/optional/ の原本と有効化コピーを [gui-test] enable と整合させる |
| ツール | .claude/addf/addfTools/paths.toml | **旧→新パスマップの単一ソース**（Plan 0037）。migrate-paths / lint-residual-paths / テストが全てこれを参照する。[meta].new_root（移行済み判定アンカー）と backup_ref を定義 |
| ツール | .claude/addf/addfTools/migrate-paths.py | ディレクトリ大移行の3モード: check（実在・衝突・旧参照の全数提示＋射程外候補プリフライトスキャン）/ apply（backup ref 作成→git mv 一括。コミットは呼び出し側の責務）/ rewrite（全 git 追跡テキストの旧パス参照を新パスへ書き換え） |
| ツール | .claude/addf/addfTools/lint-residual-paths.py | 移行の**完了ゲート**。旧パス残存を ERROR 検査（ゼロになるまで完了扱いしない）。移行後は docs/ への逆流を WARNING で恒久検査。移行前リポジトリは SKIP 明示 |
| ツール | .claude/addf/addfTools/verify-checksums.sh + checksums.sha256 | 配布バイナリ（Swift ツール）の SHA-256 照合＋allowlist ガード（Plan 0031。→ system-visual-testing） |
| ディレクトリ | .claude/addf/optional/ | オプトインスキル・エージェントの原本置き場（現在は GUI テスト一式: 3スキル+1エージェント） |
| ファイル | .claude/addf/lock.json | バージョン追跡（現在 v0.6.1）。`version` / `ref` / `updated_at` / `repository`。プロジェクト種別の明示シグナルの一部。旧位置 `.claude/addf-lock.json` から v0.6.0 で移動 <!-- residual-path: allow --> |
| ファイル | .claude/addf/CHANGELOG.md | フレームワーク変更履歴。migrate 時に該当バージョン間のエントリを表示（2026-07-11 時点で Plan 0053 が進行中の課題として Plan 0030/0031/0032/0035/0036/0038/0039/0041/0049/0051/0052 のエントリ記載漏れを検出・回収作業中） |
| ファイル | .claude/addf/Release.addf.md | ADDF 本体（upstream）のリリース手順定義。プレリリースチェック5が overview 鮮度を検査し、patch で通した場合の full 負債はリリース後タスクとして TODO に積む（full のトリガーはリリースではなく構造変更） |
| ファイル | CONTRIBUTING.md | コントリビューションモデル（計画駆動レビュー・きっかけの記載。英語版 CONTRIBUTING.en.md あり） |
| ファイル | .gitignore の ADDF マーカーブロック | 実行時生成ファイルの除外定義（addf-init がブロックごとコピー — 列挙を持たない単一ソース化） |
| テンプレート | .claude/addf/templates/Release.md | リリース手順テンプレート |
| ディレクトリ | .claude/addf/guides/ | セットアップ・運用ガイド群（10本） |
| ディレクトリ | docs/（VitePress サイト） | `.claude/addf/guides/` を単一ソースとする公開ドキュメントサイトの骨格（Plan 0039 フェーズ2）。`scripts/sync-docs.mjs` が guides/ の全 Markdown を `docs/guide/`（生成物・.gitignore 対象）へコピーし、相対リンクをサイト内リンクまたは GitHub blob/raw URL に書き換える。`docs/.vitepress/config.mts` がナビ・サイドライン（はじめに/スキル・エージェント/運用/環境別セットアップの4グループ）を定義。`package.json` の `docs:sync` / `docs:dev` / `docs:build` / `docs:preview` から実行。GitHub Pages への実公開（フェーズ3）はオーナー操作待ち |

### .claude/addf/guides/ 一覧

| ファイル | 内容 |
|---|---|
| setup.md | ADDF 導入ガイド |
| development-process.md | 開発プロセスガイド（代替わり日記の語彙の意図もここ。lint ペア4で CLAUDE.md と同期検査） |
| skills.md | スキル一覧・使い方 |
| agents.md | エージェント一覧・使い方 |
| gui-test-setup.md | GUI テストセットアップ（オプトイン有効化手順を含む） |
| codex-setup.md | Codex 環境セットアップ |
| migration.md | マイグレーションガイド |
| pr-format.md | PR 本文規約の単一ソース（Plan 0035。通常 PR・投機昇格 PR が参照） |
| model-allocation.md | モデル配分ポリシーガイド（Plan 0049）。役割（メインループ運転手・実装サブエージェント・レビュー・ドキュメント・Plan 起草）別のモデル選定の考え方とエージェント定義 `model:` frontmatter / `/model` / `Agent` ツール呼び出しの使い分けを解説。CLAUDE.repo.example.md の「モデル配分ポリシー」節から参照される |
| speculative-development.md | 投機開発の概観（2層モデル・オプトイン・clean・昇格・投機適性・one-shot 定義の単一ソース。手順の正はスキル本文 — → system-speculation） |

## 設計思想

ADDF は「配布されるフレームワーク」であり、導入→運用→更新のライフサイクルを持つ。リポジトリは `fruitriin/ADDF`（Plan 0025 でリネーム）。

### 占有名前空間 `.claude/addf/` — Plan 0037（v0.6.0 の破壊的変更）

ADDF 管理ファイルは `.claude/addf/` 占有名前空間に集約され、**docs/ は明け渡された**（plans / plans-add / knowhow / guides / project-overview が `.claude/addf/` 配下へ移動。ダウンストリームの docs/ 直下の独自コンテンツには触れない — 「存在≠所有」原則により ADDF 管理サブディレクトリ単位でのみ移動する）。`.claude` 直下の ADDF ファイル群（Progress / Feedback / Questions / Dashboard / Behavior.toml / templates / tests / addfTools 等）も同名前空間へ移動した。`tools` は一般名でダウンストリーム独自ディレクトリと検索衝突するため **addfTools の名称は維持**（.claude/addf/addfTools/）。

移行機構の設計:
- **paths.toml が旧→新マップの単一ソース**。migrate-paths.py・lint-residual-paths.py・テストの全てが参照し、将来の再配置はこのファイルの更新だけで各ツールが追従する（手書きリスト間ドリフトの構造的排除 — Plan 0022 問題の根治）
- **migrate-paths.py の3モード分離**: check は無変更のプリフライト（rewrite の射程外5類型 — バイナリ・行内マーカー除外行・除外ファイル・境界規則不一致等 — の候補も WARNING 列挙）。apply は backup ref（refs/backup/pre-0037-migration）作成後に git mv 一括実行し**コミットはしない**（git mv コミットと参照書き換えコミットを分離し revert 一発で戻せる原子性）。rewrite は apply コミット後にのみ動く（dirty・未 apply は拒否）
- **行単位の除外マーカー `residual-path: allow`**: 移行手順書等の正当な旧パス言及は行内マーカーで除外する。ファイル丸ごと除外はそのファイルが lint の永久盲点になるため原則しない
- **lint-residual-paths.py が完了ゲート**: 旧パス残存 ERROR がゼロになるまで移行を完了扱いしない。移行後は docs/ への ADDF ファイル再出現（逆流）を WARNING で恒久検査。走査対象・境界規則は migrate-paths.py と同期契約
- 知見は .claude/addf/knowhow/ADDF/map-driven-migration-tool.md に蓄積

**導入パス**:
1. **新規プロジェクト**: GitHub Template から `addf-init` で初期化
2. **既存プロジェクト**: `addf-init` を外部起動（URL 検証 → tmp クローン）。既存の CLAUDE.md / AGENTS.md を統合して `CLAUDE.repo.md` に退避し、干渉チェック（Phase 2.5）・導入前レビュー（Phase 2.7: hooks/権限/CLAUDE.md への影響を明示）を経て統合する
3. **部分導入からの正規化**（Plan 0034）: lock 不在のまま ADDF 由来ファイルの一部が存在するプロジェクト（手縫い導入・旧版の部分コピー）を正規状態に揃える。`addf-migrate` が検出して誘導する。**存在≠所有**の原則で2群に分けて扱う — `addf-` プレフィックス等で所有識別できるものは差分確認のうえ一括上書き承認、hooks / AGENTS.md / Behavior.toml は個別確認（AGENTS.md は ADDF ブートシーケンス見出しの有無で所有判定。Behavior.toml は enable 値を保持してマージ）。完了時に lock を生成する

**バージョン管理**:
- `addf-lock.json` は **ref（`vX.Y.Z` タグ名）を記録する**。旧形式（`commit` ハッシュ）はリリースプロセスの都合で実在しないハッシュになりうるため、`v<version>` タグに読み替える後方互換を addf-init / addf-migrate / addf-init check が持つ
- `addf-migrate` がロックファイルの ref と最新版の差分を算出し、対象ファイル（addf- プレフィックス・.claude 配下・guides・knowhow/ADDF/）だけを安全にアップグレード。プロジェクト固有ファイル（Progress/Feedback/.exp.md/CLAUDE.repo.md/TODO 等）はスキップ。`.claude/addf/optional/` に変更があれば `sync-optional-skills.py apply` を再実行し、旧配布の `*.addf.md` 残留も検出して削除提案する
- CLAUDE.md / CLAUDE.repo.md の分離設計により、マイグレーション時の衝突を最小化

**分離パターン（配布の前提）**: `.addf.md` サフィックス並置 / `ADDF/` サブディレクトリ隔離 / `addf-` プレフィックス識別の3パターン（.claude/addf/knowhow/ADDF/upstream-downstream-separation.md）。lint・テストは対象ファイル欠如を SKIP 扱いにしてダウンストリームでの誤 ERROR を防ぐ。**upstream/downstream の判定はファイルの存在ではなく明示シグナル（CLAUDE.repo.md の種別宣言＋addf-lock.json）で行い、配布から `*.addf.md` を除外する**（Plan 0033。「存在≠所有」— 配布物として物理存在しても所有の証明にならない）。

**オプトインスキル機構**（Plan 0029）: 全プロジェクトが使うとは限らない機能（現在は GUI テスト一式）は `.claude/addf/optional/` に原本を退避し、`addf-Behavior.toml` のフラグ＋ `sync-optional-skills.py apply` で有効化コピーを配置する。原本が真実源・コピーは使い捨て・改変コピーは触らず WARNING（.claude/addf/knowhow/ADDF/optional-skill-optin.md）。

**リリース**:
- `addf-release` が upstream（ADDF 本体）と downstream（利用プロジェクト）で手順を自動切替
- 責務分割: スキル=ルーター、設定ファイル（Release.addf.md）=手順定義、.exp.md=プロジェクト戦略（.claude/addf/knowhow/ADDF/release-skill-separation.md）
- バージョン履歴: v0.1.0（lock+migrate 基盤）→ v0.2.0（init/release・Codex 対応・guides 分離）→ v0.3.0（迷ったときの作法・日記・knowhow ライフサイクル・ペルソナレビュー・同期 lint・context-reminder）→ v0.4.0（チェックリスト裏付け lint・オプトインスキル機構・投機開発基盤・tomllib 環境ガード）→ v0.5.0（投機開発サイクル完成・投機運用ガイド）→ v0.6.0（ディレクトリ大集約・移行ツール・doc-review・plan-audit・CI 品質ゲート・止まらない教義。2026-07-06 リリース）→ v0.6.1（トランスクリプトアーカイブ・destructive-git-guard・addf-implementer とモデル配分ポリシー・VitePress ドキュメントサイト骨格・移行実行時耐障害性強化。2026-07-07 lock 更新）

### マイグレーション実行時耐障害性 — Plan 0052（GitHub Issue #26 実測回収）

ダウンストリームプロジェクト（wardrobe-test）での実際の `/addf-migrate` v0.5.0→v0.6.1 実行が4件のツール堅牢性ギャップを発見した。最も深刻だったのは `test-tools.sh` の `window-info` バイナリ呼び出しが、初回実行時の画面収録権限ダイアログ待ちで**無期限にハングする**問題（`timeout` ガードで解消）。他に guides/ 混在確認・.gitignore 旧位置パターン検知・Test15 の SKIP フォールバック追加を実装し、`.claude/addf/knowhow/ADDF/map-driven-migration-tool.md` に知見を追記した。3体レビュー（code-review Critical1・doc-review Warning3・contribution-agent Medium2）を反映済み。「マップ駆動移行ツール」の設計は Plan 0037 由来だが、実運用フィードバックによる耐障害性強化は継続的なテーマ。

## 主要フロー

```
導入:
  addf-init
  ├─ 外部起動 → URL 検証（https:// のみ）→ tmp クローン
  │   → 既存ファイルから自動推定 → 干渉チェック → 導入前レビュー
  │   → コピー & マージ（カテゴリ1: 無条件（optional/ 含む） / 2: マージ / 3: 生成）
  ├─ Template 経由 → lock 生成のみ（ファイルは同梱済み）
  ├─ 部分導入からの正規化 → 外部起動手順に合流し、ADDF 所有ファイルだけ
  │   最新版で上書き（安全一括 or 個別確認の2群） → lock 生成
  └─ check → 必須ファイル・@メンション解決・TODO⇔plans 整合・lock 妥当性・AGENTS.md の5項目検証

更新:
  addf-migrate
  ├─ Phase 1: lock 読み込み（旧形式 commit → v<version> タグに読み替え）・クリーン確認・URL 検証
  │           lock 不在＋ADDF ファイル検出 → 部分導入正規化を提案
  ├─ Phase 2: 最新版クローン
  ├─ Phase 2.5: ディレクトリ大移行（v0.6.0 ワンショット。構造差分で発動 —
  │           ターゲットが新構造 ∧ ローカル未移行。部分適用はセカンダリチェックで検出）
  │           道具導入（migrate-paths 一式を単独コミット）→ check → apply →
  │           git mv コミット → rewrite → 参照書き換えコミット → lint-residual-paths で
  │           完了ゲート。一発通し切り推奨・想定外は backup ref へ巻き戻し。
  │           旧版スキルで開始した場合は Phase 5 のスキル上書き後に再実行で発動
  ├─ Phase 3: ref（タグ）基準で差分算出（対象/対象外の区別。旧 *.addf.md 残留検出）
  ├─ Phase 4: 変更プレビュー + CHANGELOG 表示 → ユーザー確認
  ├─ Phase 5: 適用（settings.json ユニオンマージ、CLAUDE.md はテンプレート部分のみ更新、
  │           optional/ 変更時は sync-optional-skills.py apply）
  └─ Phase 6: lock 更新（ref = v<new-version>）・tmp 削除

リリース:
  addf-release
  ├─ upstream: Release.addf.md に従う（タグ vX.Y.Z 発行 → migrate の参照先になる）
  └─ downstream: .exp.md or 対話的に戦略構築

ドキュメント化:
  addf-overview
  ├─ full: 全スキャン → 概念システム探索 → .claude/addf/project-overview/ 再生成
  └─ patch: .lock からの diff → 影響システムのみ再生成
```

## 下流でのカスタマイズ

- `CLAUDE.repo.md` でプロジェクト種別（ADDF 開発 or ADDF 利用）を宣言 — addf-release / addf-permission-audit / lint の種別判定に使われる（明示シグナル）
- `.claude/addf/guides/` にプロジェクト固有のガイドを追加可能
- `addf-release` は downstream で初回実行時に対話的にリリース戦略を構築し、.exp.md に保存
- `addf-lock.json` の `repository` を差し替えれば fork した ADDF からのマイグレーションも可能（デフォルト URL と異なる場合は警告）
- オプトイン機能（GUI テスト等）は addf-Behavior.toml のフラグで各プロジェクトが選択する

## 関連するシステム

- **セッション管理**: CLAUDE.md, settings.json, hooks, Behavior.toml は配布対象でありセッション管理の構成要素でもある
- **品質ゲート**: addf-lint がフレームワーク整合性を検証（配布物の品質保証）。lint の SKIP 設計・addf-init コピーリストのカバレッジ検査（ペア5）・オプトイン同期検査（項目10）・残存参照検査（lint-residual-paths — 移行完了ゲート兼 docs/ 逆流検知）は配布安全性のための機構
- **視覚テスト**: オプトインスキル機構の現在唯一の適用対象が GUI テスト一式
- **投機開発**: speculate-*.py は addfTools として配布対象。[speculation] は Behavior.toml のオプトインフラグ
- **ノウハウ蓄積**: .claude/addf/knowhow/ADDF/ は配布・マイグレーション対象。プロジェクト固有 knowhow は対象外
- **全システム**: addf-overview が全システムを横断的にドキュメント化。VitePress ドキュメントサイト（docs/）は `.claude/addf/guides/` を単一ソースとするため、guides/ が扱う全システムの運用ガイドが公開ドキュメントとして間接的に配布される
- **計画駆動**: addf-implementer・DelegationRules.md は並列実装方針（worktree 隔離下の実装委譲）の一部として配布される（本体詳細 → system-planning）
