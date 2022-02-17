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
