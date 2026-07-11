# 計画駆動 — Plan-driven development loop

> 概念単位の記録。実装がスキル/エージェント/フック/ファイルのどれであっても、
> 「計画からタスク完遂までの開発ループと、その途中の判断・引き継ぎ」に関わるものをまとめている。

## 構成要素

| 種別 | 名前 | 役割 |
|---|---|---|
| スキル | addf-dev | TODO から1タスクを選び、実装→品質検証→コミットまで完遂する。アイドル時（着手可能タスクなし）は [speculation] オプトイン時に /addf-speculate を1サイクル実行する |
| スキル | addf-mode | 「迷ったときの作法」3軸モードと unattended 情報伝達フラグの切替（保存先: CLAUDE.local.md） |
| スキル | addf-plan-audit | 「完了扱いだが未完了タスクが残っている計画」（埋没）の掘り起こし棚卸し（Plan 0036）。構造検査・意味的パターン・TODO 突合の3層で走査し、処置3択（回収計画に起こす / 一部完了に訂正 / 意図的な完了と明記）を**提案する**（完了状態の変更・採否はオーナー判断） |
| エージェント | addf-implementer | Plan・スコープ・完了条件が明示された委譲プロンプトを受けて実装を専任で行う（model: opus）。Stage 1（ビルド・Lint・テスト）を自己完結で通過させ、明示指示がない限り commit しない。並列実装方針（CLAUDE.md）で worktree 隔離下に委譲されることを想定（Plan 0049） |
| テンプレート | .claude/addf/templates/DelegationRules.md | 委譲エージェント共通の禁止事項5条（Progress.md「## タスク」以降不可侵・git commit/push/tag 禁止・単一ソース尊重・スコープ厳守・knowhow はレポートに残すのみで直接編集しない）の単一ソース。下流プロジェクト固有ルールの追記枠を末尾に持つ（Plan 0049） |
| ファイル | TODO.md | ダウンストリームのタスクバックログ |
| ファイル | .claude/addf/plans-add/TODO.addf.md | ADDF 開発のタスクバックログ（Phase 1〜53。lint ペア6が Plan の実装状況ヘッダと突合。2026-07-11 時点で Plan 0053 が着手中） |
| ファイル | .claude/addf/Progress.md | 現在のタスク進捗・運用ルール（チェックリスト・日記・品質検証フロー） |
| ファイル | .claude/addf/Feedback.md | 問題・改善アクションの記録。タスク完了時に追記 |
| ファイル | .claude/addf/Questions.md | 非同期質問箱。閾値割れ時に質問を置いて別タスクへ移る（コミットされる共有チャンネル） |
| ファイル | .claude/addf/Dashboard.md | unattended 自走の差分まとめ（実行時生成・.gitignore。オーナー確認後に削除） |
| ファイル | .claude/addf/Questions.example.md / Dashboard.example.md | 上記2ファイルの書式定義（addf-init コピー対象） |
| ディレクトリ | .claude/addf/plans/ | ダウンストリーム実装計画ファイル |
| ディレクトリ | .claude/addf/plans-add/ | ADDF 自身の開発計画ファイル（47件） |
| ディレクトリ | .claude/addf/Progresses/ | 完了タスクの Progress アーカイブ（日記ごと保存） |
| テンプレート | .claude/addf/templates/PlanTemplate.md | Plan の標準書式（Plan 0035）。実装状況ヘッダ・完了条件チェックボックス・`execution_style: one-shot` マーカー（大改造 Plan の実施様式宣言 — 意味の単一ソースは guides/speculative-development.md） |
| テンプレート | .claude/addf/templates/ProgressTemplate.md | ダウンストリーム用 Progress テンプレート |
| テンプレート | .claude/addf/templates/ProgressTemplate.addf.md | ADDF 開発用 Progress テンプレート（lint ペア1・2の正） |

## 設計思想

ADDF の第一の柱。CLAUDE.md のブートシーケンスがこのシステムの起点となる:

1. Feedback.md を読む → 未対応の改善アクション確認
   - 1.5 Questions.md → オーナーの回答を Plan に反映
   - 1.6 Dashboard.md → unattended 自走の差分をオーナーに提示
