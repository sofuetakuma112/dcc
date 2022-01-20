import math

import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

import numpy as np
from tqdm import tqdm

import util
import cable
import transferFunction as tfModules


def drawBodePlot(frequencies_Hz, endCondition, cable, fileName=""):
    """
    分布定数線路のボード線図を表示する

    Parameters
    ----------
    frequencies_Hz : list
        周波数(Hz)のリスト
    endCondition: dict
        受電端のインピーダンスに関する条件
    cable : instance
        Cableクラスのインスタンス
    fileName: string
        表示するグラフを保存する際のファイル名
    """

    tfs = []
    tfs_nthPwrOf10 = []
    # 周波数ごとに伝達関数を求める
    for frequency_Hz in tqdm(frequencies_Hz, leave=False):
        tf = tfModules.createTransferFunction(frequency_Hz, endCondition, cable)
        tfs.append(tf)

        # 周波数が10のn乗ごとに、伝達関数の計算結果を控えておく
        if frequency_Hz > 1 and math.log10(frequency_Hz).is_integer():
            tfs_nthPwrOf10.append({"frequency_Hz": frequency_Hz, "tf": tf})

    # ゲインの傾きを求める
    slope = util.calcMinimumSlope(tfs_nthPwrOf10)
    print(f"傾き: {slope}[dB/dec]")

    fig, axes = plt.subplots(1, 2)
    axes[0].plot(
        frequencies_Hz,
        list(map(util.convertGain2dB, tfs)),
    )
    axes[0].set_xlabel("frequency [Hz]")
    axes[0].set_ylabel("Gain [dB]")
    axes[0].set_xscale("log")
    if max(np.abs(tfs)) - min(np.abs(tfs)) < 1e-6:
        axes[0].set_ylim(-5, 5)

    axes[1].plot(
        frequencies_Hz,
        list(map(lambda tf: math.atan2(tf.imag, tf.real) * 180 / np.pi, tfs)),
    )
    axes[1].set_xlabel("frequency [Hz]")
    axes[1].set_ylabel("phase [deg]")
    axes[1].set_xscale("log")

    if fileName != "":
        fig.savefig(f"{fileName}")
    plt.show()


def drawFrequencyResponse(frequencies_Hz, cable, fileName=""):
    """
    分布定数線路の周波数特性をグラフに表示する

    Parameters
    ----------
    frequencies_Hz : list
        周波数(Hz)のリスト
    cable : instance
        Cableクラスのインスタンス
    fileName: string
        表示するグラフを保存する際のファイル名
    """

    # open
    # 共振周波数の分母
    resonance_denominator_open = (
        2 * cable.length * math.sqrt(cable.inductance * cable.capacitance)
    )
    # 反共振周波数の分母
    antiresonance_denominator_open = (
        4 * cable.length * math.sqrt(cable.inductance * cable.capacitance)
    )

    # 開放
    resonance_freqs_open = []  # 共振周波数
    antiresonance_freqs_open = []  # 反共振周波数
    # 整数n
    n_length = range(10)
    for n in n_length:
        # 共振周波数
        resonance_freq_open = n / resonance_denominator_open
        resonance_freqs_open.append(resonance_freq_open)
        # 反共振周波数
        antiresonance_freq_open = (2 * n + 1) / antiresonance_denominator_open
        antiresonance_freqs_open.append(antiresonance_freq_open)
    # 引数のfrequencies_Hzに一番近い
    # 短絡
    resonance_freqs_short = antiresonance_freqs_open  # 共振周波数
    antiresonance_freqs_short = resonance_freqs_open  # 反共振周波数

    conditions = [
        {"shouldMatching": True, "impedance": 0},
        {"shouldMatching": False, "impedance": 1e6},
        {"shouldMatching": False, "impedance": 1e-6},
    ]
    for (i, condition) in enumerate(conditions):
        # ケーブルが損失あり、かつマッチング条件のときスキップ
        if (cable.resistance != 0 or cable.conductance != 0) and i == 0:
            continue
        fig, ax = plt.subplots()

        tfs = []
        for frequency_Hz in tqdm(frequencies_Hz, leave=False):
            tf = tfModules.createTransferFunction(frequency_Hz, condition, cable)
            tfs.append(tf)

        ax.plot(
            frequencies_Hz,
            list(map(abs, tfs)),
            # list(map(util.convertGain2dB, tfs)),
        )
        if cable.resistance == 0 and cable.conductance == 0:
            # 無損失ケーブル
            if i == 1:
                # open
                ax.plot(
                    resonance_freqs_open,
                    list(
                        map(
                            abs,
                            tfModules.calcTfsBySomeFreqs(
                                resonance_freqs_open, condition, cable
                            ),
                        )
                    ),
                    marker="v",
                    color="blue",
                    linestyle="",
                )
                ax.plot(
                    antiresonance_freqs_open,
                    list(
                        map(
                            abs,
                            tfModules.calcTfsBySomeFreqs(
                                antiresonance_freqs_open, condition, cable
                            ),
                        )
                    ),
                    marker="o",
                    color="red",
                    linestyle="",
                )
                ax.legend(["全ての周波数", "共振周波数", "反共振周波数"], loc="best")
            elif i == 2:
                # short
                ax.plot(
                    resonance_freqs_short,
                    list(
                        map(
                            abs,
                            tfModules.calcTfsBySomeFreqs(
                                resonance_freqs_short, condition, cable
                            ),
                        )
                    ),
                    marker="v",
                    color="blue",
                    linestyle="",
                )
                ax.plot(
                    antiresonance_freqs_short[1:],
                    list(
                        map(
                            abs,
                            tfModules.calcTfsBySomeFreqs(
                                antiresonance_freqs_short[1:], condition, cable
                            ),
                        )
                    ),
                    marker="o",
                    color="red",
                    linestyle="",
                )
                ax.legend(["全ての周波数", "共振周波数", "反共振周波数"], loc="best")
        text = (
            "matching"
            if condition["shouldMatching"]
            else "open"
            if condition["impedance"] >= 1e6
            else "short"
        )
        FONT_SIZE = 12
        ax.set_title(f"{text}")
        ax.set_ylabel("|H(f)|", fontsize=FONT_SIZE)  # y軸は、伝達関数の絶対値
        ax.set_xlabel("frequency [Hz]", fontsize=FONT_SIZE)
        ax.set_yscale("log")  # y軸はlogスケールで表示する
        ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
        if cable.resistance == 0 and cable.conductance == 0:
            if max(np.abs(tfs)) - min(np.abs(tfs)) < 1e-6:
                ax.set_ylim(1e-1, 1e3)

    if fileName != "":
        fig.savefig(util.createImagePath(fileName))

    plt.tight_layout()
    plt.show()


# ケーブルの周波数特性をグラフにする
frequencies_Hz = list(range(0, 10000, 10))
frequencies_Hz.extend(list(range(10000, 200 * 10 ** 6, 10000)))
# drawBodePlot(
#     np.logspace(4, 6, 1000, base=10),
#     {"shouldMatching": False, "impedance": 1e6},
#     cable_vertual,
# )
# drawBodePlot(
#     np.logspace(4, 6, 1000, base=10),
#     {"shouldMatching": True, "impedance": 1e6},
#     cable_noLoss_vertual,
# )

drawFrequencyResponse(
    list(range(0, util.ONE_HUNDRED, 1000)),
    # cable.Cable(
    #     resistance=1e-3,
    #     inductance=100e-12 * 50 ** 2,  # C * Zo ** 2
    #     conductance=1e-4,
    #     capacitance=100e-12,
    #     length=1000,
    # ),
    cable.cable_vertual,
)
