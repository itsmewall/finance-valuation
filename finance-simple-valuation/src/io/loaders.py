import pandas as pd
from pathlib import Path
from typing import Dict

def load_data(data_dir: Path) -> Dict[str, pd.DataFrame]:
    """
    Loads financial data from CSV files in the data directory.
    Returns a dictionary of DataFrames.
    """
    files = {
        "income_statement": "ambev_income_statement.csv",
        "balance_sheet": "ambev_balance_sheet.csv",
        "cash_flow": "ambev_cash_flow.csv"
    }
    
    data = {}
    for key, filename in files.items():
        file_path = data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        df = pd.read_csv(file_path)
        # Ensure year is int
        if 'year' in df.columns:
            df['year'] = df['year'].astype(int)
        
        data[key] = df
        
    return data
