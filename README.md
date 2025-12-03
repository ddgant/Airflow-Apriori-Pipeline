# 🎬 Movie Rental Apriori Pipeline

## Movie Rental Patterns Analysis System

Automated data mining pipeline using Apriori algorithm to discover co-rental patterns in a movie rental store, orchestrated with Apache Airflow.

---

## 📋 Project Description

This project implements a complete data analysis pipeline to discover which movies tend to be rented together by customers. It uses the Apriori algorithm to find frequent itemsets and generate association rules that can be used for:

- **Recommendation systems**: Suggest movies based on current rentals
- **Marketing strategies**: Create promotional bundles of related movies
- **Inventory organization**: Place related movies near each other
- **Trend analysis**: Understand customer tastes and preferences

---

## 🎯 Business Scenario

**Context**: We are the data team of a movie rental store.

**Problem**: Every day new rental transactions are generated, and we need to:
1. Identify which movies are frequently rented together
2. Discover customer behavior patterns
3. Generate automatic recommendations

**Solution**: An automated pipeline that:
- Processes daily transactions
- Executes the Apriori algorithm
- Generates reports with actionable insights

---

## 📊 Dataset

### Movies in Catalog
The dataset contains rental transactions with the following movies:

**Sci-Fi/Thriller Category:**
- Inception
- Interstellar
- The Dark Knight
- The Martian

**Crime/Drama Category:**
- The Godfather
- Goodfellas
- Scarface

**Action/Tarantino Category:**
- Pulp Fiction
- Kill Bill
- Django Unchained

**Superhero Category:**
- Joker
- The Batman

### Data Format
```csv
TransactionID,Items
1,"Inception,The Dark Knight,Interstellar"
2,"The Godfather,Goodfellas"
3,"Inception,Interstellar"
...
```

### Characteristics
- **40 sample transactions**
- **12 unique movies** in catalog
- **2-3 movies per transaction** on average
- Simulated data with realistic patterns

---

## 🏗️ Pipeline Architecture

![Architecture Diagram](diagram/architecture_diagram.png)

---

## 🔧 Requirements and Installation

### Prerequisites
- Python 3.8 or higher
- Apache Airflow 2.0 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository>
   cd movie_rental_apriori
   ```

2. **Start the environment**
   
   Run the following command to build the image and start the containers:
   ```bash
   docker-compose up --build
   ```
   
   Wait until the logs stabilize and you see "Listening at..."

3. **Create the Admin User**
   
  Open a new terminal inside the project folder and run:
  ```bash
  docker-compose exec airflow-webserver airflow users create \
      --username admin \
      --firstname Admin \
      --lastname User \
      --role Admin \
      --email admin@example.com \
      --password admin
  ```

4. **Access the Pipeline**

   - Open your browser at: `http://localhost:8080`
   - Login: `admin` / `admin`
   - Search for DAG: `movie_rental_apriori_pipeline`
   - Toggle the switch to ON and click the Play button (Trigger DAG)

### Optional: Run Individual Scripts (For Testing)

If you want to test scripts individually without Airflow:

```bash
# Enter the container
docker-compose exec airflow-webserver bash

# Then run scripts
python /opt/airflow/scripts/load_data.py
python /opt/airflow/scripts/clean_data.py
python /opt/airflow/scripts/apriori.py
python /opt/airflow/scripts/generate_report.py
```

---

## 📁 Project Structure

```
movie_rental_apriori/
│
├── dags/
│   └── apriori_pipeline_dag.py       # Airflow DAG
│
├── data/
│   ├── raw/
│   │   └── data.csv                  # Raw transaction data
│   ├── processed/
│   │   ├── loaded_transactions.json   # Loaded data
│   │   ├── cleaned_transactions.json  # Clean data
│   │   └── cleaning_stats.json        # Cleaning statistics
│   └── results/
│       ├── frequent_itemsets.json     # Frequent itemsets
│       ├── association_rules.json     # Association rules
│       ├── analysis_report.txt        # Readable report
│       ├── frequent_itemsets.csv      # Itemsets in CSV
│       ├── association_rules.csv      # Rules in CSV
│       └── summary_statistics.json    # Summary statistics
│
├── scripts/
│   ├── load_data.py                  # Loading script
│   ├── clean_data.py                 # Cleaning script
│   ├── apriori.py                    # Apriori implementation
│   └── generate_report.py            # Report generator
│
├── Dockerfile                         # Docker image definition
├── docker-compose.yaml                # Docker orchestration
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

---

## 🧮 Apriori Algorithm - Explanation

### What is Apriori?

Apriori is a data mining algorithm designed to find **frequent itemsets** (sets of items that appear together frequently) and generate **association rules** (co-occurrence patterns).

### Step-by-Step Operation

#### 1. Find Frequent Individual Items (L1)
```
Scan transactions and count each movie
Example:
- Inception: appears in 15 transactions (support = 15/40 = 37.5%)
- The Dark Knight: 12 transactions (30%)
...
Filter by minimum support (15%)
```

#### 2. Generate Pair Candidates (C2)
```
Combine frequent L1 items to create pairs
Example:
- {Inception, The Dark Knight}
- {Inception, Interstellar}
- {The Godfather, Goodfellas}
...
```

#### 3. Prune Using Apriori Property
```
Principle: If an itemset is frequent, 
           all its subsets must also be frequent

