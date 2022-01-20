import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

import numpy as np

import transferFunction as tfModules
import cable


def squareWaveFftAndIfft(cable, endCondition):
    # サンプリング周期の逆数が入力波形の周波数？
    f = 1000
    rate = 44100  # サンプリング周波数（1秒間に何回サンプリングするか、ナイキスト周波数は44100 / 2）
    # 方形波
    T = np.arange(
        0, 0.0087, 1 / rate  # 0.0087は単パルスが真ん中に来るよう調整した
    )  # len(T) => 441, 1 / rate はサンプリング周期（何秒おきにサンプリングするか）
    # 足し合わされる波は、入力波の周波数の整数倍の周波数を持つ
    squareWaves_time = np.sign(np.sin(2 * np.pi * f * T))
    prevIndex = 0
    indexChunk = []
    chunks = []
    for index, discreteValue in enumerate(squareWaves_time):
        if discreteValue == 1:
            if prevIndex + 1 == index:
                # 同じ-1の塊に現在いる
                indexChunk.append(index)
            else:
                # 次の-1の塊に移動した
                chunks.append(indexChunk)
                indexChunk = []
            prevIndex = index

    single_palse = []
    # print(chunks[4])
    # print("単パルス波形の周波数？ => ", 1 / (len(chunks[4]) * (1 / rate)))
    for index, y in enumerate(squareWaves_time):
        if index in chunks[4]:
            single_palse.append(y)
        else:
            single_palse.append(0)
    inputWaves_time = list(single_palse)

    # sinc関数
    # T = np.linspace(-10, 10, 1000)
    # sincWaves_time = np.sinc(T)
    # inputWaves_time = sincWaves_time

    fig, axes = plt.subplots(3, 2)
    axes = axes.flatten()
    # fig, axes = plt.subplots()
    # fig, axes1 = plt.subplots()
    # fig, axes2 = plt.subplots()
    # fig, axes3 = plt.subplots()
    # fig, axes4 = plt.subplots()
    # fig, axes5 = plt.subplots()
    # axes = [axes, axes1, axes2, axes3, axes4, axes5]

    FONT_SIZE = 12

    axes[0].plot(T, inputWaves_time)
    axes[0].set_title("input(t)")
    axes[0].set_ylabel("Gain", fontsize=FONT_SIZE)
    axes[0].set_xlabel("time [s]", fontsize=FONT_SIZE)

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
    # frequencies = np.fft.fftfreq(len(inputWaves_time), 1.0 / rate)
    frequencies = np.fft.rfftfreq(
        len(inputWaves_time), 1.0 / rate
    )  # len(frequencies) => 193, 1/rate はサンプリング周期（何秒おきにサンプリングするか）
    # print(frequencies, len(frequencies))

    axes[1].plot(frequencies, np.abs(inputWaves_fft))  # absで振幅を取得
    axes[1].set_title("abs(F[input(t)])")
    axes[1].set_ylabel("|F[input(t)]|", fontsize=FONT_SIZE)
    axes[1].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)

    tfs = tfModules.calcTfsBySomeFreqs(
        frequencies,
        endCondition,
        cable,
    )

    axes[2].plot(frequencies, list(map(lambda tf: abs(tf), tfs)))
    axes[2].set_title("abs(H(f))")
    axes[2].set_ylabel("|H(f)|", fontsize=FONT_SIZE)
    axes[2].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    # axes[2].set_yscale("log")

    convolution = np.array(inputWaves_fft) * np.array(
        tfs
    )  # 時間軸の畳み込み積分 = フーリエ変換した値同士の積(の値も周波数軸のもの)
    # convolution = np.array(inputWaves_fft, dtype=np.complex) * np.array(
    #     list(map(lambda tf: abs(tf), tfs)), dtype=np.complex
    # )

    # 入力波形のフーリエ変換 * 伝達関数
    axes[3].plot(frequencies, np.abs(convolution))  # absで振幅を取得
    axes[3].set_title("abs(F[input(t)] * H(f))")
    axes[3].set_ylabel("|F[input(t)] * H(f)|", fontsize=FONT_SIZE)
    axes[3].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)

    # 逆フーリエ変換
    # r = np.fft.ifft(convolution, len(T))
    # 入力波形が実数データ向けの逆FFT np.fft.irfft が用意されている。
    # 33点のrfft結果を入力すれば64点の時間領域信号が得られる。
    # 入力波形が実数値のみなので、出力波形も虚数部分は捨ててよい？
    r = np.fft.irfft(convolution, len(T))
    axes[4].plot(T, np.real(r))
    axes[4].set_title("output(t).real")
    axes[4].set_ylabel("Gain", fontsize=FONT_SIZE)
    axes[4].set_xlabel("time [s]", fontsize=FONT_SIZE)

    r = np.fft.irfft(convolution, len(T))
    axes[5].plot(T, np.imag(r))
    axes[5].set_title("output(t).imag")
    axes[5].set_ylabel("Gain", fontsize=FONT_SIZE)
    axes[5].set_xlabel("time [s]", fontsize=FONT_SIZE)

    plt.tight_layout()
    plt.show()


squareWaveFftAndIfft(
    # cable.Cable(
    #     resistance=1e-3,
    #     # ケーブルの特性インピーダンスの計算結果が50[Ω]になるように意図的に値を設定
    #     inductance=100e-12 * 50 ** 2,
    #     conductance=1e-4,
    #     capacitance=100e-12,  # シートの値を参考に設定？
    #     length=1000,
    # ),
    cable.cable_vertual,
    {"shouldMatching": False, "impedance": 1e-6},  # 受電端の抵抗が0のとき、断線していない正常のケーブル？
)
