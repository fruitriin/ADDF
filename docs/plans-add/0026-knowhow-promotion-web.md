# Plan: Web 系 knowhow 3本の昇格 (Vite+/Bun・判定ゲート UI 計画・deprecated 保守方針)

## 実装状況: 完了（2026-06-11）

## きっかけ

- 元となったプロンプト/会話: MagiaMagica Phase 4 フロントエンド系列 (Phase 4.0.5〜4.0.9) で蓄積した knowhow の昇格。オーナー指示 2026-06-11
- アイデアの出典: MagiaMagica の `docs/knowhow/` に蓄積された Web フロントエンド系知見のうち、ADDF 利用プロジェクト全般に通用するもの
- 関連Issue: なし

## 動機

MagiaMagica の Phase 4 (フロントエンド充実) で確立した知見のうち、以下3点は
プロジェクト固有ではなく「ADDF 利用プロジェクトで Web UI を立ち上げる」場面全般に
通用するため、`docs/knowhow/ADDF/` へ昇格する。

1. **Vite+ (vp) + Bun のツールチェーン知見** — alpha ツールチェーンの罠 (bin 解決・採番・IPv6 listen)、Vue 化最小セット、rust-embed 同梱、テスト基盤の実値知見
2. **目視判定ゲート付き UI 計画の運用** — UI 実装をマイルストーン分割しオーナー判定を同期点にするプロセス、URL 全状態同期による判定素材の低コスト化、機能等価移植・画素等価検証の方法論
3. **deprecated モジュールへの保守方針コメント** — 段階的移行の過渡期に、後続セッションの AI が捨てるコードへ無駄な投資をするのを防ぐコメントパターン

## 設計

### 昇格対象と汎用化方針

| # | ファイル | ソース | 方針 |
|---|---|---|---|
| 1 | `docs/knowhow/ADDF/viteplus-bun-frontend-bootstrap.md` | MagiaMagica 同名ファイル | 汎用化して昇格 |
| 2 | `docs/knowhow/ADDF/milestone-gated-ui-plan.md` | MagiaMagica 同名ファイル | 汎用化して昇格 |
| 3 | `docs/knowhow/ADDF/deprecated-module-maintenance-policy.md` | MagiaMagica のコード実例 (deprecated レンダラの冒頭コメント) | 新規書き起こし |

### 汎用化ルール

- frontmatter (title / created / last_verified / depends_on / status) を付与
- 冒頭に出典行「> 出典: MagiaMagica (コード可視化ツール) Phase 4.0.5〜4.0.9 で確立」を残し、アイデアの系譜を追跡可能にする
- プロジェクト固有の語彙・パス (魔法陣、palette.rs、magia serve、crates/... 等) は一般的な言い回しに置換、または「出典では〜」「適用例: 〜」の括弧書きで簡潔に残す
- 「プロジェクトへの適用」節は削除し、必要な内容は本文に吸収
- 「参照」節のプロジェクト内パスは削除 (外部 URL は残す)
- **技術的内容 (パターン・落とし穴・コマンド・数値) は削らない** — 汎用化は語彙の置換であって要約ではない

## 影響範囲

| ファイル | 変更 |
|---|---|
| `docs/knowhow/ADDF/viteplus-bun-frontend-bootstrap.md` | 新規 (昇格) |
| `docs/knowhow/ADDF/milestone-gated-ui-plan.md` | 新規 (昇格) |
| `docs/knowhow/ADDF/deprecated-module-maintenance-policy.md` | 新規 (書き起こし) |
| `docs/knowhow/INDEX.addf.md` | 3行追記 |
| `docs/plans-add/0026-knowhow-promotion-web.md` | 本計画 |

コード・スキル・テンプレートへの変更はなし (ドキュメントのみ)。
