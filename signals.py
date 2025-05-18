from binance_client import get_klines
import pandas as pd
import ta
from datetime import datetime

def fetch_ohlcv(symbol="BTCUSDT", interval="15m", limit=100):
    try:
        klines = get_klines(symbol, interval, limit)
        if not klines or len(klines) == 0:
            print(f"[ERROR] Пустые данные от Binance для {symbol}")
            return None
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'num_trades',
            'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['volume'] = df['volume'].astype(float)
        return df
    except Exception as e:
        print(f"[ERROR] Ошибка получения данных для {symbol}: {e}")
        return None

def analyze(symbol="BTCUSDT"):
    df = fetch_ohlcv(symbol)
    if df is None or df.empty:
        return {
            "symbol": symbol,
            "price": 0,
            "signal": "WAIT",
            "score": 0,
            "reasons": ["Нет данных с Binance"],
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

    close = df['close'].iloc[-1]
    rsi = ta.momentum.RSIIndicator(df['close']).rsi().iloc[-1]
    macd_line = ta.trend.MACD(df['close']).macd().iloc[-1]
    macd_signal = ta.trend.MACD(df['close']).macd_signal().iloc[-1]
    ema20 = df['close'].ewm(span=20).mean().iloc[-1]
    ema50 = df['close'].ewm(span=50).mean().iloc[-1]
    sma7 = df['close'].rolling(window=7).mean().iloc[-1]
    sma25 = df['close'].rolling(window=25).mean().iloc[-1]
    volume_now = df['volume'].iloc[-1]
    volume_avg = df['volume'].rolling(window=20).mean().iloc[-1]
    range_now = df['high'].iloc[-1] - df['low'].iloc[-1]
    range_avg = (df['high'] - df['low']).rolling(window=10).mean().iloc[-1]

    score = 0
    reasons = []

    if rsi < 30:
        score += 1
        reasons.append("RSI < 30 (перепродан)")
    elif rsi > 70:
        score -= 1
        reasons.append("RSI > 70 (перекуплен)")

    if macd_line > macd_signal:
        score += 1
        reasons.append("MACD пересёк вверх")
    elif macd_line < macd_signal:
        score -= 1
        reasons.append("MACD пересёк вниз")

    if ema20 > ema50:
        score += 1
        reasons.append("EMA20 > EMA50 (тренд вверх)")
    else:
        score -= 1
        reasons.append("EMA20 < EMA50 (тренд вниз)")

    if sma7 > sma25:
        score += 1
        reasons.append("SMA7 > SMA25 (бычий)")
    else:
        score -= 1
        reasons.append("SMA7 < SMA25 (медвежий)")

    if volume_now > volume_avg:
        score += 1
        reasons.append("Объём выше среднего")
    else:
        reasons.append("Объём низкий")

    if range_now < range_avg * 0.7:
        reasons.append("Низкая волатильность — сигнал пропущен")
        return {
            "symbol": symbol,
            "price": round(close, 2),
            "signal": "WAIT",
            "score": score,
            "reasons": reasons,
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

    signal = "WAIT"
    if score >= 3:
        signal = "BUY"
    elif score <= -3:
        signal = "SELL"

    return {
        "symbol": symbol,
        "price": round(close, 2),
        "signal": signal,
        "score": score,
        "reasons": reasons,
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
