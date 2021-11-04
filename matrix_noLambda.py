import numpy as np

def calculateTheta(cableLength, alpha):
  beta = 2 * np.pi
  gamma = alpha + beta * 1j
  return gamma * cableLength

def createFMatrixForDcc(Z0, theta):
  return np.array([
    [np.cosh(theta), Z0 * np.sinh(theta)],
    [np.sinh(theta) / Z0, np.cosh(theta)],
  ])

def calculateInputImpedanceByFMatrix(Z0, Zr, cableLength, alpha=0):
  theta = calculateTheta(cableLength, alpha)
  
  # 分布定数回路のF行列
  f_matrix_dcc = createFMatrixForDcc(Z0, theta)
  
  # 受電端のZrのF行列
  f_matrix_Zr = np.array([
    [1, 0],
    [1 / Zr, 1],
  ])
  
  # 受信端にZrを接続した場合のf行列
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
  R1 = 0 # 入力側の抵抗は0で考える
  R2 = Zr
  
  theta = calculateTheta(cableLength, alpha)
  f_matrix_dcc = createFMatrixForDcc(Z0, theta)
  
  A = f_matrix_dcc[0][0]
  B = f_matrix_dcc[0][1]
  C = f_matrix_dcc[1][0]
  D = f_matrix_dcc[1][1]
  
  # 伝達関数
  return 1 / (A + B / R2 + R1 * C + (R1 / R2) * D)

def createTransferFunctionFromGivenFMatrix(f_matrix, R2, R1=0):
  A = f_matrix[0][0]
  B = f_matrix[0][1]
  C = f_matrix[1][0]
  D = f_matrix[1][1]
  
  return 1 / (A + B / R2 + R1 * C + (R1 / R2) * D)
  

# 5C-2V
l2 = 5 / 4
Z02 = 75 # 同軸ケーブルのインピーダンス
alpha2 = 7.6
Zr = 50 # 受端のインピーダンス

Zin2NoAlpha = calculateInputImpedanceByFMatrix(Z02, Zr, l2)
Zin2 = calculateInputImpedanceByFMatrix(Z02, Zr, l2, alpha2)
transferFunc2 = createTransferFunction(Z02, Zr, l2, alpha2)

# 3D-2V
l1 = 3 / 2
Z01 = 50 # 同軸ケーブルのインピーダンス
alpha1 = 13

Zin1NoAlpha = calculateInputImpedanceByFMatrix(Z01, Zin2NoAlpha, l1)
Zin1 = calculateInputImpedanceByFMatrix(Z01, Zin2, l1, alpha1)
transferFunc1 = createTransferFunction(Z01, Zin2, l1, alpha1)

print('5C-2V + Zrの入力インピーダンス（alpha無し）', Zin2NoAlpha) # 112.5
print('3D-2V + 5C-2V + Zrの入力インピーダンス（alpha無し）', Zin1NoAlpha) # 112.5

print('5C-2V + Zrの入力インピーダンス（alpha有り）', Zin2) # 75.0000001680839
print('3D-2V + 5C-2V + Zrの入力インピーダンス（alpha有り）', Zin1) # 50.0

print('transferFunc2')
print(transferFunc2) # (1.8333410714827925e-20-5.9881463843059744e-05j)
print(abs(transferFunc2), '\n') # 5.9881463843059744e-05

print('transferFunc1')
print(transferFunc1) # (-4.077921387049728e-09-1.498204012147495e-24j)
print(abs(transferFunc1), '\n') # 4.077921387049728e-09

print('transferFunc1 * transferFunc2')
print(transferFunc1 * transferFunc2) # (-1.644768570345007e-28+2.4419190209345835e-13j)
print(abs(transferFunc1 * transferFunc2), '\n') # 2.4419190209345835e-13

theta2 = calculateTheta(l2, alpha2)
f_matrix_dcc2 = createFMatrixForDcc(Z02, theta2)

theta1 = calculateTheta(l1, alpha1)
f_matrix_dcc1 = createFMatrixForDcc(Z01, theta1)

# 2本の同軸ケーブル + Zrを含めた回路全体の伝達関数を求める
fMatrixOfTwoCombinedCables = np.dot(f_matrix_dcc1, f_matrix_dcc2)
transferFunctionOfEntireCircuit = createTransferFunctionFromGivenFMatrix(fMatrixOfTwoCombinedCables, Zr, 0)

print('transferFunctionOfEntireCircuit')
print(transferFunctionOfEntireCircuit) # (-1.6447685716854143e-28+2.441919020934583e-13j)
print(abs(transferFunctionOfEntireCircuit)) # 2.441919020934583e-13
