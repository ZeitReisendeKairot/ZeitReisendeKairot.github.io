// 内容集合（content collections）配置：定义"文章"这类内容的规则
// 文章都放在 src/content/blog/ 目录下，frontmatter（文件开头 --- 之间的部分）
// 必须符合这里定义的 schema，写错了构建时会明确报错——这是好事，帮你挡住低级失误。
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    // 标签可写可不写；写了会显示在文章标题下方
    tags: z.array(z.string()).default([]),
    // 系列名（可选）：同一系列的文章互相有关联（如「数学基础」系列：
    // sin/cos → e → i → π → 欧拉公式 → 傅里叶……），显示为文章头部的系列徽章
    series: z.string().optional(),
    // true = 草稿：本地 dev 预览可见，正式构建发布时不会出现在网站上
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
