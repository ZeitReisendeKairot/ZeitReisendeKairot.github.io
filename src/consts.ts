// ========== 站点全局信息（改成你自己的！）==========
// 这个文件里的内容会出现在页眉、页脚、关于页和浏览器标签页上

// TODO: 换成你的博客名字
export const SITE_TITLE = '我的音频算法博客';

// TODO: 一句话介绍这个博客
export const SITE_DESCRIPTION = '分享音频算法与深度学习的学习笔记、代码实践与踩坑记录';

// TODO: 换成你的名字或网名
export const PROFILE_NAME = '你的名字';

// ========== 专栏（系列）配置 ==========
// 专栏名 → URL 标识（决定专栏页的网址 /series/标识/）
// 新建专栏时在这里加一行即可
export const SERIES_SLUGS: Record<string, string> = {
  '数学基础': 'math-basics',
  'Python 基础': 'python-basics',
};

// 专栏名 → URL（没有登记的专栏也能用，网址会是编码后的中文名）
export function seriesSlug(name: string): string {
  return SERIES_SLUGS[name] ?? encodeURIComponent(name);
}
