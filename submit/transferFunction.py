import cmath
import math
import warnings

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

import cable
import util

warnings.resetwarnings()
warnings.simplefilter("error")


def calculateTheta(frequency_Hz, cable):
    """
    伝搬定数γと同軸ケーブルの長さlの積を求める

    Parameters
    ----------
    frequency_Hz : float
        周波数(Hz)
    cable : instance
        Cableクラスのインスタンス
    """
    omega = 2 * np.pi * frequency_Hz

    R = cable.resistance  # Ω/m
    L = cable.inductance  # H/m
    G = cable.conductance  # S/m
    C = cable.capacitance  # F/m

    gamma = cmath.sqrt((R + 1j * omega * L) * (G + 1j * omega * C))
    theta = gamma * cable.length

    return theta


def createFMatrixForDcc(frequency_Hz, theta, cable):
    """
    分布定数回路のF行列を求める

    Parameters
    ----------
    frequency_Hz : float
        周波数(Hz)
    theta : float
        伝搬定数γと同軸ケーブルの長さlの積
    cable : instance
        Cableクラスのインスタンス
    """

    cosh = cmath.cosh(theta)
    sinh = cmath.sinh(theta)
    return np.array(
        [
            [cosh, cable.calcCharacteristicImpedance(frequency_Hz) * sinh],
            [sinh / cable.calcCharacteristicImpedance(frequency_Hz), cosh],
        ]
    )


def createTransferFunction(frequency_Hz, shouldMatching, cable):
    """
    受電端に抵抗を接続した分布定数回路の伝達関数を求める

    Parameters
    ----------
    frequency_Hz : float
        周波数(Hz)
    shouldMatching: boolean
        マッチングさせるか
    cable : instance
        Cableクラスのインスタンス
    """
    # 分布定数線路のF行列を求める
    f_matrix_dcc = createFMatrixForDcc(
        frequency_Hz, calculateTheta(frequency_Hz, cable), cable
    )

    if shouldMatching:
        # 線路の特性インピーダンスと、受電端の抵抗のインピーダンスを同じにする
        endImpedance = cable.calcCharacteristicImpedance(frequency_Hz)
    else:
        # 受電端のインピーダンスを50Ωに固定する
        endImpedance = 50

    # F行列と末端のインピーダンスから伝達関数を計算する
    return util.createTransferFunctionFromFMatrix(endImpedance, f_matrix_dcc)


def drawFrequencyResponse(frequencies_Hz, shouldMatching, cable, fileName=""):
    """
    分布定数線路の周波数特性をグラフに表示する

    Parameters
    ----------
    frequencies_Hz : list
        周波数(Hz)のリスト
    shouldMatching: boolean
        マッチングさせるか
    cable : instance
        Cableクラスのインスタンス
    fileName: string
        表示するグラフを保存する際のファイル名
    """

    tfs = []
    tfs_nthPwrOf10 = []
    # 周波数ごとに伝達関数を求める
    for frequency_Hz in tqdm(frequencies_Hz, leave=False):
        #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
        tf = createTransferFunction(frequency_Hz, shouldMatching, cable)
        tfs.append(tf)

        # 周波数が10のn乗ごとに、伝達関数の計算結果を控えておく
        if frequency_Hz > 1 and math.log10(frequency_Hz).is_integer():
            tfs_nthPwrOf10.append({"frequency_Hz": frequency_Hz, "tf": tf})

    # ゲインの傾きを求める
    slope = util.calcMinimumSlope(tfs_nthPwrOf10)
    print(f"傾き: {slope}[dB/dec]")

    fig, ax = plt.subplots()
    ax.plot(
        frequencies_Hz,
        list(map(util.convertGain2dB, tfs)),
    )
    ax.set_xlabel("frequency [Hz]")
    ax.set_ylabel("Gain [dB]")
    ax.set_xscale("log")
    ax.set_yticks([-20, 0, 5])

    if fileName != "":
        fig.savefig(f"{fileName}")
    plt.show()


# ケーブルのインスタンスを作成
cable_vertual = cable.Cable(
    resistance=1e-6,
    inductance=1.31e-7,
    conductance=1e-4,
    capacitance=67e-12,
    length=1000,
)

# 無損失ケーブル
cable_noLoss_vertual = cable.Cable(
    resistance=0,
    inductance=1.31e-7,
    conductance=0,
    capacitance=67e-12,
    length=1000,
)

# ケーブルの周波数特性をグラフにする
frequencies_Hz = list(range(0, 10000, 10))
frequencies_Hz.extend(list(range(10000, 200 * 10 ** 6, 10000)))
# drawFrequencyResponse(frequencies_Hz, True, cable_vertual)
drawFrequencyResponse(frequencies_Hz, True, cable_noLoss_vertual)
