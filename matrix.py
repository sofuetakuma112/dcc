import numpy as np

LAMBDA = 1 # λ

def calculateInputImpedanceByFMatrix(Z0, Zr, cableLength):
  # theta = (2 * np.pi) * cableLength # 無損失なので、β*l2 = 2π/λ * l2 がtanのθ
  alpha = 0 # 無損失
  beta = 2 * np.pi / LAMBDA
  gamma = alpha + beta * 1j
  theta = gamma * cableLength
  
  # 受信端にZrを接続した場合のf行列
  f_matrix = np.array([
    [np.cosh(theta) + Z0 * np.sinh(theta) / Zr, Z0 * np.sinh(theta)],
    [(np.sinh(theta) / Z0) + (np.cosh(theta) / Zr), np.cosh(theta)],
  ])
  
  return abs(f_matrix[0, 0] / f_matrix[1, 0])

Z02 = 75 # 同軸ケーブルのインピーダンス
Zr = 50 # 受端のインピーダンス

l2 = 5 * LAMBDA / 4
theta = (2 * np.pi) * l2 # 無損失の場合

Zin2 = calculateInputImpedanceByFMatrix(Z02, Zr, l2)

l1 = 3 / 2
Z01 = 50

Zin1 = calculateInputImpedanceByFMatrix(Z01, Zin2, l1)

print('Zin1 =', Zin1)
print('Zin2 =', Zin2)