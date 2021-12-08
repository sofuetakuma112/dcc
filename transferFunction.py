import numpy as np
import matplotlib.pyplot as plt
import math
import cmath


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

    # R_ohmPerM = cableInfo["resistance"] * 1000  # Ω/m
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

    # 高周波につれて差が小さくなっている
    # 低周波から高周波まで
    # (波長の差 / 光速から求めた波長) * 100 の割合は一定(平均10％)
    SPEED_OF_LIGHT = 3 * 10 ** 8  # 光速
    waveLength = SPEED_OF_LIGHT / frequency_Hz  # λ(m)
    # waveLength2 = 2 * np.pi / gamma.imag
    # print((abs(waveLength - waveLength2) / waveLength) * 100)

    theta = gamma * cableInfo["cableLength"] * waveLength
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
    theta = calculateTheta(frequency, cableInfo)

    R1 = 0  # 入力側の抵抗は0で考える
    R2 = Zr

    f_matrix_dcc = createFMatrixForDcc(cableInfo, theta)
    A = f_matrix_dcc[0][0] # 無損失の場合、実数
    B = f_matrix_dcc[0][1] # 無損失の場合、虚数
    C = f_matrix_dcc[1][0] # 無損失の場合、虚数
    D = f_matrix_dcc[1][1] # 無損失の場合、実数

    return 1 / (A + B / R2 + R1 * C + (R1 / R2) * D)


# 5C-2V
alpha2_1mhz = 7.6
alpha2_10mhz = 25
alpha2_200mhz = 125
cable_5c2v = {
    "cableLength": 5 / 4,
    "impedance": 75,  # 同軸ケーブルのインピーダンス
    "capacitance": 67,  # (nF/km)
    "resistance": 35.9,  # (MΩ/km?)
    "alphas": [alpha2_1mhz, alpha2_10mhz, alpha2_200mhz],
}

# 3D-2V
alpha1_1mhz = 13
alpha1_10mhz = 44
alpha1_200mhz = 220
cable_3d2v = {
    "cableLength": 3 / 2,
    "impedance": 50,  # 同軸ケーブルのインピーダンス
    "capacitance": 100,  # (nF/km)
    "resistance": 33.3,  # (MΩ/km?) https://www.systemgear.jp/kantsu/3c2v.php
    "alphas": [alpha1_1mhz, alpha1_10mhz, alpha1_200mhz],
}

# 受端のインピーダンス
Zr = 50

# 単位はMHz (= 1 x 10^6 Hz)
frequencies_Hz = range(1, 200 * 10 ** 2, 1)
frequencies = frequencies_Hz

transferFunctions1 = []
transferFunctions2 = []
# 周波数ごとに伝達関数を求める
for frequency in frequencies:
    # 5C-2V + Zrの回路の入力インピーダンスを求める
    inputImpedance2 = calculateInputImpedanceByFMatrix(
        Zr,
        frequency,
        cable_5c2v,
    )

    # 回路全体の伝達関数を求める
    transferFunction2 = createTransferFunction(Zr, frequency, cable_5c2v)
    transferFunctions2.append(transferFunction2)

    #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
    transferFunction1 = createTransferFunction(inputImpedance2, frequency, cable_3d2v)
    transferFunctions1.append(transferFunction1)

# 周波数特性
# fig, ax = plt.subplots()
# ax.plot(frequencies, list(map(abs, transferFunctions1)), label="Gain")
# ax.set_xlabel("frequency [Hz]")
# ax.set_ylabel("Gain")
# plt.show()

fig, ax = plt.subplots(1, 2)
ax[0].plot(frequencies, list(map(abs, transferFunctions1)), label="Gain")
ax[0].set_xlabel("frequency [Hz]")
ax[0].set_ylabel("|H(f)|")

ax[1].plot(frequencies, list(map(abs, transferFunctions2)), label="Gain")
ax[1].set_xlabel("frequency [Hz]")
ax[1].set_ylabel("|H(f)|")
# ax[0].set_xscale('log')
# ax[0].set_yscale('log')
plt.show()
