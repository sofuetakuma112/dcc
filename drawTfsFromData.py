import numpy as np
import pandas as pd
import matplotlib
import statistics

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt


import cable as cableModules
import util
import transferFunction as tfModules
import matplotlibSettings as pltSettings


df = pd.read_csv("csv/data.csv")
frequencies_Hz = list(df["frequency[Hz]"])[16:]
output_volts = list(df["volt_output[V]"])[16:]
print(f"開始: {frequencies_Hz[0]}[Hz]")
print(f"開始: {output_volts[0]}[V]")

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

firstIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 1e5))
lastIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 6e6))
maxAmpIndex = tfs.index(max(tfs[firstIndex:lastIndex]))
minAmpIndex = tfs.index(min(tfs[firstIndex:lastIndex]))

# 隣接する要素の値と比較して同じ値を取るインデックスのリストを作る
def searchIndexesTakeSameValue(values, indexOfValue):
    currentNum = 1
    indexes = [indexOfValue]
    value = values[indexOfValue]
    while True:
        if values[indexOfValue - currentNum] == value:
            indexes = [indexOfValue - currentNum] + indexes
        if values[indexOfValue + currentNum] == value:
            indexes = indexes + [indexOfValue + currentNum]
        if (
            values[indexOfValue - currentNum] != value
            and values[indexOfValue + currentNum] != value
        ):
            return indexes
        currentNum += 1


minAmpIndexes = searchIndexesTakeSameValue(tfs, minAmpIndex)
maxAmpIndexes = searchIndexesTakeSameValue(tfs, maxAmpIndex)

maxAmpFreqMean = statistics.mean([frequencies_Hz[i] for i in maxAmpIndexes[1:3]])
minAmpFreqMean = statistics.mean([frequencies_Hz[i] for i in minAmpIndexes])

print(f"谷に対応した周波数: {minAmpFreqMean}")
print(f"山に対応した周波数: {maxAmpFreqMean}")
print(f"1つ目の山谷の間隔: {abs(maxAmpFreqMean - minAmpFreqMean)}[Hz]")  # 4.2MHz

firstIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 2e6))
lastIndex = frequencies_Hz.index(util.getNearestNumber(frequencies_Hz, 12e6))
maxAmpIndex = tfs.index(max(tfs[firstIndex:lastIndex]))
minAmpIndex = tfs.index(min(tfs[firstIndex:lastIndex]))
minAmpIndexes = searchIndexesTakeSameValue(tfs, minAmpIndex)
maxAmpIndexes = searchIndexesTakeSameValue(tfs, maxAmpIndex)
maxAmpFreqMean = statistics.mean([frequencies_Hz[i] for i in maxAmpIndexes[1:3]])
minAmpFreqMean = statistics.mean([frequencies_Hz[i] for i in minAmpIndexes])
print(f"谷に対応した周波数: {minAmpFreqMean}")
print(f"山に対応した周波数: {maxAmpFreqMean}")
print(f"2つ目の山谷の間隔: {abs(maxAmpFreqMean - minAmpFreqMean)}[Hz]")  # 4.2MHz

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
