#!/bin/bash
# test-turn-reminder.sh
# turn-reminder.sh のテスト。カウンターをシミュレートして exit コード・stdout を検証。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
HOOK="$PROJECT_DIR/.claude/hooks/turn-reminder.sh"
COUNTER_FILE="$PROJECT_DIR/.claude/.turn-count"
PASS=0
FAIL=0

cleanup() {
  rm -f "$COUNTER_FILE"
}
trap cleanup EXIT

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

assert_stdout_empty() {
  local test_name="$1" stdout="$2"
  if [ -z "$stdout" ]; then
    echo "  PASS: $test_name (stdout empty)"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $test_name (expected empty stdout, got: $stdout)"
    FAIL=$((FAIL + 1))
  fi
}

assert_stdout_contains() {
  local test_name="$1" stdout="$2" pattern="$3"
  if echo "$stdout" | grep -q "$pattern"; then
    echo "  PASS: $test_name (contains '$pattern')"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $test_name (expected '$pattern' in stdout)"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== test-turn-reminder.sh ==="

# テスト 1: 通常ターン（リマインダーなし）
echo "Test 1: 通常ターン (0→1)"
echo "0" > "$COUNTER_FILE"
export CLAUDE_PROJECT_DIR="$PROJECT_DIR"
stdout=$(echo '{}' | bash "$HOOK" 2>/dev/null) || true
assert_exit "exit code" 0 $?
assert_stdout_empty "no reminder at turn 1" "$stdout"

# テスト 2: 10ターン目（リマインダーあり）
echo "Test 2: 10ターン目 (9→10)"
echo "9" > "$COUNTER_FILE"
stdout=$(echo '{}' | bash "$HOOK" 2>/dev/null)
assert_exit "exit code" 0 $?
assert_stdout_contains "10 turn reminder" "$stdout" "10ターン経過"
assert_stdout_contains "安心文（切り上げ指示でない）" "$stdout" "作業を切り上げる指示ではありません"
if echo "$stdout" | grep -q "コンテキストが大きくなって"; then
  echo "  FAIL: 根拠のない残量言及が残っている"
  FAIL=$((FAIL + 1))
else
  echo "  PASS: 残量への決め打ち言及なし"
  PASS=$((PASS + 1))
fi

# テスト 3: 15ターン目（リマインダーあり）
echo "Test 3: 15ターン目 (14→15)"
echo "14" > "$COUNTER_FILE"
stdout=$(echo '{}' | bash "$HOOK" 2>/dev/null)
assert_exit "exit code" 0 $?
assert_stdout_contains "15 turn reminder" "$stdout" "15ターン経過"

# テスト 4: 11ターン目（リマインダーなし）
echo "Test 4: 11ターン目 (10→11)"
echo "10" > "$COUNTER_FILE"
stdout=$(echo '{}' | bash "$HOOK" 2>/dev/null)
assert_exit "exit code" 0 $?
assert_stdout_empty "no reminder at turn 11" "$stdout"

# テスト 5: カウンターファイルが存在しない場合
echo "Test 5: カウンターファイルなし (→1)"
rm -f "$COUNTER_FILE"
stdout=$(echo '{}' | bash "$HOOK" 2>/dev/null)
assert_exit "exit code" 0 $?
assert_stdout_empty "no reminder at turn 1 (no file)" "$stdout"
count=$(cat "$COUNTER_FILE")
if [ "$count" -eq 1 ]; then
  echo "  PASS: counter file created with value 1"
  PASS=$((PASS + 1))
else
  echo "  FAIL: expected counter=1, got=$count"
  FAIL=$((FAIL + 1))
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
