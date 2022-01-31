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

axes = [plt.subplots()[1]] * 2

thetas = [
    tfModules.calculateTheta(freq, cableModules.cable_vertual)
    for freq in frequencies_Hz
]

FONT_SIZE = 12
axes[0].plot(
    frequencies_Hz, list(map(lambda theta: np.real(theta), thetas)), label="theta.real"
)
axes[0].set_title("周波数ごとの伝搬定数の推移")
axes[0].set_ylabel("theta.real", fontsize=FONT_SIZE)
axes[0].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
axes[0].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
axes[0].legend()
# axes[0].set_xscale("log")
# axes[0].set_yscale("log")

axes[1].plot(
    frequencies_Hz, list(map(lambda theta: np.imag(theta), thetas)), label="theta.imag"
)
axes[1].set_title("周波数ごとの伝搬定数の推移")
axes[1].set_ylabel("theta.imag", fontsize=FONT_SIZE)
axes[1].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
axes[1].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
axes[1].legend()

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

for i in range(len(frequencies_Hz)):
    fMatrix = fMatrixesForDcc[i]
    A = fMatrix[0][0]
    B = fMatrix[0][1]
    C = fMatrix[1][0]
    D = fMatrix[1][1]
    As.append(A)
    Bs.append(B)
    Cs.append(C)
    Ds.append(D)

plt.tight_layout()
plt.show()
