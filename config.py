from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ScenarioParams:
    revenue_growth: float
    ebit_margin: float  # Explicit margin assumption
    wacc: float
    terminal_g: float
    capex_pct_rev: float
    depreciation_pct_capex: float
    nwc_pct_rev_change: float

@dataclass
class SensitivityConfig:
    wacc_values: List[float]
    terminal_g_values: List[float]

@dataclass
class Config:
    company_name: str
    currency_unit: str
    years_forecast: int
    tax_rate: float
    net_debt: float  # Pre-defined net debt if data not available, or override
    scenarios: Dict[str, ScenarioParams]
    sensitivity: SensitivityConfig

# GLOBAL CONFIGURATION
SETTINGS = Config(
    company_name="Ambev (Dummy)",
    currency_unit="BRL_MILLIONS",
    years_forecast=5,
    tax_rate=0.34,
    net_debt=6580.0, # Example fixed value, usually calculated from balance sheet if available
    
    scenarios={
        "base": ScenarioParams(
            revenue_growth=0.05,        # 5% annual growth
            ebit_margin=0.28,           # 28% EBIT margin
            wacc=0.11,                  # 11% cost of capital
            terminal_g=0.03,            # 3% terminal growth
            capex_pct_rev=0.15,         
            depreciation_pct_capex=0.80, 
            nwc_pct_rev_change=0.10     
        ),
        "downside": ScenarioParams(
            revenue_growth=0.02,
            ebit_margin=0.24,
            wacc=0.13,
            terminal_g=0.01,
            capex_pct_rev=0.12,
            depreciation_pct_capex=0.85,
            nwc_pct_rev_change=0.15     
        ),
        "upside": ScenarioParams(
            revenue_growth=0.08,
            ebit_margin=0.32,
            wacc=0.09,
            terminal_g=0.04,
            capex_pct_rev=0.18,         
            depreciation_pct_capex=0.75,
            nwc_pct_rev_change=0.08     
        ),
    },
    sensitivity=SensitivityConfig(
        wacc_values=[0.09, 0.10, 0.11, 0.12, 0.13, 0.14],
        terminal_g_values=[0.01, 0.015, 0.02, 0.025, 0.03, 0.035]
    )
)
