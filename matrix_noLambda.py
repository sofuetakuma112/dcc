import numpy as np

def calculateTheta(cableLength, alpha):
  beta = 2 * np.pi
  gamma = alpha + beta * 1j
  return gamma * cableLength

def createFMaxrixForDcc(Z0, theta):
  return np.array([
    [np.cosh(theta), Z0 * np.sinh(theta)],
    [np.sinh(theta) / Z0, np.cosh(theta)],
  ])

def calculateInputImpedanceByFMatrix(Z0, Zr, cableLength, alpha=0):
  theta = calculateTheta(cableLength, alpha)
  
  # 分布定数回路のF行列
  f_matrix_dcc = createFMaxrixForDcc(Z0, theta)
  
  # 受電端のZrのF行列
  f_matrix_Zr = np.array([
    [1, 0],
    [1 / Zr, 1],
  ])
  
  # 縦続行列
  f_matrix = np.dot(f_matrix_dcc, f_matrix_Zr)
  
  # 受信端にZrを接続した場合のf行列
  # f_matrix = np.array([
  #   [np.cosh(theta) + Z0 * np.sinh(theta) / Zr,
  #    Z0 * np.sinh(theta)],
  #   [(np.sinh(theta) / Z0) + (np.cosh(theta) / Zr),
  #    np.cosh(theta)],
  # ])
  
  return abs(f_matrix[0, 0] / f_matrix[1, 0])

def createTransferFunction(Z0, Zr, cableLength, alpha=0):
  theta = calculateTheta(cableLength, alpha)
  
  f_matrix_dcc = createFMaxrixForDcc(Z0, theta)
  
  # 伝達関数
  R1 = 0 # 入力側の抵抗は0で考える
  return 1 / (f_matrix_dcc[0][0] + f_matrix_dcc[0][1] / Zr + R1 * f_matrix_dcc[1][0] + R1 / Zr * f_matrix_dcc[1][1])
  
Z02 = 75 # 同軸ケーブルのインピーダンス
Zr = 50 # 受端のインピーダンス

l2 = 5 / 4

Zin2 = calculateInputImpedanceByFMatrix(Z02, Zr, l2)
transferFunc2 = createTransferFunction(Z02, Zr, l2)

l1 = 3 / 2
Z01 = 50 # 同軸ケーブルのインピーダンス

Zin1 = calculateInputImpedanceByFMatrix(Z01, Zin2, l1)
transferFunc1 = createTransferFunction(Z01, Zin2, l1)

print('Zin1 =', Zin1) # Zin1 = 112.5
print('Zin2 =', Zin2) # Zin2 = 112.5