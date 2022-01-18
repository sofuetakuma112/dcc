import numpy as np
import matplotlib.pyplot as plt
import math
import cmath
import datetime
import random, string
import os

# 与えられたF行列から伝達関数を求める
def createTransferFunctionFromFMatrix(resistance, f_matrix):
    R1 = 0  # 入力側の抵抗は0で考える
    R2 = resistance

    A = f_matrix[0][0]
    B = f_matrix[0][1]
    C = f_matrix[1][0]
    D = f_matrix[1][1]

    # R1 = 0 の場合、1 / (A + B / R2)
    result = 1 / (A + B / R2 + R1 * C + (R1 / R2) * D)

    return result


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


def createImagePath(fileName=""):
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, "JST")
    now = datetime.datetime.now(JST)
    today_string = now.strftime("%Y%m%d")
    year = today_string[0:4]
    month = today_string[4:6]
    day = today_string[6:8]

    todayDirectoryName = f"{year}_{month}_{day}"
    imageFileName = randomname(12) if fileName == "" else fileName

    if not os.path.exists(f"img/{todayDirectoryName}"):
        # ディレクトリが存在しない場合、ディレクトリを作成する
        os.makedirs(f"img/{todayDirectoryName}")

    image_file_path = f"img/{todayDirectoryName}/{imageFileName}"
    print(image_file_path)
    return image_file_path


def randomname(n):
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return "".join(randlst)


def getNearestValue(list, num):
    """
    概要: リストからある値に最も近い値を返却する関数
    @param list: データ配列
    @param num: 対象値
    @return 対象値に最も近い値
    """

    # リスト要素と対象値の差分を計算し最小値のインデックスを取得
    idx = np.abs(np.asarray(list) - num).argmin()
    return list[idx]
