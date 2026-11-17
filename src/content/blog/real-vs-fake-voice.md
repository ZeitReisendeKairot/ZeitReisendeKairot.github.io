---
title: '用眼睛"听"出伪造语音：真伪语音的波形与频谱对比'
description: '同一说话人、同一段话，一真一伪——先听再看，波形几乎一样、频谱藏着痕迹。附完整可复现代码。'
pubDate: 2026-11-17
tags: ['音频算法', '深度学习', '语音安全']
draft: true
---

AI 语音合成已经好到什么程度？你打电话听到的"客服"、短视频里的"明星配音"，很可能不是真人。人耳越来越难分辨，那**眼睛**呢？把声音画成图，真伪之间有没有肉眼可见的痕迹？

这篇文章带你亲手制造一对"完美对照组"——**同一个说话人、念同一段话、时长一模一样**，一个是真实录音，一个是算法伪造——然后逐层拆开看：波形、线性频谱、梅尔谱、差异图。

## 一、素材从哪来？真/伪配对数据的三条路

想对比真伪，最理想的数据是"配对"的：除真假以外一切条件相同。获取方式从易到难：

| 方法 | 说明 | 适合 |
| --- | --- | --- |
| **现场制造（本文）** | 真实录音 → 提取梅尔谱 → 声码器重构回音频 | 入门、完全可控、零下载 |
| 现成数据集 | LJSpeech + WaveFake、ASVspoof 系列 | 正经做检测实验 |
| 自己录音 + 声音克隆 | 录一段自己的声音，用 GPT-SoVITS / XTTS / OpenVoice 克隆 | 最有冲击力的展示 |

本文用第一种：**Griffin-Lim 重构**。它把真实语音压缩成 80 维梅尔谱（扔掉相位信息），再凭空"猜"出相位重构回音频——这是早期 TTS 的标准声码器流程，它产出的音频就是一类典型的"伪造语音"（ASVspoof 2019 的 LA 攻击里，A1–A4 就是声码器类伪造）。

**想用现成数据集的话**：

