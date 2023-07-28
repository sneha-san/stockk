import pandas as pd
import yfinance as yf
from NSEDownload import stocks


def get_ticker(country):
    if country == 'India':
        df = pd.read_csv('data/nse_stocks.csv')
        return df['SYMBOL'].tolist()
    elif country == 'USA':
        df = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/s-and-p-500-companies/master/data/constituents_symbols.txt')
        return df

def get_ticker_name(tickerSymbol):
    df = pd.read_csv('data/nse_stocks.csv')
    return df[df['SYMBOL'] == tickerSymbol]['NAME OF COMPANY'].tolist()[0]

def get_indian_stock(tickerSymbol,startDate,endDate):
    df = stocks.get_data(stock_symbol=tickerSymbol, start_date=str(startDate), end_date=str(endDate))
    return df




def get_usa_stock(tickerSymbol,start_date,end_date):
    tickerData = yf.download(tickerSymbol, period='1d', start=start_date, end=end_date)  # Get ticker data
    tickerData2 = yf.Ticker(tickerSymbol)
    return tickerData,tickerData2
