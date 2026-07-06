# システム間相互作用

> 生成日: 2026-07-05
> 7つの概念システム間の相互作用をアスキーアートで表現。

## 1. 全システム関係図

```
┌────────────────────────────────────────────────────────────────────┐
│                        ADDF エコシステム                              │
│                                                                    │
│  ┌────────────────┐   ブート起点    ┌────────────────┐              │
│  │  セッション管理   │──────────────▶│    計画駆動      │              │
│  │  (session)      │               │   (planning)   │              │
│  │ CLAUDE.md/hooks │  モード保存先   │ TODO/Plans     │              │
│  │ context-reminder│◀──────────────│ Progress(日記)  │              │
│  │ Behavior.toml   │ (CLAUDE.local) │ Questions/     │              │
│  │ settings        │               │ Dashboard      │              │
│  └───────┬────────┘               │ addf-dev/mode  │              │
│          │                        └───┬───────┬────┘              │
│    棚卸し促し                          │       │ アイドル検出        │
│    (turn 10/15 +                完了時記録/    │ ([speculation]     │
│     実測 180k 超過)              ブート時参照   │  enable 時)        │
│          │                            │       ▼                   │
│          ▼                            │  ┌────────────────┐       │
│  ┌────────────────┐                   │  │   投機開発       │       │
│  │  ノウハウ蓄積     │◀──worktree/統合──┼──│ (speculation)  │       │
│  │  (knowhow)      │   設計知見        │  │ addf-speculate │       │
│  │ knowhow/ 鮮度   │                   │  │ speculate-*.py │       │
│  │ revise/network  │                   │  │ Worktrees.md   │       │
│  │ .exp.md 🔀      │                   │  │ 2層ブランチ      │       │
│  └───────┬────────┘                   │  └───────┬────────┘       │
│          │ 知見蓄積 ▲                  ▼          │ Stage 1/2      │
│          ▼          │           ┌────────────────▼─┐              │
│  分かれ道の目印 ──────┴────────── │   品質ゲート        │              │
│          INDEX/鮮度/リンク検査 ──▶│  (quality)        │              │
│                                 │ review agents     │              │
│                                 │ (5ペルソナ)         │              │
│                                 │ addf-lint(11)     │              │
│                                 │ sync-lint 6ペア    │              │
│                                 └──────┬───────────┘              │
│                                        │ Stage 2 参加（オプトイン時）  │
│  ┌────────────────┐              ┌────▼────────────┐              │
│  │   配布・導入      │ オプトイン機構 │  視覚テスト        │              │
│  │ (distribution)  │◀────────────│ (visual-test)   │              │
│  │ init/migrate    │  optional/ + │ [オプトイン]      │              │
│  │ release/overview│  sync-       │ gui-test        │              │
│  │ lock(ref形式)   │  optional-   │ addfTools(Swift)│              │
│  │ 部分導入正規化    │  skills.py   │ ui-test-agent   │              │
│  └───────▲────────┘              └─────────────────┘              │
│          │ 整合性検証・SKIP 設計・明示シグナル種別判定（配布安全性）        │
│          └──────── addf-lint / run-all.sh ─────────────────────────│
└────────────────────────────────────────────────────────────────────┘
```

## 2. addf-dev の全フェーズフロー図

```
/addf-dev 起動（/loop 1h /addf-dev で自律実行）
│
▼
┌─────────────────────────────┐
│ Step 1: コンテキスト読み込み    │
│ Feedback.md → TODO.md →     │
│ Progress.md（日記の末尾3件で   │
│ 前任者の文脈を引き継ぐ）        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│ Step 2: タスク選択                        │
│ 優先1: 複利効果（ブロッカー解消・            │
│ インフラ整備） 優先2: 若番                  │
│                                          │
│ アイドル（着手可能タスクなし）?              │
│ ├─ [speculation].enable = true           │
│ │   → /addf-speculate 1サイクル ──────────┼──▶ 図5 投機サイクルへ
│ │     （終了後 Step 4 完了処理に合流）       │
│ └─ false → オーナーに確認                  │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Step 3: knowhow 参照         │
│ addf-knowhow-agent (Haiku)  │
│ ├─ superseded → 後継に差替え  │
│ └─ stale → 鮮度低下を注記     │
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ Step 4: 実装                              │
│ Progress.md にチェックリスト                │
│ サブタスク単位で実装 + 日記を書く            │
│ 並列可能なら git worktree（.claude コピー）  │
│                                           │
│ 確信度 < 閾値（デフォルト7割）?              │
│ ├─ interactive: 即時質問                   │
│ ├─ relaxed: Questions.md に置き別タスクへ ──┼──▶ Step 2 へ戻る
│ └─ unattended: speculative/ で投機続行     │
│    （Dashboard.md に差分まとめ）             │
│ checkpoint/<phase>-<N> / alt/ 分岐可       │
└──────────┬───────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ Step 5: 品質検証                              │
│                                              │
│ Stage 1: ビルド検証 ◀──── 失敗時ループ         │
│ ├─ bash .claude/addf/tests/run-all.sh             │
│ └─ プロジェクト固有 build/lint/test            │
│         │                                     │
│         ▼ (通過)                               │
│ Stage 2: 品質検証チーム（並列）                  │
│ ├─ addf-code-review-agent ──┐                │
│ │   通常: 単体 / マイルストーン・ │                │
│ │   unattended: 3体 / critical: 5体並列       │
│ ├─ addf-security-review ────┤─ 集約           │
│ └─ addf-contribution ───────┘ (コンセンサス補正)│
│         │                                     │
│ Critical/High → 修正 → Stage 1 再実行         │
│ 関心事の異なるバグ → 新 Plan に分離             │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Step 6: 完了処理              │
│ ├─ Plan に実装状況ヘッダ反映   │
│ ├─ /addf-knowhow 記録（3観点）│
│ │   └─ 分かれ道の目印を提案    │
│ ├─ Feedback.md 更新          │
│ ├─ Progress.md を日記ごと     │
│ │   Progresses/ にアーカイブ  │
│ └─ コミット                   │
└──────────┬──────────────────┘
           │
           ▼
  /loop 時: 次のタスクへ（次の代の自分が日記から再開）
```

