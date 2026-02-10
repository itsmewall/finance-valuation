from typing import Dict
import pandas as pd
from config import SETTINGS
from .projections import project_financials
from .dcf import calculate_dcf, ValuationResult

def run_scenarios(historical_df: pd.DataFrame, net_debt: float) -> Dict[str, ValuationResult]:
    """
    Runs metrics, projections, and DCF for all scenarios defined in config.
    """
    results = {}
    
    for scenario_name, params in SETTINGS.scenarios.items():
        # Project future
        proj_df = project_financials(historical_df, params)
        
        # Calculate DCF
        val_result = calculate_dcf(proj_df, params, net_debt, scenario_name)
        
        results[scenario_name] = val_result
        
    return results
