import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any
from ..finance.dcf import ValuationResult

def export_summary(results: Dict[str, ValuationResult], output_dir: Path) -> None:
    """
    Exports summary.json and projections.csv to the output directory.
    """
    summary_data = {}
    projections_list = []
    
    for scenario_name, res in results.items():
        summary_data[scenario_name] = {
            "enterprise_value": res.enterprise_value,
            "equity_value": res.equity_value,
            "terminal_value": res.terminal_value,
            "pv_explicit": res.pv_explicit,
            "pv_terminal": res.pv_terminal,
            "wacc": res.wacc,
            "terminal_g": res.terminal_g
        }
        
        # Projections
        proj = res.projections.copy()
        proj["scenario"] = scenario_name
        projections_list.append(proj)
        
    # Save summary.json
    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary_data, f, indent=4)
        
    # Save projections.csv
    if projections_list:
        all_projections = pd.concat(projections_list, ignore_index=True)
        all_projections.to_csv(output_dir / "projections.csv", index=False)
