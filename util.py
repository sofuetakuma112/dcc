import numpy as np
import math
import datetime
import random, string
import os


def convertGain2dB(tf):
    """
    伝達関数G(f)[計算済み]からdBへ変換する

    Parameters
    ----------
    tf: complex
        計算した伝達関数の値
    """
    return 20 * math.log10(abs(tf))


def calcMinimumSlope(tfs_nthPwrOf10):
    """
    リストの中から傾きが最小となる組み合わせを見つけて、その傾きを返す

    Parameters
    ----------
    tfs_nthPwrOf10: list
        10の累乗の周波数に対応した伝達関数のリスト
    """
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
    """
    imgディレクトリ配下に実行時のYYYY_MM_DDのディレクトリを作成し
    そのディレクトリ配下への相対パスを作成する

    Parameters
    ----------
    fileName: string
        保存するファイル名
    """
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, "JST")
    now = datetime.datetime.now(JST)
    today_string = now.strftime("%Y%m%d")
    year = today_string[0:4]
    month = today_string[4:6]
    day = today_string[6:8]

    todayDirectoryName = f"{year}_{month}_{day}"
    imageFileName = createRandomChars(12) if fileName == "" else fileName

    if not os.path.exists(f"img/{todayDirectoryName}"):
        # ディレクトリが存在しない場合、ディレクトリを作成する
        os.makedirs(f"img/{todayDirectoryName}")

    image_file_path = f"img/{todayDirectoryName}/{imageFileName}"
    print(image_file_path)
    return image_file_path


def createRandomChars(n):
    """
    指定された数の長さをもつランダムな文字列を作成する

    Parameters
    ----------
    n: float
        生成する文字数
    """
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return "".join(randlst)


def getNearestNumber(list, num):
    """
    listの中でnumに最も近い値を返却する関数

    Parameters
    ----------
    list : list
        データ配列
    num: float
        対象値
    """

    # リスト要素と対象値の差分を計算し最小値のインデックスを取得
    idx = np.abs(np.asarray(list) - num).argmin()
    return list[idx]


def calcAttenuationConstant(frequency, cable):
    """
    引数の周波数、ケーブル情報から減衰定数を求める

    Parameters
    ----------
    frequency : float
        周波数[Hz]
    cable: instance
        Cableインスタンス
    """
    omega = 2 * np.pi * frequency
    R = cable.resistance
    L = cable.inductance
    G = cable.conductance
    C = cable.capacitance
    return np.sqrt(
        (
            np.sqrt((R ** 2 + omega ** 2 * L ** 2) * (G ** 2 + omega ** 2 * C ** 2))
            + (R * G - omega ** 2 * L * C)
        )
        / 2
    )

def np2db(np):
    """
    ネーパをデジベルに変換する

    Parameters
    ----------
    np : float
        ネーパ(Np)
    """
    return np * (20 / math.log(10))


# matplotlibのグラフ表示に使用するオプション群
colors = [
    "tab:blue",
    "tab:orange",
    "tab:green",
    "tab:red",
    "tab:purple",
    "tab:brown",
    "tab:pink",
    "tab:gray",
    "tab:olive",
]
markers = [".", ",", "o", "v", "^", "<", ">", "1", "2"]

ONE_HUNDRED = 1000000