2. TODO.md を読む → タスクバックログ把握
3. Progress.md を読む → 進行中タスク継続（日記の末尾3エントリーで前任者の文脈を引き継ぐ）
4. タスクなし → プロジェクト初回なら骨格プランニング（ヒアリング→初動計画2〜3本生成）、それ以外はオーナーに確認

「コードではなく計画をレビューする」（CONTRIBUTING.md）が基本方針。人間が計画の方向性を判断し、実装品質は AI（品質ゲートシステム）が担保する。Progress.md には運用ルールが埋め込まれており、addf-dev スキルはこれをステートマシンとして動作する。

### 迷ったときの作法（7割共有原則）— Plan 0016

Plan の曖昧さに遭遇したら確信度を見積もり、3軸で進む/止まる/問うを決める:

- **軸A 信頼性（trust）**: nervous(5割) / normal(7割・デフォルト) / full(9割) — 閾値そのもの
- **軸B 応答性（responsiveness）**: interactive（即時質問）/ relaxed（Questions.md に置いて別タスクへ・デフォルト）/ unattended（質問を置き `speculative/` ブランチで投機続行）
- **軸C 完成イメージ確度（image_clarity）**: specific(-1段) / balanced(±0) / vague(+1段)

モードは Plan フロントマターまたは `/addf-mode` で宣言する。worktree 隔離下は閾値を1段下げてよい。サブタスク完了時点で `checkpoint/<phase>-<N>` ブランチを切り、別方針は `alt/` で分岐できる。3軸の表は固定式ではなくガイドラインであり、見立ては Progress.md に書き残す。

### 埋没タスクの掘り起こし — Plan 0035/0036

「完了」の嘘は2層で防ぐ: **新規の嘘**は lint-plan-status.py（`/addf-lint` セクション12。ヘッダ「完了」×未チェック `- [ ]` の構造矛盾を常時ブロック）、**過去の埋没**（「先送り」「残課題は別途」等の文章・番号ずれ・TODO 不整合）は /addf-plan-audit が棚卸しで掘り起こす。走査対象は明示シグナル（CLAUDE.repo.md 種別宣言 → lock フォールバック）で upstream/downstream を切り替え、機械検出はスクリプト実行結果を取り込む（再実装しない）。ADDF アップデートで本スキルが初めて入ったときは addf-migrate が一回きりの棚卸しを案内する。

### 止まらない教義（満杯時の出口）— Plan 0041

コンテキスト残量が少ないことを**理由にループを止めない・タスク着手を控えない**。auto-compact は harness が上限接近時に自動発動し、post-compact-recovery.sh と日記が受け止める（発動点はフェーズ2で実測済み）。残量少時のタスク運び: 復帰容易性の高いタスク（進捗がファイル差分に現れる・刻みが小さい）を優先し、未コミットの大きな途中状態を抱える one-shot 級タスクには着手しない。進捗の外部化（こまめなコミット・チェックリスト・日記）を通常より密に刻む。Progress 運用ルール 3.5 に配線され、context-reminder.py の注入文言も同じ教義で締める（→ system-session）。

### 実装委譲と並列実装方針 — Plan 0049・CLAUDE.md「並列実装方針」

サブタスクを並列実装する場合、git worktree を積極的に使う。実装エージェント（addf-implementer 等。モデル配分は CLAUDE.repo.md「モデル配分ポリシー」節を参照）への委譲は原則 `isolation: "worktree"` で起動し、各 worktree は独立ブランチで作業して完了後にメインブランチへマージする。委譲プロンプトには `DelegationRules.md` の5条（Progress.md 境界・git 操作制限・単一ソース尊重・スコープ厳守・knowhow はレポートに残すのみ）を含める。worktree 起動後は `.claude` ディレクトリを worktree にコピーする（hooks 等 .gitignore 対象は自動複製されないため）。**隔離破りの既知の落とし穴**: Bash ツールは呼び出し間で作業ディレクトリが持続しうるため、隔離下のエージェントが共有チェックアウト側を絶対パス `cd` で覗くと、次に worktree へ `cd` し直すまで以降のコマンド（`git commit` 等）が共有チェックアウト側で実行されてしまう（Plan 0051 で発見）。覗くときは `cd <path> && <command>` を1コマンド内で完結させるか `git -C <path> <command>` を使う（`.claude/addf/knowhow/ADDF/worktree-isolation-cd-persistence.md`）。

