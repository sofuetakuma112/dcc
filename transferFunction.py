import numpy as np
import matplotlib.pyplot as plt
import math
import cmath
import tqdm
import cables
import util


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

    R_ohmPerM = 0
    L = 1.31 * 10 ** -7  # H/m
    C_FperM = cableInfo["capacitance"] * 10 ** -12  # F/m
    G = 0

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
    return np.array(
        [
            [cmath.cosh(theta), cableInfo["impedance"] * cmath.sinh(theta)],
            [cmath.sinh(theta) / cableInfo["impedance"], cmath.cosh(theta)],
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


# 受端のインピーダンス
Zr = 50

# 単位はMHz (= 1 x 10^6 Hz)
frequencies_Hz = range(0, 200 * 10 ** 6, 100)

transferFunctions1 = []
transferFunctions2 = []
# 周波数ごとに伝達関数を求める
for frequency in tqdm.tqdm(frequencies_Hz):
    # 5C-2V + Zrの回路の入力インピーダンスを求める
    inputImpedance2 = calculateInputImpedanceByFMatrix(
        Zr,
        frequency,
        cables.cable_5c2v,
    )

    # 回路全体の伝達関数を求める
    transferFunction1 = createTransferFunction(
        inputImpedance2, frequency, cables.cable_3d2v
    )
    transferFunctions1.append(transferFunction1)

    #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
    transferFunction2 = createTransferFunction(Zr, frequency, cables.cable_5c2v)
    transferFunctions2.append(transferFunction2)

fig, ax = plt.subplots()
ax.plot(
    frequencies_Hz,
    list(map(util.convertTf2dB, transferFunctions2)),
)
ax.set_xlabel("frequency [Hz]")
ax.set_ylabel("Gain [db]")
ax.set_xscale("log")

fig.savefig(f"dcc_frequency_response_from_fMatrix.png")
plt.show()
