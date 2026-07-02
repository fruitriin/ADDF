# フェーズ進行スキル一覧

> 毎回の実行時に全スキルをスキャンして自動生成。対象リストは決め打ちしない。
> 検出基準: Phase/Step 番号付き構造、または3ステップ以上の手順フローを持つスキル。
> 生成日: 2026-07-02

## 検出結果: 16本（17本中）

| スキル | フェーズ数 | 概要 |
|---|---|---|
| addf-dev | 5 steps | コンテキスト読込→タスク選択→実装（日記・閾値割れ対応込み）→完了処理→ループ |
| addf-init | 4+ phases ×3経路 + check | 状態確認→情報収集→干渉チェック→導入前レビュー→コピー&マージ→完了 |
| addf-migrate | 6 phases | 状態確認→最新取得→差分算出→プレビュー→適用→完了（lock 更新） |
| addf-overview | 8 steps (full) + 4 steps (patch) | 経験読込→データ収集→フロー検出→システム発見→生成→経験記録→.lock→報告 |
| addf-release | 4 steps | プロジェクト種別判定→手順ロード→実行→経験更新 |
| addf-permission-audit | 11 steps | ノウハウ読込→種別判定→権限収集→分類→配置→出力→構文検証→レビュー→適用→確認 |
| addf-lint | 8 checks | JSON構文→hooks権限→frontmatter→TOML→INDEX整合→テンプレート同期→knowhow鮮度→双方向リンク |
| addf-knowhow | 4 phases | 調査→記録→自己ブラッシュアップ→分かれ道の目印の記録提案 |
| addf-knowhow-filter | 5 steps | Plan読込→knowhow走査→関連判定→結果出力→（該当なし報告） |
| addf-knowhow-revise | 4 steps | 対象特定→再検証（妥当/訂正/superseded/retired）→訂正履歴→reindex・報告 |
| addf-knowhow-network | 5 steps | 関連性抽出→関連セクション生成→双方向リンク担保→ハブサマリ→報告 |
| addf-experience | 4 phases | スキャン→判定→修正→検証 |
| addf-gui-test | 7 steps | シナリオ読込→Behavior確認→前提条件→手順実行→期待結果比較→クリーンアップ→レポート |
| addf-annotate-grid | 5 steps | 引数解析→ツールビルド→グリッド描画→出力→次ステップ案内 |
| addf-clip-image | 5 steps | 引数解析→ツールビルド→領域切出し→出力→確認 |
| addf-mode | 3 steps（引数あり時） | 引数解釈→CLAUDE.local.md 更新→影響の要約表示 |

**非該当**: addf-knowhow-index（参照 or reindex の2モード切替のみ。構造化フェーズなし）

---

## addf-dev

> TODO.md から未実施タスクを1つ選んで実装・品質検証・コミットまで完遂する。

1. コンテキスト読み込み（Feedback → TODO → Progress）
2. タスク選択（優先1: 複利効果（ブロッカー解消・インフラ整備）/ 優先2: 若番）
3. 実装（CLAUDE.md ブートシーケンス + 2段階品質ゲート。日記を書く。閾値割れは relaxed: Questions.md へ / unattended: speculative/ で投機続行 / worktree 下は閾値1段下げ可）
4. 完了処理（Progress 運用ルールのステップ 9〜15: ノウハウ蓄積→フィードバック記録→アーカイブとコミット）
5. ループ継続（/loop が次サイクルを自動スケジュール）

---

## addf-init

> ADDF プロジェクトの初期セットアップまたは構造検証を行う。

**外部起動（既存プロジェクト導入）**: URL 検証（https:// のみ）→ tmp クローン → 既存ファイルから自動推定 → init モード Phase 1 へ
**init モード**:
- Phase 1: 状態確認（lock 有無で導入済み / Template 経由 / 既存プロジェクト / 新規を判別）
- Phase 2: セットアップ情報収集（外部起動: 自動推定+確認 / Template: 対話）
- Phase 2.5: 干渉チェック（競合なし / マージ必要 / 要確認 / 新規作成に分類）
- Phase 2.7: 導入前レビュー（hooks・権限・CLAUDE.md への影響を明示して確認）
- Phase 3: ファイルコピー & マージ（カテゴリ1: 無条件コピー / 2: インテリジェントマージ / 3: プロジェクト固有生成。lock は ref = クローン元タグで生成）
- Phase 4: 完了レポート・tmp 削除
**check モード**: 必須ファイル（Questions.md 含む）→ @メンション解決 → TODO⇔plans 整合 → lock 妥当性（ref 形式・旧形式は WARNING）→ AGENTS.md の5項目

