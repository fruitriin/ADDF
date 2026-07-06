# 視覚テスト — Screenshot-based GUI testing toolchain（オプトイン）

> 概念単位の記録。実装がスキル/エージェント/フック/ファイルのどれであっても、
> 「GUI の視覚的検証」に関わるものをまとめている。

**オプトイン機能（デフォルト無効）**: GUI スキル一式は常設ではなく `.claude/addf/optional/` に原本が退避されており、
`addf-Behavior.toml` の `[gui-test] enable = true` に設定して
`sync-optional-skills.py apply` を実行した場合のみ `.claude/commands/` / `.claude/agents/` に有効化コピーが配置される。
ADDF 本体リポジトリでは現在 `enable = false`（無効）。

## 構成要素

| 種別 | 名前 | 役割 |
|---|---|---|
| スキル（オプトイン） | addf-gui-test | テストシナリオ（docs/test-scenarios/）の実行・結果判定。原本: .claude/addf/optional/commands/ |
| スキル（オプトイン） | addf-annotate-grid | PNG 画像にグリッド線・座標ラベルを描画（--divide / --every）。原本: .claude/addf/optional/commands/ |
| スキル（オプトイン） | addf-clip-image | PNG 画像の指定領域を切り出し（--rect / --grid-cell / --grid-range）。原本: .claude/addf/optional/commands/ |
| エージェント（オプトイン） | addf-ui-test-agent | GUI テスト専門エージェント（Sonnet、skills: gui-test/annotate-grid/clip-image。品質ゲート Stage 2 に参加可能）。原本: .claude/addf/optional/agents/ |
| ツール | .claude/addf/addfTools/sync-optional-skills.py | [gui-test] enable と有効化コピーの同期（check / apply。→ system-distribution と共有） |
| ツール | .claude/addf/addfTools/capture-window(.swift) | ウィンドウスクリーンショット撮影（macOS 15+、ScreenCaptureKit） |
| ツール | .claude/addf/addfTools/window-info(.swift) | ウィンドウ一覧・位置・サイズ取得（macOS、AXUIElement） |
| ツール | .claude/addf/addfTools/annotate-grid(.swift) | グリッド描画（macOS） |
| ツール | .claude/addf/addfTools/clip-image(.swift) | 画像切り出し（macOS） |
| ツール | .claude/addf/addfTools/check-screen-recording.sh | Screen Recording 権限チェック（--request で設定を開く） |
| ツール | .claude/addf/addfTools/build.sh | Swift ツール群のビルドスクリプト（ビルド後に checksums.sha256 を生成・更新する） |
| ツール | .claude/addf/addfTools/verify-checksums.sh + checksums.sha256 | コミット済みバイナリの SHA-256 照合＋allowlist ガード（Plan 0031）。ハッシュ計算のみでバイナリを実行しないため全 OS で動作。upstream で checksums 不在は ERROR（ビルド漏れ/削除ドリフト）、downstream 不在は明示 SKIP。repo_kind 判定は明示シグナル（lint-template-sync の detect_repo_kind() と同期契約） |
| 設定 | .claude/addf/Behavior.toml [gui-test] | enable（オプトインの真実源。デフォルト false）・machine（"mac" / "linux" / "windows"） |
| ガイド | .claude/addf/guides/gui-test-setup.md | セットアップ手順（オプトイン有効化を含む） |
| テスト | .claude/addf/tests/tools/test-tools.sh / test-optional-skills.sh | ツール疎通テスト（非 macOS はバイナリ実行を SKIP）とオプトイン同期のテスト |

## 設計思想

LLM のビジョン能力を活用した GUI テスト。スクリーンショットを撮影し、グリッド座標系で領域を特定し、視覚的に検証する。

**ワークフロー**: window-info → capture-window → annotate-grid → clip-image → LLM 判定

### オプトイン機構（Plan 0029 フェーズ1）

GUI テストは全プロジェクトが使う機能ではないため、常設をやめてオプトインに変更された。設計原則（.claude/addf/knowhow/ADDF/optional-skill-optin.md）:

- **原本が真実源**: `.claude/addf/optional/` の原本だけを編集する。有効化コピーは使い捨て
- **コピーは削除して作り直す**: apply は差分マージをしない。改変された有効化コピーは触らず WARNING（オーナー判断に委ねる）
- **シンボリックリンクではなくコピー**: Windows 対応のため
- 無効化（enable = false → apply）でコピーが撤去され、孤児コピーは addf-lint セクション10が検出する

