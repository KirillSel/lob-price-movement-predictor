import ccxt
import time
import numpy as np
import tensorflow as tf
from datetime import datetime
import json
import os

symbol = 'SOL/BTC'
level_max = 100
level_increment = 0.001
price_digit = 8
sample_num = 50
predict_num = 20
feature_num = 40


model_path = './models/checkpoint-50_20_0.001/ckpt-loss=1.02-epoch=0031.keras'
cnn_model = tf.keras.models.load_model(model_path)
binance = ccxt.binance()

cnn_dataset = []

def arr_sort(arr, ascend=True):
    return sorted(arr, key=lambda x: x[0], reverse=not ascend)

def build_dataset(orderbook, ticker):
    bids = arr_sort(orderbook['bids'], ascend=False)
    asks = arr_sort(orderbook['asks'], ascend=True)
    mid_price = (bids[0][0] + asks[0][0]) / 2

    bucketed_lob = {'bids': [], 'asks': []}
    for l in range(1, level_max + 1):
        bid_pc = 1 - level_increment * l
        ask_pc = 1 + level_increment * l
        bucketed_lob['bids'].append([round(mid_price * bid_pc, price_digit), 0])
        bucketed_lob['asks'].append([round(mid_price * ask_pc, price_digit), 0])

    for side, data in [('bids', bids), ('asks', asks)]:
        for price, size in data:
            for i, (bucket_price, _) in enumerate(bucketed_lob[side]):
                if (side == 'bids' and price >= bucket_price) or (side == 'asks' and price <= bucket_price):
                    bucketed_lob[side][i][1] += size
                    break

    flat = []
    for side in ['bids', 'asks']:
        for price, size in bucketed_lob[side]:
            flat.extend([price, size])

    return [ticker['timestamp'], ticker['last'], *flat]

def normalize_row(row):
    size_values = [v for i, v in enumerate(row) if i >= 2 and (i - 2) % 2 == 1]
    mean = np.mean(size_values)
    std = np.std(size_values)
    return [((v - mean) / std if i >= 2 and (i - 2) % 2 == 1 else v) for i, v in enumerate(row)]

def cnn_dataset_create(sample_array):
    sample_array = np.array(sample_array)  # shape (50, 42)
    sample_array = sample_array[:, 2:2 + feature_num]  # берем только признаки
    sample_array = sample_array.reshape(1, sample_num, feature_num, 1)
    return sample_array


def forward_test_log(prediction_obj, predicted_side):
    time.sleep(predict_num)
    ticker = binance.fetch_ticker(symbol)
    delta = ticker['last'] / prediction_obj['price'] - 1
    correct = (predicted_side == 'up' and delta > 0) or (predicted_side == 'down' and delta < 0)

    log_data = {
        'time': str(datetime.utcnow()),
        'delta': delta,
        'prediction': predicted_side,
        'correct': correct,
        'price_now': ticker['last'],
        'predicted_price': prediction_obj['price']
    }
    log_dir = './logs'
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f'binance_validationlog_{datetime.utcnow().date()}.json')
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_data) + '\n')

print(f"Listening to {symbol} every second...")
while True:
    try:
        orderbook = binance.fetch_order_book(symbol, limit=500)
        ticker = binance.fetch_ticker(symbol)
        row = build_dataset(orderbook, ticker)
        norm_row = normalize_row(row)
        cnn_dataset.append(norm_row)
        if len(cnn_dataset) > sample_num:
            cnn_dataset.pop(0)

        if len(cnn_dataset) == sample_num:
            input_tensor = cnn_dataset_create(cnn_dataset)
            pred = cnn_model.predict(input_tensor)[0]
            print(f"Prediction: {pred}")
            if pred[0] > 0.7:
                print(f"[{datetime.utcnow()}] ↓ prediction")
                forward_test_log({'price': row[1]}, 'down')
            elif pred[2] > 0.7:
                print(f"[{datetime.utcnow()}] ↑ prediction")
                forward_test_log({'price': row[1]}, 'up')

    except Exception as e:
        print("Error:", e)
    time.sleep(1)
