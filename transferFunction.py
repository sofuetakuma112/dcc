import numpy as np
import matplotlib.pyplot as plt
import math
import cmath
from tqdm import tqdm
import cables
import util
import warnings

warnings.resetwarnings()
warnings.simplefilter("error")


def calculateTheta(frequency_Hz, cableInfo):
    """
    伝搬定数γと同軸ケーブルの長さlの積を求める
    G = 0で考える

    Parameters
    ----------
    frequency_Hz : float
        周波数(Hz)
    cableInfo : dictionary
        ケーブルの仕様
    """
    omega = 2 * np.pi * frequency_Hz

    R = cableInfo.resistance  # Ω/m
    L = cableInfo.inductance  # H/m
    C = cableInfo.capacitance  # F/m
    G = cableInfo.conductance  # S/m 回路における電流の流れやすさ

    # cmathを使わないとエラーが返ってくる
    # R=G=0で以下の式を計算しているのならば
    # alpha = 0
    # beta = omega * math.sqrt(L * C)
    # で、gamma = alpha + beta * 1j
    # で計算した値とほぼ一致している
    gamma = cmath.sqrt((R + omega * L * 1j) * (G + omega * C * 1j))
    theta = gamma * cableInfo.length

    return theta


def createFMatrixForDcc(frequency_Hz, theta, cableInfo):
    """
    分布定数回路のF行列を求める

    Parameters
    ----------
    cableInfo : dictionary
        ケーブルの仕様
    theta : float
        伝搬定数γと同軸ケーブルの長さlの積
    """
    try:
        cosh = cmath.cosh(theta)
    except OverflowError:
        cosh = 1e6 * 1j * 1e6
    try:
        sinh = cmath.sinh(theta)
    except OverflowError:
        sinh = 1e6 * 1j * 1e6

    return np.array(
        [
            [cosh, cableInfo.calcCharacteristicImpedance(frequency_Hz) * sinh],
            [sinh / cableInfo.calcCharacteristicImpedance(frequency_Hz), cosh],
        ]
    )


# TODO: cableInfoのインスタンス版に対応する
def calculateInputImpedanceByFMatrix(Zr, frequency_Hz, cableInfo):
    """
    受電端に抵抗を接続した分布定数回路の入力インピーダンスを求める
    与えられた周波数から入力インピーダンスを求める

    Parameters
    ----------
    Zr : float
        受電端のインピーダンス
    frequency_Hz : float
        周波数
    cableInfo : dictionary
        ケーブルの仕様
    """
    # γlを求める
    theta = calculateTheta(frequency_Hz, cableInfo)

    # 分布定数回路のF行列
    f_matrix_dcc = createFMatrixForDcc(cableInfo, theta)
    # 受電端のZrのF行列
    f_matrix_Zr = np.array(
        [
            [1, 0],
            [1 / Zr, 1],
        ]
    )

    # 受信端にZrを接続した場合のf行列
    f_matrix = np.dot(f_matrix_dcc, f_matrix_Zr)

    return f_matrix[0, 0] / f_matrix[1, 0]


def createTransferFunction(Zr, frequency_Hz, cableInfo):
    """
    受電端に抵抗を接続した分布定数回路の伝達関数を求める

    Parameters
    ----------
    Zr : float
        受電端のインピーダンス
    frequency_Hz : float
        周波数(Hz)
    cableInfo : dictionary
        ケーブルの仕様
    """

    f_matrix_dcc = createFMatrixForDcc(
        frequency_Hz, calculateTheta(frequency_Hz, cableInfo), cableInfo
    )

    # endImpedance = Zr
    endImpedance = cableInfo.calcCharacteristicImpedance(frequency_Hz)
    # endImpedance = float('inf')
    # endImpedance = 1e-8
    return util.createTransferFunctionFromFMatrix(endImpedance, f_matrix_dcc)


