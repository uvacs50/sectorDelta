import requests
import pandas as pd
import datetime
import plotly.graph_objects as go
import cufflinks as cf
import concurrent.futures
cf.go_offline()

class SimpleChart:

    def __init__(self, ticker: str, interval: str, bars_back: int = 200) -> None:
        self.ticker = ticker
        self.interval = interval
        self.bars_back = bars_back
        self.session = requests.Session()

    def get_existing_tickers(self) -> list[str]:
        """This will return a list of all tickers
        that are found on binance
        
        post: list[str]"""

        # Make request
        r = self.session.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
        data = r.json()

        # Form the list
        all_tickers = [idx["symbol"] for idx in data["symbols"]]

        return all_tickers


    def get_data(self) -> pd.DataFrame:
        """ This function will store a Pandas Dataframe
            Containing the OHLC data of some ticker
            in the .df attribute
            
            pre: ticker
            post: pd.DataFrame
            
            wss://stream.binance.com:9443/stream?streams=iqusdt@kline_1s
            """
        
        assert self.ticker in self.get_existing_tickers()
        if self.bars_back > 1500:
            self.bars_back = 1500

        # get data
        r = self.session.get(f"https://api.binance.com/api/v3/klines?symbol={self.ticker}&interval={self.interval}&limit={self.bars_back}")
        data = r.json()


        # extract necessary data
        data = [sub[0:5] for sub in data]
        # print(data)
        
        #get correct timestamp
        for candle in data:

            _time = int(candle[0]) // 1000
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

        self.df = df
    

    def get_chart_html(self):
        """This function will store the html code for the chart
            In the .html attribute"""

    # Create a QuantFig chart
        qf = cf.QuantFig(self.df, title=f"{self.ticker}", name=self.ticker)

        # Add EMA with a specific color for the dark theme
        qf.add_ema(periods=36, column='close', color='#1E90FF')  # Use a shade of blue

        # Convert the Cufflinks chart to a Plotly figure
        figure = qf.figure()

        # Convert the Plotly figure to an HTML div
        chart_div = go.Figure(figure).to_html(full_html=False)   

        self.html = chart_div




class SimpleBasketChart:

    def __init__(self, basket: str, counter: str, interval: str, bars_back: int = 200) -> None:
        self.basket = basket
        self.counter = counter
        self.interval = interval
        self.bars_back = bars_back
        self.session = requests.Session()

    def get_existing_tickers(self) -> list[str]:
        """This will return a list of all tickers
        that are found on binance
        
        post: list[str]"""

        # Make request
        r = self.session.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
        data = r.json()

        # Form the list
        all_tickers = [idx["symbol"] for idx in data["symbols"]]

        return all_tickers
    
    def get_data(self, ticker) -> pd.DataFrame:
        """ This function will return a Pandas Dataframe
            Containing the OHLC data of some ticker
            
            pre: ticker
            post: pd.DataFrame
            
            wss://stream.binance.com:9443/stream?streams=iqusdt@kline_1s
            """
        
        assert ticker in self.get_existing_tickers()
        if self.bars_back > 1500:
            self.bars_back = 1500

        # get data
        r = self.session.get(f"https://api.binance.com/api/v3/klines?symbol={ticker}&interval={self.interval}&limit={self.bars_back}")
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
    
    def get_basket_data(self) -> None:
        """ This function will return a Pandas Dataframe
        Containing the OHLC data of a basket ticker
        and store it in the .df attribute
        
        pre: basket
        post: pd.DataFrame
        """
    
        sectors = {"L1": ["SOLUSDT", "ETHUSDT", "BNBUSDT", "APTUSDT"],
                "DEFI": ["LINKUSDT", "SNXUSDT", "LDOUSDT", "RUNEUSDT"],
                "AI": ["FETUSDT", "RLCUSDT", "OCEANUSDT"]}
        
        assert self.basket in sectors.keys()
        assert self.counter in self.get_existing_tickers()

        # get data
        # Use concurrent.futures for parallel processing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            data = {ticker: executor.submit(self.get_data, ticker) for ticker in sectors[self.basket]}
            data[self.counter] = executor.submit(self.get_data, self.counter)

        # Wait for all tasks to complete and retrieve the results
        for ticker, result in data.items():
            data[ticker] = result.result()

        # start with first tickers dataframe
        first_in_sector = sectors[self.basket][0]
        combined_df = pd.DataFrame(1, columns=data[first_in_sector].columns, index=data[first_in_sector].index)
        # print(combined_df)


        # fill in the combined df
        for ticker, df in data.items():

            if ticker != self.counter:

                # Apply the formula to each column in the combined DataFrame
                combined_df['open'] *= df['open']
                combined_df['high'] *= df['high']
                combined_df['low'] *= df['low']
                combined_df['close'] *= df['close']

                # print(f"After {ticker}: ", combined_df)



        # Take the (1/len(data))th root of each column to complete the formula
        combined_df = combined_df ** (1 / len(sectors[self.basket]))


        # then divide by the counter asset
        combined_df['open'] /= data[self.counter]['open']
        combined_df['high'] /= data[self.counter]['high']
        combined_df['low'] /= data[self.counter]['low']
        combined_df['close'] /= data[self.counter]['close']


        self.df = combined_df


    def get_chart_html(self) -> None:
        """This function will store the html code for the chart 
            in the .html attribute"""

        qf = cf.QuantFig(self.df, title=f"{self.basket} / {self.counter}", name=self.basket)

        # Add EMA with a specific color for the dark theme
        qf.add_ema(periods=36, column='close', color='#1E90FF')  # Use a shade of blue

        # Convert the Cufflinks chart to a Plotly figure
        figure = qf.figure()

        # Convert the Plotly figure to an HTML div
        chart_div = go.Figure(figure).to_html(full_html=False)

        self.html = chart_div



