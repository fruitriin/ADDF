# 品質ゲート — Multi-agent quality assurance

> 概念単位の記録。実装がスキル/エージェント/フック/ファイルのどれであっても、
> 「コード品質・フレームワーク整合性の検証・保証」に関わるものをまとめている。

## 構成要素

| 種別 | 名前 | 役割 |
|---|---|---|
| エージェント | addf-code-review-agent | コード品質・可読性・ベストプラクティスのレビュー（Sonnet）。5ペルソナの視点ずらしレビュー・全体監査モード対応 |
| エージェント | addf-security-review-agent | ペネトレーションテスター人格で脆弱性検出・修正案提示（Sonnet。実装はしない） |
| エージェント | addf-contribution-agent | ADDF / プロジェクト固有コードの識別、分離パターン違反検出、アップストリーム貢献候補検出（Sonnet） |
| エージェント | addf-doc-review-agent | ドキュメントドリフト（実装との乖離）とモチベーション/実装事実の混同を検出（Sonnet。Plan 0039 フェーズ1で EnumaElish から逆輸入・汎用化）。**ドキュメントに触れた変更のときのみ起動**（起動判定はメインエージェント側） |
| スキル | addf-lint | フレームワーク整合性チェック（13項目: JSON構文・hooks実行権限・frontmatter・Behavior.toml・INDEX整合・テンプレート同期・knowhow鮮度・knowhow双方向リンク・チェックリスト裏付け・オプショナルスキル同期・hooks配線・Plan状態整合・ccchain同期〔セクション13 — Plan 0040 フェーズ2〕） |
| テスト | .claude/addf/tests/run-all.sh | フレームワーク自動テスト（フック5本・ツール19本。スキルシナリオ8本は手動）。非 macOS ではバイナリ実行テストを SKIP。ランタイム不在を SKIP=成功として扱わない（silent 無効化の禁止）。Plan 0052（Issue #26）で GUI バイナリの画面収録権限ダイアログ待ちによる無限ハングを timeout ガードで解消し、Test の SKIP フォールバックを追加。Plan 0059（Issue #30・#31）で downstream 環境適合を強化 — `make_sandbox()` の `*.addf.md` 疑似コピー方式・TODO テーブルのリンク書式両対応・downstream 分岐を明示的に踏む回帰テスト24件 |
| CI | .github/workflows/test.yml + .github/scripts/run-lint.sh | GitHub Actions 品質ゲート（Plan 0030）。PR / main push ごとに run-all.sh と lint 一式を自動実行。lint の3値 exit を run-lint.sh がマッピング（1=ジョブ失敗 / 2=通過+warning annotation）。ADDF 本体固有（配布対象外・ダウンストリームの雛形） |
| ツール | .claude/addf/addfTools/lint-json.py / lint-frontmatter.py / lint-toml.py | 構文 Lint スクリプト（uv run --python 3.11 で実行。uv が無ければ python3 直接実行） |
| ツール | .claude/addf/addfTools/lint-hooks-exec.py | hooks の実行権限検査（実行権限のないフックは settings 登録済みでも静かに失敗する問題の防止） |
| ツール | .claude/addf/addfTools/lint-hooks-wiring.py | hooks ファイル名と settings.json / settings.local.json の配線突合（`# hooks-wiring: indirect` エスケープハッチあり） |
| ツール | .claude/addf/addfTools/lint-template-sync.py | テンプレート同期チェック（8ペア）。exit 0=全一致 / 1=ERROR / 2=WARNING のみ |
| ツール | .claude/addf/addfTools/lint-checklist.py | 手順書の「確認/検証」ステップの裏付け検査（実行チェック or human-judgment マーカー。WARNING のみ） |
| ツール | .claude/addf/addfTools/lint-plan-status.py | Plan の `## 実装状況:` ヘッダ「完了」×完了条件の未チェック `- [ ]` 残存の矛盾検出（誤完了防止・Plan 0035 フェーズC。addf-lint セクション12） |
| ツール | .claude/addf/addfTools/lint-residual-paths.py | 旧パス残存の検査（Plan 0037 移行完了ゲート＋docs/ 逆流 WARNING。→ system-distribution と共有）。Plan 0060（Issue #33）で `compile_pattern()` に lookbehind 境界を導入 — 外部 URL・他プロジェクト絶対パスの言及を誤検知しない（migrate-paths.py と同期契約。既知の限界と根治は Plan 0068） |
| ツール | .claude/addf/addfTools/sync-ccchain.py（check モード） | ccchain 同期検査（addf-lint セクション13。[ccchain] enable と `.ccchain.conf`・settings.json フックエントリの整合。enable=true でバイナリ不在は WARNING — フェイルセーフ素通し設計。→ system-distribution / system-session と共有） |
| ツール | .claude/addf/addfTools/verify-checksums.sh | 配布バイナリの SHA-256 照合＋allowlist ガード（Plan 0031。→ system-visual-testing と共有。repo_kind 判定は lint-template-sync の detect_repo_kind() と同期契約 — ペア7が契約文言を機械検査） |
| ツール | .claude/addf/addfTools/sync-optional-skills.py（check モード） | オプトインスキルの同期検査（孤児コピー・enable の型。→ system-distribution / system-visual-testing と共有） |

