import tkinter as tk
import tkinter.ttk as ttk

import numpy as np
import math
import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.ticker as ticker


import cable as cableModules
import util
import matplotlibSettings as pltSettings
import transferFunction as tfModules

root = tk.Tk()  # ウインドの作成
root.title("減衰特性と特性インピーダンスの周波数特性")  # ウインドのタイトル
size = root.maxsize()
root.geometry("{}x{}+0+0".format(*size))
# root.geometry("650x350")  # ウインドの大きさ
frame_1 = tk.LabelFrame(root, labelanchor="nw", text="グラフ", foreground="green")
frame_1.grid(row=0, column=0)
frame_2 = tk.LabelFrame(root, labelanchor="nw", text="パラメータ", foreground="green")
frame_2.grid(row=0, column=1, sticky="nwse")

# frequencies_Hz = list(range(0, 220 * util.ONE_HUNDRED, 100000))
frequencies_Hz = list(range(500 * 1000, 100 * util.ONE_HUNDRED, 100000))

# スケールバーが動いたらその値を読み取りグラフを更新する
def graph(*args):
    axes[0].cla()
    axes[1].cla()
    R = scale_var.get()
    L = scale_var_L.get()
    G = scale_var_G.get()
    C = scale_var_C.get()
    R_nthOf10_negative = scale_var_int.get()
    L_nthOf10_negative = scale_var_L_int.get()
    G_nthOf10_negative = scale_var_G_int.get()
    C_nthOf10_negative = scale_var_C_int.get()

    value_R = f"{R * 10 ** (-1 * R_nthOf10_negative)}"
    value_L = f"{L * 10 ** (-1 * L_nthOf10_negative)}"
    value_G = f"{G * 10 ** (-1 * G_nthOf10_negative)}"
    value_C = f"{C * 10 ** (-1 * C_nthOf10_negative)}"
    text_display.set(str(value_R))
    text_display_L.set(str(value_L))
    text_display_G.set(str(value_G))
    text_display_C.set(str(value_C))

    resistance = R * 10 ** (-1 * R_nthOf10_negative)
    capacitance = C * 10 ** (-1 * C_nthOf10_negative)
    inductance = (1 / (2 * 6 * 15933717.375) ** 2) / capacitance
    # inductance = L * 10 ** (-1 * L_nthOf10_negative)
    conductance = G * 10 ** (-1 * G_nthOf10_negative)

    # drawFrequencyResponseOfAlphaAndCharaImpedance(
    #     frequencies_Hz, resistance, inductance, conductance, capacitance, axes
    # )
    drawFrequencyResponseOfTf(resistance, inductance, conductance, capacitance, axes)
    # calcEndVoltByAnyFreqUnderEndOpenCondition(
    #     frequencies_Hz, resistance, inductance, conductance, capacitance, axes
    # )

    canvas.draw()


