# 品質ゲート — Multi-agent quality assurance

> 概念単位の記録。実装がスキル/エージェント/フック/ファイルのどれであっても、
> 「コード品質・フレームワーク整合性の検証・保証」に関わるものをまとめている。

## 構成要素

| 種別 | 名前 | 役割 |
|---|---|---|
| エージェント | addf-code-review-agent | コード品質・可読性・ベストプラクティスのレビュー（Sonnet）。5ペルソナの視点ずらしレビュー対応 |
| エージェント | addf-security-review-agent | ペネトレーションテスター人格で脆弱性検出・修正案提示（Sonnet。実装はしない） |
| エージェント | addf-contribution-agent | ADDF / プロジェクト固有コードの識別、分離パターン違反検出、アップストリーム貢献候補検出（Sonnet） |
| スキル | addf-lint | フレームワーク整合性チェック（8項目: JSON構文・hooks権限・frontmatter・Behavior.toml・INDEX整合・テンプレート同期・knowhow鮮度・knowhow双方向リンク） |
| テスト | .claude/tests/run-all.sh | フレームワーク自動テスト（フック3本・ツール2本。スキルシナリオ8本は手動）。非 macOS ではバイナリ実行テストを SKIP |
| ツール | .claude/addfTools/lint-json.py / lint-frontmatter.py / lint-toml.py | 構文 Lint スクリプト（uv run --python 3.11 で実行） |
| ツール | .claude/addfTools/lint-template-sync.py | テンプレート同期チェック（6ペア）。exit 0=全一致 / 1=ERROR / 2=WARNING のみ |

## 設計思想

ADDF の第三の柱。「人間がレビューするのは計画の方向性、コード品質は AI が担保する」という CONTRIBUTING.md の方針を実装する。

2段階の品質ゲート:
- **Stage 1（ゲートキーパー）**: ビルド・Lint・テスト。失敗したら実装に差し戻し
- **Stage 2（品質検証チーム）**: code-review, security-review, contribution-agent を並列実行

重要度による対応方針:
- **Critical/High**: 必ずそのフェーズ内で修正（先送り禁止）
- **Medium**: 原則修正、先送りは独立計画へ
- **Low/Info**: 計画に記録
- **バグ分離**: 現在の Plan と関心事が異なるバグは修正せず新 Plan を起こす

### 視点ずらしレビュー（ペルソナ並列）— Plan 0020

実装者と同じモデルのレビュアーは実装者と同じ盲点を持ちやすい。ペルソナはこの盲点をずらす装置。addf-code-review-agent は起動プロンプトの「ペルソナ: <名前>」指定で単一視点に固定される:

| ペルソナ | 視点 |
|---|---|
| skeptic | 実装者の暗黙の前提を全て疑う |
| attacker | コードロジックの穴を壊す目的で読む（システムレベルは security-review-agent の担当） |
| newcomer | 初見で意図が読み取れない箇所を指摘 |
| maintainer | 半年後の変更容易性・依存の罠・テストの抜け |
| domain-skeptic | Plan と実装の乖離・要件の読み違え |

発動条件: 通常タスクは単体（ペルソナなし）。マイルストーン・リリース直前・unattended 自走時は3体並列、`mode: critical` 宣言時は5体並列。集約ルール: 同一箇所・同一原因は1件にまとめてペルソナを列挙し、**2ペルソナ以上が独立に指摘した項目は重要度を1段上げる**（コンセンサス補正）。

### テンプレート同期 lint — Plan 0021/0022/0024

「意思で覚えず機械化する」。同期ファイルペアのドリフトを決定的スクリプトで検出し、解釈と修復はエージェントが行う:

| ペア | 検証内容 | 重要度 |
|---|---|---|
| 1. ProgressTemplate.addf.md ⇔ Progress.md | 運用ルールのテキスト包含 | ERROR |
| 2. ProgressTemplate.addf.md ⇔ ProgressTemplate.md | 運用ルールの正規化比較 | WARNING |
| 3. CLAUDE.md ⇔ AGENTS.md | ブートシーケンス手順番号の対応 | WARNING |
| 4. CLAUDE.md ⇔ docs/guides/development-process.md | ブートシーケンス概要の手順番号 | WARNING |
| 5. CLAUDE.md ⇔ addf-init.md コピーリスト | 参照ファイルのカバレッジ（.gitignore ADDF ブロック含む） | WARNING |
| 6. TODO ⇔ Plan の `## 実装状況:` ヘッダ | 状態の矛盾・参照切れ・登録漏れ・表記ゆれヘッダ検出 | WARNING |

ペア2〜6はダウンストリームで対象ファイルが無ければ SKIP（欠如はドリフトではない — 配布時誤 ERROR の防止）。WARNING には git log の最終更新日ヒントが併記され、どちらを正とするかはエージェントが文脈で判断する。ペア6により TODO の状態表記は「信用ベース」で扱える（docs/knowhow/ADDF/plan-status-drift-check.md）。新たな同期ペアが生まれたら lint と addf-lint.md セクション6の表を同時更新する（Feedback.md 記録済み）。

## 主要フロー

```
タスク実装完了
  │
  ▼
Stage 1: ビルド検証（ゲートキーパー）
  ├─ bash .claude/tests/run-all.sh
  ├─ プロジェクト固有の build/lint/test
  └─ 失敗 → 実装に差し戻し
  │
  ▼（Stage 1 通過後）
Stage 2: 品質検証チーム（並列起動）
  ├─ addf-code-review-agent ────┐  通常: 単体
  │   （条件により3〜5ペルソナ並列） │  集約: コンセンサス補正
  ├─ addf-security-review-agent ─┤─ フィードバック集約
  ├─ addf-contribution-agent ───┤
  └─ addf-ui-test-agent（GUI時） ┘
  │
  ▼
指摘対応
  ├─ Critical/High → 即修正 → Stage 1 再実行
  ├─ Medium → 修正 or 独立計画
  ├─ Low/Info → 計画に記録
  └─ 関心事の異なるバグ → 新 Plan に分離
```

## 下流でのカスタマイズ

- Stage 2 の品質検証チームの構成を CLAUDE.repo.md で変更可能（「品質ゲート拡張」セクション）
- addf-ui-test-agent を追加して GUI テストを品質ゲートに組み込める（オプション）
- addf-contribution-agent はダウンストリームでは分離パターン違反と ADDF への還元候補を検出する
- lint-template-sync.py はダウンストリームでも動作する（ADDF 固有ペアは SKIP、ペア1は ProgressTemplate.md を正として比較）
- ペルソナ並列の発動条件（`mode: critical` 等）は Plan フロントマターで宣言

## 関連するシステム

- **計画駆動**: Progress.md の品質検証フローが品質ゲートを起動する。unattended モード（/addf-mode）がペルソナ並列の発動条件になる
- **ノウハウ蓄積**: レビューで得た知見が knowhow に、差し戻しは .exp.md「分かれ道の目印」に蓄積される。addf-lint の項目5・7・8が knowhow の整合・鮮度・リンクを検査
- **視覚テスト**: addf-ui-test-agent が Stage 2 に参加可能
- **配布・導入**: addf-lint と run-all.sh は配布物の品質保証でもある（SKIP 設計はダウンストリーム配布前提）
