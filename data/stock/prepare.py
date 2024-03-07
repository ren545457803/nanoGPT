import tushare as ts
import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import pickle


pro = ts.pro_api()
pro = ts.pro_api('679a90f4181cbe580393fa19da8c083260bc7be22fbfdb4c1c30b14d')

file_stocks = os.path.join(os.path.dirname(__file__), 'stock.csv')

def get_stocks():
    if os.path.exists(file_stocks):
        return
    
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    print(len(data))
    # data = data[data['list_date'] < 2010010]
    print(len(data))
    data.to_csv(file_stocks, index=False)

def get_daily():
    stocks = pd.read_csv(file_stocks)
    stocks = stocks[stocks['list_date'] < 20100101]
    
    folder_detail = os.path.join(os.path.dirname(__file__), 'detail')
    os.makedirs(folder_detail, exist_ok=True)

    start_date = datetime(2010, 1, 1)
    current_date = datetime.now()
    # 循环遍历日期范围
    while start_date <= current_date:
        datestr = start_date.strftime('%Y%m%d')
        file_detail = os.path.join(folder_detail, f'{datestr}.csv')
        if not os.path.exists(file_detail):
            df = pro.daily(trade_date=datestr)
            df.to_csv(file_detail, index=False)
        
        start_date += timedelta(days=1) 

def get_qfq_daily():
    stocks = pd.read_csv(file_stocks)
    stocks = stocks[stocks['list_date'] < 20100101]
    
    folder_detail = os.path.join(os.path.dirname(__file__), 'qfq')
    os.makedirs(folder_detail, exist_ok=True)

    for _, row in stocks.iterrows():
        print(row)
        code = row['ts_code']
        file_code = os.path.join(folder_detail, f'{code}.csv')
        if not os.path.exists(file_code):
            df = ts.pro_bar(ts_code=code, adj='qfq', start_date='20100101')
            df.to_csv(file_code, index=False)
            
     

def create_data():
    file_input = os.path.join(os.path.dirname(__file__), 'input.csv')
    df = pd.read_csv(file_input)
    # df = df.iloc[:, 1:] # 不要第一列日期
    
    # vocab_size = 1024
    # df = df.iloc[:, :vocab_size] #取前1024列数据

    vocabs = df.columns.values
    
    stoi = { ch:i for i,ch in enumerate(vocabs)}
    itos = { i:ch for i,ch in enumerate(vocabs)}
    def encode(s):
        return [stoi[c] for c in s]
    def decode(l):
        return ''.join([itos[i] for i in l])
    
    print(np.argmax(df))
    problematic_value = df[np.argmax(df)]
    print(problematic_value)

    n = len(df)
    train_data = df[:int(n*0.9)]
    val_data = df[int(n*0.9):]
    
    np.array(train_data, dtype=np.float16).tofile(os.path.join(os.path.dirname(__file__), 'train.bin'))
    np.array(val_data, dtype=np.float16).tofile(os.path.join(os.path.dirname(__file__), 'val.bin'))

    meta = {
        'vocab_size': 1024,
        'itos': itos,
        'stoi': stoi,
    }
    with open(os.path.join(os.path.dirname(__file__), 'meta.pkl'), 'wb') as f:
        pickle.dump(meta, f)
    



def create_input():     
    # 定义输入文件夹路径
    folder_path = os.path.join(os.path.dirname(__file__), 'qfq')

    # 初始化一个空的DataFrame来存储结果
    result_df = pd.DataFrame(columns=["trade_date", "ts_code", "close", "close_chg", "amount", "amount_chg"])

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv") and '.' in filename:
            file_path = os.path.join(folder_path, filename)

            # 读取股票内容文件为DataFrame
            stock_df = pd.read_csv(file_path)

            # 计算股价涨幅和交易额涨幅
            stock_df["close_chg"] = (stock_df["close"] / stock_df["close"].shift(-1)).round(4)
            stock_df["amount_chg"] = (stock_df["amount"] / stock_df["amount"].shift(-1)).round(4)

            # 处理除以0的情况
            stock_df.loc[stock_df["close"].shift(1) == 0, "close_chg"] = 0
            stock_df.loc[stock_df["amount"].shift(1) == 0, "amount_chg"] = 0

            # 提取所需的列，并将结果追加到result_df中
            result_df = pd.concat([result_df, stock_df[["trade_date", "ts_code", "close", "close_chg", "amount", "amount_chg"]]])

    # 保存结果到input.csv文件
    result_df.to_csv(os.path.join(os.path.dirname(__file__), 'input.csv'), index=False)


# get_stocks()
# get_daily()
create_input()  
# create_data()
# get_qfq_daily()
    

