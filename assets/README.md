# ADDF ロゴアセット

## ファイル構成

```
assets/
├── ADDF ロゴ (standalone).html   # ロゴ全案を含む standalone HTML（React + 埋め込みフォント・画像）
├── logos/                         # HTML から書き出した個別 PNG
│   ├── gh-readme-dark.png         # README バナー (1280×320) ダーク
│   ├── gh-readme-light.png        # README バナー (1280×320) ライト
│   ├── gh-social-h-dark.png       # Social Preview H案 (1280×640) ダーク
│   ├── gh-social-h-light.png      # Social Preview H案 (1280×640) ライト
│   ├── gh-social-f-dark.png       # Social Preview F案 (1280×640) ダーク
│   ├── gh-social-f-light.png      # Social Preview F案 (1280×640) ライト
│   ├── gh-icon-f-dark.png         # アイコン F案 (640×640) ダーク
│   ├── gh-icon-f-light.png        # アイコン F案 (640×640) ライト
│   ├── dark-{A,B,C,D}.png         # ロゴ4案 (1040×600) ダーク
│   ├── light-{A,B,C,D}.png        # ロゴ4案 (1040×600) ライト
│   ├── sil-dark-{E,F,G,H}.png     # シルエット4案 (1040×600) ダーク
│   └── sil-light-{E,F,G,H}.png    # シルエット4案 (1040×600) ライト
└── README.md                      # このファイル
```

## HTML から PNG を再書き出しする手順

### 前提

- Node.js (v18+)
- bun または npm

### 手順

1. 作業ディレクトリを用意して Playwright をインストール:

```bash
mkdir /tmp/clip-logos && cd /tmp/clip-logos
npm init -y && npm install playwright
npx playwright install chromium
```

2. 以下のスクリプトを `clip-logos.mjs` として保存:

```javascript
import { chromium } from 'playwright';
import path from 'path';
import fs from 'fs';

const HTML_PATH = '<path-to>/assets/ADDF ロゴ (standalone).html';
const OUT_DIR = '<path-to>/assets/logos';

fs.mkdirSync(OUT_DIR, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });

await page.goto(`file://${HTML_PATH}`, { waitUntil: 'networkidle', timeout: 30000 });
await page.waitForSelector('#root > *', { timeout: 15000 });
await page.waitForTimeout(3000);

const slots = await page.evaluate(() => {
  const els = document.querySelectorAll('[data-dc-slot]');
  return Array.from(els).map(el => ({
    slot: el.getAttribute('data-dc-slot'),
  }));
});

for (const { slot } of slots) {
  const card = await page.$(`[data-dc-slot="${slot}"] .dc-card`);
  if (!card) { console.log(`skip: ${slot}`); continue; }
  await card.screenshot({ path: path.join(OUT_DIR, `${slot}.png`) });
  console.log(`saved: ${slot}.png`);
}

await browser.close();
```

3. 実行:

```bash
node clip-logos.mjs
```

`assets/logos/` に 24 枚の PNG が書き出されます。