def drawFrequencyResponse(frequencies_Hz, cableInfo, fileName=""):
    # transferFunctions1 = []
    transferFunctions2 = []
    tfs_nthPwrOf10 = []
    # 周波数ごとに伝達関数を求める
    for frequency_Hz in tqdm(frequencies_Hz):
        # 5C-2V + Zrの回路の入力インピーダンスを求める
        # 仮想ケーブルのインスタンス化
        # inputImpedance2 = calculateInputImpedanceByFMatrix(
        #     Zr,
        #     frequency_Hz,
        #     cables.cable_5c2v,
        # )

        # 回路全体の伝達関数を求める
        # transferFunction1 = createTransferFunction(
        #     inputImpedance2, frequency_Hz, cables.cable_3d2v
        # )
        # transferFunctions1.append(transferFunction1)

        #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
        transferFunction2 = createTransferFunction(Zr, frequency_Hz, cableInfo)
        transferFunctions2.append(transferFunction2)

        if frequency_Hz > 1 and math.log10(frequency_Hz).is_integer():
            tfs_nthPwrOf10.append(
                {"frequency_Hz": frequency_Hz, "tf": transferFunction2}
            )

    # ゲインの傾きを求める
    slope = util.calcMinimumSlope(tfs_nthPwrOf10)
    print(f"slope: {slope}[dB/dec]")

    fig, axes = plt.subplots(1, 2)

    axes[0].plot(
        frequencies_Hz,
        list(map(util.convertGain2dB, transferFunctions2)),
    )
    axes[0].set_title("vertual cable + Zr")
    axes[0].set_xlabel("frequency [Hz]")
    axes[0].set_ylabel("Gain [dB]")
    axes[0].set_xscale("log")

    axes[1].plot(
        frequencies_Hz,
        list(map(lambda tf: math.atan(tf.imag / tf.real), transferFunctions2)),
    )
    axes[1].set_title("vertual cable + Zr")
    axes[1].set_xlabel("frequency [Hz]")
    axes[1].set_ylabel("theta [rad]")
    axes[1].set_xscale("log")

    # fig, ax = plt.subplots()
    # ax.plot(
    #     frequencies_Hz,
    #     list(map(util.convertGain2dB, transferFunctions2)),
    # )
    # ax.set_title("vertual cable + Zr")
    # ax.set_xlabel("frequency [Hz]")
    # ax.set_ylabel("Gain [dB]")
    # ax.set_xscale("log")

    if fileName != "":
        fig.savefig(f"{fileName}")
    plt.show()


def drawFrequencyResponseBySomeConditions(resistances, conductances, mode="r"):
    if mode == "both":
        # すべてのR, Gの組み合わせで描画する
        fig, axes = plt.subplots(len(resistances), len(conductances))
        logs = []
        for i, resistance in tqdm(enumerate(resistances)):
            for j, conductance in enumerate(conductances):
                tfs = []
                tfs_nthPwrOf10 = []
                for frequency_Hz in tqdm(frequencies_Hz, leave=False):
                    cable_vertual = cables.Cable(
                        resistance=resistance,
                        inductance=1.31e-7,
                        conductance=conductance,
                        capacitance=67e-12,
                        length=1000,
                    )
                    #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
                    tf = createTransferFunction(Zr, frequency_Hz, cable_vertual)
                    tfs.append(tf)

                    if frequency_Hz > 1 and math.log10(frequency_Hz).is_integer():
                        tfs_nthPwrOf10.append({"frequency_Hz": frequency_Hz, "tf": tf})

                # 周波数特性の傾きを求める
                slope = util.calcMinimumSlope(tfs_nthPwrOf10)
                # 傾きのリストの中から最小値を選択する
                logs.append(
                    f"R = {resistance}, G = {conductance}, slope: {slope}[dB/dec]"
                )

                axes[i][j].plot(
                    frequencies_Hz,
                    list(map(util.convertGain2dB, tfs)),
                )
                if i == 0:
                    # Gだけ表記
                    axes[i][j].set_title(f"G = {conductance}")
                if j == 0:
                    # Rだけ表記
                    axes[i][j].set_ylabel(f"R = {resistance}")
                # axes[i][j].set_xlabel("frequency [Hz]")
                # axes[i][j].set_ylabel("Gain [dB]")
                axes[i][j].tick_params(
                    labelbottom=False, labelright=False, labeltop=False
                )
                axes[i][j].set_xscale("log")
        for log in logs:
            print(log)
    elif mode == "r":
        # それぞれのRについてグラフを描画する
        fig, axes = plt.subplots(1, len(resistances))
        for i, resistance in enumerate(resistances):
            tfs = []
            for frequency_Hz in tqdm(frequencies_Hz):
                cable_vertual = cables.Cable(
                    resistance=resistance,
                    inductance=1.31e-7,
                    conductance=1e-4,
                    capacitance=67e-12,
                    length=1000,
                )
                #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
                tf = createTransferFunction(Zr, frequency_Hz, cable_vertual)
                tfs.append(tf)
            axes[i].plot(
                frequencies_Hz,
                list(map(util.convertGain2dB, tfs)),
            )
            conductance = cables.cable_5c2v["conductance"]
            axes[i].set_title(f"R = {resistance}, G = {conductance}")
            axes[i].set_xlabel("frequency [Hz]")
            axes[i].set_ylabel("Gain [dB]")
            axes[i].set_xscale("log")
    elif mode == "g":
        # それぞれのGについてグラフを描画する
        fig, axes = plt.subplots(1, len(conductances))
        for i, conductance in enumerate(conductances):
            tfs = []
            for frequency_Hz in tqdm(frequencies_Hz):
                cable_vertual = cables.Cable(
                    resistance=1e-6,
                    inductance=1.31e-7,
                    conductance=conductance,
                    capacitance=67e-12,
                    length=1000,
                )
                #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
                tf = createTransferFunction(Zr, frequency_Hz, cable_vertual)
                tfs.append(tf)
            axes[i].plot(
                frequencies_Hz,
                list(map(util.convertGain2dB, tfs)),
            )
            resistance = cables.cable_5c2v["resistance"]
            axes[i].set_title(f"R = {resistance}, G = {conductance}")
            axes[i].set_xlabel("frequency [Hz]")
            axes[i].set_ylabel("Gain [dB]")
            axes[i].set_xscale("log")
    else:
        raise ValueError("modeの引数に不正な値が渡された")

    plt.show()


