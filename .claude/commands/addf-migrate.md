---
name: addf-migrate
description: |
  ADDF フレームワークを最新版にアップグレードする。addf-lock.json のバージョンと
  最新版の差分を算出し、安全にマイグレーションする。
  ADDF のアップデート・バージョンアップ・マイグレーションを行いたいときに使う。
user_invocable: true
---

# ADDF マイグレーション

ADDF フレームワークを最新版（またはターゲットバージョン）にアップグレードする。

## 引数

- **引数なし**: 最新版にアップグレード
- `$ARGUMENTS`: ターゲットのコミットハッシュまたはタグを指定

## 前提条件

- `.claude/addf/lock.json` が存在すること。存在しない場合は2分岐:
  - ADDF 由来ファイル（`.claude/commands/addf-*.md` 等）も存在しない → エラー終了し `/addf-init` を案内する
  - ADDF 由来ファイルが存在する（= lock 未生成の**部分導入**プロジェクト。手縫い導入・旧版の部分コピー） → 「lock がありませんが ADDF ファイルを検出しました。初期正規化モードで走りますか？」と提案する <!-- human-judgment -->。承認されたら `/addf-init` の「部分導入からの正規化」手順に合流する: 最新版をクローンし、既存の ADDF 由来ファイルは最新版で上書き（安全一括上書きと個別確認必須の2群に分けて扱う — 存在≠所有）・プロジェクト固有ファイル（`*.exp.md`・`Progress.md`・`CLAUDE.repo.md` 等）は保護・完了時に `addf-lock.json` を生成する。手順の実体は `addf-init.md`（外部起動導入＋読み替え）を参照する — ここには重複記述しない
- ワーキングツリーがクリーンであること（未コミットの変更があれば中断して案内する）

## マイグレーション手順

### Phase 1: 状態確認

1. `.claude/addf/lock.json` を読み、現在の `ref`（`vX.Y.Z` タグ名）と `version` を記録する
   - **旧形式の後方互換**: `ref` がなく `commit` フィールドがある lock（v0.3.0 以前の形式）は、`v<version>` タグを起点として扱う（記録されたハッシュはリリースプロセスの都合で実在しない場合があるため、タグを正とする）
2. `git status` でワーキングツリーがクリーンか確認する
   - クリーンでなければ: 「未コミットの変更があります。コミットまたはスタッシュしてから再実行してください」と案内して終了
3. ロックファイルの `repository` フィールドから ADDF リポジトリの URL を取得し検証する:
   - `https://` スキームであることを確認する（`file://`, `ssh://`, `git://` は拒否）: `grep -q '^https://' <<<"<repository-url>"`
   - デフォルト URL（`https://github.com/fruitriin/ADDF.git`）と異なる場合は警告を表示
   - URL をユーザーに表示して確認 <!-- human-judgment -->

### Phase 2: 最新版の取得

4. 一時ディレクトリを作成する:
   ```bash
   mktemp -d
   ```
5. ADDF リポジトリを一時ディレクトリにクローンする:
   ```bash
   git clone --depth 1 <repository-url> <tmp-dir>/addf-latest
   ```
   ターゲット指定時:
   ```bash
   git clone <repository-url> <tmp-dir>/addf-latest
   git -C <tmp-dir>/addf-latest checkout <target>
   ```
6. 最新版のコミットハッシュを記録する:
   ```bash
   git -C <tmp-dir>/addf-latest rev-parse HEAD
   ```

### Phase 3: 差分算出

7. 現在のロックファイルの `ref`（タグ）と最新版の間で、ADDF 管理ファイルの差分をリストアップする

**マイグレーション対象ファイル**（除外規則: `*.addf.md` に該当するファイルは対象外 — ADDF 本体専用。
旧バージョンの配布で残っている `*.addf.md`（例: `ProgressTemplate.addf.md`、`INDEX.addf.md`）があれば削除を提案する）:
- `.claude/commands/addf-*.md` — スキル定義
- `.claude/agents/addf-*.md` — エージェント定義
- `.claude/addf/optional/` — オプトイン式スキル・エージェントの原本（適用後に `sync-optional-skills.py` の再実行を案内）
- `.claude/hooks/` — フック
- `.claude/addf/templates/` — テンプレート
- `.claude/addf/addfTools/` — ツール群
- `.claude/addf/tests/` — テストスイート
- `.claude/settings.json` — 共有権限設定（マージ — Phase 5 参照）
- `CLAUDE.md` — ブートシーケンス（マージ注意）
- `AGENTS.md` — Codex 向けブートシーケンス（上書き）
- `CONTRIBUTING.md` — コントリビューションガイド
- `.claudeignore` — Claude 除外設定
- `.claude/addf/CHANGELOG.md` — 変更履歴（`ADDF-Release.addf.md` は除外規則により対象外）
- `.claude/addf/guides/` — ADDF ガイドドキュメント
- `.claude/addf/knowhow/ADDF/` — ADDF ノウハウ