- [LJSpeech](https://keithito.com/LJ-Speech-Dataset/)：单一女声、13,100 句英语、公有领域——"真实"侧的标准素材
- [WaveFake](https://github.com/dessa-oss/wavefake)：用 6 种声码器伪造 LJSpeech 得到的约 11.8 万条音频——和 LJSpeech 混起来正好是配对数据，完美贴合"同说话人同文本"的需求
- [ASVspoof](https://www.asvspoof.org/)：语音伪造检测领域的权威基准（2019/2021/5 各届），攻击类型最全，需注册下载
- [FakeAVCeleb](https://github.com/Dashkez/FakeAVCeleb)：音视频结合的伪造数据

## 二、先听一听（建议戴耳机 🔊）

真实语音（LibriSpeech 原始录音）：

<audio controls src="/audio/rvf-real.wav"></audio>

伪造语音（Griffin-Lim 从梅尔谱重构，内容完全相同）：

<audio controls src="/audio/rvf-fake.wav"></audio>

乍一听内容一样，但伪造版带着一种"金属感/机器人味"——这就是声码器痕迹。人耳都能察觉的粗糙，图上能看出来吗？

## 三、波形：肉眼看不出区别

![真伪语音波形对比](/images/rvf-waveform.png)

包络几乎重合——当然，内容相同、时长相同（4.0 秒），波形本来就该长得一样。**波形是"内容"的投影，伪造成熟到内容层面毫无破绽。** 想找痕迹，得往频率域看。

## 四、线性频谱：高频区露出马脚

![真伪语音线性频谱对比](/images/rvf-stft.png)

把横轴时间、纵轴频率（线性刻度）摊开看：两者在 4 kHz 以下高度相似，但**真实语音的高频区（4–8 kHz）有丰富细密的纹理，伪造版明显更"干净"**——因为 80 个梅尔滤波器对高频的分辨率很低，高频细节在"压缩成梅尔谱"那一步就已经丢了，Griffin-Lim 变不回来。

## 五、梅尔谱：人耳视角下的细微差异

![真伪语音梅尔谱对比](/images/rvf-mel.png)

梅尔刻度模拟人耳对频率的感知（低频分辨细、高频分辨粗，$m = 2595 \log_{10}(1 + f/700)$）。梅尔谱上的差异更微妙：伪造版的频谱整体更"平滑"、谐波纹理更模糊。坦白说，**只看两张梅尔谱，不标注哪张是假的话，我也分不出来**——这本身就是很好的教学结论。

## 六、差异图：把不同直接画出来

![真伪梅尔谱差异图](/images/rvf-diff.png)

把两张梅尔谱相减（真实 − 伪造），差异就藏不住了：红色区域是真实语音能量更强的地方，集中在高频段和瞬态（辅音起始）处——**真实的"毛边"与伪造的"光滑"**。

## 七、核心代码（完整脚本见仓库 `scripts/make_real_vs_fake.py`）

```python
import librosa
import soundfile as sf

SR, N_FFT, HOP, N_MELS = 16000, 1024, 256, 80

# 1) 真实语音
real, _ = librosa.load("real.wav", sr=SR, mono=True)

# 2) 压缩成梅尔谱（80 维，丢掉相位）
mel = librosa.feature.melspectrogram(
    y=real, sr=SR, n_fft=N_FFT, hop_length=HOP, n_mels=N_MELS, fmax=8000
)

# 3) Griffin-Lim 猜相位、重构音频 → 这就是"伪造"
fake = librosa.feature.inverse.mel_to_audio(
    M=mel, sr=SR, n_fft=N_FFT, hop_length=HOP, n_iter=100, fmax=8000
)
sf.write("fake.wav", fake, SR)

# 4) 画梅尔谱对比
import librosa.display
import matplotlib.pyplot as plt
fig, ax = plt.subplots(2, 1, figsize=(10, 6))
for a, sig, name in zip(ax, [real, fake], ["real", "fake"]):
    M = librosa.power_to_db(
        librosa.feature.melspectrogram(y=sig, sr=SR, n_fft=N_FFT,
                                       hop_length=HOP, n_mels=N_MELS, fmax=8000),
        ref=np.max)
    librosa.display.specshow(M, sr=SR, hop_length=HOP,
                             x_axis="time", y_axis="mel", ax=a)
plt.savefig("mel.png", dpi=150)
```

复现环境：`librosa 0.11` + `matplotlib` + `soundfile`（本文在 conda 环境 ktorch / torch 2.5 下运行）。

## 八、诚实的结论 + 下一篇文章的引子

| 可视化 | 能否看出真伪 | 原因 |
| --- | --- | --- |
| 波形 | ❌ 几乎不能 | 只反映内容包络 |
| 线性频谱 | ✅ 较明显 | 高频细节丢失可见 |
| 梅尔谱 | ⚠️ 有细微痕迹 | 需要经验，不标注难以判断 |
| 差异图 | ✅ 直观 | 但前提是你**已经拿到配对样本** |

更扎心的现实：本文用的 Griffin-Lim 只是"入门级"伪造。现代神经声码器（HiFi-GAN、VITS 的解码器）伪造的语音，连差异图都干净得多——**当肉眼看图失效时，就轮到深度学习出场了：让模型学习人眼看不见的统计与相位痕迹**。这正是 ASVspoof 竞赛里各家检测模型的战场，也是本系列下一篇文章的主题。

## 参考

- [librosa 文档](https://librosa.org/doc/latest/index.html)：`melspectrogram`、`mel_to_audio`
- [WaveFake 论文](https://arxiv.org/abs/2011.05533)：用声码器制造伪造数据集
- [ASVspoof 2019 LA 数据集介绍](https://www.asvspoof.org/)
- Griffin, D., & Lim, J. (1984). Signal estimation from modified short-time Fourier transform. *IEEE TASSP*.
