import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

def _invalid_ibi_sample_indices(ibi_ms):
    invalidIndices = []
    for i, sample in enumerate(ibi_ms):
        if sample > 1500 or sample < 100:
            invalidIndices.append(i)
    return invalidIndices

def resample_ibi(ibi_ms, target_sampling_rate_hz=5, scale_output=False, filter_ibi=True):  
    # convert ibi to time series (t, ibi)
    t_ms_raw = np.cumsum(np.insert(t_ms_raw, 0, 0)[:-1])
    ibi_ms_raw = np.array(ibi_ms)

    # clean ibi time series
    delete_indices = _invalid_ibi_sample_indices(ibi_ms_raw) if filter_ibi else []
    t_ms_clean = np.delete(t_ms_raw, delete_indices)
    ibi_ms_clean = np.delete(ibi_ms_raw, delete_indices)

    # Create a cubic spline interpolation
    cs = CubicSpline(t_ms_clean, ibi_ms_clean)

    # Generate time grid for interpolation
    sampling_interval_ms = 1000/target_sampling_rate_hz
    t_ms_interpl = np.arange(min(t_ms_clean), max(t_ms_clean), sampling_interval_ms)

    # Get sample values at new grid
    ibi_ms_interpl = cs(t_ms_interpl)

    # optionally scale interpolated ibi
    sum_ibi_original = sum(ibi_ms)
    sum_ibi_interpl = sum(ibi_ms_interpl)
    scl = sum_ibi_original / sum_ibi_interpl
    ibi_ms_interpl_out = ibi_ms_interpl * (scl if scale_output else 1)

    return ibi_ms_interpl_out