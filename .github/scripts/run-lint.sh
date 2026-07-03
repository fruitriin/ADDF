#!/bin/bash
# CI 用 lint ラッパー。
# ADDF の lint は exit code 3値（0 = OK / 1 = ERROR / 2 = WARNING のみ）。
# ERROR はジョブを落とし、WARNING はジョブを通しつつ GitHub Actions の
# annotation（::warning::）で PR 上に可視化する。
#
# 使い方: run-lint.sh <スクリプト名（.py 抜き）> [引数...]

set -uo pipefail

name="$1"
shift
script=".claude/addfTools/${name}.py"

if [ ! -f "$script" ]; then
  echo "::error::lint スクリプトが見つからない: $script"
  exit 1
fi

output="$(python3 "$script" "$@" 2>&1)"
code=$?
echo "$output"

case "$code" in
  0) exit 0 ;;
  2)
    # WARNING のみ → ジョブは通す。annotation は1行ずつ（複数行はまとめると読めない）
    while IFS= read -r line; do
      [ -n "$line" ] && echo "::warning title=${name}::${line}"
    done <<< "$output"
    exit 0
    ;;
  *)
    echo "::error title=${name}::${name} が ERROR（exit ${code}）で失敗"
    exit 1
    ;;
esac
