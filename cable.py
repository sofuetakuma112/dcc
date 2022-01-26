import cmath
import numpy as np


class Cable:
    def __init__(
        self, resistance, inductance, conductance, capacitance, length
    ):  # イニシャライザ
        self.resistance = resistance
        self.inductance = inductance
        self.conductance = conductance
        self.capacitance = capacitance
        self.length = length

    def calcCharacteristicImpedance(self, frequency_Hz):
        omega = 2 * np.pi * frequency_Hz
        if omega == 0:
            omega = 1e-8  # ZeroDivisionError回避
        return cmath.sqrt(
            (self.resistance + 1j * omega * self.inductance)
            / (self.conductance + 1j * omega * self.capacitance)
        )


# 損失有りのケーブル
# RG58A/U
cable_vertual = Cable(
    resistance=1e-8,
    inductance=3.21e-17 / 9.77e-11, # LC / CでLを求めている(LCは[1/(4 * l * np.sqrt(LC))]から求めた)
    conductance=1e-2,
    capacitance=9.77e-11,
    length=6,
)

# 5D-2W
# cable_vertual = Cable(
#     resistance=1e-7,
#     inductance=2.6e-9,
#     conductance=1e-4,
#     capacitance=7.7e-13,
#     length=10,
# )
# cable_vertual = Cable(
#     resistance=1e-8,
#     inductance=3e-9,
#     conductance=1e-4,
#     capacitance=1e-12,
#     length=300,
# )

# 無損失ケーブル
# 特性インピーダンスの計算結果が50[Ω]になるように意図的に値を設定
cable_noLoss_vertual = Cable(
    resistance=0,
    inductance=100e-12 * 50 ** 2,  # C * Zo ** 2 から求めた
    conductance=0,
    capacitance=100e-12,
    length=1000,
)

# データシートの値をpythonのデータ構造で表現したもの
# alphas: 1MHz, 10MHz, 200MHzにおける減衰定数[dB/km]のリスト
# name: ケーブルの名称
exist_cables = [
    {"alphas": [27, 82, 390], "name": "1.5C-2V"},
    {"alphas": [12, 40, 195], "name": "3C-2V"},
    {"alphas": [7.6, 25, 125], "name": "5C-2V"},
    {"alphas": [27, 85, 420], "name": "1.5D-2V"},
    {"alphas": [13, 44, 220], "name": "3D-2V"},
    {"alphas": [7.3, 26, 125], "name": "5D-2V(5D-2W)"},
    {"alphas": [4.8, 17, 85], "name": "8D-2V"},
    {"alphas": [13, 42, 200], "name": "RG58/U"},
    {"alphas": [14, 48, 230], "name": "RG58A/U"},
]
