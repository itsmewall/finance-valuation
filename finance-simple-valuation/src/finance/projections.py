import pandas as pd
import numpy as np
from typing import Dict, Any, List
from config import SETTINGS, ScenarioParams
from .metrics import calculate_historical_metrics

def project_financials(history_df: pd.DataFrame, scenario: ScenarioParams) -> pd.DataFrame:
    """
    Projects financials for future years based on the scenario parameters.
    Returns projection dataframe.
    """
    last_year = history_df.iloc[-1]
    last_date = last_year["year"]
    
    projections = []
    
    # Starting values for iterative projection
    current_rev = last_year["revenue"]
    
    # Calculate margin from last year to maintain or use a stable assumption?
    # Prompt says: "Margens constantes por padrão (ou leve convergência)"
    # We'll use last year's margins as base.
    ebit_margin = last_year["ebit"] / last_year["revenue"]
    
    for i in range(1, SETTINGS.years_forecast + 1):
        year = last_date + i
        
        # Grow Revenue
        rev = current_rev * (1 + scenario.revenue_growth)
        delta_rev = rev - current_rev
        current_rev = rev
        
        # Calculate Expense Items
        # COGS/Opex scale with revenue effectively via EBIT Margin
        ebit = rev * ebit_margin
        
        # NOPAT
        nopat = ebit * (1 - SETTINGS.tax_rate)
        
        # Capex
        capex = rev * scenario.capex_pct_rev
        
        # Depreciation
        # As % of Capex (from config)
        depreciation = capex * SETTINGS.depreciation_pct_capex
        
        # NWC Change
        # Delta NWC = % of Delta Revenue
        delta_nwc = delta_rev * scenario.nwc_pct_rev_change
        
        # FCF
        fcf = nopat + depreciation - capex - delta_nwc
        
        projections.append({
            "year": year,
            "revenue": rev,
            "ebit": ebit,
            "nopat": nopat,
            "depreciation": depreciation,
            "capex": -capex, # Standard accounting sign convention often negative
            "delta_nwc": delta_nwc,
            "fcf": fcf
        })
        
    return pd.DataFrame(projections)
