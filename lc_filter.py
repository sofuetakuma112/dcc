import numpy as np
import matplotlib.pyplot as plt
import math
import cmath
import tqdm
import util
import cable


def createFMatrixLC(frequency_Hz, cableInfo):
    L = 1.31 * 10 ** -7  # H/m
    C_FperM = cableInfo["capacitance"] * 10 ** -12  # F/m
    omega = 2 * np.pi * frequency_Hz

    return np.array(
        [
            [1 - omega ** 2 * L * C_FperM, 1j * omega * L],
            [1j * omega * C_FperM, 1],
        ]
    )


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


def createTransferFunctionByContinuousLCCircuit(frequency_Hz, resistance, cableInfo):
    # LのF行列とCのF行列の行列積
    f_matrix_lc = createFMatrixLCByMatmul(frequency_Hz, cableInfo)

    return util.createTransferFunctionFromFMatrix(resistance, f_matrix_lc)


# 解析的に求めたLCフィルタの伝達関数の式を用いて計算する
def calcTfByEquation(frequency_Hz, resistance, cableInfo):
    # 受端のインピーダンス
    R = resistance  # (Ω)
    L = 1.31 * 10 ** -7  # H/m
    C_FperM = cableInfo["capacitance"] * 10 ** -12  # F/m

    # LCフィルタの伝達関数(https://detail-infomation.com/lc-low-pass-filter/)
    omega = 2 * np.pi * frequency_Hz

    return R / (R * (1 - (omega ** 2) * L * C_FperM) + 1j * omega * L)


# frequencies_Hz = range(0, 200 * 10 ** 6, 10000)
frequencies_Hz = range(180 * 10 ** 6, 200 * 10 ** 6, 100)
# resistances = [5, 50, 1000000]
resistances = [50]
times = 10


def drawFrequencyResponse(calcTransferFunction, cableInfo, outputFileName=""):
    fig, axes = plt.subplots(1, len(resistances))
    # axes = axes.flatten()

    for i, resistance in enumerate(resistances):
        tfs = []
        # tf_10Mhz = 0
        # tf_100Mhz = 0
        # gain_ratio = 0

        for frequency_Hz in tqdm.tqdm(frequencies_Hz):
            tf = calcTransferFunction(
                frequency_Hz,
                resistance,
                cableInfo,
            )
            tfs.append(tf)

            # ゲインの傾きを求める
            # # 周波数が10Mhzのとき
            # if frequency_Hz == 10 * 10 ** 6:
            #     tf_10Mhz = tf
            # if frequency_Hz == 100 * 10 ** 6:
            #     tf_100Mhz = tf
            #     # gain_ratio = (util.convertTf2dB(tf_100Mhz) / util.convertTf2dB(tf_10Mhz))
            #     gain_ratio = (abs(tf_100Mhz) / abs(tf_10Mhz))
            # if gain_ratio != 0:
            #     print(f"{gain_ratio}")
            #     gain_ratio = 0

        # 伝達関数G(f)にabs関数を適用してゲインを求める
        currentAx = None
        if type(axes) is list:
            currentAx = axes[i]
        else:
            currentAx = axes
        currentAx.plot(
            frequencies_Hz,
            list(map(util.convertTf2dB, tfs)),
        )
        currentAx.set_title(f"R = {resistance}")
        currentAx.set_xlabel("frequency [Hz]")
        currentAx.set_ylabel("Gain [db]")
        currentAx.set_xscale("log")

    if outputFileName != "":
        fig.savefig(f"{outputFileName}.png")
    plt.show()


def drawFParameter(cableInfo, outputFileName=""):
    resistance = 50
    f_matrix_list = []

    fig, axes = plt.subplots(1, 2)
    for frequency_Hz in tqdm.tqdm(frequencies_Hz):
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


# drawFrequencyResponse(calcTfByEquation, cable.cable_5c2v, "calc_by_tf_equation")
# drawFrequencyResponse(createTransferFunction, cable.cable_5c2v, "calc_by_fMatrix")
# drawFrequencyResponse(
#     createTransferFunctionByContinuousLCCircuit,
#     cable.cable_5c2v,
#     f"calc_by_{times}_consective_LC_circuits_fMatrix",
# )

drawFParameter(cable.cable_5c2v)
