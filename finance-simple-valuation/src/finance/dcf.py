from dataclasses import dataclass
import pandas as pd
from typing import Dict
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
    terminal_share_pct: float

def calculate_dcf(projections: pd.DataFrame, scenario: ScenarioParams, net_debt: float, scenario_name: str) -> ValuationResult:
    """
    Calculates Enterprise Value using DCF method.
    """
    wacc = scenario.wacc
    g = scenario.terminal_g
    
    # Validation: g must be less than wacc
    if g >= wacc:
        raise ValueError(f"Terminal growth (g={g:.1%}) must be less than WACC (wacc={wacc:.1%}) for standard Gordon Growth Model to work.")
        
    # Calculate Discount Factors
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
    
    # Terminal Share Pct
    terminal_share_pct = pv_terminal / enterprise_value if enterprise_value != 0 else 0
    
    return ValuationResult(
        scenario_name=scenario_name,
        enterprise_value=enterprise_value,
        equity_value=equity_value,
        terminal_value=terminal_value,
        pv_explicit=pv_explicit,
        pv_terminal=pv_terminal,
        projections=projections,
        wacc=wacc,
        terminal_g=g,
        terminal_share_pct=terminal_share_pct
    )
