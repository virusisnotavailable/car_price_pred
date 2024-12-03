import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime

def get_klines(symbol, interval, limit=100):
    """
    Fetch historical candlestick (kline) data from Binance.
    Args:
        symbol (str): Trading pair (e.g., BTCUSDT).
        interval (str): Time interval (e.g., '1m' for 1 minute).
        limit (int): Number of data points to fetch.
    Returns:
        pd.DataFrame: Candlestick data with 'time' and 'close' columns.
    """
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    data = response.json()

    # Create DataFrame
    df = pd.DataFrame(data, columns=[ 
        "time", "open", "high", "low", "close", "volume", 
        "close_time", "quote_asset_volume", "number_of_trades", 
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    df["time"] = pd.to_datetime(df["time"], unit="ms")  # Convert timestamp
    return df[["time", "close"]]

def calculate_rsi(data, window=14):
    """
    Calculate the Relative Strength Index (RSI).
    Args:
        data (pd.Series): Series of closing prices.
        window (int): Lookback period for RSI calculation.
    Returns:
        pd.Series: RSI values.
    """
    delta = data.diff()  # Price changes
    gain = np.where(delta > 0, delta, 0)  # Gains
    loss = np.where(delta < 0, -delta, 0)  # Losses

    avg_gain = pd.Series(gain).rolling(window=window, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss  # Relative Strength
    rsi = 100 - (100 / (1 + rs))  # RSI formula
    return rsi

def check_signals(rsi, last_close):
    """
    Generate buy/sell signals based on RSI levels.
    Args:
        rsi (float): Current RSI value.
        last_close (float): Latest close price.
    Returns:
        str: Signal message or None.
    """
    if rsi >= 80:
        return f"[{datetime.now()}] RSI: {rsi:.2f} - Stop Buying. Overbought condition (Short Strategy)."
    elif rsi <= 40:
        return f"[{datetime.now()}] RSI: {rsi:.2f} - Sell Signal. Exit short position (Short Strategy)."
    elif rsi <= 20:
        return f"[{datetime.now()}] RSI: {rsi:.2f} - Buy Signal. Oversold condition (Long Strategy)."
    elif rsi >= 60:
        return f"[{datetime.now()}] RSI: {rsi:.2f} - Sell Signal. Lock profits (Long Strategy)."
    return None

if __name__ == "__main__":
    symbol = "BTCUSDT"  # Trading pair
    interval = "1m"  # Interval: 1-minute candlesticks
    data_limit = 100  # Number of candles to fetch

    print("Starting RSI-based Notification System. Press Ctrl+C to stop.")
    try:
        while True:
            # Fetch the latest data
            df = get_klines(symbol, interval, data_limit)
            df["RSI"] = calculate_rsi(df["close"])

            # Get the latest RSI and closing price
            latest_rsi = df["RSI"].iloc[-1]
            latest_close = df["close"].iloc[-1]

            # Check for signals
            signal = check_signals(latest_rsi, latest_close)
            if signal:
                print(signal)

            # Wait for 1 seconds before checking again
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nNotification system stopped by user.")
