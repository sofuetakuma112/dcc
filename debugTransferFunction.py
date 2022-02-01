import tkinter as tk
import tkinter.ttk as ttk

import numpy as np
import math
import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import cable as cableModules
import util
import matplotlibSettings as pltSettings
import transferFunction as tfModules

frequencies_Hz = list(range(500 * 1000, 100 * util.ONE_HUNDRED, 100000))

axes = [plt.subplots()[1] for i in range(5)]

thetas = [
    tfModules.calculateTheta(freq, cableModules.cable_vertual)
    for freq in frequencies_Hz
]

FONT_SIZE = 12
axes[0].plot(
    frequencies_Hz, list(map(lambda theta: np.real(theta), thetas)), label="α * l"
)
axes[0].plot(
    frequencies_Hz, list(map(lambda theta: np.imag(theta), thetas)), label="β * l"
)
axes[0].set_title("周波数ごとの伝搬定数の推移")
axes[0].set_ylabel("theta", fontsize=FONT_SIZE)
axes[0].set_xlabel("Frequency [MHz]", fontsize=FONT_SIZE)
axes[0].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
axes[0].legend()

fMatrixesForDcc = [
    tfModules.createFMatrixForDcc(
        frequencies_Hz[i], thetas[i], cableModules.cable_vertual
    )
    for i in range(len(frequencies_Hz))
]

As = []
Bs = []
Cs = []
Ds = []
sinhs = []
for i in range(len(frequencies_Hz)):
    fMatrix = fMatrixesForDcc[i]
    A = fMatrix[0][0]
    B = fMatrix[0][1]
    C = fMatrix[1][0]
    D = fMatrix[1][1]
    As.append(A)  # cosh
    Bs.append(B)
    Cs.append(C)
    Ds.append(D)

    sinhs.append(np.sqrt(B * C))
coshs = As

axes[1].plot(frequencies_Hz, np.real(coshs), label="cosh.real")
axes[1].plot(frequencies_Hz, np.imag(coshs), label="cosh.imag")
axes[1].set_title("周波数ごとのcoshの推移")
axes[1].set_ylabel("cosh.imag", fontsize=FONT_SIZE)
axes[1].set_xlabel("Frequency [MHz]", fontsize=FONT_SIZE)
axes[1].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
axes[1].legend()

axes[2].plot(frequencies_Hz, np.real(sinhs), label="sinh.real")
axes[2].plot(frequencies_Hz, np.imag(sinhs), label="sinh.imag")
axes[2].set_title("周波数ごとのsinhの推移")
axes[2].set_ylabel("sinh.imag", fontsize=FONT_SIZE)
axes[2].set_xlabel("Frequency [MHz]", fontsize=FONT_SIZE)
axes[2].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
axes[2].legend()

axes[3].plot(
    frequencies_Hz,
    [np.real(coshs[i] + sinhs[i]) for i in range(len(frequencies_Hz))],
    label="(cosh + sinh).real",
)
axes[3].plot(
    frequencies_Hz,
    [np.imag(coshs[i] + sinhs[i]) for i in range(len(frequencies_Hz))],
    label="(cosh + sinh).imag",
)
axes[3].set_title("周波数ごとの(cosh + sinh)の推移")
axes[3].set_ylabel("(cosh + sinh).imag", fontsize=FONT_SIZE)
axes[3].set_xlabel("Frequency [MHz]", fontsize=FONT_SIZE)
axes[3].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
axes[3].legend()

# 伝達関数を計算する
tfs = []
for i in range(len(frequencies_Hz)):
    frequency_Hz = frequencies_Hz[i]
    fMatrix = fMatrixesForDcc[i]
    cable = cableModules.cable_vertual
    endCondition = {"shouldMatching": False, "impedance": 1e6}

    if endCondition["shouldMatching"]:
        # 線路の特性インピーダンスと、受電端の抵抗のインピーダンスを同じにする
        endImpedance = cable.calcCharacteristicImpedance(frequency_Hz)
    else:
        endImpedance = endCondition["impedance"]

    # F行列と受電端のインピーダンスから伝達関数を計算する
    tfs.append(tfModules.createTransferFunctionFromFMatrix(endImpedance, fMatrix))

axes[4].plot(frequencies_Hz, list(map(lambda tf: np.real(tf), tfs)), label="tf.real")
axes[4].plot(frequencies_Hz, list(map(lambda tf: np.imag(tf), tfs)), label="tf.imag")
axes[4].plot(frequencies_Hz, list(map(lambda tf: np.abs(tf), tfs)), label="abs(tf)")
axes[4].set_title("周波数ごとの伝達関数の推移")
axes[4].set_ylabel("abs(tf)", fontsize=FONT_SIZE)
axes[4].set_xlabel("Frequency [MHz]", fontsize=FONT_SIZE)
axes[4].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
axes[4].legend()

plt.tight_layout()
plt.show()
