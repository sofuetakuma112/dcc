import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt
import matplotlibSettings as pltSettings

import numpy as np

from tqdm import tqdm

import cable as cableModules
import util


def drawAttenuationConstantAndCharaImpedance(
    frequencies_Hz, cable, shouldShowOneGlaph=True
):
    fig, axes = plt.subplots(2, 1)

    # 周波数ごとにalphaを求める
    alphas_db = []
    for frequency_Hz in tqdm(frequencies_Hz, leave=False):
        #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
        alpha_np = util.calcAttenuationConstant(frequency_Hz, cable)  # Np/m
        alpha_db = util.np2db(alpha_np)  # dB/m
        alphas_db.append(alpha_db)
    # 縦軸alpha, 横軸周波数でプロットする(alphaの値を1000倍して単位をdb/kmにしてプロットする？)
    FONT_SIZE = 12
    axes[0].plot(
        frequencies_Hz,
        list(map(lambda x: x * 1000, alphas_db)),
        label="vertual cable",
        zorder=5,
    )  # absで振幅を取得
    axes[0].set_title("周波数ごとの減衰定数の推移")
    axes[0].set_ylabel("α [dB/km]", fontsize=FONT_SIZE)
    axes[0].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    for (exist_cable, color, marker) in zip(
        cableModules.exist_cables, pltSettings.colors, pltSettings.markers
    ):
        axes[0].plot(
            [1e6, 10e6, 200e6],  # 1MHz, 10MHz, 200MHz
            exist_cable["alphas"],
            marker=marker,
            color=color,
            # linestyle="",
            label=exist_cable["name"],
        )
        axes[0].legend()

    characteristicImpedances = []
    for frequency_Hz in list(frequencies_Hz):
        characteristicImpedances.append(
            cableModules.cable_vertual.calcCharacteristicImpedance(frequency_Hz)
        )
    axes[1].plot(frequencies_Hz, np.abs(characteristicImpedances))

    if shouldShowOneGlaph:
        plt.tight_layout()
        plt.show()


# 横軸距離、縦軸減衰定数でグラフを描画する
def drawAttenuationConstantByDistance(cable):
    frequencies_Hz = [1e6, 10e6, 200e6]
    alphas_db = []
    for frequency_Hz in tqdm(frequencies_Hz, leave=False):
        #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
        alpha_np = util.calcAttenuationConstant(frequency_Hz, cable)  # Np/m
        alpha_db = util.np2db(alpha_np)  # dB/m
        alphas_db.append(alpha_db)

    for i, alpha_db in enumerate(alphas_db):
        fig, ax = plt.subplots()
        distances = list(range(0, 1000, 10))  # [m]
        # 求めたαをグラフに表示
        ax.plot(
            distances,
            list(map(lambda distance: distance * alpha_db, distances)),
            label="vertual cable",
            zorder=5,
            color="black",
        )
        for j, exist_cable in enumerate(cableModules.exist_cables):
            alpha_db_km = exist_cable["alphas"][i]
            ax.plot(
                distances,
                list(map(lambda distance: distance * alpha_db_km / 1000, distances)),
                color=pltSettings.colors[j],
                label=exist_cable["name"],
            )
        ax.set_title(f"{frequencies_Hz[i] / util.ONE_HUNDRED} [MHz]で求めた減衰定数を使用")
        ax.set_xlabel("distance [m]")
        ax.set_ylabel("α×distance [dB]")
        ax.legend()
    plt.tight_layout()
    plt.show()


drawAttenuationConstantAndCharaImpedance(
    list(range(0, 220 * util.ONE_HUNDRED, 10000)), cableModules.cable_vertual
)
# drawAttenuationConstantByDistance(cableModules.cable_vertual)

print(
    util.calcConductanceFromAttenuationConstant(
        util.ONE_HUNDRED, cableModules.cable_vertual, 7.3 / 1000
    )
)
print(
    util.calcConductanceFromAttenuationConstant(
        10 * util.ONE_HUNDRED, cableModules.cable_vertual, 26 / 1000
    )
)
print(
    util.calcConductanceFromAttenuationConstant(
        200 * util.ONE_HUNDRED, cableModules.cable_vertual, 125 / 1000
    )
)
