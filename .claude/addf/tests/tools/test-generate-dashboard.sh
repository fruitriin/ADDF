#!/bin/bash
# test-generate-dashboard.sh
# generate-dashboard.py（Plan 0058）がリポジトリ状態からローカルダッシュボード
# （.claude/addf/dashboard/）を生成できることを検証する。
# python3（または uv）が無い環境では SKIP。vitepress の実ビルド検証は node があり
# node_modules が整っている場合のみ実施し、無ければ SKIP する（欠如 = SKIP 設計）。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
GEN_SCRIPT="$REPO_ROOT/.claude/addf/addfTools/generate-dashboard.py"
OUT_DIR="$REPO_ROOT/.claude/addf/dashboard"
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

# python3 / uv のどちらかで実行（uv 優先はしない — stdlib のみのため python3 直接で十分）
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

echo "Test 1: generate-dashboard.py が正常終了する"
(cd "$REPO_ROOT" && $RUN_PY "$GEN_SCRIPT" >/dev/null 2>&1)
check "生成スクリプトが exit 0" 0 $?

echo "Test 2: 3ページ + VitePress 設定が生成される"
missing=0
for f in index.md active.md backlog.md .vitepress/config.mts .vitepress/theme/custom.css; do
  if [ ! -f "$OUT_DIR/$f" ]; then
    echo "  MISSING: $f"
    missing=$((missing + 1))
  fi
done
check "必須生成物が揃っている（欠落 $missing 件）" 0 "$([ "$missing" -eq 0 ]; echo $?)"

echo "Test 3: プランビューア（Plan 本文コピー）が生成される"
plan_count=$(find "$OUT_DIR/plans" -name "[0-9]*.md" 2>/dev/null | wc -l | tr -d ' ')
check "plans/ 配下に1件以上コピーされる（実際: $plan_count 件）" 0 "$([ "$plan_count" -ge 1 ]; echo $?)"

echo "Test 4: owner_feedback フィールドがキューに反映される"
# 本体リポジトリでは Plan 0058 起票時点以降、待ち Plan が最低1件は存在する前提だが、
# 将来ゼロ件になっても壊れないよう「見出しの存在」を主張の軸にする
if grep -q "^## オーナー判断待ちの Plan" "$OUT_DIR/index.md"; then
  echo "  PASS: 要フィードバックページに判断待ちセクションがある"
  PASS=$((PASS + 1))
else
  echo "  FAIL: 判断待ちセクションが index.md に無い"
  FAIL=$((FAIL + 1))
fi

echo "Test 5: Vue コンパイルを壊す裸のタグ様テキストがエスケープされている"
# インラインコード内（バッククォート内）は markdown-it が安全に処理するため対象外。
# 「バッククォートを含まない行」に裸の <concept> が残っていないことと、
# エスケープ済みの証拠（&lt;concept）が実在することの両面で検証する
bare=$(grep -rn 'speculative/<concept>' "$OUT_DIR/plans/" 2>/dev/null | grep -v '\`' || true)
if [ -n "$bare" ]; then
  echo "$bare"
  echo "  FAIL: 既知の再現ケース（バッククォート外の裸 <concept>）が未エスケープで残存"
  FAIL=$((FAIL + 1))
else
  echo "  PASS: バッククォート外の裸 <concept> は残っていない"
  PASS=$((PASS + 1))
fi
if grep -rq 'speculative/&lt;concept' "$OUT_DIR/plans/" 2>/dev/null; then
  echo "  PASS: エスケープ済みの証拠（&lt;concept）が実在する"
  PASS=$((PASS + 1))
else
  echo "  FAIL: エスケープ済みの証拠が見つからない（エスケープ関数が機能していない疑い）"
  FAIL=$((FAIL + 1))
fi

echo "Test 6: vitepress 実ビルド（node + node_modules がある場合のみ）"
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
