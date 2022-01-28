import numpy as np
import pandas as pd
import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt


import cable as cableModules
import util
import transferFunction as tfModules
import matplotlibSettings as pltSettings


def calcVoltByAnyDistanceUnderEndOpenCondition(distance):
    frequency_Hz = 50
    t = 0
    cable = cableModules.Cable(
        resistance=0.2139e-3,
        inductance=0.16588e-5,
        conductance=0,
        capacitance=0.66982e-11,
        length=3e6,  # alphaとZoの計算には関係ないので適用な値で初期化
    )
    amp_input_volt = 1000  # 入力電圧のPeek値が1.000Vだから1?

    x = distance  # 線路上の始端からの距離
    l = cable.length  # 線路の長さ
    # TODO: 位相遅れを求める処理を実装する

    alpha = util.calcAttenuationConstant(frequency_Hz, cable)  # 一致
    beta = util.calcPhaseConstant(frequency_Hz, cable)  # 一致
    gamma = alpha + 1j * beta
    omega = 2 * np.pi * frequency_Hz

    cosh = np.cosh(gamma * l)
    theta = np.arctan((cosh * -1).imag / (cosh * -1).real)  # 位相遅れ

    # abs(np.cosh(gamma * l))は一致

    return (-1 * amp_input_volt / abs(np.cosh(gamma * l))) * (
        (
            (1 / 2)
            * np.exp(-1 * alpha * x + alpha * l)
            * np.cos(omega * t + beta * l - 1 * beta * x - theta)
        )
        + (
            (1 / 2)
            * np.exp(alpha * x - 1 * alpha * l)
            * np.cos(omega * t - 1 * beta * l + beta * x - 1 * theta)
        )
    )


def calcEndVoltByAnyFreqUnderEndOpenCondition(frequency_Hz):
    t = 0
    cable = cableModules.Cable(
        resistance=0.2139e-3,
        inductance=0.16588e-5,
        conductance=0,
        capacitance=0.66982e-11,
        length=3e6,  # alphaとZoの計算には関係ないので適用な値で初期化
    )
    # cable = cableModules.cable_vertual
    amp_input_volt = 1000  # 入力電圧のPeek値が1000V

    x = cable.length  # 受電端の電圧を見る
    l = cable.length  # 線路の長さ
    # TODO: 位相遅れを求める処理を実装する

    alpha = util.calcAttenuationConstant(frequency_Hz, cable)
    beta = util.calcPhaseConstant(frequency_Hz, cable)
    gamma = alpha + 1j * beta
    omega = 2 * np.pi * frequency_Hz

    # gammaは周波数の関数なので、位相遅れθはfごとに変化する
    cosh = np.cosh(gamma * l)
    theta = np.arctan((cosh * -1).imag / (cosh * -1).real)  # 位相遅れ

    return (-1 * amp_input_volt / abs(np.cosh(gamma * l))) * (
        (
            (1 / 2)
            * np.exp(-1 * alpha * x + alpha * l)
            * np.cos(omega * t + beta * l - 1 * beta * x - theta)
        )
        + (
            (1 / 2)
            * np.exp(alpha * x - 1 * alpha * l)
            * np.cos(omega * t - 1 * beta * l + beta * x - 1 * theta)
        )
    )


# fig, ax = plt.subplots()
fig, axes = plt.subplots(2, 1)

distances = list(range(0, 3 * util.ONE_HUNDRED, 1000))
FONT_SIZE = 12

axes[0].plot(
    distances,
    list(map(calcVoltByAnyDistanceUnderEndOpenCondition, distances)),
)
axes[0].set_ylabel("Volt[V]", fontsize=FONT_SIZE)  # y軸は、伝達関数の絶対値
axes[0].set_xlabel("distance [m]", fontsize=FONT_SIZE)

frequencies_Hz = list(range(0, 100 * util.ONE_HUNDRED, 10000))

axes[1].plot(
    frequencies_Hz,
    list(
        map(
            lambda freq: util.convertGain2dB(
                calcEndVoltByAnyFreqUnderEndOpenCondition(freq) / 1000  # Vout / Vin
            ),
            frequencies_Hz,
        )
    ),
)

axes[1].set_ylabel("Gain[dB]", fontsize=FONT_SIZE)  # y軸は、伝達関数の絶対値
axes[1].set_xlabel("frequency [MHz]", fontsize=FONT_SIZE)
axes[1].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
axes[1].ticklabel_format(style="sci", axis="x", scilimits=(0, 0))

plt.tight_layout()
plt.show()
