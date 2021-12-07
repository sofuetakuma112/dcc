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
    L = 1.31 * 10 ** -7  # H/m
    C_FperM = C * 10 ** -12  # F/m
    omega = 2 * np.pi * frequency
    gamma = math.sqrt((R + omega * L * 1j) * (G + omega * C_FperM * 1j))
    print("gamma", gamma)
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
    # frequency_MHz = frequency_Hz * 10 ** -6
    # alpha_m = calculateAlphaFromHz(frequency_MHz, alphas)
    alpha_m = 0
    omega = 2 * np.pi * frequency_Hz
    L = 1.31 * 10 ** -7  # H/m
    C_FperM = C * 10 ** -12  # F/m
    beta = omega * math.sqrt(L * C_FperM)
    waveLength = 2 * np.pi / beta
    gamma = alpha_m + beta * 1j
    theta = gamma * cableLength * waveLength
    return theta


def calculateTheta4(frequency_Hz, cableLength, alphas, C):
    """
    伝搬定数γと同軸ケーブルの長さlの積を求める
    R = G = 0の無損失(https://denki-no-shinzui.com/7717/)で考える

    Parameters
    ----------
    frequency_Hz : float
        周波数(Hz)
    cableLength : float
        同軸ケーブルの長さ
    alphas : float
        減衰定数αの離散値のリスト
    C : float
        静電容量(nF/km)
    """
    # alphaはシートから求める
    frequency_MHz = frequency_Hz * 10 ** -6
    alpha_m = calculateAlphaFromHz(frequency_MHz, alphas)
    omega = 2 * np.pi * frequency_Hz
    L = 1.31 * 10 ** -7  # H/m
    C_FperM = C * 10 ** -12  # F/m
    beta = math.sqrt(
        (
            math.sqrt((omega ** 2 * L ** 2) * (omega ** 2 * C_FperM ** 2))
            - (-1 * omega ** 2 * L * C_FperM)
        )
        / 2
    )
    waveLength = 2 * np.pi / beta
    gamma = alpha_m + beta * 1j
    theta = gamma * cableLength * waveLength
    print("waveLength", waveLength)
    print("gamma", gamma)
    print("theta", theta)
    return theta


def calculateTheta(impedance, cableLength, frequency, alphas, capacity):
    """
    伝搬定数γと同軸ケーブルの長さlの積を求める

    Parameters
    ----------
    cableLength : float
        同軸ケーブルの長さ
    alpha : float
        減衰定数α
    """
    alpha = calculateAlpha(frequency, alphas)
    # 無損失の場合のみ成り立つ計算の仕方
    # beta = 2 * np.pi * frequency * capacity * impedance
    FRACTIONAL_SHORTENING = 0.67  # 波長短縮率（同軸ケーブルは一律で0.67）
    SPEED_OF_LIGHT = 3 * 10 ** 8  # 光速
    beta = 2 * np.pi * frequency / (SPEED_OF_LIGHT * FRACTIONAL_SHORTENING)
    gamma = alpha + beta * 1j
    return gamma * cableLength


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


def calculateAlphaFromHz(frequency_hz, alphas):
    """
    周波数に対応した減衰定数を取得する

    Parameters
    ----------
    frequency_hz : float
        周波数(Hz)
    alphas : float
        減衰定数αの離散値のリスト
    """
    oneMHz_Hz = 1 * 10 ** 6
    tenMHz_Hz = 10 * oneMHz_Hz
    twoHundredMHz_Hz = 200 * oneMHz_Hz
    if frequency_hz < tenMHz_Hz == True:
        coef = (alphas[1] - alphas[0]) / (tenMHz_Hz - oneMHz_Hz)
        intercept = alphas[0] - coef * oneMHz_Hz
        return coef * frequency_hz + intercept
    else:
        coef = (alphas[2] - alphas[1]) / (twoHundredMHz_Hz - tenMHz_Hz)
        intercept = alphas[1] - coef * tenMHz_Hz
        return (coef * frequency_hz + intercept) / 1000


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
    # return np.array(
    #     [
    #         [np.cosh(theta), cableInfo["impedance"] * np.sinh(theta)],
    #         [np.sinh(theta) / cableInfo["impedance"], np.cosh(theta)],
    #     ]
    # )
    # cmath.cosh、cmath.sinhは複素数が返ってくる
    return np.array(
        [
            [cmath.cosh(theta), cableInfo["impedance"] * cmath.sinh(theta)],
            [cmath.sinh(theta) / cableInfo["impedance"], cmath.cosh(theta)],
        ]
    )


def calculateDegreesFromTransferFunction(transferFunction):
    return math.degrees(math.atan2(transferFunction.imag, transferFunction.real))


# n = 10^-6
# 67 x 10^-12(F/m)?
C2 = 67  # 静電容量(nF/km)
C1 = 100  # 静電容量(nF/km)

# def calculateGainFromTransferFunction(transferFunction):
#     return 20 * math.log10(abs(transferFunction))

# 5c-2vとZrのみの回路
# plt.plot(x, list(map(abs, transferFunctions2)), label="gain")
# plt.legend()
# plt.show()

frequencies_MHz = range(1, 201)

# 周波数特性
# frequencies_Mhz = list(map(lambda x: x / 10 ** 6, frequencies))

fig, ax = plt.subplots()
ax.plot(frequencies, list(map(abs, transferFunctions1)), label="Gain")
ax.set_xlabel("frequency [MHz]")
ax.set_ylabel("Gain [dB/km]")
# fig.savefig("frequency_characteristic.png")
plt.show()

# 減衰定数のグラフ
# fig, ax = plt.subplots()
# ax.plot([1, 10, 200], alphas1, marker="o")
# ax.set_xlabel("frequency [MHz]")
# ax.set_ylabel("Attenuation coefficient [dB/km]")
# # fig.savefig("attenuation_coefficient.png")
# plt.show()

# # 5×5サイズのFigureを作成してAxesを追加
# fig = plt.figure(figsize=(5, 5))
# ax = fig.add_subplot(111)

# # 格子点を表示
# ax.grid()

# # 軸ラベルの設定
# ax.set_xlabel("x", fontsize=16)
# ax.set_ylabel("y", fontsize=16)

# # 軸範囲の設定
# # ax.set_xlim(-3, 3)
# # ax.set_ylim(-3, 3)

# # x軸とy軸
# ax.axhline(0, color="gray")
# ax.axvline(0, color="gray")

# # ベクトルを表示
# # quiver(始点x,始点y,終点x,終点y)
# ax.quiver(0, 0, 2, 1, color="red", angles="xy", scale_units="xy", scale=1)

# # ベクトルにテキストを添える
# ax.text(2, 1, "[2, 1]", color="red", size=15)

# plt.show()

# 横軸θ? 縦軸位相
# x = np.linspace(0, 100, 1000)
# plt.plot(
#     x,
#     list(
#         map(
#             lambda complex: math.degrees(math.atan2(complex.imag, complex.real)),
#             createTransferFunction(Z01, Zin2, l1, x),
#         )
#     ),
#     label="theta",
# )
# plt.legend()
# plt.show()
