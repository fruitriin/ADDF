#!/bin/bash
# test-generate-dashboard.sh
# generate-dashboard.py（Plan 0058）がリポジトリ状態からローカルダッシュボード
# を生成できることを検証する。
#
# 検証の主体は mktemp サンドボックスに作る合成リポジトリ（drift-injection 方式）。
# 実リポジトリの固有コンテンツに依存したアサーションを置かない — 依存すると
# ダウンストリームで必ず FAIL する（Issue #29 / Plan 0055 と同型の再発を
# contribution-agent がサンドボックス実測で検出した教訓）。
# python3（または uv）が無い環境では SKIP。vitepress の実ビルド検証は node と
# node_modules が揃っている場合のみ実施する（欠如 = SKIP 設計）。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
GEN_SCRIPT="$REPO_ROOT/.claude/addf/addfTools/generate-dashboard.py"
PASS=0
FAIL=0
SKIP=0

check() {
  local desc="$1" expected_exit="$2" actual_exit="$3"
  if [ "$actual_exit" -ne "$expected_exit" ]; then
    echo "  FAIL: $desc (exit: expected=$expected_exit actual=$actual_exit)"
    FAIL=$((FAIL + 1))
    return
  fi
  echo "  PASS: $desc"
  PASS=$((PASS + 1))
}

echo "=== test-generate-dashboard.sh ==="

if [ ! -f "$GEN_SCRIPT" ]; then
  echo "SKIP: generate-dashboard.py が見つかりません"
  echo ""
  echo "Results: 0 passed, 0 failed, 1 skipped"
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  RUN_PY="python3"
elif command -v uv >/dev/null 2>&1; then
  RUN_PY="uv run"
else
  echo "SKIP: python3 も uv も見つかりません"
  echo ""
  echo "Results: 0 passed, 0 failed, 1 skipped"
  exit 0
fi

# ---- サンドボックス（ダウンストリーム構成: plans/ + TODO.md・git/gh/Questions 無し）----
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
mkdir -p "$SANDBOX/.claude/addf/plans"

# 合成 Plan 1: FB 待ち + Vue コンパイルを壊す敵対的入力
#  - 裸の <concept>（英字開始タグ様テキスト — 実際に vitepress build を落とした再現ケース）
#  - タイトルにも <foo>（本文コピー以外のページへの挿入経路の検証）
#  - 奇数個のバッククォートを含む行（閉じ無しバッククォートでエスケープが
#    免除される退行の検証 — code-review C1）
cat > "$SANDBOX/.claude/addf/plans/0001-sample.md" <<'EOF'
# Plan 0001: サンプル計画 <foo> のタイトル

## 実装状況: 未着手

owner_feedback: 待ち
feedback_ask: テスト用の判断ですよ
feedback_since: 2026-01-01