Example: If {A, B, C} is a candidate,
         verify that {A,B}, {A,C}, {B,C} are frequent
         If any is not, eliminate {A,B,C}
```

#### 4. Calculate Candidate Support (L2)
```
Scan transactions and count pairs
Filter by minimum support
```

#### 5. Repeat for Triples, Quadruples, etc.
```
Continue until no more frequent itemsets exist
```

#### 6. Generate Association Rules
```
For each frequent itemset of size ≥ 2:
  Divide into antecedent → consequent
  
Example: {Inception, Interstellar, The Dark Knight}
  → {Inception, Interstellar} => {The Dark Knight}
  → {Inception} => {Interstellar, The Dark Knight}
  ... all possible combinations
  
Calculate metrics:
  - Support: % of transactions containing complete itemset
  - Confidence: % of times consequent appears given antecedent
  - Lift: How much more likely is consequent given antecedent
```

### Metrics Explained

**Support**: How frequent is this itemset?
```
Support({A,B}) = Transactions with A and B / Total transactions
Example: 6/40 = 0.15 (15%)
```

**Confidence**: If someone rents A, how likely are they to rent B?
```
Confidence(A→B) = Support({A,B}) / Support({A})
Example: 0.15 / 0.30 = 0.50 (50%)
```

**Lift**: Is the rule better than chance?
```
Lift(A→B) = Confidence(A→B) / Support({B})
Lift > 1: Positive correlation (useful!)
Lift = 1: Independent
Lift < 1: Negative correlation
```

### Configurable Parameters

In `scripts/apriori.py`:
```python
apriori = AprioriAlgorithm(
    min_support=0.15,      # 15% - Adjust as needed
    min_confidence=0.5,    # 50% - More reliable rules
    min_lift=1.0           # Only positive correlations
)
```

---

## 📈 Results Interpretation

### Frequent Itemset Example
```
Itemset: [Inception, Interstellar]
Support: 0.35 (35%)

Interpretation:
35% of customers who rent movies 
rent these two together.
```

### Association Rule Example
```
Rule: [Inception] => [Interstellar]
Support: 0.35
Confidence: 0.78
Lift: 2.1

Interpretation:
- If a customer rents Inception, there's a 78% probability 
  they will also rent Interstellar
- This combination is 2.1 times more likely than if 
  they were independent
