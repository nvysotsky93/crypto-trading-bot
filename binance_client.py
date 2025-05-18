import requests

def get_klines(symbol="BTCUSDT", interval="15m", limit=100):
    url = f"https://fapi.binance.com/fapi/v1/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    return response.json()
