import pandas as pd
from datetime import datetime
from pathlib import Path
from config import SETTINGS
from ..io.loaders import load_data
from ..io.validators import validate_data
from ..finance.metrics import calculate_historical_metrics
from ..finance.scenarios import run_scenarios
from ..reporting.export import export_summary
from ..reporting.plots import plot_sensitivity

def log_message(message: str, log_file: Path) -> None:
    """
    Logs message to console and appends to log file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    print(formatted_msg)
    with open(log_file, "a") as f:
        f.write(formatted_msg + "\n")

def run_all(base_dir: Path) -> None:
    """
    Orchestrates the entire valuation pipeline in batch mode.
    """
    data_dir = base_dir / "data"
    output_dir = base_dir / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    log_file = output_dir / "run_log.txt"
    # Clear log file on start
    with open(log_file, "w") as f:
        f.write(f"Run Log initialized at {datetime.now()}\n")
        
    log_message("Starting Valuation Pipeline (Batch Mode)...", log_file)
    
    # 1. Load Data
    log_message(f"Loading data from {data_dir}...", log_file)
    try:
        data = load_data(data_dir)
    except FileNotFoundError as e:
        log_message(f"[ERROR] Could not load data: {e}", log_file)
        return
        
    # 2. Validate Data
    log_message("Validating data structure...", log_file)
    try:
        validate_data(data)
    except ValueError as e:
        log_message(f"[ERROR] Data validation failed: {e}", log_file)
        return
        
    # 3. Calculate Historical Metrics
    log_message("Calculating historical metrics (FCF, NWC, etc.)...", log_file)
    historical_df = calculate_historical_metrics(data)
    
    # 4. Determine Net Debt & Run Scenarios
    # Use config net_debt or override from balance sheet if desired.
    # We will use the config value as requested in the new prompt "net_debt (pré-definido)"
    net_debt = SETTINGS.net_debt
    
    log_message(f"Running scenarios (Base, Downside, Upside) with Net Debt: {net_debt:,.2f} {SETTINGS.currency_unit}...", log_file)
    try:
        results = run_scenarios(historical_df, net_debt)
    except ValueError as e:
        log_message(f"[ERROR] Scenario calculation failed: {e}", log_file)
        return
    
    # 5. Export Standard Outputs (JSON + CSV)
    log_message(f"Exporting results to {output_dir}...", log_file)
    export_summary(results, output_dir)
    
    # 6. Run Sensitivity Analysis (Heatmap + Matrix CSV)
    base_res = results.get("base")
    if base_res:
        log_message("Generating sensitivity analysis (Plot + CSV)...", log_file)
        # Pass base projections for sensitivity base
        plot_sensitivity(base_res.projections, output_dir)
    else:
        log_message("[WARNING] Base scenario not found, skipping sensitivity.", log_file)
    
    # 7. Summary Log
    log_message("VALUATION RESULTS (Enterprise Value):", log_file)
    for name, res in results.items():
        log_message(f"- {name.capitalize()}: {res.enterprise_value:,.2f}", log_file)
        
    log_message("Pipeline completed successfully.", log_file)
