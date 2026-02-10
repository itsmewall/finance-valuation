import streamlit as st
import pandas as pd
import json
from pathlib import Path
import os

# Set page title and layout
st.set_page_config(page_title="Valuation Dashboard", layout="wide")

# Paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
SUMMARY_FILE = OUTPUT_DIR / "summary.json"
PROJECTIONS_FILE = OUTPUT_DIR / "projections.csv"
SENSITIVITY_IMG = OUTPUT_DIR / "sensitivity.png"

def main():
    st.title("Finance Valuation Dashboard")
    st.markdown("---")

    # Check if outputs exist
    if not SUMMARY_FILE.exists() or not PROJECTIONS_FILE.exists():
        st.warning("⚠️ Outputs not found!")
        st.info("Plese run `python run.py` first to generate valuation results.")
        return

    # Load Data
    with open(SUMMARY_FILE, "r") as f:
        summary_data = json.load(f)
    
    projections_df = pd.read_csv(PROJECTIONS_FILE)

    # --- Section 1: Valuation Summary (Cards) ---
    st.subheader("Valuation Summary (Enterprise Value)")
    
    # Create columns for scenarios
    cols = st.columns(len(summary_data))
    
    for idx, (scenario, data) in enumerate(summary_data.items()):
        ev = data.get("enterprise_value", 0)
        wacc = data.get("wacc", 0)
        g = data.get("terminal_g", 0)
        
        with cols[idx]:
            st.metric(
                label=f"{scenario.capitalize()} Scenario",
                value=f"${ev:,.0f}",
                delta=None
            )
            st.caption(f"WACC: {wacc:.1%} | g: {g:.1%}")

    st.markdown("---")

    # --- Section 2: Projections ---
    st.subheader("Financial Projections (Base Case)")
    
    # Filter for base case (assuming 'base' exists, otherwise take first)
    base_proj = projections_df[projections_df["scenario"] == "base"]
    if base_proj.empty and not projections_df.empty:
        base_proj = projections_df[projections_df["scenario"] == projections_df["scenario"].iloc[0]]
        st.caption("Showing first available scenario.")
    
    # Display table
    st.dataframe(base_proj.style.format("{:,.0f}"), use_container_width=True)

    st.markdown("---")

    # --- Section 3: Sensitivity Analysis ---
    st.subheader("Sensitivity Analysis (WACC vs Growth)")
    
    if SENSITIVITY_IMG.exists():
        st.image(str(SENSITIVITY_IMG), caption="Enterprise Value Heatmap", use_column_width=False)
    else:
        st.warning("Sensitivity plot not found.")

if __name__ == "__main__":
    main()
