# ADDF Changelog

ADDF フレームワークの変更履歴。`/addf-migrate` 実行時に該当バージョン間のエントリを表示する。

## [0.6.0] - 2026-07-06

> **⚠️ このバージョンへの移行は、必ず最新版の addf-migrate.md（Phase 2.5 入り）で実行すること。**
> 旧版（v0.5.0 以前）の addf-migrate.md はローカル保存のまま実行されるため、ディレクトリ
> 大移行（Phase 2.5）を知らない。**旧版スキルで `/addf-migrate` を開始してしまった場合**:
> Phase 5 のスキル上書きで addf-migrate.md が新版になった後、**もう一度 `/addf-migrate` を
> 実行**すれば Phase 2.5 が発動する（1周目ではディレクトリ移行されない）。また、旧版の
> Phase 3/4 は新旧構造の差分を「削除」と誤認しうるが、**削除の物理実行はしないこと**。

### 破壊的変更 — ディレクトリ大集約（Plan 0037）

ADDF 管理ファイルの配置を全面変更した。`docs/` を明け渡し（ダウンストリームが GitHub Pages 等の
一般用途に使えるように）、ADDF 由来ファイルを `.claude/addf/` 名前空間に集約した。
旧→新の全対応は `.claude/addf/addfTools/paths.toml`（単一ソース — migrate の移動処理・
残存 lint・テストが全て参照する）が保持する。主な移動:

- `docs/plans` → `.claude/addf/plans`（同様に `plans-add` / `knowhow` / `guides` / <!-- residual-path: allow -->
  `project-overview`。docs/ 直下の ADDF 管理外ファイル — Pages コンテンツ等 — には
  一切触れない: 存在≠所有）
- `.claude/templates` → `.claude/addf/templates`（同様に `tests` / `optional` / `Progresses` / <!-- residual-path: allow -->
  `addfTools`）
- リネームを伴う移動（`.claude/addf/` 内は占有空間のため `addf-` プレフィックスを外す）:
  - `.claude/addf-Behavior.toml` → `.claude/addf/Behavior.toml` <!-- residual-path: allow -->
  - `.claude/addf-lock.json` → `.claude/addf/lock.json`（旧位置は `/addf-migrate` が <!-- residual-path: allow -->
    フォールバック検出する）
  - `.claude/ADDF-CHANGELOG.md` → `.claude/addf/CHANGELOG.md`（本ファイル） <!-- residual-path: allow -->
  - `.claude/ADDF-Release.addf.md` → `.claude/addf/Release.addf.md`（`.addf.md` サフィックスは <!-- residual-path: allow -->
    配布除外規則の判定パターンのため維持）
  - `.claude/Progress.md`・`Feedback.md`・`Questions.md`・`Questions.example.md`・ <!-- residual-path: allow -->
    `Dashboard.example.md`・`Dashboard.md`・`Worktrees.md` → `.claude/addf/` 直下へ
- 移動しないもの: `.claude/commands`・`agents`・`hooks`・`skills`・`settings*.json`
  （Claude Code が読み込み位置を規定 — 従来どおり `addf-` プレフィックスで分離）と、
  ルートのエントリポイント（`CLAUDE.md`・`TODO.md`・`AGENTS.md`・`CLAUDE.repo.md` 等）
- 旧パスへの symlink 等の後方互換スタブは置かない。残存参照は lint が即時 ERROR で知らせる
  （「静かに壊れる」より「うるさく直させる」）

### 移行ガイド

`/addf-migrate` を実行すると Phase 2.5（構造差分で発動 — 0.4.x 以前からの直行アップグレード
でも漏れない）が本手順を案内する。手動で行う場合の要約:

1. 作業ツリーを clean にする（dirty なら開始しない）
2. 最新版クローンから移行ツール3点（`migrate-paths.py`・`lint-residual-paths.py`・
   `paths.toml`）を旧位置 `.claude/addfTools/` へコピーしてコミットする <!-- residual-path: allow -->
   （移行前のプロジェクトには道具がまだ無い）
3. `uv run --python 3.11 .claude/addfTools/migrate-paths.py check` で移動計画・旧パス参照数・ <!-- residual-path: allow -->
   rewrite 射程外の候補を確認する（uv が無ければ python3（3.11+）で直接実行）
4. `uv run --python 3.11 .claude/addfTools/migrate-paths.py apply` → **git mv だけを <!-- residual-path: allow -->
   単独コミット**（backup ref `refs/backup/pre-0037-migration` が自動作成される）
