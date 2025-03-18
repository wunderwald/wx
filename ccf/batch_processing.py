import os
import xlsx
from signal_processing import preprocess_dyad
from export import export_sxcorr_data, export_wxcorr_data
from cross_correlation import windowed_cross_correlation, standard_cross_correlation

def _process_dyad(batch_input_folder, dyad_folder, output_dir, params):
    # get list of xlsx files in dyad folder
    xlsx_files = [f for f in os.listdir(os.path.join(batch_input_folder, dyad_folder)) if f.endswith('.xlsx')]
    if len(xlsx_files) < 2:
        print(f"! {dyad_folder}-  ")
        return
    # select the two files of the dyad
    file_path_a = os.path.join(batch_input_folder, dyad_folder, xlsx_files[0])
    file_path_b = os.path.join(batch_input_folder, dyad_folder, xlsx_files[1])
    # read data to workbooks
    wb_a = xlsx.read_xlsx(file_path_a)
    wb_b = xlsx.read_xlsx(file_path_b)

    try:
        # create columns object from selected sheet
        columns_a = xlsx.get_columns(wb_a, params['selected_sheet'], headers=params['workbook_data']['has_headers'])
        columns_b = xlsx.get_columns(wb_b, params['selected_sheet'], headers=params['workbook_data']['has_headers'])

        # get raw data
        raw_signal_a = columns_a[params['workbook_data']['selected_column_a']]
        raw_signal_b = columns_b[params['workbook_data']['selected_column_b']]

        # process data
        signal_a, signal_b = preprocess_dyad(
            raw_signal_a,
            raw_signal_b,
            signal_type='IBI_MS' if params['checkbox_IBI'] else 'EDA'
        )

        # make and export correlation data
        if params['checkbox_windowed_xcorr']:
            # WXCorr
            window_size = params['window_size']
            step_size = params['step_size']
            max_lag = params['max_lag']
            absolute_values = params['checkbox_absolute_corr']
            average_windows = params['checkbox_average_windows']
            corr_data = windowed_cross_correlation(signal_a, signal_b, window_size=window_size, step_size=step_size, max_lag=max_lag, absolute=absolute_values, average_windows=average_windows)
            # export
            export_params = {
                'selected_dyad_dir': dyad_folder,
                'selected_file_a': file_path_a,
                'selected_file_b': file_path_b,
                'checkbox_EDA': params['checkbox_EDA'],
                'window_size': params['window_size'],
                'max_lag': params['max_lag'],
                'step_size': params['step_size'],
                'checkbox_absolute_corr': params['checkbox_absolute_corr'],
                'checkbox_average_windows': params['checkbox_average_windows'],
                'checkbox_IBI': params['checkbox_IBI'],
                'signal_a': signal_a,
                'signal_b': signal_b,
                'wxcorr': corr_data
            }
            output_file_name = f"{dyad_folder}_wxcorr.xlsx"
            output_file_path = os.path.join(output_dir, output_file_name)
            export_wxcorr_data(output_file_path, export_params)
        else:
            # Standard XCorr
            max_lag = params['max_lag_sxc']
            absolute_values = params['checkbox_absolute_corr_sxc']
            corr_data = standard_cross_correlation(signal_a, signal_b, max_lag=max_lag, absolute=absolute_values)
            # export
            export_params = {
                'selected_dyad_dir': dyad_folder,
                'selected_file_a': file_path_a,
                'selected_file_b': file_path_b,
                'checkbox_EDA': params['checkbox_EDA'],
                'max_lag': params['max_lag_sxc'],
                'checkbox_absolute_corr': params['checkbox_absolute_corr_sxc'],
                'checkbox_IBI': params['checkbox_IBI'],
                'signal_a': signal_a,
                'signal_b': signal_b,
                'sxcorr': corr_data
            }
            output_file_path = os.path.join(output_dir, output_file_name)
            export_sxcorr_data(output_file_path, export_params)
    except Exception as e:
        print(f"! {dyad_folder}: {e}")

def random_pair_analysis(params):
    # TODO: run random pair analysis
    pass

def batch_process(params):
    """
    Processes a batch of dyad data files, performs cross-correlation analysis, and exports the results.
    Args:
        params (dict): A dictionary containing the following keys:
            - batch_input_folder (str): Path to the directory containing dyad folders.
            - output_dir (str): Path to the directory where output files will be saved.
            - selected_sheet (str): Name of the sheet to be processed in the Excel files.
            - workbook_data (dict): Contains the following keys:
                - has_headers (bool): Indicates if the Excel sheets have headers.
                - selected_column_a (str): Column name for the first signal.
                - selected_column_b (str): Column name for the second signal.
            - checkbox_IBI (bool): If True, process data as 'IBI_MS', otherwise as 'EDA'.
            - checkbox_windowed_xcorr (bool): If True, perform windowed cross-correlation, otherwise standard cross-correlation.
            - window_size (int): Size of the window for windowed cross-correlation.
            - step_size (int): Step size for windowed cross-correlation.
            - max_lag (int): Maximum lag for windowed cross-correlation.
            - checkbox_absolute_corr (bool): If True, use absolute values for windowed cross-correlation.
            - checkbox_average_windows (bool): If True, average the windows for windowed cross-correlation.
            - max_lag_sxc (int): Maximum lag for standard cross-correlation.
            - checkbox_absolute_corr_sxc (bool): If True, use absolute values for standard cross-correlation.
            - checkbox_EDA (bool): If True, indicates that EDA data is being processed.
            - include_flexibility (bool): If True, include flexibility (measured as fisher z-transformed average wcc and variance) in the analysis.
            - include_random_pair (bool): If True, include random pair analysis in the output.
    Returns:
        None
    """

    # get directory in which dyad directories are stored
    batch_input_folder = params['batch_input_folder']
    if not batch_input_folder: return

    # get output directory
    output_dir = params['output_dir']
    if not output_dir: return

    # process dyads in folder
    dyad_folders = [f for f in os.listdir(batch_input_folder) if os.path.isdir(os.path.join(batch_input_folder, f))]
    for dyad_folder in dyad_folders:
        _process_dyad(batch_input_folder, dyad_folder, output_dir, params)

    # random pair analysis
    if params['include_random_pair']:
        random_pair_analysis(params)