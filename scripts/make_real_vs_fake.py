# -*- coding: utf-8 -*-
"""
生成"真实 vs 伪造语音"对比素材（LJSpeech + WaveFake 真实数据集版）

数据来源：
  真实语音   LJSpeech-1.1（单一说话人，公有领域）
  伪造语音 A WaveFake / ljspeech_melgan    —— 老式声码器（2020 前后，痕迹明显）
  伪造语音 B WaveFake / ljspeech_hifiGAN   —— 现代神经声码器（痕迹细微）
  三者是同一个人念同一句话（LJ014-0227），时长一致——完美的对照实验。

用法：
  1. 准备三个 wav 到 DATA_DIR（见下），分别命名 real.wav / melgan.wav / hifiGAN.wav
  2. 在博客根目录运行：python scripts/make_real_vs_fake.py
"""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ---------- 数据与参数 ----------
DATA_DIR = Path(".tools/ljpair")   # LJ014-0227.wav / melgan.wav / hifiGAN.wav
SR = 22050                          # LJSpeech 原生采样率
N_FFT, HOP, N_MELS, FMAX = 1024, 256, 80, 8000
HF_LO, HF_HI = 4000, 8000           # 统计用的高频段

OUT_AUDIO = Path("public/audio")
OUT_IMAGES = Path("public/images")
OUT_AUDIO.mkdir(parents=True, exist_ok=True)
OUT_IMAGES.mkdir(parents=True, exist_ok=True)

MEL_KW = dict(sr=SR, n_fft=N_FFT, hop_length=HOP, n_mels=N_MELS, fmax=FMAX)

# ---------- 1. 载入三个版本，统一长度与响度 ----------
def load_norm(name):
    y, _ = librosa.load(DATA_DIR / name, sr=SR, mono=True)
    return y / np.abs(y).max() * 0.9  # 统一峰值响度，对比才公平

real = load_norm("LJ014-0227.wav")
melgan = load_norm("melgan.wav")
hifi = load_norm("hifiGAN.wav")
n = min(len(real), len(melgan), len(hifi))
real, melgan, hifi = real[:n], melgan[:n], hifi[:n]

sf.write(OUT_AUDIO / "rvf-real.wav", real, SR, subtype="PCM_16")
sf.write(OUT_AUDIO / "rvf-melgan.wav", melgan, SR, subtype="PCM_16")
sf.write(OUT_AUDIO / "rvf-hifigan.wav", hifi, SR, subtype="PCM_16")

# ---------- 2. 各种谱 ----------
def logmel(y):
    M = librosa.power_to_db(librosa.feature.melspectrogram(y=y, **MEL_KW), ref=np.max)
    return M

def lin_db(y):
    S = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP))
    return librosa.amplitude_to_db(S, ref=np.max)

mel_r, mel_m, mel_h = logmel(real), logmel(melgan), logmel(hifi)
lin_r, lin_m, lin_h = lin_db(real), lin_db(melgan), lin_db(hifi)

# ---------- 3. 数值统计（写进文章的"证据"）----------
def corr(a, b):
    return np.corrcoef(a.ravel(), b.ravel())[0, 1]

def hf_energy_db(y):
    S = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP)) ** 2
    freqs = librosa.fft_frequencies(sr=SR, n_fft=N_FFT)
    band = (freqs >= HF_LO) & (freqs < HF_HI)
    return 10 * np.log10(S[band].mean() + 1e-12)

print("=== 数值统计 ===")
print(f"梅尔谱相关系数  真实vs MelGAN : {corr(mel_r, mel_m):.4f}")
print(f"梅尔谱相关系数  真实vs HiFiGAN: {corr(mel_r, mel_h):.4f}")
print(f"4-8kHz 能量      真实        : {hf_energy_db(real):.1f} dB")
print(f"4-8kHz 能量      MelGAN      : {hf_energy_db(melgan):.1f} dB")
print(f"4-8kHz 能量      HiFi-GAN    : {hf_energy_db(hifi):.1f} dB")

# ---------- 4. 画图 ----------
NAMES = ["真实语音（LJSpeech 原始录音）", "伪造 A：MelGAN 声码器（WaveFake）", "伪造 B：HiFi-GAN 声码器（WaveFake）"]
SIGS = [real, melgan, hifi]

def trio_fig(title):
    fig, axes = plt.subplots(3, 1, figsize=(11, 8.6), sharex=True, dpi=150)
    fig.suptitle(title, fontsize=14, fontweight="bold")
    return fig, axes

# 4.1 波形
fig, axes = trio_fig("波形对比：三个版本几乎重合")
for ax, sig, name in zip(axes, SIGS, NAMES):
    librosa.display.waveshow(sig, sr=SR, ax=ax, color="#0369a1")
    ax.set_title(name, fontsize=10, loc="left")
    ax.set_ylabel("幅值")
axes[-1].set_xlabel("时间 (秒)")
fig.tight_layout()
fig.savefig(OUT_IMAGES / "rvf-waveform.png"); plt.close(fig)

# 4.2 线性频率 STFT
fig, axes = trio_fig("线性频率谱：真实的高频纹理 vs 声码器的高频缺失")
for ax, D, name in zip(axes, [lin_r, lin_m, lin_h], NAMES):
    img = librosa.display.specshow(D, sr=SR, hop_length=HOP, x_axis="time", y_axis="hz", ax=ax, cmap="magma")
    ax.set_title(name, fontsize=10, loc="left")
    ax.set_ylabel("频率 (Hz)")
axes[-1].set_xlabel("时间 (秒)")
fig.colorbar(img, ax=axes, format="%+2.0f dB")
fig.savefig(OUT_IMAGES / "rvf-stft.png"); plt.close(fig)

# 4.3 梅尔谱
fig, axes = trio_fig("梅尔谱对比")
for ax, M, name in zip(axes, [mel_r, mel_m, mel_h], NAMES):
    img = librosa.display.specshow(M, sr=SR, hop_length=HOP, x_axis="time", y_axis="mel", ax=ax, cmap="magma")
    ax.set_title(name, fontsize=10, loc="left")
    ax.set_ylabel("梅尔频率")
axes[-1].set_xlabel("时间 (秒)")
fig.colorbar(img, ax=axes, format="%+2.0f dB")
fig.savefig(OUT_IMAGES / "rvf-mel.png"); plt.close(fig)

# 4.4 差异图（两栏共用同一色标，公平对比）
d_m = mel_r - mel_m
d_h = mel_r - mel_h
v = max(6.0, np.percentile(np.abs(np.concatenate([d_m.ravel(), d_h.ravel()])), 99))
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True, dpi=150)
fig.suptitle("梅尔谱差异图（真实 − 伪造，单位 dB）：老式声码器痕迹重，现代声码器痕迹轻", fontsize=13, fontweight="bold")
for ax, d, name in zip(axes, [d_m, d_h], ["真实 − MelGAN", "真实 − HiFi-GAN"]):
    img = librosa.display.specshow(d, sr=SR, hop_length=HOP, x_axis="time", y_axis="mel", ax=ax, cmap="coolwarm", vmin=-v, vmax=v)
    ax.set_title(name, fontsize=11)
    ax.set_xlabel("时间 (秒)")
axes[0].set_ylabel("梅尔频率")
fig.colorbar(img, ax=axes, format="%+2.0f dB")
fig.savefig(OUT_IMAGES / "rvf-diff.png"); plt.close(fig)

print("图片已保存：rvf-waveform / rvf-stft / rvf-mel / rvf-diff .png")
print("音频已保存：rvf-real / rvf-melgan / rvf-hifigan .wav")
print("全部完成")
