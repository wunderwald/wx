import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

RETINA = True

FIGSIZE = (5, 4) if RETINA else (10, 8)

if RETINA:
    plt.rcParams.update({
        'font.size': 6,         # Default font size
        'axes.titlesize': 4,    # Title font size
        'axes.labelsize': 4,    # Axis label font size
        'xtick.labelsize': 4,   # X-axis tick label font size
        'ytick.labelsize': 4,   # Y-axis tick label font size
        'lines.linewidth': 1,    # Line width
    })

def plot_init():
    fig = plt.figure(figsize=FIGSIZE)
    return fig

def plot_windowed_cross_correlation(wxc_data, window_size, max_lag, step_size, signal_a, signal_b, use_win_center_tscl=False):
    """
    Create and return a figure plotting the wxc_data of the windowed cross-correlation.

    Args:
        wxc_data (list of dict): Output from `windowed_cross_correlation`.
        max_lag (int): Maximum lag used in the computation.
        step_size (int): Step size for the sliding window.
        signal_a (array-like): First input signal.
        signal_b (array-like): Second input signal.
        use_win_center_tscl (bool): Use time/index of window centers for time axes (instead of window start indices; this helps to compare to other plots)

    Returns:
        matplotlib.figure.Figure: The figure containing the plots.
    """
    # Extract values for plotting
    window_start_indices = [res['start_idx'] for res in wxc_data]
    window_center_indices = [res['center_idx'] for res in wxc_data]
    r_max_values = [res['r_max'] for res in wxc_data]
    tau_max_values = [res['tau_max'] for res in wxc_data]

    # Initialize plot layout
    fig = plt.figure(figsize=FIGSIZE)
    # gs = gridspec.GridSpec(4, 1, height_ratios=[5, 1, 1, 1])
    gs = gridspec.GridSpec(4, 1, height_ratios=[8, 1, 1, 1])

    # Create a heatmap of correlations
    ax1 = fig.add_subplot(gs[0])
    heatmap_data = np.array([res['correlations'] for res in wxc_data])
    im = ax1.imshow(
        heatmap_data.T,
        aspect='auto',
        cmap='magma', # options: viridis, plasma, magma...
        extent=[0, len(wxc_data) * step_size, -max_lag, max_lag] if not use_win_center_tscl
          # else [max_lag, (len(wxc_data)-1) * step_size + max_lag, -max_lag, max_lag]
          else [window_size // 2, (len(wxc_data)-1) * step_size + window_size // 2, -max_lag, max_lag]
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
    ax3.plot(window_start_indices if not use_win_center_tscl else window_center_indices, r_max_values, marker='o', markersize=.8, color='black', label='Peak Correlation')
    ax3.set_xlabel('Window Start Index' if not use_win_center_tscl else 'Time [window centers]')
    ax3.set_ylabel('r_max')
    ax3.set_title('Peak Correlation Over Time')
    ax3.legend()
    ax3.grid()

    # Plot corresponding lags over time
    ax4 = fig.add_subplot(gs[3])
    ax4.plot(window_start_indices if not use_win_center_tscl else window_center_indices, tau_max_values, marker='o', markersize=.8, color='black', label='Lag at Peak')
    ax4.set_xlabel('Window Start Index' if not use_win_center_tscl else 'Time [window centers]')
    ax4.set_ylabel('tau_max')
    ax4.set_title('Lag at Peak Correlation Over Time')
    ax4.legend()
    ax4.grid()

    # Adjust layout
    fig.tight_layout()

    # Return the figure
    return fig

def plot_standard_cross_correlation(sxc_data, signal_a, signal_b):
    """
    Create and return a figure plotting the standard cross-correlation between two signals.

    Args:
        sxc_data (dict): Dictionary containing 'corr' (correlation values) and 'lags' arrays.
        signal_a (array-like): First input signal.
        signal_b (array-like): Second input signal.

    Returns:
        matplotlib.figure.Figure: The figure containing the plot.
    """
    corr = sxc_data['corr']
    lags = sxc_data['lags']

    # Initialize plot layout
    fig = plt.figure(figsize=FIGSIZE)
    gs = gridspec.GridSpec(3, 1, height_ratios=[3, 1, 1])

    # Plot cross-correlation
    ax2 = fig.add_subplot(gs[0])
    ax2.plot(lags, corr, marker='o', color='black')
    ax2.set_xlabel('Lag')
    ax2.set_ylabel('Cross-correlation')
    ax2.set_title('Standard Cross-correlation')
    ax2.grid()

    # Plot input signal a over time
    ax1 = fig.add_subplot(gs[1])
    ax1.plot(signal_a, label='Signal a', color='blue')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Sample Value')
    ax1.legend()
    ax1.grid()

    # Plot input signal b over time
    ax1 = fig.add_subplot(gs[2])
    ax1.plot(signal_b, label='Signal b', color='purple')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Sample Value')
    ax1.legend()
    ax1.grid()

    # Return figure object
    fig.tight_layout()
    return fig

def plot_preprocessed_signals(signal_a, signal_b):
    # Initialize plot layout
    fig = plt.figure(figsize=FIGSIZE)
    gs = gridspec.GridSpec(2, 1)
    
    # Plot signal_a
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(signal_a, color='blue')
    ax1.set_title('signal_a')
    ax1.set_xlabel('Index')
    ax1.set_ylabel('Value')
    ax1.grid()
    
    # Plot signal_b
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(signal_b, color='purple')
    ax2.set_title('signal_b')
    ax2.set_xlabel('Index')
    ax2.set_ylabel('Value')
    ax2.grid()
    
    fig.tight_layout()
    return fig

# update windowed xcorr plots
def update_wxcorr_plots(params):
    """
    Updates the windowed cross-correlation plots based on the provided parameters.
    Args:
        params (dict): A dictionary containing the following keys:
            - "signal_a" (array-like): The first signal data.
            - "signal_b" (array-like): The second signal data.
            - "window_size" (int): The size of the window for cross-correlation.
            - "step_size" (int): The step size for moving the window.
            - "max_lag" (int): The maximum lag to consider in the cross-correlation.
            - "use_timescale_win_center" (bool): Flag indicating whether window center times or window start indices are used for time axis.
            - "windowed_xcorr_data" (array-like): The precomputed windowed cross-correlation data.
    Returns:
        matplotlib.figure.Figure: The figure object containing the updated plot.
    """
    signal_a = params["signal_a"]
    signal_b = params["signal_b"]
    window_size = params['window_size']
    step_size = params['step_size']
    max_lag = params['max_lag']
    windowed_xcorr_data = params['windowed_xcorr_data']
    use_timescale_win_center = params['use_timescale_win_center']
    
    # create and store plot figure
    fig = plot_windowed_cross_correlation(windowed_xcorr_data, window_size, max_lag, step_size, signal_a, signal_b, use_win_center_tscl=use_timescale_win_center)
    return fig

# update standard xcorr plots
def update_sxcorr_plots(params):
    """
    Updates the standard cross-correlation plots based on the provided parameters.
    Args:
        params (dict): A dictionary containing the following keys:
            - "signal_a" (array-like): The first signal data.
            - "signal_b" (array-like): The second signal data.
            - "xcorr_data" (array-like): The cross-correlation data.
    Returns:
        matplotlib.figure.Figure: The figure object containing the updated cross-correlation plot.
    """

    # read data from data containers and state variables
    signal_a = params["signal_a"]
    signal_b = params["signal_b"]
    xcorr_data = params["xcorr_data"]

    # create and store plot figure
    fig = plot_standard_cross_correlation(xcorr_data, signal_a, signal_b)
    return fig

# update preprocessing preview plots
def update_preproc_plots(params):
    # extract data
    signal_a = params["signal_a"]
    signal_b = params["signal_b"]
    # create figure
    fig = plot_preprocessed_signals(signal_a, signal_b)
    return fig