5. **新位置**の `uv run --python 3.11 .claude/addf/addfTools/migrate-paths.py rewrite` →
   参照書き換えを別コミット（ツール自身も移動済みのため旧パスのコピペは不可）
6. `uv run --python 3.11 .claude/addf/addfTools/lint-residual-paths.py` で残存ゼロを確認する
   （ERROR = 移行未完了）
7. プロジェクト自身のビルド・テストを実行する。失敗したら **rewrite 射程外の4類型**
   （相対階層参照 / `os.path.join` 等の分割断片 / 書き込み先の親 mkdir / Markdown 相対リンク）
   を疑う — ADDF 本体の移行実測では 19 スイート中 18 の失敗が全てこの類型だった。
   git 追跡外ファイル（`settings.local.json` の許可ルール等）とコンパイル済みバイナリ内の
   パス断片も rewrite の対象外のため手動確認する
8. 失敗時の巻き戻し: `git reset --hard refs/backup/pre-0037-migration`

### 追加
- `migrate-paths.py` — paths.toml 駆動の移行ツール（check / apply / rewrite の3モード）。
  apply と rewrite の dirty 拒否でコミット分離を構造的に強制・backup ref の既存上書き拒否・
  symlink 除外・境界チェック付き置換（`docs/plans` が `docs/plans-add` に誤マッチしない）。 <!-- residual-path: allow -->
  check は rewrite 射程外の候補（相対階層参照・パス断片・相対リンク）も警告する
- `lint-residual-paths.py` — 旧パス残存の完了ゲート（ERROR ゼロになるまで移行を完了扱い
  しない）＋移行後の docs/ 逆流 WARNING（移行前のリポジトリでは明示 SKIP）
- `paths.toml` — 旧→新パスマップの単一ソース（コピーリスト類の手書きドリフトの構造的排除）
- `test-migrate-paths.sh` — 71 アサーション（独自 knowhow・Pages コンテンツを持つ合成
  プロジェクトでのダウンストリーム移行シミュレーション・ドリフト注入・攻撃再現テスト込み）
- 行単位の除外マーカー `residual-path: allow` — 移行手順書・移行ガイドの正当な旧パス
  言及行を行単位で除外する（ファイル丸ごとの除外による lint 盲点を排除）
- rewrite 完了メッセージに書き換え対象外（追跡外ファイル・パス断片・相対リンク・バイナリ）の
  手動確認案内

### 変更
- `/addf-migrate` に Phase 2.5（ディレクトリ大移行のワンショット手順）と lock 旧位置
  （`.claude/addf-lock.json`）のフォールバック検出を追加 <!-- residual-path: allow -->

## [0.5.0] - 2026-07-05

### 追加
- 投機開発の再構築・掃除・昇格運用（Plan 0028 フェーズ3完結）
  - `speculate-reconcile.py` — check（worktree prune＋走査＋merged_hint）/ clean（`--delete` 明示指定制。Worktrees.md の「昇格済み/放棄」記載との突合を削除前に強制、過去日付 integration の自動掃除、dirty worktree 既定拒否）
  - 昇格手順（`speculative/<concept>` → main の squash マージ。オーナーの明示応答必須・無応答を承認とみなすこと禁止）
  - テスト `test-speculate-reconcile.sh` 17本・72アサーション
- 投機運用ガイド `.claude/addf/guides/speculative-development.md` — 2層モデル・オプトイン・ライフサイクル・昇格の定義・clean 原則の概観
- `lint-hooks-wiring.py` — settings.json のフック配線と実ファイルの突合（境界チェック付き。addf-lint セクション11・addf-init check 項目6）
- addf-migrate の部分導入正規化モード — lock 不在＋ADDF ファイル有りの構成で「安全一括上書き / 個別確認必須」の2分割手順を提案
- プレリリースチェックに項目4（README 和英の新機能反映確認）・項目5（project-overview の鮮度確認）を追加
- project-overview に「投機開発」を独立の概念システムとして追加（6→7 システム）

