# Agribusiness Data Cleaning & Preprocessing Framework

[![Current Milestone: Week 2 – Data Cleaning and Preprocessing Strategy](https://img.shields.io/badge/Milestone-Week%202%20%7C%20Data%20Cleaning%20Strategy-blue.svg)](reports/week2_data_cleaning_preprocessing_strategy.md)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

> **Project Phase**: **Week 2 – Data Cleaning and Preprocessing Strategy**  
> **Role**: Data Scientist Intern  
> **Repository**: `agribusiness-data-cleaning`  
> **Primary Deliverable**: [`reports/week2_data_cleaning_preprocessing_strategy.md`](reports/week2_data_cleaning_preprocessing_strategy.md)

---

## 1. Project Overview & Objective

Agricultural and agribusiness data pipelines operate in a uniquely challenging environment characterized by decentralized administrative reporting, legacy nomenclature, unit divergence, and volatile market dynamics.

The **Agribusiness Data Cleaning & Preprocessing Framework** establishes an auditable, reproducible, and agronomically grounded data cleaning pipeline designed to ingest raw, heterogeneous agricultural datasets and transform them into certified, analysis-ready tables.

Key project objectives include:
1. **Defensive Schema & Integrity Auditing**: Catching data entry defects, missing keys, and invalid formats upon ingestion.
2. **Harmonized Taxonomy & Geography**: Normalizing crop synonyms (`" rice "`, `"RICE"`, `"Paddy"` $\rightarrow$ `"Rice"`) and resolving historical state/district administrative naming changes.
3. **Unit Normalization & Yield Calculation**: Converting disparate measures into metric standards (Hectares, Metric Tonnes, kg/ha) and computing yield using compatible dimensions.
4. **Multi-Tiered Outlier Flagging**: Applying biological yield ceilings and statistical grouped IQR fences without blindly erasing genuine market volatility.
5. **Quality Scorecard Verification**: Programmatically auditing datasets across Completeness, Accuracy, Consistency, Validity, and Uniqueness.

> **Methodological Disclaimer**: In accordance with rigorous internship guidelines, all sample datasets and numerical demonstrations in this repository are **HYPOTHETICAL EXAMPLES** used strictly to validate cleaning algorithms. No real-world statistics or findings are fabricated.

---

## 2. Business Context & Data-Quality Challenges

Agribusiness decisions—ranging from smallholder planting advice to industrial procurement, warehousing logistics, and government price support policies—rely directly on trustworthy agricultural data.

Common data quality defects encountered in raw agricultural reporting include:
- **Missing Values**: Uninformative nulls, seasonal reporting omissions, and non-trading day gaps.
- **Duplicate Records**: Administrative double-counting that artificially inflates production and distorts price averages.
- **Unit Mismatches**: Entering production in quintals into a metric tonne column, inflating yields by a factor of 10.
- **Invalid & Impossible Values**: Corrupted negative values for cultivated area, production, or commodity prices.
- **Semantic Fragmentation**: Inconsistent spelling, dialectal aliases, and whitespace padding that fragment commodity groups.

---

## 3. Preprocessing Workflow

The pipeline executes through a sequence of fifteen audited transformation stages:

```
+--------------------------------------------------------------------------------------------------+
|                             Agribusiness Data Preprocessing Pipeline                             |
+--------------------------------------------------------------------------------------------------+
                                        [ 1. Raw Data Ingestion ]
                                                   ↓
                                        [ 2. Source Validation ]
                                 (Verify checksums, headers, encodings)
                                                   ↓
                                        [ 3. Schema Inspection ]
                                   (Detect missing mandatory columns)
                                                   ↓
                                     [ 4. Data Type Conversion ]
                                 (Coerce numeric, datetime, category)
                                                   ↓
                                  [ 5. Missing Value Assessment ]
                                 (Classify MCAR/MAR; drop or impute)
                                                   ↓
                                       [ 6. Duplicate Detection ]
                                (Filter multi-dimensional composite keys)
                                                   ↓
                                 [ 7. Categorical Standardisation ]
                               (Trim whitespace, title-case, map aliases)
                                                   ↓
                                       [ 8. Unit Normalisation ]
                              (Convert to Hectares, Metric Tonnes, kg/ha)
                                                   ↓
                                       [ 9. Date Preprocessing ]
                              (Standardize ISO 8601, map crop seasons)
                                                   ↓
                                    [ 10. Invalid Value Detection ]
                               (Eliminate negative area, price, or prod)
                                                   ↓
                                     [ 11. Outlier Flagging ]
                              (Apply biological ceilings & IQR fences)
                                                   ↓
                                    [ 12. Feature Engineering ]
                             (Compute growth rates, moving averages, lags)
                                                   ↓
                                    [ 13. Quality Scorecard ]
                              (Audit completeness, validity, consistency)
                                                   ↓
                                       [ 14. Clean Dataset ]
                                   (Immutable processed Parquet/CSV)
                                                   ↓
                                    [ 15. Analytical Dataset ]
                              (Subsets partitioned for Week 3 EDA & ML)
```

---

## 4. Repository Structure

```
agribusiness-data-cleaning/
│
├── README.md                                      # Executive overview, methodology & setup guide
├── requirements.txt                               # Pinned dependencies for reproducible execution
├── .gitignore                                     # Ignores virtualenvs, caches, and large raw data files
│
├── data/
│   ├── README.md                                  # Storage policies, data dictionary, and schemas
│   ├── raw/                                       # Immutable raw data snapshots (audit-tracked)
│   │   └── .gitkeep
│   └── processed/                                 # Cleaned, standardized Parquet/CSV tables
│       └── .gitkeep
│
├── notebooks/
│   └── 01_data_cleaning_preprocessing_demo.ipynb  # Interactive demonstration of cleaning & scorecard
│
├── src/
│   ├── __init__.py                                # Package initialization
│   ├── utils.py                                   # Standardized logging, SHA-256 hashing & timers
│   ├── data_cleaning.py                           # Core AgribusinessCleaner pipeline engine
│   └── validation.py                              # DataQualityValidator & automated scorecard engine
│
└── reports/
    └── week2_data_cleaning_preprocessing_strategy.md # Comprehensive 23-section technical report
```

---

## 5. Hypothetical Examples

### Example 1: Categorical Casing & Taxonomic Mapping
```
Raw entries:
  [ " rice ", "RICE", "Rice", "Paddy", "PADDY", "paddy " ]

Transformation Logic:
  1. Strip whitespace: ["rice", "RICE", "Rice", "Paddy", "PADDY", "paddy"]
  2. Lowercase:       ["rice", "rice", "rice", "paddy", "paddy", "paddy"]
  3. Map Synonyms:    {"paddy": "Rice", "rice": "Rice"}

Clean Output:
  [ "Rice", "Rice", "Rice", "Rice", "Rice", "Rice" ]
  (Assigned Category: "Cereals")
```

### Example 2: Unit Normalization and Yield Calculation
```
Raw Input:
  Cultivated Area = 500 Hectares
  Production Volume = 10,000 Quintals

Unit Conversion:
  Production (Tonnes) = 10,000 Quintals * 0.1 = 1,000 Metric Tonnes

Yield Calculation:
  Yield (Tonnes/ha) = 1,000 t / 500 ha = 2.0 Tonnes/Hectare
  Yield (kg/ha)     = (1,000 t * 1000) / 500 ha = 2,000 kg/Hectare
```

---

## 6. Technology Stack

- **Core Language**: [Python 3.10+](https://www.python.org/)
- **Data Wrangling & Pipeline**: [Pandas](https://pandas.pydata.org/) (v2.0+), [NumPy](https://numpy.org/) (v1.24+)
- **Spreadsheet Ingestion**: [OpenPyXL](https://openpyxl.readthedocs.io/) (v3.1+)
- **Interactive Development**: [Jupyter Notebook](https://jupyter.org/) (v7.0+)

---

## 7. How to Reproduce the Environment

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/agribusiness-data-cleaning.git
cd agribusiness-data-cleaning
```

### 2. Create and Activate Virtual Environment
```bash
# On Linux/macOS
python -m venv venv
source venv/bin/activate

# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run Demonstration Notebook
```bash
jupyter notebook notebooks/01_data_cleaning_preprocessing_demo.ipynb
```

---

## 8. Current Project Status & Week 3 Roadmap

- [x] **Week 1 Completed**: Agribusiness Data Analysis Planning & Source Sourcing (Separate repo).
- [x] **Week 2 Completed**:
  - Authoring of 23-section comprehensive technical strategy report (`reports/week2_data_cleaning_preprocessing_strategy.md`).
  - Modular implementation of `AgribusinessCleaner` and `DataQualityValidator` in `src/`.
  - Interactive demonstration notebook with pre/post scorecards (`notebooks/01_data_cleaning_preprocessing_demo.ipynb`).
  - Unit normalization, composite key deduplication, and biological boundary detection.
- [ ] **Week 3 Upcoming**: Exploratory Data Analysis (EDA), spatial yield choropleth mapping, and econometric hypothesis testing.
