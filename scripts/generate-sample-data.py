import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate comprehensive OEE sample data
np.random.seed(42)

# Time range
start_date = datetime(2020, 1, 1)
hours = 8760  # One year of hourly data

# Generate base time series
time_index = pd.date_range(start=start_date, periods=hours, freq='H')

# Generate realistic OEE data with patterns
data = []

for i, timestamp in enumerate(time_index):
    # Base patterns
    hour_of_day = timestamp.hour
    day_of_week = timestamp.weekday()
    month = timestamp.month
    
    # Shift patterns (3 shifts: 0-8, 8-16, 16-24)
    if hour_of_day < 8:
        shift = 'Night'
        shift_factor = 0.85  # Night shift typically lower
    elif hour_of_day < 16:
        shift = 'Day'
        shift_factor = 1.0   # Day shift baseline
    else:
        shift = 'Evening'
        shift_factor = 0.92  # Evening shift moderate
    
    # Seasonal patterns
    seasonal_factor = 0.95 + 0.1 * np.sin(2 * np.pi * month / 12)
    
    # Weekly patterns (weekends different)
    weekly_factor = 0.9 if day_of_week >= 5 else 1.0
    
    # Random variations
    noise = np.random.normal(0, 0.05)
    
    # Generate correlated metrics
    base_availability = 0.85 * shift_factor * seasonal_factor * weekly_factor + noise
    base_performance = 0.80 * shift_factor * seasonal_factor + np.random.normal(0, 0.08)
    base_quality = 0.90 * shift_factor * seasonal_factor + np.random.normal(0, 0.06)
    
    # Ensure realistic bounds
    availability = np.clip(base_availability, 0.5, 0.98)
    performance = np.clip(base_performance, 0.4, 0.95)
    quality = np.clip(base_quality, 0.7, 0.99)
    
    # Calculate OEE
    oee = availability * performance * quality
    
    # Additional factors
    temp = 20 + 10 * np.sin(2 * np.pi * month / 12) + np.random.normal(0, 3)
    humidity = 45 + 15 * np.sin(2 * np.pi * (month + 3) / 12) + np.random.normal(0, 5)
    energy_price = 0.12 + 0.03 * np.sin(2 * np.pi * hour_of_day / 24) + np.random.normal(0, 0.01)
    
    # Worker fatigue (higher at end of shifts)
    shift_hour = hour_of_day % 8
    fatigue = 0.1 + 0.4 * (shift_hour / 8) + np.random.normal(0, 0.1)
    fatigue = np.clip(fatigue, 0, 1)
    
    # Downtime events (random)
    downtime = np.random.exponential(0.02) if np.random.random() < 0.05 else 0
    
    data.append({
        'hour': i,
        'timestamp': timestamp,
        'OEE': oee,
        'availability': availability,
        'performance': performance,
        'quality': quality,
        'shift': shift,
        'temp': temp,
        'humidity': humidity,
        'energy_price': energy_price,
        'fatigue': fatigue,
        'downtime': downtime
    })

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('ultra_complex_OEE.csv', index=False)
print(f"Generated {len(df)} rows of OEE data")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"Average OEE: {df['OEE'].mean():.3f}")
