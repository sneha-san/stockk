import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import cufflinks as cf
import datetime
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from dotenv import load_dotenv
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews
import pandas_ta as ta
from newsdata import get_news
import os
from get_sock_data import get_ticker, get_indian_stock, get_usa_stock, get_ticker_name
from stock_prediction import get_prediction, get_charts

load_dotenv(".env")

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_KEY")
# select country
country = st.sidebar.radio('Country', ['USA', 'India'],horizontal=True)
tickerSymbol = st.sidebar.selectbox("Select Stock", get_ticker(country))

start_date = st.sidebar.date_input("Start date", datetime.date.today() - datetime.timedelta(days=30),
                                       max_value=datetime.date.today())
end_date = st.sidebar.date_input("End date", datetime.date.today(),min_value=start_date, max_value=datetime.date.today())

if country == 'India':
    indianTickerData = get_indian_stock(tickerSymbol,startDate=start_date,endDate=end_date)
    name = (get_ticker_name(tickerSymbol))
    st.header(name)
    fig = px.line(indianTickerData, x=indianTickerData.index, y=indianTickerData['Last Price'], title=f'{tickerSymbol}'                                                                                                f' Stock Price')
    st.plotly_chart(fig)
    st.header('**Bollinger Bands**')
    qf=cf.QuantFig(indianTickerData,title='First Quant Figure',legend='top',name='GS')
    qf.add_bollinger_bands()
    fig = qf.iplot(asFigure=True)
    st.plotly_chart(fig)

    pricing_data, news, tech_indicator, predicted_stock = st.tabs(["Pricing Data","News", "Technical Analysis",
                                                                   "Predicted Stock Price"])

    with pricing_data:
        with pricing_data:
            st.header('Pricing Movements')
            data2 = indianTickerData
            data2['% Change'] = indianTickerData['Last Price'] / indianTickerData['Last Price'].shift(1) - 1
            data2.dropna(inplace=True)
            st.write(data2)
            annual_return = data2['% Change'].mean() * 252 * 100
            st.write('Annual return : ', annual_return, '%')
            stdev = np.std(data2['% Change']) * np.sqrt(252) * 100
            st.write('Standard Deviation : ', stdev, '%')
            st.write('Risk Adj return : ', annual_return / stdev)

    with news:
        st.header('News')
        response = get_news(category="business", language="en", query=get_ticker_name(tickerSymbol), country="in")
        col1, col2 = st.columns(2)
        for article in response['results']:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(article['title'])
                st.write(article['description'])
                st.write(article['link'])
            with col2:
                if article['image_url'] is not None:
                    st.image(article['image_url'])

    with tech_indicator:
        st.subheader('Technical Analysis')
        df= pd.DataFrame()
        ind_list= df.ta.indicators(as_list=True)
        ind_list = [indicator for indicator in ind_list if 'above' not in indicator and 'above_value' not in indicator]
        technical_indicator= st.selectbox('Select Technical Indicator', options=ind_list)
        method= technical_indicator
        indicator= pd.DataFrame(getattr(ta, method)(low=indianTickerData['Low Price'],
                                                    high=indianTickerData['High Price'],
                                                    close=indianTickerData['Close Price'],
                                                    volume=indianTickerData['Total Traded Quantity']))
        indicator['Close Price']= indianTickerData['Close Price']
        fig_ind= px.line(indicator)
        st.plotly_chart(fig_ind)
        st.write(indicator)

    with predicted_stock:
        st.subheader('Predicted Stock Price')
        fig1, fig2, forecast = get_charts(indianTickerData)
        st.dataframe(forecast)
        st.pyplot(fig1)
        st.pyplot(fig2)


else:
    tickerData, tickerData2 = get_usa_stock(tickerSymbol, start_date, end_date)
    show_ticker_info = st.sidebar.checkbox("Show Ticker Information")
    string_name = tickerData2.info['longName']
    st.header('**%s**' % string_name)

    # Ticker information
    if show_ticker_info:
        string_summary = tickerData2.info['longBusinessSummary']
        st.info(string_summary)

    fig= px.line(tickerData, x=tickerData.index, y=tickerData['Adj Close'], title=f'{tickerSymbol} Stock Price')
    st.plotly_chart(fig)

    st.header('**Bollinger Bands**')
    qf=cf.QuantFig(tickerData,title='First Quant Figure',legend='top',name='GS')
    qf.add_bollinger_bands()
    fig = qf.iplot(asFigure=True)
    st.plotly_chart(fig)

    pricing_data, fundamental_data, news, tech_indicator, predicted_stock = st.tabs(["Pricing Data",
                                                                                     "Fundamental Data",
                                                                                     "News",
                                                                                     "Technical Analysis",
                                                                                     "Predicted Stock Price"])

    with pricing_data:
        st.header('Pricing Movements')
        data2= tickerData
        data2['% Change'] = tickerData['Adj Close']/tickerData['Adj Close'].shift(1)-1
        data2.dropna(inplace=True)
        st.write(data2)
        annual_return = data2['% Change'].mean() * 252 * 100
        st.write('Annual return : ', annual_return, '%')
        stdev = np.std(data2['% Change']) * np.sqrt(252) * 100
        st.write('Standard Deviation : ', stdev, '%')
        st.write('Risk Adj return : ', annual_return/stdev)

    with fundamental_data:
        key = ALPHA_VANTAGE_API_KEY
        fd = FundamentalData(key, output_format='pandas')
        st.subheader('Balance Sheet')
        balance_sheet = fd.get_balance_sheet_annual(tickerSymbol)[0]
        bs= balance_sheet.T[2:]
        bs.columns= list(balance_sheet.T.iloc[0])
        st.write(bs)
        st.subheader('Income Statement')
        income_statement = fd.get_income_statement_annual(tickerSymbol)[0]
        ist= income_statement.T[2:]
        ist.columns= list(income_statement.T.iloc[0])
        st.write(ist)
        st.subheader('Cash Flow Statement')
        cash_flow = fd.get_cash_flow_annual(tickerSymbol)[0]
        cf= cash_flow.T[2:]
        cf.columns= list(cash_flow.T.iloc[0])
        st.write(cf)

    with news:
        st.header(f'News of {tickerSymbol}')
        sn= StockNews(tickerSymbol, save_news=False)
        df_news= sn.read_rss()
        for i in range(10):
            st.subheader(df_news['title'][i])
            st.write(df_news['published'][i])
            st.write(df_news['summary'][i])
            title_sentiment = df_news['sentiment_title'][i]
            st.write(f'Title Sentiment : {title_sentiment}')
            news_sentiment = df_news['sentiment_summary'][i]
            st.write(f'News Sentiment : {news_sentiment}')

    with tech_indicator:
        st.subheader('Technical Analysis')
        df = pd.DataFrame()
        ind_list = df.ta.indicators(as_list=True)
        ind_list = [indicator for indicator in ind_list if 'above' not in indicator and 'above_value' not in indicator]
        technical_indicator = st.selectbox('Select Technical Indicator', options=ind_list)
        method = technical_indicator
        indicator = pd.DataFrame(getattr(ta, method)(low=tickerData['Low'], high=tickerData['High'], close=tickerData['Close'], volume=tickerData['Volume']))
        indicator['Close']= tickerData['Close']
        fig_ind = px.line(indicator)
        st.plotly_chart(fig_ind)
        st.write(indicator)

    with predicted_stock:
        st.subheader('Predicted Stock Price')
        # df= get_prediction(tickerData)
        # create charts

        fig1,fig2,forecast = get_charts(tickerData)
        st.dataframe(forecast)
        st.pyplot(fig1)
        st.pyplot(fig2)

