#!/usr/bin/env python
from control.matlab import *
from matplotlib import pyplot as plt


def main():
    num = [0, 0, 3]
    den = [2, 1, 3]
    # create transfer function (TF) models
    sys = tf(num, den)
    # Bode plot of the frequency response
    bode(sys)
    plt.show()


if __name__ == "__main__":
    main()
