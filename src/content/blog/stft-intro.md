---
title: '一文搞懂 STFT：短时傅里叶变换'
description: '傅里叶变换到底缺了什么？为什么要加窗？窗长和跳步怎么选？从直觉到公式再到代码。'
pubDate: 2026-11-13
tags: ['音频算法', '数字信号处理']
draft: true
---

> 📌 **这是一篇文章骨架**：每个「TODO」就是留给你填内容的地方，公式和结构已经搭好。
> 填完后把 frontmatter 里的 `draft: true` 删掉（或改成 `false`）即可发布。

## 1. 问题：傅里叶变换缺了什么？

TODO：先说清楚痛点，读者才有动力读下去。可以围绕这几个点展开：

- 对一段完整语音做 FFT，得到的频谱**完全看不出"什么时候"出现了什么频率**
- 举例：一句话前半段是干净人声、后半段是噪声，FFT 只能告诉你"有哪些频率"，不能告诉你"何时"
- 一句话结论：我们需要**时间与频率同时局部化**的分析工具

## 2. 直觉：给声音拍"连续快照"

TODO：用类比把直觉讲清楚。参考思路：

- 相机拍高速运动：快门越短，单张越清晰，但每张包含的信息越少
- STFT 的本质就是"滑动一个窗口，对每个窗口内的信号分别做 FFT"
- 配图建议：一张"分帧 + 加窗"的示意图（TODO：画好后放进 `public/images/`）

## 3. 数学定义

STFT 的定义：

$$
X(m, k) = \sum_{n=0}^{N-1} x[n + mH] \, w[n] \, e^{-j 2\pi k n / N}
$$

其中：

| 符号 | 含义 | 备注 |
| --- | --- | --- |
| $x[n]$ | 离续信号 | 采样率 $f_s$ |
| $w[n]$ | 窗函数 | 汉宁窗、汉明窗常用 |
| $N$ | 窗长（FFT 点数） | 决定频率分辨率 |
| $H$ | 跳步（hop size） | 决定时间分辨率 |
| $m$ | 帧索引 | 第 $m$ 帧 |
| $k$ | 频带索引 | 第 $k$ 个频点 |

两个关键分辨率（把这对矛盾讲清楚，文章就有深度了）：

$$
\Delta f = \frac{f_s}{N} \qquad \Delta t = \frac{H}{f_s}
$$

TODO：解释"不确定性原理"式的权衡——窗长越大，频率越准、时间越糊；窗长越小，时间越准、频率越糊。语音处理常用 20–40 ms 窗长，正是这对矛盾里的折中。

## 4. 代码实战

```python
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

# 1. 读音频（TODO: 换成你自己的音频文件）
y, sr = librosa.load("sample.wav", sr=16000, mono=True)

# 2. STFT：窗长 512（= 32 ms @ 16 kHz），跳步 128（75% 重叠）
N, H = 512, 128
S = np.abs(librosa.stft(y, n_fft=N, hop_length=H, window="hann"))

# 3. 画幅度谱（dB 刻度）
S_db = librosa.amplitude_to_db(S, ref=np.max)
fig, ax = plt.subplots(figsize=(10, 4))
img = librosa.display.specshow(S_db, sr=sr, hop_length=H,
                               x_axis="time", y_axis="hz", ax=ax)
fig.colorbar(img, ax=ax, format="%+2.0f dB")
ax.set_title("STFT magnitude spectrogram")
plt.tight_layout()
plt.savefig("spectrogram.png", dpi=150)
plt.show()
```

TODO：把生成的频谱图复制到 `public/images/` 后插入文章，并写你观察到的现象：

![STFT 频谱图示例](/images/spectrogram.png)

## 5. 实验与踩坑（文章的灵魂 ✨）

TODO：这是全文最有价值的部分，建议做一个小实验 + 记录你踩的坑。一些灵感：

- 同一段音频，分别用 $N = 128 / 512 / 2048$ 做 STFT，把三张频谱图放一起对比
- 跳步 $H$ 取得太大（不重叠）会怎样？
- 忘了加窗（等效于矩形窗）时的频谱泄漏有多难看？
- 深度学习里为什么常喂 log-mel 而不是原始 STFT？（可以留作下一篇文章的引子）

## 6. 总结

TODO：三句话以内，把全文压缩成几条要点。例如："STFT = 分帧 + 加窗 + FFT，本质是在时间分辨率和频率分辨率之间做折中。"

## 参考

- [librosa STFT 文档](https://librosa.org/doc/latest/generated/librosa.stft.html)
- TODO: 补上你读过的教材 / 论文 / 博客链接
