# try:
#     cosh = cmath.cosh(theta)
# except OverflowError:
#     cosh = 1e6 * 1j * 1e6
# try:
#     sinh = cmath.sinh(theta)
# except OverflowError:
#     sinh = 1e6 * 1j * 1e6

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
    # SPEED_OF_LIGHT = 3 * 10 ** 8  # 光速
    # waveLength = SPEED_OF_LIGHT / frequency_Hz  # λ(m)

    # ケーブル長を1kmと仮定
    cableLength = 1000

    # theta = gamma * cableInfo["cableLength"] * waveLength
    theta = gamma * cableLength
    return theta


def calculateWaveLengthDiff(frequency_Hz, cableInfo):
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
    # (波長の差 / 光速から求めた波長) * 100 の割合は一定(平均12％)
    SPEED_OF_LIGHT = 3 * 10 ** 8  # 光速
    waveLength1 = SPEED_OF_LIGHT / frequency_Hz  # λ(m)
    waveLength2 = 2 * np.pi / gamma.imag

    diff = waveLength1 - waveLength2
    return abs(diff) * 100 / waveLength1


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


# TODO: cableのインスタンス版に対応する
def calculateInputImpedanceByFMatrix(Zr, frequency_Hz, cable):
    """
    受電端に抵抗を接続した分布定数回路の入力インピーダンスを求める
    与えられた周波数から入力インピーダンスを求める

    Parameters
    ----------
    Zr : float
        受電端のインピーダンス
    frequency_Hz : float
        周波数
    cable : instance
        Cableクラスのインスタンス
    """
    # γlを求める
    theta = calculateTheta(frequency_Hz, cable)

    # 分布定数回路のF行列
    f_matrix_dcc = createFMatrixForDcc(cable, theta)
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


def drawFrequencyResponse(frequencies_Hz, cable, fileName=""):
    # transferFunctions1 = []
    transferFunctions2 = []
    tfs_nthPwrOf10 = []
    # 周波数ごとに伝達関数を求める
    for frequency_Hz in tqdm(frequencies_Hz, leave=False):
        # 5C-2V + Zrの回路の入力インピーダンスを求める
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
        transferFunction2 = createTransferFunction(Zr, frequency_Hz, cable)
        transferFunctions2.append(transferFunction2)

        if frequency_Hz > 1 and math.log10(frequency_Hz).is_integer():
            tfs_nthPwrOf10.append(
                {"frequency_Hz": frequency_Hz, "tf": transferFunction2}
            )

    # ゲインの傾きを求める
    slope = util.calcMinimumSlope(tfs_nthPwrOf10)
    print(f"slope: {slope}[dB/dec]")

    # fig, axes = plt.subplots(1, 2)
    # axes[0].plot(
    #     frequencies_Hz,
    #     list(map(util.convertGain2dB, transferFunctions2)),
    # )
    # axes[0].set_title("vertual cable + Zr")
    # axes[0].set_xlabel("frequency [Hz]")
    # axes[0].set_ylabel("Gain [dB]")
    # axes[0].set_xscale("log")

    # axes[1].plot(
    #     frequencies_Hz,
    #     list(map(lambda tf: math.atan(tf.imag / tf.real), transferFunctions2)),
    # )
    # axes[1].set_title("vertual cable + Zr")
    # axes[1].set_xlabel("frequency [Hz]")
    # axes[1].set_ylabel("theta [rad]")
    # axes[1].set_xscale("log")

    fig, ax = plt.subplots()
    ax.plot(
        frequencies_Hz,
        list(map(util.convertGain2dB, transferFunctions2)),
    )
    ax.set_title("vertual cable + Zr")
    ax.set_xlabel("frequency [Hz]")
    ax.set_ylabel("Gain [dB]")
    ax.set_xscale("log")
    ax.set_yticks([-20, 0, 10])

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

# 軽量版
def drawFrequencyResponseBySomeConditions(resistances, conductances, mode="r"):
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
                tf = createTransferFunction(frequency_Hz, False, cable_vertual)
                tfs.append(tf)

                if frequency_Hz > 1 and math.log10(frequency_Hz).is_integer():
                    tfs_nthPwrOf10.append({"frequency_Hz": frequency_Hz, "tf": tf})

            # 周波数特性の傾きを求める
            slope = util.calcMinimumSlope(tfs_nthPwrOf10)
            # 傾きのリストの中から最小値を選択する
            logs.append(f"R = {resistance}, G = {conductance}, slope: {slope}[dB/dec]")

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
            axes[i][j].tick_params(labelbottom=False, labelright=False, labeltop=False)
            axes[i][j].set_xscale("log")
    for log in logs:
        print(log)

    plt.show()


# R = G = 0.0001だとcosh, sinhの計算にエラーは発生しない
# R = G = 1でもエラーは発生しない
# R = 0.0001, G = 1だとRuntimeWarning: overflow encountered in multiply
def drawHyperbolic(frequencies_Hz, cable):
    coshs = []
    sinhs = []
    for frequency_Hz in tqdm(frequencies_Hz):
        theta = calculateTheta(frequency_Hz, cable)
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


def drawImpedance(frequencies_Hz, cable):
    impedances = []
    for frequency_Hz in tqdm(frequencies_Hz, leave=False):
        impedances.append(cable.calcCharacteristicImpedance(frequency_Hz))

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


# cosh, sinhの計算結果をグラフに描画する
frequencies_forHyperbolic_Hz = list(range(0, 10000, 10))
frequencies_forHyperbolic_Hz.extend(list(range(10000, 200 * 10 ** 6, 10000)))
# drawHyperbolic(frequencies_forHyperbolic_Hz, cable_vertual)
# drawHyperbolic(frequencies_forHyperbolic_Hz, cable_noLoss_vertual)

# 複数のR, Gの組み合わせごとに周波数特性をグラフ化する
nthPwrOf10_list = [v * 10 ** (-1 * (i + 2)) for i, v in enumerate([1] * 5)]
nthPwrOf10_list2 = [v * 10 ** (-1 * (i + 3)) for i, v in enumerate([4] * 5)]
# drawFrequencyResponseBySomeConditions(nthPwrOf10_list, nthPwrOf10_list2, "both")

# 回路素子の値と周波数から求めた特性インピーダンスをグラフにする
frequencies_test_Hz = list(range(0, 10000, 10))
frequencies_test_Hz.extend(list(range(10000, 200 * 10 ** 6, 10000)))
# drawImpedance(frequencies_test_Hz, cable_vertual)
# drawImpedance(frequencies_test_Hz, cable_noLoss_vertual)
