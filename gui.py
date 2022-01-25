import tkinter as tk
import tkinter.ttk as ttk

import numpy as np

import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import cable as cableModules
import util
import matplotlibSettings as pltSettings

root = tk.Tk()  # ウインドの作成
root.title("減衰特性と特性インピーダンスの周波数特性")  # ウインドのタイトル
root.geometry("650x350")  # ウインドの大きさ
frame_1 = tk.LabelFrame(root, labelanchor="nw", text="グラフ", foreground="green")
frame_1.grid(row=0, column=0)
frame_2 = tk.LabelFrame(root, labelanchor="nw", text="パラメータ", foreground="green")
frame_2.grid(row=0, column=1, sticky="nwse")

frequencies_Hz = list(range(0, 220 * util.ONE_HUNDRED, 100000))

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
    inductance = L * 10 ** (-1 * L_nthOf10_negative)
    conductance = G * 10 ** (-1 * G_nthOf10_negative)
    capacitance = C * 10 ** (-1 * C_nthOf10_negative)

    drawFrequencyResponse(resistance, inductance, conductance, capacitance, axes)
    canvas.draw()


def drawFrequencyResponse(R, L, G, C, axes):
    # Cableインスタンスの作成
    cable = cableModules.Cable(
        resistance=R,
        inductance=L,
        conductance=G,
        capacitance=C,
        length=100,  # alphaとZoの計算には関係ないので適用な値で初期化
    )
    # 周波数ごとにalphaを求める
    alphas_db = []
    for frequency_Hz in frequencies_Hz:
        #  5C-2V + Zrの回路の入力インピーダンスを受電端側の抵抗Zrとする
        alpha_np = util.calcAttenuationConstant(frequency_Hz, cable)  # Np/m
        alpha_db = util.np2db(alpha_np)  # dB/m
        alphas_db.append(alpha_db)

    FONT_SIZE = 12
    axes[0].plot(
        frequencies_Hz,
        list(map(lambda x: x * 1000, alphas_db)),
        label="vertual cable",
        zorder=5,
    )  # absで振幅を取得
    axes[0].set_title("周波数ごとの減衰定数の推移")
    axes[0].set_ylabel("α [dB/km]", fontsize=FONT_SIZE)
    axes[0].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    for (exist_cable, color, marker) in zip(
        cableModules.exist_cables, pltSettings.colors, pltSettings.markers
    ):
        axes[0].plot(
            [1e6, 10e6, 200e6],  # 1MHz, 10MHz, 200MHz
            exist_cable["alphas"],
            marker=marker,
            color=color,
            label=exist_cable["name"],
        )
        axes[0].legend()

    # axes[0].set_title(
    #     f"R = {str(value_R)}, L = {str(value_L)}, G = {str(value_G)}, C = {str(value_C)}"
    # )

    characteristicImpedances = []
    for frequency_Hz in list(frequencies_Hz):
        characteristicImpedances.append(cable.calcCharacteristicImpedance(frequency_Hz))
    axes[1].plot(frequencies_Hz, np.abs(characteristicImpedances))


# スクロールバーの初期値を設定
R = 1
L = 3
G = 1
C = 1

R_nthOf10_negative = 8
L_nthOf10_negative = 9
G_nthOf10_negative = 4
C_nthOf10_negative = 12

resistance = R * 10 ** (-1 * R_nthOf10_negative)
inductance = L * 10 ** (-1 * L_nthOf10_negative)
conductance = G * 10 ** (-1 * G_nthOf10_negative)
capacitance = C * 10 ** (-1 * C_nthOf10_negative)

fig = plt.Figure()
fig, axes = plt.subplots(2, 1)

drawFrequencyResponse(resistance, inductance, conductance, capacitance, axes)

# tkinterのウインド上部にグラフを表示する
canvas = FigureCanvasTkAgg(fig, master=frame_1)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# リアクタンス(R)のスケール作成
scale_var = tk.DoubleVar()
scale_var.set(R)  # スクロールバーの初期値設定？
scale_var.trace("w", graph)
scale = ttk.Scale(frame_2, from_=1, to=10, length=150, orient="h", variable=scale_var)
scale.grid(row=1, column=0)
# リアクタンスのテキスト
text = tk.Label(frame_2, text="リアクタンス:R")
text.grid(row=0, column=0)
# リアクタンスの数値表示テキスト
text_display = tk.StringVar()
text_display.set(str(R))
label = tk.Label(frame_2, textvariable=text_display)
label.grid(row=1, column=1)

