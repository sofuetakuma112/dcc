import numpy as np
import matplotlib.pyplot as plt
import math


def calculateTheta(cableLength, frequency, alphas):
    """
    伝搬定数γと同軸ケーブルの長さlの積を求める

    Parameters
    ----------
    cableLength : float
        同軸ケーブルの長さ
    frequency : float
        周波数
    alphas : float
        減衰定数αの離散値のリスト
    """
    alpha = calculateAlpha(frequency, alphas)
    # 無損失の場合のみ成り立つ計算の仕方
    FRACTIONAL_SHORTENING = 0.67  # 波長短縮率（同軸ケーブルは一律で0.67）
    SPEED_OF_LIGHT = 3 * 10 ** 8  # 光速
    omega = 2 * np.pi * frequency
    beta = omega / (SPEED_OF_LIGHT * FRACTIONAL_SHORTENING)
    gamma = alpha + beta * 1j
    return gamma * cableLength


# ルート内がマイナスになる問題がある
def calculateTheta2(cableLength, C, frequency):
    """
    伝搬定数γと同軸ケーブルの長さlの積を求める

    Parameters
    ----------
    cableLength : float
        同軸ケーブルの長さ
    C : float
        静電容量(nF/km)
    frequency : float
        周波数(Hz)
    """
    R = 0
    G = 0
    # http://energychord.com/children/energy/trans/tl/contents/tl_cable_ind.html
    # を参考に値を設定
    L = 1.31 * 10 ** -7 # H/m
    C_FperM = C * 10 ** -12 # F/m
    omega = 2 * np.pi * frequency
    gamma = math.sqrt((R + omega * L * 1j) * (G + omega * C_FperM * 1j))
    print('gamma', gamma)
    return gamma * cableLength

# alpha = 0で計算すると|G(f)| = 1の期待通りのグラフが得られた
def calculateTheta3(frequency_Hz, cableLength, alphas, C):
    """
    伝搬定数γと同軸ケーブルの長さlの積を求める
    R = G = 0の無損失(https://denki-no-shinzui.com/7717/)で考える

    Parameters
    ----------
    frequency : float
        周波数(Hz)
    cableLength : float
        同軸ケーブルの長さ
    alphas : float
        減衰定数αの離散値のリスト
    """
    frequency_MHz = frequency_Hz * 10 ** -6
    alpha_km = calculateAlpha(frequency_MHz, alphas)
    alpha_m = alpha_km / 1000
    omega = 2 * np.pi * frequency_Hz
    L = 1.31 * 10 ** -7 # H/m
    C_FperM = C * 10 ** -12 # F/m
    beta = omega * math.sqrt(L * C_FperM)
    # waveLength = 0
    # try:
    #     waveLength = 2 * np.pi / beta
    # except ZeroDivisionError:
    #     print('Error', beta, frequency_Hz)
    waveLength = 2 * np.pi / beta
    gamma = alpha_m + beta * 1j
    theta = gamma * cableLength * waveLength
    return theta
    

def createFMatrixForDcc(Z0, theta):
    """
    分布定数回路のF行列を求める

    Parameters
    ----------
    Z0 : float
        同軸ケーブルの入力インピーダンス
    theta : float
        伝搬定数γと同軸ケーブルの長さlの積
    """
    return np.array(
        [
            [np.cosh(theta), Z0 * np.sinh(theta)],
            [np.sinh(theta) / Z0, np.cosh(theta)],
        ]
    )


# fからαを求める
def calculateAlpha(frequency, alphas):
    """
    周波数に対応した減衰定数を取得する

    Parameters
    ----------
    frequency : float
        周波数
    alphas : float
        減衰定数αの離散値のリスト
    """
    if frequency < 10 == True:
        coef = (alphas[1] - alphas[0]) / (10 - 1)
        intercept = alphas[0] - coef * 1
        return coef * frequency + intercept
    else:
        coef = (alphas[2] - alphas[1]) / (200 - 10)
        intercept = alphas[1] - coef * 10
        return coef * frequency + intercept


