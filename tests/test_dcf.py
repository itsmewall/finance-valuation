import pytest
import pandas as pd
import numpy as np
from src.finance.dcf import calculate_dcf, ValuationResult
from config import ScenarioParams

def test_dcf_calculation():
    """
    Test simple DCF calculation sanity.
    """
    # Create simple projection dataframe
    # 2 years projection
    projections = pd.DataFrame([
        {"year": 2024, "fcf": 100},
        {"year": 2025, "fcf": 110}
    ])
    
    # Create scenario params
    scenario = ScenarioParams(
        revenue_growth=0.05,
        ebit_margin=0.20,
        wacc=0.10,
        terminal_g=0.02,
        capex_pct_rev=0.1,
        depreciation_pct_capex=0.8,
        nwc_pct_rev_change=0.1
    )
    
    net_debt = 50
    scenario_name = "test_case"
    
    result = calculate_dcf(projections, scenario, net_debt, scenario_name)
    
    # Manual Calculation Check
    # Year 1 Discount: (1.10)^-1 = 0.90909
    # Year 2 Discount: (1.10)^-2 = 0.82645
    
    pv_1 = 100 * (1.10)**-1
    pv_2 = 110 * (1.10)**-2
    # PV Explicit sum
    expected_pv_explicit = pv_1 + pv_2
    
    assert np.isclose(result.pv_explicit, expected_pv_explicit)
    
    # Terminal Value
    # TV = FCF_n * (1+g) / (wacc - g)
    # TV = 110 * (1.02) / (0.10 - 0.02)
    # TV = 112.2 / 0.08 = 1402.5
    expected_tv = 110 * 1.02 / 0.08
    assert np.isclose(result.terminal_value, expected_tv)
    
    # PV Terminal
    # PV_TV = TV * Discount_Factor_Year_2
    expected_pv_tv = expected_tv * (1.10)**-2
    assert np.isclose(result.pv_terminal, expected_pv_tv)
    
    # Enterprise Value
    expected_ev = expected_pv_explicit + expected_pv_tv
    assert np.isclose(result.enterprise_value, expected_ev)
    
    # Equity Value
    expected_equity = expected_ev - net_debt
    assert np.isclose(result.equity_value, expected_equity)

def test_dcf_invalid_g():
    """
    Test that DCF raises validation error if g >= wacc.
    """
    projections = pd.DataFrame([{"year": 2024, "fcf": 100}])
    scenario = ScenarioParams(
        revenue_growth=0.05,
        ebit_margin=0.20,
        wacc=0.05,
        terminal_g=0.05, # Equal to WACC
        capex_pct_rev=0.1,
        depreciation_pct_capex=0.8,
        nwc_pct_rev_change=0.1
    )
    
    with pytest.raises(ValueError, match="must be less than WACC"):
        calculate_dcf(projections, scenario, 0, "test")
