#!/bin/bash
# test-speculate-reconcile.sh
# speculate-reconcile.py の走査（check）と確定済み削除（clean）を mktemp サンドボックスで検証する。
# bare origin 付きの fake git リポジトリで「一覧と merged_hint」「過去日付 integration の区別と削除」
# 「--delete 指定分のみ削除・判断待ち保護」「remote 無し環境の SKIP」に加え、ペルソナ並列レビューで
# 実測再現した穴（origin 単独削除・未来日付注入・日付またぎ削除・記録なし削除・dirty 破棄）を
# ドリフト注入 TDD で固定する（Plan 0028 フェーズ3）。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RECONCILE="$(cd "$SCRIPT_DIR/../.." && pwd)/addfTools/speculate-reconcile.py"
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

check_absent() {
  local desc="$1" output="$2" pattern="$3"
  if grep -q "$pattern" <<<"$output"; then
    echo "  FAIL: $desc (出力に '$pattern' が含まれている)"
    echo "$output" | sed 's/^/    | /'
    FAIL=$((FAIL + 1))
  else
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  fi
}

assert() {
  local desc="$1"; shift
  if "$@"; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    FAIL=$((FAIL + 1))
  fi
}

# --today は「過去日付の注入のみ許容」のため、実システム日付基準で動的に組む
TODAY="$(date +%F)"
YESTERDAY="$(python3 -c 'import datetime; print(datetime.date.today() - datetime.timedelta(days=1))')"
TWO_DAYS_AGO="$(python3 -c 'import datetime; print(datetime.date.today() - datetime.timedelta(days=2))')"
FUTURE="$(python3 -c 'import datetime; print(datetime.date.today() + datetime.timedelta(days=1))')"
PAST="2020-01-01"

# サンドボックス: bare origin + clone 相当の fake リポジトリ
# （macOS では /var → /private/var のため、git が報告する実体パスに解決しておく）
box="$(cd "$(mktemp -d)" && pwd -P)"
trap 'rm -rf "$box"' EXIT
origin="$box/origin.git"
git init -q --bare -b main "$origin"
repo="$box/repo"
mkdir -p "$repo"
g() { git -C "$repo" -c user.name=t -c user.email=t@t "$@"; }
(
  cd "$repo"
  git init -q -b main .
  printf 'line1\n' > base.txt
  git -c user.name=t -c user.email=t@t add base.txt
  git -c user.name=t -c user.email=t@t commit -qm init
  git remote add origin "$origin"
  git push -q origin main
)

make_feature() {
  local name="$1" file="$2"
  g checkout -q -b "speculative/$name" main
  printf 'content-%s\n' "$name" > "$repo/$file"
  g add "$file"
  g commit -qm "$name"
  g checkout -q main
}

# Worktrees.md を行指定で書く（各引数 = 「ブランチ 状態」のペア）
write_worktrees_md() {
  mkdir -p "$repo/.claude"
  {
    echo "# Worktrees（投機の進行状態）"
    echo ""
    echo "| worktree パス | ブランチ | 対象概念（出典） | 状態 | 最終更新 |"
    echo "|---|---|---|---|---|"
    local pair
    for pair in "$@"; do
      echo "| ../wt | ${pair%% *} | test | ${pair#* } | $TODAY |"
    done
  } > "$repo/.claude/Worktrees.md"
}

# a: worktree あり・origin あり・未マージ / b: worktree なし・origin あり・未マージ
make_feature a a.txt
make_feature b b.txt
g push -q origin speculative/a speculative/b
g worktree add -q "$box/repo-spec-a" speculative/a
# done: main に ff マージ済み（cherry で merged_hint=yes になる）
make_feature done d.txt
g merge -q --ff-only speculative/done
# integration: 過去日付（worktree 付き）と当日
g branch integration/loop-$PAST main
g worktree add -q "$box/repo-int-old" integration/loop-$PAST
g branch integration/loop-$TODAY main

run_reconcile() {
  (cd "$repo" && python3 "$RECONCILE" "$@" 2>&1)
}

echo "=== test-speculate-reconcile.sh ==="

