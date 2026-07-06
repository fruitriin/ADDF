# Plan 0031: コミット済みバイナリの検証可能性（チェックサム照合）

## 実装状況: 完了（実装・ローカル検証・CI（Linux）通過確認 すべて 2026-07-06）

> 実装完了（2026-07-06・worktree 実装）: 第一段階（checksums 照合）を実装し、
> 第二段階（ビルド決定性）は実験で「同一環境内のみ決定的」と実測。
> 詳細は「実装記録」「未決事項の決定」参照。

## 目的

`.claude/addf/tools/` にコミットされている Mach-O バイナリ4種（window-info / capture-window /
annotate-grid / clip-image）について、**改竄・取り違え・片側コミットを機械検出する**
自己整合性検証（バイナリと checksums.sha256 の一致・BINARIES allowlist との一致）を導入する。
**保証しないこと**: ビルド再現性（ソース⇔バイナリの再現）は保証しない — 同一 toolchain 内でのみ
決定的で、環境をまたぐと再現しない実測結果があるため（下記「未決事項の決定」参照）。
悪意あるコミッタが「バイナリと checksums をセットで差し替える」ケースは PR レビューで防ぐ領分に残す
（本 Plan の checksums 導入前後で不変のリスク）。

## 背景

- Plan 0026 レビュー残課題の Medium 指摘:
  「コミット済み Mach-O バイナリ4種の検証手段がない — ソースとバイナリの一致を保証する仕組み
  （チェックサム・再現ビルド・CI 署名）がない。addf-init が無条件コピーする」
- 0026 では独立 Plan 化が推奨されていたが、番号（0027/0028）が別テーマに使われたため、
  本 Plan で正式にバックログ化する
- オーナー指示待ちのセキュリティ項目（deny ルール・addf-init 実物レビュー）とは独立に
  進められる（本 Plan は既存ファイルの検証可能性の話で、権限設計の判断を伴わない）

## 設計の骨子

### 1. チェックサムファイルの導入（第一段階）

- `build.sh` がビルド完了時に `checksums.sha256`（4バイナリの SHA-256）を生成する
- `checksums.sha256` はコミット対象。「このバイナリはビルダーが意図してコミットしたもの」という
  署名代わりになる（改竄・取り違え・ビルド漏れの検出）
- 照合テストを `.claude/addf/tests/tools/` に追加する:
  - **全 OS で実行可能**（`sha256sum` / `shasum -a 256` のフォールバック。ハッシュ計算に
    バイナリの実行は不要なので、非 macOS でも SKIP せず照合できる）
  - バイナリと checksums の不一致 → FAIL。checksums 不在 → ダウンストリーム配布を考慮して
    SKIP か FAIL かは要検討（addf-init がバイナリと checksums をセットでコピーするなら FAIL でよい）

### 2. ソース⇔バイナリの再現検証（第二段階・要実験）

- macOS 環境でのみ: ソースから再ビルドしてハッシュが再現するかを検証する
- Swift コンパイルの出力がビルド環境（Xcode バージョン・アーキテクチャ）に対して
  決定的かは**未検証**。再現しない場合は「再ビルド→ハッシュ更新→差分レビュー」の
  運用手順に留め、機械検証は第一段階の照合までとする

### 3. 「バイナリをリポジトリから外す」選択肢の評価

- 0026 で示された代替案: バイナリを外しローカルビルド必須化
- 影響: GUI ツールは macOS 専用（Plan 0029 フェーズ1で optional 化済み）のため、
  影響を受けるのは mac で GUI テストをオプトインするダウンストリームのみ
- ただし addf-init のコピーリスト・sync-optional-skills の前提が崩れるため、
  本 Plan では**採否の評価まで**とし、採用する場合は独立 Plan を起こす

## 影響範囲

- `.claude/addf/tools/build.sh`（checksums 生成の追加）
- `.claude/addf/tools/checksums.sha256`（新規・コミット対象）
- `.claude/addf/tests/tools/`（照合テスト追加。run-all.sh は既存のグロブで自動的に拾う）
- `/addf-init` コピーリスト（checksums を配布物に含める）と lint ペア5 への影響確認
- Plan 0030（CI）が先行 or 並行する場合、照合テストは CI にもそのまま乗る

