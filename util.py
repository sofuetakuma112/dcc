import numpy as np
import matplotlib.pyplot as plt
import math
import cmath

# 与えられたF行列から伝達関数を求める
def createTransferFunctionFromFMatrix(resistance, f_matrix):
    R1 = 0  # 入力側の抵抗は0で考える
    R2 = resistance

    A = f_matrix[0][0]
    B = f_matrix[0][1]
    C = f_matrix[1][0]
    D = f_matrix[1][1]

    return 1 / (A + B / R2 + R1 * C + (R1 / R2) * D)

# 伝達関数G(f)からdBへ変換する
def convertGain2dB(tf):
    return 20 * math.log10(abs(tf))

# リストの中から傾きが最小となる組み合わせを見つけて、その傾きを返す
def calcMinimumSlope(tfs_nthPwrOf10):
    slopes = []
    nOfCombinations = len(tfs_nthPwrOf10) - 1
    index = 0
    for _ in range(nOfCombinations):
        tf_big = tfs_nthPwrOf10[index]["tf"]
        tf_small = tfs_nthPwrOf10[index + 1]["tf"]
        gain_ratio = abs(tf_small) / abs(tf_big)
        slopes.append(convertGain2dB(gain_ratio))
        index += 1
    # 傾きのリストの中から最小値を選択する
    return min(slopes)
