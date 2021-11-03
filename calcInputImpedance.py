import numpy as np

def calculateInputImpedance(Z0, Zr, cableLength):
  theta = (2 * np.pi) * cableLength # 無損失なので、β*l2 = 2π/λ * l2 がtanのθ
  return abs(Z0 * (Zr + Z0 * np.tan(theta) * 1j) / (Z0 + Zr * np.tan(theta) * 1j))

l2 = 5 / 4 # 同軸ケーブルl2の長さ
Z02 = 75 # 同軸ケーブルのインピーダンス
Zr = 50 # 受端のインピーダンス

Zin2 = calculateInputImpedance(Z02, Zr, l2)

l1 = 3 / 2
Z01 = 50

Zin1 = calculateInputImpedance(Z01, Zin2, l1)

print('Zin1', Zin1)
print('Zin2', Zin2)