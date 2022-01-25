import numpy as np
import pandas as pd
import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt


import cable as cableModules
import util
import transferFunction as tfModules

frequencies_Hz = list(range(500 * 1000, 50 * util.ONE_HUNDRED, 1000))
tfs = tfModules.calcTfsBySomeFreqs(
    frequencies_Hz,
    {"shouldMatching": False, "impedance": 50},
    cableModules.cable_vertual,
)

fig, ax = plt.subplots()
ax.plot(
    frequencies_Hz,
    list(map(util.convertGain2dB, tfs)),
)
ax.set_xlabel("frequency [Hz]")
ax.set_ylabel("Gain [dB]")
ax.set_xscale("log")

freqAndTfs = np.array((frequencies_Hz, tfs)).T
df = pd.DataFrame(
    freqAndTfs,
    columns=["frequency_Hz", "tf"],
)
df["frequency_Hz"] = df["frequency_Hz"].astype("float64")
df.to_csv("csv/out.csv", index=False)

plt.show()
