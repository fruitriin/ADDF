# Plan 0029: GUI テストの環境マトリクス化（環境別オプトイン・差し替え・組み合わせ）

## 実装状況: 未着手

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

- 配置規約（案）: `.claude/addfTools/drivers/<driver名>/` に環境固有実装を置き、
  環境非依存ツール（annotate-grid / clip-image）は現行の場所のまま共用する
- 本 Plan で**実装まで持つのは mac（既存）と web（Playwright）の2ドライバ**とし、
  windows / linux / ios / android は「インターフェース準拠のスタブ＋SKIP 報告」まで
  （ダウンストリームや後続 Plan が差し込める形を先に作る）

### 5. スキル・エージェント・ドキュメントの追随

- `.claude/commands/addf-gui-test.md`: 手順2のプラットフォーム判定を「環境タグ解決 → シナリオフィルタ →
  ドライバ選択」に書き換える
- `.claude/agents/addf-ui-test-agent.md`: ツール一覧をドライバ抽象前提の記述に更新する
- `docs/guides/gui-test-setup.md`: 「現在 macOS のみ対応」を環境マトリクス表に更新し、
  環境ごとのセットアップ手順（web: Playwright、ios: Xcode/simctl 等）を追記する
- `docs/test-scenarios/README.md`（あれば）: frontmatter 書式を記載する

## 影響範囲

- `.claude/addf-Behavior.toml`（スキーマ拡張・後方互換）
- `.claude/commands/addf-gui-test.md` / `.claude/agents/addf-ui-test-agent.md`
- `.claude/addfTools/`（drivers/ ディレクトリ導入、web ドライバ新規）
- `docs/guides/gui-test-setup.md` / `docs/test-scenarios/` の書式
- `/addf-migrate`（`machine` → `environments` 移行）
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

## 完了条件（暫定）

- 環境ごとに GUI テストをオプトインでき、未オプトイン環境ではシナリオが FAIL せず SKIP 報告される
- シナリオが要求環境を宣言でき、実行側が現環境で満たせるものだけを実行する
- ドライバが差し替え可能で、mac（既存）と web（Playwright）の2実装が動作する。
  windows / linux / ios / android はスタブとして差し込み口が存在する
- `machine` 単一値の既存設定が後方互換で動き、`/addf-migrate` で新スキーマへ移行できる
- `bash .claude/tests/run-all.sh` が通過する

## 関連

- Plan 0004（GUI テストのクロスプラットフォーム抽象化）— 本 Plan はその抽象を環境マトリクスへ拡張する
- `docs/guides/gui-test-setup.md` — セットアップガイド（要更新）
- Feedback.md「ダウンストリーム配布時の安全性」観点 — デフォルト無効・SKIP 設計の根拠