## 3. 品質ゲートフロー図

```
実装完了
│
▼
┌───────────────────────────────────┐
│ Stage 1: ゲートキーパー             │
│                                    │
│ bash .claude/addf/tests/run-all.sh     │
│ （フック3 + ツール11。非 macOS は   │
│   バイナリ実行 SKIP）               │
│ + プロジェクト固有 build/lint/test   │
│ + /addf-lint（11項目・sync 6ペア）  │
│                                    │
│ ┌──────┐    ┌──────┐             │
│ │ PASS │    │ FAIL │──▶ 差し戻し  │
│ └──┬───┘    └──────┘    (修正後   │
│    │                     再実行)   │
└────┼──────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────┐
│ Stage 2: 品質検証チーム（並列起動）             │
│                                             │
│ ┌──────────────────┐  ┌────────────────┐  │
│ │ code-review      │  │ security-review│  │
│ │ (Sonnet)         │  │ (Sonnet)       │  │
│ │ 通常: 単体         │  │ ペネトレーション │  │
│ │ 発動条件により      │  │ テスター人格    │  │
│ │ ペルソナ並列:      │  │ 脆弱性検出・    │  │
│ │ skeptic/attacker/ │  │ 修正案提示のみ  │  └───────┬────────┘  │
│ │ newcomer/         │          │            │
│ │ maintainer/       │  ┌───────┴────────┐  │
│ │ domain-skeptic    │  │ ui-test-agent  │  │
│ └────────┬─────────┘  │ (Sonnet)       │  │
│          │             │ [GUI オプトイン │  │
│ ┌────────┴─────────┐  │  有効時のみ]    │  │
│ │ contribution     │  │ 視覚検証        │  │
│ │ (Sonnet)         │  └───────┬────────┘  │
│ │ 分離パターン違反   │          │            │
│ │ 検出（最優先）+    │          │            │
│ │ upstream 貢献候補 │          │            │
│ └────────┬─────────┘          │            │
└──────────┼────────────────────┼────────────┘
           │                    │
           ▼                    ▼
┌───────────────────────────────────────┐
│ フィードバック集約                       │
│                                        │
│ ペルソナ並列時:                          │
│  同一箇所・同一原因は1件に統合             │
│  2ペルソナ以上の独立指摘は重要度+1段       │
│  （コンセンサス補正）                     │
│                                        │
│ Critical/High → 即修正 → Stage 1       │
│ Medium → 修正 or 独立計画               │
│ Low/Info → 計画に記録                   │
│ 関心事の異なるバグ → 新 Plan に分離       │
└───────────────────────────────────────┘
```

## 4. 迷ったときの作法（stop-or-go）の情報の流れ

```
Plan の曖昧さに遭遇
│
▼ 確信度見積り vs 閾値（trust ± image_clarity 補正。/addf-mode で宣言）
│
├─ 閾値以上 ──▶ そのまま進む（見立てを Progress.md 日記に残す）
│
└─ 閾値割れ
   ├─ interactive ──▶ 即時質問（オーナー在席）
   ├─ relaxed ──────▶ Questions.md に質問を置く
   │                  └─▶ TODO を「要確認」にして別タスクへ
   │                      └─▶ オーナーが Answer 記入
   │                          └─▶ 次セッションのブート 1.5 で Plan に反映
   └─ unattended ───▶ 質問を置き speculative/ ブランチで投機続行
                      ├─ dashboard_report → Dashboard.md 生成
                      │   └─▶ 次セッションのブート 1.6 で冒頭提示
                      └─ uncertainty_notify → 外部通知
```

## 5. 投機サイクル（speculation）の情報の流れ

```
/addf-dev がアイドル検出（[speculation].enable = true）
│
▼ speculate-guard.py（enable / max_worktrees / slots。フェイルセーフ ERROR）
▼ speculate-reconcile.py（Worktrees.md ⇔ git 実体の突合。復元・掃除候補）
│
▼ 直交概念の選定（計画済み残課題 > Questions.md > 常設リクエスト）
│
├──────────────┬──────────────┐
▼              ▼              ▼
speculative/A  speculative/B  speculative/C   ← feature 層（worktree + .claude/. 複製）
│ Stage 1      │ Stage 1      │ Stage 1        （失敗は深追いせず打ち切り）
└──────┬───────┴──────┬───────┘
       ▼ テスト通過のみ  │
┌─────────────────────▼─────────────┐
│ integration/loop-<日付>             │ ← 検証層（squash 統合・使い捨て・push しない）
│ speculate-integrate.py             │    衝突解消は必ず feature 側へ反映
│ Stage 2: 相互作用テスト +            │
│ code-review 3ペルソナ並列（一括償却） │
└─────────────────┬─────────────────┘
                  │
                  ▼
  Dashboard.md 書き分け ─┬─「投機ブランチ（採否判断待ち）」（Stage 2 通過のみ）
                        └─「気になった点」（失敗・衝突・上限待機）
  speculative/* を origin へ push（エフェメラル環境対策）
  Progress.md 日記に記録してコミット
                  │
                  ▼（オーナーの明示承認 — 自動昇格経路は存在しない）
  昇格: main へ squash マージ → 昇格後テスト → Worktrees.md「昇格済み」
  → clean --delete（Worktrees.md の記録と突合してから削除）
```
