import pandas as pd
import matplotlib

import matplotlibSettings as pltSettings


matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

import util

# 受電端開放, RG58A/U, 500kHz ~ 30MHz
df = pd.read_csv("csv/T3DSO2204A_Bode_1.csv", skiprows=27)
frequencies_Hz = list(df["Frequency(Hz)"])
amps = list(df["CH1 Amplitude(dB)"])
phases = list(df["CH1 Phase(Deg)"])

# 5MHz ~ 17MHzで最大値と最小値をとる周波数を出力する
firstIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 5e6))
lastIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 17e6))
maxAmpIndex = amps.index(max(amps[firstIndex:lastIndex]))
minAmpIndex = amps.index(min(amps[firstIndex:lastIndex]))
mountainFreq = frequencies_Hz[maxAmpIndex]
valleyFreq = frequencies_Hz[minAmpIndex]
print(f"山に対応した周波数: {mountainFreq}")
print(f"谷に対応した周波数: {valleyFreq}")
print(f"山谷の間隔: {abs(mountainFreq - valleyFreq)}[Hz]") # 7346938.819999999[Hz] => 7.34[MHz]
# LC = 6e-9
# LC = 0.000000006(l = 6[m])を満たせば、RG58A/Uの周波数特性の山谷間隔を再現できる

fig, axes = plt.subplots(2, 1)

FONT_SIZE = 12
axes[0].plot(frequencies_Hz, amps)
# axes[0].set_title("input(t)")
axes[0].set_ylabel("Gain[dB]", fontsize=FONT_SIZE)
axes[0].set_xlabel("frequency[MHz]", fontsize=FONT_SIZE)
axes[0].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))

axes[1].plot(frequencies_Hz, phases)
# axes[1].set_title("input(t)")
axes[1].set_ylabel("phase[θ]", fontsize=FONT_SIZE)
axes[1].set_xlabel("frequency[MHz]", fontsize=FONT_SIZE)
axes[1].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))

plt.tight_layout()
plt.show()
