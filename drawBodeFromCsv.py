import pandas as pd
import matplotlib

import matplotlibSettings as pltSettings


matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

# 受電端開放, RG58A/U, 500kHz ~ 30MHz
df = pd.read_csv("csv/T3DSO2204A_Bode_1.csv", skiprows=27)
frequencies_Hz = list(df["Frequency(Hz)"])
amps = list(df["CH1 Amplitude(dB)"])
phases = list(df["CH1 Phase(Deg)"])

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