echo "Test 1: check — speculative ブランチ一覧と機械的事実（worktree 有無・origin・merged_hint）"
out="$(run_reconcile --today $TODAY)"; code=$?
check "走査完了で exit 0" 0 "$code" "$out" "local_speculative=speculative/a,speculative/b,speculative/done"
check "worktree ありの a" 0 "$code" "$out" "branch=speculative/a worktree=yes origin=yes merged_hint=no"
check "worktree なしの b" 0 "$code" "$out" "branch=speculative/b worktree=no origin=yes merged_hint=no"
check "マージ済み done は merged_hint=yes" 0 "$code" "$out" "branch=speculative/done worktree=no origin=no merged_hint=yes"
check "speculative worktree のパスが出る" 0 "$code" "$out" "speculative_worktree=speculative/a:$box/repo-spec-a"
check "origin/speculative の一覧が出る" 0 "$code" "$out" "remote_speculative=speculative/a,speculative/b"

echo "Test 2: check — --today 指定で過去日付 integration が「過去」と区別される"
check "過去日付は integration_past" 0 "$code" "$out" "integration_past=integration/loop-$PAST"
check "当日分は integration_today" 0 "$code" "$out" "integration_today=integration/loop-$TODAY"

echo "Test 3: check — rm -rf された stale worktree を prune して数え続けない"
g worktree add -q "$box/repo-spec-b" speculative/b
rm -rf "$box/repo-spec-b"
out="$(run_reconcile --today $TODAY)"; code=$?
check "prune 後は b の worktree なし" 0 "$code" "$out" "branch=speculative/b worktree=no"

echo "Test 4: check — detached HEAD の worktree が detached_worktree= で報告される"
g worktree add -q --detach "$box/repo-detached" main
out="$(run_reconcile --today $TODAY)"; code=$?
check "detached worktree が報告される" 0 "$code" "$out" "detached_worktree=$box/repo-detached"
g worktree remove "$box/repo-detached"

echo "Test 5: check — 前日の integration は猶予で「今日」側、2日前は「過去」側"
g branch integration/loop-$YESTERDAY main
g branch integration/loop-$TWO_DAYS_AGO main
out="$(run_reconcile --today $TODAY)"; code=$?
check "前日分は integration_today 側（猶予）" 0 "$code" "$out" "integration_today=.*integration/loop-$YESTERDAY"
check "2日前は integration_past 側" 0 "$code" "$out" "integration_past=.*integration/loop-$TWO_DAYS_AGO"

echo "Test 6: clean --keep-integrations — 過去 integration の自動削除をオプトアウトできる"
out="$(run_reconcile clean --today $TODAY --keep-integrations)"; code=$?
check "keep 指定で exit 0" 0 "$code" "$out" "kept=branch:integration/loop-$PAST (--keep-integrations で保護)"
assert "過去 integration が残っている" test -n "$(g branch --list integration/loop-$PAST)"

echo "Test 7: clean --delete — 指定ブランチの worktree/ローカル/origin が消え、判断待ちは残る"
write_worktrees_md "speculative/a 昇格済み"
out="$(run_reconcile clean --today $TODAY --delete speculative/a)"; code=$?
check "削除完了で exit 0" 0 "$code" "$out" "removed=branch:speculative/a"
check "worktree の除去が報告される" 0 "$code" "$out" "removed=worktree:$box/repo-spec-a"
check "origin 側の削除が報告される" 0 "$code" "$out" "removed=origin:speculative/a"
check "指定外の b は判断待ち保護" 0 "$code" "$out" "kept=branch:speculative/b (判断待ち保護)"
assert "worktree ディレクトリが消えている" test ! -d "$box/repo-spec-a"
assert "ローカルブランチが消えている" test -z "$(g branch --list speculative/a)"
assert "origin 側も消えている" test -z "$(git -C "$origin" branch --list speculative/a)"
assert "判断待ちの b はローカルに残る" test -n "$(g branch --list speculative/b)"
assert "判断待ちの b は origin にも残る" test -n "$(git -C "$origin" branch --list speculative/b)"

