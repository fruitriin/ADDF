#!/bin/bash
# test-genealogy.sh
# Plan 0056 フェーズ1: 系統樹の基盤検証。
#   1) lint-genealogy.py が edge 構文・対象実在・pruned メタデータ・リンク併記を検出する
#   2) generate-dashboard.py が genealogy.md を生成し、Mermaid graph・classDef・
#      サイドバー配線を含む
#
# 全て mktemp サンドボックスに合成フィクスチャを作って検証する（drift-injection 方式）。
# 実リポジトリ固有コンテンツに依存するアサーションは書かない — ダウンストリーム
# （plans 0件・plans-add 不在）でも成立する設計（Issue #29 / Plan 0055 の教訓）。
# python3 も uv も無い環境では SKIP。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
GEN_SCRIPT="$REPO_ROOT/.claude/addf/addfTools/generate-dashboard.py"
LINT_SCRIPT="$REPO_ROOT/.claude/addf/addfTools/lint-genealogy.py"
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

echo "=== test-genealogy.sh ==="

if [ ! -f "$LINT_SCRIPT" ] || [ ! -f "$GEN_SCRIPT" ]; then
  echo "SKIP: lint-genealogy.py または generate-dashboard.py が見つかりません"
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

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT
PLANS_DIR="$SANDBOX/.claude/addf/plans"
mkdir -p "$PLANS_DIR"

# ---- 合成 Plan 群（複数の edge 型を網羅） ----

# Plan 0100: 正常な derived-from + blocked-by owner。関連 Plan 節にリンク併記あり
cat > "$PLANS_DIR/0100-derived.md" <<'EOF'
# Plan 0100: 派生先の Plan

## 実装状況: 未着手

owner_feedback: 待ち
edge: derived-from 0101
edge: blocked-by owner

## 関連 Plan

- [Plan 0101: 派生元](0101-origin.md) — derived-from
EOF

# Plan 0101: 単純な未着手 Plan（0100 のターゲット）
cat > "$PLANS_DIR/0101-origin.md" <<'EOF'
# Plan 0101: 派生元の Plan

## 実装状況: 未着手
EOF

# Plan 0102: absorbed-into + revives（ターゲット存在 + リンク併記あり）
cat > "$PLANS_DIR/0102-absorbed.md" <<'EOF'
# Plan 0102: 吸収された残タスク

## 実装状況: 完了

edge: absorbed-into 0101
edge: revives 0103

## 関連 Plan

- [Plan 0101](0101-origin.md) — absorbed-into 先
- [Plan 0103: 剪定済み](0103-pruned.md) — revives 対象
EOF

# Plan 0103: pruned Plan（メタデータ3項目あり）
cat > "$PLANS_DIR/0103-pruned.md" <<'EOF'
# Plan 0103: 剪定済みの Plan

## 実装状況: 未着手

edge: pruned

## 関連 Plan

- **理由**: 実測でスコープ内の実害ゼロ
- **証拠**: EnumaElish/wasurenainder の実測ログ
- **復活条件**: 肥大化の実害が観測されたとき
EOF

# Plan 0104: blocked-by external + blocked-by 0101（数値ターゲットはリンク併記が必要）
cat > "$PLANS_DIR/0104-blocked.md" <<'EOF'
# Plan 0104: 依存で待たされている Plan

## 実装状況: 進行中

edge: blocked-by external
edge: blocked-by 0101

## 関連 Plan

- [Plan 0101](0101-origin.md) — blocked-by
EOF

# TODO テーブル（進行中・完了状態注入用）
cat > "$SANDBOX/TODO.md" <<'EOF'
| 優先度 | Phase | 計画ファイル | 状態 |
|---|---|---|---|
| 1 | 1 | `.claude/addf/plans/0100-derived.md` | 未着手 |
| 2 | 2 | `.claude/addf/plans/0101-origin.md` | 未着手 |
| 3 | 3 | `.claude/addf/plans/0102-absorbed.md` | 完了 |
| 4 | 4 | `.claude/addf/plans/0103-pruned.md` | 未着手 |
| 5 | 5 | `.claude/addf/plans/0104-blocked.md` | 進行中 |
EOF

# ---- lint テスト ----

