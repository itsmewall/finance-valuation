from dataclasses import dataclass
from typing import Dict

@dataclass
class ScenarioParams:
    revenue_growth: float
    wacc: float
    terminal_g: float
    capex_pct_rev: float
    nwc_pct_rev_change: float

@dataclass
class Config:
    company_name: str
    years_forecast: int
    tax_rate: float
    scenarios: Dict[str, ScenarioParams]
    depreciation_pct_capex: float  # Or pct_revenue, using pct_capex as simple default

# GLOBAL CONFIGURATION
SETTINGS = Config(
    company_name="Ambev",
    years_forecast=5,
    tax_rate=0.34,  # Effective tax rate assumption
    depreciation_pct_capex=0.80, # Assuming depreciation trails capex
    scenarios={
        "base": ScenarioParams(
            revenue_growth=0.05,        # 5% annual growth
            wacc=0.11,                  # 11% cost of capital
            terminal_g=0.03,            # 3% terminal growth
            capex_pct_rev=0.15,         # 15% of revenue
            nwc_pct_rev_change=0.10     # 10% of revenue change goes to NWC
        ),
        "downside": ScenarioParams(
            revenue_growth=0.02,
            wacc=0.13,
            terminal_g=0.01,
            capex_pct_rev=0.12,
            nwc_pct_rev_change=0.15     # Less efficient
        ),
        "upside": ScenarioParams(
            revenue_growth=0.08,
            wacc=0.09,
            terminal_g=0.04,
            capex_pct_rev=0.18,         # More investment
            nwc_pct_rev_change=0.08     # More efficient
        ),
    }
)
