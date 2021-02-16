from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import os
import json
import argparse


'''1st data source___web_scraper'''
def get_ipo_since2019(limit=None):
    page = requests.get('https://www.iposcoop.com/ipos-recently-filed/').text
    soup = BeautifulSoup(page, 'lxml')

    ipo_table = soup.find('table', attrs={'class': 'standard-table ipolist'})
    ipo_table_data = ipo_table.tbody.find_all('tr')

#     find headings of the IPOtable
    headings = []
    for th in ipo_table.find_all('th'):
        # convert to text and remove any newlines
        th = (th.text).rstrip('\n')
        headings.append(th)

#     find all other rows in the IPO table
    all_data = []
    for i in range(limit): # A row at a time
        rows = []
        for value in ipo_table_data[i].find_all('td'):
            # removes \n, \r, \t
            newval = re.sub('(\n)|(\r)|(\t)','',value.text)
            rows.append(newval)
        all_data.append(rows)
    
    symbol_lst = []
    for i in range(len(all_data)):
        symbol = all_data[i][2]
        symbol_lst.append(symbol)

    ipo_df = pd.DataFrame(data=all_data,columns=headings)
    return ipo_df


'''2nd data source___web_scraper'''
# get the historical s&p 500 data for past 100 days
def get_sp500(loops=None):    
    url = requests.get('https://finance.yahoo.com/quote/%5EGSPC/history?p=%5EGSPC&').text 
    soup = BeautifulSoup(url, 'lxml')
    
    spx_table = soup.find('div',attrs={'Pb(10px) Ovx(a) W(100%)'})
    spx_table_data = spx_table.find_all('table')
    
    spx_data = []
    rows  = spx_table_data[0].find_all('tr')

    for tr in rows:
        cols = tr.find_all('td')
        if len(cols) == 7:
            for td in cols:
                text = td.find(text=True)
                spx_data.append(text)
    if loops != None:
        spx_data = spx_data[0:loops*7]
    
#     calculate percent change in spx price
    percentChange = []
    for i in range(len(spx_data)):
        if int(i+1)%7 == 6 and i+7 <= len(spx_data):
            change = float(spx_data[i].replace(',',''))/float(spx_data[i+7].replace(',','')) - 1
#             percent = '{:.4%}'.format(round(change,2))
            percentChange.append(change)
        elif int(i+1)%7 == 6 and i+7 > len(spx_data):
            change = 0
            percentChange.append(change)
    
    df = pd.DataFrame(np.array(spx_data).reshape(int(len(spx_data)/7),7))
    df.columns=['date','open','high','low','close','Aclose','volume']
    df['date']= pd.to_datetime(df['date'])
    df['percentChange'] = percentChange
    return df

# get ceo info with symbol
def get_ceo_info(symbol):
    url = requests.get('https://finance.yahoo.com/quote/'+symbol+'/profile').text
    soup = BeautifulSoup(url, 'lxml')
    
    executive_table = soup.find('div',attrs={'W(100%)'})
    executive_table_data = executive_table.find_all('table')
    
    exec_data = []
    rows  = executive_table_data[0].find_all('tr')
    for tr in rows:
        cols = tr.find_all('td')
        if len(cols) == 5:
            for td in cols:
                text = td.text
                exec_data.append(text)
    ceo_data = exec_data[0:5]
    return ceo_data

def get_ceo_table(lst):
    ceo_info = []
    for i in lst:
        try:
            ceo = get_ceo_info(i)
            ceo_info.append(ceo)
        except:
            ceo = ['N/A','N/A','N/A','N/A','N/A']
            ceo_info.append(ceo)
    ceo_df=pd.DataFrame(ceo_info,columns=['name','title','pay','exercised','born'])
    return ceo_df


'''3rd data source___api_crawler'''
def get_3m_close(symbol):
    sandbox_url = 'https://sandbox.iexapis.com/stable'
    ttoken = 'Tpk_e610491432ef4f61bb208c27187de069'
    endpoint2 = '/stock/'+symbol+'/chart/'+'3m'
    try:
        historical_json = requests.get(sandbox_url+ endpoint2 +'?token='+ttoken).json()
        lst = []
        for i in range(len(historical_json)):
            symbol = historical_json[i]['symbol']
            date = historical_json[i]['date']
            close = historical_json[i]['close']
            lst.append([symbol,date,close])
    except:
        print('api requests exceed limtis, please try again in an hour')
    return lst