echo "Test 1: 正常な合成フィクスチャで lint-genealogy.py が OK"
(cd "$SANDBOX" && $RUN_PY "$LINT_SCRIPT" > "$SANDBOX/lint1.log" 2>&1)
lint_exit=$?
if [ "$lint_exit" -ne 0 ]; then
  echo "  --- lint output ---"
  cat "$SANDBOX/lint1.log"
  echo "  --- /output ---"
fi
check "正常フィクスチャで exit 0" 0 "$lint_exit"

echo "Test 2: pruned のメタデータ欠落を ERROR で検出（ドリフト注入）"
# 復活条件ラベルを削除する
sed -i.bak 's/\*\*復活条件\*\*/**旧ラベル**/' "$PLANS_DIR/0103-pruned.md"
(cd "$SANDBOX" && $RUN_PY "$LINT_SCRIPT" > "$SANDBOX/lint2.log" 2>&1)
lint_exit=$?
check "メタデータ欠落で exit 1" 1 "$lint_exit"
if ! grep -q "復活条件" "$SANDBOX/lint2.log"; then
  echo "  FAIL: エラーメッセージが「復活条件」欠落を示していない"
  FAIL=$((FAIL + 1))
else
  echo "  PASS: エラーメッセージが欠落項目を明示"
  PASS=$((PASS + 1))
fi
# 復元
mv "$PLANS_DIR/0103-pruned.md.bak" "$PLANS_DIR/0103-pruned.md"

echo "Test 3: 未知の edge 型を ERROR で検出"
cat > "$PLANS_DIR/0105-invalid.md" <<'EOF'
# Plan 0105: 未知型テスト

## 実装状況: 未着手

edge: unknown-type 0101
EOF
(cd "$SANDBOX" && $RUN_PY "$LINT_SCRIPT" > "$SANDBOX/lint3.log" 2>&1)
lint_exit=$?
check "未知の edge 型で exit 1" 1 "$lint_exit"
grep -q "未知の edge 型" "$SANDBOX/lint3.log" || {
  echo "  FAIL: エラーメッセージが「未知の edge 型」を示していない"
  FAIL=$((FAIL + 1))
}
rm -f "$PLANS_DIR/0105-invalid.md"

echo "Test 4: 存在しない Plan 番号を ERROR で検出"
cat > "$PLANS_DIR/0106-missing.md" <<'EOF'
# Plan 0106: 存在しない対象

## 実装状況: 未着手

edge: derived-from 9999

## 関連 Plan

- [Plan 9999](9999-nonexistent.md) — derived-from（存在しない）
EOF
(cd "$SANDBOX" && $RUN_PY "$LINT_SCRIPT" > "$SANDBOX/lint4.log" 2>&1)
lint_exit=$?
check "存在しない対象で exit 1" 1 "$lint_exit"
grep -q "9999" "$SANDBOX/lint4.log" || {
  echo "  FAIL: エラーメッセージに対象 Plan 番号 9999 が現れない"
  FAIL=$((FAIL + 1))
}
rm -f "$PLANS_DIR/0106-missing.md"

echo "Test 5: 数値エッジで「関連 Plan」節リンク併記漏れを ERROR で検出"
cat > "$PLANS_DIR/0107-nolink.md" <<'EOF'
# Plan 0107: リンク併記漏れ

## 実装状況: 未着手

edge: derived-from 0101

## 関連 Plan

- ここには 0101 への markdown リンクが無い（プレーンテキストのみ）
EOF
(cd "$SANDBOX" && $RUN_PY "$LINT_SCRIPT" > "$SANDBOX/lint5.log" 2>&1)
lint_exit=$?
check "リンク併記漏れで exit 1" 1 "$lint_exit"
grep -q "Markdown リンクが" "$SANDBOX/lint5.log" || {
  echo "  FAIL: エラーメッセージがリンク併記漏れを示していない"
  FAIL=$((FAIL + 1))
}
rm -f "$PLANS_DIR/0107-nolink.md"

echo "Test 6: plans ディレクトリ不在（ダウンストリーム互換）は SKIP + exit 0"
EMPTY_BOX="$(mktemp -d)"
(cd "$EMPTY_BOX" && $RUN_PY "$LINT_SCRIPT" > "$EMPTY_BOX/lint6.log" 2>&1)
lint_exit=$?
check "plans 不在で exit 0" 0 "$lint_exit"
grep -q "SKIP" "$EMPTY_BOX/lint6.log" || {
  echo "  FAIL: SKIP 出力が無い"
  FAIL=$((FAIL + 1))
}
rm -rf "$EMPTY_BOX"

