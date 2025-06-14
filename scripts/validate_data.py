import pandas as pd
import sys
import os

def validate_csv_file(filepath):
    """Validate CSV file format for OEE dashboard"""
    required_columns = [
        'timestamp', 'OEE', 'availability', 'performance', 'quality',
        'temp', 'humidity', 'machine_speed', 'vibration', 'pressure',
        'power_consumption', 'hour_of_day', 'day_of_week', 'month'
    ]
    
    try:
        # Load CSV
        df = pd.read_csv(filepath)
        print(f"📊 Validating: {os.path.basename(filepath)}")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {len(df.columns)}")
        
        # Check required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        
        # Check data types
        try:
            pd.to_datetime(df['timestamp'])
            print("✅ Timestamp format: OK")
        except:
            print("❌ Timestamp format: Invalid")
            return False
        
        # Check numeric ranges
        numeric_checks = [
            ('OEE', 0, 1),
            ('availability', 0, 1),
            ('performance', 0, 1),
            ('quality', 0, 1),
            ('temp', -50, 100),
            ('humidity', 0, 100)
        ]
        
        for col, min_val, max_val in numeric_checks:
            if df[col].min() < min_val or df[col].max() > max_val:
                print(f"⚠️  {col}: Values outside expected range [{min_val}, {max_val}]")
        
        print("✅ Validation complete")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_data.py <csv_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        sys.exit(1)
    
    is_valid = validate_csv_file(filepath)
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()