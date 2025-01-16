import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

FIGSIZE=(10, 8)

def plot_init():
    fig = plt.figure(figsize=FIGSIZE)
    return fig

def plot_windowed_cross_correlation(results, window_size, max_lag, step_size, signal_a, signal_b, use_win_center_tscl=False):
    """
    Create and return a figure plotting the results of the windowed cross-correlation.

    Args:
        results (list of dict): Output from `windowed_cross_correlation`.
        max_lag (int): Maximum lag used in the computation.
        step_size (int): Step size for the sliding window.
        signal_a (array-like): First input signal.
        signal_b (array-like): Second input signal.
        use_win_center_tscl (bool): Use time/index of window centers for time axes (instead of window start indices; this helps to compare to other plots)

    Returns:
        matplotlib.figure.Figure: The figure containing the plots.
    """
    # Extract values for plotting
    window_start_indices = [res['start_idx'] for res in results]
    window_center_indices = [res['center_idx'] for res in results]
    r_max_values = [res['r_max'] for res in results]
    tau_max_values = [res['tau_max'] for res in results]

    # Initialize plot layout
    fig = plt.figure(figsize=FIGSIZE)
    gs = gridspec.GridSpec(4, 1, height_ratios=[5, 1, 1, 1])

    # Create a heatmap of correlations
    ax1 = fig.add_subplot(gs[0])
    heatmap_data = np.array([res['correlations'] for res in results])
    im = ax1.imshow(
        heatmap_data.T,
        aspect='auto',
        cmap='magma', # options: viridis, plasma, magma...
        extent=[0, len(results) * step_size, -max_lag, max_lag] if not use_win_center_tscl
          # else [max_lag, (len(results)-1) * step_size + max_lag, -max_lag, max_lag]
          else [window_size // 2, (len(results)-1) * step_size + window_size // 2, -max_lag, max_lag]
    )
    fig.colorbar(im, ax=ax1, label='Correlation')
    ax1.set_xlabel('Window Start Index' if not use_win_center_tscl else 'Time')
    ax1.set_ylabel('Lag')
    ax1.set_title('Correlation Heatmap')

    # Plot input signals over time
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(signal_a, label='Signal a', color='blue')
    ax2.plot(signal_b, label='Signal b', color='purple')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Sample Value')
    ax2.set_title('Signals over time')
    ax2.legend()
    ax2.grid()

    # Plot peak correlation values over time
    ax3 = fig.add_subplot(gs[2])
    ax3.plot(window_start_indices if not use_win_center_tscl else window_center_indices, r_max_values, marker='o', color='black', label='Peak Correlation')
    ax3.set_xlabel('Window Start Index' if not use_win_center_tscl else 'Time [window centers]')
    ax3.set_ylabel('r_max')
    ax3.set_title('Peak Correlation Over Time')
    ax3.legend()
    ax3.grid()

    # Plot corresponding lags over time
    ax4 = fig.add_subplot(gs[3])
    ax4.plot(window_start_indices if not use_win_center_tscl else window_center_indices, tau_max_values, marker='o', color='black', label='Lag at Peak')
    ax4.set_xlabel('Window Start Index' if not use_win_center_tscl else 'Time [window centers]')
    ax4.set_ylabel('tau_max')
    ax4.set_title('Lag at Peak Correlation Over Time')
    ax4.legend()
    ax4.grid()

    # Adjust layout
    fig.tight_layout()

    # Return the figure
    return fig

def plot_standard_cross_correlation(signal_a, signal_b, corr, lags):
    """
    Create and return a figure plotting the standard cross-correlation between two signals.

    Args:
        signal_a (array-like): First input signal.
        signal_b (array-like): Second input signal.
        corr (array-like): Cross-correlation values.
        lags (array-like): Array of lag values.

    Returns:
        matplotlib.figure.Figure: The figure containing the plot.
    """
    # Initialize plot layout
    fig = plt.figure(figsize=FIGSIZE)
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

    # Plot cross-correlation
    ax2 = fig.add_subplot(gs[0])
    ax2.plot(lags, corr, marker='o', color='black')
    ax2.set_xlabel('Lag')
    ax2.set_ylabel('Cross-correlation')
    ax2.set_title('Standard Cross-correlation')
    ax2.grid()

    # Plot input signals over time
    ax1 = fig.add_subplot(gs[1])
    ax1.plot(signal_a, label='Signal a', color='blue')
    ax1.plot(signal_b, label='Signal b', color='purple')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Sample Value')
    ax1.set_title('Signals over time')
    ax1.legend()
    ax1.grid()

    # Return figure object
    fig.tight_layout()
    return fig