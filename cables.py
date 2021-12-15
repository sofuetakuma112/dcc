import cmath
import numpy as np

# 5C-2V
alpha2_1mhz = 7.6
alpha2_10mhz = 25
alpha2_200mhz = 125
cable_5c2v = {
    "impedance": 75,  # 同軸ケーブルのインピーダンス
    "capacitance": 67 * 10 ** -12,  # (F/m)
    "alphas": [alpha2_1mhz, alpha2_10mhz, alpha2_200mhz],
    "length": 1000, # 1kmと仮定
    "resistance": 0.001,
    "conductance": 0.001,
}

# 3D-2V
alpha1_1mhz = 13
alpha1_10mhz = 44
alpha1_200mhz = 220
cable_3d2v = {
    "impedance": 50,  # 同軸ケーブルのインピーダンス
    "capacitance": 100,  # (nF/km)
    "alphas": [alpha1_1mhz, alpha1_10mhz, alpha1_200mhz],
    "length": 1000, # 1kmと仮定
    "resistance": 0.001,
    "conductance": 0.001,
}

# 仮想的なケーブル
cable_vertual = {
    "impedance": 0, # 適当な値で初期化
    "resistance": 0.001, # (Ω/m)
    "inductance": 1.31 * 10 ** -7,  # H/m
    "conductance": 0.001, # (S/m)
    "capacitance": 100 * 10 ** -12,  # (F/m)
    "length": 1000, # 1kmと仮定
}

class Cable:
    # ここはクラス変数を定義する場所
    the_name = "animal"  # クラス変数

    def __init__(self, resistance, inductance, conductance, capacitance, length):  # イニシャライザ
        self.resistance = resistance  # インスタンス変数
        self.inductance = inductance
        self.conductance = conductance
        self.capacitance = capacitance
        self.length = length

    # ここはメソッドを定義する場所
    def calcCharacteristicImpedance(self, frequency_Hz):  # インスタンスメソッド
        omega = 2 * np.pi * frequency_Hz
        if omega == 0:
            omega = 1e-8 # ZeroDivisionError回避
        return cmath.sqrt((self.resistance + 1j * omega * self.inductance) / (self.conductance + 1j * omega * self.capacitance))

    @classmethod
    def speak(cls, adjective):  # クラスメソッド
        print("I am a {} {}".format(adjective, cls.the_name))

    @staticmethod
    def happening(person, do):  # 静的メソッド
        print("{} is {}ing".format(person, do))