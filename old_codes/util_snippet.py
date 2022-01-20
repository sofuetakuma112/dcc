import datetime
import random, string
import os


def createImagePath(fileName=""):
    """
    imgディレクトリ配下に実行時のYYYY_MM_DDのディレクトリを作成し
    そのディレクトリ配下への相対パスを作成する

    Parameters
    ----------
    fileName: string
        保存するファイル名
    """
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, "JST")
    now = datetime.datetime.now(JST)
    today_string = now.strftime("%Y%m%d")
    year = today_string[0:4]
    month = today_string[4:6]
    day = today_string[6:8]

    todayDirectoryName = f"{year}_{month}_{day}"
    imageFileName = createRandomChars(12) if fileName == "" else fileName

    if not os.path.exists(f"img/{todayDirectoryName}"):
        # ディレクトリが存在しない場合、ディレクトリを作成する
        os.makedirs(f"img/{todayDirectoryName}")

    image_file_path = f"img/{todayDirectoryName}/{imageFileName}"
    print(image_file_path)
    return image_file_path


def createRandomChars(n):
    """
    指定された数の長さをもつランダムな文字列を作成する

    Parameters
    ----------
    n: float
        生成する文字数
    """
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return "".join(randlst)


def getNearestNumber(list, num):
    """
    listの中でnumに最も近い値を返却する関数

    Parameters
    ----------
    list : list
        データ配列
    num: float
        対象値
    """

    # リスト要素と対象値の差分を計算し最小値のインデックスを取得
    idx = np.abs(np.asarray(list) - num).argmin()
    return list[idx]
