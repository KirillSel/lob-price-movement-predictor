import ccxt
import time
import os
import json
import csv
from datetime import datetime

# Настройки
symbol = 'ETH/USDT'
pair_name = symbol.replace('/', '')
limit = 10  # 10 уровней стакана
interval = 1  # секунда
output_dir = f'./data_binance_{pair_name}'
os.makedirs(output_dir, exist_ok=True)

binance = ccxt.binance()
row_count = 0
start_time = time.time()
last_log_time = start_time
start_time_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

print(f"--- Data collection started at {start_time_str} UTC for {symbol} ---")

def flatten_orderbook(orderbook, system_time):
    bids = sorted(orderbook['bids'], key=lambda x: -x[0])[:limit]
    asks = sorted(orderbook['asks'], key=lambda x: x[0])[:limit]

    row = [
        int(system_time)  # timestamp в секундах
    ]
    for b in bids:
        row.extend([b[0], b[1]])
    for a in asks:
        row.extend([a[0], a[1]])
    return row

def main_loop():
    global row_count, last_log_time
    while True:
        try:
            system_time = time.time()
            timestamp_sec = int(system_time)
            date_str = datetime.utcfromtimestamp(system_time).strftime('%Y-%m-%d')

            orderbook = binance.fetch_order_book(symbol, limit=limit)

            # CSV запись
            row = flatten_orderbook(orderbook, timestamp_sec)
            with open(f'{output_dir}/binance_dataset_{date_str}.csv', 'a', newline='') as f_csv:
                writer = csv.writer(f_csv)
                writer.writerow(row)

            row_count += 1

            # Лог каждые 10 минут
            if time.time() - last_log_time >= 600:
                elapsed = int(time.time() - start_time)
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Rows: {row_count}, elapsed: {elapsed // 60} min")
                last_log_time = time.time()

        except Exception as e:
            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Error: {e}")
            time.sleep(5)

        time.sleep(interval)

if __name__ == "__main__":
    main_loop()
