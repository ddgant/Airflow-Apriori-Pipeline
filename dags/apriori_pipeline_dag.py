"""
apriori_pipeline_dag.py
Airflow DAG to orchestrate the movie rental patterns analysis pipeline.
Implements Market Basket Analysis using Apriori algorithm.

Pipeline:
1. Load Data: Load transactions from CSV
2. Clean Data: Clean and preprocess transactions
3. Run Apriori: Execute Apriori algorithm to find itemsets and rules
4. Generate Report: Generate readable reports of results
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
import os

# Add scripts directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

# Import functions from scripts
from load_data import load_raw_transactions, save_loaded_data
from clean_data import load_json_data, clean_transactions, generate_statistics, save_cleaned_data
from apriori import AprioriAlgorithm, load_cleaned_transactions, save_results
from generate_report import load_results, generate_text_report, generate_csv_reports, generate_summary_stats


# Define default DAG arguments
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

# Define the DAG
dag = DAG(
    'movie_rental_apriori_pipeline',
    default_args=default_args,
    description='Pipeline for movie rental patterns analysis using Apriori',
    schedule_interval='@daily',  # Runs daily
    catchup=False,
    tags=['data_mining', 'apriori', 'market_basket'],
)


def task_load_data(**context):
    """
    Task 1: Load raw transaction data.
    Reads CSV file and prepares data for processing.
    """
    print("="*60)
    print("TASK 1: DATA LOADING")
    print("="*60)
    
    # Define paths
    RAW_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'data.csv')
    OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'loaded_transactions.json')
    
    # Load and save data
    df = load_raw_transactions(RAW_FILE)
    save_loaded_data(df, OUTPUT_FILE)
    
    # Save information in XCom for next tasks
    context['ti'].xcom_push(key='num_transactions', value=len(df))
    
    print("\n✓ Loading task completed successfully")


def task_clean_data(**context):
    """
    Task 2: Clean and preprocess transactions.
    Separates items, removes whitespace and generates statistics.
    """
    print("="*60)
    print("TASK 2: DATA CLEANING")
    print("="*60)
    
    # Define paths
    INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'loaded_transactions.json')
    OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_transactions.json')
    STATS_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'cleaning_stats.json')
    
    # Load, clean and save
    raw_data = load_json_data(INPUT_FILE)
    cleaned_transactions = clean_transactions(raw_data)
    stats = generate_statistics(cleaned_transactions)
    save_cleaned_data(cleaned_transactions, stats, OUTPUT_FILE, STATS_FILE)
    
    # Save information in XCom
    context['ti'].xcom_push(key='num_cleaned_transactions', value=len(cleaned_transactions))
    context['ti'].xcom_push(key='unique_movies', value=stats['unique_items'])
    
    print("\n✓ Cleaning task completed successfully")


def task_run_apriori(**context):
    """
    Task 3: Execute Apriori algorithm.
    Finds frequent itemsets and generates association rules.
    """
    print("="*60)
    print("TASK 3: APRIORI EXECUTION")
    print("="*60)
    
    # Define paths
    INPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'cleaned_transactions.json')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'results')
    
    # Load transactions
    transactions = load_cleaned_transactions(INPUT_FILE)
    
    # Configure and execute Apriori
    apriori = AprioriAlgorithm(
        min_support=0.15,      # 15% of transactions
        min_confidence=0.5,    # 50% confidence
        min_lift=1.0           # Lift greater than 1
    )
    
    apriori.load_transactions(transactions)
    frequent_itemsets = apriori.find_frequent_itemsets()
    rules = apriori.generate_association_rules()
    
    # Save results
    save_results(frequent_itemsets, rules, OUTPUT_DIR)
    
    # Save information in XCom
    context['ti'].xcom_push(key='num_frequent_itemsets', value=len(frequent_itemsets))
    context['ti'].xcom_push(key='num_rules', value=len(rules))
    
    print("\n✓ Apriori task completed successfully")


def task_generate_report(**context):
    """
    Task 4: Generate readable reports of results.
    Creates reports in text, CSV and summary statistics.
    """
    print("="*60)
    print("TASK 4: REPORT GENERATION")
    print("="*60)
    
    # Define paths
    RESULTS_DIR = os.path.join(BASE_DIR, 'data', 'results')
    
    # Load results
    frequent_itemsets, rules = load_results(RESULTS_DIR)
    
    # Generate reports
    text_report_file = os.path.join(RESULTS_DIR, 'analysis_report.txt')
    generate_text_report(frequent_itemsets, rules, text_report_file)
    generate_csv_reports(frequent_itemsets, rules, RESULTS_DIR)
    
    stats_file = os.path.join(RESULTS_DIR, 'summary_statistics.json')
    generate_summary_stats(frequent_itemsets, rules, stats_file)
    
    # Retrieve information from previous tasks
    num_transactions = context['ti'].xcom_pull(task_ids='load_data', key='num_transactions')
    num_itemsets = context['ti'].xcom_pull(task_ids='run_apriori', key='num_frequent_itemsets')
    num_rules = context['ti'].xcom_pull(task_ids='run_apriori', key='num_rules')
    
    print("\n" + "="*60)
    print("PIPELINE SUMMARY")
    print("="*60)
    print(f"Transactions processed: {num_transactions}")
    print(f"Frequent itemsets found: {num_itemsets}")
    print(f"Association rules generated: {num_rules}")
    print("="*60)
    
    print("\n✓ Report task completed successfully")


# Define DAG tasks
load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=task_load_data,
    provide_context=True,
    dag=dag,
)

clean_data_task = PythonOperator(
    task_id='clean_data',
    python_callable=task_clean_data,
    provide_context=True,
    dag=dag,
)

run_apriori_task = PythonOperator(
    task_id='run_apriori',
    python_callable=task_run_apriori,
    provide_context=True,
    dag=dag,
)

generate_report_task = PythonOperator(
    task_id='generate_report',
    python_callable=task_generate_report,
    provide_context=True,
    dag=dag,
)

# Define task execution order
load_data_task >> clean_data_task >> run_apriori_task >> generate_report_task