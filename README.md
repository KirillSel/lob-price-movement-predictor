# lob-price-movement-predictor
This repository contains the codebase for our HSE Master's thesis project on cryptocurrency price movement forecasting using order book liquidity data and machine learning methods.

## Title:
Predicting Price Movements in the Cryptocurrency Market Using Liquidity Analysis and Machine Learning Methods

### Проектная структура:
```
.
├── data_collection/               # Сбор данных со стакана (order book) через REST API Binance
│   └── data_binance_SOLBTC/       # Собранные сырые данные по паре SOL/BTC
├── datasets/                      # Нормализованные .npy файлы train/val
│   ├── train/
│   └── validation/
├── live_prediction/               # Модуль live-инференса (прогнозы в реальном времени)
├── models/                        # Сохранённые модели keras (.keras)
├── notebooks/                     # Jupyter ноутбуки для анализа и тестов
├── requirements.txt               # Зависимости проекта
└── README.md                      # Документация проекта
```

### Установка окружения
```
python3 -m venv trading-env
source trading-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Сбор данных с Binance

Скрипт: pooling_raw.py

Описание: парсит стакан заявок (order book) и тикер по паре SOL/BTC с биржи Binance.
Данные сохраняются в двух форматах:

- binance_orderbook_YYYY-MM-DD.json — сырые данные (order book + ticker)
- binance_dataset_YYYY-MM-DD.csv — табличные, плоские данные

Сбор происходит раз в секунду, по 500 уровней стакана.

### Нормализация и препроцессинг
Скрипт: dataset_compile.py
Описание: загружает .csv из data_binance_SOLBTC/, нормализует размер заявок и сохраняет .npy:

- datasets/train/*.npy

- datasets/validation/*.npy

### Параметры:

- max_level = 100 — уровни стакана (±10% диапазон)

- feature_level = 10 — число признаков (±1%)

- train_pc = 80 — 80% в обучение, 20% в валидацию

Объединение всех .npy в один файл
Скрипт: dataset_full.py
Объединяет .npy по дням в один файл для обучения и валидации:

- datasets/train/binance_dataset_all_days_train.npy

- datasets/validation/binance_dataset_all_days_val.npy

### Обучение модели
Для обучения модели использовался ноутбук notebooks/DeepLOB_train_prototype.ipynb, реализующий кастомную архитектуру на основе:

- сверточных слоев (Conv2D),
- Inception-модуля (по аналогии с GoogLeNet),
- слоя LSTM для обработки временных зависимостей,
- выходного слоя с функцией активации softmax для классификации движения цены (вверх / нейтрально / вниз).

### Основные параметры обучения:

- datasample_period = 50 — количество временных шагов в одном сэмпле 
- prediction_period = 20 — горизонт прогнозирования в секундах
- feature_columns = 40 — число признаков (10 уровней стакана * 4 признака: цена и объем по bid/ask)
- band_size = 0.001 — порог чувствительности (0.1%) для классификации направленного движения
- batch_size = 256
- epochs = 50 — использовалось ограниченное количество эпох из-за малого объема данных

Архитектура модели реализована вручную (не через Keras.Sequential), и включает блоки нормализации, сверточные фильтры с различными ядрами, объединение Inception-подобных веток и LSTM.

Вывод: из-за ограниченного количества обучающих данных (~5000 строк) модель показывает невысокую уверенность в предсказаниях. Для улучшения качества рекомендуется собрать больше данных и увеличить число эпох.

### Прогноз в реальном времени
Скрипт: live_prediction/lob_live_test.py
Модель загружается из:
```
model_path = './models/checkpoint-50_20_0.001/ckpt-loss=1.02-epoch=0031.keras'
```

Логи сохраняются в ./logs/
