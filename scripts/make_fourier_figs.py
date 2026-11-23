# -*- coding: utf-8 -*-
"""傅里叶系列文章全套配图（按专家审稿意见的图位清单生成）"""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path("public/images")
OUT.mkdir(parents=True, exist_ok=True)
DPI = 150


def trap(y, x):
    """手写梯形积分（兼容旧版 numpy，没有 trapezoid/trapz 之争）"""
    return np.sum((y[:-1] + y[1:]) * np.diff(x)) * 0.5


def sinh_ratio(k, y, H):
    """sinh(k(H-y))/sinh(kH) 的数值稳定版（大 k 不溢出）"""
    a = k * (H - y)
    b = k * H
    return np.exp(a - b) * (1 - np.exp(-2 * a)) / (1 - np.exp(-2 * b))

def save(fig, name):
    fig.savefig(OUT / name, dpi=DPI)
    plt.close(fig)
    print("saved:", name)


# ═══ 图A（第二章）：方波合成过程 + 吉布斯现象特写 ═══
t = np.linspace(0, 2 * np.pi, 4001)
square = np.sign(np.sin(t))


def partial_sum(t, N):
    s = np.zeros_like(t)
    for n in range(1, N + 1, 2):
        s += np.sin(n * t) / n
    return 4 / np.pi * s


fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), dpi=DPI)
ax = axes[0]
ax.plot(t, square, "k--", lw=2, label="目标：方波")
for N, c in [(1, "#94a3b8"), (3, "#0369a1"), (5, "#059669"), (10, "#e11d48")]:
    ax.plot(t, partial_sum(t, N), color=c, lw=1.4, label=f"前 {N} 项")
ax.set_title("逐项叠加，越来越像方波", fontsize=12)
ax.set_xlabel("t"); ax.set_ylabel("f(t)")
ax.legend(fontsize=9, loc="upper right"); ax.set_ylim(-1.7, 1.7)
ax = axes[1]
mask = (t > np.pi - 0.6) & (t < np.pi + 0.6)
for N, c in [(10, "#0369a1"), (100, "#e11d48")]:
    ax.plot(t[mask], partial_sum(t, N)[mask], color=c, lw=1.5, label=f"前 {N} 项")
ax.plot(t[mask], square[mask], "k--", lw=2, label="目标")
ax.axhline(1, color="#94a3b8", lw=0.8)
ax.axhline(1.17898, color="#f59e0b", lw=1, ls=":")
ax.annotate("过冲 ≈ 跳变高度的 8.95%（吉布斯现象）", xy=(np.pi - 0.02, 1.19),
            xytext=(np.pi - 0.58, 1.45), fontsize=10, color="#b45309",
            arrowprops=dict(arrowstyle="->", color="#b45309"))
ax.set_title("放大跳变处：过冲高度不降、宽度趋零", fontsize=12)
ax.set_xlabel("t"); ax.legend(fontsize=9, loc="lower left")
fig.suptitle("用正弦波合成方波：傅里叶级数前 N 项的部分和", fontsize=13, fontweight="bold")
fig.tight_layout()
save(fig, "fourier-square-wave.png")

# ═══ 图B（1.2）：一小段杆的热流记账示意 ═══
fig, ax = plt.subplots(figsize=(9, 3.2), dpi=DPI)
ax.add_patch(plt.Rectangle((0.18, 0.35), 0.64, 0.3, facecolor="#cbd5e1", edgecolor="#475569", lw=1.5))
ax.annotate("", xy=(0.18, 0.5), xytext=(0.02, 0.5), arrowprops=dict(arrowstyle="-|>", lw=2.5, color="#e11d48"))
ax.text(0.10, 0.56, "流入 q(x)", fontsize=11, color="#e11d48", ha="center")
ax.annotate("", xy=(0.98, 0.5), xytext=(0.82, 0.5), arrowprops=dict(arrowstyle="-|>", lw=2.5, color="#0369a1"))
ax.text(0.90, 0.56, "流出 q(x+Δx)", fontsize=11, color="#0369a1", ha="center")
ax.text(0.5, 0.5, "这一小段\n升温储热", fontsize=11, ha="center", va="center")
ax.plot([0.18, 0.18], [0.28, 0.35], "k-", lw=1)
ax.plot([0.82, 0.82], [0.28, 0.35], "k-", lw=1)
ax.text(0.18, 0.22, "x", fontsize=12, ha="center")
ax.text(0.82, 0.22, "x+Δx", fontsize=12, ha="center")
ax.set_xlim(0, 1); ax.set_ylim(0.1, 0.75); ax.axis("off")
ax.set_title("能量记账：流入 − 流出 = 这一小段升温所需的热量", fontsize=12)
save(fig, "fig-heat-budget.png")

