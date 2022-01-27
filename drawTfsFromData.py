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
    500 * util.ONE_THUOSAND,
    1 * util.ONE_HUNDRED,
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
    100 * util.ONE_HUNDRED,
]

volts_input = [0.5] * len(freqs)
volts_output = [
    1,
    1,
    0.9,
    0.87,
    0.94,
    1.05,
    1.8,
    1.5,
    0.99,
    0.93,
    0.89,
    0.83,
    0.815,
    0.8,
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

print(tfs)

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
ax.set_xlabel("frequency [Hz]")
ax.xaxis.set_major_formatter(pltSettings.FixedOrderFormatter(6, useMathText=True))
ax.set_ylabel("Gain [dB]")

plt.tight_layout()
plt.show()
