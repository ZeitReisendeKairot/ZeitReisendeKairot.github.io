# -*- coding: utf-8 -*-
"""
生成"真实 vs 伪造语音"对比素材（波形图 / 线性谱 / 梅尔谱 / 差异图 + 音频）

原理：
  取一段真实人声 → 算它的梅尔谱 → 用 Griffin-Lim 声码器从梅尔谱重构回音频。
  重构出的"伪造"音频与原始音频内容完全相同（同说话人、同文本、同时长），
  但带有声码器的典型痕迹——这正是 TTS/语音转换伪造的一种基本形式。

用法：
  python scripts/make_real_vs_fake.py
  （在博客根目录运行；素材输出到 public/audio/ 和 public/images/）
"""
import numpy as np
import matplotlib

matplotlib.use("Agg")  # 无窗口环境画图
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf
from pathlib import Path

# ---------- 中文显示设置（Windows 自带微软雅黑）----------
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ---------- 参数（文章里会逐一解释）----------
SR = 16000          # 采样率：语音任务标准 16 kHz
DUR = 4.0           # 取 4 秒片段
N_FFT = 1024        # FFT 点数（窗长）
HOP = 256           # 跳步（约 75% 重叠的邻居）
N_MELS = 80         # 梅尔滤波器个数
FMAX = 8000         # 最高频率（奈奎斯特 = 8000 Hz）
N_ITER = 100        # Griffin-Lim 迭代次数，越多越接近但永远"差一口气"

OUT_AUDIO = Path("public/audio")
OUT_IMAGES = Path("public/images")
OUT_AUDIO.mkdir(parents=True, exist_ok=True)
OUT_IMAGES.mkdir(parents=True, exist_ok=True)

# ---------- 1. 载入真实语音，挑一个"有人说话"的 4 秒窗口 ----------
print("载入真实语音（LibriSpeech 样例）...")
y_full, _ = librosa.load(librosa.example("libri1"), sr=SR, mono=True)

win = int(DUR * SR)
rms = librosa.feature.rms(y=y_full, frame_length=2048, hop_length=512)[0]
frame_per_win = win // 512
best = int(np.argmax(np.convolve(rms, np.ones(frame_per_win), mode="valid"))) * 512
real = y_full[best : best + win].copy()
print(f"选中片段：{best/SR:.1f}s ~ {best/SR + DUR:.1f}s，峰值 {np.abs(real).max():.3f}")

# ---------- 2. 制造"伪造"版本：梅尔谱 → Griffin-Lim 重构 ----------
print("Griffin-Lim 重构中（迭代 100 次）...")
mel = librosa.feature.melspectrogram(
    y=real, sr=SR, n_fft=N_FFT, hop_length=HOP, n_mels=N_MELS, fmax=FMAX
)
fake = librosa.feature.inverse.mel_to_audio(
    M=mel, sr=SR, n_fft=N_FFT, hop_length=HOP, n_iter=N_ITER, fmax=FMAX
)

# 长度对齐（重构长度 ≈ 帧数×跳步，和原始可能差几个采样点）
n = min(len(real), len(fake))
real, fake = real[:n], fake[:n]

# 归一化到相同峰值，听感对比才公平（只调音量，不动内容）
real = real / np.abs(real).max() * 0.9
fake = fake / np.abs(fake).max() * 0.9

# 保存音频（网页内嵌播放器用）
sf.write(OUT_AUDIO / "rvf-real.wav", real, SR, subtype="PCM_16")
sf.write(OUT_AUDIO / "rvf-fake.wav", fake, SR, subtype="PCM_16")
print("音频已保存：public/audio/rvf-real.wav, rvf-fake.wav")

# ---------- 3. 三种频谱 ----------
stft_real = np.abs(librosa.stft(real, n_fft=N_FFT, hop_length=HOP))
stft_fake = np.abs(librosa.stft(fake, n_fft=N_FFT, hop_length=HOP))
db_real = librosa.amplitude_to_db(stft_real, ref=np.max)
db_fake = librosa.amplitude_to_db(stft_fake, ref=np.max)

