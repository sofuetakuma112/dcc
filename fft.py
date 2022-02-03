import pandas as pd
import matplotlib
import numpy as np

import matplotlibSettings as pltSettings


matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

axes = [plt.subplots()[1] for i in range(2)]

df = pd.read_csv("csv/singlePlus_end50ohm.csv", skiprows=11)
seconds = list(df["Second"])
values = list(df["Value"])
inputWaves_fft = np.fft.rfft(values)
frequencies = np.fft.rfftfreq(len(values), seconds[1] - seconds[0])
axes[0].plot(
    [freq / 1e6 for freq in frequencies[:51]], np.abs(inputWaves_fft[:51])
)  # absで振幅を取得

df = pd.read_csv("csv/singlePlus_endOpen.csv", skiprows=11)
seconds = list(df["Second"])
values = list(df["Value"])
inputWaves_fft = np.fft.rfft(values)
frequencies = np.fft.rfftfreq(len(values), seconds[1] - seconds[0])
axes[1].plot(
    [freq / 1e6 for freq in frequencies[:51]], np.abs(inputWaves_fft[:51])
)  # absで振幅を取得

FONT_SIZE = 16
for i in range(len(axes)):
    axes[i].set_ylabel("Amp", fontsize=FONT_SIZE)
    axes[i].set_xlabel("Frequency[MHz]", fontsize=FONT_SIZE)
    axes[i].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[i].tick_params(axis="x", labelsize=FONT_SIZE)
    axes[i].xaxis.get_offset_text().set_fontsize(FONT_SIZE)
    # axes[i].set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
    # axes[i].xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))

plt.tight_layout()
plt.show()