## 未決事項の決定（2026-07-06 実装時）

1. **checksums 不在時のセマンティクス** → **upstream=FAIL / downstream=明示 SKIP / 判定不能=SKIP+WARNING（exit 2）**
   - 根拠: 本体では build.sh が生成・コミットするため不在はドリフト（FAIL）。ダウンストリームでは
     checksums 導入前の旧配布に存在せず環境（配布状態）起因のため SKIP。ただし silent 無効化に
     ならないよう SKIP は必ず明示出力する（`sync-lint-design.md` の SKIP 規律）
   - upstream/downstream 判定は「存在≠所有」原則に従い、CLAUDE.repo.md の種別宣言（一次）→
     addf-lock.json の存在（フォールバック）の明示シグナルで行う。`lint-template-sync.py`
     `detect_repo_kind()` の bash ミラーを `verify-checksums.sh` に実装（判定仕様を変えるときは両方更新）
2. **Swift ビルドの決定性** → **同一環境内のみ決定的**（2026-07-06 実測: swiftc 6.3.2 / arm64-macosx26.0）
   - 同一環境で2回ビルド → 4バイナリ全て同一ハッシュ（決定的）
   - コミット済みバイナリとの比較 → 4バイナリ全て不一致（コミット時とは別 toolchain。環境をまたぐ再現は不成立）
   - よって第二段階の機械検証（ソース⇔バイナリの再現検証）は toolchain 固定なしでは成立しない。
     **運用**: ソース変更時は `bash .claude/addf/tools/build.sh` で再ビルド →
     checksums が自動更新される → バイナリと checksums が**セットで**差分に出ることを
     レビューで確認してコミットする（片側コミットは照合テストが FAIL で検出）
3. **ビルド環境の記録を checksums に併記するか** → **併記しない**
   - 根拠: checksums.sha256 を標準の `<sha256>  <ファイル名>` 行のみに保ち、
     `shasum -c` / `sha256sum -c` 互換を維持する（コメント行の扱いは実装間で差がある）。
     ビルド環境は本 Plan（上記2）とコミットログに記録する
4. **バイナリ外し案の評価軸** → 下記「バイナリ外し案の評価」参照

## バイナリ外し案の評価（設計骨子3の採否）

- **安全性**: バイナリを外しローカルビルド必須化しても、checksums 導入前後で残るのは
  「ビルダー自身が悪意あるバイナリと checksums をセットでコミットする」ケースであり、
  これは PR レビューでしか防げない（バイナリ外しでも同じ）。checksums 照合は改竄・取り違え・
  片側コミットの自己整合性を機械検出できる。攻撃者モデル対策（allowlist 外の実行可能ファイル
  混入検出）は本 Plan の verify-checksums.sh に組み込み済み
- **導入摩擦**: 影響は mac で GUI テストをオプトインするダウンストリームのみだが、そこに
  Xcode CLT（swiftc）必須化を持ち込む。addf-init のコピーリスト・sync-optional-skills の前提も崩れ、
  init フローにビルドステップ追加が必要になる
- **提案**: **不採用（現状維持 + checksums 照合）**。理由は導入摩擦（Xcode CLT 必須化と init フロー
  変更）が checksums 照合で得られる自己整合性の上積みメリットに対して大きい。
  将来 CI での自動ビルド + リリースアセット配布に移行する場合は独立 Plan を起こす

## 完了条件

- [x] `bash .claude/addf/tests/run-all.sh` にバイナリ照合テストが含まれ通過する（macOS ローカルで
      15/15 PASS を確認。ハッシュ計算のみでバイナリ実行不要のため非 macOS でも SKIP しない設計）
- [x] CI（ubuntu-latest）で test-binary-checksums.sh が通過する — run 79bbd17 で success 確認
- [x] `build.sh` 実行で checksums が更新され、バイナリだけ・checksums だけの片側コミットを
      テストが検出できる（ドリフト注入テスト Test 3/4 で FAIL を実測）
- [x] addf-init 配布物で照合が成立する（addf-init / addf-migrate は `.claude/addf/tools/` を
      ディレクトリ丸ごとコピーするため checksums.sha256 とテストは自動的に配布物に含まれる。
      加えて旧配布＝checksums 不在時のダウンストリーム挙動を明示 SKIP として定義済み）

