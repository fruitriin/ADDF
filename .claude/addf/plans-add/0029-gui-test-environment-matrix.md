# Plan 0029: GUI テストの環境マトリクス化（環境別オプトイン・差し替え・組み合わせ）

## 実装状況: 一部完了（2026-07-02。フェーズ1 = スキル本体のオプトイン配置が完了。環境マトリクス・ドライバ抽象はフェーズ2以降・オーナー方針 2026-07-06 反映）

## フェーズ2 以降のオーナー判断（2026-07-06）

- **別途適宜実施したい**（フェーズ2 以降は着手時期未定・優先度は下）
- **動作確認環境の手配を考察する必要あり**:
  - macOS: メイン開発環境（既存）
  - Windows: **Crossover 環境**をユーザー側で用意可能（実機ではなく Crossover 経由での Windows 動作確認）
  - Linux: CI（ubuntu-latest）で run-all は既に実行中。GUI テストは非対応（バイナリは macOS 専用）
- 環境マトリクスの設計時に「Crossover 経由 Windows」を1環境として明示する。純 Windows と Crossover の差分（挙動・パフォーマンス・API 互換性）は着手時に実測して knowhow 化

### フェーズ1 実装記録（2026-07-02）

「設計の骨子 5.」を、既存 `gui-test.enable` をマスタースイッチとして環境スキーマと独立に実装:

- GUI スキル3本＋`addf-ui-test-agent` を `.claude/addf/optional/{commands,agents}/` へ git mv（原本化）
- `sync-optional-skills.py` 新設（check = /addf-lint セクション10 / apply = 配置・撤去）。3原則
  「原本が真実源・コピーは使い捨て・改変コピーは削除も上書きもしない」を実装。
  gitignore 列挙漏れ・原本を失った孤児コピーの検出付き（列挙の陳腐化対策）。
  enable の型検証（`"false"` 文字列の誤 True を ERROR）、TOML 構文エラーは lint-toml へ責務分離して SKIP
- `.gitignore` ADDF ブロックに有効化コピー4パス追加（残骸エントリ問題の正統な再来版）
- addf-init コピーリスト・addf-migrate（Phase 5 に手順 14.5「オプショナルスキルの同期」を実行ステップとして追加、
  完了レポートに /addf-lint 案内）・lint-frontmatter・addf-experience のスキャン範囲・
  .claude/addf/guides（gui-test-setup / agents / skills）を追随
- テスト25件（`test-optional-skills.sh`: 配置・撤去・改変保護・設定不正・gitignore 整合）
- レビュー High 2件（ガイドの旧前提 / migrate 手順の未具現化 — 「参照では実行されない」の同型穴）・
  Medium 5件をフェーズ内修正

**フェーズ1の残課題（Low/Info、記録のみ）**:
- ~~L1: `.claude/addf/project-overview/*` が GUI スキル常設前提のまま（生成物。次回 /addf-overview 再生成で解消）~~
  → **解消済み（2026-07-05）**: Plan 0028 フェーズ3-4 の /addf-overview full 再生成で
  オプトイン前提の記述に統一。常設前提表現の残存ゼロを grep 確認済み
- L3: `.claude/addf/tests/skills/test-addf-{clip-image,annotate-grid}.md` に enable+apply 前提の一言がない

> **粗々の起票**: 設計の方向性と未決事項を出す段階。実装詳細は着手時に詰める。

## 目的

環境によって動作しない GUI テストを**シナリオ単位でオプトイン式**にし、GUI テストの実装（ドライバ）を
**環境ごとに差し替え・組み合わせ**できるようにする。対象環境は win / mac / linux / web / ios / android。

現状（Plan 0004 の到達点）:
- `addf-Behavior.toml` の `[gui-test]` は `enable`（全体 ON/OFF）と `machine`（単一値 `"mac" | "linux" | "windows"`）のみ
- mac 以外は「未実装です」と報告して**全体が終了**する — 環境が合わないと GUI テスト全部が動かない
- シナリオ側（`docs/test-scenarios/`）に「どの環境で動くか」を宣言する場所がなく、
  動かない環境で実行すると SKIP ではなく FAIL / エラーになる

