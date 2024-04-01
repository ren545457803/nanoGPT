import tushare as ts
import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import json
import time

pro = ts.pro_api()
pro = ts.pro_api('679a90f4181cbe580393fa19da8c083260bc7be22fbfdb4c1c30b14d')
chg_default = -100

file_stocks = os.path.join(os.path.dirname(__file__), 'stock.csv')

def get_stocks():
    if os.path.exists(file_stocks):
        return
    
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    print(len(data))
    # data = data[data['list_date'] < 2010010]
    print(len(data))
    data.to_csv(file_stocks, index=False)

def get_train_stock():
    stocks = pd.read_csv(file_stocks)
    stocks = list(stocks[stocks['list_date'] < 20300101][:].iloc[:,0])
    stocks = [stock for stock in stocks if stock.endswith('.SH') or stock.endswith('.SZ')]
    print(len(stocks))
    return stocks

def get_qfq_daily():
    stocks = pd.read_csv(file_stocks)
    stocks = stocks[stocks['list_date'] < 20300101]
    
    folder_detail = os.path.join(os.path.dirname(__file__), 'qfq')
    os.makedirs(folder_detail, exist_ok=True)

    for _, row in stocks.iterrows():
        # print(row)
        code = row['ts_code']
        file_code = os.path.join(folder_detail, f'{code}.csv')
        if not os.path.exists(file_code):
            time.sleep(0.3)
            df = ts.pro_bar(ts_code=code, adj='qfq', start_date='20230101')
            df.to_csv(file_code, index=False)


def create_input():
    if os.path.exists(os.path.join(os.path.dirname(__file__), 'input.csv')):
        return
    stocks = get_train_stock()

    # 定义输入文件夹路径
    folder_path = os.path.join(os.path.dirname(__file__), 'qfq')

    # 初始化一个空的DataFrame来存储结果
    result_df = pd.DataFrame(columns=["trade_date", "ts_code", "close_chg"])

    # 遍历文件夹中的所有文件
    for filename_stock in stocks:
        file_path = os.path.join(folder_path, filename_stock + '.csv')
        print(file_path)
        # 读取股票内容文件为DataFrame
        stock_df = pd.read_csv(file_path)

        # 计算股价涨幅和交易额涨幅
        stock_df["close_chg"] = (stock_df["close"] / stock_df["close"].shift(-1)).round(4)

        # 处理除以0的情况
        stock_df.loc[stock_df["close"].shift(1) == 0, "close_chg"] = 0

        # 提取所需的列，并将结果追加到result_df中
        result_df = pd.concat([result_df, stock_df[["trade_date", "ts_code", "close_chg"]]])

    # 保存结果到input.csv文件
    result_df.to_csv(os.path.join(os.path.dirname(__file__), 'input.csv'), index=False)


def create_ml_data():
    create_input()

    # 1. 待训练标签，输入 ts_code 列表
    ts_codes = get_train_stock()
    
    # 2. 生成meta数据
    size = len(ts_codes)
    stoi = { ch:i for i,ch in enumerate(ts_codes)}
    itos = { i:ch for i,ch in enumerate(ts_codes)}
    def encode(s):
        return [stoi[c] for c in s]
    def decode(l):
        return ','.join([itos[i] for i in l])
    
    meta = {
        'vocab_size': size,
        'itos': itos,
        'stoi': stoi,
    }
    # 将meta字典写入JSON文件
    with open(os.path.join(os.path.dirname(__file__), 'meta.pkl'), "w") as f:
        json.dump(meta, f)

    # 3. 生成训练和测试数据
    # 3.1 生成全部数据
    file_path = os.path.join(os.path.dirname(__file__), 'input.csv')
    data = pd.read_csv(file_path)
    # 对 trade_date 进行正序排列
    data = data.sort_values(by='trade_date')
    # 初始化一个新的 DataFrame 存储结果
    output_data = pd.DataFrame()


    # 将 trade_date 添加到结果 DataFrame 中
    output_data['trade_date'] = data['trade_date'].unique()

    # 遍历 ts_code 列表并获取 amount_chg 和 close_chg 的数据
    for ts_code in ts_codes:
        print(ts_code)
        # 获取当前 ts_code 的子集
        subset = data[data['ts_code'] == ts_code]

        # 使用 merge() 函数将子集与 output_data DataFrame 合并
        # 在此操作中，我们使用 left_on 和 right_on 参数来指定合并的键
        # how='left' 确保保留所有 trade_date
        output_data = output_data.merge(subset[['trade_date', 'close_chg']], 
                                         left_on='trade_date', right_on='trade_date', 
                                         how='left', suffixes=('', f'_{ts_code}'))

        # 用 1 填充缺失值，并重命名列名以匹配期望的格式
        output_data[f'{ts_code}'] = output_data[f'close_chg'].fillna(chg_default)
        output_data.drop(columns=[f'close_chg'], inplace=True)

    # 3.2 分割数据，成train和val
    n = len(output_data)
    output_data.to_csv(os.path.join(os.path.dirname(__file__), 'train.csv'), index=False)
    

   

print('开始')
get_stocks()
get_qfq_daily()
create_ml_data()

