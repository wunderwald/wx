import numpy as np
from scipy.interpolate import CubicSpline

def _remove_invalid_IBI(ibi_ms):
    return [sample for sample in ibi_ms if sample >= 100 and sample < 1000]

def _remove_invalid_EDA(eda):
    print("!! EDA filter not implemented yet.")
    return [sample for sample in eda if sample >= 0]

def resample_ibi(ibi_ms, target_sampling_rate_hz=5, scale_output=False):  
    """
    Resample inter-beat intervals (IBI) to a target sampling rate using cubic spline interpolation.
    Parameters:
    -----------
    ibi_ms : list or array-like
        List or array of inter-beat intervals in milliseconds.
    target_sampling_rate_hz : int, optional
        The target sampling rate in Hertz (Hz). Default is 5 Hz.
    scale_output : bool, optional
        If True, scales the output IBI to maintain the same total sum as the original IBI. Default is False.
    filter_ibi : bool, optional
        If True, filters out invalid IBI samples before resampling. Default is True.
    Returns:
    --------
    ibi_ms_interpl_out : numpy.ndarray
        The resampled IBI values.
    """
    # convert ibi to time series (t, ibi)
    t_ms_ts = np.cumsum(np.insert(ibi_ms, 0, 0)[:-1])
    ibi_ms_ts = np.array(ibi_ms)

    # Create a cubic spline interpolation
    cs = CubicSpline(t_ms_ts, ibi_ms_ts)

    # Generate time grid for interpolation
    sampling_interval_ms = 1000/target_sampling_rate_hz
    t_ms_interpl = np.arange(min(t_ms_ts), max(t_ms_ts), sampling_interval_ms)

    # Get sample values at new grid
    ibi_ms_interpl = cs(t_ms_interpl)

    # optionally scale interpolated ibi
    sum_ibi_original = sum(ibi_ms)
    sum_ibi_interpl = sum(ibi_ms_interpl)
    scl = sum_ibi_original / sum_ibi_interpl
    ibi_ms_interpl_out = ibi_ms_interpl * (scl if scale_output else 1)

    return ibi_ms_interpl_out



def preprocess_dyad(signal_a, signal_b, signal_type, remove_invalid_samples=False):
    """
    Preprocesses two signals (dyad) by filtering invalid values, resampling, and aligning their lengths.
    Parameters:
        signal_a (list or array-like): The first signal to preprocess.
        signal_b (list or array-like): The second signal to preprocess.
        signal_type (str): The type of the signals, must be either 'IBI_MS' or 'EDA'.
        remove_invalid_samples (bool, optional): If True, invalid samples will be removed from the signals. Defaults to False.
    Returns:
        tuple: A tuple containing the preprocessed signal_a and signal_b.
    Raises:
        Exception: If the signal_type is not 'IBI_MS' or 'EDA'.
    """
    if signal_type not in ['IBI_MS', 'EDA']:
        raise Exception("Invalid signal type. Must be 'IBI_MS' or 'EDA'.")
    
    # optionally remove invalid values
    if remove_invalid_samples:
        signal_a = _remove_invalid_IBI(signal_a) if signal_type == 'IBI_MS' else _remove_invalid_EDA(signal_a)
        signal_b = _remove_invalid_IBI(signal_b) if signal_type == 'IBI_MS' else _remove_invalid_EDA(signal_b)

    # TODO: in IBI data - first and last sample should only be used for timing, they are not valid ibi samples

    # resample IBI
    if signal_type == 'IBI_MS':
        signal_a = resample_ibi(signal_a, target_sampling_rate_hz=5)
        signal_b = resample_ibi(signal_b, target_sampling_rate_hz=5)

    # fix lengths
    min_length = min(len(signal_a), len(signal_b))
    signal_a = signal_a[:min_length]
    signal_b = signal_b[:min_length]

    return signal_a, signal_b