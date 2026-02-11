import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any

def plot_sensitivity(sensitivity_data: Dict[str, Any], output_dir: Path) -> None:
    """
    Generates a sensitivity heatmap from pre-calculated data.
    """
    ev_df = sensitivity_data["matrix"]
    ev_matrix = ev_df.values
    wacc_values = ev_df.index.values
    g_values = ev_df.columns.values
    
    # Export CSV
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
        
        output_path = output_dir / "sensitivity.png"
        plt.savefig(output_path)
        plt.close()
    except Exception as e:
        print(f"[ERROR] Could not generate plot: {e}")
