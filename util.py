import numpy as np
import math


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


def calcAttenuationConstant(frequency, cable):
    """
    引数の周波数、ケーブル情報から減衰定数[Np/m]を求める

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


def calcPhaseConstant(frequency, cable):
    """
    引数の周波数、ケーブル情報から位相定数[rad/m]を求める

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
            - (R * G - omega ** 2 * L * C)
        )
        / 2
    )


def calcConductanceFromAttenuationConstant(frequency, cable, alpha_db):
    # dB/m => Np/mに変換する
    alpha_np = db2np(alpha_db)
    L = cable.inductance
    C = cable.capacitance
    omega = 2 * np.pi * frequency
    return np.sqrt(
        ((2 * alpha_np ** 2 + omega ** 2 * L * C) / (omega * L)) ** 2
        - omega ** 2 * C ** 2
    )


def np2db(np):
    """
    ネーパをデジベルに変換する

    Parameters
    ----------
    np : float
        ネーパ(Np)
    """
    return np * (20 / math.log(10))  # Np/mを約8.68倍している


def db2np(db):
    """
    デジベルをネーパに変換する

    Parameters
    ----------
    np : float
        ネーパ(Np)
    """
    return db * (math.log(10) / 20)


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


ONE_THUOSAND = 1000
ONE_HUNDRED = 1000000
