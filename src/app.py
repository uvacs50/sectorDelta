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
    


@app.route('/complex-basket', methods=["GET", "POST"])
def complex_basket():
    
    if request.method == "GET":
        # Create a sample DataFrame (replace this with your data)
        # Default values or user-selected options from the form
        default_basket_nominator = "AI"
        default_basket_denominator = "L1"
        default_interval = '1h'
        default_bars_back = 200

        # Initialize chart
        chart = ComplexBasketChart(default_basket_nominator, default_basket_denominator, default_interval, default_bars_back)

        # Get basket chart data
        chart.get_complex_basket_data()
        
        # Get chart html
        chart.get_chart_html()

        return render_template('complex-basket.html', chart_div=chart.html, selected_basket_nominator = chart.basket_nominator, 
                               selected_basket_denominator = chart.basket_denominator, selected_bars_back = chart.bars_back)
    
    else:

        # Create a sample DataFrame (replace this with your data)
        # Default values or user-selected options from the form
        t1 = int(time.time())*1000

        default_basket_nominator = "AI"
        default_basket_denominator = "L1"
        default_interval = '1h'
        default_bars_back = 200

        # Get user-selected options from the form
        selected_basket_nominator = request.form.get('basket_nominator', default_basket_nominator)
        selected_basket_denominator = request.form.get('basket_denominator', default_basket_denominator)
        selected_interval = request.form.get('interval', default_interval)
        selected_bars_back = int(request.form.get('bars_back', default_bars_back))

        chart = ComplexBasketChart(selected_basket_nominator, selected_basket_denominator, selected_interval, selected_bars_back)

        # Get basket chart data
        chart.get_complex_basket_data()
        
        # Get chart html
        chart.get_chart_html()

        return render_template('complex-basket.html', chart_div=chart.html, selected_basket_nominator = chart.basket_nominator, 
                               selected_basket_denominator = chart.basket_denominator, selected_bars_back = chart.bars_back)
    

