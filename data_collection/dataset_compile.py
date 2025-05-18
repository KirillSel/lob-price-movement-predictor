import os
import pandas as pd

input_path = './data_binance_ETHUSDT/'
output_file = 'combined_orderbooks_eth.csv'

compiled_df = []

# Читаем все csv из директории
for file in os.listdir(input_path):
    if file.endswith('.csv'):
        file_path = os.path.join(input_path, file)
        df = pd.read_csv(file_path, header=None)
        compiled_df.append(df)

# Объединяем все данные
all_data = pd.concat(compiled_df, ignore_index=True)

# Сохраняем
all_data.to_csv(output_file, index=False, header=False)
print(f"✅ Данные сохранены в {output_file}")
