import pandas as pd
from datetime import datetime
from pathlib import Path
from config import SETTINGS
from ..io.loaders import load_data
from ..io.validators import validate_data
from ..finance.metrics import calculate_historical_metrics
from ..finance.scenarios import run_scenarios
from ..finance.checks import check_projection_consistency
from ..finance.sensitivity import calculate_sensitivity_grid
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
        
    log_message("Starting Valuation Pipeline (Professional Mode)...", log_file)
    
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
    log_message("Calculating historical metrics...", log_file)
    historical_df = calculate_historical_metrics(data)
    
    # 4. Scenarios
    net_debt = SETTINGS.net_debt
    log_message(f"Running scenarios with Net Debt: {net_debt:,.2f} {SETTINGS.currency_unit}...", log_file)
    
    try:
        results = run_scenarios(historical_df, net_debt)
    except ValueError as e:
        log_message(f"[ERROR] Scenario calculation failed: {e}", log_file)
        return
    
    # 5. Consistency Checks & Warnings
    all_warnings = []
    log_message("Running economic consistency checks...", log_file)
    
    for name, res in results.items():
        # Check Terminal Share
        if res.terminal_share_warning:
            msg = f"[{name}] {res.terminal_share_warning}"
            all_warnings.append(msg)
            log_message(f"[WARN] {msg}", log_file)
            
        # Check Economic Consistency
        scenario_warnings = check_projection_consistency(historical_df, res.projections, name)
        for w in scenario_warnings:
            all_warnings.append(w)
            log_message(f"[WARN] {w}", log_file)

    # 6. Sensitivity Analysis (Base Case)
    sensitivity_data = {}
    base_res = results.get("base")
    
    if base_res:
        log_message("Calculating sensitivity grid (Base Case)...", log_file)
        sensitivity_data = calculate_sensitivity_grid(base_res.projections)
        
        # Log Driver Analysis
        log_message(f"[INSIGHT] {sensitivity_data['driver_analysis']}", log_file)
        
        # Generate Plot
        log_message("Generating sensitivity plot...", log_file)
        plot_sensitivity(sensitivity_data, output_dir)
    else:
        log_message("[WARNING] Base scenario not found, skipping sensitivity.", log_file)
    
    # 7. Export All
    log_message(f"Exporting comprehensive results to {output_dir}...", log_file)
    export_summary(results, sensitivity_data, all_warnings, output_dir)
    
    # 8. Summary Log
    log_message("VALUATION SUMMARY (Enterprise Value):", log_file)
    for name, res in results.items():
        log_message(f"- {name.capitalize()}: {res.enterprise_value:,.2f} ({SETTINGS.currency_unit})", log_file)
        
    log_message("Pipeline completed successfully.", log_file)
