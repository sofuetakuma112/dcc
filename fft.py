import pandas as pd
import matplotlib
import numpy as np

import matplotlibSettings as pltSettings


matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

# df = pd.read_csv("csv/T3DSO2204A_CSV_C1_1.csv", skiprows=11)
df = pd.read_csv("csv/singlePlus_end50ohm.csv", skiprows=11)
seconds = list(df["Second"])
values = list(df["Value"])

FONT_SIZE = 12
axes = [plt.subplots()[1] for i in range(2)]

inputWaves_fft = np.fft.rfft(values)
frequencies = np.fft.rfftfreq(len(values), seconds[1] - seconds[0])

axes[0].plot(frequencies[:50], np.abs(inputWaves_fft[:50]))  # absで振幅を取得
axes[0].set_ylabel("|F[input(t)]|", fontsize=FONT_SIZE)
# axes[0].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
axes[0].set_xlabel("frequency [MHz]", fontsize=FONT_SIZE)
axes[0].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))

df = pd.read_csv("csv/singlePlus_endOpen.csv", skiprows=11)
seconds = list(df["Second"])
values = list(df["Value"])

inputWaves_fft = np.fft.rfft(values)
frequencies = np.fft.rfftfreq(len(values), seconds[1] - seconds[0])

axes[1].plot(frequencies[:50], np.abs(inputWaves_fft[:50]))  # absで振幅を取得
axes[1].set_ylabel("|F[input(t)]|", fontsize=FONT_SIZE)
# axes[1].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
axes[1].set_xlabel("frequency [MHz]", fontsize=FONT_SIZE)
axes[1].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))

plt.tight_layout()
plt.show()