## 設計の骨子

### 1. ホスト × ターゲットの2次元で環境を捉える

「環境」は1軸ではない。**ホスト OS**（テストを実行するマシン）と**ターゲットランタイム**（テスト対象が動く場所）
を分けて考える:

- ホスト OS: `mac` / `windows` / `linux`
- ターゲットランタイム: `native`（ホスト上のデスクトップアプリ）/ `web`（ブラウザ）/ `ios`（シミュレータ）/ `android`（エミュレータ）

「mac 上で web アプリをテスト」「mac 上で ios シミュレータをテスト」のような**組み合わせ**が自然に表現できる。
シナリオは環境タグの集合を要求し、実行側は「現在満たせるタグの集合」を持ち、要求がサブセットなら実行する。

### 2. `addf-Behavior.toml` — 環境ごとのオプトインとドライバ宣言

単一 `machine` を環境テーブルの集合に拡張する（案）:

```toml
[gui-test]
enable = false          # 全体マスタースイッチ（既存互換）

[gui-test.environments.mac]
enable = true
driver = "addftools-swift"   # 既存 Swift 実装（window-info / capture-window 等）

[gui-test.environments.web]
enable = true
driver = "playwright"        # ブラウザ経由。ホスト OS 非依存

[gui-test.environments.ios]
enable = false               # 未セットアップ環境はオプトインしない（デフォルト無効）
driver = "simctl"

[gui-test.environments.android]
enable = false
driver = "adb"
```

- **各環境はデフォルト無効＝オプトイン式**。有効化した環境のタグだけが「満たせる集合」に入る
- `driver` で実装を差し替え可能にする（例: linux native を `xdotool` 系にするか独自実装にするかは
  ダウンストリームが選べる）
- 既存の `machine = "mac"` は後方互換として読み、`[gui-test.environments.mac] enable = true` 相当に解釈する
  （`/addf-migrate` でのマイグレーションパスも用意する）

### 3. シナリオ側の環境宣言と SKIP セマンティクス

`docs/test-scenarios/` のシナリオファイルに frontmatter で要求環境を宣言する（案）:

```yaml
---
environments: [mac]          # このシナリオが動く環境タグ。複数書けば「いずれかで可」
# environments: [mac+web]    # 組み合わせ要求（mac ホストのブラウザ）は + 連結（表記は要検討）
---
```

- 実行時、要求を満たせないシナリオは **FAIL ではなく SKIP** とし、理由（どのタグが不足か）を必ず報告する
  — 「全部やったように見える silent truncation」を避ける（Feedback.md の精神と一致）
- frontmatter がないレガシーシナリオは「全環境要求＝現環境で常に実行」ではなく
  **警告付きで現環境実行**とし、移行を促す（要検討）
- `/addf-gui-test` 引数なしの一覧表示に、各シナリオの要求環境と現環境での実行可否（RUN / SKIP）を併記する

### 4. ドライバ抽象 — 操作プリミティブの差し替え

Plan 0004 で定義した抽象操作（window-info / capture-window / annotate-grid / clip-image）を
**ドライバインターフェース**として明文化し、環境ごとに実装を差し替える:

| プリミティブ | mac (native) | windows (native) | linux (native) | web | ios / android |
|---|---|---|---|---|---|
| window-info | Swift 実装（既存） | 未実装（スタブ） | 未実装（スタブ） | Playwright page/viewport | simctl / adb（スタブ） |
| capture-window | Swift 実装（既存） | 未実装（スタブ） | 未実装（スタブ） | Playwright screenshot | simctl io / adb screencap |
| annotate-grid | 環境非依存（既存実装を全環境で共用） | ← | ← | ← | ← |
| clip-image | 環境非依存（既存実装を全環境で共用） | ← | ← | ← | ← |

- 配置規約（案）: `.claude/addf/tools/drivers/<driver名>/` に環境固有実装を置き、
  環境非依存ツール（annotate-grid / clip-image）は現行の場所のまま共用する
- 本 Plan で**実装まで持つのは mac（既存）と web（Playwright）の2ドライバ**とし、
  windows / linux / ios / android は「インターフェース準拠のスタブ＋SKIP 報告」まで
  （ダウンストリームや後続 Plan が差し込める形を先に作る）

