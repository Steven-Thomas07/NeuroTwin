import numpy as np

def calculate_risk(df):
    avg_stress = df['stress'].mean()
    avg_sleep = df['sleep_hours'].mean()
    base_risk = 40 + (avg_stress * 6.2) - (avg_sleep * 3.8)
    return np.clip(base_risk, 0, 100)
