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

    
# get_stocks()
get_daily()
