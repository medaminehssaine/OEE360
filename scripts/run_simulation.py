# scripts/run_simulation.py

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ts_oee360.generator import run_simulation

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    run_simulation("data/ultra_complex_OEE.csv")
