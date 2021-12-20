import numpy as np
import matplotlib.pyplot as plt

def Dot(M1, M2):
    A = M1[0][0] * M2[0][0] + M1[0][1] * M2[1][0]
    B = M1[0][0] * M2[0][1] + M1[0][1] * M2[1][1]
    C = M1[1][0] * M2[0][0] + M1[1][1] * M2[1][0]
    D = M1[1][0] * M2[0][1] + M1[1][1] * M2[1][1]
    return np.array([[A, B], [C, D]])


# 回路図は、[ https://www.macnica.co.jp/business/semiconductor/articles/basic/127625/ ]
# F1 信号源出力インピーダンス
# Len = 1000
Len = 1000
zeros = np.zeros(Len, dtype=float)
R1 = zeros  # 入力側の抵抗は0.で考える
ones = np.ones(Len, dtype=float)
# 送電端側のF行列
F1 = np.array([[ones, R1], [zeros, ones]])
# print('F1', F1);#stop

# F2: 無損失ケーブル、5D2V < https://moodle35.lms.ehime-u.ac.jp/moodle/pluginfile.php/206396/mod_resource/content/9/%E5%90%8C%E8%BB%B8.pdf >
Z0 = 50 # 特性インピーダンス
# [Ohm]
Re = 0
Co = 0
Ca = 100e-9 # キャパシタンス
# [F/km]
In = Ca * Z0 ** 2 # インダクタンス（無損失条件での特性インピーダンスの式から求めている）
# [H/km]
# print(Z0**2, np.sqrt(In/Ca));stop
Length = 1
# [km]

# 10^4 ～ 10^6 までを値に持つ配列を生成
frequencies_Hz = np.logspace(4, 6, Len, base=10)
# print(frequencies_Hz)
omega = 2 * np.pi * frequencies_Hz
gamma = np.sqrt((Re + 1j * omega * In) * (Co + 1j * omega * Ca))
theta = gamma * Length
cosh = np.cosh(theta)
sinh = np.sinh(theta)
# F2は長さがLenの、線路のF行列のリスト
F2 = np.array(
    [
        [cosh, Z0 * sinh],
        [sinh / Z0, cosh],
    ]
)

# F3　終端抵抗
R2 = ones * 1e6 # 受電端を開放で考えているので、R2を無限に近似している
# 解放#ones*1e-3; # 短絡#ones*Z0  # 整合終端
# 受電端側のF行列
F3 = np.array([[ones, zeros], [1.0 / R2, ones]])
# print(F3);stop

# F1*F3の伝達関数H13
# F13=np.dot(F1, F3)
F13 = Dot(F1, F3)
A13 = F13[0][0]
H13 = 1 / A13
# print(H13);stop

# F1*F2*F3の入力インピーダンスZ11_123
F12 = Dot(F1, F2)
F123 = Dot(F12, F3)
Z11_123 = F123[0][0] / F123[1][0] # (A / C)
# Z11=A/C
# print(Z11_123);

fig, axes = plt.subplots(1, 2)

axes[0].plot(frequencies_Hz, np.abs(Z11_123))
axes[0].set_title("input impedance")
# axes[0].set_xscale("log");#axes[0].xlim(right=1.e6);
axes[0].set_yscale("log")
axes[0].grid()

# 無損失ケーブルの伝達関数
# 受電端を開放(R_2 = ∞)しているので、伝達関数がH(f) = 1 / Aで表される
axes[1].plot(frequencies_Hz, 1 / np.abs(F123[0][0]))
axes[1].set_title("transfer function")
# axes[1].set_xscale("log");
axes[1].set_yscale("log")
axes[1].grid()

plt.show()