def drawFrequencyResponseOfTf(R=0, L=0, G=0, C=0, axes=plt.subplots(2, 1)[1]):
    # Cableインスタンスの作成
    cable = cableModules.Cable(
        resistance=R,
        inductance=L,
        conductance=G,
        capacitance=C,
        length=6,
    )

    # 共振周波数の分母（開放条件）
    resonance_denominator_open = (
        4 * cable.length * math.sqrt(cable.inductance * cable.capacitance)
    )
    # 反共振周波数の分母（開放条件）
    antiresonance_denominator_open = (
        2 * cable.length * math.sqrt(cable.inductance * cable.capacitance)
    )

    # 開放
    resonance_freqs_open = []  # 開放条件時の共振周波数
    antiresonance_freqs_open = []  # 開放条件時の反共振周波数
    # 整数n
    n_length = range(0)  # range(3)だと, 0 ~ 2
    for n in n_length:
        # 共振周波数（開放）
        # nは0から
        resonance_freq_open = (2 * n + 1) / resonance_denominator_open
        resonance_freqs_open.append(resonance_freq_open)
        # 反共振周波数（開放）
        # nは1から
        antiresonance_freq_open = (n + 1) / antiresonance_denominator_open
        antiresonance_freqs_open.append(antiresonance_freq_open)
    resonance_freqs_short = antiresonance_freqs_open  # 短絡条件時の共振周波数
    antiresonance_freqs_short = resonance_freqs_open  # 短絡条件時の反共振周波数

    conditions = [
        {"shouldMatching": False, "impedance": 1e6},
        # {"shouldMatching": False, "impedance": 50},
        # {"shouldMatching": False, "impedance": 1e-6},
    ]
    for (i, condition) in enumerate(conditions):
        tfs = list(
            map(
                lambda frequency_Hz: tfModules.createTransferFunction(
                    frequency_Hz, condition, cable
                ),
                frequencies_Hz,
            )
        )
        axes[i].plot(
            [freq / 1e6 for freq in frequencies_Hz],
            # list(map(abs, tfs)),
            list(map(util.convertGain2dB, tfs)),
        )
        # if i == 0:
        #     # open
        #     axes[i].plot(
        #         resonance_freqs_open,
        #         list(
        #             map(
        #                 util.convertGain2dB,
        #                 tfModules.calcTfsBySomeFreqs(
        #                     resonance_freqs_open, condition, cable
        #                 ),
        #             )
        #         ),
        #         marker="v",
        #         color="blue",
        #         linestyle="",
        #     )
        #     axes[i].plot(
        #         antiresonance_freqs_open,
        #         list(
        #             map(
        #                 util.convertGain2dB,
        #                 # abs,
        #                 tfModules.calcTfsBySomeFreqs(
        #                     antiresonance_freqs_open, condition, cable
        #                 ),
        #             )
        #         ),
        #         marker="o",
        #         color="red",
        #         linestyle="",
        #     )
        #     axes[i].legend(["全ての周波数", "共振周波数", "反共振周波数"], loc="best")
        # elif i == 1:
        #     # short
        #     axes[i].plot(
        #         resonance_freqs_short,
        #         list(
        #             map(
        #                 util.convertGain2dB,
        #                 # abs,
        #                 tfModules.calcTfsBySomeFreqs(
        #                     resonance_freqs_short, condition, cable
        #                 ),
        #             )
        #         ),
        #         marker="v",
        #         color="blue",
        #         linestyle="",
        #     )
        #     axes[i].plot(
        #         antiresonance_freqs_short[1:],
        #         list(
        #             map(
        #                 util.convertGain2dB,
        #                 # abs,
        #                 tfModules.calcTfsBySomeFreqs(
        #                     antiresonance_freqs_short[1:], condition, cable
        #                 ),
        #             )
        #         ),
        #         marker="o",
        #         color="red",
        #         linestyle="",
        #     )
        #     axes[i].legend(["全ての周波数", "共振周波数", "反共振周波数"], loc="best")
        # text = (
        #     "インピーダンスマッチング条件における周波数特性"
        #     if condition["shouldMatching"]
        #     else "受電端開放条件における周波数特性"
        #     if condition["impedance"] >= 1e6
        #     else "受電端短絡条件における周波数特性"
        # )
        FONT_SIZE = 12
        # axes[i].set_title(f"{text}")
        axes[i].set_ylabel("$H_{dB}$[dB]", fontsize=FONT_SIZE)  # y軸は、伝達関数の絶対値
        axes[i].set_xlabel("Frequency [MHz]", fontsize=FONT_SIZE)
        axes[i].xaxis.set_major_formatter(
            pltSettings.FixedOrderFormatter(0, useMathText=True)
        )
        axes[i].ticklabel_format(style="sci", axis="x", scilimits=(0, 0))

    characteristicImpedances = []
    for frequency_Hz in list(frequencies_Hz):
        characteristicImpedances.append(cable.calcCharacteristicImpedance(frequency_Hz))

    # axes[1].plot(frequencies_Hz, np.abs(characteristicImpedances))

    # thetas = [tfModules.calculateTheta(freq, cable) for freq in frequencies_Hz]
    # axes[1].plot(
    #     frequencies_Hz,
    #     list(map(lambda theta: util.np2db(np.real(theta) * 1000), thetas)),
    #     label="α * l",
    # )
    # axes[1].scatter(
    #     [1e6, 10e6],
    #     [14, 48],
    #     label="α * l",
    # )
    # axes[1].set_title("周波数ごとの伝搬定数の推移")
    # axes[1].set_ylabel("alpha[dB/km]", fontsize=FONT_SIZE)
    # axes[1].set_xlabel("Frequency [MHz]", fontsize=FONT_SIZE)
    # axes[1].xaxis.set_major_formatter(
    #     pltSettings.FixedOrderFormatter(6, useMathText=True)
    # )
    # axes[1].legend()

    axes[1].plot(
        [frequency_Hz / 1e6 for frequency_Hz in frequencies_Hz],
        np.abs(
            [
                cable.calcCharacteristicImpedance(frequency_Hz)
                for frequency_Hz in frequencies_Hz
            ]
        ),
    )
    # axes[1].yaxis.set_major_formatter(
    #     pltSettings.FixedOrderFormatter(0, useMathText=True)
    # )
    plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)