def calculateInputImpedanceByFMatrix(Zr, Z0, cableLength, frequency, alphas, C = 0):
    """
    受電端に抵抗を接続した分布定数回路の入力インピーダンスを求める
    与えられた周波数から入力インピーダンスを求める

    Parameters
    ----------
    Zr : float
        受電端のインピーダンス
    Z0 : float
        同軸ケーブルの入力インピーダンス
    cableLength : float
        同軸ケーブルのケーブル長
    frequency : float
        周波数
    alphas : float
        減衰定数αの離散値のリスト
    """
    # γlを求める
    # theta = calculateTheta(cableLength, frequency, alphas)
    theta = calculateTheta3(frequency, cableLength, alphas, C)
    # 分布定数回路のF行列
    f_matrix_dcc = createFMatrixForDcc(Z0, theta)
    # 受電端のZrのF行列
    f_matrix_Zr = np.array(
        [
            [1, 0],
            [1 / Zr, 1],
        ]
    )

    # 受信端にZrを接続した場合のf行列
    f_matrix = np.dot(f_matrix_dcc, f_matrix_Zr)

    return abs(f_matrix[0, 0] / f_matrix[1, 0])


def createTransferFunction(Zr, Z0, cableLength, frequency, alphas, C = 0):
    """
    受電端に抵抗を接続した分布定数回路の伝達関数を求める

    Parameters
    ----------
    Zr : float
        受電端のインピーダンス
    Z0 : float
        同軸ケーブルの入力インピーダンス
    cableLength : float
        同軸ケーブルのケーブル長
    frequency : float
        周波数
    alphas : float
        減衰定数αの離散値のリスト
    """
    # theta = calculateTheta(cableLength, frequency, alphas)
    theta = calculateTheta3(frequency, cableLength, alphas, C)

    R1 = 0  # 入力側の抵抗は0で考える
    R2 = Zr

    f_matrix_dcc = createFMatrixForDcc(Z0, theta)
    A = f_matrix_dcc[0][0]
    B = f_matrix_dcc[0][1]
    C = f_matrix_dcc[1][0]
    D = f_matrix_dcc[1][1]

    return 1 / (A + B / R2 + R1 * C + (R1 / R2) * D)


# 5C-2V
l2 = 5 / 4
Z02 = 75  # 同軸ケーブルのインピーダンス
C2 = 67 # (nF/km)

alpha2_1mhz = 7.6
alpha2_10mhz = 25
alpha2_200mhz = 125
alphas2 = [alpha2_1mhz, alpha2_10mhz, alpha2_200mhz]

Zr = 50  # 受端のインピーダンス


# 3D-2V
l1 = 3 / 2
Z01 = 50  # 同軸ケーブルのインピーダンス
C1 = 100 # (nF/km)

alpha1_1mhz = 13
alpha1_10mhz = 44
alpha1_200mhz = 220
alphas1 = [alpha1_1mhz, alpha1_10mhz, alpha1_200mhz]

# 単位はMHz (= 1 x 10^6 Hz)
frequencies_MHz = range(1, 201)
frequencies_Hz = range(1, 1000)
frequencies = frequencies_Hz
# frequencies = range(1, 11)

transferFunctions1 = []
# 周波数ごとに伝達関数を求める
for frequency in frequencies:
    # 5C-2V + Zrの回路の入力インピーダンスを求める
    inputImpedance2 = calculateInputImpedanceByFMatrix(Zr, Z02, l2, frequency, alphas2, C2)

    # 回路全体の伝達関数を求める
    # transferFunctions2 = createTransferFunction(Zr, Z02, l2, frequency, alphas2)
    transferFunction1 = createTransferFunction(
        inputImpedance2, Z01, l1, frequency, alphas1, C1
    )  #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする

    transferFunctions1.append(transferFunction1)

# 周波数特性
fig, ax = plt.subplots()
ax.plot(frequencies, list(map(abs, transferFunctions1)), label="Gain")
ax.set_xlabel("frequency [Hz]")
ax.set_ylabel("Gain")
plt.show()
