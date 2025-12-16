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

def plot_windowed_cross_correlation(wxc_data, window_size, max_lag, step_size, signal_a, signal_b, use_lag_filter=False, lag_filter_min=None, lag_filter_max=None, use_win_center_tscl=False):
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

    # get lag range (filtered or unfiltered) for y-axis
    _min_lag = -max_lag
    _max_lag = max_lag
    if use_lag_filter and not (lag_filter_min is None or lag_filter_max is None):
        _min_lag = min(lag_filter_min, lag_filter_max)
        _max_lag = max(lag_filter_min, lag_filter_max)

    # Create a heatmap of correlations
    ax1 = fig.add_subplot(gs[0])
    heatmap_data = np.array([res['correlations'] for res in wxc_data])
    im = ax1.imshow(
        heatmap_data.T,
        aspect='auto',
        cmap='magma', # options: viridis, plasma, magma...
        extent=[0, len(wxc_data) * step_size, _min_lag, _max_lag] if not use_win_center_tscl
          else [window_size // 2, (len(wxc_data)-1) * step_size + window_size // 2, _min_lag, _max_lag]
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

def make_plot_titles_preproc(dyad_folder, selected_sheet, filename_a, filename_b, column_a, column_b, is_resampled):
    """
    Generate plot titles for preprocessed signal visualization.

    Args:
        dyad_folder (str): Name of the dyad folder.
        selected_sheet (str): Name of the selected sheet in the Excel files.
        filename_a (str): Filename of the first Excel file.
        filename_b (str): Filename of the second Excel file.
        column_a (str): Column name for the first signal.
        column_b (str): Column name for the second signal.
        is_resampled (bool): Whether the signals have been resampled to 5Hz.

    Returns:
        dict: Dictionary with keys 'a' and 'b' containing formatted title strings for each signal.
    """
    title_a = f"Data in column '{column_a}' of sheet '{selected_sheet}' of '{filename_a}' [in folder '{dyad_folder}']{' - resampled to 5hz' if is_resampled else ''}"
    title_b = f"Data in column '{column_b}' of sheet '{selected_sheet}' of '{filename_b}' [in folder '{dyad_folder}']{' - resampled to 5hz' if is_resampled else ''}"
    return {'a': title_a, 'b': title_b}

def plot_preprocessed_signals(signal_a, signal_b, plot_titles):
    """
    Plot two preprocessed signals on separate subplots.
    Args: 
        signal_a (array-like): First signal to plot.
        signal_a (array-like): Second signal to plot.
        plot_titles (dict): Dictionary containing plot titles with keys 'a' and 'b'.
    Returns:
        matplotlib.figure.Figure: The figure containing the plot.
    """
    # Initialize plot layout
    fig = plt.figure(figsize=FIGSIZE)
    gs = gridspec.GridSpec(2, 1)
    
    # Plot signal_a
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(signal_a, color='blue')
    ax1.set_title(plot_titles['a'])
    ax1.set_xlabel('Index')
    ax1.set_ylabel('Value')
    ax1.grid()
    
    # Plot signal_b
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(signal_b, color='purple')
    ax2.set_title(plot_titles['b'])
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
    use_lag_filter = params['use_lag_filter']
    lag_filter_min = params['lag_filter_min']
    lag_filter_max = params['lag_filter_max']
    
    # create and store plot figure
    fig = plot_windowed_cross_correlation(windowed_xcorr_data, window_size, max_lag, step_size, signal_a, signal_b, use_lag_filter=use_lag_filter, lag_filter_min=lag_filter_min, lag_filter_max=lag_filter_max, use_win_center_tscl=use_timescale_win_center)
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
    """
    Updates the preprocessing preview plots based on the provided parameters.
    Args:
        params (dict): A dictionary containing the following keys:
            - "signal_a" (array-like): The first signal data.
            - "signal_b" (array-like): The second signal data.
            - "dyad_folder" (str): Path to the dyad folder.
            - "selected_sheet" (str): Name of selected sheet.
            - "filename_a" (str): Filename associated with signal_a.
            - "filename_b" (str): Filename associated with signal_b.
            - "column_a" (str): Column name for signal_a.
            - "column_b" (str): Column name for signal_b.
            - "is_resampled" (bool): Flag indicating whether signals have been resampled (to 5hz).
    Returns:
        matplotlib.figure.Figure: The figure object containing the updated plot.
    """
    signal_a = params["signal_a"]
    signal_b = params["signal_b"]
    plot_titles = make_plot_titles_preproc(params["dyad_folder"], params["selected_sheet"], params["filename_a"], params["filename_b"], params["column_a"], params["column_b"], params["is_resampled"])
    fig = plot_preprocessed_signals(signal_a, signal_b, plot_titles)
    return fig