# リアクタンス_10のn乗(R)のスケール作成
scale_var_int = tk.IntVar()
scale_var_int.set(R_nthOf10_negative)  # スクロールバーの初期値設定？
scale_var_int.trace("w", graph)
spinbox = ttk.Spinbox(frame_2, from_=0, to=15, textvariable=scale_var_int)
spinbox.grid(row=3, column=0)
# リアクタンス_10のn乗のテキスト
text_nthOf10 = tk.Label(frame_2, text="リアクタンス_10のマイナスn乗:R")
text_nthOf10.grid(row=2, column=0)
# # リアクタンス_10のn乗の数値表示テキスト
# text_display_nthOf10 = tk.StringVar()
# text_display_nthOf10.set(str(R))
# label = tk.Label(frame_2, textvariable=text_display_nthOf10)
# label.grid(row=3, column=1)

# row: 4 ~ 7
# インダクタンス(L)のスケール作成
scale_var_L = tk.DoubleVar()
scale_var_L.set(L)
scale_var_L.trace("w", graph)
scale_L = ttk.Scale(
    frame_2, from_=1, to=10, length=150, orient="h", variable=scale_var_L
)
scale_L.grid(row=5, column=0)
# # インダクタンスのテキスト
text_L = tk.Label(frame_2, text="インダクタンス:L")
text_L.grid(row=4, column=0)
# インダクタンスの数値表示テキスト
text_display_L = tk.StringVar()
text_display_L.set(str(L))
label_L = tk.Label(frame_2, textvariable=text_display_L)
label_L.grid(row=5, column=1)

# インダクタンス_10のn乗(R)のスケール作成
scale_var_L_int = tk.IntVar()
scale_var_L_int.set(L_nthOf10_negative)  # スクロールバーの初期値設定？
scale_var_L_int.trace("w", graph)
spinbox_L = ttk.Spinbox(frame_2, from_=0, to=15, textvariable=scale_var_L_int)
spinbox_L.grid(row=7, column=0)
# インダクタンス_10のn乗のテキスト
text_L_nthOf10 = tk.Label(frame_2, text="インダクタンス_10のマイナスn乗:R")
text_L_nthOf10.grid(row=6, column=0)

# row: 8 ~ 11
# コンダクタンスのスケール作成
scale_var_G = tk.DoubleVar()
scale_var_G.set(G)
scale_var_G.trace("w", graph)
scale_G = ttk.Scale(
    frame_2, from_=1, to=10, length=150, orient="h", variable=scale_var_G
)
scale_G.grid(row=9, column=0)
# コンダクタンスのテキスト
text_G = tk.Label(frame_2, text="コンダクタンス:G")
text_G.grid(row=8, column=0)
# コンダクタンスの数値表示テキスト
text_display_G = tk.StringVar()
text_display_G.set(str(G))
label_G = tk.Label(frame_2, textvariable=text_display_G)
label_G.grid(row=9, column=1)

# コンダクタンス_10のn乗(R)のスケール作成
scale_var_G_int = tk.IntVar()
scale_var_G_int.set(G_nthOf10_negative)  # スクロールバーの初期値設定？
scale_var_G_int.trace("w", graph)
spinbox_G = ttk.Spinbox(frame_2, from_=0, to=15, textvariable=scale_var_G_int)
spinbox_G.grid(row=11, column=0)
# コンダクタンス_10のn乗のテキスト
text_G_nthOf10 = tk.Label(frame_2, text="コンダクタンス_10のマイナスn乗:R")
text_G_nthOf10.grid(row=10, column=0)

# row: 12 ~ 15
# キャパシタンスのスケール作成
scale_var_C = tk.DoubleVar()
scale_var_C.set(C)
scale_var_C.trace("w", graph)
scale_C = ttk.Scale(
    frame_2, from_=1, to=10, length=150, orient="h", variable=scale_var_C
)
scale_C.grid(row=13, column=0)
# キャパシタンスのテキスト
text_C = tk.Label(frame_2, text="キャパシタンス:C")
text_C.grid(row=12, column=0)
# キャパシタンスの数値表示テキスト
text_display_C = tk.StringVar()
text_display_C.set(str(C))
label_C = tk.Label(frame_2, textvariable=text_display_C)
label_C.grid(row=13, column=1)

# キャパシタンス_10のn乗(R)のスケール作成
scale_var_C_int = tk.IntVar()
scale_var_C_int.set(C_nthOf10_negative)  # スクロールバーの初期値設定？
scale_var_C_int.trace("w", graph)
spinbox_C = ttk.Spinbox(frame_2, from_=0, to=15, textvariable=scale_var_C_int)
spinbox_C.grid(row=15, column=0)
# キャパシタンス_10のn乗のテキスト
text_C_nthOf10 = tk.Label(frame_2, text="キャパシタンス_10のマイナスn乗:R")
text_C_nthOf10.grid(row=14, column=0)

root.mainloop()
