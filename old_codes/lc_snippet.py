# 解析的に求めたゲイン|G(f)|に値を代入して求める
axes[index + 1].plot(
    frequencies_Hz,
    list(map(lambda tf_abs: 20 * math.log10(tf_abs.real), tfs_abs)),
)
axes[index + 1].set_title(f"R = {R}: Calculated by |G(f)| equation.")
axes[index + 1].set_xlabel("frequency [Hz]")
axes[index + 1].set_ylabel("Gain [db]")
axes[index + 1].set_xscale("log")

def drawFrequencyResponse(calcTransferFunction, cableInfo, outputFileName=""):
    fig, axes = plt.subplots(1, 3)
    axes = axes.flatten()
    index = 0

    for resistance in [5, 50, 1000000]:
        tfs = []
        # tfs_abs = []
        # tf_10Mhz = 0
        # tf_100Mhz = 0
        # gain_ratio = 0

        for frequency_Hz in frequencies_Hz:
            tf = calcTransferFunction(frequency_Hz, resistance, cableInfo)
            tfs.append(tf)

            # tf_abs = R / cmath.sqrt(
            #     (R ** 2) * (1 - (omega ** 2) * L * C_FperM) ** 2 + (omega ** 2) * (L ** 2)
            # )
            # tfs_abs.append(tf_abs)

            # ゲインの傾きを求める
            # # 周波数が10Mhzのとき
            # if frequency_Hz == 10 * 10 ** 6:
            #     tf_10Mhz = tf
            # if frequency_Hz == 100 * 10 ** 6:
            #     tf_100Mhz = tf
            #     # gain_ratio = (util.convertTf2dB(tf_100Mhz) / util.convertTf2dB(tf_10Mhz))
            #     gain_ratio = (abs(tf_100Mhz) / abs(tf_10Mhz))
            # if gain_ratio != 0:
            #     print(f"{gain_ratio}")
            #     gain_ratio = 0

        # 伝達関数G(f)にabs関数を適用してゲインを求める
        axes[index].plot(
            frequencies_Hz,
            list(map(lambda tf: 20 * math.log10(abs(tf)), tfs)),
        )
        axes[index].set_title(f"R = {resistance}")
        axes[index].set_xlabel("frequency [Hz]")
        axes[index].set_ylabel("Gain [db]")
        axes[index].set_xscale("log")

        index += 1

    if outputFileName != "":
        fig.savefig(f"{outputFileName}.png")
    plt.show()



fig, axes = plt.subplots(1, 2)

# デシベル
axes[0].plot(
    frequencies_Hz,
    list(map(lambda tf: 20 * math.log10(abs(tf)), tfs)),
)
# 電圧比
# axes[0].plot(
#     frequencies_Hz,
#     list(map(abs, tfs)),
# )

axes[0].set_title("Apply abs function to transfer function")

axes[0].set_xlabel("frequency [Hz]")
# axes[0].set_ylabel("|H(f)|")
axes[0].set_ylabel("Gain [db]")

axes[0].set_xscale("log")
# axes[0].set_yscale('log')

# デシベル
axes[1].plot(
    frequencies_Hz,
    list(map(lambda tf_abs: 20 * math.log10(tf_abs.real), tfs_abs)),
)
# 電圧比
# axes[1].plot(
#     frequencies_Hz,
#     tfs_abs,
# )

axes[1].set_title("Calculated by substituting values into the gain equation.")

axes[1].set_xlabel("frequency [Hz]")
# axes[1].set_ylabel("|H(f)|")
axes[1].set_ylabel("Gain [db]")

axes[1].set_xscale("log")
# axes[1].set_yscale('log')

fig.savefig("lc_filter_frequency_characteristic.png")