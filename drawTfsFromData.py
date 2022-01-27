import numpy as np
import pandas as pd
import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt


import cable as cableModules
import util
import transferFunction as tfModules
import matplotlibSettings as pltSettings


freqs = [
    10,
    100 * util.ONE_THUOSAND,
    500 * util.ONE_THUOSAND,
    1 * util.ONE_HUNDRED,
    2 * util.ONE_HUNDRED,
    3 * util.ONE_HUNDRED,
    4 * util.ONE_HUNDRED,
    5 * util.ONE_HUNDRED,
    6 * util.ONE_HUNDRED,
    7 * util.ONE_HUNDRED,
    8 * util.ONE_HUNDRED,
    9 * util.ONE_HUNDRED,
    10 * util.ONE_HUNDRED,
    11 * util.ONE_HUNDRED,
    12 * util.ONE_HUNDRED,
    13 * util.ONE_HUNDRED,
    14 * util.ONE_HUNDRED,
    15 * util.ONE_HUNDRED,
    17 * util.ONE_HUNDRED,
    20 * util.ONE_HUNDRED,
    22 * util.ONE_HUNDRED,
    23 * util.ONE_HUNDRED,
    24 * util.ONE_HUNDRED,
    25 * util.ONE_HUNDRED,
    26 * util.ONE_HUNDRED,
    27 * util.ONE_HUNDRED,
    28 * util.ONE_HUNDRED,
    29 * util.ONE_HUNDRED,
    30 * util.ONE_HUNDRED,
    31 * util.ONE_HUNDRED,
    32 * util.ONE_HUNDRED,
    33 * util.ONE_HUNDRED,
    34 * util.ONE_HUNDRED,
    35 * util.ONE_HUNDRED,
    36 * util.ONE_HUNDRED,
    37 * util.ONE_HUNDRED,
    38 * util.ONE_HUNDRED,
    39 * util.ONE_HUNDRED,
    40 * util.ONE_HUNDRED,
    41 * util.ONE_HUNDRED,
    42 * util.ONE_HUNDRED,
    43 * util.ONE_HUNDRED,
    44 * util.ONE_HUNDRED,
    45 * util.ONE_HUNDRED,
    46 * util.ONE_HUNDRED,
    47 * util.ONE_HUNDRED,
    48 * util.ONE_HUNDRED,
    49 * util.ONE_HUNDRED,
    50 * util.ONE_HUNDRED,
    100 * util.ONE_HUNDRED,
]

volts_input = [0.5] * len(freqs)
volts_output = [
    0.62,
    0.62,
    1,
    1,
    0.98,
    0.97,
    0.96,
    0.96,
    0.97,
    0.99,
    1.01,
    1.04,
    1.04,
    1.04,
    1.0,
    0.96,
    0.91,
    0.88,
    0.87,
    0.94,
    1.05,
    1.07,
    1.05,
    0.99,
    0.93,
    0.89,
    0.83,
    0.815,
    0.8,
    0.82,
    0.86,
    0.91,
    0.95,
    0.95,
    1.01,
    0.95,
    0.95,
    0.9,
    0.87,
    0.85,
    0.83,
    0.84,
    0.84,
    0.86,
    0.88,
    0.89,
    0.89,
    0.88,
    0.86,
    0.75,
]

tfs = list(
    map(
        lambda volt_input, volt_output: util.convertGain2dB(
            abs(volt_output / volt_input)
        ),
        volts_input,
        volts_output,
    )
)

# 30MHz未満の範囲でゲイン[dB]の最大値と最小値を求める
firstIndex = freqs.index(util.getNearestNumber(freqs, 0))
lastIndex = freqs.index(util.getNearestNumber(freqs, 28e6))
maxAmpIndex = tfs.index(max(tfs[firstIndex:lastIndex]))
minAmpIndex = tfs.index(min(tfs[firstIndex:lastIndex]))
mountainFreq = freqs[maxAmpIndex]
valleyFreq = freqs[minAmpIndex]

print(f"山に対応した周波数: {mountainFreq}")
print(f"谷に対応した周波数: {valleyFreq}")
print(f"山谷の間隔: {abs(mountainFreq - valleyFreq)}[Hz]")

fig, ax = plt.subplots()
ax.scatter(
    freqs,
    tfs,
    c="red",
)
ax.plot(
    freqs,
    tfs,
)
ax.set_xlabel("frequency [MHz]")
ax.xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
ax.set_ylabel("Gain [dB]")

plt.tight_layout()
plt.show()
