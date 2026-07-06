#!/bin/bash
# test-migrate-paths.sh
# migrate-paths.py / lint-residual-paths.py / paths.toml（Plan 0037 フェーズ1）を
# mktemp サンドボックスの合成プロジェクトで検証する（実リポジトリは汚さない）。
#
# 合成プロジェクト: 独自 knowhow 記事あり・docs/ 直下に Pages コンテンツ
# （docs/index.html）あり・docs/plans-add なし、のダウンストリーム相当。
# check → apply → rewrite → lint-residual-paths が ERROR ゼロになるまでを通し、
# 存在≠所有・境界チェック・ドリフト注入 TDD・dirty 拒否・逆流 WARNING を検証する。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS="$(cd "$SCRIPT_DIR/../.." && pwd)/addfTools"
MIGRATE="$TOOLS/migrate-paths.py"
LINT="$TOOLS/lint-residual-paths.py"
PATHS_TOML="$TOOLS/paths.toml"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PASS=0
FAIL=0

check() {
  local desc="$1" expected_exit="$2" actual_exit="$3" output="$4" expected_grep="${5:-}"
  if [ "$actual_exit" -ne "$expected_exit" ]; then
    echo "  FAIL: $desc (exit: expected=$expected_exit actual=$actual_exit)"
    echo "$output" | sed 's/^/    | /'
    FAIL=$((FAIL + 1))
    return
  fi
  if [ -n "$expected_grep" ] && ! grep -q "$expected_grep" <<<"$output"; then
    echo "  FAIL: $desc (出力に '$expected_grep' が見つからない)"
    echo "$output" | sed 's/^/    | /'
    FAIL=$((FAIL + 1))
    return
  fi
  echo "  PASS: $desc"
  PASS=$((PASS + 1))
}

expect() {
  local desc="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    FAIL=$((FAIL + 1))
  fi
}

# tomllib（Python 3.11+）前提のため uv があれば 3.11 を明示する（test-speculate-guard.sh と同パターン）
if command -v uv >/dev/null 2>&1; then
  runpy() { local dir="$1" script="$2"; shift 2; (cd "$dir" && uv run --python 3.11 "$script" "$@" 2>&1); }
else
  runpy() { local dir="$1" script="$2"; shift 2; (cd "$dir" && python3 "$script" "$@" 2>&1); }
fi

git_box() { git -C "$box" -c user.email=t@t -c user.name=t "$@"; }

# ---- 合成プロジェクト（ダウンストリーム相当）の構築 ----
box="$(mktemp -d)"
trap 'rm -rf "$box"' EXIT
(
  cd "$box"
  git init -q -b main .
  mkdir -p docs/plans docs/knowhow/ADDF docs/guides docs/plans-addendum \
           .claude/addfTools .claude/templates .claude/tests
  # ADDF 管理ドキュメント（docs/ サブディレクトリ単位で移動される側）
  printf '# Plan 0001\n参照: docs/knowhow/ADDF/tips.md\n' > docs/plans/0001-sample.md
  printf '# tips\n' > docs/knowhow/ADDF/tips.md
  printf '# 独自記事（プロジェクト所有だが knowhow の仕組みの一部として一緒に移動する）\n' > docs/knowhow/original-article.md
  printf '# ガイド。docs/plans を参照\n' > docs/guides/dev.md
  # Pages コンテンツ（ADDF 管理外 — 絶対に触らない: 存在≠所有）
  printf '<html><body>pages content</body></html>\n' > docs/index.html
  # 境界チェック用: docs/plans-add への参照（本体のみのディレクトリで、ローカルには無い）と
  # マップ外のユーザーパス docs/plans-addendum（前方一致だが別トークン）
  cat > ref-boundary.md <<'EOF'
- upstream plan: docs/plans-add/0037-addf-directory-consolidation.md
- my plan: docs/plans/0001-sample.md
- user dir (map 外・置換されてはならない): docs/plans-addendum/readme.md
EOF
  printf 'user note\n' > docs/plans-addendum/readme.md
  # .claude 側（配布された paths.toml を含む）
  cp "$PATHS_TOML" .claude/addfTools/paths.toml
  printf '# ProgressTemplate\n' > .claude/templates/ProgressTemplate.md
  printf '# Progress\nテンプレート: .claude/templates/ProgressTemplate.md\n' > .claude/Progress.md
  printf '# Feedback\n' > .claude/Feedback.md
  printf '[gui-test]\nenable = false\n' > .claude/addf-Behavior.toml
  printf 'echo ok\n' > .claude/tests/run-all.sh
  printf '# CLAUDE.md\n@.claude/Feedback.md\n計画: docs/plans/ ノウハウ: docs/knowhow/\nテスト: bash .claude/tests/run-all.sh\n' > CLAUDE.md
  git add -A
  git -c user.email=t@t -c user.name=t commit -q -m init
)

echo "Test 1: check モード（既定）— 何も変更せず計画と参照数を提示する"
out="$(runpy "$box" "$MIGRATE")"; code=$?
check "check が exit 0" 0 "$code" "$out" "MOVE (dir): docs/plans → .claude/addf/plans"
check "docs/plans-add（不在・optional）は SKIP 明示" 0 "$code" "$out" "SKIP: docs/plans-add"
expect "check は何も変更しない（作業ツリー clean のまま）" test -z "$(git_box status --porcelain)"

echo "Test 2: 移行前の合成プロジェクトで lint は SKIP を明示する"
out="$(runpy "$box" "$LINT")"; code=$?
check "移行前 SKIP（exit 0）" 0 "$code" "$out" "SKIP: 移行前のリポジトリ"