## 設計思想

ADDF の第三の柱。「人間がレビューするのは計画の方向性、コード品質は AI が担保する」という CONTRIBUTING.md の方針を実装する。

2段階の品質ゲート:
- **Stage 1（ゲートキーパー）**: ビルド・Lint・テスト。失敗したら実装に差し戻し
- **Stage 2（品質検証チーム）**: code-review, security-review, contribution-agent を並列実行

対応方針（**一次軸: 主題との関係 / 二次軸: クリティカル度** — Plan 0047 で更新）:
- **主題内 → このフェーズで対応**（クリティカル度は問わない）: Critical/High は必修正、Medium 以下は原則修正の順で
- **主題外 → 別 Plan に切り出す**（「ついでに見つけてしまった何か」）: 切り出した Plan の優先度をクリティカル度で決め、Critical/High は TODO 最上位＋次タスク即着手（「フェーズ内先送り禁止」の安全性は維持）
- **切り出した Plan の実装ルート**は `変更ルート判断表`（→ speculative-development.md）で改めて判定する

### 視点ずらしレビュー（ペルソナ並列）— Plan 0020

実装者と同じモデルのレビュアーは実装者と同じ盲点を持ちやすい。ペルソナはこの盲点をずらす装置。addf-code-review-agent は起動プロンプトの「ペルソナ: <名前>」指定で単一視点に固定される:

| ペルソナ | 視点 |
|---|---|
| skeptic | 実装者の暗黙の前提を全て疑う |
| attacker | コードロジックの穴を壊す目的で読む（システムレベルは security-review-agent の担当） |
| newcomer | 初見で意図が読み取れない箇所を指摘 |
| maintainer | 半年後の変更容易性・依存の罠・テストの抜け |
| domain-skeptic | Plan と実装の乖離・要件の読み違え |

発動条件: 通常タスクは単体（ペルソナなし）。マイルストーン・リリース直前・unattended 自走時は3体並列、`mode: critical` 宣言時は5体並列。**投機サイクルの Stage 2（integration 一括レビュー）も3体並列**（→ system-speculation）。集約ルール: 同一箇所・同一原因は1件にまとめてペルソナを列挙し、**2ペルソナ以上が独立に指摘した項目は重要度を1段上げる**（コンセンサス補正）。one-shot 級の大改造（Plan 0037 実績）では、巻き戻し困難な適用**前**にレビューを打ち、attacker には手順書どおりの実地リハーサルをさせる「実地リハーサル型レビュー」が有効（.claude/addf/knowhow/ADDF/persona-review-oneshot.md）。

### ドキュメントレビュー（addf-doc-review-agent）— Plan 0039 フェーズ1

コードレビューが見ないもの — README・ガイド・スキル定義と実装の乖離 — を専任で見る。観点は (1) ドキュメントドリフト（「未実装」注記の実装済み化・廃止機能の残存・新機能の記載漏れ）、(2) モチベーション（なぜ）と実装事実（何ができるか）の混同。毎タスク起動はコスト過剰なため、`git diff` に `*.md`・docs/ 配下・スキル/エージェント定義の変更が含まれるときのみ起動する。コードレビューとは変更差分の別観点を見るため**並列起動でよい**（集約は起動側）。テストフィクスチャ（.claude/addf/tests/fixtures/doc-review-drift/）でドリフト検出能力自体も検証される。

### テンプレート同期 lint — Plan 0021/0022/0024（＋ペア7 = Plan 0031）

「意思で覚えず機械化する」。同期ファイルペアのドリフトを決定的スクリプトで検出し、解釈と修復はエージェントが行う:

