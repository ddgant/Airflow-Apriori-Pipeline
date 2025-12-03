"""
clean_data.py
Script to clean and process movie rental transactions.
Converts CSV format to a clean list of transactions.
"""

import json
import os
from datetime import datetime
from collections import Counter


def load_json_data(file_path):
    """
    Loads data from the JSON file generated in the previous step.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        list: List of dictionaries with transactions
    """
    print(f"[INFO] Loading data from: {file_path}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    print(f"[INFO] Loaded {len(data)} transactions")
    return data


def clean_transactions(raw_data):
    """
    Cleans transactions, separating items and removing whitespace.
    
    Args:
        raw_data (list): List of dictionaries with raw transactions
        
    Returns:
        list: List of lists, where each sublist is a clean transaction
    """
    print("[INFO] Cleaning transactions...")
    
    cleaned_transactions = []
    
    for record in raw_data:
        transaction_id = record['TransactionID']
        items_str = record['Items']
        
        # Split items by comma and clean whitespace
        items = [item.strip() for item in items_str.split(',')]
        
        # Filter empty items
        items = [item for item in items if item]
        
        if items:  # Only add if there are items
            cleaned_transactions.append(items)
    
    print(f"[INFO] Cleaned {len(cleaned_transactions)} valid transactions")
    return cleaned_transactions


def generate_statistics(transactions):
    """
    Generates basic statistics about the transactions.
    
    Args:
        transactions (list): List of clean transactions
        
    Returns:
        dict: Dictionary with statistics
    """
    print("[INFO] Generating statistics...")
    
    # Count all items
    all_items = []
    for transaction in transactions:
        all_items.extend(transaction)
    
    item_counts = Counter(all_items)
    
    # Calculate statistics
    total_transactions = len(transactions)
    total_items_rented = len(all_items)
    unique_items = len(item_counts)
    avg_items_per_transaction = total_items_rented / total_transactions if total_transactions > 0 else 0
    
    stats = {
        'total_transactions': total_transactions,
        'total_items_rented': total_items_rented,
        'unique_items': unique_items,
        'avg_items_per_transaction': round(avg_items_per_transaction, 2),
        'most_common_items': dict(item_counts.most_common(10))
    }
    
    return stats


def save_cleaned_data(transactions, stats, output_file, stats_file):
    """
    Saves cleaned transactions and statistics.
    
    Args:
        transactions (list): List of clean transactions
        stats (dict): Generated statistics
        output_file (str): Path to save cleaned transactions
        stats_file (str): Path to save statistics
    """
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save cleaned transactions
    with open(output_file, 'w') as f:
        json.dump(transactions, f, indent=2)
    
    print(f"[INFO] Cleaned transactions saved to: {output_file}")
    
    # Save statistics
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"[INFO] Statistics saved to: {stats_file}")


def main():
    """
    Main function that executes the cleaning process.
    """
    print("="*60)
    print("STARTING DATA CLEANING")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'loaded_transactions.json')
    OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_transactions.json')
    STATS_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'cleaning_stats.json')
    
    # Load data
    raw_data = load_json_data(INPUT_FILE)
    
    # Clean transactions
    cleaned_transactions = clean_transactions(raw_data)
    
    # Generate statistics
    stats = generate_statistics(cleaned_transactions)
    
    # Display statistics
    print("\n[INFO] Cleaning statistics:")
    print(f"  - Total transactions: {stats['total_transactions']}")
    print(f"  - Total movies rented: {stats['total_items_rented']}")
    print(f"  - Unique movies: {stats['unique_items']}")
    print(f"  - Average movies per transaction: {stats['avg_items_per_transaction']}")
    print(f"\n  - Top 5 most rented movies:")
    for i, (item, count) in enumerate(list(stats['most_common_items'].items())[:5], 1):
        print(f"    {i}. {item}: {count} rentals")
    print()
    
    # Save data
    save_cleaned_data(cleaned_transactions, stats, OUTPUT_FILE, STATS_FILE)
    
    print("\n" + "="*60)
    print("DATA CLEANING COMPLETED SUCCESSFULLY")
    print("="*60)


if __name__ == "__main__":
    main()