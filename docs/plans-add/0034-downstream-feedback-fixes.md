# Plan 0034: ダウンストリーム実働フィードバック対応（Issue #18/#19/#20）

## 実装状況: 一部完了（2026-07-03 フェーズ1 完了。フェーズ2=#19 設計系要望は未着手）

### フェーズ1 実装記録（2026-07-03）

- #18: `.claude` 複製を3行構成に（cp → venv/node_modules/__pycache__/venv の find 除外
  （symlink 含む）→ `git checkout -- .claude` で追跡下ファイル復元）。knowhow 追記
- #20-1: `--base` を origin default branch 自動検出に（ローカル無ければ `origin/<name>` 起点、
  検出不能時は main フォールバック＋NOTE 可視化）
- #20-2: migrate 14.6 に .gitignore ADDF ブロック置換（マーカー数検査必須・全文一致 sed・
  不成立は手動マージへフォールバック）
- #20-3/4: レビュー発動条件表に投機 Stage 2 行・単独実行時の完了処理を明記
- ペルソナ並列レビューで Critical 2（sed range の EOF 飲み込み・default branch 検出の
  ローカル不在 die とサイレント誤 base、いずれも実測再現）を検出しフェーズ内修正。
  テスト36件全パス

> 出典: 2つのダウンストリーム実働報告 — Issue #18（venv 破損バグ）、#19（ワードローブ/朔の現場報告）、
> #20（イヴの時間のフィードバックとお便り）。いずれも実測ベース。

## 目的

投機サイクル・migrate・テストランナーの実運用で踏まれた穴を塞ぐ。共通するテーマは
「本体では成立する前提が、ダウンストリームの多様な構成（venv 持ち・default branch 非 main・
独自運用）で崩れる」こと。

## フェーズ1: 実装が明確な修正（#18＋#20 小ネタ）

1. **#18: worktree への `.claude` 複製で venv が壊れる**（該当構成では毎サイクル必発）
   - addf-speculate.md 手順3 の複製を除外付きに変更（`.venv` / `node_modules` / `__pycache__` は
     コピーしない。rsync 依存を避け `cp -r` ＋ `find ... -prune -exec rm -rf` の後処理方式）
   - 手順4（Stage 1 前）に「除外した依存はコピー先で再構築（`uv sync` / `bun install` 等）」の注記
   - knowhow `worktree-dotdir-copy.md` に「venv は relocatable でない」落とし穴を追記
2. **#20-1: `speculate-integrate.py` の `--base` が `main` 固定** — `git symbolic-ref
   refs/remotes/origin/HEAD` からの自動検出（remote なし・未設定時は `main` フォールバック）＋テスト
3. **#20-2: ダウンストリームの `.gitignore` に ADDF ブロックの更新が届かない** — addf-migrate の
   対象に「.gitignore の ADDF マーカーブロックのみクローン元の同ブロックで置換を提案」を追加
   （マーカー囲みなので機械的に安全。ブロック外は従来どおり触らない）
4. **#20-3: ペルソナ並列の発動条件表に投機サイクルの行がない** — addf-code-review-agent.md の
   表に「投機の Stage 2（integration 一括）」行を追加（addf-speculate.md 手順7 と同期）
5. **#20-4: `/addf-speculate` 単独実行（cron/loop）時の完了処理** — 手順10 に「単独実行時は
   Progress.md の日記＋コミットのみでよい」の一文

## フェーズ2: 設計系要望（#19）

1. **migrate の部分導入正規化モード**: addf-lock.json 不在時に ERROR 終了ではなく
   「初期正規化モードで走るか」を提案する分岐（または /addf-init に既存プロジェクト正規化を明記）
2. **run-all.sh の設計ガイドライン**: 「必須ランタイム不在は SKIP=成功ではなく失敗として扱う」
   （SKIP の乱用が silent 無効化になる — Plan 0033 の SKIP 可視化と同根）を run-all.sh コメント
   と knowhow に明文化
3. **addf-init check の hooks 配線確認**: settings.json に ADDF 由来 hooks が配線されているかの検査
4. **addf-dev.md の Stage 1/2 読み替え明示**: ダウンストリーム独自の Progress 運用がある場合の
   カスタマイズ指針を一文

## 注記のみで対応（設計は変えない）

- #19 引っかかり4（手順6 のコマンドが素の python3）: speculate-integrate.py は tomllib 不要で
  Python 3.6+ で動くため python3 表記は意図的（設計は変えない）。ただし誤解が実際に起きたため、
  addf-speculate.md 手順6 に「tomllib 不要のためシステム python3（3.6+）でそのまま動く。uv 不要」の
  注記を追加した（**対応済み**）

## 完了条件

- フェーズ1: `bash .claude/tests/run-all.sh` 全パス（--base 自動検出の回帰テスト含む）。
  venv 除外は fake `.venv` を仕込んだサンドボックスで「コピーされないこと」を機械検証
- フェーズ2: 各項目の受け入れ確認はフェーズ2 詳細化時に定義する
- Issue #18/#19/#20 への返信はオーナー確認後に行う <!-- human-judgment: Issue 返信文はオーナーが承認してから投稿する -->

## 関連

- Issue: https://github.com/fruitriin/ADDF/issues/18 / 19 / 20
- `docs/knowhow/ADDF/worktree-dotdir-copy.md` — 複製の既知の罠（今回 venv を追記）
- `docs/knowhow/ADDF/sync-lint-design.md` — SKIP 設計の裏面（#19 引っかかり2 と同根）
- Plan 0028（投機基盤）/ Plan 0033（存在≠所有）
