import os
import xlsx

def export_wxcorr_data(file_path, params):
    metadata = {
        'xcorr type': "windowed cross-correlation",
        'Input dyad directory': f"{os.path.basename(params['selected_dyad_dir'])}",
        'Input file A': f"{os.path.basename(params['selected_file_a'])}",
        'Input file B': f"{os.path.basename(params['selected_file_b'])}",
        'Phsyiological data type': 'EDA' if params['checkbox_EDA'] else 'IBI', 
        'Window size': params['window_size'],
        'Max lag': params['max_lag'],
        'Step size': params['step_size'],
        'Window overlap ratio': (params['window_size'] - params['step_size']) / params['window_size'],
        'Absolute correlation values': params['checkbox_absolute_corr'],
        'Per-window averages': params['checkbox_average_windows'],
        'Input signals resampled to 5hz': params['checkbox_IBI'],
    }
    vectors = {
        'signal_a': params['signal_a'],
        'signal_b': params['signal_b'],
        'window start index': [o['start_idx'] for o in params['wxcorr']],
        'max correlation (r_max)': [o['r_max'] for o in params['wxcorr']],
        'lag of max correlation (tau_max)': [o['tau_max'] for o in params['wxcorr']],
    }
    for window_index, window in enumerate(params['wxcorr']):
        vectors[f"w_{window_index}_correlations"] = window['correlations']
        vectors[f"w_{window_index}_meta"] = [ f"start_idx={window['start_idx']}", f"center_idx={window['center_idx']}", f"r_max={window['r_max']}", f"tau_max={window['tau_max']}" ]

    xlsx.write_xlsx(vectors=vectors, single_values=metadata, output_path=file_path)

def export_sxcorr_data(file_path, params):
    metadata = {
        'xcorr type': "(standard) cross-correlation",
        'Input dyad directory': f"{os.path.basename(params['selected_dyad_dir'])}",
        'Input file A': f"{os.path.basename(params['selected_file_a'])}",
        'Input file B': f"{os.path.basename(params['selected_file_b'])}",
        'Phsyiological data type': 'EDA' if params['checkbox_EDA'] else 'IBI', 
        'Max lag': params['max_lag'],
        'Absolute correlation values': params['checkbox_absolute_corr'],
        'Input signals resampled to 5hz': params['checkbox_IBI'],
    }
    vectors = {
        'signal_a': params['signal_a'],
        'signal_b': params['signal_b'],
        'lag': params['sxcorr']['lags'],
        'correlation': params['sxcorr']['corr'],
    }
    xlsx.write_xlsx(vectors=vectors, single_values=metadata, output_path=file_path)