# スクロールバーの初期値を設定
R = 1
L = 3
G = 1
C = 1.02

R_nthOf10_negative = 8
L_nthOf10_negative = 9
G_nthOf10_negative = 4
C_nthOf10_negative = 10

resistance = R * 10 ** (-1 * R_nthOf10_negative)
conductance = G * 10 ** (-1 * G_nthOf10_negative)
capacitance = C * 10 ** (-1 * C_nthOf10_negative)
inductance = (1 / (2 * 6 * 15933717.375) ** 2) / capacitance
# inductance = (1 / (5500000 * 24) ** 2) / capacitance
# inductance = L * 10 ** (-1 * L_nthOf10_negative)

number, power = str(inductance).split("e-")
L = float(number[:4])
L_nthOf10_negative = int(power)

fig = plt.Figure()
fig, axes = plt.subplots(2, 1, figsize=(8, 8))
# fig, ax = plt.subplots()
# axes = [ax]

# drawFrequencyResponseOfAlphaAndCharaImpedance(
#     frequencies_Hz, resistance, inductance, conductance, capacitance, axes
# )
drawFrequencyResponseOfTf(resistance, inductance, conductance, capacitance, axes)
# calcEndVoltByAnyFreqUnderEndOpenCondition(
#     frequencies_Hz, resistance, inductance, conductance, capacitance, axes
# )

# tkinterのウインド上部にグラフを表示する
canvas = FigureCanvasTkAgg(fig, master=frame_1)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# row: 0 ~ 3
baseNum = 0
# リアクタンス(R)のスケール作成
scale_var = tk.DoubleVar()
scale_var.set(R)  # スクロールバーの初期値設定？
scale_var.trace("w", graph)
scale = ttk.Scale(frame_2, from_=1, to=10, length=150, orient="h", variable=scale_var)
scale.grid(row=baseNum + 1, column=0)
# リアクタンスのテキスト
text = tk.Label(frame_2, text="リアクタンス:R")
text.grid(row=baseNum, column=0)
# リアクタンスの数値表示テキスト
text_display = tk.StringVar()
text_display.set("{:.3e}".format(R * 10 ** (-1 * R_nthOf10_negative)))
label = tk.Label(frame_2, textvariable=text_display)
label.grid(row=baseNum + 1, column=1)

# リアクタンス_10のn乗(R)のスケール作成
scale_var_int = tk.IntVar()
scale_var_int.set(R_nthOf10_negative)  # スクロールバーの初期値設定？
scale_var_int.trace("w", graph)
spinbox = ttk.Spinbox(frame_2, from_=0, to=15, textvariable=scale_var_int)
spinbox.grid(row=baseNum + 3, column=0)
# リアクタンス_10のn乗のテキスト
text_nthOf10 = tk.Label(frame_2, text="10のマイナスn乗")
text_nthOf10.grid(row=baseNum + 2, column=0)
# # リアクタンス_10のn乗の数値表示テキスト
# text_display_nthOf10 = tk.StringVar()
# text_display_nthOf10.set(str(R))
# label = tk.Label(frame_2, textvariable=text_display_nthOf10)
# label.grid(row=3, column=1)