### 変更
- upstream/downstream 判定を暗黙推定から明示シグナルに統一（Plan 0033）
- worktree への `.claude` 複製を3行構成に — venv/node_modules/__pycache__ の除外（symlink 含む）と追跡ファイル復元（Issue #18）
- `speculate-integrate.py` の `--base` を origin default branch 自動検出に（検出不能時は main フォールバック＋NOTE 可視化）（Issue #20）
- addf-migrate 14.6 の .gitignore ADDF ブロック置換をマーカー数検査付きに（不成立は手動マージへフォールバック）（Issue #20）
- run-all.sh に「必須ランタイム不在を SKIP=成功にしない」ガイドラインを追加
- addf-dev に Stage 構成の読み替え指針（独自フェーズ構成・単線構成プロジェクト対応）
- README（和・英）に addf-speculate と投機開発ガイドを掲載
- project-overview の GUI テスト記述をオプトイン前提に統一（Plan 0029 残課題 L1 解消）
- 投機の同時 worktree 上限（`max_worktrees`）の推奨値を 3→7 に変更

### 修正
- 投機 worktree の venv 破損バグ — `.claude` 複製時に venv/シンボリックリンクを持ち込まない（Issue #18・ダウンストリーム実測報告）
- default branch が main でないダウンストリームでの integration 誤 base — 自動検出化により解消（Issue #20）
- lint-template-sync のダウンストリーム構成（addf-lock.json あり・独自 AGENTS.md あり）での誤検知（Plan 0033）

## [0.4.0] - 2026-07-03

### 追加
- worktree 投機開発（`/addf-speculate`）— アイドル時に直交概念を `speculative/` ブランチで投機し、integration ブランチで一括動作確認する2層モデル（Plan 0028 フェーズ1・2）
  - `speculate-guard.py` — `[speculation]` enable・上限の発動ガード（オプトイン式・デフォルト無効）
  - `speculate-integrate.py` — integration ブランチへの squash 統合。衝突 feature のスキップ報告・commit フック拒否の検出（`commit_failed`）・メイン作業ツリー不可侵
  - Stage 2 一括ゲート（integration 上の相互作用テスト＋ペルソナ並列レビュー）と Dashboard 書き分け
- オプショナルスキルのオプトイン機構 — GUI スキル一式を `.claude/addf/optional/` に退避し、`[gui-test] enable` + `sync-optional-skills.py apply` で有効化コピーを配置（Plan 0029 フェーズ1）
- チェックリスト裏付け lint（`lint-checklist.py`）— 手順書の「確認」項目に実行チェックか human-judgment マーカーの裏付けを要求（Plan 0027）
- 旧 Python 環境ガード — tomllib（Python 3.11+）・PEP 723 依存（pyyaml）を使うスクリプトに責務別 import ガード（lint = SKIP / 実行前ゲート = フェイルセーフ ERROR / 変更系 = ERROR）
- 再現テスト群 — `test-lint-toml` / `test-lint-frontmatter` / `test-speculate-guard` / `test-speculate-integrate` / `test-optional-skills`（PYTHONPATH シム・commit フック注入によるドリフト注入 TDD）

### 変更
- Python スクリプトの呼び出しを `uv run --python 3.11` に統一し、uv 不在環境向けの `python3` 直接実行フォールバック注記を手順書（addf-lint / addf-migrate / addf-speculate / .claude/addf/guides）に併記
- GUI テストシナリオ（test-addf-clip-image / test-addf-annotate-grid）にオプトイン前提の注記を追加
- 非 macOS 環境ではバイナリ実行テストを SKIP（Plan 0029）

### 修正
- macOS システム python3（3.9）で tomllib 依存スクリプトが未捕捉の Traceback で落ちる罠を修正
- `lint-frontmatter.py` の pyyaml 欠如時の未捕捉クラッシュを SKIP ガード化（ペルソナ並列レビューの3者独立指摘による検出）

## [0.3.0] - 2026-06-29

