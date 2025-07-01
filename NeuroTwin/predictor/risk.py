import numpy as np

def predict_depression(avg_stress, avg_sleep):
    # LSTM-like risk model (mock but realistic)
    base = 40 + (avg_stress * 6.2) - (avg_sleep * 3.8)
    noise = np.random.uniform(-8, 8)
    return np.clip(base + noise, 0, 100)
