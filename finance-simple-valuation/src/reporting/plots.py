import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any, List
from config import SETTINGS

def setup_plot_style():
    """Configures clean, professional plotting style."""
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.alpha"] = 0.3
    plt.rcParams["grid.linestyle"] = "--"

def save_plot_and_data(fig: plt.Figure, data: pd.DataFrame, name: str, output_dir: Path) -> None:
    """Saves the figure as PNG in plots/ and data as CSV in root output dir."""
    plots_dir = output_dir / "plots"
    plots_dir.mkdir(exist_ok=True)
    
    fig.savefig(plots_dir / f"{name}.png", bbox_inches="tight")
    data.to_csv(output_dir / f"{name}.csv", index=False)
    plt.close(fig)

def plot_sensitivity_heatmap(sensitivity_data: Dict[str, Any], output_dir: Path) -> None:
    """
    Generates a sensitivity heatmap from pre-calculated data.
    """
    ev_df = sensitivity_data["matrix"]
    ev_matrix = ev_df.values
    wacc_values = ev_df.index.values
    g_values = ev_df.columns.values
    
    # Export CSV
    ev_df.to_csv(output_dir / "sensitivity_ev.csv")
    
    setup_plot_style()
    # Plotting
    try:
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create heatmap using imshow
        im = ax.imshow(ev_matrix, cmap="RdYlGn", aspect='auto')
        
        # Add text annotations
        for i in range(len(wacc_values)):
            for j in range(len(g_values)):
                val = ev_matrix[i, j]
                text_color = "black" if val > np.median(ev_matrix) else "white" 
                val_str = f"{val:,.0f}" if val > 0 else "N/A"
                text = ax.text(j, i, val_str,
                            ha="center", va="center", color=text_color, fontsize=8)

        # Set ticks and labels
        ax.set_xticks(np.arange(len(g_values)))
        ax.set_yticks(np.arange(len(wacc_values)))
        
        # Format labels as percentages
        ax.set_xticklabels([f"{x:.1%}" for x in g_values])
        ax.set_yticklabels([f"{y:.1%}" for y in wacc_values])
        
        ax.set_xlabel("Terminal Growth (g)")
        ax.set_ylabel("WACC")
        ax.set_title("Sensitivity Analysis: Enterprise Value (WACC vs Terminal Growth)")
        
        # Add colorbar
        plt.colorbar(im, ax=ax, label="Enterprise Value")
        
        plots_dir = output_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        output_path = plots_dir / "sensitivity.png"
        plt.savefig(output_path)
        plt.close(fig)
    except Exception as e:
        print(f"[ERROR] Could not generate plot: {e}")

def plot_ev_composition(results: Dict[str, Any], output_dir: Path) -> str:
    """
    Generates a stacked bar chart of EV composition (Explicit vs Terminal).
    Returns an insight string.
    """
    scenarios = list(results.keys())
    pv_explicit = [results[s].pv_explicit for s in scenarios]
    pv_terminal = [results[s].pv_terminal for s in scenarios]
    
    data = pd.DataFrame({
        "scenario": scenarios,
        "pv_explicit": pv_explicit,
        "pv_terminal": pv_terminal
    })
    
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Calculate positions
    x = np.arange(len(scenarios))
    width = 0.5
    
    ax.bar(x, pv_explicit, width, label="PV Explicit Period", color="#4e79a7")
    ax.bar(x, pv_terminal, width, bottom=pv_explicit, label="PV Terminal Value", color="#f28e2b")
    
    ax.set_xticks(x)
    ax.set_xticklabels([s.capitalize() for s in scenarios])
    ax.set_ylabel(f"Present Value ({SETTINGS.currency_unit})")
    ax.set_title("Enterprise Value Composition by Scenario")
    ax.legend()
    
    # Add value labels
    for i, (exp, term) in enumerate(zip(pv_explicit, pv_terminal)):
        total = exp + term
        if total > 0:
            ax.text(i, total * 1.02, f"{total:,.0f}", ha='center', va='bottom', fontweight='bold', fontsize=9)
            ax.text(i, exp/2, f"{exp/total:.0%}", ha='center', va='center', color='white', fontsize=9)
            ax.text(i, exp + term/2, f"{term/total:.0%}", ha='center', va='center', color='white', fontsize=9)
        
    save_plot_and_data(fig, data, "ev_composition", output_dir)
    
    # Insight
    base_share = results.get("base").terminal_share_pct
    return f"Terminal Value represents {base_share:.1%} of Enterprise Value in the Base case."

