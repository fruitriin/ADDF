# 計画: スキル品質向上

## 実装状況: 完了（2026-03-19、2026-06-11 遡及確認）

## 動機
一部のスキル定義が簡素すぎ、意図が伝わりにくい。スキル全体の品質・統一性を底上げする。

## 設計

### 1. `addf-experience.md` の充実化
現状は2行程度の簡素な記述。以下を追加:
- 明確な手順（Phase 構造）
- 検証対象の具体例
- エラーケースの対処

### 2. スキル description の統一性チェック
全スキルの frontmatter を確認し、以下を統一:
- description の粒度・文体
- user_invocable の正確性
- 引数の説明形式

### 3. スキル間の参照整合性
- スキルが参照するファイル・エージェントが全て存在するか確認
- 存在しない参照先があれば修正

## 影響範囲
- `.claude/commands/addf-experience.md`
- `.claude/commands/` 配下の各スキルファイル（軽微な修正）

## 実装結果

- [x] 1. `addf-experience.md` の充実化: 2行 → Phase 構造（スキャン→判定→修正→検証）、エラーケース対処、@メンション展開 knowhow への参照を追加
- [x] 2. description 統一性: `addf-dev-loop` の冗長な description を簡潔化、`addf-knowhow-index` の description に INDEX.addf.md / INDEX.md の使い分けを明記
- [x] 3. 参照整合性修正:
  - `addf-gui-test.md` に前提条件セクション追加（`docs/test-scenarios/` 不在時のエラーハンドリング）
  - `commands/optional/addf-gui-test.md`（重複）を削除
  - `addf-knowhow-index` を INDEX.addf.md 自動優先に対応
