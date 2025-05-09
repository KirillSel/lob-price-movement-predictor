import ccxt
import time
import os
import json
import csv
from datetime import datetime, timedelta

# Настройки
symbol = 'SOL/BTC'
pair_name = symbol.replace('/', '')  # Например, SOLBTC
limit = 500  # уровни стакана
interval = 1  # секунда
output_dir = f'./data_binance_{pair_name}'
os.makedirs(output_dir, exist_ok=True)

binance = ccxt.binance()

# Вспомогательные переменные
start_time = time.time()
start_time_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
last_log_time = start_time
row_count = 0

print(f"--- Data collection started at {start_time_str} UTC for {symbol} ---")

def flatten_orderbook(orderbook, ticker, system_time):
    bids = sorted(orderbook['bids'], key=lambda x: -x[0])
    asks = sorted(orderbook['asks'], key=lambda x: x[0])
    flat_bids = [val for entry in bids for val in entry][:limit * 2]
    flat_asks = [val for entry in asks for val in entry][:limit * 2]

    row = [
        ticker['timestamp'],           # Биржевой timestamp
        ticker['last'],                # Последняя цена
        int(system_time * 1000),       # Системное время в мс
        *flat_bids,
        *flat_asks
    ]
    return row

def main_loop():
    global row_count, last_log_time
    while True:
        try:
            system_time = time.time()
            date_str = datetime.utcfromtimestamp(system_time).strftime('%Y-%m-%d')
            orderbook = binance.fetch_order_book(symbol, limit=limit)
            ticker = binance.fetch_ticker(symbol)

            # JSON (сырые данные)
            with open(f'{output_dir}/binance_orderbook_{date_str}.json', 'a') as f_json:
                json.dump({'orderbook': orderbook, 'ticker': ticker}, f_json)
                f_json.write('\n')

            # CSV (обработанные)
            row = flatten_orderbook(orderbook, ticker, system_time)
            with open(f'{output_dir}/binance_dataset_{date_str}.csv', 'a', newline='') as f_csv:
                writer = csv.writer(f_csv)
                writer.writerow(row)

            row_count += 1

            # Каждые 20 минут (или при первом запуске)
            if time.time() - last_log_time >= 20 * 60:
                elapsed = int(time.time() - start_time)
                print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Recorded rows: {row_count}, elapsed time: {elapsed // 60} min {elapsed % 60} sec")
                last_log_time = time.time()

        except KeyboardInterrupt:
            elapsed = int(time.time() - start_time)
            print(f"\n--- Data collection interrupted by user ---")
            print(f"Total rows: {row_count}")
            print(f"Total time: {elapsed // 60} min {elapsed % 60} sec")
            break

        except Exception as e:
            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Error: {e}")

        time.sleep(interval)

if __name__ == "__main__":
    main_loop()
