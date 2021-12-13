import numpy as np
import matplotlib.pyplot as plt
import math
import cmath
import tqdm
import util
import cables


def createFMatrixLC(frequency_Hz, cableInfo):
    L = 1.31 * 10 ** -7 * cableInfo["length"]  # H/m * m
    C_FperM = cableInfo["capacitance"] * 10 ** -12 * cableInfo["length"]  # F/m * m
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
frequencies_Hz = list(range(0, 1000, 1))
frequencies_Hz.extend(list(range(1000, 200 * 10 ** 6, 1000)))
# resistances = [5, 50, 1000000]
resistances = [50]
times = 1


def drawFrequencyResponse(calcTransferFunction, cableInfo, outputFileName=""):
    fig, axes = plt.subplots(1, len(resistances))
    tfs_nthPwrOf10 = []

    for i, resistance in enumerate(resistances):
        tfs = []

        for frequency_Hz in tqdm.tqdm(frequencies_Hz):
            tf = calcTransferFunction(
                frequency_Hz,
                resistance,
                cableInfo,
            )
            tfs.append(tf)

            # 10の累乗の周波数ごとに伝達関数の値をリストに格納する
            if frequency_Hz > 1 and math.log10(frequency_Hz).is_integer():
                tfs_nthPwrOf10.append({"frequency_Hz": frequency_Hz, "tf": tf})

        # 伝達関数G(f)にabs関数を適用してゲインを求める
        currentAx = None
        if type(axes) is list:
            # 複数のグラフを同時に描画する場合
            currentAx = axes[i]
        else:
            # 一つのグラフを描画する場合
            currentAx = axes
        currentAx.plot(
            frequencies_Hz,
            list(map(util.convertGain2dB, tfs)),
        )
        currentAx.set_title(f"R = {resistance}")
        currentAx.set_xlabel("frequency [Hz]")
        currentAx.set_ylabel("Gain [dB]")
        currentAx.set_xscale("log")

        # ゲインの傾きを求める
        gain_ratio = abs(tfs_nthPwrOf10[-1]["tf"]) / abs(tfs_nthPwrOf10[-2]["tf"])
        print(f"{util.convertGain2dB(gain_ratio)}[dB/dec]")

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
drawFrequencyResponse(createTransferFunction, cables.cable_5c2v, "calc_by_fMatrix")
# drawFrequencyResponse(
#     createTransferFunctionByContinuousLCCircuit,
#     cable.cable_5c2v,
#     f"calc_by_{times}_consective_LC_circuits_fMatrix",
# )

# drawFParameter(cable.cable_5c2v)