class ComplexBasketChart:
    
    def __init__(self, basket_nominator: str, basket_denominator: str, interval: str, bars_back: int = 200) -> None:
        self.basket_nominator = basket_nominator
        self.basket_denominator = basket_denominator
        self.interval = interval
        self.bars_back = bars_back
        self.session = requests.Session()

    def get_existing_tickers(self) -> list[str]:
        """This will return a list of all tickers
        that are found on binance
        
        post: list[str]"""

        # Make request
        r = self.session.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
        data = r.json()

        # Form the list
        all_tickers = [idx["symbol"] for idx in data["symbols"]]

        return all_tickers
    
    def get_data(self, ticker) -> pd.DataFrame:
        """ This function will return a Pandas Dataframe
            Containing the OHLC data of some ticker
            
            pre: ticker
            post: pd.DataFrame
            
            wss://stream.binance.com:9443/stream?streams=iqusdt@kline_1s
            """
        
        assert ticker in self.get_existing_tickers()
        if self.bars_back > 1500:
            self.bars_back = 1500

        # get data
        r = self.session.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={ticker}&interval={self.interval}&limit={self.bars_back}")
        data = r.json()


        # extract necessary data
        data = [sub[0:5] for sub in data]
        
        #get correct timestamp
        for candle in data:
            _time = int(candle[0]) // 1000
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
    
    def get_complex_basket_data(self) -> None:
        """ This function will return a Pandas Dataframe
        Containing the OHLC data of a basket ticker
        and store it in the .df attribute
        
        
        post: pd.DataFrame
        """
    
        sectors = {"L1": ["SOLUSDT", "ETHUSDT", "BNBUSDT", "APTUSDT"],
                "DEFI": ["LINKUSDT", "SNXUSDT", "LDOUSDT", "RUNEUSDT"],
                "AI": ["FETUSDT", "RLCUSDT", "OCEANUSDT"]}
        
        assert self.basket_nominator in sectors.keys()
        assert self.basket_denominator in sectors.keys()

        # get data
        # Use concurrent.futures for parallel processing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            data_nominator = {ticker: executor.submit(self.get_data, ticker) for ticker in sectors[self.basket_nominator]}
            data_denominator = {ticker: executor.submit(self.get_data, ticker) for ticker in sectors[self.basket_denominator]}
            

        # Wait for all tasks to complete and retrieve the results for nominator data
        for ticker, result in data_nominator.items():
            data_nominator[ticker] = result.result()

        # Wait for all tasks to complete and retrieve the results for denominator data
        for ticker, result in data_denominator.items():
            data_denominator[ticker] = result.result()

        # start with first tickers dataframe
        first_in_sector_nominator = sectors[self.basket_nominator][0]
        first_in_sector_denominator = sectors[self.basket_denominator][0]
        
        combined_df_nominator = pd.DataFrame(1, columns=data_nominator[first_in_sector_nominator].columns, index=data_nominator[first_in_sector_nominator].index)
        combined_df_denominator = pd.DataFrame(1, columns=data_denominator[first_in_sector_denominator].columns, index=data_denominator[first_in_sector_denominator].index)


        # fill in the combined df for the nominator
        for ticker, df in data_nominator.items():

            # Apply the formula to each column in the combined DataFrame
            combined_df_nominator['open'] *= df['open']
            combined_df_nominator['high'] *= df['high']
            combined_df_nominator['low'] *= df['low']
            combined_df_nominator['close'] *= df['close']

        # fill in the combined df for the denominator
        for ticker, df in data_denominator.items():

            # Apply the formula to each column in the combined DataFrame
            combined_df_denominator['open'] *= df['open']
            combined_df_denominator['high'] *= df['high']
            combined_df_denominator['low'] *= df['low']
            combined_df_denominator['close'] *= df['close']


        # Take the (1/len(data))th root of each column to complete the formula
        combined_df_nominator = combined_df_nominator ** (1 / len(sectors[self.basket_nominator]))
        combined_df_denominator = combined_df_denominator ** (1 / len(sectors[self.basket_denominator]))


        # then divide by the counter basket
        result_df = combined_df_nominator / combined_df_denominator

        self.df = result_df


    def get_chart_html(self) -> None:
        """This function will store the html code for the chart 
            in the .html attribute"""

        qf = cf.QuantFig(self.df, title=f"{self.basket_nominator} / {self.basket_denominator}", name=f"{self.basket_nominator}/{self.basket_denominator}")

        # Add EMA with a specific color for the dark theme
        qf.add_ema(periods=36, column='close', color='#1E90FF')  # Use a shade of blue

        # Convert the Cufflinks chart to a Plotly figure
        figure = qf.figure()

        # Convert the Plotly figure to an HTML div
        chart_div = go.Figure(figure).to_html(full_html=False)

        self.html = chart_div



