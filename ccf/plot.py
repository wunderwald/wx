import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

def plot_windowed_cross_correlation(results, max_lag, step_size, signal_a, signal_b):
    """
    Plot the results of the windowed cross-correlation.

    Parameters:
        results (list of dict): Output from `windowed_cross_correlation`.
        max_lag (int): Maximum lag used in the computation.
        step_size (int): Step size for the sliding window.
    """
    # Extract values for plotting
    window_starts = [res['start_idx'] for res in results]
    r_max_values = [res['r_max'] for res in results]
    tau_max_values = [res['tau_max'] for res in results]

    # init plot layout
    plt.figure(figsize=(16, 8))
    gs = gridspec.GridSpec(4, 1, height_ratios=[5, 1, 1, 1])
    plt.subplot(gs[0]) 
    plt.subplot(gs[1]) 
    plt.subplot(gs[2]) 
    plt.subplot(gs[3]) 

    # Create a heatmap of correlations
    heatmap_data = np.array([res['correlations'] for res in results])
    plt.subplot(4, 1, 1)
    plt.imshow(heatmap_data.T, aspect='auto', cmap='viridis', extent=[0, len(results) * step_size, -max_lag, max_lag])
    plt.colorbar(label='Correlation')
    plt.xlabel('Window Start Index')
    plt.ylabel('Lag')
    plt.title('Correlation Heatmap')

    # Plot input signals over time
    plt.subplot(4, 1, 2)
    plt.plot(signal_a, label='Signal a')
    plt.plot(signal_b, label='Signal b')
    plt.xlabel('Time')
    plt.ylabel('Sample Value')
    plt.title('Signals over time')
    plt.legend()
    plt.grid()

    # Plot peak correlation values over time
    plt.subplot(4, 1, 3)
    plt.plot(window_starts, r_max_values, marker='o', label='Peak Correlation')
    plt.xlabel('Window Start Index')
    plt.ylabel('r_max')
    plt.title('Peak Correlation Over Time')
    plt.legend()
    plt.grid()

    # Plot corresponding lags over time
    plt.subplot(4, 1, 4)
    plt.plot(window_starts, tau_max_values, marker='o', label='Lag at Peak')
    plt.xlabel('Window Start Index')
    plt.ylabel('tau_max')
    plt.title('Lag at Peak Correlation Over Time')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()

    
