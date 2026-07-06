---
title: 自分自身を移動させる移行ツールの設計パターン
created: 2026-07-06
last_verified: 2026-07-06
depends_on:
  - file: .claude/addfTools/paths.toml
  - file: .claude/addfTools/migrate-paths.py
  - file: .claude/addfTools/lint-residual-paths.py
status: active
---

# 自分自身を移動させる移行ツールの設計パターン

Plan 0037（ADDF ディレクトリ大集約）フェーズ1 で、リポジトリ内の大規模ファイル移動＋参照書き換えを
マップ駆動で行うツールを実装して得たパターン。**ツール自身が移動対象に含まれる**点が通常の
リファクタリングスクリプトと違う難所になる。

## 発見した知見

### モード分離とコミット分離の構造的強制

- `check`（読み取り専用プリフライト）/ `apply`（git mv のみ）/ `rewrite`（参照書き換えのみ）の
  3モードに分け、**apply と rewrite の両方が dirty な作業ツリーを拒否**する。これにより
  「git mv コミット」と「参照書き換えコミット」の分離（revert 一発で戻せる原子性）が
  オペレーターの規律ではなく構造で強制される
- backup ref は**既存確認してから**作成する。無条件 `update-ref` だと2回目の実行が
  「本当の移行前」を指す ref を静かに上書きし、巻き戻し案内が嘘になる

### 自己移動の罠

- apply でツール自身のディレクトリが移動するため、**完了メッセージには移動後の新パスで
  次コマンドのコマンドラインを具体的に表示**する（旧パスをコピペすると No such file で即死。
  2ペルソナが独立に指摘した実質 Critical）
- マップファイル（paths.toml）の探索は**新位置優先**の候補リストにする。マップ内の旧パス文字列は
  書き換え除外（allowlist）にし、移行後もマップが旧→新対応を保持し続ける = ダウンストリーム移行に再利用できる
- テストは「apply 後に**新位置から** rewrite を呼ぶ」経路を実際に通すこと。旧位置固定の
  テストハーネスはこの罠を素通りする

### 走査の安全化

- **symlink は open 前に除外する**。git は symlink を blob として追跡するため、走査対象に普通に
  混入し、rewrite がリンク先（リポジトリ外の任意ファイル）へ書き込む脆弱性になる（attacker
  ペルソナが実再現）
- バイナリ判定は拡張子ホワイトリストではなく **NUL バイト検査＋UTF-8 デコード失敗**で行い、
  書き換え系と検査系（lint）で走査対象集合を一致させる。不一致だと「check 0箇所 → lint で初 ERROR」
  という食い違いが完了ゲートで初めて露見する
- 部分文字列の誤マッチ（`docs/plans` → `docs/plans-add`）は長いキー優先＋境界判定
  （前後が英数字・ハイフン・アンダースコアならマッチしない）で防ぐ。逐次置換は
  「置換後の新パス文字列が他エントリの旧キーを含まない」という**暗黙の不変条件**に依存する —
  マップ拡張時に守る必要があるためコメントで明示し、ロード時 assert（immovable との重複検査等）を置く

### クラッシュ耐性

- 移動直前の `makedirs` が残す**空の中間ディレクトリは `git status` に出ない**。そのため
  「dirty 判定は clean なのにプリフライトは衝突で拒否」という自己ロックが起きる（attacker が実再現）。
  移動先が空ディレクトリなら衝突扱いせず rmdir して継続する
- 途中失敗状態（apply 済み・rewrite 未了等）を識別できるよう、lint の ERROR には
  「未完了の可能性 → check で確認」の注記を添える

## プロジェクトへの適用

- Plan 0037 フェーズ2（本体移行）・フェーズ3（addf-migrate 統合）はこのツール群を使う。
  実行順は apply → コミット → **新位置の** rewrite → コミット → lint-residual-paths ERROR ゼロ
- 将来の再配置は paths.toml の更新だけで migrate・lint・テストが追従する（単一ソース）

## 注意点・制約

- import ガード（変更系=ERROR / lint=SKIP）とドリフト注入 TDD の一般則は
  [sync-lint-design.md](sync-lint-design.md) が単一ソース
- ADDF 管理サブディレクトリ内部の非所有ファイルは無条件に巻き込む仮定が残る（Plan 0037
  レビュー残課題参照）

## 参照

- `.claude/addfTools/migrate-paths.py` / `lint-residual-paths.py` / `paths.toml`
- `.claude/tests/tools/test-migrate-paths.sh`（51アサーション。攻撃再現テスト込み）
- `docs/plans-add/0037-addf-directory-consolidation.md`
- [persona-review-oneshot.md](persona-review-oneshot.md) — これらの穴を検出したレビュー体制
