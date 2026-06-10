#!/bin/bash
# test-template-sync.sh
# lint-template-sync.py の同期チェックテスト。
# 実リポジトリでの正常系と、サンドボックスでの意図的ドリフト検出を検証する。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LINT="$PROJECT_DIR/.claude/addfTools/lint-template-sync.py"
PASS=0
FAIL=0

if command -v uv >/dev/null 2>&1; then
  run_lint() { (cd "$1" && uv run --python 3.11 "$LINT" 2>&1); }
else
  run_lint() { (cd "$1" && python3 "$LINT" 2>&1); }
fi

assert_exit() {
  local test_name="$1" expected_exit="$2" actual_exit="$3"
  if [ "$actual_exit" -eq "$expected_exit" ]; then
    echo "  PASS: $test_name (exit=$actual_exit)"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $test_name (expected exit=$expected_exit, got=$actual_exit)"
    FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local test_name="$1" needle="$2" haystack="$3"
  if echo "$haystack" | grep -qF "$needle"; then
    echo "  PASS: $test_name"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $test_name (output missing: $needle)"
    FAIL=$((FAIL + 1))
  fi
}

make_sandbox() {
  local box
  box="$(mktemp -d)"
  mkdir -p "$box/.claude/templates" "$box/docs/guides"
  cp "$PROJECT_DIR/CLAUDE.md" "$PROJECT_DIR/AGENTS.md" "$box/"
  cp "$PROJECT_DIR/.claude/Progress.md" "$box/.claude/"
  cp "$PROJECT_DIR/.claude/templates/ProgressTemplate.addf.md" \
     "$PROJECT_DIR/.claude/templates/ProgressTemplate.md" "$box/.claude/templates/"
  cp "$PROJECT_DIR/docs/guides/development-process.md" "$box/docs/guides/"
  echo "$box"
}

echo "=== test-template-sync.sh ==="

# テスト 1: 実リポジトリで全ペア同期済み（意図的差分が誤検出されないことの確認を兼ねる）
# 前提: リポジトリがクリーンに同期された状態であること。ここが FAIL したら
# テストではなく実ファイルのドリフトを疑い、lint の出力に従って同期する
echo "Test 1: 実リポジトリで OK"
output=$(run_lint "$PROJECT_DIR")
assert_exit "実リポジトリ" 0 $?
assert_contains "OK メッセージ" "OK: 同期チェック通過" "$output"

# テスト 2: ProgressTemplate.md のステップ欠落 → WARNING (exit=2)
echo "Test 2: ダウンストリーム版テンプレートのステップ欠落"
box="$(make_sandbox)"
grep -v '^15\. コミットする' "$box/.claude/templates/ProgressTemplate.md" > "$box/tmp" \
  && mv "$box/tmp" "$box/.claude/templates/ProgressTemplate.md"
output=$(run_lint "$box")
assert_exit "ステップ欠落で WARNING" 2 $?
assert_contains "ペア2の WARNING" "[2] WARNING" "$output"
assert_contains "欠落行の特定" "ADDF版のみ: 15. コミットする" "$output"
assert_contains "git ヒント" "ヒント(最終更新)" "$output"
rm -rf "$box"

# テスト 3: AGENTS.md のブートシーケンス手順欠落 → WARNING (exit=2)
echo "Test 3: AGENTS.md の手順欠落"
box="$(make_sandbox)"
sed -i.bak 's/^5\. /- /' "$box/AGENTS.md" && rm -f "$box/AGENTS.md.bak"
output=$(run_lint "$box")
assert_exit "手順欠落で WARNING" 2 $?
assert_contains "ペア3の WARNING" "[3] WARNING" "$output"
rm -rf "$box"

# テスト 4: Progress.md の運用ルール乖離 → ERROR (exit=1)
echo "Test 4: Progress.md の運用ルール乖離"
box="$(make_sandbox)"
grep -v '^15\. コミットする' "$box/.claude/Progress.md" > "$box/tmp" \
  && mv "$box/tmp" "$box/.claude/Progress.md"
output=$(run_lint "$box")
assert_exit "運用ルール乖離で ERROR" 1 $?
assert_contains "ペア1の ERROR" "[1] ERROR" "$output"
rm -rf "$box"

# テスト 5: development-process.md の手順追加ドリフト → WARNING (exit=2)
echo "Test 5: development-process.md の手順ドリフト"
box="$(make_sandbox)"
sed -i.bak 's/^4\. TODO に未完了タスクがない場合/44. TODO に未完了タスクがない場合/' \
  "$box/docs/guides/development-process.md" && rm -f "$box/docs/guides/development-process.md.bak"
output=$(run_lint "$box")
assert_exit "手順ドリフトで WARNING" 2 $?
assert_contains "ペア4の WARNING" "[4] WARNING" "$output"
rm -rf "$box"

# テスト 6: ダウンストリーム環境（ADDF 本体固有ファイルなし）→ ペア2〜4 SKIP で exit=0
echo "Test 6: ダウンストリーム環境シミュレーション"
box="$(make_sandbox)"
rm -f "$box/.claude/templates/ProgressTemplate.addf.md" "$box/AGENTS.md"
rm -rf "$box/docs/guides"
# Progress.md をダウンストリーム版テンプレート由来の内容に変換する
sed -i.bak -e 's/ProgressTemplate\.addf\.md/ProgressTemplate.md/g' \
  -e '/ADD フレームワークテスト/d' "$box/.claude/Progress.md" && rm -f "$box/.claude/Progress.md.bak"
output=$(run_lint "$box")
assert_exit "ダウンストリームで OK" 0 $?
assert_contains "ペア2の SKIP" "[2] SKIP" "$output"
assert_contains "ペア3の SKIP" "[3] SKIP" "$output"
assert_contains "ペア4の SKIP" "[4] SKIP" "$output"
rm -rf "$box"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