# row: 4 ~ 7
baseNum += 4
# インダクタンス(L)のスケール作成
scale_var_L = tk.DoubleVar()
scale_var_L.set(L)
scale_var_L.trace("w", graph)
scale_L = ttk.Scale(
    frame_2, from_=1, to=10, length=150, orient="h", variable=scale_var_L
)
scale_L.grid(row=baseNum + 1, column=0)
# # インダクタンスのテキスト
text_L = tk.Label(frame_2, text="インダクタンス:L")
text_L.grid(row=baseNum, column=0)
# インダクタンスの数値表示テキスト
text_display_L = tk.StringVar()
text_display_L.set("{:.3e}".format(L * 10 ** (-1 * L_nthOf10_negative)))
label_L = tk.Label(frame_2, textvariable=text_display_L)
label_L.grid(row=baseNum + 1, column=1)

# インダクタンス_10のn乗(R)のスケール作成
scale_var_L_int = tk.IntVar()
scale_var_L_int.set(L_nthOf10_negative)  # スクロールバーの初期値設定？
scale_var_L_int.trace("w", graph)
spinbox_L = ttk.Spinbox(frame_2, from_=0, to=15, textvariable=scale_var_L_int)
spinbox_L.grid(row=baseNum + 3, column=0)
# インダクタンス_10のn乗のテキスト
text_L_nthOf10 = tk.Label(frame_2, text="10のマイナスn乗")
text_L_nthOf10.grid(row=baseNum + 2, column=0)

# row: 8 ~ 11
baseNum += 4
# コンダクタンスのスケール作成
scale_var_G = tk.DoubleVar()
scale_var_G.set(G)
scale_var_G.trace("w", graph)
scale_G = ttk.Scale(
    frame_2, from_=1, to=10, length=150, orient="h", variable=scale_var_G
)
scale_G.grid(row=baseNum + 1, column=0)
# コンダクタンスのテキスト
text_G = tk.Label(frame_2, text="コンダクタンス:G")
text_G.grid(row=baseNum, column=0)
# コンダクタンスの数値表示テキスト
text_display_G = tk.StringVar()
text_display_G.set("{:.3e}".format(G * 10 ** (-1 * G_nthOf10_negative)))
label_G = tk.Label(frame_2, textvariable=text_display_G)
label_G.grid(row=baseNum + 1, column=1)

# コンダクタンス_10のn乗(R)のスケール作成
scale_var_G_int = tk.IntVar()
scale_var_G_int.set(G_nthOf10_negative)  # スクロールバーの初期値設定？
scale_var_G_int.trace("w", graph)
spinbox_G = ttk.Spinbox(frame_2, from_=0, to=15, textvariable=scale_var_G_int)
spinbox_G.grid(row=baseNum + 3, column=0)
# コンダクタンス_10のn乗のテキスト
text_G_nthOf10 = tk.Label(frame_2, text="10のマイナスn乗")
text_G_nthOf10.grid(row=baseNum + 2, column=0)

# row: 12 ~ 15
baseNum += 4
# キャパシタンスのスケール作成
scale_var_C = tk.DoubleVar()
scale_var_C.set(C)
scale_var_C.trace("w", graph)
scale_C = ttk.Scale(
    frame_2, from_=1, to=10, length=150, orient="h", variable=scale_var_C
)
scale_C.grid(row=baseNum + 1, column=0)
# キャパシタンスのテキスト
text_C = tk.Label(frame_2, text="キャパシタンス:C")
text_C.grid(row=baseNum, column=0)
# キャパシタンスの数値表示テキスト
text_display_C = tk.StringVar()
text_display_C.set("{:.3e}".format(C * 10 ** (-1 * C_nthOf10_negative)))
label_C = tk.Label(frame_2, textvariable=text_display_C)
label_C.grid(row=baseNum + 1, column=1)

# キャパシタンス_10のn乗(R)のスケール作成
scale_var_C_int = tk.IntVar()
scale_var_C_int.set(C_nthOf10_negative)  # スクロールバーの初期値設定？
scale_var_C_int.trace("w", graph)
spinbox_C = ttk.Spinbox(frame_2, from_=0, to=15, textvariable=scale_var_C_int)
spinbox_C.grid(row=baseNum + 3, column=0)
# キャパシタンス_10のn乗のテキスト
text_C_nthOf10 = tk.Label(frame_2, text="10のマイナスn乗")
text_C_nthOf10.grid(row=baseNum + 2, column=0)

root.mainloop()
