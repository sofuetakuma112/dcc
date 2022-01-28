import numpy as np
import pandas as pd
import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt


import cable as cableModules
import util
import transferFunction as tfModules
import matplotlibSettings as pltSettings


df = pd.read_csv("csv/out_wave_to100MHz.csv")
frequencies_Hz = list(df["frequency[Hz]"])[2:]
output_volts = list(df["volt_output[V]"])[2:]

# freqAndTfs = np.array((freqs, volts_output)).T
# df = pd.DataFrame(
#     freqAndTfs,
#     columns=["frequency[Hz]", "volt_output[V]"],
# )
# df["frequency[Hz]"] = df["frequency[Hz]"].astype("float64")
# df.to_csv("csv/data.csv", index=False)

volts_input = [0.5] * len(frequencies_Hz)

tfs = list(
    map(
        lambda volt_input, volt_output: util.convertGain2dB(
            abs(volt_output / volt_input)
        ),
        volts_input,
        output_volts,
    )
)

firstIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 0))
lastIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 14e6))
maxAmpIndex = tfs.index(max(tfs[firstIndex:lastIndex]))
minAmpIndex = tfs.index(min(tfs[firstIndex:lastIndex]))
mean = (frequencies_Hz[minAmpIndex] + frequencies_Hz[minAmpIndex + 1]) / 2
mountainFreq = frequencies_Hz[maxAmpIndex]
valleyFreq = frequencies_Hz[minAmpIndex]

print(f"谷に対応した周波数: {mean}")
print(f"山に対応した周波数: {mountainFreq}")
print(f"１つ目の山谷の間隔: {abs(mountainFreq - mean)}[Hz]")

firstIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 8))
lastIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 20e6))
maxAmpIndex = tfs.index(max(tfs[firstIndex:lastIndex]))
minAmpIndex = tfs.index(min(tfs[firstIndex:lastIndex]))
mountainFreq = frequencies_Hz[maxAmpIndex]
mean = (frequencies_Hz[minAmpIndex - 1] + frequencies_Hz[minAmpIndex]) / 2
mean2 = (frequencies_Hz[minAmpIndex] + mean) / 2

print(f"山に対応した周波数: {mountainFreq}")
print(f"谷に対応した周波数: {mean2}")
print(f"２つ目の山谷の間隔: {abs(mountainFreq - mean)}[Hz]")

fig, ax = plt.subplots()
ax.scatter(
    frequencies_Hz,
    tfs,
    c="red",
)

ax.plot(
    frequencies_Hz,
    tfs,
)
ax.set_xlabel("frequency [MHz]")
ax.xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
ax.set_ylabel("Gain [dB]")

plt.tight_layout()
plt.show()
