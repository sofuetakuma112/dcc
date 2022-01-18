import cmath
import math
import math

import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

import numpy as np
from tqdm import tqdm

import cable
from snippet import drawFrequencyResponse
import util


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


def drawFrequencyResponse(frequencies_Hz, cable, fileName=""):
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
    # fig, axes = plt.subplots(1, 3)
    for (i, condition) in enumerate(conditions):
        fig, ax = plt.subplots()
        axes = [ax, ax, ax]

        tfs = []
        for frequency_Hz in tqdm(frequencies_Hz, leave=False):
            tf = createTransferFunction(frequency_Hz, condition, cable)
            tfs.append(tf)

        # if i == 2:
        #     print(list(map(abs, tfs)))

        axes[i].plot(
            frequencies_Hz,
            list(map(abs, tfs)),
            # list(map(util.convertGain2dB, tfs)),
        )
        if cable.resistance == 0 and cable.conductance == 0:
            # 無損失ケーブル
            if i == 1:
                # open
                axes[i].plot(
                    resonance_freqs_open,
                    list(
                        map(
                            abs,
                            calcTfsBySomeFreqs(resonance_freqs_open, condition, cable),
                        )
                    ),
                    marker="v",
                    color="blue",
                    linestyle="",
                )
                axes[i].plot(
                    antiresonance_freqs_open,
                    list(
                        map(
                            abs,
                            calcTfsBySomeFreqs(
                                antiresonance_freqs_open, condition, cable
                            ),
                        )
                    ),
                    marker="o",
                    color="red",
                    linestyle="",
                )
                axes[i].legend(["全ての周波数", "共振周波数", "反共振周波数"], loc="best")
            elif i == 2:
                # short
                axes[i].plot(
                    resonance_freqs_short,
                    list(
                        map(
                            abs,
                            calcTfsBySomeFreqs(resonance_freqs_short, condition, cable),
                        )
                    ),
                    marker="v",
                    color="blue",
                    linestyle="",
                )
                axes[i].plot(
                    antiresonance_freqs_short[1:],
                    list(
                        map(
                            abs,
                            calcTfsBySomeFreqs(
                                antiresonance_freqs_short[1:], condition, cable
                            ),
                        )
                    ),
                    marker="o",
                    color="red",
                    linestyle="",
                )
                axes[i].legend(["全ての周波数", "共振周波数", "反共振周波数"], loc="best")
        text = (
            "matching"
            if condition["shouldMatching"]
            else "open"
            if condition["impedance"] >= 1e6
            else "short"
        )
        axes[i].set_title(f"{text}")
        axes[i].set_ylabel("|H(f)|")  # y軸は、伝達関数の絶対値
        axes[i].set_xlabel("frequency [Hz]")
        axes[i].set_yscale("log")  # y軸はlogスケールで表示する
        axes[i].ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
        if cable.resistance == 0 and cable.conductance == 0:
            if max(np.abs(tfs)) - min(np.abs(tfs)) < 1e-6:
                axes[i].set_ylim(1e-1, 1e3)

    if fileName != "":
        fig.savefig(util.createImagePath(fileName))

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
    inductance=100e-12 * 50 ** 2,  # C * Zo ** 2
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
    # list(range(10000, 1000000, 100)),
    list(range(0, 1000000, 100)),
    cable_noLoss_vertual,
    # cable.Cable(
    #     resistance=1e-3,
    #     inductance=100e-12 * 50 ** 2,  # C * Zo ** 2
    #     conductance=1e-4,
    #     capacitance=100e-12,
    #     length=1000,
    # ),
)