### 5. スキル本体のオプトイン配置 — 退避 ＋ 有効化コピー

設定レベル（Behavior.toml）のオプトインに加えて、**GUI を扱うスキル定義そのものを能力レベルでオプトイン**にする。
GUI 関連スキルを発見パス外に退避しておき、オプトイン時にスキルディレクトリへ実体化する。

**対象**（GUI を扱う一式）:
- `.claude/commands/addf-gui-test.md` / `addf-annotate-grid.md` / `addf-clip-image.md`
- `.claude/agents/addf-ui-test-agent.md`（エージェントも自動発見されるため同じ機構に乗せる）

**配置（案）**:
```
.claude/addf/optional/commands/addf-gui-test.md      ← 原本（コミット対象。発見パス外）
.claude/addf/optional/agents/addf-ui-test-agent.md   ← 同上
.claude/commands/addf-gui-test.md               ← 有効化コピー（gitignore。オプトイン時に生成）
```
- 退避先は `.claude/commands/` / `.claude/agents/` の**外**に置く（`.claude/commands/` のサブディレクトリは
  名前空間付きコマンドとして発見されてしまうため不可）

**方式はシンボリックリンクではなくコピーを推奨**:
- ダウンストリームは Windows も対象。Windows のシンボリックリンクは権限（Developer Mode）と
  git 設定（`core.symlinks`）依存が強く、「clone したら壊れたリンクだった」が起きうる
- コピーの弱点（原本とのドリフト）は次の3点で殺す:
  1. 有効化コピーは **gitignore**（`.gitignore` ADDF ブロックには残骸エントリ
     `.claude/skills/addf-gui-test.md` が現存する — Plan 0026 Low 指摘。本 Plan で正しいパスに直して再利用し、指摘を解消する）
  2. 原本からいつでも再生成可能（コピーは使い捨て）
  3. **同期 lint に新ペアを追加**: 「オプトイン中は原本と有効化コピーが一致すること」＋
     「Behavior.toml の enable 状態とスキル実体の有無が一致すること」（enable なのにスキル不在 / disable なのに残存 → WARNING）。
     Feedback.md のルールに従い、ペア追加時に addf-lint.md セクション6の表も同時更新する

**Behavior.toml を単一の真実源とする**:
- オーナーが直接コピーを操作するのではなく、`[gui-test]` の enable 状態を宣言 →
  同期ステップ（`/addf-gui-test setup`（新設サブコマンド）または `/addf-init` / `/addf-migrate` の一部）が
  スキル実体を配置・撤去する。手で剥がしても lint が不整合を検出する
- 有効化の粒度は「いずれかの環境が enable ならスキル一式を配置」（環境タグはシナリオフィルタ側の関心事で、
  スキルの有無は「GUI を扱ってよいか」のマスタースイッチ）

**経験ファイル（.exp.md）の扱い**:
- `addf-gui-test.exp.md` 等は gitignore 済みの実行時生成物。無効化時も**削除しない**
  （再オプトイン時に過去の経験が戻るように。スキル不在時に exp だけ残っていても無害）

### 6. スキル・エージェント・ドキュメントの追随

- `.claude/commands/addf-gui-test.md`: 手順2のプラットフォーム判定を「環境タグ解決 → シナリオフィルタ →
  ドライバ選択」に書き換える
- `.claude/agents/addf-ui-test-agent.md`: ツール一覧をドライバ抽象前提の記述に更新する
- `.claude/addf/guides/gui-test-setup.md`: 「現在 macOS のみ対応」を環境マトリクス表に更新し、
  環境ごとのセットアップ手順（web: Playwright、ios: Xcode/simctl 等）を追記する
- `docs/test-scenarios/README.md`（あれば）: frontmatter 書式を記載する

## 影響範囲

- `.claude/addf/Behavior.toml`（スキーマ拡張・後方互換）
- `.claude/commands/addf-gui-test.md` / `addf-annotate-grid.md` / `addf-clip-image.md` /
  `.claude/agents/addf-ui-test-agent.md`（`.claude/addf/optional/` への退避＋有効化コピー機構）
