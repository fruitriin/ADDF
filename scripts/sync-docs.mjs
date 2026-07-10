#!/usr/bin/env node
// .claude/addf/guides/*.md を docs/guide/*.md へコピーする（単一ソースは .claude/addf/guides/）。
// docs/guide/*.md はビルド時生成物のため .gitignore 対象。手で編集しないこと。
//
// ガイド内の相対リンクはコピー元のディレクトリ深さを前提にしているため、そのままでは
// docs/guide/ に配置したときにリンク切れになる。リンク先を解決し、他のガイドを指す場合は
// docs/guide/ 内の相対パスへ、docs サイトに含まれないリポジトリファイルを指す場合は
// GitHub の blob URL へ書き換える。

import { readdirSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join, dirname, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const repoRoot = join(__dirname, '..')
const srcDir = join(repoRoot, '.claude/addf/guides')
const destDir = join(repoRoot, 'docs/guide')
const GITHUB_BLOB_BASE = 'https://github.com/fruitriin/ADDF/blob/main/'
const GITHUB_RAW_BASE = 'https://raw.githubusercontent.com/fruitriin/ADDF/main/'

mkdirSync(destDir, { recursive: true })

const files = readdirSync(srcDir).filter((f) => f.endsWith('.md'))
const guideNameSet = new Set(files.map((f) => f.replace(/\.md$/, '')))

// `!` を先頭キャプチャに含めて画像リンク（`![alt](path)`）と通常リンクを区別する
const linkPattern = /(!?\[[^\]]*\]\()(\.\.?\/[^)]+)(\))/g

function rewriteLinks(content, sourceFile) {
  return content.replace(linkPattern, (match, prefix, href, suffix) => {
    const isImage = prefix.startsWith('!')

    // アンカー（`#section`）は解決対象から切り離し、書き換え後のリンクに戻す
    const hashIndex = href.indexOf('#')
    const hrefPath = hashIndex === -1 ? href : href.slice(0, hashIndex)
    const fragment = hashIndex === -1 ? '' : href.slice(hashIndex)

    const resolvedAbs = resolve(dirname(sourceFile), hrefPath)
    const repoRelative = relative(repoRoot, resolvedAbs)

    // 他のガイドを指している場合は docs/guide/ 内の相対パスに書き換える（画像は対象外）
    const guideMatch = repoRelative.match(/^\.claude\/addf\/guides\/([^/]+)\.md$/)
    if (!isImage && guideMatch && guideNameSet.has(guideMatch[1])) {
      return `${prefix}./${guideMatch[1]}${fragment}${suffix}`
    }

    // 画像は blob（HTML ページ）ではなく raw（実体）を指す必要がある
    const base = isImage ? GITHUB_RAW_BASE : GITHUB_BLOB_BASE
    return `${prefix}${base}${repoRelative}${fragment}${suffix}`
  })
}

for (const file of files) {
  const srcPath = join(srcDir, file)
  const content = readFileSync(srcPath, 'utf-8')
  writeFileSync(join(destDir, file), rewriteLinks(content, srcPath))
}

const indexBody = `# ガイド一覧

> このページと配下のガイドは \`.claude/addf/guides/\` から自動生成されています（単一ソース）。
> 内容を直したい場合は \`docs/guide/\` ではなく元ファイルを編集してください。

${files
  .map((file) => `- [${file.replace(/\.md$/, '')}](./${file.replace(/\.md$/, '')})`)
  .join('\n')}
`

writeFileSync(join(destDir, 'index.md'), indexBody)

console.log(`docs/guide/ に ${files.length} 件のガイドを同期しました`)
