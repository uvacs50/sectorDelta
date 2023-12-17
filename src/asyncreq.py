import asyncio
import requests


url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=200"
s = requests.Session()

async def main():

    data = s.get(url).json()
    return data


async def t():

    results = await asyncio.gather(
        main(),
        main()
    )

    print(results)


asyncio.run(t())