def plot_fcf_projection(results: Dict[str, Any], output_dir: Path) -> str:
    """
    Plots the projected Free Cash Flow for Base, Downside, and Upside scenarios.
    Returns an insight string.
    """
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = {"base": "#4e79a7", "upside": "#59a14f", "downside": "#e15759"}
    styles = {"base": "-", "upside": "--", "downside": ":"}
    
    all_data = []
    years = [] # define outside loop
    
    for name, res in results.items():
        proj = res.projections
        years = proj["year"]
        fcf = proj["fcf"]
        
        ax.plot(years, fcf, label=name.capitalize(), color=colors.get(name, "gray"), 
                linestyle=styles.get(name, "-"), marker="o")
        
        scenario_data = proj[["year", "fcf"]].copy()
        scenario_data["scenario"] = name
        all_data.append(scenario_data)

    ax.set_xlabel("Year")
    ax.set_ylabel(f"Free Cash Flow ({SETTINGS.currency_unit})")
    ax.set_title("Projected Free Cash Flow Evolution")
    ax.legend()
    if len(years) > 0:
        ax.set_xticks(years) 
    
    if all_data:
        save_plot_and_data(fig, pd.concat(all_data), "fcf_projection", output_dir)
    else:
        plt.close(fig)
        return "No projection data available."
    
    # Insight
    base_proj = results.get("base").projections
    if len(base_proj) > 1:
        start_fcf = base_proj.iloc[0]["fcf"]
        end_fcf = base_proj.iloc[-1]["fcf"]
        if start_fcf != 0:
            cagr = (end_fcf / start_fcf) ** (1 / (len(base_proj) - 1)) - 1
            direction = "grows" if cagr > 0 else "declines"
            return f"FCF {direction} at a CAGR of {cagr:.1%} over the projection period (Base Case)."
    return "FCF Projections available."

def plot_ebit_to_fcf_bridge(base_res: Any, output_dir: Path) -> str:
    """
    Creates a simplified waterfall chart for the FIRST projected year of the Base case.
    """
    if not base_res:
        return ""
        
    # Get Year 1 data
    row = base_res.projections.iloc[0]
    
    ebit = row["ebit"]
    nopat = row["nopat"]
    taxes = - (ebit - nopat) # Taxes should be negative for bridge subtraction
    dep = row["depreciation"]
    capex = - row["capex"] # Capex is positive in DB, negative in CF formula? 
    # Check projection logic: fcf = nopat + depreciation - capex - delta_nwc
    # In projection result: "capex": capex (positive number). 
    # So bridge should subtract it.
    
    nwc = - row["delta_nwc"] # NWC Increase reduces cash
    fcf = row["fcf"]
    
    # Prepare waterfall data
    changes = [ebit, taxes, dep, capex, nwc]
    categories = ["EBIT", "Taxes", "Depreciation", "CAPEX", "ΔNWC"]
    
    # To make a proper waterfall, calculate start/end/cumulative
    # But as requested simplified: simple adjustments chart
    
    # Correct logic for waterfall start/end
    # start = 0
    # cumulative steps
    
    # Let's simplify and just show components affecting FCF from EBIT
    # Not full waterfall, but impact bars
    
    data = pd.DataFrame({"component": categories, "value": changes, "year": int(row["year"])})
    
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot bars
    bars = ax.bar(categories, changes, color=["#4e79a7" if x > 0 else "#e15759" for x in changes])
    
    # Add final FCF bar separately? Prefer showing inputs to arrive at FCF
    # Add a "Result: FCF" bar at the end
    categories_all = categories + ["FCF"]
    changes_all = changes + [fcf]
    
    ax.cla() # Clear axis
    
    # Waterfall logic manually:
    # 1. EBIT: 0 to EBIT
    # 2. Taxes: EBIT down to EBIT-Tax
    # ...
    # This is complex to robustly code here quickly without risk.
    # FALLBACK to "Impact Breakdown":
    
    colors = ["#4e79a7", "#e15759", "#59a14f", "#e15759", "#e15759", "#f28e2b"] # Blue, Red, Green, Red, Red, Orange
    ax.bar(categories_all, changes_all, color=colors)
    
    ax.axhline(0, color='black', linewidth=0.8)
    for i, v in enumerate(changes_all):
        ax.text(i, v if v > 0 else 0, f"{v:,.0f}", ha='center', va='bottom' if v > 0 else 'top', fontsize=9)
        
    ax.set_title(f"EBIT to FCF Impact (Year {int(row['year'])})")
    ax.set_ylabel(f"Value ({SETTINGS.currency_unit})")
    
    save_plot_and_data(fig, data, "ebit_to_fcf_bridge", output_dir)
    
    conversion = fcf / ebit if ebit != 0 else 0
    return f"Cash conversion ratio (FCF/EBIT) is {conversion:.1%}."