# ═══ 图C（1.3）：底边恒温 1° 的矩形板稳态温度热力图 ═══
L, H = 1.0, 1.0
N = 201
xs = np.linspace(0, L, N)
ys = np.linspace(0, H, N)
U = np.zeros((N, N))
for n in range(1, 400, 2):  # f(x)=1 时 b_n = 4/(nπ)，只有奇次
    b = 4 / (n * np.pi)
    decay = sinh_ratio(n * np.pi / L, ys, H)
    U += b * np.outer(decay, np.sin(n * np.pi * xs / L))
fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=DPI)
im = ax.imshow(U, origin="lower", extent=[0, L, 0, H], cmap="magma", aspect="auto")
ax.set_title("底边恒为 1°、三边为 0°：金属板稳态温度（级数解）", fontsize=12)
ax.set_xlabel("x"); ax.set_ylabel("y（高度）")
fig.colorbar(im, ax=ax, label="温度")
save(fig, "fig-plate-heatmap.png")

# ═══ 图D（1.4）：本征函数 + 沿 y 衰减 ═══
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), dpi=DPI)
x = np.linspace(0, 1, 400)
for n, c in zip([1, 2, 3, 4], ["#e11d48", "#0369a1", "#059669", "#b45309"]):
    axes[0].plot(x, np.sin(n * np.pi * x), color=c, lw=1.8, label=f"n={n}")
axes[0].set_title("x 方向的本征函数（边界条件筛出的驻波）", fontsize=11)
axes[0].set_xlabel("x"); axes[0].legend(fontsize=9)
yy = np.linspace(0, 1, 400)
for n, c in zip([1, 2, 4, 8], ["#e11d48", "#0369a1", "#059669", "#b45309"]):
    axes[1].plot(yy, sinh_ratio(n * np.pi, yy, 1.0), color=c, lw=1.8, label=f"n={n}")
axes[1].set_title("沿 y 的衰减：n 越大，热渗得越浅", fontsize=11)
axes[1].set_xlabel("y（1=底边，0=顶边）"); axes[1].legend(fontsize=9)
fig.suptitle("分离变量的产物：每块积木 = x 向驻波 × y 向指数衰减", fontsize=12, fontweight="bold")
fig.tight_layout()
save(fig, "fig-eigenmodes.png")

# ═══ 图E（1.6）：正交性乘积抵消 + 奇延拓 ═══
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.4), dpi=DPI)
xx = np.linspace(0, 1, 500)
for ax, (n, m) in zip(axes[:2], [(2, 3), (3, 3)]):
    p = np.sin(n * np.pi * xx) * np.sin(m * np.pi * xx)
    ax.plot(xx, p, color="#0369a1", lw=1.6)
    ax.fill_between(xx, p, 0, where=p > 0, color="#e11d48", alpha=0.45)
    ax.fill_between(xx, p, 0, where=p < 0, color="#0369a1", alpha=0.45)
    ax.axhline(0, color="#94a3b8", lw=0.8)
    if n != m:
        ax.set_title(f"n={n}, m={m}：正负面积抵消 → 积分 0", fontsize=10.5)
    else:
        ax.set_title(f"n=m={n}：全部为正 → 积分 L/2", fontsize=10.5)
    ax.set_xlabel("x/L")
