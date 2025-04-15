import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data")

def load_iaq(room: str) -> pd.DataFrame:
    path = os.path.join(DATA_PATH, f"sample_iaq_data_{room}.csv")
    return pd.read_csv(path)

def load_presence(room: str) -> pd.DataFrame:
    path = os.path.join(DATA_PATH, f"sample_presence_sensor_data_{room}.csv")
    return pd.read_csv(path)

def load_power() -> pd.DataFrame:
    path = os.path.join(DATA_PATH, "sample_power_meter_data.csv")
    return pd.read_csv(path)
