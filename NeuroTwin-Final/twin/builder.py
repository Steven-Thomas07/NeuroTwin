import pandas as pd
from predictor.risk import calculate_risk
import logging
from datetime import datetime

logging.basicConfig(filename='logs/neurotwin.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class DigitalTwin:
    def __init__(self, df):
        self.df = df
        self.risk = 0
    
    def build(self):
        self.risk = calculate_risk(self.df)
        logging.info(f"Digital Twin Built: Risk = {self.risk:.2f}% from {len(self.df)} entries")
        print(f"Digital Twin Built: Risk = {self.risk:.2f}%")
        return self.risk
