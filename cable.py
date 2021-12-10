# 5C-2V
alpha2_1mhz = 7.6
alpha2_10mhz = 25
alpha2_200mhz = 125
cable_5c2v = {
    "cableLength": 5 / 4,
    "impedance": 75,  # 同軸ケーブルのインピーダンス
    "capacitance": 67,  # (nF/km)
    "alphas": [alpha2_1mhz, alpha2_10mhz, alpha2_200mhz],
}

# 3D-2V
alpha1_1mhz = 13
alpha1_10mhz = 44
alpha1_200mhz = 220
cable_3d2v = {
    "cableLength": 3 / 2,
    "impedance": 50,  # 同軸ケーブルのインピーダンス
    "capacitance": 100,  # (nF/km)
    "alphas": [alpha1_1mhz, alpha1_10mhz, alpha1_200mhz],
}