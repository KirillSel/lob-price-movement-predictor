![image](https://github.com/user-attachments/assets/a09dfe44-0379-42f5-b2bf-34dd92459bdb)# lob-price-movement-predictor
This repository contains the codebase for our HSE Master's thesis project on cryptocurrency price movement forecasting using order book liquidity data and machine learning methods.

## Title:
Predicting Price Movements in the Cryptocurrency Market Using Liquidity Analysis and Machine Learning Methods

### Установка окружения
```
python3 -m venv trading-env
source trading-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Подходы в директории notebooks
EDA.ipynb - ноутбук с EDA
eth_deeplob_baseline.ipynb - Бейзалйн с архитектурой DeepLOB
eth_deeplob_modified_version_1_final.ipynb - Первый подход с Bidirectional LSTM + Attention + Focal Loss
eth_deeplob_modified_v2_final.ipynb - Второй подход с Bidirectional GRU + Attention + Focal Loss


