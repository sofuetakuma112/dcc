import pandas as pd
import matplotlib

import matplotlibSettings as pltSettings


matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

df = pd.read_csv("csv/T3DSO2204A_CSV_C1_1.csv", skiprows=11)
seconds = list(df["Second"])
values = list(df["Value"])

fig, ax = plt.subplots()

FONT_SIZE = 12
ax.plot(seconds, values)
ax.set_title("input(t)")
ax.set_ylabel("Gain", fontsize=FONT_SIZE)
ax.set_xlabel("time [μs]", fontsize=FONT_SIZE)
ax.xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(-6, useMathText=True))

plt.tight_layout()
plt.show()