- `.gitignore` ADDF ブロック（有効化コピーのエントリ追加。残骸エントリ `.claude/skills/addf-gui-test.md` の修正 — Plan 0026 Low 指摘の解消）
- `.claude/addf/tools/`（drivers/ ディレクトリ導入、web ドライバ新規）
- `.claude/addf/tools/lint-template-sync.py`（原本⇔有効化コピー・Behavior.toml⇔スキル実体の同期ペア追加。addf-lint.md セクション6の表も同時更新）
- `/addf-init`（コピーリスト変更: GUI スキルを無条件コピーから optional 配置に変更。lint ペア5への影響確認）
- `.claude/addf/guides/gui-test-setup.md` / `docs/test-scenarios/` の書式
- `/addf-migrate`（`machine` → `environments` 移行、既存プロジェクトの GUI スキルの optional 退避移行）
- `/addf-lint`（lint-toml.py の対象キー拡張。新スキーマの検証を足すか要検討）

## 未決事項（粗々ゆえ）

- 組み合わせタグの表記: `mac+web` 連結か、`host: mac` / `target: web` の2キー分離か
  （2キー分離のほうが lint しやすいが、シナリオ frontmatter が重くなる）
- web ドライバの実行基盤: Playwright 直叩き（Bash + npx）か、addfTools に薄いラッパースクリプトを置くか。
  リモート実行環境には Chromium がプリインストールされている前提を活かせるか
- レガシーシナリオ（frontmatter なし）の扱い: 警告付き実行か、明示宣言を必須にするか
- ios / android のプリミティブに「タップ・スワイプ」等の入力操作を含めるか（現行は撮影系のみ。
  入力まで広げるとインターフェースが倍化するため、本 Plan は撮影系に限定する案が有力）
- ダウンストリーム配布時の安全性: `enable = false` デフォルトの維持と、
  未オプトイン環境での挙動（SKIP 報告）が addf-init 配布物でも成立するかの確認（Feedback.md の観点）
- スキル実体化の同期トリガーの主体: `/addf-gui-test setup` サブコマンド新設か、`/addf-init` / `/addf-migrate` に
  同梱か、SessionStart フックで Behavior.toml と突き合わせて自動整合か（フック自動はオーナーの意図しない
  配置変更が起きうるため lint WARNING 留めが無難か）
- Unix 環境限定でシンボリックリンクを許すか: コピー一本に統一するほうが lint・ドキュメントが単純。
  リンクの利点（原本編集が即反映）は開発時のみで、ダウンストリームでは原本を編集しないため薄い

## 完了条件（暫定）

- 環境ごとに GUI テストをオプトインでき、未オプトイン環境ではシナリオが FAIL せず SKIP 報告される
- GUI 関連スキル・エージェント定義が `.claude/addf/optional/` に退避され、オプトイン時のみ発見パスに実体化される。
  無効時はスキルがコンテキストに載らず、Behavior.toml とスキル実体の不整合は lint が検出する
- シナリオが要求環境を宣言でき、実行側が現環境で満たせるものだけを実行する
- ドライバが差し替え可能で、mac（既存）と web（Playwright）の2実装が動作する。
  windows / linux / ios / android はスタブとして差し込み口が存在する
- `machine` 単一値の既存設定が後方互換で動き、`/addf-migrate` で新スキーマへ移行できる
- `bash .claude/addf/tests/run-all.sh` が通過する

## 関連

- Plan 0004（GUI テストのクロスプラットフォーム抽象化）— 本 Plan はその抽象を環境マトリクスへ拡張する
- Plan 0026（レビュー残課題バックログ）— `.gitignore` 残骸エントリの Low 指摘を本 Plan で解消する
- Plan 0021 / 0022 / 0024（同期 lint 機構）— 原本⇔有効化コピーの同期ペアはこの機構に追加する
- `.claude/addf/knowhow/ADDF/sync-lint-design.md` — 同期ペア追加時の作法
- `.claude/addf/guides/gui-test-setup.md` — セットアップガイド（要更新）
- Feedback.md「ダウンストリーム配布時の安全性」観点 — デフォルト無効・SKIP 設計の根拠