**マイグレーション対象外（スキップ）:**
- `.claude/addf/Progress.md` — プロジェクト固有の進捗
- `.claude/addf/Feedback.md` — プロジェクト固有の記録
- `.claude/addf/Progresses/` — 完了タスクアーカイブ
- `.claude/commands/*.exp.md` — ローカル経験ファイル
- `.claude/settings.local.json` — ローカル設定
- `.claude/addf/lock.json` — 自身（最後に更新）
- `CLAUDE.repo.md`, `CLAUDE.local.md` — プロジェクト固有設定
- `TODO.md`, `.claude/addf/plans/` — プロジェクトのタスク管理
- `.claude/addf/knowhow/*.md`（ADDF/ 以外） — プロジェクトのノウハウ
- `README.md`, `README.en.md` — プロジェクトの説明
- `.gitignore` — プロジェクトの除外設定。ただし ADDF マーカーブロック（`# --- ADDF Framework` 〜 `# --- /ADDF Framework`）**のみ**はステップ 14.6 でクローン元の同ブロックによる置換を提案する。ブロック外に変更がある場合は従来どおり手動マージを案内

7.5. **旧配布 `*.addf.md` の残留検出**（「7.5」は後続の番号参照を壊さないための枝番）:
旧バージョンの配布でダウンストリームに残っている `*.addf.md` を検出する:
```bash
find . -name '*.addf.md' -not -path './.git/*'
```
検出されたファイルは ADDF 本体専用の残留物のため、Phase 4 の「削除推奨」カテゴリで削除を提案する
（ADDF 本体で実行された場合は `*.addf.md` が正当に存在するが、そもそも本体では
`/addf-migrate` の前提となる `addf-lock.json` の向き先が自身であり通常実行しない）

### Phase 4: 変更の確認

8. 変更をカテゴリ別にユーザーに表示する:

```
╔══════════════════════════════════════════╗
║  ADDF Migration Preview                 ║
║  Current: v0.1.0 (ref: v0.1.0)          ║
║  Target:  v0.2.0 (def5678)              ║
╚══════════════════════════════════════════╝

■ 新規追加 (3)
  + .claude/commands/addf-new-skill.md
  + .claude/agents/addf-new-agent.md
  + .claude/addf/knowhow/ADDF/new-pattern.md

■ 更新 (5)
  ~ .claude/commands/addf-lint.md
  ~ .claude/hooks/turn-reminder.sh
  ~ .claude/addf/templates/ProgressTemplate.md
  ~ CLAUDE.md
  ~ CONTRIBUTING.md

■ 削除 (1)
  - .claude/commands/addf-deprecated.md

■ 削除推奨（旧配布残留ファイル） (2)
  - .claude/addf/templates/ProgressTemplate.addf.md
  - .claude/addf/knowhow/INDEX.addf.md

■ 要手動マージ (1)
  ! .gitignore (変更あり — 手動確認推奨)

■ スキップ (対象外)
  ○ .claude/addf/Progress.md, .claude/addf/Feedback.md, *.exp.md ...
```

9. 最新版の `.claude/addf/CHANGELOG.md` から、現在のバージョンからターゲットバージョンまでのエントリを抽出して表示する:
    ```
    ■ Changelog (v0.1.0 → v0.2.0)
      [0.2.0] - 2026-04-15
        追加: /addf-init スキル
        変更: CLAUDE.md ブートシーケンス改善
      [0.1.1] - 2026-04-01
        修正: addf-lint の INDEX 整合性チェック
    ```

10. ユーザーに確認を求める: 「このマイグレーションを適用しますか？」 <!-- human-judgment -->

### Phase 5: 適用

