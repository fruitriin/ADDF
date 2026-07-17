# Plan 0068: compile_pattern の URL スキーム検出設計と同期契約 lint 化（Plan 0059/0060 レビュー残件回収）

## 実装状況: 完了（2026-07-18。BoundaryPattern〔マッチ後前方文脈判定〕・remote 由来 self URL 判定〔git@/ssh:///https 3形式・host 小文字化・user@ 剥がし〕・ペア9 lint〔テキスト一致＋必須シンボル＋順序ドリフト明示〕・テスト計32件追加。code-review H-1/M-1〜3/L-1〜2 全反映。CI downstream 模擬は Plan 0069 に切り出し）

edge: derived-from 0059
edge: derived-from 0060

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

## 実装記録（2026-07-18）

### 変更ファイル

- `.claude/addf/addfTools/migrate-paths.py` — compile_pattern を `BoundaryPattern` クラスに構造変更。
  同期ブロック `# --- BEGIN/END sync: compile_pattern (Plan 0068) ---` で囲う
- `.claude/addf/addfTools/lint-residual-paths.py` — 同上（両ファイルは文字通り同一実装に保つ契約）
- `.claude/addf/addfTools/lint-template-sync.py` — ペア9（`check_pair9`）追加。同期ブロックの
  正規化テキスト一致を Counter で検査（ヘルパ `_extract_sync_block`・`_normalize_sync_lines`）
- `.claude/commands/addf-lint.md` — セクション6のペア表に9行目を追加
- `.claude/addf/tests/tools/test-migrate-paths.sh` — Test 13.6（blob/raw 自リポジトリ URL 検出・
  basename 衝突誤検知なし・外部 URL 書き換え不可）と Test 13.7（remote 不在フェイルセーフ）を追加。
  drift-injection TDD で検証（合成フィクスチャの sandbox に remote を追加/削除して分岐を踏む）
- `.claude/addf/tests/tools/test-template-sync.sh` — Test 27〜30（pair9 の正常系・片側注入検出・
  マーカー欠如検出・docstring 内引用の誤認識防止）を追加

### データフローと判定順序（BoundaryPattern._keep）

1. マッチ位置を含む `https?://...` URL を先に走査
   - 内側なら:
     - `_self_url_prefixes()` が空 → False（remote 不在フェイルセーフ）
     - 該当プレフィックス（`<host>/<owner>/<repo>` に一致・末尾 `/` 直後で境界）→ True（自リポジトリ URL 内自己参照 = blob/raw 自己参照残存）
     - それ以外の URL → False（外部 URL）
2. URL 外なら、直前2文字を検査
   - `[A-Za-z0-9]/` の場合:
     - 直前が `/<self_basename>/` → True（自リポジトリ絶対パス）
     - それ以外 → False（他プロジェクト絶対パス）
   - それ以外 → True（相対パス・行頭裸パス）

### remote 不在時の挙動

`_self_url_prefixes()` が空リストを返した時点で、URL 内マッチは全て「外部扱い」として除外される。
理由: 自リポジトリを名乗れない状況で「これは自分」の判定は原理的に不可能なため、安全側
（rewrite が外部 URL を絶対に壊さない）に倒す。lint での検出漏れは受容可能なトレードオフ（残存
検出が本題であって、自リポジトリの blob URL 自己参照は remote 設定して再スキャンできる）。

### GitHub raw URL のエイリアス

`git remote get-url origin` の host が `github.com` の場合、`_self_url_prefixes()` は
`raw.githubusercontent.com/<owner>/<repo>` も併記する。これで `github.com/owner/repo/blob/branch/path`
と `raw.githubusercontent.com/owner/repo/branch/path` の両形式が自己参照として検出できる。

### CI downstream 模擬（項目4）の取り扱い

実測評価（scratchpad で DS 相当ディレクトリを構築して `bash .claude/addf/tests/run-all.sh` を
実行）で、hook テスト（`test-context-reminder`・`test-destructive-git-guard`・
`test-pre-compact-archive` 等）が DS 環境で多数 FAIL することを確認した。これらはリアルな
hooks 配線・upstream 特有の環境前提を要するため、DS 対応化には Plan 0059 の延長として
本格的な取り組みが必要。本 Plan では「切り出し推奨」の報告に留める（Plan 本文の
「規模が大きすぎると判断したら」条項の適用）。

**切り出し候補**: 新 Plan「run-all.sh の DS 環境対応化と CI での downstream 模擬ジョブ追加」。
着手時は (1) 各 hook テストの DS 対応化 or SKIP 化を先行、(2) 合成 DS ディレクトリ生成の
共通ヘルパ（`.github/scripts/make-fake-downstream.sh` 等）を新設、(3) `.github/workflows/test.yml`
に downstream 模擬ジョブを追加、の順が妥当。
