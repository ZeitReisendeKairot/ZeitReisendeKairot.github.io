---
title: '用眼睛"听"出伪造语音：真伪语音的波形与频谱对比'
description: '同一说话人、同一段话，一真两伪（MelGAN / HiFi-GAN）——先听再看，波形几乎一样、频谱藏着痕迹，数据告诉我们为什么肉眼不够用。'
pubDate: 2026-11-17
tags: ['音频算法', '深度学习', '语音安全']
draft: true
---

AI 语音合成已经好到什么程度？你打电话听到的"客服"、短视频里的"明星配音"，很可能不是真人。人耳越来越难分辨，那**眼睛**呢？把声音画成图，真伪之间有没有肉眼可见的痕迹？

这篇文章用**真实数据集**做对照实验——同一位说话人念同一句话（LJSpeech 的 `LJ014-0227`），三个版本：

1. **真实**：LJSpeech 原始录音
2. **伪造 A**：MelGAN 声码器合成（WaveFake 数据集，2020 年前后的技术）
3. **伪造 B**：HiFi-GAN 声码器合成（WaveFake 数据集，现代神经声码器）

## 一、数据从哪来？

想对比真伪，最理想的数据是"配对"的：除真假以外一切条件相同。

| 数据集 | 说明 |
| --- | --- |
| **LJSpeech + WaveFake（本文使用）** | LJSpeech：单一女声 13,100 句英语、公有领域；WaveFake：用 MelGAN / HiFi-GAN / WaveGlow 等 6 种声码器对**同样的句子**合成伪造版——天然完美配对 |
| ASVspoof 2019 LA / 2021 / 5 | 语音伪造检测的权威基准（19 种 TTS/VC/声码器攻击），做检测实验绕不开 |
| FakeAVCeleb | 音视频结合的伪造数据 |
| 自己录音 + 声音克隆 | 用 GPT-SoVITS / XTTS / OpenVoice 克隆自己的声音，最有冲击力 |

> 为什么伪造版和真实版内容一致？因为 TTS 系统的工作方式就是：文本（或从真实语音提取的声学特征）→ 声码器 → 波形。声码器伪造（vocoder-based spoof）是一类经典攻击，ASVspoof 2019 LA 的 19 种攻击里就有 4 种属于此类。

## 二、先听一听（建议戴耳机 🔊）

真实语音（LJSpeech 原始录音）：

<audio controls src="/audio/rvf-real.wav"></audio>

伪造 A：MelGAN 声码器合成——注意听一种"沙沙/浑浊"的底噪感：

<audio controls src="/audio/rvf-melgan.wav"></audio>

伪造 B：HiFi-GAN 声码器合成——听感已非常接近真实：

<audio controls src="/audio/rvf-hifigan.wav"></audio>

## 三、波形：三个版本几乎重合

![真伪语音波形对比](/images/rvf-waveform.png)

内容相同、时长相同（3.6 秒），波形本来就该长得一样。**波形是"内容"的投影，成熟的伪造在内容层面毫无破绽**——想找痕迹得去频率域。

## 四、线性频谱：高频区开始露马脚

![真伪语音线性频谱对比](/images/rvf-stft.png)

横轴时间、纵轴线性频率。对比三张图：MelGAN 版（中）的高频纹理明显更"平"——老式声码器合成的谐波和噪声结构更简单；HiFi-GAN 版（下）高频信息丰富得多，肉眼已经需要仔细找茬。

## 五、梅尔谱：人耳视角，也是"快要看不出"的视角

![真伪语音梅尔谱对比](/images/rvf-mel.png)

梅尔刻度模拟人耳的频率感知（低频分辨细、高频分辨粗，$m = 2595\log_{10}(1+f/700)$）。我在生成图片的同时算了一组**数值证据**：

| 指标 | 真实 vs MelGAN | 真实 vs HiFi-GAN |
| --- | --- | --- |
| 梅尔谱相关系数 | 0.985 | **0.978** |
| 4–8 kHz 平均能量 | 真实 −2.7 dB / MelGAN −3.0 dB | **HiFi-GAN −1.1 dB（比真实还高 1.6 dB！）** |

