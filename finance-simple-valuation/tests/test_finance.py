import pytest
import pandas as pd
import numpy as np
from src.finance.metrics import calculate_historical_metrics
from config import SETTINGS

def test_calculate_fcf():
    """
    Test FCF calculation with simple known values.
    """
    # Create simple dummy dataframes
    is_data = pd.DataFrame([{
        "year": 2020,
        "revenue": 100,
        "cogs": 40,
        "opex": 20,
        "depreciation": 10,
        "interest_expense": 5,
        "taxes": 0 # simplified tax for testing if metrics uses tax from data or logic
    }])
    
    bs_data = pd.DataFrame([{
        "year": 2020,
        "cash": 10,
        "receivables": 10,  # NWC = 10+20-15 = 15
        "inventory": 20,
        "payables": 15,
        "debt_short": 0,
        "debt_long": 0,
        "equity": 0
    }])
    
    cf_data = pd.DataFrame([{
        "year": 2020,
        "cfo": 0,
        "capex": -30, # Capex is conventionally negative outflow, logic uses abs()
        "cfi_other": 0,
        "cff_other": 0
    }])
    
    data = {"income_statement": is_data, "balance_sheet": bs_data, "cash_flow": cf_data}
    
    # Run Function
    result = calculate_historical_metrics(data)
    row = result.iloc[0]
    
    # Assertions
    # EBIT = Rev (100) - COGS (40) - Opex (20) - Dep (10) = 30
    assert row["ebit"] == 30
    
    # NOPAT = EBIT * (1 - tax_rate in config)
    # Config tax_rate is 0.34
    expected_nopat = 30 * (1 - 0.34)
    assert np.isclose(row["nopat"], expected_nopat)
    
    # Delta NWC
    # NWC = 10 + 20 - 15 = 15. Previous year is 0 (first year has 0 delta in simplified logic)
    assert row["nwc"] == 15
    assert row["delta_nwc"] == 0
    
    # FCF = NOPAT + Dep - Capex - Delta_NWC
    # FCF = 19.8 + 10 - 30 - 0 = -0.2
    expected_fcf = expected_nopat + 10 - 30 - 0
    assert np.isclose(row["fcf"], expected_fcf)

def test_delta_nwc_change():
    """
    Test delta NWC across two years.
    """
    is_data = pd.DataFrame([
        {"year": 2020, "revenue": 100, "cogs": 0, "opex": 0, "depreciation": 0, "interest_expense": 0, "taxes": 0},
        {"year": 2021, "revenue": 100, "cogs": 0, "opex": 0, "depreciation": 0, "interest_expense": 0, "taxes": 0}
    ])
    
    bs_data = pd.DataFrame([
        {"year": 2020, "receivables": 10, "inventory": 10, "payables": 10, "cash":0, "debt_short":0, "debt_long":0, "equity":0}, # NWC = 10
        {"year": 2021, "receivables": 15, "inventory": 10, "payables": 10, "cash":0, "debt_short":0, "debt_long":0, "equity":0}  # NWC = 15
    ])
    
    cf_data = pd.DataFrame([
        {"year": 2020, "cfo": 0, "capex": 0, "cfi_other": 0, "cff_other": 0},
        {"year": 2021, "cfo": 0, "capex": 0, "cfi_other": 0, "cff_other": 0}
    ])

    data = {"income_statement": is_data, "balance_sheet": bs_data, "cash_flow": cf_data}
    
    result = calculate_historical_metrics(data)
    
    assert result.iloc[0]["delta_nwc"] == 0 # First year 0
    assert result.iloc[1]["delta_nwc"] == 5 # 15 - 10 = 5
