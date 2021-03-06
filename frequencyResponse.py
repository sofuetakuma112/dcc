import math

import matplotlib
import pandas as pd

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

import numpy as np
from tqdm import tqdm

import util
import cable
import transferFunction as tfModules


def drawFrequencyResponse(frequencies_Hz, cable, showMeasuredValue=False, fileName=""):
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
        fig, ax = plt.subplots()

        tfs = [
            tfModules.createTransferFunction(frequency_Hz, condition, cable)
            for frequency_Hz in tqdm(frequencies_Hz, leave=False)
        ]

        ax.plot(
            [freq / 1e6 for freq in frequencies_Hz],
            list(map(util.convertGain2dB, tfs)),
            label="シミレーション",
        )
        if cable.resistance == 0 and cable.conductance == 0:
            if i == 1:
                # open
                ax.scatter(
                    [freq / 1e6 for freq in resonance_freqs_open],
                    list(
                        map(
                            util.convertGain2dB,
                            tfModules.calcTfsBySomeFreqs(
                                resonance_freqs_open, condition, cable
                            ),
                        )
                    ),
                    marker="x",
                    color="blue",
                )
                ax.scatter(
                    [freq / 1e6 for freq in antiresonance_freqs_open],
                    list(
                        map(
                            util.convertGain2dB,
                            tfModules.calcTfsBySomeFreqs(
                                antiresonance_freqs_open, condition, cable
                            ),
                        )
                    ),
                    color="red",
                )
                ax.legend(["全ての周波数", "共振周波数", "反共振周波数"], loc="best")
            elif i == 2:
                # short
                ax.scatter(
                    [freq / 1e6 for freq in resonance_freqs_short],
                    list(
                        map(
                            util.convertGain2dB,
                            tfModules.calcTfsBySomeFreqs(
                                resonance_freqs_short, condition, cable
                            ),
                        )
                    ),
                    marker="x",
                    color="blue",
                )
                ax.scatter(
                    [freq / 1e6 for freq in antiresonance_freqs_short],
                    list(
                        map(
                            util.convertGain2dB,
                            tfModules.calcTfsBySomeFreqs(
                                antiresonance_freqs_short, condition, cable
                            ),
                        )
                    ),
                    color="red",
                )
                ax.legend(["全ての周波数", "共振周波数", "反共振周波数"], loc="best")
        text = (
            "インピーダンスマッチング条件における周波数特性"
            if condition["shouldMatching"]
            else "受電端開放条件における周波数特性"
            if condition["impedance"] >= 1e6
            else "受電端短絡条件における周波数特性"
        )
        FONT_SIZE = 16
        ax.set_ylabel("$H_{dB}$[dB]", fontsize=FONT_SIZE)  # y軸は、伝達関数の絶対値
        ax.tick_params(axis="y", labelsize=FONT_SIZE)
        ax.set_xlabel("Frequency[MHz]", fontsize=FONT_SIZE)
        ax.tick_params(axis="x", labelsize=FONT_SIZE)
        ax.xaxis.get_offset_text().set_fontsize(FONT_SIZE)
        if cable.resistance == 0 and cable.conductance == 0:
            # 最大値と最小値の差がほぼない場合, y軸のスケールを変更する
            if max(np.abs(tfs)) - min(np.abs(tfs)) < 1e-6:
                ax.set_ylim(-10, 10)

        # 測定した伝達関数をグラフ表示
        if showMeasuredValue:
            df = pd.read_csv("csv/bode_rg58au.csv", skiprows=27)
            frequencies_Hz = list(df["Frequency(Hz)"])
            amps = list(df["CH1 Amplitude(dB)"])
            ax.plot(
                [frequency_Hz / 1e6 for frequency_Hz in frequencies_Hz],
                amps,
                label="実測値",
            )
            ax.legend(fontsize=FONT_SIZE - 2)

    if fileName != "":
        fig.savefig(util.createImagePath(fileName))

    plt.tight_layout()
    plt.show()


drawFrequencyResponse(
    # 無損失ケーブル用
    # list(range(0, 5 * util.ONE_HUNDRED, 1000)),
    # cable.cable_noLoss_vertual,
    # 損失ありケーブル用
    list(range(0, 50 * util.ONE_HUNDRED, 10000)),
    cable.cable_vertual,
    # showMeasuredValue=True,
)