昇格の定義は speculative/<concept> → main とする。
出力例`のようになる。閉じ無しバッククォートの後の speculative/<concept> も対象。
EOF

# 合成 Plan 2: FB 済（キューに出ないことの検証）
cat > "$SANDBOX/.claude/addf/plans/0002-done-fb.md" <<'EOF'
# Plan 0002: フィードバック済みの計画

## 実装状況: 一部完了（テスト用）

owner_feedback: 済
EOF

cat > "$SANDBOX/TODO.md" <<'EOF'
| 優先度 | Phase | 計画ファイル | 状態 |
|---|---|---|---|
| 1 | 1 | `.claude/addf/plans/0001-sample.md` | 未着手（テスト用） |
| 2 | 2 | `.claude/addf/plans/0002-done-fb.md` | 一部完了（テスト用） |
EOF

OUT="$SANDBOX/.claude/addf/dashboard"

echo "Test 1: サンドボックス（DS 構成・git/gh/Questions/Progress 無し）で正常終了する"
(cd "$SANDBOX" && ADDF_DASHBOARD_ROOT="$SANDBOX" $RUN_PY "$GEN_SCRIPT" >/dev/null 2>&1)
check "生成スクリプトが exit 0（欠如フェイルセーフ）" 0 $?

echo "Test 2: 3ページ + VitePress 設定が生成される"
missing=0
for f in index.md active.md backlog.md .vitepress/config.mts .vitepress/theme/custom.css; do
  if [ ! -f "$OUT/$f" ]; then
    echo "  MISSING: $f"
    missing=$((missing + 1))
  fi
done
check "必須生成物が揃っている（欠落 $missing 件）" 0 "$([ "$missing" -eq 0 ]; echo $?)"

echo "Test 3: プランビューアに合成 Plan がコピーされる"
check "plans/0001-sample.md が存在する" 0 "$([ -f "$OUT/plans/0001-sample.md" ]; echo $?)"

echo "Test 4: owner_feedback フィールドがキューに反映される（独立オラクル: 待ちは1件）"
if grep -q "オーナー判断待ちの Plan — 1件" "$OUT/index.md" \
  && grep -q "テスト用の判断ですよ" "$OUT/index.md"; then
  echo "  PASS: 待ち1件・feedback_ask がキュー行に表示される"
  PASS=$((PASS + 1))
else
  echo "  FAIL: キューの件数または feedback_ask の表示が期待と異なる"
  FAIL=$((FAIL + 1))
fi
if grep -q "0002" "$OUT/index.md"; then
  echo "  FAIL: owner_feedback: 済 の Plan がキューに出ている"
  FAIL=$((FAIL + 1))
else
  echo "  PASS: owner_feedback: 済 の Plan はキューに出ない"
  PASS=$((PASS + 1))
fi

echo "Test 5: Vue コンパイルを壊す入力がエスケープされている"
bad=0
# 5a: 本文コピー — 裸の <concept> が残らず、エスケープ済み証拠がある
if grep -q 'speculative/<concept>' "$OUT/plans/0001-sample.md"; then
  echo "  FAIL: 本文コピーに裸の <concept> が残存"
  bad=$((bad + 1))
fi
if ! grep -q 'speculative/&lt;concept' "$OUT/plans/0001-sample.md"; then
  echo "  FAIL: 本文コピーにエスケープ済み証拠（&lt;concept）が無い"
  bad=$((bad + 1))
fi
# 5b: 奇数バッククォート行の後もエスケープされる（C1 リグレッション）
if ! grep -q '閉じ無しバッククォートの後の speculative/&lt;concept' "$OUT/plans/0001-sample.md"; then
  echo "  FAIL: 奇数バッククォート行の後半がエスケープされていない（C1 再発）"
  bad=$((bad + 1))
fi
# 5c: タイトル経由の挿入（index/backlog）もエスケープされる（C2 リグレッション）
if grep -q '<foo>' "$OUT/index.md" "$OUT/backlog.md" 2>/dev/null; then
  echo "  FAIL: タイトル由来の <foo> が未エスケープでページに挿入されている（C2 再発）"
  bad=$((bad + 1))
fi
if ! grep -q '&lt;foo&gt;\|&lt;foo>' "$OUT/index.md"; then
  echo "  FAIL: index.md にタイトルのエスケープ済み証拠（&lt;foo）が無い"
  bad=$((bad + 1))
fi
check "敵対的入力のエスケープ（不備 $bad 件）" 0 "$([ "$bad" -eq 0 ]; echo $?)"

echo "Test 6: 実リポジトリでも生成が正常終了する"
(cd "$REPO_ROOT" && $RUN_PY "$GEN_SCRIPT" >/dev/null 2>&1)
check "実リポジトリで exit 0" 0 $?

echo "Test 7: vitepress 実ビルド（node + node_modules がある場合のみ）"
if command -v node >/dev/null 2>&1 && [ -d "$REPO_ROOT/node_modules/vitepress" ]; then
  (cd "$REPO_ROOT" && ./node_modules/.bin/vitepress build .claude/addf/dashboard >/dev/null 2>&1)
  check "vitepress build が通る" 0 $?
else
  echo "  SKIP: node または node_modules/vitepress が無いため実ビルドは省略"
  SKIP=$((SKIP + 1))
fi

echo ""
echo "Results: $PASS passed, $FAIL failed, $SKIP skipped"
[ "$FAIL" -eq 0 ]
