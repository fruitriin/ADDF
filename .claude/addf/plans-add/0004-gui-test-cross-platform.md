# 計画: GUI テストのクロスプラットフォーム抽象化

## 実装状況: 完了（2026-03-18、2026-06-11 遡及確認）

## 動機
現在の GUI テスト機能は macOS（Swift/ScreenCaptureKit）専用。プラットフォーム設定と抽象インターフェースを導入し、将来の拡張に備える。

## 設計

### 1. `add-Behavier.toml` の拡張（ファイル名 typo: `Behavier` → `Behavior` のリネームも実施する）
```toml
[gui-test]
enable = false
machine = "mac"  # "mac" | "linux" | "windows"
```

### 2. 抽象インターフェース定義
スキル（`addf-gui-test.md`）がプラットフォームを意識せず使えるよう、以下の操作を抽象化:
- **window-info**: ウィンドウ一覧取得
- **capture-window**: スクリーンショット撮影
- **annotate-grid**: グリッド描画（プラットフォーム非依存、既存実装で対応可能）
- **clip-image**: 画像切り出し（プラットフォーム非依存、既存実装で対応可能）

### 3. プラットフォーム固有実装
- macOS: 既存の Swift 実装をそのまま使用
- Linux/Windows: 未実装（スタブまたはエラーメッセージ）

### 4. ドキュメント
- GUI テスト機能のセットアップ手順
- macOS での Screen Recording 権限の設定方法

## 影響範囲
- `.claude/addf/Behavior.toml`（旧 `add-Behavier.toml` からリネーム）
- `.claude/skills/addf-gui-test.md`（プラットフォーム判定ロジック追加）
- `.claude/skills/optional/addf-gui-test.md`（同上）
- `.claude/addf/tools/window-info.swift`, `capture-window.swift`（参照更新）
- `README.md`, `README.en.md`（ファイル名参照更新）
- `.claude/addf/guides/gui-test-setup.md`（新規作成）

## 実装完了状況
- 全項目を実施完了（2026-03-18）
- `add-Behavier.toml` → `addf-Behavior.toml` リネーム＋全参照更新
- `machine` 設定追加、プラットフォーム判定ロジック追加
- セットアップガイド作成、Swift バイナリ再ビルド成功
