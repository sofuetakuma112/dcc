import pandas as pd
import matplotlib
import statistics
import numpy as np

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt


import util


df = pd.read_csv("csv/data.csv")
frequencies_Hz = list(df["frequency[Hz]"])[21:]
output_volts = list(df["volt_output[V]"])[21:]

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
print(f"1つ目の山谷の間隔: {abs(maxAmpFreqMean - minAmpFreqMean)}[Hz]")

fig, ax = plt.subplots()

FONT_SIZE = 16
ax.plot(
    [freq / 1e6 for freq in frequencies_Hz],
    tfs,
)
# 谷の部分に縦線
ax.plot([4.5, 4.5], [5, 6], color="black", linestyle="dashed")
# 山の部分に縦線
ax.plot([10, 10], [5, 6.5], color="black", linestyle="dashed")
# 谷山の縦線の間に矢印
ax.arrow(
    x=4.5,
    y=5.1,
    dx=5.3,
    dy=0,
    width=0.01,
    head_width=0.1,
    head_length=1,
    length_includes_head=True,
    color="k",
)
# fbetweeenの文言を表示
plt.text(3.5, 4.7, '$f_{between}$', fontsize=FONT_SIZE)
ax.set_xlabel("Frequency [Hz]", fontsize=FONT_SIZE)
ax.tick_params(axis="x", labelsize=FONT_SIZE)
ax.set_ylabel("Gain [dB]", fontsize=FONT_SIZE)
ax.tick_params(axis="y", labelsize=FONT_SIZE)
ax.xaxis.get_offset_text().set_fontsize(FONT_SIZE)

plt.tight_layout()
plt.show()
