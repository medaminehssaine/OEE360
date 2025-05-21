# ts_oee360/utils.py

import matplotlib.pyplot as plt
import pandas as pd

def plot_oee_components(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df["time"], df["availability"], label="Availability")
    plt.plot(df["time"], df["performance"], label="Performance")
    plt.plot(df["time"], df["quality"], label="Quality")
    plt.plot(df["time"], df["oee"], label="OEE", linewidth=2)
    plt.xlabel("Time (h)")
    plt.ylabel("Value")
    plt.title("OEE and Its Components Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def load_simulation_data(path="data/ultra_complex_OEE.csv"):
    return pd.read_csv(path)
