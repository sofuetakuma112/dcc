import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

import transferFunction as tfModules
import cable
import util


def squareWaveFftAndIfft(cable, endCondition, showMeasuredValue=False):
    input_wave_frequency = 100e3  # 100[kHz]
    timeLength = 10000
    samplingFrequency = (
        input_wave_frequency * timeLength
    )  # サンプリング周波数（1秒間に何回サンプリングするか、ナイキスト周波数は44100 / 2）
    # 0から10μsまで
    times = np.arange(-25e-6, 25e-6, 1 / samplingFrequency)
    # times = np.arange(
    #     -100e-6, 100e-6, 1 / samplingFrequency
    # )
    if len(times) != timeLength * 5:
        times = times[:-1]
    # 足し合わされる波は、入力波の周波数の整数倍の周波数を持つ
    # squareWaves_time = np.sign(np.sin(2 * np.pi * input_wave_frequency * times))

    # 指定したDuty比になるようリストの数値を調整する
    dutyRate = 2  # [%]
    squareWaves_time = [0] * (len(times))
    riseLength = int(
        len([time for time in times if 0 <= time and time <= 10e-6]) * dutyRate / 100
    )
    count = 0
    for i in range(len(times)):
        if 0 <= times[i] and times[i] <= 10e-6 and count < riseLength:
            squareWaves_time[i] = 1
            count += 1
    squareWaves_time[0] = 0  # 先頭の要素を0にしてパルス波の頭とケツを一致させる
    coef = 2
    squareWaves_time = [n * coef for n in squareWaves_time]

    ratio = len(
        list(filter(lambda y: True if y == 1 * coef else False, squareWaves_time))
    ) / len(
        [time for time in times if 0 <= time and time <= 10e-6]
    )  # len(squareWaves_time)
    # デューティー比は、パルス幅を周期で割り算したもの
    print(f"デューティー比: {ratio * 100}%")

    # fig, axes = plt.subplots(3, 2)
    # axes = axes.flatten()
    axes = [plt.subplots()[1] for i in range(7)]

    FONT_SIZE = 16

    xfirst = -0.1
    xlast = 0.5

    inputWaves_time = squareWaves_time
    axes[0].plot([time * 1e6 for time in times], inputWaves_time)
    axes[0].set_ylabel("Amp[V]", fontsize=FONT_SIZE)
    axes[0].set_xlabel("Time[μs]", fontsize=FONT_SIZE)
    axes[0].set_xlim(xfirst, xlast)
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
    frequencies = np.fft.rfftfreq(len(inputWaves_time), 1 / samplingFrequency)
    # print(frequencies) # [0.000e+00 1.000e+05 2.000e+05 ... 9.998e+08 9.999e+08 1.000e+09]

    axes[1].plot(
        [freq / 1e6 for freq in frequencies[:51]], np.abs(inputWaves_fft)[:51]
    )  # absで振幅を取得
    axes[1].set_ylabel("Amp", fontsize=FONT_SIZE)
    axes[1].set_xlabel("Frequency[MHz]", fontsize=FONT_SIZE)
    axes[1].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[1].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[1].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    tfs = tfModules.calcTfsBySomeFreqs(
        frequencies,
        endCondition,
        cable,
    )

    axes[2].plot(
        [freq / 1e6 for freq in frequencies[:51]],
        list(map(lambda tf: util.convertGain2dB(tf), tfs))[:51],
    )
    axes[2].set_ylabel("$H_{dB}$[dB]", fontsize=FONT_SIZE)
    axes[2].set_xlabel("Frequency[MHz]", fontsize=FONT_SIZE)
    axes[2].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[2].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[2].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    convolution_out = np.array(inputWaves_fft) * np.array(
        tfs
    )  # 時間軸の畳み込み積分 = フーリエ変換した値同士の積(の値も周波数軸のもの)

    # C1(出力電圧)
    axes[3].plot(
        [freq / 1e6 for freq in frequencies[:2501]],
        np.abs(convolution_out)[:2501],
        label="シミュレーション",
        linestyle="dashed" if showMeasuredValue else "solid",
        zorder=2,
    )  # absで振幅を取得
    axes[3].set_ylabel("|Amp|", fontsize=FONT_SIZE)
    axes[3].set_xlabel("Frequency[MHz]", fontsize=FONT_SIZE)
    axes[3].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[3].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[3].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    ### 実測値の周波数応答
    if showMeasuredValue:
        if endCondition["impedance"] == 50:
            # df = pd.read_csv("csv/c1_200ns_50ohm.csv", skiprows=11)
            df = pd.read_csv("csv/c1_200ns_50ohm_c2_1Mohm.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            outputWaves_50ohm_fft = np.fft.rfft(values)
            frequencies_out_50ohm = np.fft.rfftfreq(
                len(values), seconds[2] - seconds[1]
            )
            axes[3].plot(
                [freq / 1e6 for freq in frequencies_out_50ohm[:101]],
                np.abs(outputWaves_50ohm_fft[:101]),
                label="実測値",
                zorder=1,
            )  # absで振幅を取得
            axes[3].legend(fontsize=FONT_SIZE - 2)
        elif endCondition["impedance"] == 1e6:
            df = pd.read_csv("csv/c1_200ns_open.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            outputWaves_open_fft = np.fft.rfft(values)
            frequencies_out_open = np.fft.rfftfreq(len(values), seconds[2] - seconds[1])
            axes[3].plot(
                [freq / 1e6 for freq in frequencies_out_open[:51]],
                np.abs(outputWaves_open_fft[:51]),
                label="実測値",
                zorder=1,
            )  # absで振幅を取得
            axes[3].legend(fontsize=FONT_SIZE - 2)
    ### 実測値の周波数応答

    # C2(入力電圧)
    tfs_sg = []  # 受電端抵抗を分布定数線路の送電端から見たインピーダンスとし、SGをF行列とした時の伝達関数
    for frequency_Hz in frequencies:
        # 送電端から見たインピーダンスを計算する
        Z11 = tfModules.calcImpedanceAsSeenFromTransmissionEnd(
            frequency_Hz, cable, endCondition
        )
        tfs_sg.append(Z11 / (50 + Z11))
    convolution_input = np.array(inputWaves_fft) * np.array(tfs_sg)

    axes[4].plot(
        [freq / 1e6 for freq in frequencies[:2501]],
        np.abs(convolution_input)[:2501],
        label="シミュレーション",
        linestyle="dashed" if showMeasuredValue else "solid",
        zorder=2,
    )  # absで振幅を取得
    axes[4].set_ylabel("|Amp|", fontsize=FONT_SIZE)
    axes[4].set_xlabel("Frequency[MHz]", fontsize=FONT_SIZE)
    axes[4].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[4].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[4].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    ### 実測値の周波数応答
    if showMeasuredValue:
        if endCondition["impedance"] == 50:
            # df = pd.read_csv("csv/c2_200ns_50ohm.csv", skiprows=11)
            df = pd.read_csv("csv/c2_200ns_50ohm_c2_1Mohm.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            inputWaves_50ohm_fft = np.fft.rfft(values)
            frequencies_input_50ohm = np.fft.rfftfreq(
                len(values), seconds[2] - seconds[1]
            )
            axes[4].plot(
                [freq / 1e6 for freq in frequencies_input_50ohm[:101]],
                np.abs(inputWaves_50ohm_fft[:101]),
                label="実測値",
                zorder=1,
            )  # absで振幅を取得
            axes[4].legend(fontsize=FONT_SIZE - 2)
        elif endCondition["impedance"] == 1e6:
            df = pd.read_csv("csv/c2_200ns_open.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            inputWaves_open_fft = np.fft.rfft(values)
            frequencies_input_open = np.fft.rfftfreq(
                len(values), seconds[2] - seconds[1]
            )
            axes[4].plot(
                [freq / 1e6 for freq in frequencies_input_open[:51]],
                np.abs(inputWaves_open_fft[:51]),
                label="実測値",
                zorder=1,
            )  # absで振幅を取得
            axes[4].legend(fontsize=FONT_SIZE - 2)
    ### 実測値の周波数応答

    # 逆フーリエ変換
    # r = np.fft.ifft(convolution_out, len(T))
    # 入力波形が実数データ向けの逆FFT np.fft.irfft が用意されている。
    # 33点のrfft結果を入力すれば64点の時間領域信号が得られる。
    # 入力波形が実数値のみなので、出力波形も虚数部分は捨ててよい？

    r = np.fft.irfft(convolution_out, len(times))

    axes[5].plot(
        [time * 1e6 for time in times],
        np.real(r),
        zorder=2,
        label="シミュレーション",
        linestyle="dashed" if showMeasuredValue else "solid",
    )
    axes[5].set_ylabel("Amp[V]", fontsize=FONT_SIZE)
    axes[5].set_xlabel("Time[μs]", fontsize=FONT_SIZE)
    axes[5].set_xlim(xfirst, xlast)
    axes[5].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[5].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[5].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    ### 実測値の時間応答
    if showMeasuredValue:
        if endCondition["impedance"] == 50:
            # df = pd.read_csv("csv/c1_200ns_50ohm.csv", skiprows=11)
            df = pd.read_csv("csv/c1_200ns_50ohm_c2_1Mohm.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            axes[5].plot(
                [s * 1e6 + 0.03 for s in seconds],
                values,
                zorder=1,
                label="実測値",
            )
            axes[5].legend(fontsize=FONT_SIZE - 2)
        elif endCondition["impedance"] == 1e6:
            df = pd.read_csv("csv/c1_200ns_open.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            axes[5].plot(
                [s * 1e6 for s in seconds],
                values,
                zorder=1,
                label="実測値",
            )
            axes[5].legend(fontsize=FONT_SIZE - 2)
    ### 実測値の時間応答

    r2 = np.fft.irfft(convolution_input, len(times))

    axes[6].plot(
        [time * 1e6 for time in times],
        np.real(r2),
        label="シミュレーション",
        linestyle="dashed" if showMeasuredValue else "solid",
    )
    axes[6].set_ylabel("Amp[V]", fontsize=FONT_SIZE)
    axes[6].set_xlabel("Time[μs]", fontsize=FONT_SIZE)
    axes[6].set_xlim(xfirst, xlast)
    axes[6].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[6].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[6].xaxis.get_offset_text().set_fontsize(FONT_SIZE)

    ### 実測値の時間応答
    if showMeasuredValue:
        if endCondition["impedance"] == 50:
            # df = pd.read_csv("csv/c2_200ns_50ohm.csv", skiprows=11)
            df = pd.read_csv("csv/c2_200ns_50ohm_c2_1Mohm.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            axes[6].plot(
                [s * 1e6 + 0.03 for s in seconds],
                values,
                zorder=1,
                label="実測値",
            )
            axes[6].legend(fontsize=FONT_SIZE - 2)
        elif endCondition["impedance"] == 1e6:
            df = pd.read_csv("csv/c2_200ns_open.csv", skiprows=11)
            seconds = list(df["Second"])
            values = list(df["Value"])
            axes[6].plot(
                [s * 1e6 for s in seconds],
                values,
                zorder=1,
                label="実測値",
            )
            axes[6].legend(fontsize=FONT_SIZE - 2)
    ### 実測値の時間応答

    plt.tight_layout()
    plt.show()


# 受電端の抵抗が0のとき、断線していない正常のケーブル？
squareWaveFftAndIfft(
    cable.cable_vertual,
    # {"shouldMatching": False, "impedance": 1e6},
    {"shouldMatching": False, "impedance": 50},
    showMeasuredValue=True,
)