echo "Test 7: 空の plans ディレクトリ（0件）で NOTE + exit 0"
EMPTY_PLANS="$(mktemp -d)"
mkdir -p "$EMPTY_PLANS/.claude/addf/plans"
(cd "$EMPTY_PLANS" && $RUN_PY "$LINT_SCRIPT" > "$EMPTY_PLANS/lint7.log" 2>&1)
lint_exit=$?
check "plans 0件で exit 0" 0 "$lint_exit"
grep -q "検査対象 0 件" "$EMPTY_PLANS/lint7.log" || {
  echo "  FAIL: NOTE メッセージが無い"
  FAIL=$((FAIL + 1))
}
rm -rf "$EMPTY_PLANS"

# ---- generate-dashboard.py 経由の統合検証 ----

echo "Test 8: generate-dashboard.py が genealogy.md を生成し必須要素を含む"
CRIT_DIR="$SANDBOX/crit-empty"
mkdir -p "$CRIT_DIR"
OUT="$SANDBOX/.claude/addf/dashboard"
(cd "$SANDBOX" && ADDF_DASHBOARD_ROOT="$SANDBOX" ADDF_CRIT_REVIEWS_DIR="$CRIT_DIR" $RUN_PY "$GEN_SCRIPT" > "$SANDBOX/gen.log" 2>&1)
gen_exit=$?
check "生成スクリプトが exit 0" 0 "$gen_exit"
if [ ! -f "$OUT/genealogy.md" ]; then
  echo "  FAIL: genealogy.md が生成されていない"
  FAIL=$((FAIL + 1))
else
  echo "  PASS: genealogy.md が生成されている"
  PASS=$((PASS + 1))
fi

echo "Test 9: genealogy.md に Mermaid ブロック・ノード・classDef が含まれる"
bad=0
grep -q 'class="addf-mermaid"' "$OUT/genealogy.md" || { echo "  FAIL: addf-mermaid コンテナが無い"; bad=$((bad+1)); }
grep -q '^graph TD' "$OUT/genealogy.md" || { echo "  FAIL: graph TD ヘッダが無い"; bad=$((bad+1)); }
grep -q '^  P0100\[' "$OUT/genealogy.md" || { echo "  FAIL: ノード P0100 が無い"; bad=$((bad+1)); }
# derived-from の向き: 0101 → 0100（合成フィクスチャ）
grep -q 'P0101 -->|derived-from| P0100' "$OUT/genealogy.md" || { echo "  FAIL: derived-from の向き（0101→0100）が正しくない"; bad=$((bad+1)); }
# revives は太線
grep -q 'P0103 ==>|revives| P0102' "$OUT/genealogy.md" || { echo "  FAIL: revives の太線描画（0103==>0102）が無い"; bad=$((bad+1)); }
# pruned Plan（0103）を絡めるエッジは点線に格上げされる — revives edge (0103→0102) は片方 pruned なので点線
# ただし現在 revives は thick 優先で書いているためドットにならない（設計判断: revives は太線を優先）
# ノードスタイル: pruned が classDef pruned に入る
grep -q 'class P0103 pruned;\|class .*P0103.* pruned' "$OUT/genealogy.md" || { echo "  FAIL: P0103 が pruned クラスに入っていない"; bad=$((bad+1)); }
grep -q 'class .*P0100.* blockedOwner\|class P0100 blockedOwner' "$OUT/genealogy.md" || { echo "  FAIL: P0100 が blockedOwner クラスに入っていない"; bad=$((bad+1)); }
grep -q 'class .*P0104.* blockedExternal\|class P0104 blockedExternal' "$OUT/genealogy.md" || { echo "  FAIL: P0104 が blockedExternal クラスに入っていない"; bad=$((bad+1)); }
# classDef 定義（オーナーブロック=赤枠）
grep -q 'classDef blockedOwner .*stroke:#c62828' "$OUT/genealogy.md" || { echo "  FAIL: blockedOwner classDef が無い"; bad=$((bad+1)); }
grep -q 'classDef blockedExternal .*stroke:#d4a017' "$OUT/genealogy.md" || { echo "  FAIL: blockedExternal classDef が無い"; bad=$((bad+1)); }
grep -q 'classDef pruned' "$OUT/genealogy.md" || { echo "  FAIL: pruned classDef が無い"; bad=$((bad+1)); }
check "Mermaid 要素の網羅（不備 $bad 件）" 0 "$([ "$bad" -eq 0 ]; echo $?)"

