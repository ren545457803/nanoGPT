import tushare as ts
import os
import pandas as pd
from datetime import datetime, timedelta


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

def create_input():
    # Step 1: 读取股票文件A，获取list_date<20100101的股票数据，生成数据inputStocks
    stock_file_path = "/home/ren/python/nanoGPT/data/stock/stock.csv"
    input_stocks = pd.read_csv(stock_file_path)
    input_stocks = input_stocks[input_stocks['list_date'] < 20100101][:]
    print(input_stocks)

    # Step 2: 读取文件夹B，获取所有日期文件C
    detail_folder_path = "/home/ren/python/nanoGPT/data/stock/detail"
    detail_files = os.listdir(detail_folder_path)

    # Step 3: 根据ts_code，合并inputStocks和日期文件C，生成文件D
    output_data = {}

    for detail_file in detail_files[:]:
        date = detail_file.split(".")[0]
        detail_file_path = os.path.join(detail_folder_path, detail_file)
        detail_data = pd.read_csv(detail_file_path)

        merged_data = pd.merge(input_stocks, detail_data, on='ts_code', how='inner')
        merged_data = merged_data[['trade_date', 'ts_code', 'pct_chg']]

        for index, row in merged_data.iterrows():
            ts_code = row['ts_code']
            pct_chg = row['pct_chg']
            if date not in output_data:
                output_data[date] = {}
            if ts_code not in output_data[date]:
                output_data[date][ts_code] = pct_chg

    # Convert output_data to DataFrame
    output_df = pd.DataFrame.from_dict(output_data, orient='index')
    output_df.index.name = 'trade_date'

    # Sort DataFrame by trade_date
    output_df.sort_index(inplace=True)

    # Fill NaN values with 1e-6
    output_df.fillna(1e-4, inplace=True)

    print(output_df)

    # Write to output file
    output_file_path = "/home/ren/python/nanoGPT/data/stock/input.csv"
    output_df.to_csv(output_file_path)

    print("Data successfully generated and saved to:", output_file_path)    


# get_stocks()
# get_daily()
# create_input()  
