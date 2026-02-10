import pandas as pd
from pathlib import Path
from config import SETTINGS
from ..io.loaders import load_data
from ..io.validators import validate_data
from ..finance.metrics import calculate_historical_metrics
from ..finance.scenarios import run_scenarios
from ..reporting.export import export_summary
from ..reporting.plots import plot_sensitivity

def run_all(base_dir: Path) -> None:
    """
    Orchestrates the entire valuation pipeline.
    """
    data_dir = base_dir / "data"
    output_dir = base_dir / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    print("\n[INFO] Starting Valuation Pipeline...")
    
    # 1. Load Data
    print(f"[INFO] Loading data from {data_dir}...")
    try:
        data = load_data(data_dir)
    except FileNotFoundError as e:
        print(f"[ERROR] Could not load data: {e}")
        return
        
    # 2. Validate Data
    print("[INFO] Validating data structure...")
    try:
        validate_data(data)
    except ValueError as e:
        print(f"[ERROR] Data validation failed: {e}")
        return
        
    # 3. Calculate Historical Metrics
    print("[INFO] Calculating historical metrics (FCF, NWC, etc.)...")
    historical_df = calculate_historical_metrics(data)
    
    # 4. Run Scenarios (Base, Downside, Upside)
    # Net debt needed. Net Debt = Debt - Cash
    # We take the latest year balance sheet data
    bs_latest = data["balance_sheet"].iloc[-1]
    net_debt = (bs_latest["debt_short"] + bs_latest["debt_long"]) - bs_latest["cash"]
    
    print(f"[INFO] Running scenarios (Base, Downside, Upside) with Net Debt: {net_debt:,.2f}...")
    results = run_scenarios(historical_df, net_debt)
    
    # 5. Export Outputs
    print(f"[INFO] Exporting results to {output_dir}...")
    export_summary(results, output_dir)
    
    # 6. Generate Sensitivity Plot (Base Case)
    base_res = results.get("base")
    if base_res:
        print("[INFO] Generating sensitivity plot for Base Case...")
        # Recalc projections specifically for heatmap base?
        # The plot function does its own discount logic based on valid inputs
        # But wait, logic in plot_sensitivity is simplified and re-calculates PVs
        # It needs `base_projections`, `base_wacc`, `base_g`
        # We pass the base case projections df.
        plot_sensitivity(base_res.projections, base_res.wacc, base_res.terminal_g, output_dir)
    
    # 7. Summary Print
    print("\n" + "="*40)
    print("VALUATION RESULTS (Enterprise Value)")
    print("="*40)
    for name, res in results.items():
        print(f"- {name.capitalize()}: {res.enterprise_value:,.2f}")
    print("="*40)
    print(f"Outputs generated in: {output_dir}")
    print("To view standard report, run: streamlit run app.py")
    print("="*40 + "\n")
