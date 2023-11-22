import requests
import pandas as pd
import cufflinks as cf
import yfinance as yf
import datetime

# df = yf.download("AAPL", start = "2021-01-01", end = "2021-05-30")
# print(df)


def get_existing_tickers() -> list[str]:
    """This will return a list of all tickers
    that are found on binance
    
    post: list[str]"""

    # Make request
    r = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
    data = r.json()

    # Form the list
    all_tickers = [idx["symbol"] for idx in data["symbols"]]

    return all_tickers


def get_data(ticker: str, interval: str, start: str = 0, end: str = 0) -> pd.DataFrame:
    """ This function will return a Pandas Dataframe
        Containing the OHLC data of some ticker
        
        pre: ticker
        post: pd.DataFrame
        
        wss://stream.binance.com:9443/stream?streams=iqusdt@kline_1s
        """
    
    assert ticker in get_existing_tickers()

    # get data
    r = requests.get(f"https://api.binance.com/api/v3/klines?symbol={ticker}&interval={interval}&limit=60")
    data = r.json()

    # extract necessary data
    data = [sub[0:5] for sub in data]
    
    #get correct timestamp
    for candle in data:
        _time = candle[0] // 1000
        utc_datetime = datetime.datetime.utcfromtimestamp(_time)
        candle[0] = utc_datetime.strftime('%Y-%m-%d %H:%M:%S')

    # create DF rows
    df_data = []
    for row in data:
        row_data = {}
        row_data['time'] = row[0]
        row_data['open'] = row[1]
        row_data['high'] = row[2]
        row_data['low'] = row[3]
        row_data['close'] = row[4]

        df_data.append(row_data)

    df = pd.DataFrame(df_data)
    df.set_index('time', inplace=True)

    return df
        

def plot_chart(df: pd.DataFrame):
    """Plots the candlestick chart"""
    
    cf.go_offline()
    qf = cf.QuantFig(df, title="Bitcoin prices", name='BTCUSDT')
    qf.iplot()



df = get_data("BTCUSDT", "15m")
plot_chart(df)