| ペア | 検証内容 | 重要度 |
|---|---|---|
| 1. ProgressTemplate.addf.md ⇔ Progress.md | 運用ルールのテキスト包含 | ERROR |
| 2. ProgressTemplate.addf.md ⇔ ProgressTemplate.md | 運用ルールの正規化比較 | WARNING |
| 3. CLAUDE.md ⇔ AGENTS.md | ブートシーケンス手順番号の対応 | WARNING |
| 4. CLAUDE.md ⇔ .claude/addf/guides/development-process.md | ブートシーケンス概要の手順番号 | WARNING |
| 5. CLAUDE.md ⇔ addf-init.md コピーリスト | 参照ファイルのカバレッジ（.gitignore ADDF ブロック含む） | WARNING |
| 6. TODO ⇔ Plan の `## 実装状況:` ヘッダ | 状態の矛盾・参照切れ・登録漏れ・表記ゆれヘッダ検出 | WARNING |
| 7. verify-checksums.sh ⇔ lint-template-sync.py | `detect_repo_kind()` Python⇔Bash 実装の同期契約文言の存在チェック | WARNING |
| 8. README.md/README.en.md ⇔ .claude/commands/addf-*.md | スキルテーブルへの掲載漏れ検出。upstream 限定（downstream は SKIP） | WARNING |

ペア8は Plan 0053（2026-07-11 完了・v0.6.2 収録）で新設された。Plan 0053 は自己点検で CHANGELOG.md の記載漏れ（11 Plan 分）と README のスキル一覧掲載漏れ（addf-plan-audit）を発見・回収し、再発防止としてこのペアを追加した。ペア6の TODO テーブル解析は Plan 0059（Issue #31）で markdown リンク書式 `[title](path)` とバックティック書式の両対応になった（downstream で広く使われるリンク書式が「TODO 登録漏れ」誤 WARNING になっていた）。

ペア2〜6はダウンストリームで対象ファイルが無ければ SKIP（欠如はドリフトではない — 配布時誤 ERROR の防止。ただし SKIP は明示出力して件数計上する — silent 無効化の禁止）。WARNING には git log の最終更新日ヒントが併記され、どちらを正とするかはエージェントが文脈で判断する。upstream/downstream の判定は**存在ではなく明示シグナル**（CLAUDE.repo.md の種別宣言＋addf-lock.json）で行う（Plan 0033。「存在≠所有」— 配布で *.addf.md が物理存在しうるため）。新たな同期ペアが生まれたら lint と addf-lint.md セクション6の表を同時更新する（Feedback.md 記録済み）。

### チェックリスト裏付け lint — Plan 0027

手順書（Release.addf / addf-init / addf-migrate / addf-plan-audit / ProgressTemplate 系）の「確認/検証」ステップに、実行チェック（コードブロック・コマンド）か `<!-- human-judgment -->` マーカーの裏付けを要求するメタ lint（lint-checklist.py・WARNING のみ）。チェックリストの theater 化（確認と書いてあるが確認する手段がない）を防ぐ。理由付きホワイトリスト（skip-section マーカー）を持ち、責めないトーンで報告する（.claude/addf/knowhow/ADDF/checklist-backing-lint.md）。

### Plan 状態整合 lint（誤完了防止）— Plan 0035 フェーズC

Plan の `## 実装状況:` ヘッダが「完了」なのに完了条件に未チェック `- [ ]` が残る矛盾（フェーズ分割 Plan の途中マージで「済み」に見える誤完了）を lint-plan-status.py が常時ブロックする。過去に埋没した意味的な取りこぼしの掘り起こしは /addf-plan-audit（一回きり＋任意の棚卸し）が補完する（→ system-planning）。

### CI 品質ゲート — Plan 0030

GitHub Actions（test.yml）が PR / main push ごとに run-all.sh と lint 一式を実行する。lint の3値 exit（0=OK / 1=ERROR / 2=WARNING）を run-lint.sh が CI セマンティクスへマッピングし、WARNING は落とさず `::warning::` annotation で可視化する。最小権限（contents: read）・concurrency で連続 push の旧実行をキャンセル。branch protection の要否はオーナー判断待ち。

### セキュリティ回収（deny/ask リスト・破壊的操作ガード）— Plan 0043

品質ゲートの一部として、破壊的操作は「常時ブロック（deny）」「理由提示のうえ確認（ask + hook の advisory 注意）」の2段構えで防ぐ。`settings.json` の `permissions.deny` に極端な破壊操作11パターン（`rm -rf /` 系・`chmod 777 /` 系・`dd`・`mkfs`・`shutdown`・`reboot`）を常時ブロックし、`permissions.ask` に5種の破壊的 git 操作（`reset --hard`・`push --force`・`clean -f`・`branch -D`・`checkout -- .`/`restore .`）を置く。フック `destructive-git-guard.sh`（PreToolUse: Bash）はこれらのパターンを検出して**理由をユーザーに提示するだけ**で、ブロック自体は `permissions.ask` に委ねる分業設計（フック詳細は → system-session）。事後観測方式で段階調整する方針（Feedback.md Q3 参照）。

### ダウンストリーム環境適合テスト（合成フィクスチャと drift-injection）— Plan 0055/0058/0059

