# -*- coding: utf-8 -*-
"""傅里叶文章配图：方波合成过程 + 吉布斯现象特写"""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

t = np.linspace(0, 2 * np.pi, 4001)
square = np.sign(np.sin(t))


def partial_sum(t, N):
    """方波傅里叶级数的前 N 项部分和（只含奇次谐波）"""
    s = np.zeros_like(t)
    for n in range(1, N + 1, 2):
        s += np.sin(n * t) / n
    return 4 / np.pi * s


fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), dpi=150)

# 左图：逐项叠加逼近方波
ax = axes[0]
ax.plot(t, square, "k--", lw=2, label="目标：方波")
for N, c in [(1, "#94a3b8"), (3, "#0369a1"), (5, "#059669"), (10, "#e11d48")]:
    ax.plot(t, partial_sum(t, N), color=c, lw=1.4, label=f"前 {N} 项")
ax.set_title("逐项叠加，越来越像方波", fontsize=12)
ax.set_xlabel("t")
ax.set_ylabel("f(t)")
ax.legend(fontsize=9, loc="upper right")
ax.set_ylim(-1.7, 1.7)

# 右图：放大跳变处，展示吉布斯过冲（极限约 1.179，即跳变高度的 ~9%）
ax = axes[1]
mask = (t > np.pi - 0.6) & (t < np.pi + 0.6)
for N, c in [(10, "#0369a1"), (100, "#e11d48")]:
    ax.plot(t[mask], partial_sum(t, N)[mask], color=c, lw=1.5, label=f"前 {N} 项")
ax.plot(t[mask], square[mask], "k--", lw=2, label="目标")
ax.axhline(1, color="#94a3b8", lw=0.8)
ax.axhline(1.17898, color="#f59e0b", lw=1, ls=":")
ax.annotate(
    "过冲 ≈ 跳变高度的 9%（吉布斯现象）",
    xy=(np.pi - 0.02, 1.19),
    xytext=(np.pi - 0.58, 1.42),
    fontsize=10,
    color="#b45309",
    arrowprops=dict(arrowstyle="->", color="#b45309"),
)
ax.set_title("放大跳变处：过冲永不消失", fontsize=12)
ax.set_xlabel("t")
ax.legend(fontsize=9, loc="lower left")

fig.suptitle("用正弦波合成方波：傅里叶级数前 N 项的部分和", fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig("public/images/fourier-square-wave.png")
print("saved: public/images/fourier-square-wave.png")