# R = G = 0.0001だとcosh, sinhの計算にエラーは発生しない
# R = G = 1でもエラーは発生しない
# R = 0.0001, G = 1だとRuntimeWarning: overflow encountered in multiply
def drawHyperbolic(frequencies_Hz, cableInfo):
    coshs = []
    sinhs = []
    for frequency_Hz in tqdm(frequencies_Hz):
        theta = calculateTheta(frequency_Hz, cableInfo)
        try:
            cosh = cmath.cosh(theta)
        except OverflowError:
            cosh = 1e6 * 1j * 1e6
        try:
            sinh = cmath.sinh(theta)
        except OverflowError:
            sinh = 1e6 * 1j * 1e6
        coshs.append(cosh)
        sinhs.append(sinh)

    fig, axes = plt.subplots(2, 2)
    axes = axes.flatten()
    axes[0].plot(
        frequencies_Hz,
        list(map(lambda cosh: cosh.real, coshs)),
    )
    axes[0].set_xlabel("frequency [Hz]")
    axes[0].set_ylabel("cosh.real")
    axes[0].set_xscale("log")

    axes[1].plot(
        frequencies_Hz,
        list(map(lambda cosh: cosh.imag, coshs)),
    )
    axes[1].set_xlabel("frequency [Hz]")
    axes[1].set_ylabel("cosh.imag")
    axes[1].set_xscale("log")

    axes[2].plot(
        frequencies_Hz,
        list(map(lambda sinh: sinh.real, sinhs)),
    )
    axes[2].set_xlabel("frequency [Hz]")
    axes[2].set_ylabel("sinh.real")
    axes[2].set_xscale("log")

    axes[3].plot(
        frequencies_Hz,
        list(map(lambda sinh: sinh.imag, sinhs)),
    )
    axes[3].set_xlabel("frequency [Hz]")
    axes[3].set_ylabel("sinh.imag")
    axes[3].set_xscale("log")
    plt.show()


def drawImpedance(frequencies_Hz, cableInfo):
    impedances = []
    for frequency_Hz in tqdm(frequencies_Hz, leave=False):
        impedances.append(cableInfo.calcCharacteristicImpedance(frequency_Hz))

    fig, ax = plt.subplots()
    ax.plot(
        frequencies_Hz,
        list(map(lambda x: x.real, impedances)),
        color="red",
        label="real",
    )
    ax.plot(
        frequencies_Hz,
        list(map(lambda x: x.imag, impedances)),
        color="green",
        label="imag",
    )
    ax.plot(
        frequencies_Hz,
        list(map(lambda x: abs(x), impedances)),
        color="blue",
        label="absolute",
    )
    ax.set_xlabel("frequency [Hz]")
    ax.set_ylabel("impedance [Ω]")
    ax.set_xscale("log")
    ax.legend()

    plt.show()


# 受端のインピーダンス
Zr = 50

# 仮想ケーブルのインスタンスを作成
cable_vertual = cables.Cable(
    resistance=1e-6,
    inductance=1.31e-7,
    conductance=1e-4,
    capacitance=67e-12,
    length=1000,
)

cable_noLoss_vertual = cables.Cable(
    resistance=0,
    inductance=1.31e-7,
    conductance=0,
    capacitance=67e-12,
    length=1000,
)

# cosh, sinhの計算結果をグラフに描画する
frequencies_forHyperbolic_Hz = list(range(0, 10000, 10))
frequencies_forHyperbolic_Hz.extend(list(range(10000, 200 * 10 ** 6, 10000)))
# drawHyperbolic(frequencies_forHyperbolic_Hz, cable_vertual)
# drawHyperbolic(frequencies_forHyperbolic_Hz, cable_noLoss_vertual)

# ケーブルの周波数特性を描画する
frequencies_Hz = list(range(0, 10000, 10))
frequencies_Hz.extend(list(range(10000, 200 * 10 ** 6, 10000)))
drawFrequencyResponse(frequencies_Hz, cable_vertual)
# drawFrequencyResponse(frequencies_Hz, cable_noLoss_vertual)

# 複数のR, Gの組み合わせごとに周波数特性をグラフ化する
nthPwrOf10_list = [v * 10 ** (-1 * (i + 2)) for i, v in enumerate([1] * 5)]
nthPwrOf10_list2 = [v * 10 ** (-1 * (i + 3)) for i, v in enumerate([4] * 5)]
# drawFrequencyResponseBySomeConditions(nthPwrOf10_list, nthPwrOf10_list2, "both")

# 回路素子の値と周波数から求めた特性インピーダンスをグラフにする
frequencies_test_Hz = list(range(0, 10000, 10))
frequencies_test_Hz.extend(list(range(10000, 200 * 10 ** 6, 10000)))
# drawImpedance(frequencies_test_Hz, cable_vertual)
# drawImpedance(frequencies_test_Hz, cable_noLoss_vertual)
