import requests
from requests import Session
import pandas as pd
import cufflinks as cf
import datetime
from flask import Flask, request, render_template
import plotly.graph_objects as go
import cufflinks as cf
import concurrent.futures
import time
from classes import *



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


def get_data(ticker: str, interval: str, session: Session, bars_back: int = 200) -> pd.DataFrame:
    """ This function will return a Pandas Dataframe
        Containing the OHLC data of some ticker
        
        pre: ticker
        post: pd.DataFrame
        
        wss://stream.binance.com:9443/stream?streams=iqusdt@kline_1s
        """
    
    assert ticker in get_existing_tickers()
    if bars_back > 1500:
        bars_back = 1500

    # get data
    r = session.get(f"https://api.binance.com/api/v3/klines?symbol={ticker}&interval={interval}&limit={bars_back}")
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
        row_data['open'] = float(row[1])
        row_data['high'] = float(row[2])
        row_data['low'] = float(row[3])
        row_data['close'] = float(row[4])

        df_data.append(row_data)

    df = pd.DataFrame(df_data)
    df.set_index('time', inplace=True)

    return df






def get_basket_data(basket: str, counter: str, interval: str, session: Session, bars_back: int = 500) -> pd.DataFrame:
    """ This function will return a Pandas Dataframe
        Containing the OHLC data of a basket ticker
        
        pre: basket
        post: pd.DataFrame
        
        wss://stream.binance.com:9443/stream?streams=iqusdt@kline_1s
        """
    
    sectors = {"L1": ["SOLUSDT", "ETHUSDT", "BNBUSDT", "APTUSDT"],
               "DEFI": ["LINKUSDT", "SNXUSDT", "LDOUSDT", "RUNEUSDT"],
               "AI": ["FETUSDT", "RLCUSDT", "OCEANUSDT"]}
    
    assert basket in sectors.keys()
    assert counter in get_existing_tickers()

    # get data
    # Use concurrent.futures for parallel processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        data = {ticker: executor.submit(get_data, ticker, interval, session, bars_back) for ticker in sectors[basket]}
        data[counter] = executor.submit(get_data, counter, interval, session, bars_back)

    # Wait for all tasks to complete and retrieve the results
    for ticker, result in data.items():
        data[ticker] = result.result()

    # start with first tickers dataframe
    first_in_sector = sectors[basket][0]
    combined_df = pd.DataFrame(1, columns=data[first_in_sector].columns, index=data[first_in_sector].index)
    # print(combined_df)


    # fill in the combined df
    for ticker, df in data.items():

        if ticker != counter:

            # Apply the formula to each column in the combined DataFrame
            combined_df['open'] *= df['open']
            combined_df['high'] *= df['high']
            combined_df['low'] *= df['low']
            combined_df['close'] *= df['close']

            # print(f"After {ticker}: ", combined_df)



    # Take the (1/len(data))th root of each column to complete the formula
    combined_df = combined_df ** (1 / len(sectors[basket]))


    # then divide by the counter asset
    combined_df['open'] /= data[counter]['open']
    combined_df['high'] /= data[counter]['high']
    combined_df['low'] /= data[counter]['low']
    combined_df['close'] /= data[counter]['close']

    return combined_df

# df = get_basket_data("L1", "BTCUSDT", "15m")
# print(df)



def plot_chart(df: pd.DataFrame):
    """Plots the candlestick chart"""

    cf.go_offline()
    qf = cf.QuantFig(df, title="Bitcoin prices", name='BTCUSDT')
    qf.iplot()


app = Flask(__name__)


@app.route('/', methods=["GET"])
def index():
    

    return render_template('index.html')

@app.route('/chart', methods=["GET", "POST"])
def chart():
    if request.method == "GET":

        default_ticker = "BTCUSDT"
        default_interval = '1h'
        default_bars_back = 200

        chart = SimpleChart(default_ticker, default_interval, default_bars_back)
        
        # Obtain the dataframe
        chart.get_data()

        # Get the chart html        
        chart.get_chart_html()


        return render_template('chart.html', chart_div=chart.html, selected_ticker = chart.ticker, 
                               selected_bars_back = chart.bars_back, selected_interval = chart.interval)
    
    else:

        # Create a sample DataFrame (replace this with your data)
        # Default values or user-selected options from the form
        default_ticker = "BTCUSDT"
        default_interval = '1h'
        default_bars_back = 200

        # Get user-selected options from the form
        selected_ticker = request.form.get('ticker', default_ticker)
        selected_interval = request.form.get('interval', default_interval)
        selected_bars_back = int(request.form.get('bars_back', default_bars_back))

        chart = SimpleChart(selected_ticker, selected_interval, selected_bars_back)
        
        # Obtain the dataframe
        chart.get_data()

        # Get the chart html        
        chart.get_chart_html()


        return render_template('chart.html', chart_div=chart.html, selected_ticker = chart.ticker, 
                               selected_bars_back = chart.bars_back, selected_interval = chart.interval)


@app.route('/basket', methods=["GET", "POST"])
def basket():
    
    if request.method == "GET":
        # Create a sample DataFrame (replace this with your data)
        # Default values or user-selected options from the form
        default_basket = "L1"
        default_counter = "BTCUSDT"
        default_interval = '1h'
        default_bars_back = 200

        # Initialize chart
        chart = SimpleBasketChart(default_basket, default_counter, default_interval, default_bars_back)

        # Get basket chart data
        chart.get_basket_data()
        
        # Get chart html
        chart.get_chart_html()

        return render_template('basket.html', chart_div=chart.html, selected_basket = chart.basket, 
                               selected_counter = chart.counter, selected_bars_back = chart.bars_back)
    
    else:

        # Create a sample DataFrame (replace this with your data)
        # Default values or user-selected options from the form
        t1 = int(time.time())*1000

        default_basket = "L1"
        default_counter = "BTCUSDT"
        default_interval = '1h'
        default_bars_back = 200

        # Get user-selected options from the form
        selected_basket = request.form.get('basket', default_basket)
        selected_counter = request.form.get('counter', default_counter)
        selected_interval = request.form.get('interval', default_interval)
        selected_bars_back = int(request.form.get('bars_back', default_bars_back))

        # Initialize chart
        chart = SimpleBasketChart(selected_basket, selected_counter, selected_interval, selected_bars_back)

        # Get basket chart data
        chart.get_basket_data()
        
        # Get chart html
        chart.get_chart_html()

        t2 = int(time.time())*1000
        print(f"TIME: {t2-t1}ms")


        return render_template('basket.html', chart_div=chart.html, selected_basket = chart.basket, 
                               selected_counter = chart.counter, selected_bars_back = chart.bars_back)
    


if __name__ == "__main__":
    app.run(debug=True)