---

## addf-migrate

> ADDF フレームワークを最新版にアップグレードする。

- Phase 1: 状態確認（lock の ref 読込。旧形式 commit は v<version> タグに読み替え。git clean・URL 検証）
- Phase 2: 最新版フェッチ（ADDF リポジトリクローン）
- Phase 3: 差分算出（対象: addf- 系・.claude 配下・guides・knowhow/ADDF / 対象外: Progress・Feedback・.exp.md・CLAUDE.repo.md 等）
- Phase 4: 変更プレビュー（カテゴリ別 + CHANGELOG 表示 → 確認）
- Phase 5: 適用（settings.json ユニオンマージ、addf- ファイル上書き、CLAUDE.md はテンプレート部分のみ、.exp.md リネーム案内）
- Phase 6: 完了（lock 更新（ref = v<new-version>）、tmp 削除、サマリ報告）

---

## addf-overview

> エコシステム概要ドキュメントの生成。

**full モード**:
- Step 0: 前回経験読み込み（.exp.md）
- Step 1: 全データ収集（A: 構造 / B: スキル全件 / C: エージェント / D: フック / E: 主要ファイル / F: コミット情報）
- Step 2: フェーズフロー自動検出
- Step 3: 概念システム探索的発見（クラスタリング→命名→前回比較→残余チェック）
- Step 4: ドキュメント生成（INDEX / system-* / phase-flows / interactions / claude-md-deps）
- Step 5: 経験記録（.exp.md）
- Step 6: .lock 更新（HASH|COMMIT_MSG|DATE）
- Step 7: 完了報告

**patch モード**:
- P1: .lock diff 取得
- P2: システムマッピング（.exp.md の分類に基づく。.exp.md 不在なら full を要求）
- P3: 影響システムのみ再生成
- P4: 経験記録 + .lock 更新 + 完了報告

---

## addf-release

> プロジェクトのリリースを実行する。

1. プロジェクト種別判定（CLAUDE.repo.md の「ADDF 開発プロジェクト」宣言 → upstream / それ以外 → downstream）
2. リリース手順ロード（upstream: ADDF-Release.addf.md / downstream: .exp.md or 対話的に戦略構築）
3. リリース手順実行
4. 経験更新

---

## addf-permission-audit

> セッション中の権限要求を3パターンに分類し settings に配置提案する。

1. ノウハウ読み込み（permission-settings-pattern.md）
2. プロジェクト種別判定
3. 現在の権限設定読み込み
4. セッション中の権限要求収集
5. 分類（アップストリーム / ダウンストリーム / 汎用）
6. 配置先決定（プロジェクト種別 × パターンのマトリクス）
7. 出力生成
8. 構文チェック（`:*` 非推奨 → ` *`）
9. コントリビューションレビュー（addf-contribution-agent で分離パターン検証）
10. apply モード（オプション）
11. ユーザー確認（承認後のみコミット）

---

## addf-lint

> フレームワーク整合性チェック（8項目）。

