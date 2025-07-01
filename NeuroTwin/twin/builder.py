import pandas as pd
import numpy as np
from predictor.risk import predict_depression
import logging
import os

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename='logs/neurotwin.log', level=logging.INFO)

class DigitalTwin:
    def __init__(self, mood_file):
        self.df = pd.read_csv(mood_file)
        self.risk = 0
    
    def build(self):
        logging.info(f"Digital Twin Built: {len(self.df)} days of mood data")
        avg_stress = self.df['stress'].mean()
        avg_sleep = self.df['sleep_hours'].mean()
        self.risk = predict_depression(avg_stress, avg_sleep)
        print(f"Digital Twin Built: Risk = {self.risk}%")
    
    def predict_depression(self):
        return int(self.risk)
