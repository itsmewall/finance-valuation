import pandas as pd
from typing import Dict, List

REQUIRED_COLUMNS = {
    "income_statement": [
        "year", "revenue", "cogs", "opex", "depreciation", "interest_expense", "taxes"
    ],
    "balance_sheet": [
        "year", "cash", "receivables", "inventory", "payables", "debt_short", "debt_long", "equity"
    ],
    "cash_flow": [
        "year", "cfo", "capex", "cfi_other", "cff_other"
    ]
}

def validate_data(data: Dict[str, pd.DataFrame]) -> None:
    """
    Validates that the required columns are present in each DataFrame.
    """
    for key, cols in REQUIRED_COLUMNS.items():
        if key not in data:
            raise ValueError(f"Missing dataframe for: {key}")
        
        df = data[key]
        missing = [col for col in cols if col not in df.columns]
        
        if missing:
            raise ValueError(f"Missing columns in {key}: {missing}")
        
        # Check specific constraints
        # 1. Years in ascending order
        if not df["year"].is_monotonic_increasing:
             raise ValueError(f"Years in {key} must be sorted in ascending order.")
             
        # 2. No NaN in numeric columns (simple check)
        numeric_cols = df.select_dtypes(include="number").columns
        if df[numeric_cols].isnull().any().any():
             raise ValueError(f"Found NaN values in numeric columns of {key}.")
             
        # 3. Check for duplicates in year
        if df["year"].duplicated().any():
             raise ValueError(f"Duplicate years found in {key}.")