### バイナリ検証（Plan 0031）

Swift ツールのビルド済みバイナリはリポジトリにコミットして配布される。改竄・ドリフト対策として build.sh が checksums.sha256 を生成し、verify-checksums.sh が実行前照合を提供する: checksums.sha256 の name 列を allowlist とし、記載のない実行可能ファイルの混入も検出する（攻撃者モデル対応）。照合はハッシュ計算のみでバイナリを実行しないため非 macOS でも動作し、test-binary-checksums.sh が run-all.sh から自動検証する。

Swift ネイティブツールで macOS に最適化。`gui-test.machine` でプラットフォームを選択する（"linux" / "windows" は未実装として報告終了）。フレームワークテストも非 macOS ではバイナリ実行を SKIP し、クロスプラットフォームの CI を妨げない。テストシナリオ（.claude/addf/tests/skills/ の GUI 系）にもオプトイン前提の注記が入っている。

スキル群は独立しても使える（annotate-grid 単体で画像に座標を付与する等）が、addf-gui-test が統合ワークフローを提供し、addf-ui-test-agent が品質ゲートに参加する形で完全なテストパイプラインになる。addf-ui-test-agent は「安定していれば投機的にまとめて実行、予期しない状態でステップ実行に切り替える」適応的実行モードを持つ。

画像検査のコツ（addf-clip-image に蓄積）: clip は annotated ではなく元画像から / --grid-range が最も使いやすい / clip → annotate → clip の再帰は2段階まで / 対象が見つからないときは grid 分割 → 各セル clip の走査。一時ファイルは `tmp/` に書き出す（`/tmp/` は使用禁止 — .claude/addf/knowhow/ADDF/pretooluse-block-with-rationale.md 参照）。

## 主要フロー

```
有効化（オプトイン）:
  addf-Behavior.toml [gui-test] enable = true に編集
    │
    ▼
  uv run --python 3.11 .claude/addf/addfTools/sync-optional-skills.py apply
  （uv が無ければ python3 で直接実行。Python 3.11+ が必要）
    │
    ▼
  .claude/addf/optional/ の原本 → .claude/commands/ / .claude/agents/ に有効化コピー配置

テスト実行（有効化後）:
  テストシナリオ (docs/test-scenarios/*.md)
    │
    ▼
  addf-gui-test / addf-ui-test-agent
    ├─ 1. Behavior.toml 確認（gui-test.enable? machine?）
    ├─ 2. Screen Recording 権限チェック
    ├─ 3. ツールビルド（必要なら build.sh）
    ├─ 4. テスト実行ループ
    │  ├─ アプリ起動 → window-info でウィンドウ検出
    │  ├─ capture-window でスクリーンショット → tmp/
    │  ├─ annotate-grid で座標系確立 → clip-image で注目領域切り出し
    │  └─ LLM で期待値との比較
    ├─ 5. クリーンアップ（テスト対象プロセスは必ず終了させる）
    └─ 6. 結果レポート（PASS/FAIL + スクリーンショット）
```

## 下流でのカスタマイズ

- `addf-Behavior.toml` で `gui-test.enable = true` に設定し `sync-optional-skills.py apply` を実行して有効化、`machine` でプラットフォーム指定
- `docs/test-scenarios/` にプロジェクト固有のテストシナリオを配置
- 品質ゲート Stage 2 に addf-ui-test-agent を追加可能（CLAUDE.repo.md の品質ゲート拡張で設定。GUI オプトイン有効時のみ）
- annotate-grid / clip-image は GUI テスト以外にも画像分析に使用可能

## 関連するシステム

- **配布・導入**: オプトイン機構（.claude/addf/optional/ + sync-optional-skills.py）は配布・導入システムと共有。addf-init は optional/ を無条件コピーし、addf-migrate は optional/ 変更時に apply を再実行する
- **品質ゲート**: addf-ui-test-agent が Stage 2 の品質検証チームに参加可能（GUI オプトイン有効時）。addf-lint セクション10がオプトイン同期（孤児コピー・enable の型）を検査。test-tools.sh の SKIP 設計は lint と同じ「配布時誤 ERROR 防止」の思想
- **セッション管理**: Behavior.toml で有効/無効を制御（context-reminder・speculation と同じ設定ファイルを共有）
