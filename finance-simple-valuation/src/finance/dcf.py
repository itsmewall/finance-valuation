from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd
from config import SETTINGS, ScenarioParams

@dataclass
class ValuationResult:
    scenario_name: str
    enterprise_value: float
    equity_value: float
    terminal_value: float
    pv_explicit: float
    pv_terminal: float
    projections: pd.DataFrame
    wacc: float
    terminal_g: float

def calculate_dcf(projections: pd.DataFrame, scenario: ScenarioParams, net_debt: float, scenario_name: str) -> ValuationResult:
    """
    Calculates Enterprise Value using DCF method.
    """
    wacc = scenario.wacc
    g = scenario.terminal_g
    
    # Calculate Discount Factors
    # Assuming mid-year convention? Or simple end-period? Let's do end-period for simplicity.
    projections = projections.copy()
    projections["period"] = range(1, len(projections) + 1)
    projections["discount_factor"] = (1 + wacc) ** -projections["period"]
    projections["pv_fcf"] = projections["fcf"] * projections["discount_factor"]
    
    pv_explicit = projections["pv_fcf"].sum()
    
    # Terminal Value
    last_fcf = projections.iloc[-1]["fcf"]
    terminal_value = last_fcf * (1 + g) / (wacc - g)
    
    # Discount TV to present
    pv_terminal = terminal_value * projections.iloc[-1]["discount_factor"]
    
    enterprise_value = pv_explicit + pv_terminal
    equity_value = enterprise_value - net_debt
    
    return ValuationResult(
        scenario_name=scenario_name,
        enterprise_value=enterprise_value,
        equity_value=equity_value,
        terminal_value=terminal_value,
        pv_explicit=pv_explicit,
        pv_terminal=pv_terminal,
        projections=projections,
        wacc=wacc,
        terminal_g=g
    )
