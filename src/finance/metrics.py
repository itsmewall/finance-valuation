import pandas as pd
import numpy as np
from typing import Dict
from config import SETTINGS

def calculate_historical_metrics(data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Merges dataframes and calculates historical FCF and other metrics.
    """
    # Merge on year
    is_df = data_dict["income_statement"]
    bs_df = data_dict["balance_sheet"]
    cf_df = data_dict["cash_flow"]
    
    merged = is_df.merge(bs_df, on="year", how="inner").merge(cf_df, on="year", how="inner")
    
    # Calculate NWC
    merged["nwc"] = merged["receivables"] + merged["inventory"] - merged["payables"]
    merged["delta_nwc"] = merged["nwc"].diff().fillna(0) # First year delta is 0 or needs prior context. We assume 0 for simplicity.

    # Calculate EBIT
    # Assuming opex includes depreciation? The CSV has depreciation separately.
    # Usually EBIT = Revenue - COGS - Opex (excluding interest/tax).
    # If Dep matches the input file structure, we subtract it if not already in Opex.
    # Let's assume Opex does NOT include Dep based on the CSV structure.
    merged["ebit"] = merged["revenue"] - merged["cogs"] - merged["opex"] - merged["depreciation"]
    
    # Calculate NOPAT
    # Tax rate from config or actuals?
    # Let's use config tax rate to normalize, or implied tax rate?
    # Prompt says: "Onde NOPAT = EBIT * (1 - tax_rate)"
    # We will use the config tax rate for consistency in valuation.
    merged["nopat"] = merged["ebit"] * (1 - SETTINGS.tax_rate)
    
    # Calculate FCF
    # FCF = NOPAT + Depreciation - Capex - Delta_NWC
    # Note: Capex is usually negative in CF statement. Formula says "- Capex". 
    # If capex is negative in CSV (e.g. -4000), then we should ADD it if formula is "minus positive capex"
    # But standard FCF formula: Cash Flow available.
    # If Capex is negative number in CSV, then FCF = NOPAT + Dep + Capex - Delta_NWC
    # Let's standardise: Capex should be subtracted as an outflow.
    # If CSV has -4000, we add it (which subtracts the value).
    # To be safe: FCF = NOPAT + Dep - abs(Capex) - Delta_NWC
    
    merged["capex_abs"] = merged["capex"].abs()
    merged["fcf"] = merged["nopat"] + merged["depreciation"] - merged["capex_abs"] - merged["delta_nwc"]
    
    return merged.sort_values("year")
