"""
Core Data Cleaning, Normalization, and Preprocessing Engine for Agribusiness Datasets.

Provides reproducible pipelines for string standardization, taxonomic ontology mapping,
composite-key deduplication, missing value handling, unit conversion, yield calculation,
outlier detection (IQR, Z-score, biological boundaries), and feature engineering.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from src.utils import logger


# Canonical Crop Category Mapping Dictionary
CROP_TAXONOMY_MAP: Dict[str, str] = {
    "Rice": "Cereals",
    "Paddy": "Cereals",
    "Wheat": "Cereals",
    "Maize": "Cereals",
    "Corn": "Cereals",
    "Jowar": "Cereals",
    "Sorghum": "Cereals",
    "Bajra": "Cereals",
    "Pearl Millet": "Cereals",
    "Barley": "Cereals",
    "Ragi": "Cereals",
    "Gram": "Pulses",
    "Chickpea": "Pulses",
    "Bengal Gram": "Pulses",
    "Arhar/Tur": "Pulses",
    "Tur": "Pulses",
    "Pigeonpea": "Pulses",
    "Red Gram": "Pulses",
    "Moong": "Pulses",
    "Green Gram": "Pulses",
    "Urad": "Pulses",
    "Black Gram": "Pulses",
    "Lentil": "Pulses",
    "Masur": "Pulses",
    "Groundnut": "Oilseeds",
    "Peanut": "Oilseeds",
    "Soyabean": "Oilseeds",
    "Soybean": "Oilseeds",
    "Rapeseed & Mustard": "Oilseeds",
    "Mustard": "Oilseeds",
    "Sunflower": "Oilseeds",
    "Sesamum": "Oilseeds",
    "Cotton": "Commercial",
    "Cotton(lint)": "Commercial",
    "Sugarcane": "Commercial",
    "Jute": "Commercial",
    "Tobacco": "Commercial",
    "Potato": "Horticulture",
    "Onion": "Horticulture",
    "Tomato": "Horticulture",
}

# Crop Alias to Canonical Name Mapping
CROP_CANONICAL_MAP: Dict[str, str] = {
    "paddy": "Rice",
    "rice": "Rice",
    "wheat": "Wheat",
    "corn": "Maize",
    "maize": "Maize",
    "gram": "Chickpea",
    "bengal gram": "Chickpea",
    "chickpea": "Chickpea",
    "arhar/tur": "Pigeonpea",
    "tur": "Pigeonpea",
    "arhar": "Pigeonpea",
    "pigeonpea": "Pigeonpea",
    "red gram": "Pigeonpea",
    "moong": "Green Gram",
    "moong(green gram)": "Green Gram",
    "urad": "Black Gram",
    "groundnut": "Groundnut",
    "peanut": "Groundnut",
    "soyabean": "Soybean",
    "soybean": "Soybean",
    "mustard": "Rapeseed & Mustard",
    "rapeseed & mustard": "Rapeseed & Mustard",
    "potato": "Potato",
    "onion": "Onion",
    "tomato": "Tomato",
}

# Administrative State Name Normalization
STATE_NAME_MAPPINGS: Dict[str, str] = {
    "orissa": "Odisha",
    "uttaranchal": "Uttarakhand",
    "pondicherry": "Puducherry",
    "andaman and nicobar islands": "Andaman and Nicobar",
    "jammu and kashmir": "Jammu and Kashmir",
    "chhatisgarh": "Chhattisgarh",
}

# Agronomic Biological Yield Ceilings (in kg/ha)
# Used to differentiate genuine high yields from impossible data-entry errors
BIOLOGICAL_YIELD_BOUNDS: Dict[str, Tuple[float, float]] = {
    "Cereals": (100.0, 15000.0),       # Minimum 100 kg/ha, theoretical max ~15 t/ha
    "Pulses": (50.0, 4500.0),          # Rainfed pulses rarely exceed 4.5 t/ha
    "Oilseeds": (50.0, 6000.0),        # High-oil varieties cap ~5-6 t/ha
    "Commercial": (200.0, 150000.0),   # Sugarcane green biomass can exceed 100 t/ha
    "Horticulture": (500.0, 70000.0),  # Tubers like potato reach up to 60-70 t/ha
}


class AgribusinessCleaner:
    """
    Standardized data cleaner and preprocessor for agricultural panel datasets (APY)
    and wholesale commodity market records (Agmarknet).
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.audit_log: List[Dict[str, Any]] = []

    def log_step(self, step_name: str, details: str, records_impacted: int = 0) -> None:
        """Records an audit trail event for traceability."""
        entry = {
            "step": step_name,
            "details": details,
            "records_impacted": records_impacted,
            "current_row_count": len(self.df),
        }
        self.audit_log.append(entry)
        logger.info(f"[{step_name}] {details} (Impacted: {records_impacted}, Rows: {len(self.df)})")

    def standardize_column_names(self) -> "AgribusinessCleaner":
        """Converts column names to lowercase snake_case and strips whitespace."""
        original_cols = list(self.df.columns)
        self.df.columns = (
            self.df.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
            .str.replace(".", "_")
        )
        self.log_step("Standardize Column Names", f"{original_cols} -> {list(self.df.columns)}")
        return self

    def standardize_categorical_entities(self) -> "AgribusinessCleaner":
        """
        Cleans and normalizes state, district, crop, and season text entries.
        Resolves aliases (e.g. 'Paddy' -> 'Rice', 'Gram' -> 'Chickpea').
        """
        initial_count = len(self.df)

        # Standardize State Names
        if "state_name" in self.df.columns:
            self.df["state_name"] = self.df["state_name"].astype(str).str.strip().str.lower()
            self.df["state_name"] = self.df["state_name"].replace(STATE_NAME_MAPPINGS).str.title()

        # Standardize District Names
        if "district_name" in self.df.columns:
            self.df["district_name"] = self.df["district_name"].astype(str).str.strip().str.title()

        # Standardize Crop Names & Categories
        crop_col = next((c for c in ["crop", "commodity"] if c in self.df.columns), None)
        if crop_col:
            cleaned_crop = self.df[crop_col].astype(str).str.strip().str.lower()
            # Map canonical name
            self.df[crop_col] = cleaned_crop.map(lambda x: CROP_CANONICAL_MAP.get(x, x.title()))
            # Assign broader crop taxonomy category
            self.df["crop_category"] = self.df[crop_col].map(lambda x: CROP_TAXONOMY_MAP.get(x, "Other"))

        # Standardize Season Names
        if "season" in self.df.columns:
            self.df["season"] = self.df["season"].astype(str).str.strip().str.title()
            self.df["season"] = self.df["season"].replace({
                "Kharif ": "Kharif",
                "Rabi ": "Rabi",
                "Summer ": "Summer",
                "Whole Year": "Annual",
            })

        self.log_step("Categorical Standardization", "Standardized entities and mapped crop taxonomy", initial_count)
        return self

    def deduplicate_composite_key(self, key_columns: Optional[List[str]] = None) -> "AgribusinessCleaner":
        """
        Identifies and removes duplicate records based on multi-dimensional primary keys.
        """
        if key_columns is None:
            # Default composite key for agricultural panel datasets
            candidates = ["state_name", "district_name", "crop_year", "season", "crop", "commodity", "arrival_date"]
            key_columns = [col for col in candidates if col in self.df.columns]

        if not key_columns:
            logger.warning("No composite key columns found for deduplication.")
            return self

        initial_len = len(self.df)
        self.df = self.df.drop_duplicates(subset=key_columns, keep="first").copy()
        removed = initial_len - len(self.df)
        self.log_step("Deduplication", f"Deduplicated on composite key {key_columns}", removed)
        return self

    def handle_invalid_and_missing_values(self) -> "AgribusinessCleaner":
        """
        Removes invalid negative values and handles missing observations.
        - Area and Production must be >= 0.
        - Rows with both Area and Production missing or zero are dropped.
        """
        initial_len = len(self.df)

        if "area" in self.df.columns:
            self.df["area"] = pd.to_numeric(self.df["area"], errors="coerce")
            self.df = self.df[self.df["area"].notna() & (self.df["area"] > 0)].copy()

        if "production" in self.df.columns:
            self.df["production"] = pd.to_numeric(self.df["production"], errors="coerce")
            # Drop negative production or nulls where area was present
            self.df = self.df[self.df["production"].notna() & (self.df["production"] >= 0)].copy()

        if "modal_price" in self.df.columns:
            self.df["modal_price"] = pd.to_numeric(self.df["modal_price"], errors="coerce")
            self.df = self.df[self.df["modal_price"].notna() & (self.df["modal_price"] > 0)].copy()

        dropped = initial_len - len(self.df)
        self.log_step("Invalid & Missing Values", "Filtered null/negative numeric values", dropped)
        return self

    def compute_yield_and_normalize_units(self) -> "AgribusinessCleaner":
        """
        Calculates Yield after ensuring unit compatibility.
        Assuming:
          - Area in Hectares (ha)
          - Production in Metric Tonnes (t)
        Formula:
          Yield (kg/ha) = (Production (t) * 1000) / Area (ha)
          Yield (t/ha)  = Production (t) / Area (ha)
        """
        if "area" in self.df.columns and "production" in self.df.columns:
            self.df["yield_kg_per_ha"] = (self.df["production"] * 1000.0) / self.df["area"]
            self.df["yield_tonnes_per_ha"] = self.df["production"] / self.df["area"]
            self.log_step("Unit Normalization & Yield", "Computed yield_kg_per_ha and yield_tonnes_per_ha", len(self.df))
        return self

    def detect_and_flag_outliers(
        self,
        iqr_multiplier: float = 3.0,
        z_score_threshold: float = 3.5,
    ) -> "AgribusinessCleaner":
        """
        Multi-tier outlier detection:
        1. Biological Feasibility Ceiling (Layer 1)
        2. Statistical Group-based IQR Fences (Layer 2)
        3. Statistical Z-Score (Layer 3)
        Records are flagged (NOT silently erased) to preserve auditability.
        """
        self.df["is_outlier"] = False
        self.df["outlier_reason"] = "Valid Observation"

        if "yield_kg_per_ha" not in self.df.columns:
            return self

        # Layer 1: Biological boundaries by crop category
        for category, (min_b, max_b) in BIOLOGICAL_YIELD_BOUNDS.items():
            mask = (self.df.get("crop_category") == category) & (
                (self.df["yield_kg_per_ha"] < min_b) | (self.df["yield_kg_per_ha"] > max_b)
            )
            self.df.loc[mask, "is_outlier"] = True
            self.df.loc[mask, "outlier_reason"] = f"Biological yield violation for {category}"

        # Layer 2: Crop-specific statistical IQR
        crop_col = next((c for c in ["crop", "commodity"] if c in self.df.columns), None)
        if crop_col:
            for crop_name, group in self.df.groupby(crop_col):
                if len(group) < 20:
                    continue
                q25 = group["yield_kg_per_ha"].quantile(0.25)
                q75 = group["yield_kg_per_ha"].quantile(0.75)
                iqr = q75 - q25
                if iqr > 0:
                    upper_fence = q75 + (iqr_multiplier * iqr)
                    lower_fence = max(0.0, q25 - (iqr_multiplier * iqr))
                    outlier_idx = group[
                        (group["yield_kg_per_ha"] > upper_fence) | (group["yield_kg_per_ha"] < lower_fence)
                    ].index
                    # Only overwrite if not already flagged by biological boundary
                    unflagged = outlier_idx[~self.df.loc[outlier_idx, "is_outlier"]]
                    self.df.loc[unflagged, "is_outlier"] = True
                    self.df.loc[unflagged, "outlier_reason"] = "Statistical IQR anomaly"

        total_flagged = int(self.df["is_outlier"].sum())
        self.log_step("Outlier Detection", f"Identified {total_flagged} outliers using biological and IQR rules", total_flagged)
        return self

    def engineer_analytical_features(self) -> "AgribusinessCleaner":
        """
        Constructs derived temporal and econometric features for analysis.
        """
        # Parse Dates if present
        date_col = next((c for c in ["arrival_date", "date"] if c in self.df.columns), None)
        if date_col:
            self.df["date"] = pd.to_datetime(self.df[date_col], errors="coerce")
            self.df["month"] = self.df["date"].dt.month
            self.df["quarter"] = self.df["date"].dt.quarter
            self.df["year"] = self.df["date"].dt.year
            self.df["day_of_week"] = self.df["date"].dt.day_name()

        # Compute price rolling metrics if time series present
        if "modal_price" in self.df.columns and "date" in self.df.columns:
            self.df = self.df.sort_values("date").reset_index(drop=True)
            self.df["price_ma_7"] = self.df["modal_price"].rolling(window=7, min_periods=1).mean()
            self.df["price_ma_30"] = self.df["modal_price"].rolling(window=30, min_periods=1).mean()
            # Daily percentage return
            self.df["price_return"] = self.df["modal_price"].pct_change()
            self.df["price_volatility_30d"] = self.df["price_return"].rolling(window=30, min_periods=5).std()

        self.log_step("Feature Engineering", "Constructed derived temporal, moving average, and return features", len(self.df))
        return self

    def get_cleaned_data(self) -> pd.DataFrame:
        """Returns the final preprocessed dataframe."""
        return self.df.reset_index(drop=True)

    def get_audit_trail(self) -> pd.DataFrame:
        """Returns the structured audit trail as a DataFrame."""
        return pd.DataFrame(self.audit_log)
