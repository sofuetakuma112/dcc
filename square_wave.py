# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# データのパラメータ
N = 256  # サンプル数
dt = 0.01  # サンプリング間隔
fq1 = 5
fc = 20  # カットオフ周波数
t = np.arange(0, N * dt, dt)  # 時間軸(0 ~ 2.55まで0.01刻み)
freq = np.linspace(0, 1.0 / dt, N)  # 周波数軸(0 ~ 100まで256刻み)

# t = np.linspace(0, 1, N, endpoint=False)
# 方形波の離散値のリスト
f = signal.square(2 * np.pi * fq1 * t)  # len(f) => 256

# 高速フーリエ変換（周波数信号に変換）
F = np.fft.fft(f)  # (256,)

# 正規化 + 交流成分2倍
F = F / (N / 2)
F[0] = F[0] / 2

# 配列Fをコピー
F_copy = F.copy()

# 離散的な時刻にデータを取得することを、
# サンプリングという。
# データの取得間隔Δ𝑡をサンプリング周期といい、
# その逆数1/Δ𝑡をサンプリング周波数と呼ぶ。
"""
np.fft.rfftfreq

離散フーリエ変換のサンプル周波数を返す（rfft, irfftで使用するため）。

返されるfloat配列は、
サンプル間隔の単位あたりのサイクルで周波数ビンの中心を含む (開始点は0)。
例えば、サンプル間隔が秒の場合、周波数単位はcycles/secondとなる。

窓の長さnとサンプル間隔dが与えられた場合。

f = [0, 1, ..., n/2-1, n/2] / (d*n) (nが偶数の場合)
f = [0, 1, ..., (n-1)/2-1, (n-1)/2] / (d*n) (nが奇数)
fftfreqとは異なり（しかしscipy.ftpack.rfftfreqと同様）、ナイキスト周波数成分は正とみなされます。

パラメータ
n : int
    ウィンドウの長さ。
d : スカラー、オプション
    サンプル間隔（サンプリングレートの逆数）。デフォルトは1である。

戻り値
f : ndarray
    サンプル周波数を含む長さn/2 + 1の配列。
"""
# freqList = np.fft.rfftfreq(len(f), dt)

# ローパスフィル処理（カットオフ周波数を超える帯域の周波数信号を0にする）
# len(F_copy) => 256
# F_copy[(freq > fc)] = 0

# 高速逆フーリエ変換（時間信号に戻す）
f2 = np.fft.ifft(F_copy)

# 振幅を元のスケールに戻す
f2 = np.real(f2 * N)

# グラフ表示
fig = plt.figure(figsize=(10.0, 8.0))
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12

# 時間信号（元）
plt.subplot(221)
plt.plot(t, f, label="f(n)")
plt.xlabel("Time", fontsize=12)
plt.ylabel("Signal", fontsize=12)
plt.grid()
leg = plt.legend(loc=1, fontsize=15)
leg.get_frame().set_alpha(1)

# 周波数信号(元)
# plt.subplot(222)
# plt.plot(freq, np.abs(F), label="|F(k)|")
# plt.xlabel("Frequency", fontsize=12)
# plt.ylabel("Amplitude", fontsize=12)
# plt.grid()
# leg = plt.legend(loc=1, fontsize=15)
# leg.get_frame().set_alpha(1)

# 時間信号(処理後)
plt.subplot(223)
plt.plot(t, f2, label="f2(n)")
plt.xlabel("Time", fontsize=12)
plt.ylabel("Signal", fontsize=12)
plt.grid()
leg = plt.legend(loc=1, fontsize=15)
leg.get_frame().set_alpha(1)

# 周波数信号(処理後)
# plt.subplot(224)
# plt.plot(freq, np.abs(F_copy), label="|F_copy(k)|")
# plt.xlabel("Frequency", fontsize=12)
# plt.ylabel("Amplitude", fontsize=12)
# plt.grid()
# leg = plt.legend(loc=1, fontsize=15)
# leg.get_frame().set_alpha(1)

plt.show()
