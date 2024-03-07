import pandas as pd
import matplotlib.pyplot as plt


def plot_histogram(filename, ts_code=None):
    # 读取CSV文件
    df = pd.read_csv(filename)

    # 根据ts_code筛选数据
    if ts_code:
        df = df[df['ts_code'] == ts_code]

    # 提取close_chg和amount_chg字段的数据
    close_chg_data = df['close_chg']
    amount_chg_data = df['amount_chg']

    # 创建直方图
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    axs[0].hist(close_chg_data, bins=20, color='blue', alpha=0.7)
    axs[0].set_xlabel('close_chg')
    axs[0].set_ylabel('Frequency')

    axs[1].hist(amount_chg_data, bins=20, color='green', alpha=0.7)
    axs[1].set_xlabel('amount_chg')
    axs[1].set_ylabel('Frequency')

    # 展示直方图
    plt.tight_layout()
    plt.show()


# 指定CSV文件路径
filename = '/Users/renyabin/python/nanoGPT/data/stock/input.csv'

# 调用函数展示直方图（不传ts_code参数）
# plot_histogram(filename)

# 如果要根据ts_code筛选数据，可以传入ts_code参数
plot_histogram(filename, '000509.SZ')
