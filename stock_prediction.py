import pandas as pd
from prophet import Prophet
from datetime import datetime, timezone


def remove_timezone(dt):
    # HERE `dt` is a python datetime
    # object that used .replace() method
    return dt.replace(tzinfo=None)
def get_closing_price(df):
    df = df.reset_index()
    if 'Last Price' in df.columns:
        df = df[['Date', 'Last Price']]
        # print(df['Date'].values[0].to_datetime())
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%dT%H:%M:%S.%fZ',dayfirst=True)
        df['Date'] = df['Date'].apply(remove_timezone)
        df['Date'] = df['Date'].dt.date
        df = df.rename(columns={'Date': 'ds', 'Last Price': 'y'})
    else:
        df = df[['Date', 'Adj Close']]
        df = df.rename(columns={'Date': 'ds', 'Adj Close': 'y'})
    return df

def get_prediction(df):
    df = get_closing_price(df)
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=90)
    forecast = m.predict(future)
    # forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    # forecast = forecast.rename(columns={'ds': 'Date', 'yhat': 'Predicted Close Price'})
    # forecast['Date'] = forecast['Date'].dt.date
    # forecast = forecast.set_index('Date')
    return forecast,m

def get_charts(df):
    forecast,m = get_prediction(df)
    fig1 = m.plot(forecast)
    fig2 = m.plot_components(forecast)
    return fig1, fig2,forecast