echo "Test 8: clean — 過去日付 integration（と worktree）は消え、猶予内は残る"
check "過去日付 integration の削除" 0 "$code" "$out" "removed=branch:integration/loop-$PAST"
check "2日前の integration も削除" 0 "$code" "$out" "removed=branch:integration/loop-$TWO_DAYS_AGO"
check "当日 integration は保護" 0 "$code" "$out" "kept=branch:integration/loop-$TODAY (猶予内の integration)"
check "前日 integration も猶予で保護" 0 "$code" "$out" "kept=branch:integration/loop-$YESTERDAY (猶予内の integration)"
assert "過去 integration の worktree が消えている" test ! -d "$box/repo-int-old"
assert "過去 integration ブランチが消えている" test -z "$(g branch --list integration/loop-$PAST)"
assert "当日 integration ブランチは残る" test -n "$(g branch --list integration/loop-$TODAY)"
assert "前日 integration ブランチは残る" test -n "$(g branch --list integration/loop-$YESTERDAY)"

echo "Test 9: clean --delete — Worktrees.md の記録と突合しないと削除できない"
write_worktrees_md "speculative/other 昇格済み"
out="$(run_reconcile clean --today $TODAY --delete speculative/b)"; code=$?
check "記録なしは ERROR（exit 1）" 1 "$code" "$out" "記録なし"
assert "b のブランチは消えていない" test -n "$(g branch --list speculative/b)"
assert "b は origin にも残っている" test -n "$(git -C "$origin" branch --list speculative/b)"
write_worktrees_md "speculative/b 開発中"
out="$(run_reconcile clean --today $TODAY --delete speculative/b)"; code=$?
check "「開発中」は削除不可の ERROR" 1 "$code" "$out" "状態「開発中」"
assert "開発中の b は消えていない" test -n "$(g branch --list speculative/b)"
rm "$repo/.claude/Worktrees.md"
out="$(run_reconcile clean --today $TODAY --delete speculative/b)"; code=$?
check "Worktrees.md 自体が無ければ記録なし ERROR" 1 "$code" "$out" "記録を確認できない"

echo "Test 10: clean --delete — 「昇格済み」記載ありなら削除でき、重複指定でも誤警告が出ない"
write_worktrees_md "speculative/b 昇格済み"
out="$(run_reconcile clean --today $TODAY --delete speculative/b --delete speculative/b)"; code=$?
check "重複指定でも exit 0（誤警告なし）" 0 "$code" "$out" "removed=branch:speculative/b"
check "origin 側も削除される" 0 "$code" "$out" "removed=origin:speculative/b"
check_absent "「見つからない」の NOTE が出ない" "$out" "見つからない"
check_absent "WARNING が出ない" "$out" "WARNING:"
assert "b が消えている" test -z "$(g branch --list speculative/b)"

echo "Test 11: clean --delete --force-delete — 記録なしでも突合をスキップして削除できる"
rm -f "$repo/.claude/Worktrees.md"
out="$(run_reconcile clean --today $TODAY --delete speculative/done --force-delete)"; code=$?
check "--force-delete で突合スキップ" 0 "$code" "$out" "removed=branch:speculative/done"
assert "done が消えている" test -z "$(g branch --list speculative/done)"

echo "Test 12: clean --delete — ローカル削除が失敗したら origin 側は保護される（lock 注入）"
make_feature c c.txt
g push -q origin speculative/c
g worktree add -q "$box/repo-spec-c" speculative/c
g worktree lock "$box/repo-spec-c"
write_worktrees_md "speculative/c 放棄"
out="$(run_reconcile clean --today $TODAY --delete speculative/c)"; code=$?
check "ローカル失敗は WARNING（exit 2）" 2 "$code" "$out" "WARNING:"
check "origin 側の保護が報告される" 2 "$code" "$out" "kept=origin:speculative/c（ローカル削除未完了のため保護）"
check_absent "origin 側の削除が実行されていない" "$out" "removed=origin:speculative/c"
assert "origin 側にブランチが残っている" test -n "$(git -C "$origin" branch --list speculative/c)"
g worktree unlock "$box/repo-spec-c"
out="$(run_reconcile clean --today $TODAY --delete speculative/c)"; code=$?
check "unlock 後は削除が完了する" 0 "$code" "$out" "removed=origin:speculative/c"

