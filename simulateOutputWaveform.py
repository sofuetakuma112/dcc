import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

import matplotlibSettings as pltSettings

import numpy as np

import transferFunction as tfModules
import cable


def squareWaveFftAndIfft(cable, endCondition):
    input_wave_frequency = 1e6  # 1[MHz]
    samplingFrequency = (
        input_wave_frequency * 1000
    )  # サンプリング周波数（1秒間に何回サンプリングするか、ナイキスト周波数は44100 / 2）
    # 方形波
    times = np.arange(
        0, 1 / input_wave_frequency, 1 / samplingFrequency
    )  # 1 / samplingFrequency はサンプリング周期（何秒おきにサンプリングするか）
    # len(times) => 1000
    # 足し合わされる波は、入力波の周波数の整数倍の周波数を持つ
    squareWaves_time = np.sign(np.sin(2 * np.pi * input_wave_frequency * times))

    # 周波数f[Hz]の振幅1の正弦波形の時間関数を表している。
    # squareWaves_time = np.sin(2 * np.pi * input_wave_frequency * times)

    # prevIndex = 0
    # indexChunk = []
    # chunks = []
    # for index, discreteValue in enumerate(squareWaves_time):
    #     if discreteValue == 1:
    #         if prevIndex + 1 == index:
    #             # 同じ-1の塊に現在いる
    #             indexChunk.append(index)
    #         else:
    #             # 次の-1の塊に移動した
    #             chunks.append(indexChunk)
    #             indexChunk = []
    #         prevIndex = index

    # single_palse = []
    ratio = len(
        list(filter(lambda y: True if y == 1 else False, squareWaves_time))
    ) / len(squareWaves_time)
    # デューティー比は、パルス幅を周期で割り算したもの
    print(f"デューティー比: {ratio * 100}%")
    # for index, y in enumerate(squareWaves_time):
    #     if index in chunks[4]:
    #         single_palse.append(y)
    #     else:
    #         single_palse.append(0)
    # inputWaves_time = list(single_palse)

    # sinc関数
    # T = np.linspace(-10, 10, 1000)
    # sincWaves_time = np.sinc(T)
    # inputWaves_time = sincWaves_time

    # fig, axes = plt.subplots(3, 2)
    # axes = axes.flatten()
    fig, axes = plt.subplots()
    fig, axes1 = plt.subplots()
    fig, axes2 = plt.subplots()
    fig, axes3 = plt.subplots()
    fig, axes4 = plt.subplots()
    fig, axes5 = plt.subplots()
    axes = [axes, axes1, axes2, axes3, axes4, axes5]

    FONT_SIZE = 12

    inputWaves_time = squareWaves_time
    axes[0].plot(times, inputWaves_time)
    axes[0].set_title("input(t)")
    axes[0].set_ylabel("Gain", fontsize=FONT_SIZE)
    # axes[0].set_xlabel("time [s]", fontsize=FONT_SIZE)
    axes[0].set_xlabel("time [μs]", fontsize=FONT_SIZE)
    axes[0].xaxis.set_major_formatter(
        pltSettings.FixedOrderFormatter(-6, useMathText=True)
    )

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
    # np.fft.fftfreq(FFTを行うデータ点数, サンプリング周期) # サンプリング周期次第で時系列データの時間軸の長さが決定する（100点, 0.01）なら100 * 0.01[s]の時系列データということになる？
    # frequencies = np.fft.fftfreq(len(inputWaves_time), 1.0 / samplingFrequency)
    frequencies = np.fft.rfftfreq(
        len(inputWaves_time), 1.0 / samplingFrequency
    )  # len(frequencies) => 193, 1/samplingFrequency はサンプリング周期（何秒おきにサンプリングするか）
    # print(frequencies, len(frequencies))

    # axes[1].plot(frequencies, np.abs(inputWaves_fft))  # absで振幅を取得
    # axes[1].set_title("abs(F[input(t)])")
    # axes[1].set_ylabel("|F[input(t)]|", fontsize=FONT_SIZE)
    # # axes[1].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    # axes[1].set_xlabel("Frequency [MHz]", fontsize=FONT_SIZE)
    # axes[1].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
    axes[1].plot(frequencies[:10], np.abs(inputWaves_fft[:10]))  # absで振幅を取得
    axes[1].set_title("abs(F[input(t)])")
    axes[1].set_ylabel("|F[input(t)]|", fontsize=FONT_SIZE)
    # axes[1].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    axes[1].set_xlabel("Frequency [MHz]", fontsize=FONT_SIZE)
    axes[1].xaxis.set_major_formatter(
        pltSettings.FixedOrderFormatter(6, useMathText=True)
    )

    tfs = tfModules.calcTfsBySomeFreqs(
        frequencies,
        endCondition,
        cable,
    )

    axes[2].plot(frequencies[:10], list(map(lambda tf: abs(tf), tfs))[:10])
    axes[2].set_title("abs(H(f))")
    axes[2].set_ylabel("|H(f)|", fontsize=FONT_SIZE)
    # axes[2].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    axes[2].set_xlabel("Frequency [MHz]", fontsize=FONT_SIZE)
    axes[2].xaxis.set_major_formatter(
        pltSettings.FixedOrderFormatter(6, useMathText=True)
    )

    convolution = np.array(inputWaves_fft) * np.array(
        tfs
    )  # 時間軸の畳み込み積分 = フーリエ変換した値同士の積(の値も周波数軸のもの)
    # convolution = np.array(inputWaves_fft, dtype=np.complex) * np.array(
    #     list(map(lambda tf: abs(tf), tfs)), dtype=np.complex
    # )

    # 入力波形のフーリエ変換 * 伝達関数
    axes[3].plot(frequencies[:10], np.abs(convolution)[:10])  # absで振幅を取得
    axes[3].set_title("abs(F[input(t)] * H(f))")
    axes[3].set_ylabel("|F[input(t)] * H(f)|", fontsize=FONT_SIZE)
    # axes[3].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    axes[3].set_xlabel("Frequency [MHz]", fontsize=FONT_SIZE)
    axes[3].xaxis.set_major_formatter(
        pltSettings.FixedOrderFormatter(6, useMathText=True)
    )

    # 逆フーリエ変換
    # r = np.fft.ifft(convolution, len(T))
    # 入力波形が実数データ向けの逆FFT np.fft.irfft が用意されている。
    # 33点のrfft結果を入力すれば64点の時間領域信号が得られる。
    # 入力波形が実数値のみなので、出力波形も虚数部分は捨ててよい？

    r = np.fft.irfft(convolution, len(times))

    # timesList = [*times]
    # rs = [*np.real(r)]
    # for i in range(3):
    #     timeCoef = i + 1
    #     times_moved_positive = list(map(lambda t: t + timeCoef * 1e-6, times))
    #     time_moved_negative = list(map(lambda t: t - timeCoef * 1e-6, times))
    #     timesList = [*time_moved_negative, *timesList, *times_moved_positive]
    #     rs = [*np.real(r), *rs, *np.real(r)]
    # axes[4].plot(timesList, rs)
    # axes[4].set_xticks([-2.5e-6, -2e-6, -1e-6, 0, 1e-6, 2e-6, 2.5e-6])
    # axes[4].set_xlim(-2.5e-6, 2.5e-6)

    axes[4].plot(times, np.real(r))

    axes[4].set_title("output(t).real")
    axes[4].set_ylabel("Gain", fontsize=FONT_SIZE)
    # axes[4].set_xlabel("time [s]", fontsize=FONT_SIZE)
    axes[4].set_xlabel("time [μs]", fontsize=FONT_SIZE)
    axes[4].xaxis.set_major_formatter(
        pltSettings.FixedOrderFormatter(-6, useMathText=True)
    )

    r = np.fft.irfft(convolution, len(times))
    axes[5].plot(times, np.imag(r))
    axes[5].set_title("output(t).imag")
    axes[5].set_ylabel("Gain", fontsize=FONT_SIZE)
    # axes[5].set_xlabel("time [s]", fontsize=FONT_SIZE)
    axes[5].set_xlabel("time [μs]", fontsize=FONT_SIZE)
    axes[5].xaxis.set_major_formatter(
        pltSettings.FixedOrderFormatter(-6, useMathText=True)
    )

    plt.tight_layout()
    plt.show()


squareWaveFftAndIfft(
    cable.cable_vertual,
    {"shouldMatching": False, "impedance": 50},  # 受電端の抵抗が0のとき、断線していない正常のケーブル？
)
