import cmath
import numpy as np

class Cable:
    def __init__(self, resistance, inductance, conductance, capacitance, length):  # イニシャライザ
        self.resistance = resistance
        self.inductance = inductance
        self.conductance = conductance
        self.capacitance = capacitance
        self.length = length

    # 線路の特性インピーダンスを求める
    def calcCharacteristicImpedance(self, frequency_Hz):
        omega = 2 * np.pi * frequency_Hz
        if omega == 0:
            omega = 1e-8 # ZeroDivisionError回避
        return cmath.sqrt((self.resistance + 1j * omega * self.inductance) / (self.conductance + 1j * omega * self.capacitance))