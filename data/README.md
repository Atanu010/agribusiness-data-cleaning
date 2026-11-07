# Agribusiness Data Management & Storage Architecture

## 1. Overview and Storage Philosophy

This directory governs data storage, versioning, and validation for the **Agribusiness Data Cleaning & Preprocessing Framework** (Week 2).

In accordance with rigorous data science principles:
- **Raw Zone (`data/raw/`)**: Holds unaltered source extracts (e.g., APY crop statistics, Agmarknet mandi price series). Files are strictly **immutable** and treated as read-only snapshots.
- **Processed Zone (`data/processed/`)**: Contains standardized, deduplicated, outlier-flagged, and feature-engineered datasets stored in Apache Parquet (`.parquet`) and CSV formats.
- **Provenance & Auditing**: Every raw file must be accompanied by metadata records including ingestion timestamps and SHA-256 cryptographic hashes.

---

## 2. Directory Layout

```
data/
├── README.md                 # Storage policies, data dictionary, and schemas
├── raw/                      # Unaltered source files (excluded from git)
│   └── .gitkeep
└── processed/                # Preprocessed analytical tables
    └── .gitkeep
```

---

## 3. Data Dictionary & Standardized Units

To prevent discrepancies when merging heterogeneous agricultural reporting systems, the cleaning pipeline enforces the following standardized units:

| Dimension / Variable | Standardized Unit | Canonical Target Type | Conversion Rule from Common Variants |
| :--- | :--- | :--- | :--- |
| **State / Province** | Normalized Name | `category` / `string` | Stripped whitespace, Title Case, legacy mapping (e.g. *Orissa* $\rightarrow$ *Odisha*) |
| **District / County** | Normalized Name | `category` / `string` | Normalized Title Case; verified against official administrative gazetteer |
| **Crop / Commodity** | Canonical Item Name | `category` / `string` | Harmonized from trade/dialectal variants (e.g. *Paddy* $\rightarrow$ *Rice*, *Gram* $\rightarrow$ *Chickpea*) |
| **Crop Category** | Broad Taxonomy Group | `category` | High-level categorization: `Cereals`, `Pulses`, `Oilseeds`, `Commercial`, `Horticulture` |
| **Agricultural Season** | Canonical Season | `category` | Standardized categories: `Kharif`, `Rabi`, `Summer/Zaid`, `Annual` |
| **Cultivated Area** | **Hectares (ha)** | `float64` | $1\text{ Acre} = 0.404686\text{ ha}$; $1\text{ Hectare} = 2.47105\text{ Acres}$; $\ge 0$ |
| **Crop Production** | **Metric Tonnes (t)**| `float64` | $1\text{ Quintal} = 0.1\text{ Tonne}$; $1\text{ Tonne} = 1,000\text{ kg}$; $\ge 0$ |
| **Crop Yield** | **kg / Hectare (kg/ha)**| `float64` | $\text{Yield (kg/ha)} = \frac{\text{Production (t)} \times 1000}{\text{Area (ha)}}$; verified against biological bounds |
| **Wholesale Modal Price** | **INR / Quintal** | `float64` | Must satisfy $\text{Min Price} \le \text{Modal Price} \le \text{Max Price}$; $> 0$ |
| **Transaction Date** | **ISO 8601 (`YYYY-MM-DD`)**| `datetime64[ns]` | Standardized calendar date parsed with timezone awareness where applicable |

---

## 4. Immutability & Reproducibility Rules

1. **No Manual Edits**: Files in `data/raw/` must never be edited manually in Excel or text editors.
2. **Deterministic Processing**: Any dataset in `data/processed/` must be generated entirely through executable Python scripts in `src/`.
3. **Data Loss Prevention**: Outliers, missing entries, and structural breaks are flagged with explicit audit attributes (e.g., `is_outlier`, `imputed_flag`) rather than being silently deleted.
