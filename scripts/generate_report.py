"""
generate_report.py
Script to generate readable reports from Apriori analysis results.
Creates reports in text and CSV format with frequent itemsets and association rules.
"""

import json
import os
import csv
from datetime import datetime


def load_results(results_dir):
    """
    Loads Apriori analysis results.
    
    Args:
        results_dir (str): Directory with results
        
    Returns:
        tuple: (frequent_itemsets, association_rules)
    """
    print("[INFO] Loading analysis results...")
    
    # Load frequent itemsets
    itemsets_file = os.path.join(results_dir, 'frequent_itemsets.json')
    with open(itemsets_file, 'r') as f:
        frequent_itemsets = json.load(f)
    
    # Load association rules
    rules_file = os.path.join(results_dir, 'association_rules.json')
    with open(rules_file, 'r') as f:
        association_rules = json.load(f)
    
    print(f"[INFO] Loaded {len(frequent_itemsets)} frequent itemsets")
    print(f"[INFO] Loaded {len(association_rules)} association rules")
    
    return frequent_itemsets, association_rules


def generate_text_report(frequent_itemsets, rules, output_file):
    """
    Generates a readable text format report.
    
    Args:
        frequent_itemsets (list): List of frequent itemsets
        rules (list): List of association rules
        output_file (str): Output file path
    """
    print("[INFO] Generating text report...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("="*80 + "\n")
        f.write("MOVIE RENTAL PATTERN ANALYSIS REPORT\n")
        f.write("Algorithm: Apriori\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        # Executive Summary
        f.write("EXECUTIVE SUMMARY\n")
        f.write("-"*80 + "\n")
        f.write(f"Total frequent itemsets found: {len(frequent_itemsets)}\n")
        f.write(f"Total association rules generated: {len(rules)}\n\n")
        
        # Size distribution
        size_distribution = {}
        for item in frequent_itemsets:
            size = item['size']
            size_distribution[size] = size_distribution.get(size, 0) + 1
        
        f.write("Itemset distribution by size:\n")
        for size in sorted(size_distribution.keys()):
            f.write(f"  - Size {size}: {size_distribution[size]} itemsets\n")
        f.write("\n")
        
        # Frequent itemsets
        f.write("="*80 + "\n")
        f.write("FREQUENT ITEMSETS\n")
        f.write("="*80 + "\n\n")
        
        # Group by size
        itemsets_by_size = {}
        for item in frequent_itemsets:
            size = item['size']
            if size not in itemsets_by_size:
                itemsets_by_size[size] = []
            itemsets_by_size[size].append(item)
        
        for size in sorted(itemsets_by_size.keys()):
            f.write(f"\n--- Itemsets of size {size} ---\n\n")
            items = itemsets_by_size[size]
            # Show top 10 by support
            for i, item in enumerate(items[:10], 1):
                itemset_str = ", ".join(item['itemset'])
                f.write(f"{i}. [{itemset_str}]\n")
                f.write(f"   Support: {item['support']:.4f} ({item['support']*100:.2f}%)\n\n")
            
            if len(items) > 10:
                f.write(f"   ... and {len(items)-10} more itemsets\n\n")
        
        # Association rules
        f.write("\n" + "="*80 + "\n")
        f.write("ASSOCIATION RULES\n")
        f.write("="*80 + "\n\n")
        f.write("Top 20 rules ordered by Lift:\n\n")
        
        for i, rule in enumerate(rules[:20], 1):
            antecedent_str = ", ".join(rule['antecedent'])
            consequent_str = ", ".join(rule['consequent'])
            
            f.write(f"{i}. [{antecedent_str}] => [{consequent_str}]\n")
            f.write(f"   Support: {rule['support']:.4f} ({rule['support']*100:.2f}%)\n")
            f.write(f"   Confidence: {rule['confidence']:.4f} ({rule['confidence']*100:.2f}%)\n")
            f.write(f"   Lift: {rule['lift']:.4f}\n")
            f.write(f"\n   Interpretation: If a customer rents [{antecedent_str}],\n")
            f.write(f"   there is a {rule['confidence']*100:.2f}% probability they will also rent [{consequent_str}]\n\n")
        
        if len(rules) > 20:
            f.write(f"... and {len(rules)-20} more rules\n\n")
        
        # Key insights
        f.write("\n" + "="*80 + "\n")
        f.write("KEY INSIGHTS\n")
        f.write("="*80 + "\n\n")
        
        if rules:
            top_rule = rules[0]
            f.write("Strongest rule (highest Lift):\n")
            f.write(f"[{', '.join(top_rule['antecedent'])}] => [{', '.join(top_rule['consequent'])}]\n")
            f.write(f"Lift: {top_rule['lift']:.4f}\n\n")
            
            # Most frequent movie in itemsets
            movie_freq = {}
            for item in frequent_itemsets:
                for movie in item['itemset']:
                    movie_freq[movie] = movie_freq.get(movie, 0) + 1
            
            if movie_freq:
                most_freq_movie = max(movie_freq, key=movie_freq.get)
                f.write(f"Movie appearing in most itemsets: {most_freq_movie}\n")
                f.write(f"Appearances: {movie_freq[most_freq_movie]}\n\n")
        
        f.write("="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")
    
    print(f"[INFO] Text report saved to: {output_file}")


def generate_csv_reports(frequent_itemsets, rules, output_dir):
    """
    Generates reports in CSV format for easy analysis.
    
    Args:
        frequent_itemsets (list): List of frequent itemsets
        rules (list): List of association rules
        output_dir (str): Output directory
    """
    print("[INFO] Generating CSV reports...")
    
    # CSV of frequent itemsets
    itemsets_csv = os.path.join(output_dir, 'frequent_itemsets.csv')
    with open(itemsets_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Itemset', 'Size', 'Support', 'Support_Percentage'])
        
        for item in frequent_itemsets:
            itemset_str = "; ".join(item['itemset'])
            writer.writerow([
                itemset_str,
                item['size'],
                item['support'],
                f"{item['support']*100:.2f}%"
            ])
    
    print(f"[INFO] Itemsets CSV saved to: {itemsets_csv}")
    
    # CSV of association rules
    rules_csv = os.path.join(output_dir, 'association_rules.csv')
    with open(rules_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Antecedent', 'Consequent', 'Support', 'Confidence', 
            'Lift', 'Confidence_Percentage'
        ])
        
        for rule in rules:
            antecedent_str = "; ".join(rule['antecedent'])
            consequent_str = "; ".join(rule['consequent'])
            writer.writerow([
                antecedent_str,
                consequent_str,
                rule['support'],
                rule['confidence'],
                rule['lift'],
                f"{rule['confidence']*100:.2f}%"
            ])
    
    print(f"[INFO] Rules CSV saved to: {rules_csv}")


def generate_summary_stats(frequent_itemsets, rules, output_file):
    """
    Generates a file with summary statistics.
    
    Args:
        frequent_itemsets (list): List of frequent itemsets
        rules (list): List of association rules
        output_file (str): Output file path
    """
    print("[INFO] Generating summary statistics...")
    
    stats = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_frequent_itemsets': len(frequent_itemsets),
        'total_association_rules': len(rules),
        'itemsets_by_size': {},
        'avg_support': 0,
        'avg_confidence': 0,
        'avg_lift': 0,
        'max_lift': 0,
        'min_lift': 0
    }
    
    # Itemset statistics
    for item in frequent_itemsets:
        size = item['size']
        stats['itemsets_by_size'][size] = stats['itemsets_by_size'].get(size, 0) + 1
        stats['avg_support'] += item['support']
    
    if frequent_itemsets:
        stats['avg_support'] /= len(frequent_itemsets)
    
    # Rule statistics
    if rules:
        stats['avg_confidence'] = sum(r['confidence'] for r in rules) / len(rules)
        stats['avg_lift'] = sum(r['lift'] for r in rules) / len(rules)
        stats['max_lift'] = max(r['lift'] for r in rules)
        stats['min_lift'] = min(r['lift'] for r in rules)
    
    # Round values
    stats['avg_support'] = round(stats['avg_support'], 4)
    stats['avg_confidence'] = round(stats['avg_confidence'], 4)
    stats['avg_lift'] = round(stats['avg_lift'], 4)
    stats['max_lift'] = round(stats['max_lift'], 4)
    stats['min_lift'] = round(stats['min_lift'], 4)
    
    with open(output_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"[INFO] Statistics saved to: {output_file}")


def main():
    """
    Main function that generates all reports.
    """
    print("="*60)
    print("GENERATING ANALYSIS REPORTS")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RESULTS_DIR = os.path.join(BASE_DIR, 'data', 'results')
    
    # Load results
    frequent_itemsets, rules = load_results(RESULTS_DIR)
    
    # Generate text report
    text_report_file = os.path.join(RESULTS_DIR, 'analysis_report.txt')
    generate_text_report(frequent_itemsets, rules, text_report_file)
    
    # Generate CSV reports
    generate_csv_reports(frequent_itemsets, rules, RESULTS_DIR)
    
    # Generate summary statistics
    stats_file = os.path.join(RESULTS_DIR, 'summary_statistics.json')
    generate_summary_stats(frequent_itemsets, rules, stats_file)
    
    print("\n" + "="*60)
    print("REPORT GENERATION COMPLETED SUCCESSFULLY")
    print("="*60)
    print("\nGenerated files:")
    print(f"  - {text_report_file}")
    print(f"  - {os.path.join(RESULTS_DIR, 'frequent_itemsets.csv')}")
    print(f"  - {os.path.join(RESULTS_DIR, 'association_rules.csv')}")
    print(f"  - {stats_file}")


if __name__ == "__main__":
    main()