11. **`settings.json` のマージ**:
    - 最新版の `settings.json` を読む
    - 現在の `settings.json` を読む
    - ADDF 由来のエントリ（hooks、addf 関連権限）を最新版で更新する
    - ダウンストリームが独自に追加したエントリは保持する
    - マージ結果をユーザーに表示して確認を求める <!-- human-judgment -->

12. **スキル・エージェント・テンプレートの適用**:
    - ADDF 側を優先して上書きする
    - `addf-` プレフィックスのファイルのみ対象（プロジェクト固有のスキルは保護）
    - スキルのリネームが含まれる場合（旧名が削除され新名が追加される）、対応する `.exp.md` が存在すれば手動リネームを案内する:
      ```
      ! .claude/commands/addf-dev-loop.exp.md
        → .claude/commands/addf-dev.exp.md にリネームを推奨（経験を引き継ぐため）
      ```

13. **CLAUDE.md のマージ**:
    - ADDF テンプレート部分（ブートシーケンス等）を更新する
    - プロジェクト固有の追記部分は保持する
    - 自動マージが困難な場合は diff を表示して手動マージを案内する

14. **その他のファイル**:
    - hooks、addfTools、tests は上書き
    - .claude/addf/knowhow/ADDF/ は上書き（ADDF 由来のノウハウのみ）

14.5. **オプショナルスキルの同期**（「14.5」は後続の番号参照を壊さないための枝番）:
    `.claude/addf/optional/` に変更（追加・更新・リネーム）が含まれる場合、有効化コピーを追従させる:
    ```bash
    uv run --python 3.11 .claude/addf/addfTools/sync-optional-skills.py apply
    ```
    uv が無い環境では `python3` で直接実行する（Python 3.11+ が必要。旧い Python では ERROR 案内が出る）。
    `addf-Behavior.toml` の `[gui-test] enable` に従って配置/撤去される。改変された有効化コピーは
    削除・上書きされず WARNING になるため、表示に従って原本へ取り込んでから再実行する

14.6. **`.gitignore` の ADDF マーカーブロックの更新**（「14.6」は後続の番号参照を壊さないための枝番）:
    `.gitignore` のうち ADDF マーカーブロック（`# --- ADDF Framework (do not remove) ---` 行〜
    `# --- /ADDF Framework ---` 行）**のみ**、クローン元の同ブロックで置換を提案する。
    **ブロック外のプロジェクト固有記述には触れない** — ブロック外に差分がある場合は従来どおり
    手動マージを案内する。

    **置換前の必須検査**: 終了マーカーが欠落・重複していると範囲指定が EOF まで飲み込み、
    ブロック外のプロジェクト固有記述（秘密情報の除外設定を含みうる）を破壊する。以下を
    **すべて**満たすことを確認し、1つでも満たさなければ**置換せず手動マージへフォールバックする**:
    ```bash
    # (1) 開始マーカーがちょうど1つ（出力が 1 でなければ中止）
    grep -c '^# --- ADDF Framework (do not remove) ---$' .gitignore
    # (2) 終了マーカーがちょうど1つ（出力が 1 でなければ中止）
    grep -c '^# --- /ADDF Framework ---$' .gitignore
    # (3) 開始マーカーの行番号 < 終了マーカーの行番号（逆順なら中止）
    grep -n -e '^# --- ADDF Framework (do not remove) ---$' -e '^# --- /ADDF Framework ---$' .gitignore
    ```
    検査を通過したら、双方のブロックを抽出して差分を確認する（差分がなければこのステップはスキップ。
    範囲指定はマーカー行の**全文一致**で行う — 前方一致では類似行を誤って拾いうる）:
    ```bash
    sed -n '/^# --- ADDF Framework (do not remove) ---$/,/^# --- \/ADDF Framework ---$/p' .gitignore > <tmp-dir>/gitignore-block-current
    sed -n '/^# --- ADDF Framework (do not remove) ---$/,/^# --- \/ADDF Framework ---$/p' <tmp-dir>/addf-latest/.gitignore > <tmp-dir>/gitignore-block-latest
    diff -u <tmp-dir>/gitignore-block-current <tmp-dir>/gitignore-block-latest
    ```
    差分があればユーザーに提示し、承認を得てから現在の `.gitignore` のブロック部分を最新版の
    ブロックで置換する。**ブロック内にダウンストリーム独自の追記があった場合、その行は diff に
    「消える行」として現れる — 消える行が本当に ADDF 由来か必ず目視確認し、独自追記が含まれる
    場合はブロック外への退避を案内する**（`.gitignore` にマーカーブロック自体が無い場合は
    追記を提案する） <!-- human-judgment -->