ax = axes[2]
xt = np.linspace(-1, 3, 900)
g = np.where(((xt % 2 + 2) % 2) < 1, 1.0, -1.0)  # 周期 2 的方波（奇函数）
ax.plot(xt, g, color="#7c3aed", lw=1.6)
ax.axhline(0, color="#94a3b8", lw=0.8)
ax.set_title("半幅展开的秘密：把 f 奇延拓成周期 2L", fontsize=10.5)
ax.set_xlabel("x/L")
fig.suptitle("正交性与奇延拓：(0,L) 上的任意曲线为何能只用正弦表示", fontsize=12, fontweight="bold")
fig.tight_layout()
save(fig, "fig-orthogonality.png")

# ═══ 图F（1.7）：棱角最先融化 ═══
fig, ax = plt.subplots(figsize=(9, 3.8), dpi=DPI)
xx = np.linspace(0, 1, 400)
f0 = np.exp(-((xx - 0.5) ** 2) / 0.004)
bn = np.array([2 * trap(f0 * np.sin(n * np.pi * xx), xx) for n in range(1, 60)])
for t, c in [(0, "#e11d48"), (0.002, "#f59e0b"), (0.02, "#059669"), (0.2, "#0369a1")]:
    u = sum(bn[n - 1] * np.sin(n * np.pi * xx) * np.exp(-(n * np.pi) ** 2 * t) for n in range(1, 60))
    ax.plot(xx, u, color=c, lw=1.8, label=f"t = {t}")
ax.set_title("扩散在磨平棱角：高频分量先死，平缓起伏最后消失", fontsize=12)
ax.set_xlabel("位置 x"); ax.set_ylabel("温度"); ax.legend(fontsize=10)
save(fig, "fig-diffusion-times.png")

# ═══ 图G（第二章）：方波 vs 三角波的系数衰减（线谱）═══
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), dpi=DPI)
ns = np.arange(1, 16)
sq = np.where(ns % 2 == 1, 4 / (ns * np.pi), 0.0)
tri = np.where(ns % 2 == 1, 8 / (ns * np.pi) ** 2, 0.0)
axes[0].stem(ns, sq, basefmt=" ")
axes[0].set_title("方波（有跳变）：系数按 1/n 衰减", fontsize=11)
axes[1].stem(ns, tri, basefmt=" ")
axes[1].set_title("三角波（连续、尖角）：系数按 1/n² 衰减", fontsize=11)
for ax in axes:
    ax.set_xlabel("n（谐波次数）"); ax.set_ylabel("|系数|")
fig.suptitle("越光滑，高频系数死得越快——频谱是函数的指纹", fontsize=12, fontweight="bold")
fig.tight_layout()
save(fig, "fig-coefficient-decay.png")

# ═══ 图H（第二篇·傅里叶变换）：周期 T 增大 → 谱线变密 ═══
fig, axes = plt.subplots(1, 3, figsize=(12, 3.4), dpi=DPI)
for ax, T in zip(axes, [2, 8, 32]):
    t = np.linspace(0, T, 6000)
    xT = np.exp(-(t % T))
    nmax = 40
    freqs = np.arange(-nmax, nmax + 1) / T
    cn = np.array([trap(xT * np.exp(-2j * np.pi * f * t), t) / T for f in freqs])
    ax.stem(freqs, np.abs(cn), basefmt=" ", markerfmt=".")
    ax.set_title(f"T = {T}", fontsize=11)
    ax.set_xlabel("频率 (Hz)"); ax.set_ylim(0, 1.05 * np.abs(cn).max())
fig.suptitle("周期越大，谱线越密：离散线谱 → 连续谱（傅里叶变换）", fontsize=12, fontweight="bold")
fig.tight_layout()
save(fig, "fig-spectrum-densify.png")

