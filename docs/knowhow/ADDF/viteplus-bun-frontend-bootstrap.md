---
title: Vite+ (vp) + Bun でのフロントエンド基盤立ち上げ
created: 2026-06-11
last_verified: 2026-06-11
depends_on: []
status: active
---

# Vite+ (vp) + Bun でのフロントエンド基盤立ち上げ

> 出典: MagiaMagica (コード可視化ツール) Phase 4.0.5〜4.0.9 で確立
> Vite+ 0.1.24 (alpha) + Bun 1.3.9 の実値で確認。
> alpha のため挙動が変わりうる — 数値・コマンドは確認日 2026-06-11 時点。

## 発見した知見

### bunx は vite-plus の CLI を解決できない

- `vite-plus` パッケージの bin は `{oxfmt, oxlint, vp}` の3つで、**パッケージ名と同名の bin がない**
- そのため `bunx vite-plus --help` は**先頭の bin (oxfmt) を実行してしまう**（oxfmt のヘルプが出たら踏んでいる）
- 本体 CLI の名前は **`vp`**
- さらに bun キャッシュ直下の `bin/vp` を直接叩くと native binding (`@voidzero-dev/vite-plus-darwin-arm64`、optional dependency) が見つからず落ちる
- **正解**: 一時ディレクトリで `bun add vite-plus@<ver>` してから `./node_modules/.bin/vp` を使う

### vp create の挙動

- `vp create vite:application --no-interactive` は **vanilla-ts を生成する** (Vue ではない)。Vue にするには生成後に手で Vue 化するか、`vp create vue` (create-vue 委譲) を使う
  - Vite+ 統合 (vp scripts / `vite → vite-plus-core` overrides / CLAUDE.md) が欲しいなら **vite:application で生成して手で Vue 化**する方が綺麗
- create は内部で `vp install` を **PATH から spawn する**。PATH に vp がないと `spawn vp ENOENT` で失敗する → `env PATH="<bootstrap>/node_modules/.bin:$PATH" vp create ...` で回避
- 既定の git hooks 設定はサブディレクトリ検出で自動スキップされる (モノレポ内なら `--no-git` と合わせて無害)

### バージョンピンの採番対応

- 生成直後の package.json は `"vite-plus": "latest"` / `"vite": "npm:@voidzero-dev/vite-plus-core@latest"` の **floating 指定**
- ピンするときは **vite-plus 本体・vite-plus-core・vite-plus-test が同一採番** (例: すべて 0.1.24)
- `vp --version` の出力に出る tsdown 等のバージョン (0.22.x 系) は**別採番**。bun.lock から grep するとき取り違えない

### vp dev は IPv6 (::1) で listen する

- `curl http://127.0.0.1:<port>/` は **000 (接続失敗)** になる。確認は `http://localhost:<port>/` で行う
- バックエンドサーバ (127.0.0.1 bind) への proxy は問題なく通る (vite からバックエンドへの転送は IPv4)

### PORT 環境変数でのポート差し替え

- vite は `PORT` 環境変数を見ない。`vite.config.ts` に `server.port: Number(process.env["PORT"]) || 5173` を書くと、ポート衝突時にハーネス (preview の autoPort) や手動で差し替えられる

### Vue 化の最小セット (vanilla-ts テンプレートから)

1. `bun add vue vue-router pinia` + `bun add -d @vitejs/plugin-vue vue-tsc unocss @unocss/preset-uno @unocss/preset-attributify`
2. `vite.config.ts`: `plugins: [vue(), UnoCSS()]` (defineConfig は `vite-plus` から import — `vite-plus/prefer-vite-plus-imports` ルールが強制)
3. `src/env.d.ts` に `declare module "*.vue"` shim (vite-plus/client は .vue を知らない)
4. build スクリプトは `vue-tsc && vp build` (tsc のままだと .vue を型チェックしない)
5. tsconfig に `strict` は**生成時に入っていない**。手で足す
6. `erasableSyntaxOnly` が生成時から有効 → `enum` は書けない。`type` ベース規約 (type > interface) と整合

### UnoCSS は reset を別パッケージで入れる

- preset-uno は Tailwind と違い **preflight (CSS リセット) を含まない**。`ul` の黒丸や
  `button` の枠がそのまま出たらこれ。`bun add -d @unocss/reset` して main.ts の
  先頭 (virtual:uno.css より前) で `import "@unocss/reset/tailwind.css"`

### Vue + Vite+ alpha の HMR は editing 中に壊れることがある

- `<script setup>` のトップレベル watch + Pinia 構成で、編集中の HMR rerender が
  `TypeError: Cannot read properties of null (reading 'flags')` →
  「[HMR] Something went wrong... Full reload required」になることがある
- **full reload 後は再現しない** (本番ビルド・クリーンロードには影響なし)。
  コンソールにこのスタック (`HMRClient.queueUpdate` 経由) が積もっていても
  実バグと混同しない — クリーンリロード + `window.addEventListener('error')`
  フックで操作テストして切り分ける

