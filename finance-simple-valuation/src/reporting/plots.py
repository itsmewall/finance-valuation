import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from config import SETTINGS

def plot_sensitivity(base_projections: pd.DataFrame, output_dir: Path) -> None:
    """
    Generates a sensitivity heatmap for Enterprise Value based on range of WACC and Terminal Growth.
    Also exports the data to sensitivity_ev.csv.
    """
    # Use config values instead of internal hardcoding
    wacc_values = np.array(SETTINGS.sensitivity.wacc_values)
    g_values = np.array(SETTINGS.sensitivity.terminal_g_values)
    
    # Initialize EV matrix
    ev_matrix = np.zeros((len(wacc_values), len(g_values)))
    
    # Pre-calculate discount periods
    periods = np.arange(1, len(base_projections) + 1)
    fcf = base_projections["fcf"].values
    last_fcf = fcf[-1]
    
    # Calculate EV for each cell
    for i, w in enumerate(wacc_values):
        discount_factors = (1 + w) ** -periods
        pv_explicit = np.sum(fcf * discount_factors)
        last_factor = discount_factors[-1]
        
        for j, g in enumerate(g_values):
            if w <= g:
                ev = 0 # Invalid
            else:
                tv = last_fcf * (1 + g) / (w - g)
                pv_terminal = tv * last_factor
                ev = pv_explicit + pv_terminal
            
            ev_matrix[i, j] = ev
            
    # Export CSV
    ev_df = pd.DataFrame(ev_matrix, index=wacc_values, columns=g_values)
    ev_df.index.name = "WACC"
    ev_df.columns.name = "Terminal Growth"
    ev_df.to_csv(output_dir / "sensitivity_ev.csv")
    
    # Plotting
    try:
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create heatmap using imshow
        im = ax.imshow(ev_matrix, cmap="RdYlGn", aspect='auto')
        
        # Add text annotations
        for i in range(len(wacc_values)):
            for j in range(len(g_values)):
                val = ev_matrix[i, j]
                text_color = "black" if val > np.median(ev_matrix) else "white" # Basic contrast
                # If 0 (invalid), show N/A
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
        
        output_path = output_dir / "sensitivity.png"
        plt.savefig(output_path)
        plt.close()
    except Exception as e:
        print(f"[ERROR] Could not generate plot: {e}")
