# Plan 0068: compile_pattern の URL スキーム検出設計と同期契約 lint 化（Plan 0059/0060 レビュー残件回収）

## 実装状況: 未着手

owner_feedback: 不要

> 出典: Plan 0059・0060 の Stage 2 レビュー（code-review H-1/M-1/M-3・contribution-agent Low）。
> lookbehind 境界（Plan 0060）は Issue #33 の誤検知を解消したが、basename 文字列一致という
> 構造的限界に起因する残件が2系統（2体が独立指摘 — コンセンサス補正で High 扱い）。
> フェーズ内では docstring への既知の限界明記＋テスト可視化に留め、根治設計を本 Plan に切り出した。

## 関連 Plan

- [0060-migrate-paths-lookbehind-boundary.md](0060-migrate-paths-lookbehind-boundary.md) — 検出元（lookbehind 境界の導入）
- [0059-downstream-test-environment-compat.md](0059-downstream-test-environment-compat.md) — 項目4（CI downstream 模擬）の切り出し先も本 Plan に同梱

## 回収する残件

1. **[High] blob/raw URL 形式の自己参照残存の検出漏れ**（code-review H-1・回帰）:
   `github.com/<owner>/<repo>/blob/<branch>/<path>` は直前セグメントがブランチ名のため
   self_prefix 例外に入らず検出不能。本体リポジトリに実例あり（0035 の自己参照 blob リンク）
2. **[High 昇格] basename と外部 URL セグメントの偶然一致による誤検知**（M-1 ＋ contribution Low）:
   ディレクトリ名が `ADDF`・`docs`・`app` 等のとき外部 URL 内パスを誤検知・rewrite 対象化しうる
3. **[Medium] compile_pattern() 同期契約の機械検証**（M-3）: 現状はコメント上の申し合わせのみ。
   check_pair7 型の軽量ペア検査（ペア9）を lint-template-sync.py に追加し、
   **addf-lint.md セクション6の表も同時更新する**（Feedback.md 既録の表更新漏れ防止）
4. **[検討] CI での downstream 模擬実行**（Plan 0059 項目4）: addf-init 相当のコピーを CI で
   行い run-all.sh を回す。「upstream 前提の暗黙仮定」欠陥クラスの再発を機械検出する

## 設計方向（レビュー提案の要約）

- 根治は「外部/自己」の判定を basename 一致ではなく **URL スキーム検出**に寄せる:
  `https?://` を含むコンテキストでは URL 全体を外部とみなし除外、ただし
  `git remote get-url origin` から得た `<host>/<owner>/<repo>/` に一致する URL は自己参照として
  検出（remote 不在時は URL 全除外のフェイルセーフ）。裸のパス言及（相対・絶対）には
  従来の1文字境界のみ適用
- 可変長 lookbehind は Python `re` で使えないため、正規表現1本ではなく
  「マッチ後の前方文脈判定」への構造変更が必要（lint / rewrite 両方の呼び出し側に影響）

## テスト方針

- Test 13.5 に blob/raw URL 自己参照（検出されるべき）・basename 衝突 URL（検出されないべき）を追加
- 既存の Issue #33 回帰テスト12件の通過維持

## 破壊的変更の許容範囲

なし（検出精度の改善のみ。API・出力形式は不変）

## AI 実装時間見積もり

1セッション（項目4 の CI を含めると1.5セッション）
