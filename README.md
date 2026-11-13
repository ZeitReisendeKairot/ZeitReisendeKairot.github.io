# 我的音频算法博客

> 🌐 已上线：**https://zeitreisendekairot.github.io/**（GitHub Actions 自动部署，push 即发布）

基于 [Astro](https://astro.build) 的静态博客，为**音频算法 / 深度学习**内容定制：

- ✅ 数学公式渲染（KaTeX，写 `$...$` / `$$...$$` 即可）
- ✅ 代码高亮（Shiki，内置）
- ✅ 中文排版友好的主题
- ✅ 免费托管（GitHub Pages / Vercel），写完 `git push` 自动发布

---

## 一、环境要求

- Node.js **18 以上**（[下载地址](https://nodejs.org/)）
- 推荐 pnpm（`npm install -g pnpm`）；没有 pnpm 用 npm 也行，把下文的 `pnpm` 换成 `npm` 即可

## 二、三个常用命令

```bash
pnpm install     # 第一次使用时安装依赖（只需一次）
pnpm dev         # 本地预览：http://localhost:4321，改文章会实时刷新
pnpm build       # 构建正式网站到 dist/ 目录（发布前的自检）
pnpm preview     # 本地预览构建产物（模拟线上效果）
```

## 三、怎么写一篇文章

1. 在 `src/content/blog/` 新建 Markdown 文件，例如 `mel-spectrogram.md`
2. 文件开头写 frontmatter：

   ```yaml
   ---
   title: '文章标题'
   description: '一句话摘要，会显示在列表和搜索引擎里'
   pubDate: 2026-11-13
   tags: ['音频算法', '深度学习']   # 可省略
   draft: true                      # 可省略；true = 草稿，不会出现在正式发布的网站上
   ---
   ```

3. 正文用 Markdown 写。公式、代码、图片、表格、音频的写法见站内文章《开始写作：博客格式速查手册》（即 `src/content/blog/hello-world.md`）。

**frontmatter 字段说明：**

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `title` | ✅ | 文章标题 |
| `description` | ✅ | 一句话摘要 |
| `pubDate` | ✅ | 发布日期 |
| `tags` | ❌ | 标签列表 |
| `updatedDate` | ❌ | 大改后的更新日期 |
| `draft` | ❌ | `true` 时本地可见、线上不发布 |

**素材文件放哪里：**

- 图片 → `public/images/`，文中引用 `/images/文件名.png`
- 音频 → `public/audio/`，文中用 `<audio controls src="/audio/文件名.wav"></audio>` 嵌入

## 四、目录结构导览

```text
Blog/
├── public/                  # 原样复制的静态资源（图片、音频、favicon）
├── src/
│   ├── content/
│   │   └── blog/            # ★ 你的所有文章都在这里
│   ├── components/          # 页眉、页脚等小组件
│   ├── layouts/             # 页面骨架（全站布局 + 文章布局）
│   ├── pages/               # 路由：index.astro 是首页，blog/ 是文章页
│   ├── styles/global.css    # 全站样式（想改字体、配色就在这里）
│   ├── consts.ts            # ★ 博客名、作者名等站点信息
│   └── content.config.ts    # 文章 frontmatter 的校验规则
├── astro.config.mjs         # Astro 配置（公式、代码高亮、站点地址）
├── pnpm-workspace.yaml      # pnpm 的设置（已配置好，一般不用动）
└── package.json
```

日常写作 90% 的时间只跟 `src/content/blog/` 打交道。

## 五、发布上线（二选一）

### 方案 A：Vercel（最省心，推荐）

1. 把整个项目推到一个 GitHub 仓库：

   ```bash
   git init
   git add .
   git commit -m "init blog"
   # 在 github.com 上新建仓库后：
   git remote add origin https://github.com/<你的用户名>/<仓库名>.git
   git push -u origin main
   ```

2. 到 [vercel.com](https://vercel.com) 用 GitHub 账号登录 → Add New Project → 选中仓库 → 直接点 Deploy（Astro 会被自动识别，零配置）
3. 之后每次 `git push`，网站自动重新部署。免费送一个 `xxx.vercel.app` 域名，也可以绑自己的域名

### 方案 B：GitHub Pages（完全免费，纯 GitHub 生态）

1. 同样先把项目推到 GitHub 仓库（步骤同上）。本仓库已内置自动部署配置 `.github/workflows/deploy.yml`
2. 仓库页面 → Settings → Pages → Build and deployment → Source 选 **GitHub Actions**
3. 如果仓库不是 `<用户名>.github.io` 这种专属仓库，需要在 `astro.config.mjs` 里给 site 加路径：

   ```js
   site: 'https://<用户名>.github.io',
   base: '/<仓库名>/',
   ```

## 六、之后可以加的功能（按需）

- 💬 评论系统：[giscus](https://giscus.app/zh-CN)（基于 GitHub Discussions，免费无广告）
- 📡 RSS 订阅：`@astrojs/rss` 包
- 🌙 深色模式：CSS 变量 + 一个开关
- 📊 文章目录（TOC）：侧边栏自动生成章节导航
- 🔍 站内搜索：[pagefind](https://pagefind.app/)

## 常见问题

**Q：构建时报 frontmatter 错误？**
检查是不是缺了 `title` / `description` / `pubDate`，或者日期格式不对（`2026-11-13` 这种就行）。

**Q：pnpm 安装时提示 Ignored build scripts？**
新版 pnpm 出于安全默认拦截依赖的安装脚本。本项目已通过 `pnpm-workspace.yaml` 信任了 `esbuild` 和 `sharp`；如果你的 pnpm 版本较老仍提示，运行 `pnpm approve-builds` 手动允许这两个包即可。用 `npm install` 则没有这个问题。

**Q：公式不渲染？**
行内公式用 `$...$`，独立公式用 `$$...$$`；`$` 和内容之间不要留空格（`$x$` ✅，`$ x $` ❌）。

**Q：想换配色 / 字体？**
改 `src/styles/global.css` 顶部的 `:root` 里的 CSS 变量。
