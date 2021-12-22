import cmath
import math
import warnings

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

import cable
from snippet import drawFrequencyResponse
import util

# warnings.resetwarnings()
# warnings.simplefilter("error")


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


def drawBodePlot(frequencies_Hz, endCondition, cable, fileName=""):
    """
    分布定数線路のボード線図をグラフに表示する

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

    conditions = [
        {"shouldMatching": True, "impedance": 0},
        {"shouldMatching": False, "impedance": 1e6},
        {"shouldMatching": False, "impedance": 1e-6},
    ]
    fig, axes = plt.subplots(1, 3)
    for (i, condition) in enumerate(conditions):
        tfs = []
        for frequency_Hz in tqdm(frequencies_Hz, leave=False):
            tf = createTransferFunction(frequency_Hz, condition, cable)
            tfs.append(tf)

        axes[i].plot(
            frequencies_Hz,
            list(map(lambda tf: abs(tf), tfs)),
            # list(map(util.convertGain2dB, tfs)),
        )
        text = (
            "matching"
            if condition["shouldMatching"]
            else "open"
            if condition["impedance"] >= 1e6
            else "short"
        )
        axes[i].set_title(f"{text}")
        axes[i].set_ylabel("|H(f)|")
        axes[i].set_xlabel("frequency [Hz]")
        axes[i].set_yscale("log")
        axes[i].ticklabel_format(style="sci",  axis="x",scilimits=(0,0))
        if max(np.abs(tfs)) - min(np.abs(tfs)) < 1e-6:
            axes[i].set_ylim(1e-1, 1e3)

    if fileName != "":
        fig.savefig(f"{fileName}")

    plt.subplots_adjust(
        left=0.0625, bottom=0.1, right=0.98, top=0.9, wspace=0.2, hspace=0.35
    )
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
    np.logspace(4, 6, 1000, base=10),
    {"shouldMatching": True, "impedance": 1e6},
    cable_noLoss_vertual,
)


def squareWaveFftAndIfft():
    f = 1000
    rate = 44100  # サンプリング周波数（ナイキスト周波数は44100 / 2）
    # 方形波
    T = np.arange(0, 0.01, 1 / rate)  # len(T) => 441, 1 / rate はサンプリング周期
    squareWaves_time = np.sign(np.sin(2 * np.pi * f * T))
    inputWaves_time = squareWaves_time
    # sinc関数
    # T = np.linspace(-10, 10, 1000)
    # sincWaves_time = np.sinc(T)
    # inputWaves_time = sincWaves_time

    fig, axes = plt.subplots(3, 2)
    axes = axes.flatten()

    axes[0].plot(T, inputWaves_time)
    axes[0].set_title("input(t)")
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Gain")

    # フーリエ変換
    # 各離散値は、それぞれlen(離散信号列)個の複素正弦波の一次結合で表される（DFT）
    # inputWaves_fft = np.fft.fft(inputWaves_time)
    inputWaves_fft = np.fft.rfft(inputWaves_time)

    # 離散フーリエ変換のサンプル周波数を返す（rfft, irfftで使用するため）
    # np.fft.fftfreq(ウィンドウの長さ, サンプリングレートの逆数)
    # frequencies = np.fft.fftfreq(len(inputWaves_time), 1.0 / rate)
    frequencies = np.fft.rfftfreq(len(inputWaves_time), 1.0 / rate)

    axes[1].plot(frequencies, np.abs(inputWaves_fft))  # absで振幅を取得
    axes[1].set_title("abs(F[input(t)])")
    axes[1].set_xlabel("Frequency")
    axes[1].set_ylabel("Power")

    tfs = calcTfsBySomeFreqs(
        frequencies,
        {"shouldMatching": True, "impedance": 1e6},
        cable.Cable(
            resistance=0,
            # ケーブルの特性インピーダンスの計算結果が50[Ω]になるように意図的に値を設定
            inductance=100e-12 * 50 ** 2,
            conductance=0,
            capacitance=100e-12,
            length=1000,
        ),
    )

    axes[2].plot(frequencies, list(map(lambda tf: abs(tf), tfs)))
    axes[2].set_title("|H(f)|")
    axes[2].set_xlabel("Frequency")
    axes[2].set_ylabel("Gain [dB]")
    # axes[2].set_yscale("log")

    # convolution = []
    # for (fft_data, tf) in zip(inputWaves_fft, tfs):
    #     convolution.append(fft_data * tf)
    convolution = np.array(inputWaves_fft, dtype=np.complex) * np.array(
        tfs, dtype=np.complex
    )
    # convolution = np.array(inputWaves_fft, dtype=np.complex) * np.array(
    #     list(map(lambda tf: abs(tf), tfs)), dtype=np.complex
    # )

    # 入力波形のフーリエ変換 * 伝達関数
    axes[3].plot(frequencies, np.abs(convolution))  # absで振幅を取得
    axes[3].set_title("abs(F[input(t)] * H(f))")
    axes[3].set_xlabel("Frequency")
    axes[3].set_ylabel("Power")

    # 逆フーリエ変換
    # r = np.fft.ifft(convolution, len(T))
    #  irfft: 33点のrfft結果を入力すれば64点の時間領域信号が得られる。
    r = np.fft.irfft(convolution, len(T))
    axes[4].plot(T, r)
    axes[4].set_title("output(t)")
    axes[4].set_xlabel("Time")
    axes[4].set_ylabel("Gain")

    plt.tight_layout()
    plt.show()


# squareWaveFftAndIfft()
