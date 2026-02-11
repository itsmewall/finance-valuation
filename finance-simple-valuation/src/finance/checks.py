import pandas as pd
from typing import List
from config import SETTINGS

def check_projection_consistency(historical_df: pd.DataFrame, projections_df: pd.DataFrame, scenario_name: str) -> List[str]:
    """
    Checks for economic consistency between historical and projected data.
    Returns a list of warning messages.
    """
    warnings = []
    
    # Check 1: EBIT Margin Deviation
    hist_margin = (historical_df["ebit"] / historical_df["revenue"]).mean()
    proj_margin = (projections_df["ebit"] / projections_df["revenue"]).mean()
    
    margin_diff = abs(proj_margin - hist_margin)
    if margin_diff > 0.10: # >10% absolute deviation
        warnings.append(f"[{scenario_name}] Projected EBIT Margin ({proj_margin:.1%}) diverges significantly from historical avg ({hist_margin:.1%}). Ensure this structural change is justified.")
        
    # Check 2: Terminal Growth vs Projected Growth
    # If projection growth > terminal g for last year, it implies a fade is missing.
    terminal_g = SETTINGS.scenarios[scenario_name].terminal_g
    last_proj_growth = (projections_df["revenue"].pct_change().iloc[-1])
    
    if last_proj_growth > terminal_g:
        warnings.append(f"[{scenario_name}] Last year revenue growth ({last_proj_growth:.1%}) is higher than terminal growth ({terminal_g:.1%}). This implies potentially aggressive terminal value assumption.")
        
    # Check 3: CAPEX vs Depreciation
    # Depreciation should roughly match CAPEX in steady state.
    last_year = projections_df.iloc[-1]
    capex = last_year["capex"]
    dep = last_year["depreciation"]
    
    if capex > dep * 1.5:
        warnings.append(f"[{scenario_name}] Terminal year CAPEX ({capex:,.0f}) is significantly higher than Depreciation ({dep:,.0f}). This implies high persistent growth reinvestment in perpetuity.")
        
    return warnings
