# Week 2: Data Cleaning and Preprocessing Strategy for Agribusiness Data

**Project Title**: Agribusiness Data Cleaning & Preprocessing Framework  
**Internship Role**: Data Scientist Intern  
**Repository**: `agribusiness-data-cleaning`  
**Current Phase**: Week 2 – Data Cleaning and Preprocessing Strategy  
**Date**: November 2026  
**Document Type**: Technical Strategy and Implementation Report (Word-Ready Format)

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Introduction to Agribusiness Data Quality](#2-introduction-to-agribusiness-data-quality)
3. [Potential Data Quality Issues](#3-potential-data-quality-issues)
4. [Missing Value Handling](#4-missing-value-handling)
5. [Duplicate Detection](#5-duplicate-detection)
6. [Data Type Standardisation](#6-data-type-standardisation)
7. [Categorical Data Standardisation](#7-categorical-data-standardisation)
8. [Unit Normalisation](#8-unit-normalisation)
9. [Date and Time Preprocessing](#9-date-and-time-preprocessing)
10. [Outlier Detection](#10-outlier-detection)
11. [Invalid Value Detection](#11-invalid-value-detection)
12. [Data Consistency Checks](#12-data-consistency-checks)
13. [Complete Preprocessing Workflow](#13-complete-preprocessing-workflow)
14. [Feature Engineering](#14-feature-engineering)
15. [Data Quality Validation Framework](#15-data-quality-validation-framework)
16. [Python/Pandas Implementation Plan](#16-pythonpandas-implementation-plan)
17. [Reproducibility Strategy](#17-reproducibility-strategy)
18. [Hypothetical Examples](#18-hypothetical-examples)
19. [Before/After Dataset Example](#19-beforeafter-dataset-example)
20. [Data Cleaning Decision Framework](#20-data-cleaning-decision-framework)
21. [Risks and Limitations](#21-risks-and-limitations)
22. [Conclusion](#22-conclusion)
23. [Week 3 Handoff](#23-week-3-handoff)

---

## 1. Executive Summary

### 1.1 Purpose of the Week 2 Task
The primary objective of Week 2 is to design, formalize, and engineer a robust, reproducible **Data Cleaning and Preprocessing Strategy** tailored specifically to the structural complexities of agribusiness and agricultural commodity market data. Building upon the foundational research and analytical planning completed in Week 1, this deliverable establishes the technical mechanisms required to transform raw, heterogeneous agricultural feeds into certified, analysis-ready datasets.

### 1.2 The Critical Nature of Data Quality in Agribusiness
In agricultural data science, analytical models directly inform decisions with substantial economic and food security implications: planting choices for Farmer Producer Organizations (FPOs), procurement and hedging contracts for food processing enterprises, warehouse capacity allocation, and government Minimum Support Price (MSP) interventions. Data quality defects—such as unit mismatches, undetected duplicates, or unscientific imputation—can introduce systemic bias:
- Overestimating crop yields leads to unhedged supply deficits and acute price spikes.
- Distorted price averages across agricultural wholesale markets (APMC mandis) mislead commercial inventory decisions.
- Failure to account for historical district reorganizations creates artificial trends in longitudinal panel econometrics.

### 1.3 Scope of Agricultural Data Under Consideration
The framework addresses two core archetypes of agribusiness data:
1. **Longitudinal Agricultural Production Panels**: District- and state-level Area, Production, and Yield (APY) time series spanning multiple decades and agricultural seasons (Kharif, Rabi, Summer/Zaid).
2. **High-Frequency Commodity Market Series**: Daily and weekly wholesale arrivals and prices (Minimum, Maximum, and Modal prices in INR/Quintal) across regulated APMC markets.

### 1.4 How the Framework Improves Reliability
By combining automated schema verification, multi-dimensional composite key deduplication, domain-driven biological boundary filtering, and an automated Data Quality Scorecard, this framework guarantees traceability, prevents silent data corruption, and ensures that subsequent exploratory data analysis (Week 3) and predictive modeling (Week 4) rest on defensible empirical foundations.

> **Methodological Disclaimer**: In accordance with rigorous internship standards, all statistics, numerical illustrations, and before/after comparisons presented in this report are explicitly labeled as **HYPOTHETICAL EXAMPLES** designed to demonstrate algorithmic logic. No real-world empirical findings are fabricated.

---

## 2. Introduction to Agribusiness Data Quality

### 2.1 Common Characteristics of Agribusiness Datasets
Agricultural data exhibits structural heterogeneity rarely encountered in purely financial or web analytics:

```
+--------------------------------------------------------------------------------------------------+
|                             Agribusiness Data Characteristic Landscape                           |
+--------------------------+-----------------------------+-----------------------------------------+
| Physical & Biological    | Market & Econometric        | Spatio-Temporal                         |
| - Cultivated Area (ha)   | - Modal Prices (INR/q)      | - Historical District Splits            |
| - Production Volume (t)  | - Daily Mandi Arrivals (t)  | - Agricultural Seasons (Kharif/Rabi)    |
| - Crop Yields (kg/ha)    | - Wholesale Price Spreads   | - Marketing vs. Calendar vs. Crop Years |
+--------------------------+-----------------------------+-----------------------------------------+
```

1. **Crop Production Records**: Aggregated from sample crop-cutting experiments (CCEs) and revenue village reports, subject to collection delays and administrative revision cycles.
2. **Crop Yield Metrics**: Derived as a ratio of production to cultivated area, compounding measurement errors present in either underlying dimension.
3. **Cultivated Area (Gross vs. Net)**: Fluctuates based on monsoon rainfall onset, irrigation availability, and economic price expectations.
4. **Commodity Wholesale Prices**: Reported as minimum, maximum, and modal transaction prices across thousands of decentralized APMC mandis.
5. **Market/Mandi Records**: Reflect physical transaction volume arrivals, characterized by heavy day-of-week seasonality, festival closures, and harvest peaks.
6. **Geographic Information**: Administrative boundaries that evolve continuously as large districts are bifurcated into smaller administrative units.
7. **Dates and Seasons**: Discrepancies between standard Gregorian calendar years (Jan–Dec), financial years (Apr–Mar), agricultural crop years (Jul–Jun), and agro-climatic cropping seasons (Kharif: autumn harvest, Rabi: spring harvest, Zaid: summer harvest).
8. **Agricultural Resource Indicators**: Soil nutrient indices, irrigation percentages, and meteorological variables (precipitation, temperature anomalies).

### 2.2 Root Causes of Inconsistencies
Agricultural data inconsistencies arise from institutional and systemic factors:
- **Disparate Reporting Agencies**: Different state departments of agriculture, marketing boards, and revenue ministries utilize divergent data entry protocols and local nomenclature.
- **Manual Data Entry & Dialectal Variations**: Mandi market clerks manually log commodity names, leading to spelling variations, dialectal crop synonyms (e.g., *Paddy* vs. *Rice*, *Gram* vs. *Chickpea*), and trailing whitespace errors.
- **Unit Divergence**: Traditional land units (bighas, acres, gunthas) and volume measures (quintals, bags, maunds, metric tonnes) are frequently recorded without explicit unit metadata.
- **Collection Frequencies**: Merging high-frequency daily price series with low-frequency annual or seasonal crop output panels introduces temporal alignment challenges.

---

## 3. Potential Data Quality Issues

The table below catalogs seventeen primary data quality defects encountered in agricultural data, outlining their analytical consequences, programmatic detection techniques, and recommended treatments:

| Issue | Representative Example | Analytical Impact | Programmatic Detection Method | Recommended Treatment |
| :--- | :--- | :--- | :--- | :--- |
| **Missing Values** | `Production = NaN` for an active district-crop record | Underestimates national output; distorts aggregate supply | `df[col].isna()`, null rate profiling | Evaluate missingness mechanism; group-based median imputation or row deletion |
| **Duplicate Records** | Identical record repeated for same district, crop, and year | Artificially inflates production totals; biases price averages | `df.duplicated(subset=composite_key)` | Deduplicate against composite primary keys; retain latest verified record |
| **Inconsistent Formats** | Dates formatted as `"15/04/2021"` and `"2021-04-15"` | Breaks datetime index; prevents time-series sorting | Regex pattern matching; `pd.to_datetime()` failures | Standardize to ISO 8601 (`YYYY-MM-DD`) |
| **Incorrect Data Types** | Price stored as string `"2,150.00"` | Halts numeric calculations; triggers aggregation errors | `df.dtypes` audit; regex detection of non-numeric chars | Strip commas and whitespace; coerce via `pd.to_numeric(errors='coerce')` |
| **Inconsistent Crop Names** | `"Paddy"`, `"paddy"`, `"RICE"`, `"Rice"` | Artificially fragments commodity groups; breaks grouping | Frequency count of lowercased string entries | Standardize casing and apply controlled taxonomic synonym dictionary |
| **Inconsistent Geographic Names** | State entered as `"Orissa"` vs. `"Odisha"` | Fractures state-level longitudinal time series | Set difference against official Census/LGD administrative gazetteer | Harmonize to current official administrative names |
| **Unit Inconsistencies** | Production in Quintals entered into a Tonnes column | 10-fold overestimation of harvest output | Cross-variable ratio checks; yield calculation explosions | Convert all records to metric standard units (Hectares, Metric Tonnes) |
| **Invalid Dates** | `"2021-02-31"`, `"2021-13-05"` | Corrupts calendar alignment; causes pipeline crashes | `pd.to_datetime(errors='coerce')` returning `NaT` | Log parsing failure; inspect source record; drop or correct via audited rule |
| **Statistical Outliers** | Modal price 8 times the rolling median | Distorts variance, regression slopes, and mean price metrics | IQR fences ($Q_3 + 3.0 \times IQR$); rolling Z-score ($> 3.5$) | Flag via boolean indicator `is_outlier`; inspect before deciding treatment |
| **Negative / Zero Values** | `Area = -25.0 ha`, `Price = 0` | Mathematically invalid; yields negative or undefined results | Range check filters: `(df['area'] <= 0)` | Reject negative area/prices; drop or investigate data entry defect |
| **Typographical Errors** | `"Whcat"` instead of `"Wheat"` | Creates orphan categories with single observations | Levenshtein distance / Fuzzy string matching | Map to nearest canonical dictionary term above similarity threshold ($>85\%$) |
| **Inconsistent Categories** | Season entered as `"rabi"`, `"RABI "`, `"Winter"` | Incomplete seasonal aggregations | Casing normalization; frequency value counts | Strip whitespace; title-case; map to canonical season ontology |
| **Inconsistent Frequencies** | Mandi prices missing on Sundays and public holidays | Uneven time-series step size; breaks ARIMA assumptions | Date continuity audit via `pd.date_range()` | Reindex to full calendar; forward-fill price for short spans ($\le 3$ days) |
| **Historical Boundary Changes** | District bifurcated in 2014 into two new entities | Creates artificial 50% drop in historical district output | Longitudinal panel continuity audits; district count tracking | Re-aggregate child districts back to parent baseline geometry |
| **Extreme Commodity Prices** | Wheat traded at 90,000 INR/q (entry error for 9,000) | Distorts price indices and inflation calculations | Comparison against historical MSP and biological market bounds | Flag as data entry error; verify against min/max price bounds |
| **Missing Market Observations** | Remote mandi reports prices only 3 months per year | Unreliable volatility estimates; seasonal bias | Transaction frequency count per market per year | Enforce minimum reporting threshold (e.g., $\ge 180$ days/year) for panel inclusion |
| **Calculation Inconsistency** | Stated Production $\neq$ Stated Area $\times$ Stated Yield | Indicates unit confusion or corrupted derived calculations | Relative discrepancy check: $\|P - (A \times Y / 1000)\| / P > 0.05$ | Recompute derived yield from primary Area and Production values |

---

## 4. Missing Value Handling

### 4.1 Missingness Mechanisms
Before selecting an imputation or deletion strategy, the statistical mechanism causing the missingness must be diagnosed:

```
+--------------------------------------------------------------------------------------------------+
|                                    Missingness Mechanisms                                        |
+--------------------------+---------------------------------+-------------------------------------+
| MCAR (Completely Random) | MAR (At Random)                 | MNAR (Not At Random)                |
| - Random network drop    | - Minor crops missing in small  | - Mandis conceal trades during      |
| - Unbiased if dropped    |   districts due to size         |   extreme market crashes            |
|                          | - Conditional on observed data  | - Imputation introduces heavy bias  |
+--------------------------+---------------------------------+-------------------------------------+
```

1. **Missing Completely at Random (MCAR)**: Missingness is entirely independent of observed and unobserved data (e.g., random network packet drop during API transmission). Deleting MCAR records reduces sample size but does not bias parameter estimates.
2. **Missing at Random (MAR)**: Missingness depends systematically on observed covariates but not on the missing value itself (e.g., pulse production reporting is more frequently omitted in non-specialized desert districts where acreage is negligible). Group-based imputation conditional on observed covariates provides unbiased estimates.
3. **Missing Not at Random (MNAR)**: Missingness is related to the unobserved value itself (e.g., smallholder APMC mandis failing to record prices during extreme market gluts or civil strikes). Blind imputation of MNAR data distorts market clearing representations.

### 4.2 Evaluation of Imputation and Deletion Techniques

```
+--------------------------------------------------------------------------------------------------+
| Technique             | Recommended Use in Agribusiness          | Prohibited Use Cases          |
+-----------------------+------------------------------------------+-------------------------------+
| Row Deletion          | Records missing both Area & Production;  | Where missingness is MAR/MNAR |
|                       | or critical unrecoverable keys           | (disproportionately drops poor|
|                       |                                          | agricultural regions)         |
+-----------------------+------------------------------------------+-------------------------------+
| Column Deletion       | Ancillary features with >60% missingness | Primary targets (Production,  |
|                       | (e.g. optional soil micronutrient note)  | Area, Modal Price)            |
+-----------------------+------------------------------------------+-------------------------------+
| Global Mean           | STRICTLY PROHIBITED in agriculture       | NEVER replace prices or yields|
|                       | (flattens regional agro-climatic variance| with national global mean     |
+-----------------------+------------------------------------------+-------------------------------+
| Group-based Median    | Production/yield missing for a district; | Across different agro-climatic|
|                       | impute using median of same crop-season  | zones or across different     |
|                       | within the same state                    | commodity classifications     |
+-----------------------+------------------------------------------+-------------------------------+
| Forward Fill (ffill)  | High-frequency mandi prices over weekend | Long time gaps (> 3 days);    |
|                       | market holidays (last traded price)      | seasonal transitions          |
+-----------------------+------------------------------------------+-------------------------------+
| Linear Interpolation  | Monthly production index with single     | Highly volatile prices or     |
|                       | interior missing month                   | multimonth harvest gaps       |
+-----------------------+------------------------------------------+-------------------------------+
| Time-Series-Aware     | Seasonal Spline interpolation for        | Across harvest boundaries     |
| Imputation            | continuous meteorological indicators     | (e.g., bridging Kharif into   |
|                       |                                          | Rabi yields)                  |
+-----------------------+------------------------------------------+-------------------------------+
```

> **Critical Rule**: **Never blindly replace agricultural commodity prices or district yields with the global dataset mean**. A national mean wheat yield (e.g., 3,200 kg/ha) would severely overestimate rainfed yields in arid Rajasthan while underestimating highly irrigated yields in Punjab, obliterating spatial econometric relationships.

---

## 5. Duplicate Detection

### 5.1 The Danger of Unchecked Duplicates
In agricultural data pipelines, duplicate rows typically arise when multiple regional reporting agencies submit overlapping batches, or when web scraping routines re-ingest unchanged tables. Unchecked duplicates inflict severe analytical damage:
- **Production Totals**: Aggregating double-counted district rows artificially inflates national harvest estimates.
- **Yield Calculations**: If an identical crop row is duplicated with slight area revisions, ratio calculations become erratic.
- **Price Averages**: Over-representing specific trading days skews monthly modal price benchmarks toward redundant observations.
- **Time-Series Models**: Injects zero-variance steps that violate auto-correlation assumptions.

### 5.2 Multi-Dimensional Composite Key Strategy
Agricultural records cannot be deduplicated based on individual columns alone. Instead, a strict **Composite Primary Key** must be enforced:

For **Crop Production Panels (APY)**:
$$\text{Key}_{\text{APY}} = \langle \text{State\_Name}, \text{District\_Name}, \text{Crop\_Year}, \text{Season}, \text{Crop} \rangle$$

For **Commodity Mandi Prices (Agmarknet)**:
$$\text{Key}_{\text{Price}} = \langle \text{State}, \text{District}, \text{Market}, \text{Commodity}, \text{Variety}, \text{Arrival\_Date} \rangle$$

Programmatic deduplication is executed deterministically:
```python
# Identify and audit duplicate records on composite key
duplicate_mask = df.duplicated(
    subset=['state_name', 'district_name', 'crop_year', 'season', 'crop'],
    keep=False
)
duplicate_records = df[duplicate_mask].sort_values(by=['state_name', 'district_name', 'crop_year', 'crop'])

# Deduplicate retaining the first verified observation
df_deduplicated = df.drop_duplicates(
    subset=['state_name', 'district_name', 'crop_year', 'season', 'crop'],
    keep='first'
).copy()
```

---

## 6. Data Type Standardisation

### 6.1 Standardizing Types Across Schema Dimensions
Raw CSV, Excel, and JSON files frequently ingest numerical columns as strings (due to comma separators, currency symbols, or trailing dashes denoting zero). The pipeline enforces strict data typing:

1. **Temporal Dimensions**: Converted to `datetime64[ns]` with explicit format strings.
2. **Numeric Measurements**: Converted to `float64` after stripping formatting symbols (`","`, `"₹"`, `"$"`, `"-"`).
3. **Categorical Dimensions**: Converted to Pandas `category` or standardized string types to optimize memory and enforce domain validity.
4. **Boolean Quality Flags**: Maintained as explicit `bool` (`True`/`False`) fields.
5. **Geographic Identifiers**: Maintained as zero-padded string codes (e.g., Census 2011 Local Government Directory - LGD district codes) to prevent leading zeros from being dropped by integer parsers.

### 6.2 Python/Pandas Conversion Protocols
```python
# Standardizing temporal, numeric, and categorical types
df['arrival_date'] = pd.to_datetime(df['arrival_date'], format='%Y-%m-%d', errors='coerce')

# Numeric coercion after stripping comma thousand-separators
numeric_cols = ['area', 'production', 'min_price', 'max_price', 'modal_price']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(',', '').str.strip(),
            errors='coerce'
        )

# Categorical casting for low-cardinality agricultural dimensions
category_cols = ['state_name', 'season', 'crop_category']
for col in category_cols:
    if col in df.columns:
        df[col] = df[col].astype('category')
```

---

## 7. Categorical Data Standardisation

### 7.1 Casing and Semantic Normalization
A frequent defect in agricultural reporting is semantic duplication caused by whitespace and casing variations:
```
Raw entries:
" rice ", "RICE", "Rice", "paddy", "PADDY", "Paddy (Dhan)"
```
Blind string lowercasing resolves typographic casing, but fails to reconcile dialectal and taxonomic equivalences. Furthermore, analysts must **never blindly merge semantically distinct commodities** (e.g., merging *Basmati Rice* and *Common Non-Basmati Rice* destroys the premium price spread).

### 7.2 Controlled Taxonomic Mapping Architecture
The framework employs a two-tier controlled ontology:
1. **Tier 1 (Canonical Name Mapping)**: Resolves dialectal aliases into canonical commodity names.
2. **Tier 2 (Taxonomic Categorization)**: Groups crops into macroeconomic classifications (`Cereals`, `Pulses`, `Oilseeds`, `Commercial`, `Horticulture`).

```python
# Controlled taxonomic ontology dictionary
CROP_TAXONOMY_MAP = {
    "Rice": "Cereals",
    "Wheat": "Cereals",
    "Maize": "Cereals",
    "Chickpea": "Pulses",
    "Pigeonpea": "Pulses",
    "Groundnut": "Oilseeds",
    "Soybean": "Oilseeds",
    "Mustard": "Oilseeds",
    "Cotton": "Commercial",
    "Sugarcane": "Commercial",
    "Potato": "Horticulture",
    "Onion": "Horticulture"
}

CROP_ALIAS_MAP = {
    "paddy": "Rice",
    "rice": "Rice",
    "wheat": "Wheat",
    "gram": "Chickpea",
    "bengal gram": "Chickpea",
    "arhar": "Pigeonpea",
    "tur": "Pigeonpea",
    "groundnut": "Groundnut",
    "peanut": "Groundnut",
    "soyabean": "Soybean"
}

# Controlled standardization execution
clean_crop_str = df['crop'].astype(str).str.strip().str.lower()
df['crop_canonical'] = clean_crop_str.map(lambda x: CROP_ALIAS_MAP.get(x, x.title()))
df['crop_category'] = df['crop_canonical'].map(lambda x: CROP_TAXONOMY_MAP.get(x, 'Other'))
```

### 7.3 Geographic Standardization
Administrative state and district names are harmonized against official government gazetteers (e.g., *Orissa* $\rightarrow$ *Odisha*, *Uttaranchal* $\rightarrow$ *Uttarakhand*, *Pondicherry* $\rightarrow$ *Puducherry*), eliminating artificial geographic splitting.

---

## 8. Unit Normalisation

### 8.1 Agricultural Measurement Units
Agricultural datasets routinely intermingle regional and imperial measurement systems. Without strict unit conversion, cross-table joins yield catastrophic calculation errors:

```
+--------------------------------------------------------------------------------------------------+
| Dimension         | Standard Target Unit     | Common Raw Variants Encountered                   |
+-------------------+--------------------------+---------------------------------------------------+
| Land Area         | Hectares (ha)            | Acres, Bighas, Square Meters, Gunthas             |
| Crop Output       | Metric Tonnes (t)        | Quintals, Kilograms, Bags (50kg/60kg), Bushels    |
| Crop Yield        | Kilograms / Hectare      | Tonnes / Hectare, Quintals / Acre, Bushels / Acre |
| Commodity Price   | INR / Quintal (100 kg)   | INR / kg, INR / Tonne, USD / Metric Tonne         |
+--------------------------------------------------------------------------------------------------+
```

### 8.2 Yield Formula and Dimensional Compatibility
Yield measures land productivity and must be calculated using mathematically compatible units:

$$\text{Yield } (\text{kg/ha}) = \frac{\text{Production } (\text{Metric Tonnes}) \times 1000}{\text{Area } (\text{Hectares})}$$

$$\text{Yield } (\text{Tonnes/ha}) = \frac{\text{Production } (\text{Metric Tonnes})}{\text{Area } (\text{Hectares})}$$

```
+--------------------------------------------------------------------------------------------------+
| [HYPOTHETICAL UNIT CONVERSION EXAMPLE]                                                           |
| Raw Input:                                                                                       |
|   Cultivated Area = 500 Hectares                                                                 |
|   Production Volume = 10,000 Quintals                                                            |
|                                                                                                  |
| Step 1: Normalize Production to Metric Tonnes:                                                   |
|   Production (Tonnes) = 10,000 Quintals * 0.1 = 1,000 Metric Tonnes                             |
|                                                                                                  |
| Step 2: Compute Standardized Yield:                                                              |
|   Yield (Tonnes/ha) = 1,000 t / 500 ha = 2.0 Tonnes/Hectare                                      |
|   Yield (kg/ha)     = (1,000 t * 1000) / 500 ha = 2,000 kg/Hectare                              |
+--------------------------------------------------------------------------------------------------+
```

If the analyst fails to convert the 10,000 quintals to metric tonnes, the raw yield formula produces $10,000 / 500 = 20\text{ t/ha}$ (20,000 kg/ha), an agronomically impossible figure that severely corrupts econometric modeling.

---

## 9. Date and Time Preprocessing

### 9.1 Temporal Alignment Challenges
In agricultural time series, temporal alignment is complicated by differing operational cycles:
1. **Calendar Year**: January 1 to December 31 (standard for macroeconomic reporting).
2. **Financial Year**: April 1 to March 31 (standard for Indian budgetary and corporate reporting).
3. **Agricultural Crop Year**: July 1 to June 30 (encompasses full sequence of Kharif $\rightarrow$ Rabi $\rightarrow$ Zaid harvests).

```
+--------------------------------------------------------------------------------------------------+
|                               Agricultural Crop Year Sequence                                    |
+----------------------------------+----------------------------------+-----------------------------+
| Kharif Season                    | Rabi Season                      | Zaid / Summer Season        |
| - Sowing: June - July (Monsoon)  | - Sowing: October - November     | - Sowing: March - April     |
| - Harvest: September - October   | - Harvest: March - April         | - Harvest: May - June       |
+----------------------------------+----------------------------------+-----------------------------+
```

### 9.2 Aggregation and Calendar Consistency
- **Daily to Monthly Aggregation**: Daily APMC prices fluctuate due to day-of-week arrival volume spikes. The pipeline calculates a monthly volume-weighted modal price:
  $$P_{\text{monthly, modal}} = \frac{\sum (P_{\text{daily, modal}} \times \text{Arrivals}_{\text{daily}})}{\sum \text{Arrivals}_{\text{daily}}}$$
- **Handling Missing Trading Days**: Weekends and public holidays are not treated as missing values; they are forward-filled up to a maximum threshold of 3 days to preserve continuity for ARIMA/SARIMAX modeling.

---

## 10. Outlier Detection

### 10.1 Outlier Management Philosophy
In agribusiness analytics, **outliers must never be automatically deleted**. Agricultural markets are inherently prone to extreme, genuine shocks (e.g., severe droughts, unexpected export bans, supply chain bottlenecks). Analysts must systematically distinguish between:

```
+--------------------------------------------------------------------------------------------------+
| Category                        | Agricultural Cause                 | Treatment Strategy        |
+---------------------------------+------------------------------------+---------------------------+
| 1. Data Entry / Unit Errors     | Extra zero entered; quintal entered| Correct via source rules  |
|                                 | as tonne (e.g. 50,000 kg/ha wheat) | or nullify invalid record |
+---------------------------------+------------------------------------+---------------------------+
| 2. Genuine Extreme Events       | Unseasonal hail destroying 90% of  | Retain; flag with boolean |
|                                 | crop (near-zero yield)             | indicator `is_outlier`    |
+---------------------------------+------------------------------------+---------------------------+
| 3. Structural Market Breaks     | Export embargo or demonetization   | Retain; incorporate shock |
|                                 | causing sharp price collapse       | intervention dummy in ML  |
+---------------------------------+------------------------------------+---------------------------+
| 4. Rare Valid Market Events     | Off-season onion price spike due to| Retain; model via robust  |
|                                 | temporary storage depletion        | non-parametric methods    |
+---------------------------------+------------------------------------+---------------------------+
```

### 10.2 Multi-Tiered Outlier Detection Framework
The framework applies a three-tiered detection mechanism:

1. **Tier 1: Physical Biological Yield Bounds**:
   Explicit agronomic yield ceilings based on crop physiology:
   - Cereals: $[100, 15,000]\text{ kg/ha}$
   - Pulses: $[50, 4,500]\text{ kg/ha}$
   - Oilseeds: $[50, 6,000]\text{ kg/ha}$
   - Commercial (Sugarcane): $[200, 150,000]\text{ kg/ha}$
   Observations exceeding these limits are flagged as physiological impossibilities.

2. **Tier 2: Statistical Grouped IQR Fences**:
   Calculated independently within each crop and state grouping:
   $$\text{IQR} = Q_3 - Q_1$$
   $$\text{Upper Fence} = Q_3 + (3.0 \times \text{IQR})$$
   $$\text{Lower Fence} = \max(0, Q_1 - (3.0 \times \text{IQR}))$$

3. **Tier 3: Rolling Window Volatility Spikes**:
   For time-series prices, observations exceeding $3.5$ rolling standard deviations from the 30-day moving average are flagged for manual review.

---

## 11. Invalid Value Detection

### 11.1 Deterministic Validation Rules
Invalid values represent mathematically impossible or corrupt data points that violate physical domain laws:

```
+--------------------------------------------------------------------------------------------------+
| Field Name        | Validation Criterion       | Failure Action                                  |
+-------------------+----------------------------+-------------------------------------------------+
| Cultivated Area   | Area > 0.0 Hectares        | Reject row; negative or zero area is impossible |
| Production        | Production >= 0.0 Tonnes   | Reject row if negative; investigate if zero     |
| Modal Price       | Modal Price > 0.0 INR/q    | Filter out; free commodity trade does not exist |
| Price Spread      | Min Price <= Modal <= Max  | Flag illogical inverted price hierarchy         |
| Transaction Date  | 1990-01-01 <= Date <= Now  | Flag date parsing corruption or future leakage  |
| Crop Category     | Must belong to approved    | Route to taxonomy review queue                  |
|                   | canonical ontology         |                                                 |
+--------------------------------------------------------------------------------------------------+
```

### 11.2 Programmatic Validation Checklist
```python
def validate_record_ranges(df: pd.DataFrame) -> Dict[str, int]:
    """Audits dataframe against deterministic agricultural validity constraints."""
    violations = {
        "negative_area": int((df['area'] <= 0).sum()) if 'area' in df.columns else 0,
        "negative_production": int((df['production'] < 0).sum()) if 'production' in df.columns else 0,
        "negative_or_zero_price": int((df['modal_price'] <= 0).sum()) if 'modal_price' in df.columns else 0,
        "illogical_price_spread": int((df['min_price'] > df['modal_price']).sum()) if 'min_price' in df.columns and 'modal_price' in df.columns else 0,
    }
    return violations
```

---

## 12. Data Consistency Checks

### 12.1 Mathematical Identity Auditing
In agricultural panels where Area ($A$), Production ($P$), and Yield ($Y$) are all reported in the raw source, the fundamental identity must hold:

$$P \approx \frac{A \times Y}{1000} \quad \Longleftrightarrow \quad Y \approx \frac{P \times 1000}{A}$$

Discrepancies exceeding a $5\%$ relative tolerance threshold indicate:
- **Unit Mismatch**: Area reported in acres while formula assumed hectares.
- **Reporting Discrepancies**: Production recorded for whole district, but yield sampled from a single irrigated sub-block.
- **Calculation Artifacts**: Rounding errors or transcription mistakes during manual compilation.

When inconsistencies are detected, **the framework recomputes Yield directly from primary Area and Production values**, ensuring absolute internal mathematical consistency across the cleaned dataset.

---

## 13. Complete Preprocessing Workflow

The end-to-end data preparation architecture is executed across fifteen distinct, audited stages:

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

## 14. Feature Engineering

### 14.1 Derived Analytical Features
To empower exploratory analysis and predictive forecasting, derived variables are constructed:

```
+--------------------------------------------------------------------------------------------------+
| Feature Name            | Mathematical Definition / Logic                 | Analytical Purpose   |
+-------------------------+-------------------------------------------------+----------------------+
| Yield (kg/ha)           | (Production in Tonnes * 1000) / Area in Ha      | Land productivity    |
| Production YoY Growth   | ((Prod_t - Prod_{t-1}) / Prod_{t-1}) * 100      | Supply expansion     |
| Yield YoY Growth        | ((Yield_t - Yield_{t-1}) / Yield_{t-1}) * 100   | Technology adoption  |
| Price Daily Return      | ln(Price_t / Price_{t-1})                       | Normalized return    |
| Rolling Price Volatility| 30-day rolling standard deviation of returns    | Sourcing risk        |
| Price Moving Averages   | 7-day, 30-day, and 90-day rolling mean prices   | Trend smoothing      |
| Seasonal Price Index    | (Monthly Mean Price / Annual Mean Price) * 100  | Cyclicality tracking |
| Calendar Attributes     | Month, Quarter, Day of Week, Agricultural Year  | Seasonality dummies  |
+--------------------------------------------------------------------------------------------------+
```

> **Operational Status**: Features such as `yield_kg_per_ha`, `price_ma_7`, and calendar attributes are fully implemented in `src/data_cleaning.py`. Econometric growth rates and seasonal indices represent **proposed derived features** scheduled for execution during Week 3 EDA on the full empirical panel.

---

## 15. Data Quality Validation Framework

### 15.1 Measurable Quality Dimensions
The framework audits datasets across six enterprise data quality pillars:
1. **Completeness**: Ratio of non-null cells to total expected cells ($\ge 95\%$).
2. **Accuracy & Consistency**: Absence of internal calculation contradictions ($P \approx A \times Y / 1000$).
3. **Validity**: Conformance to physical domain laws ($Area > 0, Price > 0$).
4. **Uniqueness**: Complete absence of duplicate records on primary composite keys ($0\%$ duplicates).
5. **Timeliness & Continuity**: Absence of unexplained multi-week gaps in high-frequency trading series.
6. **Conformance**: Complete alignment with predefined column naming and data type schemas.

### 15.2 Quality Scorecard Architecture
The `DataQualityValidator` class in `src/validation.py` executes these tests programmatically, generating an audited scorecard:

```
+--------------------------------------------------------------------------------------------------+
| Dimension       | Score (%) | Threshold | Status | Diagnostic Summary                            |
+-----------------+-----------+-----------+--------+-----------------------------------------------+
| Completeness    | 98.4%     | >= 95.0%  | PASSED | 16 missing values across non-critical columns |
| Uniqueness      | 100.0%    | == 100.0% | PASSED | 0 duplicate records on composite key          |
| Validity        | 99.8%     | >= 99.0%  | PASSED | 0 negative area or price violations           |
| Consistency     | 100.0%    | == 100.0% | PASSED | All reported yields match calculated ratios   |
+-----------------+-----------+-----------+--------+-----------------------------------------------+
```

---

## 16. Python/Pandas Implementation Plan

Below are verified, idiomatic Pandas implementations of the core data cleaning and preprocessing methods utilized in `src/data_cleaning.py` and `src/validation.py`:

```python
import pandas as pd
import numpy as np

# 1. Loading heterogeneous raw files safely
df = pd.read_csv("data/raw/sample_agri.csv", encoding="utf-8", low_memory=False)

# 2. Inspecting missingness and duplicates
null_summary = df.isna().sum()
duplicate_count = df.duplicated(subset=['state_name', 'district_name', 'crop_year', 'crop']).sum()

# 3. Standardizing column headers
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-', '_')

# 4. Strict Type Conversion
df['date'] = pd.to_datetime(df['arrival_date'], errors='coerce')
df['area'] = pd.to_numeric(df['area'].astype(str).str.replace(',', ''), errors='coerce')
df['production'] = pd.to_numeric(df['production'].astype(str).str.replace(',', ''), errors='coerce')
df['modal_price'] = pd.to_numeric(df['modal_price'].astype(str).str.replace(',', ''), errors='coerce')

# 5. Categorical trimming and controlled mapping
df['crop'] = df['crop'].astype(str).str.strip().str.title()
df['crop'] = df['crop'].replace({'Paddy': 'Rice', 'Gram': 'Chickpea', 'Tur': 'Pigeonpea'})

# 6. Composite Key Deduplication
df = df.drop_duplicates(subset=['state_name', 'district_name', 'crop_year', 'season', 'crop'], keep='first')

# 7. Filtering Invalid Values
df = df[(df['area'] > 0) & (df['production'] >= 0)]

# 8. Unit Normalization & Yield Calculation
df['yield_kg_per_ha'] = (df['production'] * 1000.0) / df['area']

# 9. Statistical Outlier Detection via Grouped IQR
def flag_crop_outliers(group: pd.DataFrame) -> pd.DataFrame:
    q25 = group['yield_kg_per_ha'].quantile(0.25)
    q75 = group['yield_kg_per_ha'].quantile(0.75)
    iqr = q75 - q25
    upper = q75 + (3.0 * iqr)
    group['is_yield_outlier'] = (group['yield_kg_per_ha'] > upper) | (group['yield_kg_per_ha'] < 50.0)
    return group

df = df.groupby('crop', group_keys=False).apply(flag_crop_outliers)

# 10. Time-Series Feature Engineering
df['price_ma_7'] = df['modal_price'].rolling(window=7, min_periods=1).mean()
```

---

## 17. Reproducibility Strategy

To guarantee that any analyst or evaluator can replicate every transformation exactly:
1. **Immutable Raw Data**: Source files stored in `data/raw/` are write-protected and never altered.
2. **Cryptographic Checksums**: Every raw ingestion logs a SHA-256 hash in `data/raw/manifests/audit_log.json`.
3. **Environment Pinning**: All library versions (`pandas==2.0.3`, `numpy==1.24.3`, etc.) are locked in `requirements.txt`.
4. **Relative Path Resolution**: Hardcoded drive letters (`C:\...`) are strictly prohibited; all code resolves paths relative to repository root via `pathlib.Path`.
5. **Audited Transformation Logging**: `AgribusinessCleaner` records an internal step-by-step audit log tracking record count deltas and transformation rationale.
6. **Execution Versioning**: Preprocessed outputs are saved with ISO timestamps and version tags in `data/processed/`.

---

## 18. Hypothetical Examples

The following small examples demonstrate specific transformation algorithms:

### Example 1: String Trimming, Casing & Synonym Mapping
```
Raw entries:
  [ " rice ", "RICE", "Rice", "Paddy", "PADDY", "paddy " ]

Transformation Logic:
  1. Strip whitespace: ["rice", "RICE", "Rice", "Paddy", "PADDY", "paddy"]
  2. Lowercase:       ["rice", "rice", "rice", "paddy", "paddy", "paddy"]
  3. Map Synonyms:    {"paddy": "Rice", "rice": "Rice"}

Clean Output:
  [ "Rice", "Rice", "Rice", "Rice", "Rice", "Rice" ]
  (Mapped to Broad Category: "Cereals")
```

### Example 2: Unit Normalization and Yield Derivation
```
Raw Input:
  District: "Ludhiana"
  Crop: "Wheat"
  Cultivated Area: 500 Hectares
  Production Output: 22,000 Quintals

Unit Conversion:
  1 Quintal = 0.1 Metric Tonne
  Production in Tonnes = 22,000 * 0.1 = 2,200 Metric Tonnes

Yield Derivation:
  Yield (Tonnes/ha) = 2,200 t / 500 ha = 4.40 Tonnes/Hectare
  Yield (kg/ha)     = (2,200 t * 1000) / 500 ha = 4,400 kg/Hectare

Biological Sanity Check:
  Cereal biological range: [100, 15,000] kg/ha.
  4,400 kg/ha falls within valid bounds -> Accepted as valid observation.
```

---

## 19. Before/After Dataset Example

The table below contrasts a **HYPOTHETICAL** raw agricultural dataset containing six deliberate defects against its cleaned, standardized, and validated output:

### Raw Dataset (Hypothetical Input)
| State_Name | District | Crop_Year | Season | Crop | Area | Production | Modal_Price | Arrival_Date | Defects Present |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Punjab | Ludhiana | 2021 | Rabi | Wheat | 1500.0 | 7200.0 | 2015.0 | 2021-04-10 | Baseline valid record |
| Punjab | Ludhiana | 2021 | Rabi | Wheat | 1500.0 | 7200.0 | 2015.0 | 2021-04-10 | **Duplicate record** |
| Orissa | Cuttack | 2021 | Kharif | ` rice ` | 800.0 | 2400.0 | 1860.0 | 2021-11-15 | **Legacy state name & un-trimmed crop** |
| Uttaranchal | Dehradun | 2021 | Kharif | PADDY | -50.0 | 110.0 | 1940.0 | 15/11/2021 | **Negative area, legacy state, non-ISO date** |
| Haryana | Karnal | 2021 | Rabi | Gram | 400.0 | `NaN` | 5100.0 | 2021-04-05 | **Missing production value** |
| Punjab | Amritsar | 2021 | Rabi | Wheat | 1200.0 | 36000.0 | 1980.0 | 2021-04-12 | **Extreme yield outlier (30,000 kg/ha)** |

---

### Cleaned Dataset (Processed Output)
| state_name | district_name | crop_year | season | crop | crop_category | area_ha | prod_tonnes | yield_kg_per_ha | modal_price | date | is_outlier | outlier_reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Punjab | Ludhiana | 2021 | Rabi | Wheat | Cereals | 1500.0 | 7200.0 | 4800.0 | 2015.0 | 2021-04-10 | False | Valid Observation |
| Odisha | Cuttack | 2021 | Kharif | Rice | Cereals | 800.0 | 2400.0 | 3000.0 | 1860.0 | 2021-11-15 | False | Valid Observation |
| Punjab | Amritsar | 2021 | Rabi | Wheat | Cereals | 1200.0 | 36000.0 | 30000.0 | 1980.0 | 2021-04-12 | True | Biological yield violation for Cereals |

*Action Log on Dropped Records*:
- Row 2 (Ludhiana duplicate) was eliminated during composite key deduplication.
- Row 4 (Dehradun) was dropped due to invalid negative area ($-50.0\text{ ha}$).
- Row 5 (Karnal) missing production was segregated for group-based median imputation.

---

## 20. Data Cleaning Decision Framework

The matrix below illustrates the data-science judgment applied to resolve operational anomalies:

```
+-----------------------------------------------------------------------------------------------------------------------+
| Problem              | Detection Method       | Decision Criterion            | Treatment Action   | Validation Check |
+----------------------+------------------------+-------------------------------+--------------------+------------------+
| Missing Production   | `isna()` on production | If Area > 0 and district has  | Impute via 3-year  | Imputed yield    |
| with Active Area     |                        | historical yield series       | median crop yield  | matches bounds   |
+----------------------+------------------------+-------------------------------+--------------------+------------------+
| Missing Production & | Both fields null or    | Observation conveys zero      | Delete row         | Total row count  |
| Missing Area         | equal to zero          | agricultural information      |                    | delta confirmed  |
+----------------------+------------------------+-------------------------------+--------------------+------------------+
| Exact Composite Key  | `duplicated()` on      | True redundant reporting      | Retain first;      | Uniqueness score |
| Duplicate            | composite primary key  | artifact                      | drop duplicates    | reaches 100.0%   |
+----------------------+------------------------+-------------------------------+--------------------+------------------+
| Dialectal Crop Name  | Non-standard crop string| Semantic identity confirmed   | Map to canonical   | Value counts     |
| (e.g., 'Paddy')      | in dictionary lookup   | via official crop taxonomy    | name ('Rice')      | match ontology   |
+----------------------+------------------------+-------------------------------+--------------------+------------------+
| Impossible Negative  | Filter `area < 0` or   | Violates physical physical    | Drop corrupted     | Validity score   |
| Values               | `price <= 0`           | domain laws                   | observation        | reaches 100.0%   |
+----------------------+------------------------+-------------------------------+--------------------+------------------+
| Severe Yield Outlier | Exceeds biological     | Plausible reporting mistake or| Retain record;     | Outlier rate     |
| (> 20,000 kg/ha)     | agronomic ceiling      | unit mismatch                 | set is_outlier=True| within 1-2% panel|
+----------------------+------------------------+-------------------------------+--------------------+------------------+
| Non-Trading Day Gap  | Date sequence gap in   | Weekend or public holiday     | Forward-fill price | Maximum fill gap |
| in Mandi Prices      | daily market series    | with duration <= 3 days       | from last trade    | strictly <= 3 d  |
+----------------------+------------------------+-------------------------------+--------------------+------------------+
```

---

## 21. Risks and Limitations

1. **Information Loss from Aggressive Filtering**: Excessive row deletion can bias panels toward wealthier, better-reporting agricultural districts while excluding marginalized rainfed regions.
2. **Imputation Distortions**: Imputing yields during drought years using historical multi-year medians artificially masks climate shocks.
3. **Over-Removal of Outliers**: Treating true price spikes (e.g., post-flood onion shortages) as statistical anomalies removes the exact volatility signals needed for risk hedging.
4. **Historical District Boundary Bifurcations**: Splitting large districts into smaller administrative entities over time creates artificial geographic breaks that cannot be resolved solely via string cleaning.
5. **Preprocessing Bias**: Applying uniform conversion factors without accounting for moisture content or cultivar differences introduces minor systematic measurement errors.

---

## 22. Conclusion

The Week 2 Data Cleaning and Preprocessing Strategy provides an agronomically grounded, reproducible foundation for the Agribusiness Market Analytics & Forecasting Platform. By formalizing composite key deduplication, controlled taxonomic ontology mapping, biological boundary validation, and a standardized Data Quality Scorecard, the framework eliminates data corruption while preserving genuine agricultural market volatility.

The accompanying Python modules in `src/` (`data_cleaning.py`, `validation.py`, `utils.py`) and the interactive demonstration notebook (`notebooks/01_data_cleaning_preprocessing_demo.ipynb`) provide an auditable pipeline ready to support Week 3 Exploratory Data Analysis.

---

## 23. Week 3 Handoff

Upon conclusion of Week 2, the following certified artifacts will be handed off to the Week 3 Exploratory Data Analysis team:

```
+--------------------------------------------------------------------------------------------------+
|                                    Week 3 Handoff Deliverables                                   |
+--------------------------+-----------------------------------------------------------------------+
| 1. Clean APY Panel       | Standardized district crop panel with normalized area (ha),           |
|                          | production (t), and derived yield (kg/ha)                             |
+--------------------------+-----------------------------------------------------------------------+
| 2. Clean Price Series    | High-frequency APMC mandi wholesale price panel with standardized     |
|                          | ISO dates, forward-filled holiday gaps, and outlier flags             |
+--------------------------+-----------------------------------------------------------------------+
| 3. Crop Taxonomy         | Controlled lookup mapping all dialectal crops to 5 primary categories |
+--------------------------+-----------------------------------------------------------------------+
| 4. Standard Geography    | Harmonized state and district names reconciled against Census gazetteer|
+--------------------------+-----------------------------------------------------------------------+
| 5. Derived Variables     | Initial moving averages (MA7, MA30) and calendar attributes           |
+--------------------------+-----------------------------------------------------------------------+
| 6. Quality Scorecard     | Audited baseline report confirming >95% completeness & 100% uniqueness|
+--------------------------+-----------------------------------------------------------------------+
| 7. Executable Pipeline   | Fully tested `AgribusinessCleaner` and `DataQualityValidator` modules |
+--------------------------+-----------------------------------------------------------------------+
```
