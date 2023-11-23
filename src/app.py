import requests
from requests import Session
import pandas as pd
import cufflinks as cf
import yfinance as yf
import datetime
from flask import Flask, request, render_template
import plotly.graph_objects as go
import cufflinks as cf
import asyncio
import aiohttp
import concurrent.futures
import time

cf.go_offline()

s = Session()


# df = yf.download("AAPL", start = "2021-01-01", end = "2021-05-30")
# print(df)
dark_palette = {}
dark_palette["bg_color"] = "#2e2e2e"
dark_palette["plot_bg_color"] = "#2e2e2e"
dark_palette["grid_color"] = "#595656"
dark_palette["text_color"] = "#ffffff"
dark_palette["dark_candle"] = "#226287"
dark_palette["light_candle"] = "#a6a4a4"
dark_palette["volume_color"] = "#5c285b"
dark_palette["border_color"] = "#ffffff"
dark_palette["color_1"] = "#5c285b"
dark_palette["color_2"] = "#802c62"
dark_palette["color_3"] = "#a33262"
dark_palette["color_4"] = "#c43d5c"
dark_palette["color_5"] = "#de4f51"
dark_palette["color_6"] = "#f26841"
dark_palette["color_7"] = "#fd862b"
dark_palette["color_8"] = "#ffa600"
dark_palette["color_9"] = "#3366d6"



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
        # Create a sample DataFrame (replace this with your data)
        # Default values or user-selected options from the form
        default_ticker = "BTCUSDT"
        default_interval = '1h'
        default_bars_back = 200

        df = get_data(ticker= default_ticker, session = s, interval = default_interval,
                    bars_back= default_bars_back)
        
        # Create a QuantFig chart
        qf = cf.QuantFig(df, title=f"{default_ticker}", name=default_ticker)

        # Add EMA with a specific color for the dark theme
        qf.add_ema(periods=36, column='close', color='#1E90FF')  # Use a shade of blue

        # Convert the Cufflinks chart to a Plotly figure
        figure = qf.figure()

        # Convert the Plotly figure to an HTML div
        chart_div = go.Figure(figure).to_html(full_html=False)

        return render_template('chart.html', chart_div=chart_div, selected_ticker = default_ticker, 
                               selected_bars_back = default_bars_back, selected_interval = default_interval)
    
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

        df = get_basket_data(basket= selected_ticker, session = s, interval = selected_interval,
                    bars_back= selected_bars_back)
        

        # Create a QuantFig chart
        # Create a QuantFig chart
        qf = cf.QuantFig(df, title=f"{selected_ticker}", name=selected_ticker)

        # Add EMA with a specific color for the dark theme
        qf.add_ema(periods=36, column='close', color='#1E90FF')  # Use a shade of blue

        # Convert the Cufflinks chart to a Plotly figure
        figure = qf.figure()


        # Convert the Plotly figure to an HTML div
        chart_div = go.Figure(figure).to_html(full_html=False)



        return render_template('chart.html', chart_div=chart_div, selected_ticker = selected_ticker, 
                               selected_bars_back = selected_bars_back, selected_interval = selected_interval)


@app.route('/basket', methods=["GET", "POST"])
def basket():
    
    if request.method == "GET":
        # Create a sample DataFrame (replace this with your data)
        # Default values or user-selected options from the form
        default_basket = "L1"
        default_counter = "BTCUSDT"
        default_interval = '1h'
        default_bars_back = 500


        df = get_basket_data(basket= default_basket, counter = default_counter, session = s, interval = default_interval,
                    bars_back= default_bars_back)
        

        # Create a QuantFig chart
        # Create a QuantFig chart
        qf = cf.QuantFig(df, title=f"{default_basket} / {default_counter}", name=default_basket)

        # Add EMA with a specific color for the dark theme
        qf.add_ema(periods=36, column='close', color='#1E90FF')  # Use a shade of blue

        # Convert the Cufflinks chart to a Plotly figure
        figure = qf.figure()

        # Convert the Plotly figure to an HTML div
        chart_div = go.Figure(figure).to_html(full_html=False)

        return render_template('basket.html', chart_div=chart_div, selected_basket = default_basket, 
                               selected_counter = default_counter, selected_bars_back = default_bars_back)
    
    else:

        # Create a sample DataFrame (replace this with your data)
        # Default values or user-selected options from the form
        t1 = int(time.time())*1000
        default_basket = "L1"
        default_counter = "BTCUSDT"
        default_interval = '1h'
        default_bars_back = 500

        # Get user-selected options from the form
        selected_basket = request.form.get('basket', default_basket)
        selected_counter = request.form.get('counter', default_counter)
        selected_interval = request.form.get('interval', default_interval)
        selected_bars_back = int(request.form.get('bars_back', default_bars_back))

        df = get_basket_data(basket= selected_basket, counter = selected_counter, session = s, interval = selected_interval,
                    bars_back= selected_bars_back)
        

        # Create a QuantFig chart
        # Create a QuantFig chart
        qf = cf.QuantFig(df, title=f"{selected_basket} / {selected_counter}", name=selected_basket)

        # Add EMA with a specific color for the dark theme
        qf.add_ema(periods=36, column='close', color='#1E90FF')  # Use a shade of blue

        # Convert the Cufflinks chart to a Plotly figure
        figure = qf.figure()


        # Convert the Plotly figure to an HTML div
        chart_div = go.Figure(figure).to_html(full_html=False)

        # Convert the Plotly figure to an HTML div
        chart_div = go.Figure(figure).to_html(full_html=False)

        t2 = int(time.time())*1000
        print(f"TIME: {t2-t1}ms")


        return render_template('basket.html', chart_div=chart_div, selected_basket = selected_basket, 
                               selected_counter = selected_counter, selected_bars_back = selected_bars_back)



if __name__ == "__main__":
    app.run(debug=True)