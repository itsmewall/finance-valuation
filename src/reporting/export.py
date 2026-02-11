import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from ..finance.dcf import ValuationResult
from config import SETTINGS

def export_summary(results: Dict[str, ValuationResult], sensitivity_data: Dict[str, Any], warnings: List[str], chart_insights: Dict[str, str], output_dir: Path) -> None:
    """
    Exports summary.json and projections.csv to the output directory.
    Now includes sensitivity metrics, consistency warnings, and chart insights.
    """
    summary_data = {}
    projections_list = []
    
    # Process Scenarios
    for scenario_name, res in results.items():
        # Get params from settings
        params = SETTINGS.scenarios.get(scenario_name)
        
        summary_data[scenario_name] = {
            "enterprise_value": res.enterprise_value,
            "equity_value": res.equity_value,
            "terminal_value": res.terminal_value,
            "pv_explicit": res.pv_explicit,
            "pv_terminal": res.pv_terminal,
            "wacc": res.wacc,
            "terminal_g": res.terminal_g,
            "terminal_share_pct": res.terminal_share_pct,
            "terminal_share_warning": res.terminal_share_warning,
            "assumptions": {
                "operational": {
                    "revenue_growth": params.revenue_growth,
                    "ebit_margin": params.ebit_margin,
                    "capex_pct_rev": params.capex_pct_rev,
                    "nwc_pct_rev_change": params.nwc_pct_rev_change,
                    "forecast_years": SETTINGS.years_forecast
                },
                "financial": {
                    "wacc": params.wacc,
                    "terminal_g": params.terminal_g,
                    "tax_rate": SETTINGS.tax_rate,
                    "net_debt_used": SETTINGS.net_debt
                }
            } if params else {}
        }
        
        # Projections
        proj = res.projections.copy()
        proj["scenario"] = scenario_name
        projections_list.append(proj)

    # Sensitivity Analysis Section
    summary_data["sensitivity_analysis"] = {
        "ev_base": sensitivity_data.get("ev_base"),
        "ev_min": sensitivity_data.get("ev_min"),
        "ev_max": sensitivity_data.get("ev_max"),
        "driver_analysis": sensitivity_data.get("driver_analysis")
    }

    # Chart Insights
    summary_data["chart_insights"] = chart_insights

    # Consistency Checks
    summary_data["consistency_warnings"] = warnings
        
    # Save summary.json
    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary_data, f, indent=4)
        
    # Save projections.csv
    if projections_list:
        all_projections = pd.concat(projections_list, ignore_index=True)
        # Select required columns first + scenario
        required_cols = ["year", "revenue", "ebit", "nopat", "delta_nwc", "capex", "depreciation", "fcf", "scenario"]
        all_projections = all_projections[required_cols]
        all_projections.to_csv(output_dir / "projections.csv", index=False)
