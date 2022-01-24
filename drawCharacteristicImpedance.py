import matplotlib

matplotlib.rc("font", family="Noto Sans CJK JP")
import matplotlib.pyplot as plt

import numpy as np

import util
import cable as cableModules

frequencies_Hz = range(0, util.ONE_HUNDRED * 100, 1000)

characteristicImpedances = []
for frequency_Hz in list(frequencies_Hz):
    characteristicImpedances.append(
        cableModules.cable_vertual.calcCharacteristicImpedance(frequency_Hz)
    )

fig, ax = plt.subplots()

ax.plot(frequencies_Hz, np.abs(characteristicImpedances))

plt.tight_layout()
plt.show()
