import tkinter as tk
import tkinter.ttk as ttk

import numpy as np
import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt


import cable as cableModules
import util
import matplotlibSettings as pltSettings

def drawFrequencyResponseOfAlphaAndCharaImpedance(
    frequencies_Hz, R=0, L=0, G=0, C=0, axes=plt.subplots(2, 1)[1]
):
    # Cableインスタンスの作成
    cable = cableModules.Cable(
        resistance=R,
        inductance=L,
        conductance=G,
        capacitance=C,
        length=6,  # alphaとZoの計算には関係ないので適用な値で初期化
    )
    # 周波数ごとにalphaを求める
    alphas_db = []
    for frequency_Hz in frequencies_Hz:
        #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
        alpha_np = util.calcAttenuationConstant(frequency_Hz, cable)  # Np/m
        alpha_db = util.np2db(alpha_np)  # dB/m
        alphas_db.append(alpha_db)

    FONT_SIZE = 12
    axes[0].plot(
        frequencies_Hz,
        list(map(lambda x: x * 1000, alphas_db)),
        label="vertual cable",
        zorder=5,
    )  # absで振幅を取得
    axes[0].set_title("周波数ごとの減衰定数の推移")
    axes[0].set_ylabel("α [dB/km]", fontsize=FONT_SIZE)
    axes[0].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    for (exist_cable, color, marker) in zip(
        cableModules.exist_cables, pltSettings.colors, pltSettings.markers
    ):
        axes[0].plot(
            [1e6, 10e6, 200e6],  # 1MHz, 10MHz, 200MHz
            exist_cable["alphas"],
            marker=marker,
            color=color,
            label=exist_cable["name"],
        )
        axes[0].legend()

    # axes[0].set_title(
    #     f"R = {str(value_R)}, L = {str(value_L)}, G = {str(value_G)}, C = {str(value_C)}"
    # )

    characteristicImpedances = []
    for frequency_Hz in list(frequencies_Hz):
        characteristicImpedances.append(cable.calcCharacteristicImpedance(frequency_Hz))
    axes[1].plot(frequencies_Hz, np.abs(characteristicImpedances))
    # axes[1].set_xscale("log")
    # axes[1].set_yscale("log")


def calcEndVoltByAnyFreqUnderEndOpenCondition(
    frequencies_Hz, R=0, L=0, G=0, C=0, axes=plt.subplots(2, 1)[1]
):
    t = 0
    cable = cableModules.Cable(
        resistance=R,
        inductance=L,
        conductance=G,
        capacitance=C,
        length=6,  # alphaとZoの計算には関係ないので適用な値で初期化
    )
    # cable = cableModules.cable_vertual
    amp_input_volt = 1000  # 入力電圧のPeek値が1000V

    x = cable.length  # 受電端の電圧を見る
    l = cable.length  # 線路の長さ

    gains = []
    for frequency_Hz in frequencies_Hz:
        alpha = util.calcAttenuationConstant(frequency_Hz, cable)
        beta = util.calcPhaseConstant(frequency_Hz, cable)
        gamma = alpha + 1j * beta
        omega = 2 * np.pi * frequency_Hz

        cosh = np.cosh(gamma * l)
        theta = np.arctan((cosh * -1).imag / (cosh * -1).real)  # 位相遅れ

        gains.append(
            (
                (-1 * amp_input_volt / abs(np.cosh(gamma * l)))
                * (
                    (
                        (1 / 2)
                        * np.exp(-1 * alpha * x + alpha * l)
                        * np.cos(omega * t + beta * l - beta * x - theta)
                    )
                    + (
                        (1 / 2)
                        * np.exp(alpha * x - alpha * l)
                        * np.cos(omega * t - beta * l + beta * x - theta)
                    )
                )
            )
            / amp_input_volt
        )

    FONT_SIZE = 12
    axes[0].plot(
        frequencies_Hz,
        list(
            map(
                util.convertGain2dB,
                gains,
            )
        ),
    )
    axes[0].set_ylabel("Gain[dB]", fontsize=FONT_SIZE)  # y軸は、伝達関数の絶対値
    axes[0].set_xlabel("frequency [MHz]", fontsize=FONT_SIZE)
    axes[0].xaxis.set_major_formatter(
        pltSettings.FixedOrderFormatter(6, useMathText=True)
    )
    axes[0].ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
