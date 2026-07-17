import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'ja',
  title: 'AutomatonDevDrive Framework',
  description: 'AIエージェント駆動開発フレームワーク',
  base: '/ADDF/',
  ignoreDeadLinks: false,

  head: [['meta', { name: 'theme-color', content: '#5f67ee' }]],

  themeConfig: {
    nav: [
      { text: 'ガイド', link: '/guide/' },
      { text: 'GitHub', link: 'https://github.com/fruitriin/ADDF' },
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'はじめに',
          items: [
            { text: 'ガイド一覧', link: '/guide/' },
            { text: '詳細セットアップ', link: '/guide/setup' },
            { text: '開発プロセス', link: '/guide/development-process' },
          ],
        },
        {
          text: 'スキル・エージェント',
          items: [
            { text: 'フレームワークスキル', link: '/guide/skills' },
            { text: '組み込みエージェント', link: '/guide/agents' },
          ],
        },
        {
          text: '運用',
          items: [
            { text: 'ADDF バージョンアップ', link: '/guide/migration' },
            { text: 'モデル配分ガイド', link: '/guide/model-allocation' },
            { text: 'PR 本文フォーマット規約', link: '/guide/pr-format' },
            { text: '投機開発ガイド', link: '/guide/speculative-development' },
          ],
        },
        {
          text: '環境別セットアップ',
          items: [
            { text: 'GUI テスト セットアップ', link: '/guide/gui-test-setup' },
            { text: 'Codex で ADDF を使う', link: '/guide/codex-setup' },
          ],
        },
      ],
    },

    socialLinks: [{ icon: 'github', link: 'https://github.com/fruitriin/ADDF' }],

    footer: {
      message: 'AutomatonDevDrive Framework',
    },

    search: {
      provider: 'local',
    },
  },
})
