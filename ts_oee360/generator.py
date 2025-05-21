# ts_oee360/generator.py

import simpy
import pandas as pd
import numpy as np
import random
from .simulator import PowerGrid, Supplier, Machine

SIM_HOURS = 8760

# Shared state
raw_inventory = 1000.0
env_temp = 25.0
worker_fatigue = 1.0

def run_simulation(save_path="data/ultra_complex_OEE.csv"):
    global raw_inventory, env_temp, worker_fatigue

    env = simpy.Environment()
    workers = simpy.Container(env, init=3, capacity=3)
    power = PowerGrid(env)
    Supplier(env)
    machine = Machine(env, workers, power)

    data = []

    for _ in range(SIM_HOURS):
        env.step()

        # Simulate temp/fatigue
        env_temp = max(15, min(35, env_temp + random.gauss(0, 0.1)))
        worker_fatigue = 1 + (random.random() - 0.5) * 0.1

        # Update inventory
        if machine.working and raw_inventory > 0:
            raw_inventory -= random.uniform(0.5, 1.5)
            produced = 1
        else:
            produced = 0

        availability = 1 if machine.working else 0
        performance = produced
        quality = 1  # Placeholder, assuming perfect quality
        oee = availability * performance * quality

        data.append([
            env.now, availability, performance, quality, oee,
            raw_inventory, env_temp, worker_fatigue, power.voltage
        ])

    df = pd.DataFrame(data, columns=[
        "time", "availability", "performance", "quality", "oee",
        "inventory", "temperature", "fatigue", "voltage"
    ])
    df.to_csv(save_path, index=False)
    print(f"Simulation data saved to {save_path}")
