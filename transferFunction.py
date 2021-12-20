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


def createTransferFunction(frequency_Hz, endCondition, cable):
    """
    受電端に抵抗を接続した分布定数回路の伝達関数を求める

    Parameters
    ----------
    frequency_Hz : float
        周波数(Hz)
    endCondition: dict
        受電端の抵抗の条件
    cable : instance
        Cableクラスのインスタンス
    """
    # 分布定数線路のF行列を求める
    f_matrix_dcc = createFMatrixForDcc(
        frequency_Hz, calculateTheta(frequency_Hz, cable), cable
    )

    if endCondition["shouldMatching"]:
        # 線路の特性インピーダンスと、受電端の抵抗のインピーダンスを同じにする
        endImpedance = cable.calcCharacteristicImpedance(frequency_Hz)
    else:
        endImpedance = endCondition["impedance"]

    # F行列と末端のインピーダンスから伝達関数を計算する
    return util.createTransferFunctionFromFMatrix(endImpedance, f_matrix_dcc)


def drawFrequencyResponse(frequencies_Hz, endCondition, cable, fileName=""):
    """
    分布定数線路の周波数特性をグラフに表示する

    Parameters
    ----------
    frequencies_Hz : list
        周波数(Hz)のリスト
    endCondition: dict
        受電端の抵抗の条件
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
        tf = createTransferFunction(frequency_Hz, endCondition, cable)
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
        # list(map(util.convertGain2dB, tfs)),
        list(map(lambda tf: abs(tf), tfs)),
    )
    axes[0].set_xlabel("frequency [Hz]")
    # axes[0].set_ylabel("Gain [dB]")
    # axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    # axes[0].set_yticks([-5, 0, 5])

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


def calcTfsBySomeFreqs(frequencies_Hz, endCondition, cable):
    tfs = []
    for frequency_Hz in tqdm(frequencies_Hz, leave=False):
        #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
        tf = createTransferFunction(frequency_Hz, endCondition, cable)
        tfs.append(tf)
    return tfs


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
    # inductance=1.31e-7,
    # 特性インピーダンスの計算結果が50[Ω]になるように意図的に値を設定
    inductance=100e-12 * 50 ** 2,
    conductance=0,
    # capacitance=67e-12,
    capacitance=100e-12,
    length=1000,
)

# ケーブルの周波数特性をグラフにする
frequencies_Hz = list(range(0, 10000, 10))
frequencies_Hz.extend(list(range(10000, 200 * 10 ** 6, 10000)))
# drawFrequencyResponse(
#     np.logspace(4, 6, 1000, base=10),
#     {"shouldMatching": False, "impedance": 1e6},
#     cable_vertual,
# )
# drawFrequencyResponse(
#     np.logspace(4, 6, 1000, base=10),
#     {"shouldMatching": False, "impedance": 1e6},
#     cable_noLoss_vertual,
# )

def testFftAndIfft():
    # 正弦波のデータ作成
    f = 1000
    rate = 44100
    T = np.arange(0, 0.01, 1 / rate)
    s = []
    for t in T:
        v = np.sin(2 * np.pi * f * t)
        s.append(v)

    fig, axes = plt.subplots(1, 3)

    axes[0].plot(T, s)
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Gain")

    # フーリエ変換
    # rfft: 実数?入力に対して1次元離散フーリエ変換を計算する
    fft_data = np.abs(np.fft.rfft(s))

    # rfftfreq: 離散フーリエ変換のサンプル周波数を返す(rfft, irfftで使用するため)。
    freqList = np.fft.rfftfreq(len(s), 1.0 / rate)  # 横軸

    # loglog: X 軸と Y 軸の両方に沿って対数スケーリングを行う
    axes[1].loglog(freqList, 10 * np.log(fft_data))

    axes[1].set_xlabel("Frequency")
    axes[1].set_ylabel("Power")

    # 逆フーリエ変換
    # 位相は考慮されていないため余弦波になる
    r = np.fft.irfft(fft_data, len(T))
    axes[2].plot(T, r)
    axes[2].set_xlabel("Time")
    axes[2].set_ylabel("Gain")

    plt.show()

def squareWaveFftAndIfft():
    f = 1000
    rate = 44100
    T = np.arange(0, 0.01, 1 / rate)
    s = []
    for t in T:
        v = np.sign(np.sin(2 * np.pi * f * t))
        s.append(v)

    fig, axes = plt.subplots(1, 3)

    axes[0].plot(T, s)
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Gain")

    # フーリエ変換
    fft_data_list = np.abs(np.fft.rfft(s))
    # 0を1e-6に置き換える
    fft_data_replaced_zero_list = [1e-6 if fft_data == 0 else fft_data for fft_data in fft_data_list]
    freqList = np.fft.rfftfreq(len(s), 1.0 / rate)  # 横軸
    axes[1].loglog(freqList, 10 * np.log(fft_data_replaced_zero_list))
    axes[1].set_xlabel("Frequency")
    axes[1].set_ylabel("Power")

    # 逆フーリエ変換
    r = np.fft.irfft(fft_data_list, len(T))
    axes[2].plot(T, r)
    axes[2].set_xlabel("Time")
    axes[2].set_ylabel("Gain")

    plt.show()
    
    # # 矩形波を生成
    # times_in = np.linspace(0, 10, Len)  # 時刻配列(0 ~ 10を1024分割したリスト)
    # freq = 1 * 10 ** 0  # 矩形波の周波数
    # amp = 1.0  # 矩形波の振幅
    # squareWaves = np.sign(amp * np.sin(2 * np.pi * freq * times_in))

    # # 矩形波をフーリエ変換
    # # fft: 一次元離散フーリエ変換を計算する
    # squareWaves_fft = np.fft.fft(squareWaves)  # len(fk.shape) => (Len,)

# testFftAndIfft()
squareWaveFftAndIfft()