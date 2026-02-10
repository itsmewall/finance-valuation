import pandas as pd
import numpy as np
from config import SETTINGS, ScenarioParams

def project_financials(history_df: pd.DataFrame, scenario: ScenarioParams) -> pd.DataFrame:
    """
    Projects financials for future years based on the scenario parameters.
    Returns projection dataframe.
    """
    last_year = history_df.iloc[-1]
    last_date = last_year["year"]
    
    projections = []
    
    current_rev = last_year["revenue"]
    
    for i in range(1, SETTINGS.years_forecast + 1):
        year = last_date + i
        
        # Grow Revenue
        rev = current_rev * (1 + scenario.revenue_growth)
        delta_rev = rev - current_rev
        current_rev = rev
        
        # Calculate Expense Items
        # Use explicit EBIT margin from scenario config
        ebit = rev * scenario.ebit_margin
        
        # NOPAT
        nopat = ebit * (1 - SETTINGS.tax_rate)
        
        # Capex
        capex = rev * scenario.capex_pct_rev
        
        # Depreciation
        # As % of Capex (from scenario config)
        depreciation = capex * scenario.depreciation_pct_capex
        
        # NWC Change
        # Delta NWC = % of Delta Revenue
        delta_nwc = delta_rev * scenario.nwc_pct_rev_change
        
        # FCF
        # FCF = NOPAT + Dep - Capex - Delta_NWC
        # Capex here is treated as outflow (positive number subtracted)
        fcf = nopat + depreciation - capex - delta_nwc
        
        projections.append({
            "year": year,
            "revenue": rev,
            "ebit": ebit,
            "nopat": nopat,
            "depreciation": depreciation,
            "capex": capex,
            "delta_nwc": delta_nwc,
            "fcf": fcf
        })
        
    return pd.DataFrame(projections)
