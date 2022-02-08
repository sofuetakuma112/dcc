import numpy as np
from tqdm import tqdm


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
    gamma = calcGamma(frequency_Hz, cable)
    theta = gamma * cable.length

    return theta


def calcGamma(frequency_Hz, cable):
    """
    伝搬定数γを求める

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

    gamma = np.sqrt((R + 1j * omega * L) * (G + 1j * omega * C))

    return gamma


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

    cosh = np.cosh(theta)
    sinh = np.sinh(theta)
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

    # F行列と受電端のインピーダンスから伝達関数を計算する
    return createTransferFunctionFromFMatrix(endImpedance, f_matrix_dcc)


def createTransferFunctionFromFMatrix(resistance, f_matrix):
    """
    与えられたF行列と受電端の抵抗値から伝達関数を求める

    Parameters
    ----------
    resistance : float
        受電端のインピーダンス
    f_matrix: ndarray
        F行列
    """
    R1 = 50
    R2 = resistance

    A = f_matrix[0][0]
    B = f_matrix[0][1]
    C = f_matrix[1][0]
    D = f_matrix[1][1]

    # R1 = 0 の場合、1 / (A + B / R2)
    return 1 / (A + B / R2 + R1 * C + (R1 / R2) * D)


def calcTfsBySomeFreqs(frequencies_Hz, endCondition, cable):
    tfs = []
    for frequency_Hz in tqdm(frequencies_Hz, leave=False):
        tf = createTransferFunction(frequency_Hz, endCondition, cable)
        tfs.append(tf)
    return tfs


def calcImpedanceAsSeenFromTransmissionEnd(frequency_Hz, cable, endCondition):
    Z0 = cable.calcCharacteristicImpedance(frequency_Hz)
    Zr = endCondition["impedance"]
    tanh = np.tanh(calculateTheta(frequency_Hz, cable))

    return Z0 * (Zr + Z0 * tanh) / (Z0 + Zr * tanh)
