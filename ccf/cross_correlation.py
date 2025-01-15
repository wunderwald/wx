import numpy as np
import matplotlib.pyplot as plt

def cross_correlation(signal1, signal2, max_lag=None):
    """
    Calculate the cross-correlation of two signals up to a maximum lag.
    
    Parameters:
    signal1 (array-like): First input signal.
    signal2 (array-like): Second input signal.
    max_lag (int, optional): Maximum lag to compute the cross-correlation. If None, compute full cross-correlation.
    
    Returns:
    array: Cross-correlation of the two signals.
    """
    corr = np.correlate(signal1, signal2, mode='full')
    if max_lag is not None:
        center = len(corr) // 2
        start = max(center - max_lag, 0)
        end = min(center + max_lag + 1, len(corr))
        corr = corr[start:end]
    return corr

def windowed_cross_correlation(signal1, signal2, window_size):
    """
    Calculate the windowed cross-correlation of two signals up to a maximum lag.
    
    Parameters:
    signal1 (array-like): First input signal.
    signal2 (array-like): Second input signal.
    window_size (int): Size of the window to compute the cross-correlation.
    max_lag (int, optional): Maximum lag to compute the cross-correlation. If None, compute full cross-correlation.
    
    Returns:
    array: Windowed cross-correlation of the two signals.
    """
    n = len(signal1)
    result = []
    for i in range(n - window_size + 1):
        window1 = signal1[i:i + window_size]
        window2 = signal2[i:i + window_size]
        corr = cross_correlation(window1, window2)
        result.append(corr)
    return np.array(result)

# Generate two random sequences, each with 100 elements
np.random.seed(0)  # For reproducibility
signal1 = np.random.randn(100)
signal2 = np.random.randn(100)

# Example usage of the cross_correlation function
corr = cross_correlation(signal1, signal2)
print("Cross-correlation:", corr)

# Example usage of the windowed_cross_correlation function with a window size of 10
windowed_corr = windowed_cross_correlation(signal1, signal2, window_size=10)
print("Windowed cross-correlation:", windowed_corr)

print(windowed_corr.shape)