### 追加
- 「迷ったときの作法（7割共有原則）」— 3軸（信頼性・応答性・完成イメージ確度）でエージェントの進む/止まる/問うを制御（Plan 0016）
- 代替わり日記（Progress 日記）— compaction・resume・loop 継続での「小さな代替わり」に備える引き継ぎ書式（Plan 0017）
- knowhow ライフサイクル管理 — 鮮度タグ・`/addf-knowhow-revise`・`/addf-knowhow-network` による知見の経年管理（Plan 0018）
- 分かれ道の目印（`.exp.md` 🔀セクション）— 差し戻し・やり直しの経験を道標として記録（Plan 0019）
- 視点ずらしレビュー（ペルソナ並列）— `addf-code-review-agent` に5つのペルソナを追加し、マイルストーン時に並列起動（Plan 0020）
- テンプレート同期 lint（`lint-template-sync.py`）— 6ペアの同期チェックを自動化（Plan 0021, 0022, 0024）
- turn-reminder の関心事分離 — ターンカウンターとコンテキスト量リマインダーを独立スクリプトに分割（Plan 0023）
- 実測ベース能動コンパクション促し — `context-reminder.py` でトークン量を実測し、閾値超過時に促す（Plan 0023）
- `/addf-overview` スキル — エコシステム概要の提供
- コンパクション復帰フック — コンパクション後のブートシーケンス再開を自動化
- プロジェクト初回の骨格プランニングフロー — ブートシーケンス Step 4 でヒアリング→計画生成を自動化
- `CLAUDE.repo.md` 自動生成 — 骨格プランニング時にプロジェクト固有設定を生成
- ノウハウ記録の3観点（コーディング・品質ゲート・タスク総括）を ProgressTemplate に明文化
- `.claude/addf/Questions.md` — 非同期質問箱（relaxed/unattended モード用）
- `.claude/addf/Dashboard.md` — unattended 自走時の差分まとめ

### 変更
- リポジトリ URL を `fruitriin/ADDF` に変更（Plan 0025）
- README にロゴバナーを追加
- 代替わり日記の「同僚」表現を「同僚でもあり、寝て起きたあとの自分でもある」に改善

### 修正
- `addf-init` コピーリストの鮮度回復と同期 lint ペア5の追加（Plan 0022）
- Questions.md の運用フロー整備

## [0.2.0] - 2026-03-21

### 追加
- `/addf-init` スキル — プロジェクト初期セットアップ・構造検証・既存プロジェクトへの導入
- `/addf-release` スキル — リリース自動化（upstream/downstream 自動判定）
- `/addf-migrate` にスキルリネーム時の `.exp.md` 手動リネーム案内を追加
- `ADDF-Release.addf.md` — ADDF 本体のリリース手順定義
- `AGENTS.md` — Codex 向けブートシーケンス
- `.claude/addf/guides/codex-setup.md` — Codex ユーザー向けセットアップガイド
- 経験ファイルテンプレート（`ExperienceTemplate.md`）と主要3スキルの初期経験
- スキル使用計測フック（`skill-usage-log.sh` / PreToolUse）
- `.claude/addf/guides/` にドキュメント分離（setup, skills, agents, development-process, migration）
- 既存プロジェクトへの ADDF 導入（WebFetch → tmp クローン → 干渉チェック → 導入前レビュー）
- `.gitignore` マーカーブロック形式（`addf-migrate` での自動更新対応）

### 変更
- `/addf-dev-loop` → `/addf-dev` にリネーム（1タスク実施が基本、`/loop` で繰り返し）
- 全スキルの description にトリガー条件（「〜のとき使う」）を追加
- README をリポジトリ構成フレームワークとして再構成（対応エージェント表、既存プロジェクト導入手順）
- `addf-lint` の frontmatter チェックで `.exp.md` を除外

### 修正
- `addf-migrate` の対象リストに `settings.json`, `AGENTS.md`, `ADDF-Release.addf.md`, `.claude/addf/guides/` を追加
- `skill-usage-log.sh` の JSONL インジェクション対策（jq でエントリ全体を生成）
- `addf-init` / `addf-migrate` に URL 検証ステップを追加（`https://` のみ許可）

## [0.1.0] - 2026-03-20

### 追加
- `addf-lock.json` — バージョン追跡用ロックファイル
- `/addf-migrate` スキル — ADDF のアップグレードを安全に実行する6フェーズのマイグレーション
- `ADDF-CHANGELOG.md` — フレームワーク変更履歴（本ファイル）
- `settings.json` に `git clone`, `git -C`, `mktemp` 権限を追加

### 初期リリース内容
- ブートシーケンス（CLAUDE.md）による自動コンテキスト読み込み
- ノウハウ管理（`/addf-knowhow`, `/addf-knowhow-index`, `/addf-knowhow-filter`）
- 自律開発（`/addf-dev`、旧 `/addf-dev-loop`）
- 品質ゲート（`addf-code-review-agent`, `addf-security-review-agent`, `addf-contribution-agent`）
- GUI テスト（`/addf-gui-test`, `/addf-annotate-grid`, `/addf-clip-image`）— macOS オプション
- 経験ファイル検証（`/addf-experience`）
- フレームワーク整合性チェック（`/addf-lint`）
- 権限監査（`/addf-permission-audit`）
- ターンカウンターフック（SessionStart / UserPromptSubmit）