echo "Test 3: 本体リポジトリ（移行前）でも lint は SKIP を出す（完了条件）"
out="$(runpy "$REPO_ROOT" "$LINT")"; code=$?
check "本体で SKIP（exit 0）" 0 "$code" "$out" "SKIP: 移行前のリポジトリ"

echo "Test 4: dirty な作業ツリーでは apply を拒否する"
echo "dirty" >> "$box/CLAUDE.md"
out="$(runpy "$box" "$MIGRATE" apply)"; code=$?
check "dirty 拒否（exit 1）" 1 "$code" "$out" "dirty"
git_box checkout -q -- CLAUDE.md
expect "拒否時に何も移動していない" test -d "$box/docs/plans"

echo "Test 5: apply — backup ref 作成 → git mv 一括実行（コミットはしない）"
out="$(runpy "$box" "$MIGRATE" apply)"; code=$?
check "apply が exit 0" 0 "$code" "$out" "コミットしてください"
check "backup ref 作成を出力" 0 "$code" "$out" "refs/backup/pre-0037-migration"
expect "backup ref が実在する" git_box rev-parse -q --verify refs/backup/pre-0037-migration
expect "docs/plans → .claude/addf/plans" test -f "$box/.claude/addf/plans/0001-sample.md"
expect "独自 knowhow 記事も knowhow ごと移動" test -f "$box/.claude/addf/knowhow/original-article.md"
expect "addfTools → addf/tools（paths.toml も追従）" test -f "$box/.claude/addf/tools/paths.toml"
expect "addf-Behavior.toml → addf/Behavior.toml（リネーム）" test -f "$box/.claude/addf/Behavior.toml"
expect "存在≠所有: Pages コンテンツ docs/index.html は動かさない" test -f "$box/docs/index.html"
expect "存在≠所有: マップ外の docs/plans-addendum は動かさない" test -f "$box/docs/plans-addendum/readme.md"
expect "旧 docs/plans は消えている" test ! -e "$box/docs/plans"
git_box commit -q -m "git mv"

echo "Test 6: rewrite — マップ駆動＋境界チェックで参照を書き換える"
out="$(runpy "$box" "$MIGRATE" rewrite)"; code=$?
check "rewrite が exit 0" 0 "$code" "$out" "書き換えました"
expect "CLAUDE.md の @メンションが新パスに" grep -q '@.claude/addf/Feedback.md' "$box/CLAUDE.md"
expect "CLAUDE.md の tests 参照が新パスに" grep -q 'bash .claude/addf/tests/run-all.sh' "$box/CLAUDE.md"
expect "docs/plans 参照が新パスに" grep -q '.claude/addf/plans/0001-sample.md' "$box/ref-boundary.md"
expect "境界: docs/plans-add 参照は plans-add のマップで正しく変換" \
  grep -q '.claude/addf/plans-add/0037-addf-directory-consolidation.md' "$box/ref-boundary.md"
expect "境界: マップ外 docs/plans-addendum は無傷（docs/plans の置換で壊れない）" \
  grep -q 'docs/plans-addendum/readme.md' "$box/ref-boundary.md"
git_box add -A
git_box commit -q -m rewrite

echo "Test 7: 移行完了後の lint が ERROR ゼロ（完了ゲート通過）"
out="$(runpy "$box" "$LINT")"; code=$?
check "残存なしで exit 0" 0 "$code" "$out" "OK: 旧パス残存なし"

echo "Test 8: ドリフト注入 TDD — 旧パス参照を書き戻すと lint が ERROR で検出する"
printf '旧参照が復活: docs/plans/0001-sample.md\n' > "$box/drift.md"
git_box add drift.md
out="$(runpy "$box" "$LINT")"; code=$?
check "残存を ERROR 検出（exit 1）" 1 "$code" "$out" 'drift.md:1: 旧パス `docs/plans` が残存'
git_box rm -qf drift.md

echo "Test 9: 境界: docs/plans-addendum への言及は残存として誤検出しない"
printf 'ユーザーパス: docs/plans-addendum/readme.md\n' > "$box/user-note.md"
git_box add user-note.md
out="$(runpy "$box" "$LINT")"; code=$?
check "マップ外パスは残存扱いしない（exit 0）" 0 "$code" "$out" "OK: 旧パス残存なし"
git_box rm -qf user-note.md

echo "Test 10: 逆流 — 移行後に docs/ 配下へ ADDF 管理ファイルを再追加すると WARNING"
mkdir -p "$box/docs/knowhow"
printf '# 逆流記事\n' > "$box/docs/knowhow/reflux.md"
git_box add docs/knowhow/reflux.md
out="$(runpy "$box" "$LINT")"; code=$?
check "逆流を WARNING 検出（exit 2）" 2 "$code" "$out" "逆流"
git_box rm -qf docs/knowhow/reflux.md
rmdir "$box/docs/knowhow" 2>/dev/null

echo "Test 11: tomllib が無い環境 — migrate は ERROR（変更系）・lint は SKIP（受動 lint）"
# PYTHONPATH シムで ModuleNotFoundError を注入し、旧 Python（3.9 等）を再現する
shim="$(mktemp -d)"
printf 'raise ModuleNotFoundError("No module named '"'"'tomllib'"'"'")\n' > "$shim/tomllib.py"
out="$( (cd "$box" && PYTHONPATH="$shim" python3 "$MIGRATE" check 2>&1) )"; code=$?
check "migrate: tomllib 欠如で ERROR（フェイルセーフ）" 1 "$code" "$out" "ERROR"
out="$( (cd "$box" && PYTHONPATH="$shim" python3 "$LINT" 2>&1) )"; code=$?
check "lint: tomllib 欠如で SKIP（誤 ERROR を出さない）" 0 "$code" "$out" "SKIP"
rm -rf "$shim"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
