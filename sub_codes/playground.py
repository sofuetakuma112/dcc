import numpy as np
import math
import cmath
import statistics

print(1 / (4 * 6 * np.sqrt(2.54e-17)))  # 8267456.14721401

print(1 / (7346938.82 * 24) ** 2)  # 3.216360129084713e-17 = LC

# ndarray = np.array(
#     [
#         [1, 2],
#         [3, 4],
#     ]
# )
# print(ndarray[0][0])
# print(ndarray[0][1])

# print(20 / math.log(10))
# print(cmath.sqrt(1 + 2j))
# print((1 + 2j) * 6)

print(1 / (4500000 * 24) ** 2)  # 4.822530864197531e-17 = LC

times = np.arange(0, 1, 1e-3)  # [0, ..., 0.999]
print(len(times))

print((1 / (12 * 5e5)) ** 2)  # 2.78e-14
print((1 / (4000000 * 24) ** 2))  # 1.0850694444444444e-16

print(statistics.mean([(1 / (12 * 5e5)) ** 2, (1 / (4000000 * 24) ** 2)]))

print(1 / (4 * 6 * np.sqrt(1.0850694444444444e-16)))

for i in range(3):
    print(i)

print(3.6e-3 / (math.e ** (np.sqrt(2.3) * 50 / 138)))

print((1 / (5.5e6 * 4 * 6) ** 2) / 1.02e-10)

float_str = "5.626676749671402e-07"
number, power = float_str.split('e-')
print(number[:4], power)

print((1 / (5.5e6 * 4 * 6) ** 2) / 7.25e-11)

print((1 / (2 * 6 * 15933717.375) ** 2))

print((1 / (2 * 6 * 15933717.375) ** 2) / 1.02e-10)