mel_db_real = librosa.power_to_db(mel, ref=np.max)
mel_db_fake = librosa.power_to_db(
    librosa.feature.melspectrogram(
        y=fake, sr=SR, n_fft=N_FFT, hop_length=HOP, n_mels=N_MELS, fmax=FMAX
    ),
    ref=np.max,
)

# ---------- 4. 画图 ----------
def fig_pair(fname, title):
    """两行共享横轴的对比图骨架"""
    fig, axes = plt.subplots(2, 1, figsize=(10, 6.2), sharex=True, dpi=150)
    fig.suptitle(title, fontsize=14, fontweight="bold")
    return fig, axes

# 4.1 波形
fig, axes = fig_pair("rvf-waveform.png", "波形对比：肉眼看几乎一样")
for ax, sig, name in zip(axes, [real, fake], ["真实语音（原始录音）", "伪造语音（Griffin-Lim 重构）"]):
    librosa.display.waveshow(sig, sr=SR, ax=ax, color="#0369a1")
    ax.set_title(name, fontsize=11)
    ax.set_ylabel("幅值")
axes[1].set_xlabel("时间 (秒)")
fig.tight_layout()
fig.savefig(OUT_IMAGES / "rvf-waveform.png")
plt.close(fig)

# 4.2 线性频率 STFT（高频区域的差异在这里最明显）
fig, axes = fig_pair("rvf-stft.png", "线性频率谱对比：注意 4 kHz 以上的高频区")
for ax, D, name in zip(axes, [db_real, db_fake], ["真实语音", "伪造语音"]):
    img = librosa.display.specshow(D, sr=SR, hop_length=HOP, x_axis="time", y_axis="hz", ax=ax, cmap="magma")
    ax.set_title(name, fontsize=11)
    ax.set_ylabel("频率 (Hz)")
axes[1].set_xlabel("时间 (秒)")
fig.colorbar(img, ax=axes, format="%+2.0f dB")
fig.savefig(OUT_IMAGES / "rvf-stft.png")
plt.close(fig)

# 4.3 梅尔谱（人耳视角）
fig, axes = fig_pair("rvf-mel.png", "梅尔谱对比：伪造版的高频「纹理」更平滑")
for ax, M, name in zip(axes, [mel_db_real, mel_db_fake], ["真实语音", "伪造语音"]):
    img = librosa.display.specshow(M, sr=SR, hop_length=HOP, x_axis="time", y_axis="mel", ax=ax, cmap="magma")
    ax.set_title(name, fontsize=11)
    ax.set_ylabel("梅尔频率")
axes[1].set_xlabel("时间 (秒)")
fig.colorbar(img, ax=axes, format="%+2.0f dB")
fig.savefig(OUT_IMAGES / "rvf-mel.png")
plt.close(fig)

# 4.4 差异图（真实 d B − 伪造 d B，蓝=伪造更强，红=真实更强）
diff = mel_db_real - mel_db_fake
fig, ax = plt.subplots(figsize=(10, 4), dpi=150)
v = max(6.0, np.percentile(np.abs(diff), 99))
img = librosa.display.specshow(
    diff, sr=SR, hop_length=HOP, x_axis="time", y_axis="mel", ax=ax,
    cmap="coolwarm", vmin=-v, vmax=v,
)
ax.set_title("梅尔谱差异图（真实 − 伪造，单位 dB）", fontsize=13, fontweight="bold")
ax.set_xlabel("时间 (秒)")
ax.set_ylabel("梅尔频率")
fig.colorbar(img, ax=ax, format="%+2.0f dB")
fig.tight_layout()
fig.savefig(OUT_IMAGES / "rvf-diff.png")
plt.close(fig)

print("图片已保存：rvf-waveform / rvf-stft / rvf-mel / rvf-diff .png")
print("全部完成（音频 + 4 张图）")
