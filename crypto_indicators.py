import requests
import csv
import argparse
from typing import List, Dict
from datetime import datetime
def fetch_ohlcv(symbol: str) -> List[Dict]:
    url = "https://api-gcp.binance.com/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": "1m",
        "limit": 60
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = []
        for entry in response.json():
                ts_readable = datetime.fromtimestamp(entry[0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                data.append({
                    "timestamp":ts_readable,
                    "open": float(entry[1]),
                    "high": float(entry[2]),
                    "low": float(entry[3]),
                    "close": float(entry[4]),
                    "volume": float(entry[5])
                })
        return data
    except Exception as e:
        print(f"Error fetching data. Try again. \n\n Error details: {e}")
    

def compute_sma(data: List[Dict], window: int = 10) -> List[float]:
    sma_list = []
    closing_prices = [row["close"] for row in data]

    for price in range(len(closing_prices)):
        if price + 1 < window:
            sma_list.append(None)  # Blank when not enough data available
        else:
            window_vals = closing_prices[price + 1 - window : price + 1]
            sma = sum(window_vals) / window
            sma_list.append(sma)
    return sma_list

def compute_pct_change(data: List[Dict]) -> float:
    first_close = data[0]["close"]
    last_close = data[-1]["close"]
    return (last_close - first_close) / first_close * 100


def write_csv(data: List[Dict], sma_list: List[float], pct: float, out_path: str):
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume", "sma_10", "pct_change"])

        for count, row in enumerate(data):
            writer.writerow([
                row["timestamp"],
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row["volume"],
                "" if sma_list[count] is None else sma_list[count],
                pct  # same across rows
            ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch OHLCV data and compute indicators.")
    parser.add_argument("--symbol", type=str, required=True, help="Trading pair symbol (e.g., BTCUSDT)")
    parser.add_argument("--output", type=str, required=True, help="Output CSV file path")
    args = parser.parse_args()

    data = fetch_ohlcv(args.symbol)
    sma = compute_sma(data, window=10)
    pct = compute_pct_change(data)
    write_csv(data, sma, pct, args.output)

    print(f"Saved {len(data)} rows to {args.output}")
