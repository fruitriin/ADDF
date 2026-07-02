# 視覚テスト — Screenshot-based GUI testing toolchain

> 概念単位の記録。実装がスキル/エージェント/フック/ファイルのどれであっても、
> 「GUI の視覚的検証」に関わるものをまとめている。

## 構成要素

| 種別 | 名前 | 役割 |
|---|---|---|
| スキル | addf-gui-test | テストシナリオ（docs/test-scenarios/）の実行・結果判定 |
| スキル | addf-annotate-grid | PNG 画像にグリッド線・座標ラベルを描画（--divide / --every） |
| スキル | addf-clip-image | PNG 画像の指定領域を切り出し（--rect / --grid-cell / --grid-range） |
| エージェント | addf-ui-test-agent | GUI テスト専門エージェント（Sonnet、skills: gui-test/annotate-grid/clip-image。品質ゲート Stage 2 に参加可能） |
| ツール | .claude/addfTools/capture-window(.swift) | ウィンドウスクリーンショット撮影（macOS） |
| ツール | .claude/addfTools/window-info(.swift) | ウィンドウ一覧・位置・サイズ取得（macOS） |
| ツール | .claude/addfTools/annotate-grid(.swift) | グリッド描画（macOS） |
| ツール | .claude/addfTools/clip-image(.swift) | 画像切り出し（macOS） |
| ツール | .claude/addfTools/check-screen-recording.sh | Screen Recording 権限チェック |
| ツール | .claude/addfTools/build.sh | Swift ツール群のビルドスクリプト |
| 設定 | .claude/addf-Behavior.toml [gui-test] | enable（有効/無効）・machine（"mac" / "linux" / "windows"） |
| テスト | .claude/tests/tools/test-tools.sh | ツール疎通テスト（非 macOS 環境ではバイナリ実行テストを SKIP） |

## 設計思想

LLM のビジョン能力を活用した GUI テスト。スクリーンショットを撮影し、グリッド座標系で領域を特定し、視覚的に検証する。

**ワークフロー**: window-info → capture-window → annotate-grid → clip-image → LLM 判定

Swift ネイティブツールで macOS に最適化。`addf-Behavior.toml` の `gui-test.enable = true` で有効化し、`gui-test.machine` でプラットフォーム固有ツールを選択する（"linux" / "windows" は未実装として報告終了）。フレームワークテストも非 macOS ではバイナリ実行を SKIP し、クロスプラットフォームの CI を妨げない。

スキル群は独立しても使える（annotate-grid 単体で画像に座標を付与する等）が、addf-gui-test が統合ワークフローを提供し、addf-ui-test-agent が品質ゲートに参加する形で完全なテストパイプラインになる。addf-ui-test-agent は「安定していれば投機的にまとめて実行、予期しない状態でステップ実行に切り替える」適応的実行モードを持つ。

画像検査のコツ（addf-clip-image に蓄積）: clip は annotated ではなく元画像から / --grid-range が最も使いやすい / clip → annotate → clip の再帰は2段階まで / 対象が見つからないときは grid 分割 → 各セル clip の走査。一時ファイルは `tmp/` に書き出す（`/tmp/` は使用禁止 — docs/knowhow/ADDF/pretooluse-block-with-rationale.md 参照）。

## 主要フロー

```
テストシナリオ (docs/test-scenarios/*.md)
  │
  ▼
addf-gui-test / addf-ui-test-agent
  │
  ├─ 1. Behavior.toml 確認（gui-test.enable? machine?）
  ├─ 2. Screen Recording 権限チェック
  ├─ 3. ツールビルド（必要なら build.sh）
  │
  ├─ 4. テスト実行ループ
  │  ├─ アプリ起動
  │  ├─ window-info でウィンドウ検出
  │  ├─ capture-window でスクリーンショット → tmp/
  │  ├─ annotate-grid で座標系確立
  │  ├─ clip-image で注目領域切り出し
  │  └─ LLM で期待値との比較
  │
  ├─ 5. クリーンアップ（テスト対象プロセスは必ず終了させる）
  └─ 6. 結果レポート（PASS/FAIL + スクリーンショット）
```

## 下流でのカスタマイズ

- `addf-Behavior.toml` で `gui-test.enable = true` に設定して有効化、`machine` でプラットフォーム指定
- `docs/test-scenarios/` にプロジェクト固有のテストシナリオを配置
- 品質ゲート Stage 2 に addf-ui-test-agent を追加可能（CLAUDE.repo.md の品質ゲート拡張で設定）
- annotate-grid / clip-image は GUI テスト以外にも画像分析に使用可能

## 関連するシステム

- **品質ゲート**: addf-ui-test-agent が Stage 2 の品質検証チームに参加可能。test-tools.sh の SKIP 設計は lint と同じ「配布時誤 ERROR 防止」の思想
- **セッション管理**: Behavior.toml で有効/無効を制御（context-reminder と同じ設定ファイルを共有）
- **配布・導入**: addfTools/ は addf-init のコピー対象・addf-migrate の上書き対象