echo "Test 10: サイドバーに 系統樹 が配線される"
grep -q "'/genealogy'" "$OUT/.vitepress/config.mts" || {
  echo "  FAIL: サイドバーに /genealogy へのリンクが無い"
  FAIL=$((FAIL + 1))
}
grep -q "'系統樹'" "$OUT/.vitepress/config.mts" || {
  echo "  FAIL: サイドバーラベル「系統樹」が無い"
  FAIL=$((FAIL + 1))
}

echo "Test 11: Layout.vue に mermaid 描画配線がある"
grep -q "addf-mermaid" "$OUT/.vitepress/theme/Layout.vue" || {
  echo "  FAIL: Layout.vue に addf-mermaid セレクタが無い"
  FAIL=$((FAIL + 1))
}
grep -q "import('mermaid')" "$OUT/.vitepress/theme/Layout.vue" || {
  echo "  FAIL: Layout.vue に mermaid 動的 import が無い"
  FAIL=$((FAIL + 1))
}

echo "Test 12: クリティカルパスセクションが blocked-by owner / その他 を区別"
bad=0
grep -q "オーナー判断待ち" "$OUT/genealogy.md" || { echo "  FAIL: 「オーナー判断待ち」セクションが無い"; bad=$((bad+1)); }
grep -q "その他のブロック" "$OUT/genealogy.md" || { echo "  FAIL: 「その他のブロック」セクションが無い"; bad=$((bad+1)); }
# blocked-by owner の Plan 0100 が「オーナー判断待ち」節に載る（独立オラクル: 別経路で状態を判定）
owner_sec=$(sed -n '/オーナー判断待ち/,/その他のブロック\|## \|### /p' "$OUT/genealogy.md")
echo "$owner_sec" | grep -q '`0100`' || { echo "  FAIL: P0100 が「オーナー判断待ち」節に無い"; bad=$((bad+1)); }
check "クリティカルパス区分（不備 $bad 件）" 0 "$([ "$bad" -eq 0 ]; echo $?)"

echo "Test 13: エッジ0件の空 Plan ディレクトリでも genealogy.md は生成される"
EMPTY_BOX2="$(mktemp -d)"
mkdir -p "$EMPTY_BOX2/.claude/addf/plans" "$EMPTY_BOX2/crit-empty"
touch "$EMPTY_BOX2/TODO.md"
(cd "$EMPTY_BOX2" && ADDF_DASHBOARD_ROOT="$EMPTY_BOX2" ADDF_CRIT_REVIEWS_DIR="$EMPTY_BOX2/crit-empty" $RUN_PY "$GEN_SCRIPT" > "$EMPTY_BOX2/gen.log" 2>&1)
gen_exit=$?
check "0件 Plan で生成が exit 0" 0 "$gen_exit"
[ -f "$EMPTY_BOX2/.claude/addf/dashboard/genealogy.md" ] || {
  echo "  FAIL: 0件でも genealogy.md は生成されるべき"
  FAIL=$((FAIL + 1))
}
grep -q "エッジ付き Plan がまだ登録されていません" "$EMPTY_BOX2/.claude/addf/dashboard/genealogy.md" || {
  echo "  FAIL: 空案内メッセージが無い"
  FAIL=$((FAIL + 1))
}
rm -rf "$EMPTY_BOX2"

echo "Test 14: 実リポジトリで lint-genealogy.py が exit 0/1/2 のいずれかで終了する（構造検証）"
(cd "$REPO_ROOT" && $RUN_PY "$LINT_SCRIPT" > /dev/null 2>&1)
lint_exit=$?
if [ "$lint_exit" -eq 0 ] || [ "$lint_exit" -eq 1 ] || [ "$lint_exit" -eq 2 ]; then
  echo "  PASS: 実リポジトリで exit $lint_exit"
  PASS=$((PASS + 1))
