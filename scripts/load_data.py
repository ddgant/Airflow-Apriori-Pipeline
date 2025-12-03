"""
load_data.py
Script to load raw movie rental transaction data.
Reads the CSV file and prepares data for processing.
"""

import pandas as pd
import os
import json
from datetime import datetime


def load_raw_transactions(raw_file_path):
    """
    Loads the raw transaction CSV file.
    
    Args:
        raw_file_path (str): Path to the raw CSV file
        
    Returns:
        pd.DataFrame: DataFrame with loaded transactions
    """
    print(f"[INFO] Loading data from: {raw_file_path}")
    
    # Check if file exists
    if not os.path.exists(raw_file_path):
        raise FileNotFoundError(f"File {raw_file_path} does not exist")
    
    # Load CSV
    df = pd.read_csv(raw_file_path)
    
    print(f"[INFO] Loaded {len(df)} transactions")
    print(f"[INFO] Columns: {list(df.columns)}")
    
    return df


def save_loaded_data(df, output_path):
    """
    Saves loaded data in JSON format for the next step.
    
    Args:
        df (pd.DataFrame): DataFrame with transactions
        output_path (str): Path to save the processed file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert to list of dictionaries
    data = df.to_dict('records')
    
    # Save as JSON
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"[INFO] Data saved to: {output_path}")


def main():
    """
    Main function that executes the data loading process.
    """
    print("="*60)
    print("STARTING TRANSACTION DATA LOADING")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAW_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'data.csv')
    OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'loaded_transactions.json')
    
    # Load data
    df = load_raw_transactions(RAW_FILE)
    
    # Display data sample
    print("\n[INFO] Data sample:")
    print(df.head())
    print()
    
    # Save data
    save_loaded_data(df, OUTPUT_FILE)
    
    print("\n" + "="*60)
    print("DATA LOADING COMPLETED SUCCESSFULLY")
    print("="*60)


if __name__ == "__main__":
    main()