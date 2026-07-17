# Plan: addf-init コピーリストの鮮度回復と機械化

## 実装状況: 完了（2026-06-10、PR #11）

edge: derived-from 0015

## 関連 Plan

- [Plan 0015: 既存プロジェクトへの ADDF 組み込み](0015-existing-project-install.md) — 本 Plan の起票元（0015 の突合確認で発見された残差分を切り出し）

全4項目を実装した。機械化は案 (a)（lint へのペア5追加）を採用:
- カテゴリ1に `Questions.example.md` / `Dashboard.example.md` を追加、Progress.md 生成元を `ProgressTemplate.md` と明記
- .gitignore マージブロック例は計画外の改善として「クローン元 `<tmp>/addf-source/.gitignore` を正とする」方式に変更（列挙の陳腐化を構造的に排除。本体 .gitignore とのドリフトを実装中に発見したため）
- `lint-template-sync.py` にペア5（CLAUDE.md 参照 ⇔ addf-init コピーリスト + .gitignore ADDF ブロックのカバレッジ・WARNING・欠如時 SKIP）を追加。テストは9本・23 assertion
- E2E 手動シナリオ `.claude/addf/tests/skills/test-addf-init-external.md` を新設

品質ゲート結果: code-review は Critical/High なし（W1: コードブロック内誤抽出 / W2: マーカーブロック読み取り堅牢化 → 修正済み）。配布安全性検査も Critical/High なし（.gitignore 欠如時の WARNING はテスト9で仕様として固定化）。

### 記録のみ（Low/Info・未対応）

- gitignore エントリの末尾スラッシュなしディレクトリ指定（例: `.claude/logs`）はペア5のディレクトリマッチで検出漏れしうる（現状の .gitignore は全て `/` 付きのため実害なし）
- E2E シナリオでローカルパスに読み替えた場合、`https://` スキームチェックの検証がバイパスされる（シナリオに注記済みの運用前提）
- ペア5の検査対象は CLAUDE.md のみ（テンプレート群の参照はディレクトリ丸ごとコピーでカバーされるため意図的。lint の docstring に明記済み）

## Context

Plan 0015（既存プロジェクトへの ADDF 組み込み）は 2026-03-21 のコミット `b971d97` で実装済みだが、
その後の Plan 0016〜0021 で追加されたファイルが `addf-init.md` の Phase 3 コピーリストに反映されておらず、
鮮度ドリフトが発生している。2026-06-10 の突合確認で以下の不足が判明した。

なお `addf-*.md` のようなグロブ指定のエントリはドリフトを免れており、被害は明示列挙されたファイルに限られる。
「手書き列挙は腐る」という構造問題への対処（機械化）も本計画に含める。

## 不足項目

### 1. コピーリストの鮮度ドリフト（実害あり・最優先）

Phase 3 カテゴリ1（無条件コピー）に以下が載っていない:

- `.claude/addf/Questions.example.md`（Plan 0016 で追加）
- `.claude/addf/Dashboard.example.md`（Plan 0016 で追加）

配布される CLAUDE.md テンプレートは「書式は `.claude/addf/Dashboard.example.md` / `.claude/addf/Questions.example.md` を参照」と
両ファイルを参照しているため、現状の外部起動フローで導入したダウンストリームプロジェクトでは**参照切れ**になる。
また Questions.md 自体も冒頭で「質問の書式は `.claude/addf/Questions.example.md` の「Q例」に従う」と参照している。

**対応**: カテゴリ1リストに2ファイルを追加する。

### 2. Progress.md の生成元テンプレートが曖昧

Phase 3 カテゴリ3に「`.claude/addf/Progress.md` — テンプレートから生成」とだけあり、
`ProgressTemplate.md`（ダウンストリーム用）と `ProgressTemplate.addf.md`（ADDF 本体用）の
どちらを使うか明記されていない。実行する LLM が間違う余地がある。

**対応**: 「`.claude/addf/templates/ProgressTemplate.md` から生成（`.addf.md` は本体用のため使わない）」と明記する。

### 3. 外部起動フローの E2E 検証シナリオがない

Plan 0015 の検証項目は `run-all.sh` と `/addf-init check` のみで、
肝心の「WebFetch → tmp クローン → 既存プロジェクトへマージ」フロー自体のテストシナリオがない。

**対応**: `.claude/addf/tests/skills/` に自然言語シナリオを追加する（手動実行枠）。
シナリオ内容: ダミーの既存プロジェクト（CLAUDE.md・.gitignore・settings.json あり）に外部起動で導入し、
干渉チェック・マージ結果・参照切れの有無を確認する。

### 4. コピーリストの機械化（再発防止）

コピーリストが手書き列挙のため、今後ファイルを追加するたびに再びドリフトする。
Feedback.md の改善アクション「意思で覚えず機械化する」（`.claude/addf/knowhow/ADDF/sync-lint-design.md`）に倣う。

**対応**: 以下のいずれか（実装時に選択。a を推奨）:
- (a) `.claude/addf/addfTools/lint-template-sync.py` に「リポジトリ実体 ⇔ addf-init コピーリスト」の検査を追加する。
  CLAUDE.md テンプレートが `@` や バッククオートで参照する `.claude/` 配下のファイルが
  コピーリスト（グロブ含む）でカバーされているかを検証する
- (b) コピーリストをグロブ＋除外方式（例: `.claude/*.example.md`）に書き換え、明示列挙を減らす

(a) を選んだ場合、新しい同期ペアが lint に追加されるため、Feedback.md の
「新たな同期ペアが生まれたら lint にペアを追加すること」を満たすこと。

## 変更対象ファイル

| ファイル | 変更 |
|---|---|
| `.claude/commands/addf-init.md` | カテゴリ1に example 2ファイル追加、Progress.md 生成元の明記 |
| `.claude/addf/tests/skills/`（新規シナリオ） | 外部起動フローの E2E シナリオ |
| `.claude/addf/addfTools/lint-template-sync.py`（案 a の場合） | コピーリスト検査（ペア5）の追加 |
| `.claude/addf/tests/tools/test-template-sync.sh`（案 a の場合) | ペア5のテスト追加 |

## 検証

1. `bash .claude/addf/tests/run-all.sh` が通過すること
2. `/addf-lint` のテンプレート同期チェックが通過すること
3. （可能なら）ダミープロジェクトへの外部起動導入で参照切れがないこと
