# 計画駆動 — Plan-driven development loop

> 概念単位の記録。実装がスキル/エージェント/フック/ファイルのどれであっても、
> 「計画からタスク完遂までの開発ループと、その途中の判断・引き継ぎ」に関わるものをまとめている。

## 構成要素

| 種別 | 名前 | 役割 |
|---|---|---|
| スキル | addf-dev | TODO から1タスクを選び、実装→品質検証→コミットまで完遂する。アイドル時（着手可能タスクなし）は [speculation] オプトイン時に /addf-speculate を1サイクル実行する |
| スキル | addf-mode | 「迷ったときの作法」3軸モードと unattended 情報伝達フラグの切替（保存先: CLAUDE.local.md） |
| ファイル | TODO.md | ダウンストリームのタスクバックログ |
| ファイル | .claude/addf/plans-add/TODO.addf.md | ADDF 開発のタスクバックログ（Phase 1〜38。lint ペア6が Plan の実装状況ヘッダと突合） |
| ファイル | .claude/addf/Progress.md | 現在のタスク進捗・運用ルール（チェックリスト・日記・品質検証フロー） |
| ファイル | .claude/addf/Feedback.md | 問題・改善アクションの記録。タスク完了時に追記 |
| ファイル | .claude/addf/Questions.md | 非同期質問箱。閾値割れ時に質問を置いて別タスクへ移る（コミットされる共有チャンネル） |
| ファイル | .claude/addf/Dashboard.md | unattended 自走の差分まとめ（実行時生成・.gitignore。オーナー確認後に削除） |
| ファイル | .claude/addf/Questions.example.md / Dashboard.example.md | 上記2ファイルの書式定義（addf-init コピー対象） |
| ディレクトリ | .claude/addf/plans/ | ダウンストリーム実装計画ファイル |
| ディレクトリ | .claude/addf/plans-add/ | ADDF 自身の開発計画ファイル（38件） |
| ディレクトリ | .claude/addf/Progresses/ | 完了タスクの Progress アーカイブ（日記ごと保存） |
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
- **品質ゲート**: Progress.md の「タスク完了時 — 品質検証」で品質ゲートを起動。unattended 自走時はペルソナ並列レビューが発動
- **セッション管理**: ブートシーケンスが計画駆動の起点。addf-mode の状態は CLAUDE.local.md（セッション横断の個人設定）に保存
- **投機開発**: addf-dev のアイドル検出が投機サイクルの発動点。投機結果は Dashboard.md（採否判断待ち/気になった点）と Progress.md 日記に残り、Questions.md の未回答質問は投機対象の選定元になる