def squareWaveFftAndIfft(cable, endCondition):
    # サンプリング周期の逆数が入力波形の周波数？
    f = 1000
    rate = 44100  # サンプリング周波数（1秒間に何回サンプリングするか、ナイキスト周波数は44100 / 2）
    # 方形波
    T = np.arange(
        0, 0.0087, 1 / rate  # 0.0087は単パルスが真ん中に来るよう調整した
    )  # len(T) => 441, 1 / rate はサンプリング周期（何秒おきにサンプリングするか）
    # 足し合わされる波は、入力波の周波数の整数倍の周波数を持つ
    squareWaves_time = np.sign(np.sin(2 * np.pi * f * T))
    prevIndex = 0
    indexChunk = []
    chunks = []
    for index, discreteValue in enumerate(squareWaves_time):
        if discreteValue == 1:
            if prevIndex + 1 == index:
                # 同じ-1の塊に現在いる
                indexChunk.append(index)
            else:
                # 次の-1の塊に移動した
                chunks.append(indexChunk)
                indexChunk = []
            prevIndex = index

    single_palse = []
    # print(chunks[4])
    # print("単パルス波形の周波数？ => ", 1 / (len(chunks[4]) * (1 / rate)))
    for index, y in enumerate(squareWaves_time):
        if index in chunks[4]:
            single_palse.append(y)
        else:
            single_palse.append(0)
    inputWaves_time = list(single_palse)

    # sinc関数
    # T = np.linspace(-10, 10, 1000)
    # sincWaves_time = np.sinc(T)
    # inputWaves_time = sincWaves_time

    fig, axes = plt.subplots(3, 2)
    axes = axes.flatten()
    # fig, axes = plt.subplots()
    # fig, axes1 = plt.subplots()
    # fig, axes2 = plt.subplots()
    # fig, axes3 = plt.subplots()
    # fig, axes4 = plt.subplots()
    # fig, axes5 = plt.subplots()
    # axes = [axes, axes1, axes2, axes3, axes4, axes5]

    axes[0].plot(T, inputWaves_time)
    axes[0].set_title("input(t)")
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Gain")
    axes[0].set_xlabel("time [s]")

    # フーリエ変換
    # 各離散値は、それぞれlen(離散信号列)個の複素正弦波の一次結合で表される（DFT）
    # 実数をFFTする場合、
    # 負の周波数のフーリエ係数の値は、
    # 対応する正の周波数のフーリエ係数の虚数部分を打ち消すために共役な値をとる為、
    # 情報としては正の周波数部分のみで十分
    # numpy.fft.fft(
    # FFTを行う配列,
    # FFTを行うデータ点数。Noneとするとaの長さに等しくなる,
    # FFTを行う配列の軸方向。指定しなければ、配列の最大次元の方向となる,
    # "ortho"とすると正規化する。正規化すると変換値が1/√Nになる（Nはデータ点数
    # )
    # numpy.fft.fft()の戻り値は、長さnの複素数配列
    # inputWaves_fft = np.fft.fft(inputWaves_time)
    # 工学系の用途向けに、実数のFFTに特化した np.fft.rfft が用意されている。
    inputWaves_fft = np.fft.rfft(inputWaves_time)

    # 離散フーリエ変換のサンプル周波数を返す（rfft, irfftで使用するため）
    # np.fft.fftfreq(FFTを行うデータ点数, サンプリング周期) # サンプリング周期次第で時系列データの時間軸の長さが決定する（100点, 0.01）なら100 * 0.01[s]の時系列データということになる？
    # frequencies = np.fft.fftfreq(len(inputWaves_time), 1.0 / rate)
    frequencies = np.fft.rfftfreq(
        len(inputWaves_time), 1.0 / rate
    )  # len(frequencies) => 193, 1/rate はサンプリング周期（何秒おきにサンプリングするか）
    # print(frequencies, len(frequencies))

    axes[1].plot(frequencies, np.abs(inputWaves_fft))  # absで振幅を取得
    axes[1].set_title("abs(F[input(t)])")
    axes[1].set_xlabel("Frequency")
    axes[1].set_ylabel("|F[input(t)]|")
    axes[1].set_xlabel("Frequency [Hz]")

    tfs = calcTfsBySomeFreqs(
        frequencies,
        endCondition,
        cable,
    )

    axes[2].plot(frequencies, list(map(lambda tf: abs(tf), tfs)))
    axes[2].set_title("abs(H(f))")
    axes[2].set_xlabel("Frequency")
    axes[2].set_ylabel("|H(f)|")
    axes[2].set_xlabel("Frequency [Hz]")
    # axes[2].set_yscale("log")

    convolution = np.array(inputWaves_fft) * np.array(
        tfs
    )  # 時間軸の畳み込み積分 = フーリエ変換した値同士の積(の値も周波数軸のもの)
    # convolution = np.array(inputWaves_fft, dtype=np.complex) * np.array(
    #     list(map(lambda tf: abs(tf), tfs)), dtype=np.complex
    # )

    # 入力波形のフーリエ変換 * 伝達関数
    axes[3].plot(frequencies, np.abs(convolution))  # absで振幅を取得
    axes[3].set_title("abs(F[input(t)] * H(f))")
    axes[3].set_xlabel("Frequency")
    axes[3].set_ylabel("|F[input(t)] * H(f)|")
    axes[3].set_xlabel("Frequency [Hz]")

    # 逆フーリエ変換
    # r = np.fft.ifft(convolution, len(T))
    # 入力波形が実数データ向けの逆FFT np.fft.irfft が用意されている。
    # 33点のrfft結果を入力すれば64点の時間領域信号が得られる。
    # 入力波形が実数値のみなので、出力波形も虚数部分は捨ててよい？
    r = np.fft.irfft(convolution, len(T))
    axes[4].plot(T, np.real(r))
    axes[4].set_title("output(t).real")
    axes[4].set_xlabel("Time")
    axes[4].set_ylabel("Gain")
    axes[4].set_xlabel("time [s]")

    r = np.fft.irfft(convolution, len(T))
    axes[5].plot(T, np.imag(r))
    axes[5].set_title("output(t).imag")
    axes[5].set_xlabel("Time")
    axes[5].set_ylabel("Gain")

    plt.tight_layout()
    plt.show()


# squareWaveFftAndIfft(
#     cable.Cable(
#         resistance=1e-3,  # 無損失ケーブルを考える
#         # ケーブルの特性インピーダンスの計算結果が50[Ω]になるように意図的に値を設定
#         inductance=100e-12 * 50 ** 2,
#         conductance=1e-4,  # 無損失ケーブルを考える
#         capacitance=100e-12,  # シートの値を参考に設定？
#         length=1000,
#     ),
#     {"shouldMatching": False, "impedance": 1e-6},  # 受電端の抵抗が0のとき、断線していない正常のケーブル？
# )