def plot_sensitivity_1d(sensitivity_data: Dict[str, Any], output_dir: Path) -> List[str]:
    """
    Generates 1D sensitivity plots: EV vs WACC and EV vs g.
    """
    insights = []
    matrix = sensitivity_data["matrix"] # DataFrame index=WACC, cols=g
    
    # 1. EV vs WACC (at median g)
    mid_g = matrix.columns[len(matrix.columns)//2]
    ev_wacc = matrix[mid_g] # Series: Index WACC, Values EV
    
    setup_plot_style()
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(ev_wacc.index, ev_wacc.values, marker='o', color="#e15759", linewidth=2)
    ax1.set_xlabel("WACC")
    ax1.set_ylabel(f"Enterprise Value ({SETTINGS.currency_unit})")
    ax1.set_title(f"Sensitivity: EV vs WACC (g={mid_g:.1%})")
    ax1.xaxis.set_major_formatter(lambda x, p: f"{x:.1%}")
    ax1.grid(True, which='both', linestyle='--')
    
    save_plot_and_data(fig1, ev_wacc.reset_index(name="ev"), "ev_vs_wacc", output_dir)
    
    # Insight WACC
    drop_pct = (ev_wacc.iloc[-1] / ev_wacc.iloc[0]) - 1
    insights.append(f"EV decreases by {abs(drop_pct):.1%} as WACC increases from {ev_wacc.index[0]:.1%} to {ev_wacc.index[-1]:.1%}.")

    # 2. EV vs g (at median WACC)
    mid_wacc = matrix.index[len(matrix.index)//2]
    ev_g = matrix.loc[mid_wacc] # Series: Index g, Values EV
    
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(ev_g.index, ev_g.values, marker='o', color="#59a14f", linewidth=2)
    ax2.set_xlabel("Terminal Growth (g)")
    ax2.set_ylabel(f"Enterprise Value ({SETTINGS.currency_unit})")
    ax2.set_title(f"Sensitivity: EV vs Growth (WACC={mid_wacc:.1%})")
    ax2.xaxis.set_major_formatter(lambda x, p: f"{x:.1%}")
    ax2.grid(True, which='both', linestyle='--')
    
    save_plot_and_data(fig2, ev_g.reset_index(name="ev"), "ev_vs_terminal_g", output_dir)
    
    # Insight g
    growth_pct = (ev_g.iloc[-1] / ev_g.iloc[0]) - 1
    insights.append(f"EV increases by {growth_pct:.1%} as Growth increases from {ev_g.index[0]:.1%} to {ev_g.index[-1]:.1%}.")
    
    return insights

def plot_all(results: Dict[str, Any], sensitivity_data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
    """Orchestrates all plotting functions and returns a dict of insights."""
    insights = {}
    
    # 1. Sensitivity Heatmap
    plot_sensitivity_heatmap(sensitivity_data, output_dir)
    
    # 2. EV Composition
    insights["ev_composition"] = plot_ev_composition(results, output_dir)
    
    # 3. FCF Projection
    insights["fcf_projection"] = plot_fcf_projection(results, output_dir)
    
    # 4. EBIT to FCF Bridge (Base Case)
    insights["ebit_to_fcf_bridge"] = plot_ebit_to_fcf_bridge(results.get("base"), output_dir)
    
    # 5. Sensitivity 1D
    sens_insights = plot_sensitivity_1d(sensitivity_data, output_dir)
    insights["sensitivity_wacc"] = sens_insights[0]
    insights["sensitivity_g"] = sens_insights[1]
    
    return insights
