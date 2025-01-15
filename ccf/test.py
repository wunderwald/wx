from plot import plot_windowed_cross_correlation
from cross_correlation import windowed_cross_correlation
import numpy as np

length = 400
signal1 = np.sin(np.linspace(0, 5 * np.pi, length))
signal2 = np.cos(np.linspace(0, 4 * np.pi, length))

window_size = 40
step_size=5 # default: window size
max_lag=window_size//2

windowed_corr_data = windowed_cross_correlation(signal1, signal2, window_size=window_size, step_size=step_size, max_lag=max_lag)
plot_windowed_cross_correlation(windowed_corr_data, max_lag, step_size, signal1, signal2)
