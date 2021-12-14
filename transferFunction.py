import numpy as np
import matplotlib.pyplot as plt
import math
import cmath
import tqdm
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

    R_ohmPerM = 0.001  # Ω/m
    L = 1.31 * 10 ** -7  # H/m
    C_FperM = cableInfo["capacitance"] * 10 ** -12  # F/m
    G = 0.001 # S/m 回路における電流の流れやすさ

    # cmathを使わないとエラーが返ってくる
    # R=G=0で以下の式を計算しているのならば
    # alpha = 0
    # beta = omega * math.sqrt(L * C_FperM)
    # で、gamma = alpha + beta * 1j
    # で計算した値とほぼ一致している
    gamma = cmath.sqrt((R_ohmPerM + omega * L * 1j) * (G + omega * C_FperM * 1j))
    theta = gamma * cableInfo["length"]

    return theta


def createFMatrixForDcc(cableInfo, theta):
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
            [cosh, cableInfo["impedance"] * sinh],
            [sinh / cableInfo["impedance"], cosh],
        ]
    )


def calculateInputImpedanceByFMatrix(Zr, frequency, cableInfo):
    """
    受電端に抵抗を接続した分布定数回路の入力インピーダンスを求める
    与えられた周波数から入力インピーダンスを求める

    Parameters
    ----------
    Zr : float
        受電端のインピーダンス
    frequency : float
        周波数
    cableInfo : dictionary
        ケーブルの仕様
    """
    # γlを求める
    theta = calculateTheta(frequency, cableInfo)
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

    # return abs(f_matrix[0, 0] / f_matrix[1, 0])
    return f_matrix[0, 0] / f_matrix[1, 0]


def createTransferFunction(Zr, frequency, cableInfo):
    """
    受電端に抵抗を接続した分布定数回路の伝達関数を求める

    Parameters
    ----------
    Zr : float
        受電端のインピーダンス
    frequency : float
        周波数
    cableInfo : dictionary
        ケーブルの仕様
    """

    f_matrix_dcc = createFMatrixForDcc(cableInfo, calculateTheta(frequency, cableInfo))

    return util.createTransferFunctionFromFMatrix(Zr, f_matrix_dcc)
    # try:
    #     return util.createTransferFunctionFromFMatrix(Zr, f_matrix_dcc)
    # except:
    #     print(f_matrix_dcc[0][0], f_matrix_dcc[0][1])
    #     return 1


def drawFrequencyResponse(fileName=""):
    transferFunctions1 = []
    transferFunctions2 = []
    tfs_nthPwrOf10 = []
    # 周波数ごとに伝達関数を求める
    for frequency_Hz in tqdm.tqdm(frequencies_Hz):
        # 5C-2V + Zrの回路の入力インピーダンスを求める
        inputImpedance2 = calculateInputImpedanceByFMatrix(
            Zr,
            frequency_Hz,
            cables.cable_5c2v,
        )

        # 回路全体の伝達関数を求める
        transferFunction1 = createTransferFunction(
            inputImpedance2, frequency_Hz, cables.cable_3d2v
        )
        transferFunctions1.append(transferFunction1)

        #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
        transferFunction2 = createTransferFunction(Zr, frequency_Hz, cables.cable_5c2v)
        transferFunctions2.append(transferFunction2)

        if frequency_Hz > 1 and math.log10(frequency_Hz).is_integer():
            tfs_nthPwrOf10.append(
                {"frequency_Hz": frequency_Hz, "tf": transferFunction2}
            )

    # ゲインの傾きを求める
    tf_big = list(
        filter(lambda dict: dict["frequency_Hz"] == 1 * 10 ** 5, tfs_nthPwrOf10)
    )[0]["tf"]
    tf_small = list(
        filter(lambda dict: dict["frequency_Hz"] == 1 * 10 ** 6, tfs_nthPwrOf10)
    )[0]["tf"]
    gain_ratio = abs(tf_small) / abs(tf_big)
    print(f"{util.convertGain2dB(gain_ratio)}[dB/dec]")

    fig, axes = plt.subplots(1, 2)
    axes[0].plot(
        frequencies_Hz,
        list(map(util.convertGain2dB, transferFunctions2)),
    )
    axes[0].set_title("5C2V + Zr")
    axes[0].set_xlabel("frequency [Hz]")
    axes[0].set_ylabel("Gain [dB]")
    axes[0].set_xscale("log")

    axes[1].plot(
        frequencies_Hz,
        list(map(util.convertGain2dB, transferFunctions1)),
    )
    axes[1].set_title("2cables + Zr")
    axes[1].set_xlabel("frequency [Hz]")
    axes[1].set_ylabel("Gain [dB]")
    axes[1].set_xscale("log")

    if fileName != "":
        fig.savefig(f"{fileName}")
    plt.show()


# R = G = 0.0001だとcosh, sinhの計算にエラーは発生しない
# R = G = 1でもエラーは発生しない
# R = 0.0001, G = 1だとRuntimeWarning: overflow encountered in multiply
def drawHyperbolic(cableInfo):
    coshs = []
    sinhs = []
    for frequency_Hz in tqdm.tqdm(frequencies_Hz):
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
    axes[1].plot(
        frequencies_Hz,
        list(map(lambda cosh: cosh.imag, coshs)),
    )
    axes[1].set_xlabel("frequency [Hz]")
    axes[1].set_ylabel("cosh.imag")
    axes[2].plot(
        frequencies_Hz,
        list(map(lambda sinh: sinh.real, sinhs)),
    )
    axes[2].set_xlabel("frequency [Hz]")
    axes[2].set_ylabel("sinh.real")
    axes[3].plot(
        frequencies_Hz,
        list(map(lambda sinh: sinh.imag, sinhs)),
    )
    axes[3].set_xlabel("frequency [Hz]")
    axes[3].set_ylabel("sinh.imag")
    plt.show()


# 受端のインピーダンス
Zr = 50

# 単位はMHz (= 1 x 10^6 Hz)
frequencies_Hz = list(range(0, 1000, 1))
frequencies_Hz.extend(list(range(1000, 200 * 10 ** 5, 1000)))
# frequencies_Hz = range(0, 200 * 10 ** 6, 1000)

# drawHyperbolic(cables.cable_5c2v)
drawFrequencyResponse()
# drawFrequencyResponse("dcc_frequency_response_from_fMatrix.png")