### oxfmt は golden/fixture を必ず除外する

- `vp check --fix` はプロジェクト内の JSON/HTML も整形する。バイト等価で比較する
  golden ファイルが再フォーマットされると**ベースラインが静かに壊れる**。
  フロントエンドディレクトリの `.prettierignore` に `golden/` を書く (oxfmt は .gitignore と .prettierignore を読む)

### lint/fmt/型チェックの一括窓口

- `vp check` = oxfmt --check + oxlint + 型チェック。`vp check --fix` で fmt を自動修正
- oxlint ルールは `vite.config.ts` の `lint.rules` に書く (.oxlintrc.json 不要)。`"typescript/consistent-type-definitions": ["error", "type"]` で type 統一規約を機械化

### rust-embed + build.rs での SPA 同梱 (Rust バックエンドに同梱する場合)

- `#[derive(rust_embed::Embed)] #[folder = "../../web/dist"]` で dist をバイナリに同梱。
  HTTP サーバ側は拡張子 → Content-Type の最小マップで配信 (dist に現れる種類だけで足りる)
- **build.rs は「dist が src より新しければスキップ、古ければ bun でビルド、bun 不在なら手順つき panic」**。
  rerun-if-changed には **dist を入れない** (成果物を監視すると bun build 自体が再実行ループを起こす)。
  鮮度判定は src ツリーの最大 mtime と dist/index.html の mtime 比較で十分
- バイナリサイズへの SPA 寄与は誤差 (実測 +0.11MB)。膨らみの主因は他の依存になりがち
  (出典プロジェクトではシンタックスハイライトライブラリ)。
  `[profile.release] strip = "symbols"` + `lto = "thin"` で 7.0 → 5.9MB (約 -16%)
- CI では cargo build の**前に** bun セットアップが要る (build.rs が bun を呼ぶため)。
  cargo build する全 workflow に `oven-sh/setup-bun` を足す

### テスト基盤

- **Vitest は vp 統合済み** (`vp test`)。import は `"vitest"` でなく **`"vite-plus/test"`** —
  `prefer-vite-plus-imports` ルールが自動書き換えする。vitest を devDependencies に
  直接入れる必要はない (型解決も vite-plus が提供)
- **Playwright は vp 非統合** → `@playwright/test` を直接追加し `bunx playwright install chromium`。
  `playwright.config.ts` の webServer に**バックエンドバイナリ起動スクリプト**を置ける
  (cargo build 込みなら timeout 180s)。E2E 対象を rust-embed 配信 (本番経路) にすると
  「バイナリ単体で全機能」の受け入れ基準がそのまま回帰テストになる
- ファイル書き換えを伴う SSE/エラーテストは `workers: 1` で直列化し、`test.beforeEach` で
  fixture を既知内容に戻す (テスト間の持ち越し防止)
- 入れ子 `<details>` の summary を Playwright で叩くとき、`aside details summary` は
  strict mode violation になる — `getByText("…")` のようにテキストで特定する
- Pinia store の単体テスト定型: `setActivePinia(createPinia())` (beforeEach) +
  `vi.stubGlobal("fetch", vi.fn(...))`。store 間分配もこの形で検証できる

### テスト環境の追加注意

- DOMParser を使うコードの Vitest には `bun add -d happy-dom` + vite.config.ts の
  `test: { environment: "happy-dom" }`
- **`test:` 設定を書くと vitest の既定 exclude が外れて Playwright の e2e/ まで拾う** —
  `exclude: ["**/node_modules/**", "e2e/**"]` を明示する
- ヘッドレス撮影は **`playwright screenshot --viewport-size=… --wait-for-timeout=2500 <URL> <out.png>`**
  が良い: Playwright の chromium-headless-shell はユーザーの実 Chrome と完全分離で、
  ローカル Chrome をヘッドレス起動する方式 (プロファイルロック・既存セッション奪取で絡まる) より安定。
  wait-for-timeout を入れないと SPA の fetch 完了前に撮れる
- シェル経由の `pkill -f <パターン>` は **eval されたコマンドライン自身にマッチして自殺する**
  (zsh スナップショット経由の実行で顕在化)。プロセス停止は `pkill -x <プロセス名>` か kill PID で

## 注意点・制約

- Vite+ は alpha。バージョンを上げるときはリリースノートを確認し、本ファイルの「確認日」を更新する
- bun の `packageManager` フィールドは実行中の bun と一致していなくても警告止まりだが、実値に合わせておく
- デザイントークン (色語彙等) をバックエンド側のパレット定義と二重管理する場合は、uno.config.ts 冒頭コメントで同期元を明示する (適用例: UnoCSS theme の色名を Rust 側パレットと同語彙に保つ)

## 参照

- Vite+ ドキュメント: https://viteplus.dev/guide/ (インストール後は node_modules/vite-plus/docs にローカルコピーあり)