else
  echo "  FAIL: 想定外の exit $lint_exit（0/1/2 のいずれかであるべき）"
  FAIL=$((FAIL + 1))
fi

echo "Test 15: コードフェンス内の edge 例示は生成パーサに混入しない（code-review C2 回帰）"
FBOX="$(mktemp -d)"
mkdir -p "$FBOX/.claude/addf/plans"
cat > "$FBOX/.claude/addf/plans/0001-fence.md" <<'FIXEOF'
# Plan 0001: フェンス検証

## 実装状況: 未着手

edge: blocked-by owner

書式の例:

```
edge: derived-from 0002
edge: pruned
```
FIXEOF
printf '# TODO\n\n| 優先度 | Phase | 計画ファイル | 状態 |\n|---|---|---|---|\n' > "$FBOX/TODO.md"
edge_count=$(cd "$FBOX" && ADDF_DASHBOARD_ROOT="$FBOX" $RUN_PY -c "
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location('gd', '$GEN_SCRIPT')
gd = importlib.util.module_from_spec(spec); spec.loader.exec_module(gd)
info = gd.parse_plan(pathlib.Path('$FBOX/.claude/addf/plans/0001-fence.md'))
print(len(info['edges']))
")
if [ "$edge_count" = "1" ]; then
  echo "  PASS: フェンス内の edge 2行は無視され本物の1行のみパースされる"
  PASS=$((PASS + 1))
else
  echo "  FAIL: edge 数が期待 1 に対し $edge_count（フェンス内が混入している）"
  FAIL=$((FAIL + 1))
fi
rm -rf "$FBOX"

echo "Test 16: _mermaid_label が HTML を無害化する（code-review C1 回帰）"
out=$($RUN_PY -c "
import importlib.util
spec = importlib.util.spec_from_file_location('gd', '$GEN_SCRIPT')
gd = importlib.util.module_from_spec(spec); spec.loader.exec_module(gd)
print(gd._mermaid_label('x</pre></div><img src=x onerror=alert(1)>'))
")
if echo "$out" | grep -q '</pre>'; then
  echo "  FAIL: </pre> が素通りしている（HTML 注入可能）: $out"
  FAIL=$((FAIL + 1))
else
  echo "  PASS: HTML タグがエスケープされる: $out"
  PASS=$((PASS + 1))
fi

echo "Test 17: 自己参照エッジと5桁番号を lint が ERROR にする（code-review M1/M2 回帰）"
SBOX="$(mktemp -d)"
mkdir -p "$SBOX/.claude/addf/plans"
cat > "$SBOX/.claude/addf/plans/0001-selfref.md" <<'FIXEOF'
# Plan 0001: 自己参照

## 実装状況: 未着手

edge: derived-from 0001

## 関連 Plan

- [Plan 0001](0001-selfref.md)
FIXEOF
(cd "$SBOX" && $RUN_PY "$LINT_SCRIPT" > "$SBOX/lint.log" 2>&1)
rc=$?
if [ "$rc" -eq 1 ] && grep -q "自己参照" "$SBOX/lint.log"; then
  echo "  PASS: 自己参照エッジが ERROR"
  PASS=$((PASS + 1))
else
  echo "  FAIL: 自己参照が検出されない (rc=$rc)"
  FAIL=$((FAIL + 1))
fi
cat > "$SBOX/.claude/addf/plans/0001-selfref.md" <<'FIXEOF'
# Plan 0001: 5桁

## 実装状況: 未着手

edge: derived-from 00020

## 関連 Plan

- なし
FIXEOF
(cd "$SBOX" && $RUN_PY "$LINT_SCRIPT" > "$SBOX/lint2.log" 2>&1)
rc=$?
if [ "$rc" -eq 1 ]; then
  echo "  PASS: 5桁番号が ERROR（先頭4桁への誤解決をしない）"
  PASS=$((PASS + 1))
else
  echo "  FAIL: 5桁番号が素通り (rc=$rc)"
  FAIL=$((FAIL + 1))
fi
rm -rf "$SBOX"

echo ""
echo "Results: $PASS passed, $FAIL failed, $SKIP skipped"
[ "$FAIL" -eq 0 ]
