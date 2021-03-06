import pandas as pd
import matplotlib

import matplotlibSettings as pltSettings


matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

import util

# 受電端開放, RG58A/U, 500kHz ~ 30MHz
df = pd.read_csv("csv/bode_rg58au.csv", skiprows=27)
frequencies_Hz = list(df["Frequency(Hz)"])
amps = list(df["CH1 Amplitude(dB)"])
phases = list(df["CH1 Phase(Deg)"])

# 5MHz ~ 17MHzで最大値と最小値をとる周波数を出力する
firstIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 3e6))
lastIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 17e6))
maxAmpIndex = amps.index(max(amps[firstIndex:lastIndex]))
minAmpIndex = amps.index(min(amps[firstIndex:lastIndex]))
mountainFreq_1 = frequencies_Hz[maxAmpIndex]
valleyFreq_1 = frequencies_Hz[minAmpIndex]
print(f"1つ目の山に対応した周波数: {mountainFreq_1 / 1e6}")
print(f"1つ目の谷に対応した周波数: {valleyFreq_1 / 1e6}")
print(f"1つ目の山谷の間隔: {abs(mountainFreq_1 - valleyFreq_1) / 1e6}[MHz]")

firstIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 20e6))
lastIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 35e6))
maxAmpIndex = amps.index(max(amps[firstIndex:lastIndex]))
minAmpIndex = amps.index(min(amps[firstIndex:lastIndex]))
mountainFreq_2 = frequencies_Hz[maxAmpIndex]
valleyFreq_2 = frequencies_Hz[minAmpIndex]
print(f"2つ目の山に対応した周波数: {mountainFreq_2 / 1e6}")
print(f"2つ目の谷に対応した周波数: {valleyFreq_2 / 1e6}")
print(f"2つ目の山谷の間隔: {abs(mountainFreq_2 - valleyFreq_2) / 1e6}[MHz]")

firstIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 36e6))
lastIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 49e6))
maxAmpIndex = amps.index(max(amps[firstIndex:lastIndex]))
minAmpIndex = amps.index(min(amps[firstIndex:lastIndex]))
mountainFreq_3 = frequencies_Hz[maxAmpIndex]
valleyFreq_3 = frequencies_Hz[minAmpIndex]
print(f"3つ目の山に対応した周波数: {mountainFreq_3 / 1e6}")
print(f"3つ目の谷に対応した周波数: {valleyFreq_3 / 1e6}")
print(f"3つ目の山谷の間隔: {abs(mountainFreq_3 - valleyFreq_3) / 1e6}[MHz]")

ave = sum([mountainFreq_2 - mountainFreq_1, mountainFreq_3 - mountainFreq_2]) / 2
print(f"平均の山の間隔: {ave}[Hz]")

# fig, axes = plt.subplots(2, 1)
axes = [plt.subplots()[1]]

FONT_SIZE = 16
axes[0].plot([frequency_Hz / 1e6 for frequency_Hz in frequencies_Hz], amps)
axes[0].set_ylabel("$H_{dB}$[dB]", fontsize=FONT_SIZE)
axes[0].set_xlabel("Frequency[MHz]", fontsize=FONT_SIZE)
# axes[0].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))

# 1つ目の山の部分に縦線
axes[0].plot(
    [mountainFreq_1 / 1e6, mountainFreq_1 / 1e6],
    [0, 27],
    color="black",
    linestyle="dashed",
)
# 2つ目の山の部分に縦線
axes[0].plot(
    [mountainFreq_2 / 1e6, mountainFreq_2 / 1e6],
    [0, 27],
    color="black",
    linestyle="dashed",
)
# 3つ目の山の部分に縦線
axes[0].plot(
    [mountainFreq_3 / 1e6, mountainFreq_3 / 1e6],
    [0, 27],
    color="black",
    linestyle="dashed",
)
# 山1, 山2の縦線の間に矢印
axes[0].arrow(
    x=mountainFreq_1 / 1e6,
    y=20,
    dx=abs(mountainFreq_1 - mountainFreq_2) / 1e6,
    dy=0,
    width=0.01,
    head_width=1,
    head_length=1,
    length_includes_head=True,
    color="skyblue",
)
# fw1の文言を表示
plt.text(14, 17, "$f_{w1}$", fontsize=FONT_SIZE + 2)
# 山2, 山3の縦線の間に矢印
axes[0].arrow(
    x=mountainFreq_2 / 1e6,
    y=15,
    dx=abs(mountainFreq_2 - mountainFreq_3) / 1e6,
    dy=0,
    width=0.01,
    head_width=1,
    head_length=1,
    length_includes_head=True,
    color="skyblue",
)
# fw1の文言を表示
plt.text(31, 12, "$f_{w2}$", fontsize=FONT_SIZE + 2)

axes[0].tick_params(axis="y", labelsize=FONT_SIZE)
axes[0].tick_params(axis="x", labelsize=FONT_SIZE)

# axes[1].plot(frequencies_Hz, phases)
# # axes[1].set_title("input(t)")
# axes[1].set_ylabel("phase[θ]", fontsize=FONT_SIZE)
# axes[1].set_xlabel("Frequency[Hz]", fontsize=FONT_SIZE)
# axes[1].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))

plt.tight_layout()
plt.show()
