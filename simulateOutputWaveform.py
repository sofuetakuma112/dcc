import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

import matplotlibSettings as pltSettings

import numpy as np
import pandas as pd

import transferFunction as tfModules
import cable
import util


def squareWaveFftAndIfft(cable, endCondition, showMeasuredValue=False):
    input_wave_frequency = 100e3  # 100[kHz]
    timeLength = 20000
    samplingFrequency = (
        input_wave_frequency * timeLength
    )  # サンプリング周波数（1秒間に何回サンプリングするか、ナイキスト周波数は44100 / 2）
    # np.arange(0, 10, 1) => [0 1 2 3 4 5 6 7 8 9]
    times = np.arange(
        0, 1 / input_wave_frequency, 1 / samplingFrequency
    )  # 1 / samplingFrequency はサンプリング周期（何秒おきにサンプリングするか）
    if len(times) != timeLength:
        times = times[:-1]
    # 足し合わされる波は、入力波の周波数の整数倍の周波数を持つ
    # squareWaves_time = np.sign(np.sin(2 * np.pi * input_wave_frequency * times))

    # 指定したDuty比になるようリストの数値を調整する
    dutyRate = 50  # [%]
    squareWaves_time = [0] * (timeLength)
    for i in range(int(timeLength * dutyRate / 100)):
        squareWaves_time[i] = 1
    squareWaves_time[0] = 0  # 先頭の要素を0にしてパルス波の頭とケツを一致させる
    coef = 2
    squareWaves_time = [n * coef for n in squareWaves_time]

    ratio = len(
        list(filter(lambda y: True if y == 1 * coef else False, squareWaves_time))
    ) / len(squareWaves_time)
    # デューティー比は、パルス幅を周期で割り算したもの
    print(f"デューティー比: {ratio * 100}%")

    # fig, axes = plt.subplots(3, 2)
    # axes = axes.flatten()
    fig, axes = plt.subplots()
    fig, axes1 = plt.subplots()
    fig, axes2 = plt.subplots()
    fig, axes3 = plt.subplots()
    fig, axes4 = plt.subplots()
    fig, axes5 = plt.subplots()
    axes = [axes, axes1, axes2, axes3, axes4, axes5]

    FONT_SIZE = 16

    inputWaves_time = squareWaves_time
    axes[0].plot([time * 1e6 for time in times], inputWaves_time)
    # axes[0].set_title("入力波形")
    axes[0].set_ylabel("Amp[V]", fontsize=FONT_SIZE)
    axes[0].set_xlabel("Time[μs]", fontsize=FONT_SIZE)
    # axes[0].xaxis.set_major_formatter(
    #     pltSettings.FixedOrderFormatter(-6, useMathText=True)
    # )
    axes[0].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[0].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[0].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    # フーリエ変換
    # 各離散値は、それぞれlen(離散信号列)個の複素正弦波の一次結合で表される（DFT）
    # 実数をFFTする場合、
    # 負の周波数のフーリエ係数の値は、
    # 対応する正の周波数のフーリエ係数の虚数部分を打ち消すために共役な値をとる為、
    # 情報としては正の周波数部分のみで十分
    # numpy.fft.fft(
    # FFTを行う配列,
    # FFTを行うデータ点数(NoneとするとFFTを行う配列の長さに等しくなる),
    # FFTを行う配列の軸方向(指定しなければ、配列の最大次元の方向となる),
    # 使用する正規化手法("ortho"とすると正規化する。正規化すると変換値が1/√Nになる（Nはデータ点数)),
    # )
    # numpy.fft.fft()の戻り値は、長さnの複素数配列
    # inputWaves_fft = np.fft.fft(inputWaves_time)
    # 工学系の用途向けに、実数のFFTに特化した np.fft.rfft が用意されている。
    inputWaves_fft = np.fft.rfft(inputWaves_time)

    # 離散フーリエ変換のサンプル周波数を返す（rfft, irfftで使用するため）
    # np.fft.fftfreq(FFTを行うデータ点数, サンプリング周期)
    # # サンプリング周期次第で時系列データの時間軸の長さが決定する（100点, 0.01）なら100 * 0.01[s]の時系列データということになる？
    # input_wave_frequencyの整数倍の周波数のリストになる
    # DFTは長さnのリストを, 長さnの複素数リストに変換する
    frequencies = np.fft.rfftfreq(len(inputWaves_time), 1.0 / samplingFrequency)
    # print(frequencies) # [0.000e+00 1.000e+05 2.000e+05 ... 9.998e+08 9.999e+08 1.000e+09]

    axes[1].plot(
        [freq / 1e6 for freq in frequencies[:11]], np.abs(inputWaves_fft)[:11]
    )  # absで振幅を取得
    # axes[1].set_title("abs(F[input(t)])")
    axes[1].set_ylabel("Amp", fontsize=FONT_SIZE)
    # axes[1].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    axes[1].set_xlabel("Frequency[MHz]", fontsize=FONT_SIZE)
    # axes[1].xaxis.set_major_formatter(
    #     pltSettings.FixedOrderFormatter(6, useMathText=True)
    # )
    axes[1].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[1].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[1].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    tfs = tfModules.calcTfsBySomeFreqs(
        frequencies,
        endCondition,
        cable,
    )

    axes[2].plot(
        [freq / 1e6 for freq in frequencies[:11]],
        list(map(lambda tf: util.convertGain2dB(tf), tfs))[:11],
    )
    # axes[2].set_title("abs(H(f))")
    axes[2].set_ylabel("Gain[dB]", fontsize=FONT_SIZE)
    # axes[2].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    axes[2].set_xlabel("Frequency[MHz]", fontsize=FONT_SIZE)
    # axes[2].xaxis.set_major_formatter(
    #     pltSettings.FixedOrderFormatter(6, useMathText=True)
    # )
    axes[2].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[2].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[2].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    convolution = np.array(inputWaves_fft) * np.array(
        tfs
    )  # 時間軸の畳み込み積分 = フーリエ変換した値同士の積(の値も周波数軸のもの)
    # convolution = np.array(inputWaves_fft, dtype=np.complex) * np.array(
    #     list(map(lambda tf: abs(tf), tfs)), dtype=np.complex
    # )

    axes[3].plot(
        [freq / 1e6 for freq in frequencies[:11]], np.abs(convolution)[:11], label="シミュレーション"
    )  # absで振幅を取得
    # axes[3].set_title("abs(F[input(t)] * H(f))")
    axes[3].set_ylabel("Amp", fontsize=FONT_SIZE)
    # axes[3].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    axes[3].set_xlabel("Frequency[MHz]", fontsize=FONT_SIZE)
    # axes[3].xaxis.set_major_formatter(
    #     pltSettings.FixedOrderFormatter(6, useMathText=True)
    # )
    axes[3].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[3].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[3].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    ### 実測値の周波数応答
    if showMeasuredValue:
        if endCondition["impedance"] == 50:
            df = pd.read_csv("csv/singlePlus_end50ohm.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            inputWaves_fft = np.fft.rfft(values)
            frequencies = np.fft.rfftfreq(len(values), seconds[1] - seconds[0])
            axes[3].plot(
                [freq / 1e6 for freq in frequencies[:51]],
                np.abs(inputWaves_fft[:51]),
                label="実測値"
            )  # absで振幅を取得
            axes[3].legend()
        elif endCondition["impedance"] == 1e6:
            df = pd.read_csv("csv/singlePlus_endOpen.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            inputWaves_fft = np.fft.rfft(values)
            frequencies = np.fft.rfftfreq(len(values), seconds[1] - seconds[0])
            axes[3].plot(
                [freq / 1e6 for freq in frequencies[:51]],
                np.abs(inputWaves_fft[:51]),
                label="実測値"
            )  # absで振幅を取得
            axes[3].legend()
    ### 実測値の周波数応答

    # 逆フーリエ変換
    # r = np.fft.ifft(convolution, len(T))
    # 入力波形が実数データ向けの逆FFT np.fft.irfft が用意されている。
    # 33点のrfft結果を入力すれば64点の時間領域信号が得られる。
    # 入力波形が実数値のみなので、出力波形も虚数部分は捨ててよい？

    r = np.fft.irfft(convolution, len(times))

    axes[4].plot([time * 1e6 for time in times], np.real(r), zorder=2, label="シミュレーション")
    # axes[4].set_title("output(t).real")
    axes[4].set_ylabel("Amp[V]", fontsize=FONT_SIZE)
    axes[4].set_xlabel("Time[μs]", fontsize=FONT_SIZE)
    # axes[4].xaxis.set_major_formatter(
    #     pltSettings.FixedOrderFormatter(-6, useMathText=True)
    # )
    axes[4].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[4].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[4].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    ### 実測値の時間応答
    if showMeasuredValue:
        axes[4].set_xlim(-0.1, 10)
        if endCondition["impedance"] == 50:
            df = pd.read_csv("csv/singlePlus_end50ohm.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            axes[4].plot(
                [s * 1e6 + 0.1 for s in seconds],
                [value - 0.005 for value in values],
                zorder=1,
                label="実測値"
            )
            axes[4].legend()
        elif endCondition["impedance"] == 1e6:
            df = pd.read_csv("csv/singlePlus_endOpen.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            axes[4].plot(
                [s * 1e6 + 0.1 for s in seconds],
                [value - 0.01 for value in values],
                zorder=1,
                label="実測値"
            )
            axes[4].legend()
    ### 実測値の時間応答

    axes[5].plot([time * 1e6 for time in times], np.imag(r))
    # axes[5].set_title("output(t).imag")
    axes[5].set_ylabel("Amp[V]", fontsize=FONT_SIZE)
    axes[5].set_xlabel("Time[μs]", fontsize=FONT_SIZE)
    # axes[5].xaxis.set_major_formatter(
    #     pltSettings.FixedOrderFormatter(-6, useMathText=True)
    # )
    axes[5].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[5].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[5].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    plt.tight_layout()
    plt.show()


# 受電端の抵抗が0のとき、断線していない正常のケーブル？
squareWaveFftAndIfft(
    cable.cable_vertual,
    {"shouldMatching": False, "impedance": 1e6},
    # {"shouldMatching": False, "impedance": 50},
    showMeasuredValue=True,
)
