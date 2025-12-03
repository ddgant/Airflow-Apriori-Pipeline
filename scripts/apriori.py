"""
apriori.py
Manual implementation of the Apriori algorithm for discovering frequent itemsets
and generating association rules in movie rental data.
"""

import json
import os
from datetime import datetime
from itertools import combinations
from collections import defaultdict


class AprioriAlgorithm:
    """
    Class that implements the Apriori algorithm for frequent itemset mining.
    """
    
    def __init__(self, min_support=0.15, min_confidence=0.5, min_lift=1.0):
        """
        Initializes the Apriori algorithm.
        
        Args:
            min_support (float): Minimum support (0-1)
            min_confidence (float): Minimum confidence (0-1)
            min_lift (float): Minimum lift
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift
        self.transactions = []
        self.num_transactions = 0
        self.frequent_itemsets = {}
        self.association_rules = []
    
    def load_transactions(self, transactions):
        """
        Loads transactions for analysis.
        
        Args:
            transactions (list): List of lists with items
        """
        # Convert each transaction to frozenset to facilitate operations
        self.transactions = [frozenset(t) for t in transactions]
        self.num_transactions = len(self.transactions)
        print(f"[INFO] Loaded {self.num_transactions} transactions")
    
    def calculate_support(self, itemset):
        """
        Calculates the support of an itemset.
        
        Args:
            itemset (frozenset): Set of items
            
        Returns:
            float: Support value (0-1)
        """
        count = sum(1 for transaction in self.transactions if itemset.issubset(transaction))
        return count / self.num_transactions
    
    def get_frequent_1_itemsets(self):
        """
        Generates frequent itemsets of size 1 (individual items).
        
        Returns:
            dict: Dictionary {itemset: support}
        """
        print("[INFO] Generating frequent itemsets of size 1...")
        
        # Count occurrences of each individual item
        item_counts = defaultdict(int)
        for transaction in self.transactions:
            for item in transaction:
                item_counts[frozenset([item])] += 1
        
        # Filter by minimum support
        frequent_itemsets = {}
        for itemset, count in item_counts.items():
            support = count / self.num_transactions
            if support >= self.min_support:
                frequent_itemsets[itemset] = support
        
        print(f"[INFO] Found {len(frequent_itemsets)} frequent itemsets of size 1")
        return frequent_itemsets
    
    def generate_candidates(self, prev_frequent_itemsets, k):
        """
        Generates candidates of size k from frequent itemsets of size k-1.
        
        Args:
            prev_frequent_itemsets (dict): Frequent itemsets from previous level
            k (int): Size of new candidates
            
        Returns:
            list: List of candidates (frozensets)
        """
        items = set()
        for itemset in prev_frequent_itemsets.keys():
            items.update(itemset)
        
        # Generate all combinations of size k
        candidates = [frozenset(combo) for combo in combinations(items, k)]
        
        return candidates
    
    def prune_candidates(self, candidates, prev_frequent_itemsets):
        """
        Applies the Apriori principle: all subsets of a frequent itemset
        must be frequent.
        
        Args:
            candidates (list): List of candidates
            prev_frequent_itemsets (dict): Frequent itemsets from previous level
            
        Returns:
            list: List of candidates after pruning
        """
        pruned = []
        
        for candidate in candidates:
            # Generate all subsets of size k-1
            subsets = [frozenset(combo) for combo in combinations(candidate, len(candidate)-1)]
            
            # Verify that all subsets are frequent
            if all(subset in prev_frequent_itemsets for subset in subsets):
                pruned.append(candidate)
        
        return pruned
    
    def find_frequent_itemsets(self):
        """
        Finds all frequent itemsets using the Apriori algorithm.
        
        Returns:
            dict: Dictionary with all frequent itemsets and their supports
        """
        print("\n" + "="*60)
        print("RUNNING APRIORI ALGORITHM")
        print("="*60)
        print(f"Minimum support: {self.min_support}")
        print()
        
        all_frequent_itemsets = {}
        
        # Step 1: Find frequent itemsets of size 1
        current_frequent = self.get_frequent_1_itemsets()
        all_frequent_itemsets.update(current_frequent)
        
        k = 2
        
        # Repeat while there are frequent itemsets
        while current_frequent:
            print(f"\n[INFO] Generating candidates of size {k}...")
            
            # Generate candidates
            candidates = self.generate_candidates(current_frequent, k)
            print(f"[INFO] Generated {len(candidates)} candidates")
            
            # Prune candidates
            candidates = self.prune_candidates(candidates, current_frequent)
            print(f"[INFO] After pruning: {len(candidates)} candidates")
            
            # Calculate support and filter
            current_frequent = {}
            for candidate in candidates:
                support = self.calculate_support(candidate)
                if support >= self.min_support:
                    current_frequent[candidate] = support
            
            print(f"[INFO] Found {len(current_frequent)} frequent itemsets of size {k}")
            
            # Add to all frequent itemsets
            all_frequent_itemsets.update(current_frequent)
            
            k += 1
        
        self.frequent_itemsets = all_frequent_itemsets
        print(f"\n[INFO] Total frequent itemsets found: {len(all_frequent_itemsets)}")
        
        return all_frequent_itemsets
    
    def generate_association_rules(self):
        """
        Generates association rules from frequent itemsets.
        
        Returns:
            list: List of rules with their metrics
        """
        print("\n" + "="*60)
        print("GENERATING ASSOCIATION RULES")
        print("="*60)
        print(f"Minimum confidence: {self.min_confidence}")
        print(f"Minimum lift: {self.min_lift}")
        print()
        
        rules = []
        
        # Iterate over itemsets of size >= 2
        for itemset, support_itemset in self.frequent_itemsets.items():
            if len(itemset) < 2:
                continue
            
            # Generate all possible divisions of the itemset
            for i in range(1, len(itemset)):
                for antecedent in combinations(itemset, i):
                    antecedent = frozenset(antecedent)
                    consequent = itemset - antecedent
                    
                    # Calculate metrics
                    support_antecedent = self.frequent_itemsets.get(antecedent, 0)
                    support_consequent = self.frequent_itemsets.get(consequent, 0)
                    
                    if support_antecedent == 0:
                        continue
                    
                    confidence = support_itemset / support_antecedent
                    
                    if support_consequent == 0:
                        lift = 0
                    else:
                        lift = confidence / support_consequent
                    
                    # Filter by minimum confidence and lift
                    if confidence >= self.min_confidence and lift >= self.min_lift:
                        rule = {
                            'antecedent': list(antecedent),
                            'consequent': list(consequent),
                            'support': round(support_itemset, 4),
                            'confidence': round(confidence, 4),
                            'lift': round(lift, 4)
                        }
                        rules.append(rule)
        
        # Sort rules by lift descending
        rules.sort(key=lambda x: x['lift'], reverse=True)
        
        self.association_rules = rules
        print(f"[INFO] Total rules generated: {len(rules)}")
        
        return rules


def load_cleaned_transactions(file_path):
    """
    Loads cleaned transactions from JSON.
    
    Args:
        file_path (str): Path to JSON file
        
    Returns:
        list: List of transactions
    """
    print(f"[INFO] Loading transactions from: {file_path}")
    
    with open(file_path, 'r') as f:
        transactions = json.load(f)
    
    print(f"[INFO] Loaded {len(transactions)} transactions")
    return transactions


def save_results(frequent_itemsets, rules, output_dir):
    """
    Saves frequent itemsets and association rules.
    
    Args:
        frequent_itemsets (dict): Frequent itemsets with their supports
        rules (list): List of association rules
        output_dir (str): Output directory
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert itemsets to serializable format
    itemsets_list = []
    for itemset, support in frequent_itemsets.items():
        itemsets_list.append({
            'itemset': list(itemset),
            'size': len(itemset),
            'support': round(support, 4)
        })
    
    # Sort by support descending
    itemsets_list.sort(key=lambda x: x['support'], reverse=True)
    
    # Save frequent itemsets
    itemsets_file = os.path.join(output_dir, 'frequent_itemsets.json')
    with open(itemsets_file, 'w') as f:
        json.dump(itemsets_list, f, indent=2)
    print(f"[INFO] Frequent itemsets saved to: {itemsets_file}")
    
    # Save association rules
    rules_file = os.path.join(output_dir, 'association_rules.json')
    with open(rules_file, 'w') as f:
        json.dump(rules, f, indent=2)
    print(f"[INFO] Association rules saved to: {rules_file}")


def main():
    """
    Main function that executes the Apriori algorithm.
    """
    print("="*60)
    print("DATA MINING - APRIORI ALGORITHM")
    print("Movie Rental Pattern Analysis")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_transactions.json')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'results')
    
    # Load transactions
    transactions = load_cleaned_transactions(INPUT_FILE)
    
    # Initialize Apriori
    apriori = AprioriAlgorithm(
        min_support=0.15,      # 15% of transactions
        min_confidence=0.5,    # 50% confidence
        min_lift=1.0           # Lift greater than 1
    )
    
    # Load transactions in the algorithm
    apriori.load_transactions(transactions)
    
    # Find frequent itemsets
    frequent_itemsets = apriori.find_frequent_itemsets()
    
    # Generate association rules
    rules = apriori.generate_association_rules()
    
    # Save results
    save_results(frequent_itemsets, rules, OUTPUT_DIR)
    
    print("\n" + "="*60)
    print("APRIORI ALGORITHM COMPLETED SUCCESSFULLY")
    print("="*60)


if __name__ == "__main__":
    main()