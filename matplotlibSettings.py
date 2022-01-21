from matplotlib.ticker import ScalarFormatter

# クラス設定  ※ScalarFormatterを継承
class FixedOrderFormatter(ScalarFormatter):
    def __init__(self, order_of_mag=0, useOffset=True, useMathText=True):
        self._order_of_mag = order_of_mag
        ScalarFormatter.__init__(self, useOffset=useOffset, useMathText=useMathText)

    def _set_order_of_magnitude(self):
        self.orderOfMagnitude = self._order_of_mag


# matplotlibのグラフ表示に使用するオプション群
colors = [
    "tab:blue",
    "tab:orange",
    "tab:green",
    "tab:red",
    "tab:purple",
    "tab:brown",
    "tab:pink",
    "tab:gray",
    "tab:olive",
]
markers = [".", ",", "o", "v", "^", "<", ">", "1", "2"]
