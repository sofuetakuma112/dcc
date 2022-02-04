import pandas as pd
import matplotlib


matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

FONT_SIZE = 16
axes = [plt.subplots()[1] for i in range(2)]
df = pd.read_csv("csv/singlePlus_end50ohm.csv", skiprows=11)
seconds = list(df["Second"])
values = list(df["Value"])
axes[0].plot([s * 1e6 for s in seconds], values)

df = pd.read_csv("csv/singlePlus_endOpen.csv", skiprows=11)
seconds = list(df["Second"])
values = list(df["Value"])
axes[1].plot([s * 1e6 for s in seconds], values)

for i in range(len(axes)):
    axes[i].set_ylabel("Amp[V]", fontsize=FONT_SIZE)
    axes[i].set_xlabel("Time[μs]", fontsize=FONT_SIZE)
    # axes[i].set_xlim(-0.1, 10)
    axes[i].xaxis.get_offset_text().set_fontsize(FONT_SIZE)
    axes[i].tick_params(axis="y", labelsize=FONT_SIZE)
    axes[i].tick_params(axis="x", labelsize=FONT_SIZE)

plt.tight_layout()
plt.show()