def get_close_info(symbol_list):
    lst = []
    for sym in symbol_list:
        close_by_symbol = get_3m_close(sym)
        for i in range(len(close_by_symbol)):
            row = close_by_symbol[i]
            lst.append(row)
    df = pd.DataFrame(lst, columns = ['symbol','date','close'])
    return df

def get_stock_stats(symbol):
    sandbox_url = 'https://sandbox.iexapis.com/stable'
    ttoken = 'Tpk_e610491432ef4f61bb208c27187de069'    
    endpoint1 = '/stock/'+symbol+'/advanced-stats'
    stats_json = requests.get(sandbox_url+ endpoint1 +'?token='+ttoken).json()
    marketcap = stats_json['marketcap']
    employee = stats_json['employees']
    revenue = stats_json['revenue']
    grossProfit = stats_json['grossProfit']
    deRatio = stats_json['debtToEquity']
    peRatio = stats_json['peRatio']
    EBITDA = stats_json['EBITDA']
    beta = stats_json['beta']
    return [symbol, marketcap, employee, revenue, grossProfit, deRatio, peRatio, EBITDA, beta]

def get_stock_info(symbol_list):
    stock_info = {'symbol':[], 'marketcap':[], 'employee':[], 'revenue':[], 'grossProfit':[], 'deRatio':[], 'peRatio':[], 'EBITDA':[], 'beta':[]}
    for sym in symbol_list:
        stock_by_symbol = get_stock_stats(sym)
        stock_info['symbol'].append(stock_by_symbol[0])
        stock_info['marketcap'].append(stock_by_symbol[1])
        stock_info['employee'].append(stock_by_symbol[2])
        stock_info['revenue'].append(stock_by_symbol[3])
        stock_info['grossProfit'].append(stock_by_symbol[4])
        stock_info['deRatio'].append(stock_by_symbol[5])
        stock_info['peRatio'].append(stock_by_symbol[6])
        stock_info['EBITDA'].append(stock_by_symbol[7])
        stock_info['beta'].append(stock_by_symbol[8])       
    stock_info_df = pd.DataFrame(stock_info)
    return stock_info_df



'''get three dataframes'''
def grab_data_remote():

    #get a table of most recent ipo from ipoScoop
    '''https://www.iposcoop.com/ipos-recently-filed/'''
    ipo_info = get_ipo_since2019(limit=725)
    
    #get historical s&p 500 data/ceo data for ipo stocks from Yahoo Finance
    '''https://finance.yahoo.com/quote/%5EGSPC/history?p=%5EGSPC&'''
    sp500_historical = get_sp500()
    
    symbol_lst = ['SNOW','U','UBER','LYFT','ZM']
    # ceo_info = get_ceo_table(symbol_lst)
    
    #get closing price for selected companies
    '''https://sandbox.iexapis.com/stable'''
    top_ipo_closing = get_close_info(symbol_lst)
    
    return [ipo_info, sp500_historical, top_ipo_closing]


'''get data from local csv files'''
def grab_data_local():
    ipo_info = pd.read_csv('data/ipo_info.csv')
    sp500_historical = pd.read_csv('data/sp500_historical.csv')
    top_ipo_closing = pd.read_csv('data/top_ipo_closing.csv')
    return [ipo_info,sp500_historical,top_ipo_closing]

def convert_to_csv(data):
    '''save scrpaed data as csv files'''
    data[0].to_csv('data/ipo_info.csv',index=False)
    data[1].to_csv('data/sp500_historical.csv',index=False)
    data[2].to_csv('data/top_ipo_closing.csv',index=False)
    print('Successful! 3 csv file have been stored in the sub folder')

def grading_helper():
    ipo_info = get_ipo_since2019(limit=3)
    ipo_info.to_csv('data/grade1.csv',index=False)
    sp500_historical = get_sp500(loops=3)
    sp500_historical.to_csv('data/grade2.csv',index=False)
    top_ipo_closing = get_close_info(['SNOW'])
    top_ipo_closing.to_csv('data/grade3.csv',index=False)
    print('example csv for grading stored')


def main():
    parser = argparse.ArgumentParser(description="IPO data")
    parser.add_argument('--source', choices=['local', 'remote'], help='choose how to get data')
    parser.add_argument('--grade', required=False, action='store_true', help='help grading easier')
    args = parser.parse_args()

    source = args.source
    if source == "local":
        try:
            data = grab_data_local()
            convert_to_csv(data)
        except:
            print('no local files to get data from')
    elif source == "remote":
        print('please wait a few seconds to grab the data')
        data = grab_data_remote()
        convert_to_csv(data)
    
    grade = args.grade
    if grade:
        print('This should not take long :)')
        grading_helper()


if __name__ == '__main__':
    main()