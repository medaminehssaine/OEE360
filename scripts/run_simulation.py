import sys
import os
import pandas as pd

# Add parent directory to path to import ts_oee360 package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ts_oee360 import generate_oee_data, save_oee_data

def main():
    """
    Run OEE simulation and save results
    """
    print("Starting OEE simulation...")
    
    # Generate OEE data
    df = generate_oee_data(sim_hours=8760, lag=3)
    
    # Save data
    file_path = save_oee_data(df, filename="data/ultra_complex_OEE.csv")
    
    print(f"Simulation complete. Data saved to {file_path}")
    print("\nData preview:")
    print(df.head())
    
    # Print some statistics
    print("\nData statistics:")
    print(f"Average OEE: {df['OEE'].mean():.4f}")
    print(f"Min OEE: {df['OEE'].min():.4f}")
    print(f"Max OEE: {df['OEE'].max():.4f}")
    
    return df

if __name__ == "__main__":
    main()