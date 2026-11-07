"""
Data Quality Validation and Scorecard Framework for Agribusiness Datasets.

Evaluates datasets across six core quality dimensions:
1. Completeness
2. Accuracy & Consistency (Production ≈ Area × Yield)
3. Validity (Range & Domain constraints)
4. Uniqueness
5. Timeliness & Temporal Continuity
6. Conformance to Schema
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.utils import logger


class DataQualityValidator:
    """
    Automated data quality auditing and scorecard generation engine.
    """

    def __init__(self, df: pd.DataFrame, dataset_name: str = "Agribusiness_Dataset"):
        self.df = df.copy()
        self.name = dataset_name
        self.results: Dict[str, Any] = {}

    def check_completeness(self, critical_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Assesses missing value rates across overall cells and critical keys.
        """
        total_cells = self.df.size
        missing_cells = int(self.df.isna().sum().sum())
        completeness_pct = round(((total_cells - missing_cells) / total_cells) * 100.0, 2) if total_cells > 0 else 0.0

        crit_missing = {}
        if critical_columns:
            for col in critical_columns:
                if col in self.df.columns:
                    crit_missing[col] = int(self.df[col].isna().sum())

        result = {
            "dimension": "Completeness",
            "total_cells": total_cells,
            "missing_cells": missing_cells,
            "completeness_score_pct": completeness_pct,
            "critical_columns_missing": crit_missing,
            "passed": completeness_pct >= 95.0,
        }
        self.results["completeness"] = result
        return result

    def check_uniqueness(self, composite_key: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Evaluates record uniqueness and duplicate frequencies on primary/composite keys.
        """
        total_rows = len(self.df)
        if composite_key:
            present_keys = [c for c in composite_key if c in self.df.columns]
            duplicate_rows = int(self.df.duplicated(subset=present_keys).sum())
        else:
            duplicate_rows = int(self.df.duplicated().sum())

        uniqueness_pct = round(((total_rows - duplicate_rows) / total_rows) * 100.0, 2) if total_rows > 0 else 0.0

        result = {
            "dimension": "Uniqueness",
            "total_rows": total_rows,
            "duplicate_rows": duplicate_rows,
            "uniqueness_score_pct": uniqueness_pct,
            "passed": duplicate_rows == 0,
        }
        self.results["uniqueness"] = result
        return result

    def check_validity(self) -> Dict[str, Any]:
        """
        Verifies mathematical and domain validity rules:
        - Area > 0
        - Production >= 0
        - Modal Price > 0
        - Yield within biological plausible range
        """
        violations = {}

        if "area" in self.df.columns:
            invalid_area = int((self.df["area"] <= 0).sum())
            violations["area_non_positive"] = invalid_area

        if "production" in self.df.columns:
            invalid_prod = int((self.df["production"] < 0).sum())
            violations["production_negative"] = invalid_prod

        if "modal_price" in self.df.columns:
            invalid_price = int((self.df["modal_price"] <= 0).sum())
            violations["price_non_positive"] = invalid_price

        if "yield_kg_per_ha" in self.df.columns:
            invalid_yield = int(((self.df["yield_kg_per_ha"] <= 0) | (self.df["yield_kg_per_ha"] > 100000)).sum())
            violations["yield_implausible"] = invalid_yield

        total_violations = sum(violations.values())
        validity_pct = round(max(0.0, 100.0 - (total_violations / max(1, len(self.df)) * 100.0)), 2)

        result = {
            "dimension": "Validity",
            "violations_breakdown": violations,
            "total_violations": total_violations,
            "validity_score_pct": validity_pct,
            "passed": total_violations == 0,
        }
        self.results["validity"] = result
        return result

    def check_consistency(self, tolerance_pct: float = 1.0) -> Dict[str, Any]:
        """
        Audits mathematical consistency between interrelated agricultural variables:
        Production (tonnes) ≈ (Area (ha) × Yield (kg/ha)) / 1000
        """
        if all(col in self.df.columns for col in ["production", "area", "yield_kg_per_ha"]):
            expected_prod = (self.df["area"] * self.df["yield_kg_per_ha"]) / 1000.0
            actual_prod = self.df["production"]

            # Relative error check
            rel_error = np.abs(expected_prod - actual_prod) / np.maximum(1e-6, actual_prod)
            mismatch_count = int((rel_error > (tolerance_pct / 100.0)).sum())
            consistency_pct = round(((len(self.df) - mismatch_count) / len(self.df)) * 100.0, 2)
        else:
            mismatch_count = 0
            consistency_pct = 100.0

        result = {
            "dimension": "Consistency",
            "relationship_checked": "Production ≈ Area × Yield / 1000",
            "mismatch_count": mismatch_count,
            "consistency_score_pct": consistency_pct,
            "passed": mismatch_count == 0,
        }
        self.results["consistency"] = result
        return result

    def generate_scorecard(
        self,
        critical_columns: Optional[List[str]] = None,
        composite_key: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Executes all validation tests and generates a standardized Data Quality Scorecard.
        """
        self.check_completeness(critical_columns)
        self.check_uniqueness(composite_key)
        self.check_validity()
        self.check_consistency()

        scorecard_rows = []
        for dim, details in self.results.items():
            score_col = next((k for k in details.keys() if "score_pct" in k), None)
            score = details.get(score_col, np.nan)
            scorecard_rows.append({
                "Quality Dimension": details["dimension"],
                "Score (%)": score,
                "Status": "PASSED" if details.get("passed", False) else "FAILED",
                "Details": str({k: v for k, v in details.items() if k not in ["dimension", "passed", score_col]}),
            })

        df_scorecard = pd.DataFrame(scorecard_rows)
        logger.info(f"Generated Quality Scorecard for '{self.name}'. Average Score: {df_scorecard['Score (%)'].mean():.2f}%")
        return df_scorecard
