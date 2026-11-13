---
title: '开始写作：博客格式速查手册'
description: '你的第一篇文章——顺便学会所有常用格式：标题、公式、代码、图片、表格、引用。'
pubDate: 2026-11-13
tags: ['随笔']
---

恭喜，博客已经搭好了！🎉 这篇文章是一份"写作速查手册"——你以后写文章会用到的格式，这里全都有。可以留着当参考，也可以直接删掉。

## 写一篇文章只需要三步

1. 在 `src/content/blog/` 里新建一个 `.md` 文件（文件名会成为网址的一部分，建议用英文，比如 `mel-spectrogram.md`）
2. 写上文件开头的 frontmatter（就是本文最上面 `---` 之间的那几行：标题、描述、日期、标签）
3. 正文用 Markdown 写，保存后浏览器会自动刷新

## 常用格式速查

### 标题与段落

`## 二级标题`、`### 三级标题`；正文直接写段落，空一行就是分段。

### 公式（写算法博客的刚需）

行内公式用单个 `$` 包起来，比如采样定理 $f_s \geq 2 f_{max}$。

独立公式用双 `$$` 包裹：

$$
X(k) = \sum_{n=0}^{N-1} x[n] \, e^{-j 2\pi k n / N}
$$

### 代码

行内代码 `librosa.stft()`，代码块像这样：

```python
import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(0, 1, 16000)        # 1 秒，采样率 16 kHz
x = np.sin(2 * np.pi * 440 * t)     # 440 Hz 正弦波（A4 音符）

plt.plot(t[:320], x[:320])          # 画前 20 ms 的波形
plt.xlabel("time (s)")
plt.show()
```

### 图片

把图片放进 `public/images/` 文件夹，然后在文章里这样引用：

```markdown
![图片说明文字](/images/filename.png)
```

### 表格

| 参数 | 含义 | 常用值 |
| --- | --- | --- |
| `N` | 窗长（FFT 点数） | 512 / 1024 |
| `H` | 跳步（hop size） | N/4 |
| `fs` | 采样率 | 16 kHz |

> 引用块：适合放"写作提示"、他人的观点，或者加粗的重点结论。

### 音频（音频博客的杀手锏 🔊）

如果你想在文章里直接播放音频 demo（比如降噪前后的对比），把音频文件放进 `public/audio/`，然后写一段 HTML：

```html
<audio controls src="/audio/before-denoise.wav"></audio>
```

## 下一步

- 把 `src/consts.ts` 里的博客名、作者名改成你自己的
- 打开 `src/content/blog/stft-intro.md`，那是一篇技术文章的**完整骨架**，照着 TODO 填就行
- 写完后跑 `pnpm build` 确认没有报错，就可以发布上线了（见仓库根目录的 `README.md`）
