#!/usr/bin/env python
from control.matlab import *
from matplotlib import pyplot as plt
from scipy import arange
import numpy as np
import math

import cable


def main():
    cable_vertual = cable.Cable(
        resistance=0,
        inductance=1e-2,
        conductance=0,
        capacitance=1e-4,
        length=0,
    )

    L = cable_vertual.inductance
    C = cable_vertual.capacitance
    Zr = 50

    naturalAngularFreq = 1 / math.sqrt(L * C)  # 固有角周波数
    dampingCoef = (1 / (2 * Zr)) * math.sqrt(L / C)  # 減衰係数

    # ローパスフィルタの伝達関数
    num = [0, 0, naturalAngularFreq ** 2]  # 伝達関数の分子に掛かる係数
    den = [
        1,
        2 * dampingCoef * naturalAngularFreq,
        naturalAngularFreq ** 2,
    ]  # 伝達関数の分母に掛かる係数

    # 矩形波を生成
    times = np.linspace(0, 10, 1024)  # 時刻配列(0 ~ 10を1024分割したリスト)
    freq = 1 * 10 ** 0  # 矩形波の周波数
    amp = 1.0  # 矩形波の振幅
    u = np.sign(amp * np.sin(2 * np.pi * freq * times))

    # 線形システムを伝達関数形式に変換します。
    sys1 = tf(num, den)
    print(sys1)  # <class 'control.xferfcn.TransferFunction'>

    x0 = [0, 0]

    # 線形システムの出力をシミュレートする。
    # U: 各時刻での入力を表す配列
    # T: 入力の時間値
    # X0: 最初の状態(default = 0)
    # yout: システムの応答
    # T1a: 出力の時間値
    # xout: 状態ベクトルの時間発展?
    (yout, T1a, xout) = lsim(sys1, U=u, T=times, X0=x0)

    fig, axes = plt.subplots(1, 2)
    axes[0].plot(T1a, u, label="$X_2$")  # 入力波形(矩形波)
    axes[0].set_title('input')
    axes[0].axhline(0, color="b", linestyle="--")
    axes[0].set_xlabel('time[s]')
    # plt.plot(T1a, x1a[:,1], label="$X_1$")
    # plt.plot(T1a, x1a[:,0], label="$X_2$")
    axes[1].plot(T1a, yout, label="Output")  # 出力波形
    axes[1].set_title('output')
    axes[1].axhline(0, color="b", linestyle="--")
    axes[1].set_xlabel('time[s]')
    plt.show()


if __name__ == "__main__":
    main()