「実リポジトリ固有コンテンツ依存のテストアサーション」（実在 Plan がたまたま含む文字列への grep・Plan 1件以上の前提など）は、downstream の空リポジトリで必ず FAIL する再発性の欠陥クラス（Issue #29 → Plan 0055 で初回修正、Plan 0058 のダッシュボードテスト初版で同型が再発 — Feedback.md 記録済み）。対処の型は**合成フィクスチャの drift-injection 方式**: テストがサンドボックスに合成リポジトリを作り、意図的なドリフトを注入して検出能力自体を検証する（test-generate-dashboard.sh・test-template-sync.sh の `make_sandbox()` 疑似コピー方式〔Issue #30・Plan 0059〕）。テスト新設時の自問は「このアサーションは Plan が0件の空のダウンストリームリポジトリでも成立するか？」。

### 実行環境ガードの3類型

Python 3.11+ stdlib（tomllib）や PEP 723 依存（pyyaml）を使う addfTools は、責務別に実行環境欠如時の挙動を分ける（.claude/addf/knowhow/ADDF/sync-lint-design.md）:
- **lint** = SKIP（明示出力・件数計上）
- **実行前ゲート**（speculate-guard 等）= フェイルセーフ ERROR（動けないなら開始しない）
- **変更系**（sync-optional-skills apply 等）= ERROR

## 主要フロー

```
タスク実装完了
  │
  ▼
Stage 1: ビルド検証（ゲートキーパー）
  ├─ bash .claude/addf/tests/run-all.sh
  ├─ プロジェクト固有の build/lint/test
  └─ 失敗 → 実装に差し戻し
  │
  ▼（Stage 1 通過後）
Stage 2: 品質検証チーム（並列起動）
  ├─ addf-code-review-agent ────┐  通常: 単体
  │   （条件により3〜5ペルソナ並列） │  集約: コンセンサス補正
  ├─ addf-security-review-agent ─┤─ フィードバック集約
  ├─ addf-contribution-agent ───┤
  ├─ addf-doc-review-agent ─────┤（ドキュメントに触れた変更のときのみ）
  └─ addf-ui-test-agent（GUI オプトイン有効時） ┘
  ※ ADDF 本体では push/PR 時に CI（test.yml）が Stage 1 相当＋lint を再実行
  │
  ▼
指摘対応（一次軸: 主題との関係 / 二次軸: クリティカル度 — Plan 0047）
  ├─ 主題内 → このフェーズで対応（Critical/High は必修正 → Stage 1 再実行）
  └─ 主題外 → 別 Plan 切り出し（主題外 Critical/High は TODO 最上位で次タスク即着手）
       → 実装ルートは変更ルート判断表で改めて判定
```

## 下流でのカスタマイズ

- Stage 2 の品質検証チームの構成を CLAUDE.repo.md で変更可能（「品質ゲート拡張」セクション）
- addf-ui-test-agent を追加して GUI テストを品質ゲートに組み込める（[gui-test] オプトイン有効時）
- addf-contribution-agent はダウンストリームでは分離パターン違反と ADDF への還元候補を検出する
- lint 群はダウンストリームでも動作する（ADDF 固有ペア・対象ファイル欠如は SKIP、ペア1は ProgressTemplate.md を正として比較）
- ペルソナ並列の発動条件（`mode: critical` 等）は Plan フロントマターで宣言

## 関連するシステム

- **計画駆動**: Progress.md の品質検証フローが品質ゲートを起動する（doc-review の起動判定もここ）。unattended モード（/addf-mode）がペルソナ並列の発動条件になる。lint セクション12（誤完了防止）は /addf-plan-audit と役割分担する
- **投機開発**: 投機の Stage 1 は feature worktree 単位で、Stage 2（ペルソナ並列）は integration ブランチで一括実行される。speculate ツールのテスト3本も run-all.sh に組み込み
- **ノウハウ蓄積**: レビューで得た知見が knowhow に、差し戻しは .exp.md「分かれ道の目印」に蓄積される。addf-lint の項目5・7・8が knowhow の整合・鮮度・リンクを検査
- **視覚テスト**: addf-ui-test-agent が Stage 2 に参加可能（オプトイン有効時）。addf-lint 項目10がオプトイン同期を検査
- **配布・導入**: addf-lint と run-all.sh は配布物の品質保証でもある（SKIP 設計・明示シグナルによる種別判定・downstream 環境適合テストはダウンストリーム配布前提の機構）。lint-residual-paths はディレクトリ大移行（Plan 0037）の完了ゲート、verify-checksums は配布バイナリの検証、sync-ccchain check（項目13）は ccchain オプトインの同期検査
