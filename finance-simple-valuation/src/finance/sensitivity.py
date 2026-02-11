import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from config import SETTINGS

def calculate_sensitivity_grid(base_projections: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates the sensitivity matrix for WACC vs Terminal Growth (g).
    Returns a dictionary with:
    - matrix: The EV matrix (DataFrame)
    - ev_min: Minimum EV in the grid
    - ev_max: Maximum EV in the grid
    - ev_base: Base case EV (center of grid approx)
    - driver_analysis: String explaining which variable drives value more.
    """
    wacc_values = np.array(SETTINGS.sensitivity.wacc_values)
    g_values = np.array(SETTINGS.sensitivity.terminal_g_values)
    
    # Initialize EV matrix
    ev_matrix = np.zeros((len(wacc_values), len(g_values)))
    
    # Pre-calculate discount periods
    periods = np.arange(1, len(base_projections) + 1)
    fcf = base_projections["fcf"].values
    last_fcf = fcf[-1]
    
    # Calculate EV for each cell
    for i, w in enumerate(wacc_values):
        discount_factors = (1 + w) ** -periods
        pv_explicit = np.sum(fcf * discount_factors)
        last_factor = discount_factors[-1]
        
        for j, g in enumerate(g_values):
            if w <= g:
                ev = 0.0 # Invalid
            else:
                tv = last_fcf * (1 + g) / (w - g)
                pv_terminal = tv * last_factor
                ev = pv_explicit + pv_terminal
            
            ev_matrix[i, j] = ev
            
    # Create DataFrame
    ev_df = pd.DataFrame(ev_matrix, index=wacc_values, columns=g_values)
    ev_df.index.name = "WACC"
    ev_df.columns.name = "Terminal Growth"
    
    # Analyze Driver
    # Calculate range of variation for WACC (holding g constant at median)
    mid_g_idx = len(g_values) // 2
    wacc_range_ev = ev_matrix[:, mid_g_idx]
    wacc_impact = wacc_range_ev.max() - wacc_range_ev.min()
    
    # Calculate range of variation for g (holding WACC constant at median)
    mid_wacc_idx = len(wacc_values) // 2
    g_range_ev = ev_matrix[mid_wacc_idx, :]
    g_impact = g_range_ev.max() - g_range_ev.min()
    
    sensitivity_ratio = wacc_impact / g_impact if g_impact > 0 else float('inf')
    
    if sensitivity_ratio > 1.2:
        driver = "Sensitivity driven primarily by WACC changes."
    elif sensitivity_ratio < 0.8:
        driver = "Sensitivity driven primarily by Terminal Growth changes."
    else:
        driver = "Valuation is sensitive to both WACC and Growth similarly."
        
    return {
        "matrix": ev_df,
        "ev_min": ev_matrix[ev_matrix > 0].min(),
        "ev_max": ev_matrix.max(),
        "ev_base": ev_matrix[mid_wacc_idx, mid_g_idx], # Approx base
        "driver_analysis": driver,
        "wacc_impact_range": wacc_impact,
        "g_impact_range": g_impact
    }