## 実装記録（2026-07-06）

- `.claude/addf/tools/build.sh` — ビルド完了時に `generate_checksums` を実行。
  `--checksums-only` フラグでビルドなし再生成（swiftc 不要・全 OS 可。テストの生成経路検証にも使用）。
  sha256sum → shasum -a 256 フォールバック
- `.claude/addf/tools/checksums.sha256` — 新規・コミット対象。現行コミット済みバイナリ4種から生成
- `.claude/addf/tools/verify-checksums.sh` — 照合スクリプト（テスト・CI・手動から共用）。
  exit 0=OK/正当 SKIP、1=ERROR、2=WARNING（addfTools 3値規約）
- `.claude/addf/tests/tools/test-binary-checksums.sh` — 照合テスト8ケース（15 アサーション）。
  mktemp サンドボックスへのドリフト注入で異常系を検証。run-all.sh の `tools/test-*.sh` グロブで自動発見

## レビュー対応（2026-07-06・3ペルソナ集約）

- **C1: 未登録実行可能ファイル検出（attacker）** — `verify-checksums.sh` に allowlist（`EXPECTED_BINARIES`）を
  追加し、TOOLS_DIR 内の実行可能ファイル走査で allowlist にも `checksums.sha256` にも無いファイルを
  「未登録バイナリ検出」ERROR で拒否。攻撃者が evil-tool を紛れ込ませても FAIL する
- **C2: checksums.sha256 name の健全性検証** — 各行パースで name の空・`/`・`..` 含有・BINARIES allowlist
  外を ERROR で拒否（`actual: <hash>` の漏洩防止）
- **H3: detect_repo_kind() 同期契約の機械化** — (a) bash 側 docstring に「同期契約」を明示 /
  (b) `lint-template-sync.py` にペア7を追加し両ファイルの契約文言の存在を機械保証 /
  (c) bash 側の @メンション判定に `strip` 相当の前後空白除去を追加（Python 側と揃える） /
  (d) test に「実プロジェクトの CLAUDE.repo.md/CLAUDE.repo.example.md をサンドボックスに copy して
  upstream 判定を確認するケース」を追加（Test 15）
- **W4: 目的節の保証範囲を正直化** — 「想定されたもの」を「改竄・取り違え・片側コミットの検出
  （自己整合性）。ビルド再現性は保証しない」に置換。バイナリ外し案の不採用理由を「導入摩擦」に整理
- **W5: FAIL に復旧コマンド案内** — バイナリ不在・ハッシュ不一致の FAIL メッセージに、
  `bash .claude/addf/tools/build.sh` 呼び出しと確認手順を併記
- **W6: build.sh の checksums 上書き案内** — `.claude/addf/guides/gui-test-setup.md` に「実行すると
  checksums.sha256 も再生成される。toolchain 差でハッシュが配布物と異なる場合があるが正常」の注記追加
- **W7: build.sh コメント更新** — BINARIES 定義部を「追加漏れは verify の allowlist 検証で
  検出される」に更新
- **W8: `while read -r expected name _` → `while read -r expected name`** — 残余を捨てず name に
  すべて拾う（将来スペース含み名対策）
- **W9: 空 checksums の ERROR テスト追加** — Test 12
- **S10–S15**: build.sh の未知引数 usage 出力 (S10) / gui-test-setup.md への verify-checksums.sh
  単体実行導線 (S11) / SKIP カウンタ削除 (S12) / @メンション heredoc の意図コメント (S13) /
  `chmod 644 checksums.sha256`（build.sh 側で mv 後・S14）/ 追加テスト (S15: Test 9〜15)

## 関連

- Plan 0026（レビュー残課題バックログ）— 本 Plan の出典（Medium 指摘）
- Plan 0029 フェーズ1 — GUI ツールの optional 化。バイナリの利用対象が明確化済み
- Plan 0030（CI 品質ゲート）— 照合テストの搭載先
- `.claude/addf/knowhow/ADDF/sync-lint-design.md` — 「欠如 = SKIP」のダウンストリーム配布設計