1. JSON 構文チェック（lint-json.py）
2. Hooks 実行権限チェック（.claude/hooks/*.sh）
3. スキル frontmatter チェック（lint-frontmatter.py: name, description）
4. addf-Behavior.toml 構文チェック（lint-toml.py）
5. Knowhow INDEX 整合性チェック（INDEX ⇔ 実ファイルの相互存在）
6. テンプレート同期チェック（lint-template-sync.py: 6ペア。exit 0/1/2 = 一致/ERROR/WARNING）
7. Knowhow 鮮度チェック（フロントマター有無・🔴 stale・depends_on 切れ → WARNING 止まり）
8. Knowhow 双方向リンクチェック（リンク切れ WARNING・片方向 INFO → /addf-knowhow-network 案内）

---

## addf-knowhow

> 実装知見を記録する。

- Phase 1: 調査（既存 knowhow 全読み、重複は追記・統合優先）
- Phase 2: 記録（フロントマター必須: created / last_verified / depends_on / status。deprecated は使わない）
- Phase 3: 自己ブラッシュアップ（正確性・完全性・簡潔性・実用性の4観点で見直し）
- Phase 4: 分かれ道の目印の記録提案（差し戻し・Critical指摘・やり直し・軌道修正があれば .exp.md 🔀 へ。[計画で防げた] / [作って分かった] を判定。目印ゼロは健全でありうる）

---

## addf-knowhow-filter

> Plan に関連するノウハウだけをフィルタリングして返す。

1. Plan ファイル読み込み
2. docs/knowhow/ 全走査（INDEX・CLAUDE.md 除く）
3. 関連度判定（技術領域・ハマりポイント・アーキテクチャ影響。タイトルで推測せず本文で判断）
4. 結果出力（パス・要約・関連理由）
5. 該当なしなら「関連するノウハウはありません」

---

## addf-knowhow-revise

> 鮮度低下したノウハウを意味的に再検証・訂正する。

1. 対象特定（INDEX の 🔴 stale / needs-review。引数でファイル指定可）
2. 再検証（依存先の現状を読み直し、妥当 → last_verified 更新 / 部分的誤り → 訂正 / 後継あり → superseded / 参照不要 → retired）
3. 訂正履歴の記録（## 訂正履歴 に日付・誤り→訂正・根拠）
4. 完了処理（reindex 実行 → 件数報告）

---

## addf-knowhow-network

> knowhow 記事同士を相互リンクし wiki として育てる。

1. 関連性の抽出（概念・キーワード・depends_on から記事間の関連を推定）
2. 「## 関連ノウハウ」セクションの生成・更新（📜 Superseded / Retired プレフィックス付き）
3. 双方向リンクの担保（retired への片方向は例外、superseded → 後継は双方向必須）
4. ハブサマリ（INDEX 末尾に被リンク数トップ3〜5 — revise の優先対象）
5. 完了報告（追加リンク数・双方向欠落の修正件数）

---

## addf-experience

> .exp.md の @メンション書式を検証・修正する。

- Phase 1: スキャン（全 .claude/commands/ ファイルの .exp.md 参照行）
- Phase 2: 判定（正常 / 要修正（クオート内） / 例外（意図的リテラル））
- Phase 3: 修正（クオート除去 + 一覧報告）
- Phase 4: 検証（再スキャンで意図しない変更がないか確認）

---

## addf-gui-test

> GUI テストシナリオを実行する。

1. シナリオ引数確認（なしなら一覧表示）
2. Behavior.toml 確認（gui-test.enable / machine — 非 mac は未実装として終了）
3. 前提条件確認（ツールビルド状態 → 必要なら build.sh）
4. シナリオ手順の実行（一時ファイルは tmp/ へ）
5. 期待結果との比較
6. クリーンアップ（テスト対象プロセスの終了）
7. 結果レポート（成功/失敗 + 詳細）

---

## addf-annotate-grid / addf-clip-image

> 画像にグリッド描画 / 画像の領域切り出し。

共通フロー:
1. 引数解析（画像パス・オプション。なしなら使い方表示）
2. ツールビルド確認（未ビルドなら build.sh）
3. 出力パス決定（省略時 tmp/annotated-* / tmp/clip-*）
4. 処理実行（annotate: --divide/--every、clip: --rect/--grid-cell/--grid-range）
5. 結果報告（Read で画像表示。annotate は clip への連携を案内）

---

## addf-mode

> 「迷ったときの作法」3軸モードの切替（軽量フロー）。

引数あり時:
1. 引数解釈（trust / responsiveness / image_clarity の値 + --notify / --dashboard フラグ）
2. CLAUDE.local.md の「# ADDF モード」セクションを更新（他セクションは触らない）
3. 変更後モードと判断への影響（閾値・閾値割れ時の挙動）を一行要約

引数なし時: 現在のモード表示（セクションが無ければデフォルトを表示）。
Plan フロントマターの宣言がセッション設定より優先される。