- Action: Recommend Interstellar to those who rent Inception
```

---

## 📊 Results Visualization

Results can be visualized in several files:

### 1. Text Report (`analysis_report.txt`)
- Executive summary
- Frequent itemsets by size
- Top 20 rules ordered by lift
- Key insights

### 2. Itemsets CSV (`frequent_itemsets.csv`)
- Easy to open in Excel/Google Sheets
- Useful for additional analysis

### 3. Rules CSV (`association_rules.csv`)
- All metrics in tabular format
- Filterable and sortable

### 4. JSON Statistics (`summary_statistics.json`)
- Aggregate metrics
- Useful for dashboards

---

## 🎓 DAG Tasks Description

### Task 1: Load Data
**File**: `scripts/load_data.py`

**Responsibility**:
- Read raw CSV file
- Validate data format
- Convert to JSON for processing

**Input**: `data/raw/data.csv`

**Output**: `data/processed/loaded_transactions.json`

**XCom**: Publishes number of loaded transactions

---

### Task 2: Clean Data
**File**: `scripts/clean_data.py`

**Responsibility**:
- Separate items by commas
- Remove whitespace
- Filter empty transactions
- Generate descriptive statistics

**Input**: `data/processed/loaded_transactions.json`

**Output**: 
- `data/processed/cleaned_transactions.json`
- `data/processed/cleaning_stats.json`

**XCom**: Publishes number of clean transactions and unique movies

---

### Task 3: Run Apriori
**File**: `scripts/apriori.py`

**Responsibility**:
- Complete Apriori algorithm implementation
- Find frequent itemsets
- Generate association rules
- Calculate metrics (support, confidence, lift)

**Input**: `data/processed/cleaned_transactions.json`

**Output**:
- `data/results/frequent_itemsets.json`
- `data/results/association_rules.json`

**XCom**: Publishes number of itemsets and rules found

**Algorithm**:
1. Generate size-1 itemsets
2. For each size k:
   - Generate size-k candidates
   - Prune using Apriori property
   - Calculate support and filter
3. Generate association rules
4. Calculate confidence and lift

---

### Task 4: Generate Report
**File**: `scripts/generate_report.py`

**Responsibility**:
- Create readable text report
- Export to CSV for Excel
- Generate summary statistics
- Produce actionable insights

**Input**:
- `data/results/frequent_itemsets.json`
- `data/results/association_rules.json`

**Output**:
- `data/results/analysis_report.txt`
- `data/results/frequent_itemsets.csv`
- `data/results/association_rules.csv`
- `data/results/summary_statistics.json`

---

## 🔍 Results Verification

### 1. Verify DAG executed correctly
In Airflow UI, all tasks should be green (success).

### 2. Review main report
```bash
cat data/results/analysis_report.txt
```

### 3. Verify generated files
```bash
ls -la data/results/
```

You should see:
- `frequent_itemsets.json`
- `association_rules.json`
- `analysis_report.txt`
- `frequent_itemsets.csv`
- `association_rules.csv`
- `summary_statistics.json`

### 4. Open CSVs in Excel/Google Sheets
CSV files are ideal for visual analysis and filtering.

---

## ⚠️ Limitations

1. **Small Dataset**: Only 40 transactions for demonstration
2. **Simulated Data**: Not real transactions
3. **Limited Catalog**: Only 12 movies
4. **No Persistence**: Each execution overwrites previous results
5. **No Data Validation**: Doesn't handle edge cases or corrupted data
6. **Fixed Parameters**: Min support, confidence and lift don't adjust dynamically

---

## 🚀 Future Improvements

### Functionality
- [ ] Support for multiple CSV files (incremental processing)
- [ ] Day-to-day trend comparison
- [ ] Seasonal pattern detection
- [ ] Alert system for anomalous patterns
- [ ] REST API to query results

### Visualization
- [ ] Interactive dashboard with Plotly/Dash
- [ ] Association network graphs
- [ ] Co-occurrence heatmaps
- [ ] 3D lift visualization

### Scalability
- [ ] Database integration (PostgreSQL)
- [ ] Distributed processing with Spark
- [ ] Frequent itemsets caching
- [ ] Calculation parallelization

### Intelligence
- [ ] Automatic parameter adjustment
- [ ] Movie clustering by patterns
- [ ] Future trend prediction
- [ ] Personalized recommendations per customer

### DevOps
- [ ] Unit and integration tests
- [ ] CI/CD with GitHub Actions
- [ ] Pipeline Dockerization
- [ ] Monitoring with Prometheus/Grafana

---

## 🤝 Contributions

This is an individual academic project, but suggestions are welcome:

1. Fork the repository
2. Create branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is for academic and educational purposes.

---

## 👤 Author

**Diego De Gante**
- Final Project - Data Mining
- [Universidad Politécnica de Yucatán]
- [degantediego@gmail.com]

---

## 📚 References

- Agrawal, R., & Srikant, R. (1994). Fast algorithms for mining association rules
- Apache Airflow Documentation: https://airflow.apache.org/
- Python Documentation: https://docs.python.org/

---

## ❓ FAQ

**Q: Why use Airflow for such a small project?**

A: Although the dataset is small, Airflow demonstrates pipeline orchestration skills that are critical in production environments. It's practice for larger projects.

**Q: Can I use my own data?**

A: Yes! Replace `data/raw/data.csv` with your own file following the same format.

**Q: How do I change Apriori parameters?**

A: Edit the lines in `scripts/apriori.py` and in the DAG where `AprioriAlgorithm` is initialized.

**Q: Is the algorithm efficient for large data?**

A: This implementation is optimized for clarity, not scale. For millions of transactions, consider Spark MLlib or optimized implementations.

**Q: Why not use mlxtend?**

A: The project requires manual implementation to demonstrate understanding of the algorithm.

---

## Thank you for reviewing this project!

If you have questions or suggestions, don't hesitate to contact me.
