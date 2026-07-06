# 計画: テスト基盤整備 & addfTools リネーム

## 実装状況: 完了（2026-03-19、2026-06-11 遡及確認）

## 動機
フレームワークのスキル・フック・ツールにテストがない。品質を担保するテスト基盤を整備する。
併せて `addToolsSrc` を `addfTools` にリネームし addf- 命名規則に統一する。

## 設計

### 1. `addToolsSrc` → `addfTools` リネーム（実施済み）
- `.claude/addToolsSrc/` → `.claude/addf/tools/`
- build.sh 内のパス更新
- .claudeignore のバイナリパス更新
- settings.json の build.sh パス更新
- .claude/addf/guides/gui-test-setup.md の参照更新
- README.md / README.en.md の参照更新
- Swift バイナリ再ビルド

### 2. テストディレクトリ構成
```
.claude/addf/tests/
├── skills/           # スキルの自然言語テストシナリオ
├── hooks/            # フックの入力シミュレーションテスト
└── tools/            # addfTools のバイナリテスト
```

### 3. スキルテスト（自然言語シナリオ）
各スキルに対して「入力 → 手順 → 期待結果」を自然言語で記述。
テスト実行はスキルを実際に呼び出して結果を検証する。

対象スキル:
- addf-knowhow（引数なし / トピック指定）
- addf-knowhow-index（引数なし / reindex）
- addf-knowhow-filter（Plan パス指定）
- addf-experience
- addf-dev-loop（dry-run 的な検証）
- addf-annotate-grid（引数なし）
- addf-clip-image（引数なし）

### 4. フックテスト（シェルスクリプト）
フックに模擬 JSON を stdin で渡し、exit コード・stdout を検証。

対象:
- turn-reminder.sh（カウンター 0→1, 9→10, 14→15）
- reset-turn-count.sh（リセット確認）

### 5. ツールテスト（バイナリ疎通）
ビルド済みバイナリの基本動作を確認。

対象:
- window-info（ヘルプ or disabled 出力確認）
- capture-window（同上）
- annotate-grid（不正引数でエラー終了確認）
- clip-image（同上）

## 影響範囲
- `.claude/addToolsSrc/` → `.claude/addf/tools/`（リネーム済み）
- `.claude/addf/tests/`（新規作成）
- settings.json, .claudeignore, docs/, README 等の参照更新

## 実装完了状況
- リネーム完了、全参照更新・ビルド確認済み
- テスト基盤作成完了:
  - スキルテスト: 7件（自然言語シナリオ）
  - フックテスト: 2件（13アサーション、全 PASS）
  - ツールテスト: 1件（8アサーション、全 PASS）
  - テストランナー: run-all.sh（一括実行）
