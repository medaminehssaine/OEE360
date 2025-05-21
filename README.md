# TS_OEE360

**TS_OEE360** is a Python-based industrial simulation project that models Overall Equipment Effectiveness (OEE) using a discrete-event simulation framework with `SimPy`. It outputs synthetic time series data that can later be used for forecasting.

## 🚀 Features
- Discrete-event simulation of industrial operations
- OEE computation: Availability, Performance, Quality
- Data generation for time series forecasting

## 📂 Project Structure
```
ts_oee360/         # Main module
  ├── simulator.py     # SimPy classes (Machine, Supplier, PowerGrid)
  ├── generator.py     # Simulation runner
  └── utils.py         # Plotting & helpers
scripts/
  └── run_simulation.py
notebooks/
  └── exploration.ipynb
```

## 📦 Installation
```bash
pip install -r requirements.txt
```

## ▶️ Running the Simulation
```bash
python scripts/run_simulation.py
```
Output saved to `data/ultra_complex_OEE.csv`

## 📊 Plotting OEE
```python
from ts_oee360.utils import *
df = load_simulation_data()
plot_oee_components(df)
```

## 📈 Forecasting
You can now use the generated data to build ARIMA or deep learning models.
