import requests
from requests import Session
import pandas as pd
import cufflinks as cf
import datetime
from flask import Flask, request, render_template, redirect, session
from flask_session import Session
import jinja_partials
import plotly.graph_objects as go
import cufflinks as cf
import concurrent.futures
import os
import time
from classes import *
from db.models import *
import ast


def plot_chart(df: pd.DataFrame):
    """Plots the candlestick chart"""

    cf.go_offline()
    qf = cf.QuantFig(df, title="Bitcoin prices", name='BTCUSDT')
    qf.iplot()

def load():
    return render_template('loading.html')


app = Flask(__name__)
jinja_partials.register_extensions(app)
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


@app.route('/', methods=["GET"])
def index():

    return render_template('index.html')

@app.route('/register', methods = ["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template('register.html', message = None)
    
    else:

        username = request.form.get("username", None)
        password = request.form.get("password", None)
        confirmation = request.form.get("confirmation", None)

        if password != confirmation:
            return render_template('register.html', message = "Password unequal to confirmation")

        
        user = User(username= username, password = password)
        db.session.add(user)
        db.session.commit()

        return redirect('/login')
    


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template('/login.html', message = "Must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template('/login.html', message = "Must provide password")

        # Query database for username
        username = request.form.get("username")
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()


        # Ensure username exists and password is correct
        # if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        #     return apology("invalid username and/or password", 403)

        if not user or password != user.password:
            return render_template('/login.html', message = "Invalid username or password")

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/chart")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/chart")


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
    

@app.route('/loading', methods=["GET"])
def loading():

    loading_state = load()

    return loading_state



@app.route('/complex-basket2', methods=["GET", "POST"])
def complex_basket2():
    
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

        return render_template('complex-basket2.html', chart_div=chart.html, selected_basket_nominator = chart.basket_nominator, 
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

        return render_template('complex-basket2.html', chart_div=chart.html, selected_basket_nominator = chart.basket_nominator, 
                               selected_basket_denominator = chart.basket_denominator, selected_bars_back = chart.bars_back)
    

@app.route('/custom-basket', methods=["GET", "POST"])
def custom_basket():
    
    if request.method == "GET":
        

        return render_template('custom-basket.html')
    
    else:

        # Create a sample DataFrame (replace this with your data)
        # Default values or user-selected options from the form

        t1 = int(time.time())*1000


        # Get user-selected options from the form
        selected_basket_nominator = request.form.get('basket_nominator', "")
        selected_basket_denominator = request.form.get('basket_denominator', "")
        selected_name = request.form.get('name', "")

        selected_interval = request.form.get('interval', "")
        selected_bars_back = int(request.form.get('bars_back', ""))

        selected_basket_nominator = selected_basket_nominator.split(',')
        selected_basket_nominator = [s.replace(" ", "") + "USDT" for s in selected_basket_nominator]

        selected_basket_denominator = selected_basket_denominator.split(',')
        selected_basket_denominator = [s.replace(" ", "") + "USDT" for s in selected_basket_denominator]

        save = request.form.get("save_ticker", "")

        print(request.form.__dict__)

        print(selected_bars_back)
        print(selected_interval)

        if save == 'true':
            
            ticker = Ticker(creator = session["user_id"], name = selected_name,
                            nominator = str(selected_basket_nominator), denominator = str(selected_basket_denominator), bars_back = selected_bars_back, interval = selected_interval)
            print(ticker.__dict__)

            
            if ticker.name not in [t.name for t in Ticker.query.filter_by(creator=session["user_id"]).all()]:
                print("ADDING TICKER")
                db.session.add(ticker)
                db.session.commit()

            else: 
                print("TICKER ALREADY EXISTS")




        chart = CustomBasketChart(selected_basket_nominator, selected_basket_denominator, 
                                  selected_name, selected_interval, 
                                  selected_bars_back)

        # Get basket chart data
        chart.get_complex_basket_data()
        
        # Get chart html
        chart.get_chart_html()

        return render_template('custom-basket.html', chart_div=chart.html, selected_basket_nominator = chart.basket_nominator, 
                               selected_name = selected_name, selected_basket_denominator = chart.basket_denominator, 
                                selected_bars_back = chart.bars_back)
    


@app.route('/saved-tickers', methods=["GET", "POST"])
def saved_tickers():
    
    if request.method == "GET":
        
        fav_tickers = Ticker.query.filter_by(creator=session["user_id"]).all()
        
        options = []

        for ticker in fav_tickers:
            t1 = {}
            # print(ticker.__dict__)
            t1["id"] = ticker.id
            t1['name'] = ticker.name
            t1['nominator'] = ticker.nominator
            t1['denominator'] = ticker.denominator

            options.append(t1)

            print(t1)

        return render_template('saved-tickers.html', data = options)
    

    else:

        print(request.form.__dict__)
        item_id = request.form.get('selectedItem', None)

        ticker = Ticker.query.filter_by(id=item_id).first()

        nominator = ast.literal_eval(ticker.nominator)
        denominator = ast.literal_eval(ticker.denominator)
        name = ticker.name
        interval = ticker.interval
        bars_back = ticker.bars_back

        

        chart = CustomBasketChart(nominator, denominator, 
                                  name, interval, 
                                  bars_back)

        # Get basket chart data
        chart.get_complex_basket_data()
        
        # Get chart html
        chart.get_chart_html()

        return render_template('custom-basket.html', chart_div=chart.html, selected_basket_nominator = nominator, 
                               selected_name = name, selected_basket_denominator = denominator, 
                                selected_bars_back = bars_back, selected_interval = interval)
        
        # ADD unique row dentifier and push it to server. 

    
@app.route('/calculator', methods=["GET", "POST"])
def calculator():
    
    if request.method == "GET":
        return render_template('calculator.html', data_given = False)
    
    else:
        total_size = float(request.form.get('total_size', None))
        nominator_tickers = request.form.get('nominator_tickers', None).split(", ")
        denominator_tickers = request.form.get('denominator_tickers', None).split(", ")

        total_tickers = len(nominator_tickers) + len(denominator_tickers)
        size_per_position = total_size/total_tickers

        size_per_position = round(size_per_position, 2)

        risk = float(request.form.get('risk', None))

        long = []
        short = []

        for ticker in nominator_tickers:
            long.append(f"LONG {ticker}: {size_per_position}")

        for ticker in denominator_tickers:
            short.append(f"SHORT {ticker}: {size_per_position}")

        riskStr = f"\n\nRISK: {risk/100 * total_size}\n"

        print(nominator_tickers)
        print(denominator_tickers)

        

        return render_template('calculator.html', data_given = True, risk = riskStr, long = long, short = short)
    

@app.route('/explanation', methods=["GET"])
def explanation():
    
    
    return render_template('explanation.html')
    
    




if __name__ == "__main__":
    app.run(debug=True)