import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def plot_sensitivity(base_projections: pd.DataFrame, base_wacc: float, base_g: float, output_dir: Path) -> None:
    """
    Generates a sensitivity heatmap for Enterprise Value based on range of WACC and Terminal Growth.
    Uses only matplotlib as requested.
    """
    # Define ranges
    wacc_steps = 6
    g_steps = 6
    
    # Create ranges centered on base case
    wacc_range = np.linspace(base_wacc - 0.015, base_wacc + 0.015, wacc_steps)
    g_range = np.linspace(base_g - 0.015, base_g + 0.015, g_steps)
    
    # Initialize EV matrix
    ev_matrix = np.zeros((wacc_steps, g_steps))
    
    # Pre-calculate discount periods
    periods = np.arange(1, len(base_projections) + 1)
    fcf = base_projections["fcf"].values
    last_fcf = fcf[-1]
    
    # Calculate EV for each cell
    for i, w in enumerate(wacc_range):
        discount_factors = (1 + w) ** -periods
        pv_explicit = np.sum(fcf * discount_factors)
        last_factor = discount_factors[-1]
        
        for j, g in enumerate(g_range):
            if w <= g:
                ev = 0 # Invalid
            else:
                tv = last_fcf * (1 + g) / (w - g)
                pv_terminal = tv * last_factor
                ev = pv_explicit + pv_terminal
            
            ev_matrix[i, j] = ev
            
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create heatmap using imshow
    # Origin 'lower' means (0,0) is bottom-left, but usually matrices are top-left.
    # We want WACC on Y (increasing down or up?) and g on X.
    # Let's put WACC on Y (rows) and g on X (cols).
    # Matplotlib imshow displays [0,0] at top-left by default.
    im = ax.imshow(ev_matrix, cmap="RdYlGn", aspect='auto')
    
    # Add text annotations
    for i in range(wacc_steps):
        for j in range(g_steps):
            text = ax.text(j, i, f"{ev_matrix[i, j]:,.0f}",
                           ha="center", va="center", color="black", fontsize=8)

    # Set ticks and labels
    ax.set_xticks(np.arange(g_steps))
    ax.set_yticks(np.arange(wacc_steps))
    
    # Format labels as percentages
    ax.set_xticklabels([f"{x:.1%}" for x in g_range])
    ax.set_yticklabels([f"{y:.1%}" for y in wacc_range])
    
    ax.set_xlabel("Terminal Growth (g)")
    ax.set_ylabel("WACC")
    ax.set_title("Sensitivity Analysis: Enterprise Value (WACC vs Terminal Growth)")
    
    # Add colorbar
    plt.colorbar(im, ax=ax, label="Enterprise Value")
    
    output_path = output_dir / "sensitivity.png"
    plt.savefig(output_path)
    plt.close()