两个发现值得写进笔记本：

1. **两种伪造的梅尔谱都和真实高度相关（0.98+）**——连"数格子"级别的统计差异都极其微小；
2. **"伪造=高频弱"这条直觉并不总成立**：HiFi-GAN 的高频能量甚至**超过**真实录音。神经声码器会"无中生有"地生成高频噪声成分，简单的频段能量规律靠不住。

## 六、差异图：把不同直接画出来

![真伪梅尔谱差异图](/images/rvf-diff.png)

把梅尔谱逐点相减（真实 − 伪造），两栏共用同一色标，深色=差异大。可以看到：MelGAN（左）的差异区大而杂，HiFi-GAN（右）的差异区小且集中在细碎纹理上——**伪造技术在进步，肉眼可见的破绽在收敛**。

## 七、🎛️ 交互实验室：自己动手调参数

下面的工具直接在你的浏览器里实时计算频谱（JS 手写 FFT + 梅尔滤波器组，无服务器）。**试试同一套参数分别加载三个音频，对比差异图之外你还能发现什么**；再拖动 n_fft 从 256 到 4096，亲眼看时间/频率分辨率的跷跷板：

<iframe src="/mel-visualizer/" style="width:100%;height:860px;border:1px solid #e5e7eb;border-radius:10px" loading="lazy" title="交互式频谱实验室"></iframe>

也可以单独打开全屏版：[交互式频谱实验室](/mel-visualizer/)。

## 八、核心代码

生成本文全部图表的脚本在仓库 `scripts/make_real_vs_fake.py`，核心只有几步：

```python
import librosa, soundfile as sf

SR, N_FFT, HOP, N_MELS, FMAX = 22050, 1024, 256, 80, 8000

real,  _ = librosa.load("LJ014-0227.wav", sr=SR)   # LJSpeech 真实
melgan, _ = librosa.load("melgan.wav",     sr=SR)  # WaveFake 伪造 A
hifi,   _ = librosa.load("hifiGAN.wav",    sr=SR)  # WaveFake 伪造 B

# 梅尔谱（80 个滤波器、只保留 8 kHz 以下）
mel = librosa.power_to_db(
    librosa.feature.melspectrogram(y=real, sr=SR, n_fft=N_FFT,
                                   hop_length=HOP, n_mels=N_MELS, fmax=FMAX),
    ref=np.max)

# 线性 STFT 谱（看高频用这个）
stft = librosa.amplitude_to_db(
    np.abs(librosa.stft(real, n_fft=N_FFT, hop_length=HOP)), ref=np.max)
```

数值统计（相关系数、频段能量）的算法同样在脚本里，欢迎扩展。

## 九、结论：为什么"看图"之后还需要"模型"

| 可视化 | 能否看出真伪 | 说明 |
| --- | --- | --- |
| 波形 | ❌ | 只反映内容包络 |
| 线性频谱 | ⚠️ MelGAN 可见，HiFi-GAN 难 | 高频纹理差异随技术进步在收敛 |
| 梅尔谱 | ❌ 肉眼极难 | 相关系数 0.98+，统计差异也在消失 |
| 差异图 | ✅ 但需要配对样本 | 实战中你拿不到"真值" |

把这四行连起来读，就是整个语音伪造检测领域的立身之本：**肉眼和简单统计正在失效，而模型可以学到相位、调制、子带相关性这些图上不直观的特征**——这正是 ASVspoof 竞赛里各家检测模型的主战场，也是本系列下一篇文章的主题。

## 参考

- [LJSpeech](https://keithito.com/LJ-Speech-Dataset/)（真实语音，公有领域）
- [WaveFake](https://github.com/dessa-oss/wavefake)（6 种声码器伪造数据集）
- [ASVspoof Challenge](https://www.asvspoof.org/)（伪造检测权威基准）
- [librosa 文档](https://librosa.org/doc/latest/index.html)
- Kong et al. (2020). HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis. *NeurIPS*.
