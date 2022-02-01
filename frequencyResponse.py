import math

import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

import numpy as np
from tqdm import tqdm

import util
import cable
import transferFunction as tfModules
import matplotlibSettings as pltSettings


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

    # 共振周波数の分母（開放条件）
    resonance_denominator_open = (
        4 * cable.length * math.sqrt(cable.inductance * cable.capacitance)
    )
    # 反共振周波数の分母（開放条件）
    antiresonance_denominator_open = (
        2 * cable.length * math.sqrt(cable.inductance * cable.capacitance)
    )

    # 開放
    resonance_freqs_open = []  # 開放条件時の共振周波数
    antiresonance_freqs_open = []  # 開放条件時の反共振周波数
    # 整数n
    n_length = range(5)  # range(3)だと, 0 ~ 2
    for n in n_length:
        # 共振周波数（開放）
        # nは0から
        resonance_freq_open = (2 * n + 1) / resonance_denominator_open
        resonance_freqs_open.append(resonance_freq_open)
        # 反共振周波数（開放）
        # nは1から
        if n == 0:
            continue
        antiresonance_freq_open = n / antiresonance_denominator_open
        antiresonance_freqs_open.append(antiresonance_freq_open)
    resonance_freqs_short = antiresonance_freqs_open  # 短絡条件時の共振周波数
    antiresonance_freqs_short = resonance_freqs_open  # 短絡条件時の反共振周波数

    conditions = [
        {"shouldMatching": True, "impedance": 50},
        {"shouldMatching": False, "impedance": 1e6},
        {"shouldMatching": False, "impedance": 1e-6},
    ]
    for (i, condition) in enumerate(conditions):
        # ケーブルが損失あり、かつマッチング条件のときスキップ
        # if (cable.resistance != 0 or cable.conductance != 0) and i == 0:
        #     continue
        fig, ax = plt.subplots()

        tfs = []
        for frequency_Hz in tqdm(frequencies_Hz, leave=False):
            tf = tfModules.createTransferFunction(frequency_Hz, condition, cable)
            tfs.append(tf)

        ax.plot(
            frequencies_Hz,
            # np.abs(tfs),
            list(map(util.convertGain2dB, tfs)),
        )
        if cable.resistance == 0 and cable.conductance == 0:
            if i == 1:
                # open
                ax.scatter(
                    resonance_freqs_open,
                    list(
                        map(
                            util.convertGain2dB,
                            # abs,
                            tfModules.calcTfsBySomeFreqs(
                                resonance_freqs_open, condition, cable
                            ),
                        )
                    ),
                    # marker="v",
                    color="blue",
                    # linestyle="",
                )
                ax.scatter(
                    antiresonance_freqs_open,
                    list(
                        map(
                            util.convertGain2dB,
                            # abs,
                            tfModules.calcTfsBySomeFreqs(
                                antiresonance_freqs_open, condition, cable
                            ),
                        )
                    ),
                    # marker="o",
                    color="red",
                    # linestyle="",
                )
                ax.legend(["全ての周波数", "共振周波数", "反共振周波数"], loc="best")
            elif i == 2:
                # short
                ax.scatter(
                    resonance_freqs_short,
                    list(
                        map(
                            util.convertGain2dB,
                            # abs,
                            tfModules.calcTfsBySomeFreqs(
                                resonance_freqs_short, condition, cable
                            ),
                        )
                    ),
                    # marker="v",
                    color="blue",
                    # linestyle="",
                )
                ax.scatter(
                    antiresonance_freqs_short,
                    list(
                        map(
                            util.convertGain2dB,
                            # abs,
                            tfModules.calcTfsBySomeFreqs(
                                antiresonance_freqs_short, condition, cable
                            ),
                        )
                    ),
                    # marker="o",
                    color="red",
                    # linestyle="",
                )
                ax.legend(["全ての周波数", "共振周波数", "反共振周波数"], loc="best")
        text = (
            "matching"
            if condition["shouldMatching"]
            else "open"
            if condition["impedance"] >= 1e6
            else "short"
        )
        text = f"受電端側の抵抗値{'{:.2e}'.format(condition['impedance'])}[Ω]"
        FONT_SIZE = 12
        ax.set_title(f"{text}")
        ax.set_ylabel("Gain[dB]", fontsize=FONT_SIZE)  # y軸は、伝達関数の絶対値
        ax.set_xlabel("frequency [MHz]", fontsize=FONT_SIZE)
        # ax.set_yscale("log")  # y軸はlogスケールで表示する
        ax.xaxis.set_major_formatter(
            pltSettings.FixedOrderFormatter(6, useMathText=True)
        )
        if cable.resistance == 0 and cable.conductance == 0:
            # 最大値と最小値の差がほぼない場合, y軸のスケールを変更する
            if max(np.abs(tfs)) - min(np.abs(tfs)) < 1e-6:
                ax.set_ylim(-10, 10)

    if fileName != "":
        fig.savefig(util.createImagePath(fileName))

    plt.tight_layout()
    plt.show()


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
    # 無損失ケーブル用
    # list(range(0, 5 * util.ONE_HUNDRED, 1000)),
    # cable.cable_noLoss_vertual,
    # 損失ありケーブル用
    list(range(0, 100 * util.ONE_HUNDRED, 10000)),
    cable.cable_vertual,
)
