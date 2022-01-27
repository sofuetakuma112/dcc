import numpy as np
import matplotlib.pyplot as plt
import math
from tqdm import tqdm
import util
import cable

# LCフィルタのF行列を生成する
def createFMatrixLC(frequency_Hz, cableInfo):
    L = cableInfo.inductance  # H/m
    C = cableInfo.capacitance  # F/m
    omega = 2 * np.pi * frequency_Hz

    return np.array(
        [
            [1 - omega ** 2 * L * C, 1j * omega * L],
            [1j * omega * C, 1],
        ]
    )


# TODO: cableInfoのインスタンス化に対応する
def createFMatrixLCByMatmul(frequency_Hz, cableInfo):
    L = 1.31 * 10 ** -7  # H/m
    C_FperM = cableInfo["capacitance"] * 10 ** -12  # F/m
    omega = 2 * np.pi * frequency_Hz

    current_f_matrix = np.eye(2)
    f_matrix_l = np.array([[1, 1j * omega * L], [0, 1]])
    f_matrix_c = np.array([[1, 0], [1j * omega * C_FperM, 1]])

    for _ in range(times):
        current_f_matrix = np.dot(current_f_matrix, f_matrix_l)
        current_f_matrix = np.dot(current_f_matrix, f_matrix_c)

    return current_f_matrix


# LCフィルタのF行列を計算して、それを元に伝達関数を求める
def createTransferFunction(frequency_Hz, resistance, cableInfo):
    # LCフィルタのF行列
    f_matrix_lc = createFMatrixLC(frequency_Hz, cableInfo)

    return util.createTransferFunctionFromFMatrix(resistance, f_matrix_lc)


# TODO: cableInfoのインスタンス化に対応する
def createTransferFunctionByContinuousLCCircuit(frequency_Hz, resistance, cableInfo):
    # LのF行列とCのF行列の行列積
    f_matrix_lc = createFMatrixLCByMatmul(frequency_Hz, cableInfo)

    return util.createTransferFunctionFromFMatrix(resistance, f_matrix_lc)


# 解析的に求めたLCフィルタの伝達関数の式を用いて計算する
def calcTfByEquation(frequency_Hz, resistance, cableInfo):
    # 受端のインピーダンス
    Zr = resistance  # (Ω)
    L = cableInfo.inductance  # H/m
    C = cableInfo.capacitance  # F/m

    # LCフィルタの伝達関数(https://detail-infomation.com/lc-low-pass-filter/)
    omega = 2 * np.pi * frequency_Hz

    return Zr / (Zr * (1 - (omega ** 2) * L * C) + 1j * omega * L)


def drawFrequencyResponse(calcTransferFunction, cableInfo, outputFileName=""):
    fig, axes = plt.subplots(1, 2 * len(resistances))
    tfs_nthPwrOf10 = []

    for i, resistance in enumerate(resistances):
        tfs = []

        for frequency_Hz in tqdm(frequencies_Hz, leave=False):
            tf = calcTransferFunction(
                frequency_Hz,
                resistance,
                cableInfo,
            )
            tfs.append(tf)

            # 10の累乗の周波数ごとに伝達関数の値をリストに格納する
            if frequency_Hz > 1 and math.log10(frequency_Hz).is_integer():
                tfs_nthPwrOf10.append({"frequency_Hz": frequency_Hz, "tf": tf})

        slope = util.calcMinimumSlope(tfs_nthPwrOf10)
        print(f"slope: {slope}[dB/dec]")

        # 伝達関数G(f)にabs関数を適用してゲインを求める
        axes[i * 2].plot(
            frequencies_Hz,
            list(map(util.convertGain2dB, tfs)),
        )
        axes[i * 2].set_title(f"R = {resistance}")
        axes[i * 2].set_xlabel("frequency [Hz]")
        axes[i * 2].set_ylabel("Gain [dB]")
        axes[i * 2].set_xscale("log")

        # math.atan2(y, x)の戻り値は-piからpi（-180度から180度）の間
        # 第2象限、第3象限での角度も正しく取得できるので、
        # 極座標平面で考える場合はmath.atan()よりもmath.atan2()のほうが適当
        axes[i * 2 + 1].plot(
            frequencies_Hz,
            list(map(lambda tf: math.atan2(tf.imag, tf.real) * 180 / np.pi, tfs)),
        )
        axes[i * 2 + 1].set_title(f"R = {resistance}")
        axes[i * 2 + 1].set_xlabel("frequency [Hz]")
        axes[i * 2 + 1].set_ylabel("theta [degree]")
        axes[i * 2 + 1].set_xscale("log")

    if outputFileName != "":
        fig.savefig(f"{outputFileName}.png")
    plt.show()


def drawFParameter(cableInfo, outputFileName=""):
    resistance = 50
    f_matrix_list = []

    fig, axes = plt.subplots(1, 2)
    for frequency_Hz in tqdm(frequencies_Hz):
        f_matrix = createFMatrixLCByMatmul(
            frequency_Hz,
            cableInfo,
        )
        f_matrix_list.append(f_matrix)

    axes[0].plot(
        frequencies_Hz,
        list(map(lambda f_matrix: f_matrix[0][0], f_matrix_list)),
    )
    axes[0].set_title(f"R = {resistance}")
    axes[0].set_xlabel("frequency [Hz]")
    axes[0].set_ylabel("A")
    # axes[0].set_xscale("log")

    axes[1].plot(
        frequencies_Hz,
        list(map(lambda f_matrix: f_matrix[0][1].imag, f_matrix_list)),
    )
    axes[1].set_title(f"R = {resistance}")
    axes[1].set_xlabel("frequency [Hz]")
    axes[1].set_ylabel("B")
    # axes[1].set_xscale("log")

    if outputFileName != "":
        fig.savefig(f"{outputFileName}.png")
    plt.show()


cable_vertual = cable.Cable(
    resistance=0,
    inductance=1e-2,
    conductance=0,
    capacitance=1e-4,
    length=0,
)

# frequencies_Hz = range(0, 200 * 10 ** 6, 10000)
frequencies_Hz = list(range(0, 1000, 1))
frequencies_Hz.extend(list(range(1000, 2 * 10 ** 6, 1000)))
# resistances = [5, 50, 1000000]
resistances = [50]
times = 1

# drawFrequencyResponse(calcTfByEquation, cable_vertual)
drawFrequencyResponse(createTransferFunction, cable_vertual)
# drawFrequencyResponse(
#     createTransferFunctionByContinuousLCCircuit,
#     cable_vertual,
#     f"calc_by_{times}_consective_LC_circuits_fMatrix",
# )

# print(1 / (2 * np.pi * ))

# drawFParameter(cable_vertual)
