#!/bin/bash
# run-lint.sh — ADDF lint スクリプトの exit code 3値を GitHub Actions にマッピングする共通ラッパー
#
#   0 = OK      → ステップ成功
#   1 = ERROR   → ステップ失敗（ジョブ失敗 = マージブロック）
#   2 = WARNING → ステップは通すが `::warning::` annotation で PR / Actions UI に可視化する
#
# WARNING の扱いは全 lint 一律「通す + annotation」（lint ごとの個別設定は
# 運用実績を見てから — 判断の経緯は .claude/addf/plans-add/0030-ci-quality-gate.md 参照）。
# lint は `uv run --python 3.11` で実行し、ローカルの /addf-lint と
# Python バージョン・PEP 723 依存解決（pyyaml 等）を一致させる。
#
# 使い方: bash .github/scripts/run-lint.sh <lint スクリプトパス> [引数...]
#
# 意図的に set -e を付けていない: uv の終了コードを code=$? で読み取って
# 3値マッピングするため、非0終了で即死されると分岐できない
set -uo pipefail

if [ $# -lt 1 ]; then
  echo "usage: run-lint.sh <lint-script> [args...]" >&2
  exit 1
fi

script="$1"
shift
name="$(basename "$script")"

# lint スクリプトの存在を実行前に確認する。
# uv はスクリプト不在（spawn 失敗）でも exit 2 を返し、WARNING 規約（exit 2 = 通す）と
# 衝突する。ここで ERROR にしないと「lint スクリプトを削除すれば CI が黙って緑になる」
# 抜け道（silent green）が生まれるため、不在は必ずジョブ失敗にする
if [ ! -f "$script" ]; then
  printf '::error title=%s::lint スクリプトが見つかりません: %s\n' "$name" "$script"
  exit 1
fi

output="$(uv run --python 3.11 "$script" "$@" 2>&1)"
code=$?

# ログには生の出力をそのまま流す（SKIP 行も annotation とは別に必ず残す）。
# ただし生ダンプ中の行頭 `::workflow command::` が GitHub Actions に解釈されないよう、
# ::stop-commands:: <ランダムトークン> でブラケットして無効化する（workflow command injection 対策）
stop_token="addf-stop-$RANDOM$RANDOM$(date +%s)"
printf '::stop-commands::%s\n' "$stop_token"
printf '%s\n' "$output"
printf '::%s::\n' "$stop_token"

# exit 2 でも uv 自体の起動失敗痕跡（Failed to spawn）があれば ERROR に昇格する。
# 理由: uv は lint 本体の実行に至らない spawn 失敗でも exit 2 を返すことがあり、
# それを WARNING として通すと「lint が1行も実行されていないのに緑」になるため
if [ "$code" -eq 2 ] && printf '%s\n' "$output" | grep -q 'Failed to spawn'; then
  printf '::error title=%s::uv の起動失敗（Failed to spawn）を検出しました。exit 2 ですが lint の WARNING ではなく実行エラーとして扱います\n' "$name"
  exit 1
fi

case "$code" in
  0)
    exit 0
    ;;
  2)
    # annotation は 4000 字で切り詰める（巨大出力による annotation の破損・可読性低下を防ぐ。全文は上のステップログに残る）
    annot="$output"
    if [ "${#annot}" -gt 4000 ]; then
      annot="${annot:0:4000}...(truncated — 全文はステップログ参照)"
    fi
    # workflow command は1行制約のため、% → %25 / CR → %0D / LF → %0A の順でエスケープして載せる
    escaped="${annot//'%'/%25}"
    escaped="${escaped//$'\r'/%0D}"
    escaped="${escaped//$'\n'/%0A}"
    printf '::warning title=%s exited 2 (WARNING)::%s\n' "$name" "$escaped"
    exit 0
    ;;
  *)
    # ERROR 側の annotation が定型文なのは、失敗ステップは Actions UI が自動展開してログ全文が見えるため（WARNING と違い全文転記が不要）
    printf '::error title=%s exited %s::lint が ERROR を報告しました。このステップのログを確認してください\n' "$name" "$code"
    exit "$code"
    ;;
esac