echo "Test 13: clean --delete — dirty worktree は既定で削除拒否、--force-delete で破棄"
make_feature d d2.txt
g worktree add -q "$box/repo-spec-d" speculative/d
printf 'uncommitted\n' > "$box/repo-spec-d/dirty.txt"
write_worktrees_md "speculative/d 放棄"
out="$(run_reconcile clean --today $TODAY --delete speculative/d)"; code=$?
check "dirty は既定で拒否（exit 2）" 2 "$code" "$out" "kept=worktree:$box/repo-spec-d (未コミット変更があるため保護"
assert "worktree が残っている" test -d "$box/repo-spec-d"
assert "ブランチも残っている" test -n "$(g branch --list speculative/d)"
out="$(run_reconcile clean --today $TODAY --delete speculative/d --force-delete)"; code=$?
check "--force-delete は WARNING を出して破棄（exit 2）" 2 "$code" "$out" "WARNING: .*未コミット変更を破棄した"
check "worktree の除去が報告される" 2 "$code" "$out" "removed=worktree:$box/repo-spec-d"
check "ブランチも削除される" 2 "$code" "$out" "removed=branch:speculative/d"
assert "worktree が消えている" test ! -d "$box/repo-spec-d"
assert "ブランチが消えている" test -z "$(g branch --list speculative/d)"

echo "Test 14: clean — 未マージ実体のある無指定ブランチは何度 clean しても消えない"
make_feature e e.txt
out="$(run_reconcile clean --today $TODAY)"; code=$?
check "無指定 clean は exit 0" 0 "$code" "$out" "kept=branch:speculative/e (判断待ち保護)"
assert "e のブランチは残っている" test -n "$(g branch --list speculative/e)"

echo "Test 15: clean --prune-worktrees — worktree だけ外れ、ブランチは残る"
g worktree add -q "$box/repo-spec-e" speculative/e
out="$(run_reconcile clean --today $TODAY --prune-worktrees)"; code=$?
check "worktree の除去が報告される" 0 "$code" "$out" "removed=worktree:$box/repo-spec-e"
check "ブランチは判断待ち保護のまま" 0 "$code" "$out" "kept=branch:speculative/e (判断待ち保護。worktree のみ外した)"
assert "worktree ディレクトリが消えている" test ! -d "$box/repo-spec-e"
assert "ブランチは残っている" test -n "$(g branch --list speculative/e)"

echo "Test 16: remote 無し環境で check/clean が SKIP 表記で正常動作する"
repo2="$box/repo2"
mkdir -p "$repo2"
g2() { git -C "$repo2" -c user.name=t -c user.email=t@t "$@"; }
(
  cd "$repo2"
  git init -q -b main .
  printf 'x\n' > x.txt
  git -c user.name=t -c user.email=t@t add x.txt
  git -c user.name=t -c user.email=t@t commit -qm init
)
g2 checkout -q -b speculative/x main
printf 'y\n' > "$repo2/y.txt"
g2 add y.txt
g2 commit -qm x
g2 checkout -q main
out="$(cd "$repo2" && python3 "$RECONCILE" --today $TODAY 2>&1)"; code=$?
check "remote 無し check は exit 0" 0 "$code" "$out" "SKIP: remote なし"
check "origin は unknown 扱い" 0 "$code" "$out" "branch=speculative/x worktree=no origin=unknown merged_hint=no"
mkdir -p "$repo2/.claude"
printf '| ../wt | speculative/x | test | 放棄 | %s |\n' "$TODAY" > "$repo2/.claude/Worktrees.md"
out="$(cd "$repo2" && python3 "$RECONCILE" clean --today $TODAY --delete speculative/x 2>&1)"; code=$?
check "remote 無し clean は exit 0" 0 "$code" "$out" "SKIP: remote なし"
check "「放棄」記載でローカルブランチは削除される" 0 "$code" "$out" "removed=branch:speculative/x"
assert "speculative/x が消えている" test -z "$(g2 branch --list speculative/x)"

echo "Test 17: 異常系 — リポジトリ外・不正な --today・未来日付の --today は ERROR"
nonrepo="$box/nonrepo"
mkdir -p "$nonrepo"
out="$(cd "$nonrepo" && python3 "$RECONCILE" 2>&1)"; code=$?
check "リポジトリ外で exit 1" 1 "$code" "$out" "ERROR"
out="$(cd "$repo" && python3 "$RECONCILE" --today not-a-date 2>&1)"; code=$?
check "不正な --today で exit 1" 1 "$code" "$out" "ERROR"
out="$(run_reconcile clean --today $FUTURE)"; code=$?
check "未来日付の --today は exit 1" 1 "$code" "$out" "未来日付は指定できない"
assert "未来日付注入で当日 integration が消えていない" test -n "$(g branch --list integration/loop-$TODAY)"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
