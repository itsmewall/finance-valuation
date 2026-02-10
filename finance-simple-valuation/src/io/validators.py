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
            
    # Also check if years are aligned? For simplicity, we just check data loaded.
    # A more robust check would ensure years match across files, but we keep it simple as requested.
