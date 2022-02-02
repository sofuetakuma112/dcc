import pandas as pd
import matplotlib

import matplotlibSettings as pltSettings


matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

# df = pd.read_csv("csv/T3DSO2204A_CSV_C1_1.csv", skiprows=11)
df = pd.read_csv("csv/singlePlus_end50ohm.csv", skiprows=11)
seconds = list(df["Second"])
values = list(df["Value"])

fig, ax = plt.subplots()

FONT_SIZE = 12
# ax.plot(seconds, values)
# ax.set_title("input(t)")
ax.set_ylabel("Vout[V]", fontsize=FONT_SIZE)
ax.set_xlabel("time[μs]", fontsize=FONT_SIZE)
ax.set_xlim(-0.1e-6, 10e-6)
ax.xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(-6, useMathText=True))

df = pd.read_csv("csv/singlePlus_endOpen.csv", skiprows=11)
seconds = list(df["Second"])
values = list(df["Value"])
ax.plot(seconds, values)

plt.tight_layout()
plt.show()
