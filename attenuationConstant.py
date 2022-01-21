import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt
import matplotlibSettings as pltSettings


from tqdm import tqdm

import cable as cableModules
import util


def drawAttenuationConstant(
    frequencies_Hz, cable, ax=plt.subplots()[1], shouldShowOneGlaph=True
):
    # 周波数ごとにalphaを求める
    alphas_db = []
    for frequency_Hz in tqdm(frequencies_Hz, leave=False):
        #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
        alpha_np = util.calcAttenuationConstant(frequency_Hz, cable)  # Np/m
        alpha_db = util.np2db(alpha_np)  # dB/m
        alphas_db.append(alpha_db)
    # 縦軸alpha, 横軸周波数でプロットする(alphaの値を1000倍して単位をdb/kmにしてプロットする？)
    FONT_SIZE = 12
    ax.plot(
        frequencies_Hz,
        list(map(lambda x: x * 1000, alphas_db)),
        label="vertual cable",
        zorder=5,
    )  # absで振幅を取得
    ax.set_title("周波数ごとの減衰定数の推移")
    ax.set_ylabel("α [dB/km]", fontsize=FONT_SIZE)
    ax.set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    for (exist_cable, color, marker) in zip(
        cableModules.exist_cables, pltSettings.colors, pltSettings.markers
    ):
        ax.plot(
            [1e6, 10e6, 200e6],  # 1MHz, 10MHz, 200MHz
            exist_cable["alphas"],
            marker=marker,
            color=color,
            # linestyle="",
            label=exist_cable["name"],
        )
        ax.legend()

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


# drawAttenuationConstant(list(range(0, 220 * util.ONE_HUNDRED, 10000)), cableModules.cable_vertual)
drawAttenuationConstantByDistance(cableModules.cable_vertual)
