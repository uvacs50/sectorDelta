import requests
from requests import Session
from app import get_basket_data

s = Session()

def get_price(ticker):
    r = s.get(url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={ticker}")
    price = float(r.json()['price'])

    return price


mult = 1
prices = []
for ticker in ["SOLUSDT", "ETHUSDT", "BNBUSDT", "APTUSDT"]:
    price = get_price(ticker)
    mult *= price
    prices.append(price)


c = mult**0.25

c = c / get_price("BTCUSDT")
print(prices)
print(c)


df, df_prices  = get_basket_data("L1", "BTCUSDT", "1h", s)


m = 1
for i in df_prices:
    m *= i

print("multiplication: ", m**0.25)
print(df)