### Phase 6: 完了

15. `.claude/addf/lock.json` を更新する（旧形式の `commit` フィールドがあれば `ref` に置き換える）:
    ```json
    {
      "version": "<new-version>",
      "ref": "v<new-version>",
      "updated_at": "<today>",
      "repository": "<repository-url>"
    }
    ```
    ターゲットがタグではなくコミットハッシュ指定だった場合は、`ref` にそのハッシュを記録する

16. 一時ディレクトリを削除する:
    ```bash
    rm -rf <tmp-dir>
    ```

16.5. **バージョン差分連動のワンショット手順**（「16.5」は後続の番号参照を壊さないための枝番）:
    Phase 4 の差分プレビューで「新規追加」に `.claude/commands/addf-plan-audit.md` が
    含まれていた場合（= 本スキルを初めて含むバージョンを跨いだ更新）、マイグレーション
    完了後に `/addf-plan-audit` を1回実行し、過去 Plan の「完了扱いだが未完了タスクが
    残っている計画」を掘り起こす。手順の実体はスキル本体を参照する（ここには
    埋め込まない — 二重実装＝同期ペアの温床を避ける）。差分にスキルが現れたときだけ
    案内されるため「マイグレーションのたびに実施」にはならない。ただし一回きりの
    厳密な保証ではない — ローカル削除等で本スキルが再度「新規追加」に現れた場合は
    再案内される。実施済みならその旨を答えてスキップしてよい。検出結果への処置は
    オーナー判断 <!-- human-judgment -->

17. 完了レポートを表示する:
    ```
    ✓ ADDF マイグレーション完了
      v0.1.0 → v0.2.0 (ref: v0.2.0)
      適用: 新規 3, 更新 5, 削除 1
      手動確認: .gitignore

    次のステップ:
    1. 変更内容を確認してください (git diff)
    2. 問題なければコミットしてください
    3. 手動マージが必要なファイルを確認してください
    4. /addf-lint で整合を確認してください（オプショナルスキル同期はセクション10）
    ```

## Gotchas

<!-- checklist-lint: skip-section（設計判断の解説。チェックリストではない） -->

- **`rm -rf` の権限**: Phase 6 の一時ディレクトリ削除に `rm -rf` を使用する。`settings.json` のテンプレートには破壊的操作を含めない方針のため、この操作で権限確認が発生する。これは意図的な設計であり、ユーザーが一時ディレクトリの削除を明示的に承認する
- **CLAUDE.md のマージ**: CLAUDE.md はダウンストリームが追記している可能性がある。ADDF のテンプレート部分（ブートシーケンス等）のみ更新し、`@CLAUDE.repo.md` 行以降のプロジェクト固有部分は保持する。自動判定が困難な場合（構造が大幅に変更されている等）は diff を表示して手動マージを案内する
- **リポジトリ URL**: `addf-lock.json` の `repository` フィールドが正確であることが前提。URL が変更された場合は手動で `addf-lock.json` を更新する必要がある

## エラーケース

<!-- checklist-lint: skip-section（エラー時の対応表。チェックリストではない） -->

- `addf-lock.json` が存在しない → ADDF 由来ファイルも無ければ「ロックファイルが見つかりません。`/addf-init` でプロジェクトを初期化してください」。ADDF 由来ファイルがあれば部分導入とみなし、初期正規化モードを提案する（「前提条件」参照）
- ワーキングツリーが汚れている → 中断して案内
- リポジトリのクローンに失敗 → ネットワーク確認を案内
- ロックファイルの `ref` が ADDF リポジトリに存在しない → 浅いクローンを完全クローンに切り替えて再試行。それでも見つからなければ `v<version>` タグにフォールバックする（旧形式 lock の実在しないハッシュ対策）

## 経験の活用
- 実行前に `addf-migrate.exp.md` が存在すれば読み、過去の経験を考慮する
- 実行後、新たな教訓があれば `addf-migrate.exp.md` に追記する
