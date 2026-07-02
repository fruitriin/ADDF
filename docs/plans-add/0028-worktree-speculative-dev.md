# Plan 0028: addf-dev の worktree ベース投機開発（粗々）

## 実装状況: 未着手

> **粗々の起票**: 設計の方向性と未決事項を出す段階。実装詳細は着手時に詰める。

## 目的

`/loop /addf-dev` が**アイドル**（ユーザー確認待ちで着手可能なタスクがない）になったとき、黙って止まる
のではなく、**依存関係のない直交概念を worktree で投機開発**し、統合ブランチで動作確認を一括して、
オーナーがまとめてレビュー・取捨選択できるようにする。

現状の addf-dev は「TODO から1タスク・逐次・現ブランチにコミット」。worktree は CLAUDE.md 並列実装方針で
「*1タスク内の* 並列サブタスク」向けに使われている。本 Plan はここを一段ずらし、
**アイドル時の *別々のタスク* を並列 worktree で投機する**方向に拡張する（既存 `speculative/` ブランチ・
unattended 哲学・Dashboard 資産の自然な延長）。

## 2層モデル（feature / integration）

オーナーの feature/release アナロジーをそのまま構造化する:

```
main（保護。オーナーがレビューしたものだけマージ）
 ├─ speculative/concept-A  ← worktree = feature ブランチ
 ├─ speculative/concept-B  ← worktree = feature ブランチ
 └─ speculative/concept-C  ← worktree = feature ブランチ
        ↓ 全 feature を1本に統合（スカッシュマージ）
 integration/loop-<日付>   ← ここで動作確認を「一括」
        ↓ Dashboard でオーナーがレビュー
   勝ち残りを main へ昇格
```

### Layer 1: feature worktree（投機）
- 直交概念ごとに `speculative/<concept>` ブランチの worktree。隔離・使い捨て・`.claude` 複製
  （CLAUDE.md 並列実装方針: worktree 起動後に `.claude` をコピー）
- worktree 隔離下は閾値-1段（失敗を捨てられる。既存ドクトリン）

### Layer 2: integration ブランチ（動作確認一括）
- 機能は**統合＋動作確認**でありリリースではない。名前は `integration/`（`release/` は誤解を招く）
- **各 feature を integration ブランチへスカッシュマージ**する。理由:
  - 1 feature = 1コミットになり、Dashboard で「何が入ったか」が一望でき、feature 単位の revert が楽
  - 投機の細かい試行錯誤コミットが統合履歴を汚さない
- 品質ゲートを **1回** 回すことで: (1) コストを N×→1× に償却、(2) feature 間の衝突（同じファイルを
  触っていた）を露見させる、(3) 単体では緑でも組み合わせて壊れる相互作用を捕まえる
- integration ブランチは**使い捨て・再生成可能**。main を汚さない

## 進行中 worktree 管理ドキュメント

複数 worktree を並行運用するため、状態を追える管理ドキュメントを持つ（案: `.claude/Worktrees.md`）。
- 記録内容（案）: worktree パス / `speculative/` ブランチ名 / 対象概念（元 Plan や backlog 項目）/
  状態（開発中・緑・赤・統合済み・放棄）/ 最終更新
- 位置づけ: 実行時生成の状態ファイル → `.gitignore` 対象（Dashboard.md / Questions.md 実行時分と同様）。
  Dashboard.md からサマリを参照する導線を作る
- **打ち切った投機を silent に消さない**: 放棄・衝突で待機した feature も管理ドキュメントに残し、
  Dashboard で報告する（「全部やった」に見える silent truncation を避ける）
- 掃除: マージ済み/放棄 worktree の削除タイミングを定義（worktree は高コスト＝200-500ms＋ディスク）

## 投機実行の上限（プロジェクトごと）

同時 worktree 数などの投機上限を **プロジェクトごとに設定可能**にする。
- 置き場所（案）: `addf-Behavior.toml` に `[speculation]` セクションを追加
  （既存の `[context-reminder]` と同じ「プロジェクト固有の振る舞い設定」の枠組み）
  ```toml
  [speculation]
  enable = false          # true でアイドル時投機を有効化（デフォルト無効＝オプトイン）
  max_worktrees = 3       # 同時 speculative worktree 上限
  # 直交概念の選定元の優先順位・新規発明の可否など、必要に応じ追加
  ```
- 上限に達したら新規投機を止め、その旨を管理ドキュメント／Dashboard に記録する

## トリガーとモード整合

- **アイドル判定**: TODO に未着手なし / 残る未着手が全て確認待ち（Questions 投下済み）
- **投機は unattended の領分**: 「確認待ちで着手不能→黙らず投機」はまさに unattended 哲学。
  relaxed の「止まって聞く」と衝突しうるため、`[speculation].enable`（または responsiveness: unattended）で
  明示オプトインさせる
- `speculative/` ブランチは既存（unattended 閾値割れ隔離）と統一。「本流に自動マージしない」を継承
- **昇格は計画レビュー文化の延長**: 「投機実装をまとめてレビューして勝ち残りを選ぶ」。Dashboard が
  レビュー面（不在中に作った独立機能一覧＋integration 動作確認結果＋衝突で待機したもの）

## 直交概念の選定（設計の急所・要検討）

worktree が衝突を防ぐのは作業が本当に独立しているときだけ。
- **選定元の優先順位**: (1) Plan 0026 残課題バックログ（分解済みで独立項目多い）→ (2) Questions.md 保留項目
  → (3) オーナー常設リクエスト「品質向上計画の追加」。**新規概念の発明は最終手段**（望まれない投機を避ける）
- **直交性ヒューリスティック**: 「触るであろうファイル集合が重ならない」を Plan から見積もる。予測が外れたら
  integration の衝突で回収（統合は直交性予測の答え合わせの場でもある）

## 未決事項（粗々ゆえ）

- 品質ゲート Stage 分割: Stage1（ビルド/Lint/テスト）は各 feature、Stage2（レビューエージェント）は
  integration 一括、のハイブリッドが落とし所か？（赤の原因切り分けは feature 単位が楽）
- 昇格の粒度: cherry-pick か merge か、feature 単位か。main への反映は結局オーナー承認必須
- 管理ドキュメントを commit するか gitignore か（実行時状態なら gitignore だが、
  クラッシュ復帰時に worktree を辿れる価値もある → 要検討）
- `addf-dev.md` のステップにどう織り込むか（アイドル分岐を新ステップ化 / 別スキル `addf-speculate` に分離）
- worktree の掃除主体（loop 次サイクル / セッション終了フック / 明示コマンド）

## 完了条件（暫定）

- アイドル時に直交概念を worktree で投機開発し、integration ブランチでスカッシュ統合＋動作確認一括ができる
- 進行中 worktree が管理ドキュメントで追え、放棄/衝突も silent にならず Dashboard に出る
- 投機上限が `addf-Behavior.toml` でプロジェクトごとに設定でき、上限到達が記録される
- 投機は本流に自動マージされず、オーナーが Dashboard から勝ち残りを昇格できる

## 関連

- CLAUDE.md「並列実装方針」— worktree 利用ルール。本 Plan はこれを「タスク間並列」へ拡張
- CLAUDE.md「迷ったときの作法（7割共有原則）」— 3軸・unattended・speculative/ ブランチ・Dashboard
- Plan 0026（残課題バックログ）— 直交概念の主要な選定元
- `docs/knowhow/ADDF/` — worktree 起動時の `.claude` 複製など実装知見の蓄積先
