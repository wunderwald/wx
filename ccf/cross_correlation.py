import numpy as np

def windowed_cross_correlation(x, y, window_size, step_size, max_lag, absolute=False, average_windows=False):
    """
    Compute windowed cross-correlation between two time series.

    Parameters:
        x (np.ndarray): First time series.
        y (np.ndarray): Second time series.
        window_size (int): Number of data points in each window.
        step_size (int): Step size for the sliding window.
        max_lag (int): Maximum lag to compute cross-correlation.
        absolute (bool): Calculate abs of correlation values.
        average_windows (bool): Calculate per-window averages.

    Returns:
        results (list of dict): A list containing the results for each window. 
            Each result is a dictionary with keys:
                - 'start_idx': Start index of the window in the time series.
                - 'center_idx': Index of window center in time series (allows aligning correlation result with input time series).
                - 'r_max': Peak cross-correlation value in the window.
                - 'tau_max': Lag at which the peak correlation occurs.
                - 'correlations': Array of cross-correlation values for all lags.
    """
    n = len(x)
    results = []

    # Ensure inputs are numpy arrays
    x = np.asarray(x)
    y = np.asarray(y)

    for start in range(0, n - window_size + 1, step_size):
        # Extract the windowed segments
        x_window = x[start:start + window_size]
        y_window = y[start:start + window_size]

        # Normalize the segments (zero mean, unit variance)
        x_window = (x_window - np.mean(x_window)) / np.std(x_window)
        y_window = (y_window - np.mean(y_window)) / np.std(y_window)

        # Compute cross-correlation for lags in the range [-max_lag, max_lag]
        correlations = []
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                corr = np.mean(x_window[:lag] * y_window[-lag:])
            elif lag > 0:
                corr = np.mean(x_window[lag:] * y_window[:-lag])
            else:
                corr = np.mean(x_window * y_window)
            if absolute: corr = np.abs(corr)
            correlations.append(corr)

        # optionally average correlation values in window
        if average_windows:
            avg = np.mean(np.array(correlations))
            #correlations = [avg for c in correlations]
            correlations = [avg]

        # Find the peak correlation and its corresponding lag
        correlations = np.array(correlations)
        r_max = np.max(correlations)
        tau_max = np.argmax(correlations) - max_lag if not average_windows else 0

        # Store results for this window
        results.append({
            'start_idx': start,
            'center_idx': start + window_size//2,
            'r_max': r_max,
            'tau_max': tau_max,
            'correlations': correlations
        })

    return results