# ═══ 图I（第二篇·相位，重头戏）：先后弹 vs 同时按 ═══
sr = 8000
tt = np.arange(sr) / sr
do_ = np.sin(2 * np.pi * 261.63 * tt)
mi_ = np.sin(2 * np.pi * 329.63 * tt)
sigA = np.where(tt < 0.5, do_, mi_)            # 先后弹（旋律）
sigB = do_ + mi_                                 # 同时按（和弦）
fig, axes = plt.subplots(2, 2, figsize=(11, 6.2), dpi=DPI)
freqs = np.fft.rfftfreq(sr, 1 / sr)
for i, (sig, name) in enumerate([(sigA, "先后弹（do→mi）"), (sigB, "同时按（do+mi）")]):
    ax = axes[0, i]
    ax.plot(tt, sig, lw=0.4, color="#0369a1")
    ax.set_title(f"{name}：波形", fontsize=11)
    ax.set_xlabel("时间 (s)"); ax.set_xlim(0, 1); ax.set_ylim(-2.2, 2.2)
    ax = axes[1, i]
    ax.plot(freqs, np.abs(np.fft.rfft(sig)) / sr * 2, lw=1.0, color="#e11d48")
    ax.set_xlim(0, 800)
    ax.set_title("幅度谱：几乎一样（区别藏在相位谱里）", fontsize=11)
    ax.set_xlabel("频率 (Hz)")
fig.suptitle("傅里叶变换丢时间了吗？——没有，它把时间装进了相位", fontsize=13, fontweight="bold")
fig.tight_layout()
save(fig, "fig-phase-demo.png")

# ═══ 图J（第二篇·窗函数）：矩形窗 vs 汉宁窗 ═══
w = 8192
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6), dpi=DPI)
for ax, (win, name) in zip(axes, [(np.ones(1024), "矩形窗（不加窗）"), (np.hanning(1024), "汉宁窗")]):
    ax.plot(np.arange(1024) / 1024, win, color="#0369a1", lw=1.8)
    ax.set_title(f"{name}：时域形状", fontsize=11); ax.set_xlabel("样本位置 / M")
    ax.set_ylim(-0.05, 1.1)
fig.tight_layout()
fig2, axes = plt.subplots(1, 2, figsize=(11, 3.6), dpi=DPI)
for ax, (win, name) in zip(axes, [(np.ones(w), "矩形窗"), (np.hanning(w), "汉宁窗")]):
    W = np.abs(np.fft.rfft(win, 8 * w))
    Wdb = 20 * np.log10(W / W.max() + 1e-12)
    ax.plot(np.arange(len(W)) / w * 2, Wdb, lw=0.9, color="#e11d48")
    ax.set_xlim(0, 8); ax.set_ylim(-100, 3)
    ax.set_title(f"{name}：频域（dB）", fontsize=11); ax.set_xlabel("频率（bin 为单位）")
fig2.suptitle("窗的取舍：矩形窗主瓣最窄但旁瓣高（−13 dB）；汉宁窗旁瓣低（−31 dB）但主瓣宽一倍", fontsize=11.5)
fig2.tight_layout()
save(fig2, "fig-window-leak.png")
plt.close(fig)

# ═══ 图K（第二篇·窄带/宽带）：真实语音两种频谱图 ═══
import librosa
import librosa.display

y, srL = librosa.load("public/audio/rvf-real.wav", sr=22050)
fig, axes = plt.subplots(1, 2, figsize=(11, 3.9), dpi=DPI)
for ax, (nfft, name) in zip(axes, [(2048, "长窗（窄带）：看清谐波细线"), (256, "短窗（宽带）：看清共振峰包络")]):
    S = np.abs(librosa.stft(y, n_fft=nfft, hop_length=nfft // 4, window="hann"))
    Sdb = librosa.amplitude_to_db(S, ref=np.max)
    librosa.display.specshow(Sdb, sr=srL, hop_length=nfft // 4, x_axis="time", y_axis="hz", ax=ax, cmap="magma")
    ax.set_title(name, fontsize=11); ax.set_ylim(0, 5000)
fig.suptitle("同一句话的两种频谱图：窗长决定你看到的世界", fontsize=12, fontweight="bold")
fig.tight_layout()
save(fig, "fig-narrow-wide.png")

print("全部配图完成")
