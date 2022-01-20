def drawAttenuationConstantBySomeRLGC():
    resistances = [1e-4, 1e-5, 1e-6]
    conductances = [1e-4, 1e-5, 1e-6]
    inductances = []

    count = 0
    fig, axes = plt.subplots(len(resistances), len(conductances))
    axes = axes.flatten()
    for i, R in enumerate(resistances):
        for j, G in enumerate(conductances):
            drawAttenuationConstant(
                list(range(0, 220 * util.ONE_HUNDRED, 10000)),
                cableModules.Cable(
                    resistance=R,  # 無損失ケーブルを考える
                    inductance=2.5e-9,
                    conductance=G,  # 無損失ケーブルを考える
                    capacitance=100e-12,  # シートの値を参考に設定？
                    length=1000,
                ),
                axes[count],
                False,
            )

            axes[count].set_title(f"R = {R}, G = {G}")
            count += 1
    plt.tight_layout()
    plt.show()


# drawAttenuationConstantBySomeRLGC()
