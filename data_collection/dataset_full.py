import os
import numpy as np

train_dir = './datasets/train/'
validation_dir = './datasets/validation/'

# Обработка TRAIN
train_files = [f for f in os.listdir(train_dir) if f.endswith('.npy')]
all_arrays_train = [np.load(os.path.join(train_dir, f), allow_pickle=True) for f in train_files]
np.save(os.path.join(train_dir, 'binance_dataset_all_days_train.npy'), np.concatenate(all_arrays_train))

# Обработка VALIDATION
val_files = [f for f in os.listdir(validation_dir) if f.endswith('.npy')]
all_arrays_val = [np.load(os.path.join(validation_dir, f), allow_pickle=True) for f in val_files]
np.save(os.path.join(validation_dir, 'binance_dataset_all_days_val.npy'), np.concatenate(all_arrays_val))
