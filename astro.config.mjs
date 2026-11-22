// Astro 配置文件（改配置前可先看文档：https://docs.astro.build/zh-cn/reference/configuration-reference/）
import { defineConfig } from 'astro/config';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

export default defineConfig({
  // 站点地址：用于生成 SEO、站点地图中的链接
  // 已配置为 GitHub Pages 专属域名（用户名.github.io 仓库 → 部署在根路径，无需 base）
  site: 'https://zeitreisendekairot.github.io',

  markdown: {
    // 代码高亮：Shiki（Astro 内置，无需额外安装）
    syntaxHighlight: 'shiki',
    shikiConfig: {
      theme: 'github-dark',
    },
    // 数学公式支持（KaTeX）：
    //   行内公式用 $...$ 包裹，独立公式用 $$...$$ 包裹
    remarkPlugins: [remarkMath],
    rehypePlugins: [rehypeKatex],
  },

  // 旧地址 → 新地址（页面从 /mel-visualizer/ 改名为 /visualizer/）
  redirects: {
    '/mel-visualizer/': '/visualizer/',
  },
});
