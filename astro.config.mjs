// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// 蔡青芬律師事務所 → https://brianann2339.github.io/tsai-law/
// 合署的侯明正律師事務所是另一個獨立網站，見 src/content/site.ts 的 peer 區塊。
// 若日後換自訂網域：改 site、base 改回 '/'，並更新 public/robots.txt 的 Sitemap 行。
export default defineConfig({
  site: 'https://brianann2339.github.io',
  base: '/tsai-law',
  trailingSlash: 'always',
  integrations: [sitemap()],
});