### 代替わり日記 — Plan 0017

resume・compaction・`/loop` の次イテレーションで起きる「小さな代替わり」のたびに、Progress.md のタスク「#### 日記」に4項目（やったこと / 今の見立て / 次の自分へ / 気になっていること）を書く。ブランチ checkpoint が「何がコミットされたか（事実）」を残すのに対し、日記は「なぜそうしたか・次に何を考えていたか（文脈）」を残す。自動生成フックは意図的に導入しない（書くこと自体が思考の整理）。「遺書」ではなく「日記」という語彙を使う理由は .claude/addf/guides/development-process.md 参照。

## 主要フロー

```
ブートシーケンス
  │
  ├─ Feedback.md → Questions.md(1.5) → Dashboard.md(1.6)
  ├─ TODO.md 読み込み（ADDF: TODO.addf.md も）
  └─ Progress.md 読み込み（日記の末尾3エントリーで引き継ぎ）
       │
       ▼
  タスク選択（addf-dev）
  優先度: 複利効果（ブロッカー解消・インフラ）> 若番
  ├─ アイドル（着手可能タスクなし）かつ [speculation].enable = true
  │   → /addf-speculate を1サイクル実行（→ system-speculation）
       │
       ▼
  Progress.md にチェックリスト作成
       │
       ▼
  実装ループ（サブタスク単位）
  ├─ サブタスク完了・重要判断・計画変更時に日記を書く
  ├─ 確信度が閾値割れ → relaxed: Questions.md に質問を置き次のタスクへ
  │                     unattended: speculative/ ブランチで投機続行
  └─ checkpoint/<phase>-<N> ブランチ・alt/ 分岐（任意）
       │
       ▼
  品質検証（→ system-quality）
       │
       ▼
  完了処理
  ├─ Plan に完了状況反映（`## 実装状況:` ヘッダ — lint ペア6が TODO と突合）
  ├─ /addf-knowhow で知見記録（コーディング・品質ゲート・タスク総括の3観点）
  ├─ Feedback.md に記録
  ├─ Progress.md を日記ごと .claude/addf/Progresses/ にアーカイブ
  └─ コミット
```

## 下流でのカスタマイズ

- `TODO.md` と `.claude/addf/plans/` に独自のタスクと計画を配置する
- `ProgressTemplate.md` を編集して品質検証フローをカスタマイズ（Stage 1 のみ or Stage 1+2。CLAUDE.repo.example.md の「品質ゲート拡張」参照）
- CLAUDE.repo.md でブートシーケンスの補足を追加可能
- `/addf-mode` でオーナーの状況（在席/不在）に合わせて判断閾値を調整する
- Plan フロントマター（`trust:` / `responsiveness:` / `image_clarity:`）でタスク単位のモード宣言が可能（セッション設定より優先）

## 関連するシステム

- **ノウハウ蓄積**: ブートシーケンス Step 5 で knowhow-agent を起動、実装完了時に knowhow 記録。差し戻し・やり直しは .exp.md「分かれ道の目印」へ
- **品質ゲート**: Progress.md の「タスク完了時 — 品質検証」で品質ゲートを起動（ドキュメント変更時は addf-doc-review-agent も並列起動）。unattended 自走時はペルソナ並列レビューが発動。lint セクション12が Plan の誤完了を常時ブロック
- **セッション管理**: ブートシーケンスが計画駆動の起点。addf-mode の状態は CLAUDE.local.md（セッション横断の個人設定）に保存
- **投機開発**: addf-dev のアイドル検出が投機サイクルの発動点。投機結果は Dashboard.md（採否判断待ち/気になった点）と Progress.md 日記に残り、Questions.md の未回答質問は投機対象の選定元になる。投機に不向きな概念は `execution_style: one-shot` マーカー付き Plan として計画駆動側に戻ってくる（Plan 化フォールバック・大改造の窓 — → system-speculation）