class CustomBasketChart:
    
    def __init__(self, basket_nominator: list[str], basket_denominator: str, 
                  name: str, interval: str, bars_back: int = 200) -> None:
        
        self.basket_nominator = basket_nominator
        self.basket_denominator = basket_denominator
        self.name = name
        self.interval = interval
        self.bars_back = bars_back
        self.session = requests.Session()


    def get_existing_tickers(self) -> list[str]:
        """This will return a list of all tickers
        that are found on binance
        
        post: list[str]"""

        # Make request
        r = self.session.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
        data = r.json()

        # Form the list
        all_tickers = [idx["symbol"] for idx in data["symbols"]]

        return all_tickers
    
    def get_data(self, ticker) -> pd.DataFrame:
        """ This function will return a Pandas Dataframe
            Containing the OHLC data of some ticker
            
            pre: ticker
            post: pd.DataFrame
            
            wss://stream.binance.com:9443/stream?streams=iqusdt@kline_1s
            """
        
        assert ticker in self.get_existing_tickers()
        if self.bars_back > 1500:
            self.bars_back = 1500

        # get data
        r = self.session.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={ticker}&interval={self.interval}&limit={self.bars_back}")
        data = r.json()


        # extract necessary data
        data = [sub[0:5] for sub in data]
        
        #get correct timestamp
        for candle in data:
            _time = int(candle[0]) // 1000
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
    
    def get_complex_basket_data(self) -> None:
        """ This function will return a Pandas Dataframe
        Containing the OHLC data of a basket ticker
        and store it in the .df attribute
        
        
        post: pd.DataFrame
        """
    
        # get data
        # Use concurrent.futures for parallel processing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            data_nominator = {ticker: executor.submit(self.get_data, ticker) for ticker in self.basket_nominator}
            data_denominator = {ticker: executor.submit(self.get_data, ticker) for ticker in self.basket_denominator}
            

        # Wait for all tasks to complete and retrieve the results for nominator data
        for ticker, result in data_nominator.items():
            try: 
                data_nominator[ticker] = result.result()
            except Exception as e:
                print(f"Exception on {ticker}: {e}")
                print(f"Result: {result.result()}") 

        # Wait for all tasks to complete and retrieve the results for denominator data
        for ticker, result in data_denominator.items():
            data_denominator[ticker] = result.result()

        # start with first tickers dataframe
        first_in_sector_nominator = self.basket_nominator[0]
        first_in_sector_denominator = self.basket_denominator[0]
        
        combined_df_nominator = pd.DataFrame(1, columns=data_nominator[first_in_sector_nominator].columns, index=data_nominator[first_in_sector_nominator].index)
        combined_df_denominator = pd.DataFrame(1, columns=data_denominator[first_in_sector_denominator].columns, index=data_denominator[first_in_sector_denominator].index)


        # fill in the combined df for the nominator
        for ticker, df in data_nominator.items():

            if not isinstance(df, pd.DataFrame):
                print(f"Exception on {ticker} with df: {df} of type {type(df)}")

            # Apply the formula to each column in the combined DataFrame
            combined_df_nominator['open'] *= df['open']
            combined_df_nominator['high'] *= df['high']
            combined_df_nominator['low'] *= df['low']
            combined_df_nominator['close'] *= df['close']

        # fill in the combined df for the denominator
        for ticker, df in data_denominator.items():


            # Apply the formula to each column in the combined DataFrame
            combined_df_denominator['open'] *= df['open']
            combined_df_denominator['high'] *= df['high']
            combined_df_denominator['low'] *= df['low']
            combined_df_denominator['close'] *= df['close']


        # Take the (1/len(data))th root of each column to complete the formula
        combined_df_nominator = combined_df_nominator ** (1 / len(self.basket_nominator))
        combined_df_denominator = combined_df_denominator ** (1 / len(self.basket_denominator))


        # then divide by the counter basket
        result_df = combined_df_nominator / combined_df_denominator

        self.df = result_df


    def get_chart_html(self) -> None:
        """This function will store the html code for the chart 
            in the .html attribute"""

        qf = cf.QuantFig(self.df, title=f"{self.basket_nominator} / {self.basket_denominator}", name=f"{self.name}")

        # Add EMA with a specific color for the dark theme
        qf.add_ema(periods=36, column='close', color='#1E90FF')  # Use a shade of blue

        # Convert the Cufflinks chart to a Plotly figure
        figure = qf.figure()

        # Convert the Plotly figure to an HTML div
        chart_div = go.Figure(figure).to_html(full_html=False)

        self.html = chart_div


         