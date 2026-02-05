import os
import xlsx
from signal_processing import preprocess_dyad
from export import export_sxcorr_data, export_wxcorr_data
from cross_correlation import windowed_cross_correlation, standard_cross_correlation
import random
import numpy as np
from datetime import datetime
from scipy.stats import ttest_ind
from dfa import dfa_wxcorr

def _process_dyad(file_path_a, file_path_b, output_dir, params, export=True, dyad_dir=''):
    """
    Processes dyadic data from Excel files, performs cross-correlation analysis, and optionally exports the results.
    Args:
        file_path_a (str): Path to the first Excel file.
        file_path_b (str): Path to the second Excel file.
        output_dir (str): Directory where the output files will be saved.
        params (dict): Dictionary of parameters for processing and analysis.
            - 'selected_sheet' (str): Name of the sheet to be selected from the Excel files.
            - 'workbook_data' (dict): Dictionary containing workbook data parameters.
                - 'has_headers' (bool): Indicates if the workbook has headers.
                - 'selected_column_a' (str): Name of the column to be selected from the first Excel file.
                - 'selected_column_b' (str): Name of the column to be selected from the second Excel file.
            - 'checkbox_eb' (bool): Indicates if the signal type is event-based (not fixed rate).
            - 'checkbox_windowed_xcorr' (bool): Indicates if windowed cross-correlation should be performed.
            - 'window_size' (int): Size of the window for windowed cross-correlation.
            - 'step_size' (int): Step size for windowed cross-correlation.
            - 'max_lag' (int): Maximum lag for windowed cross-correlation.
            - 'checkbox_absolute_corr' (bool): Indicates if absolute values should be used for correlation.
            - 'checkbox_average_windows' (bool): Indicates if windows should be averaged.
            - 'max_lag_sxc' (int): Maximum lag for standard cross-correlation.
            - 'checkbox_absolute_corr_sxc' (bool): Indicates if absolute values should be used for standard cross-correlation.
            - 'checkbox_fr' (bool): Indicates if the signal type is fixed-rate.
        export (bool, optional): If True, the results will be exported to an Excel file. Defaults to True.
    Returns:
        dict: Correlation data resulting from the analysis.
    Raises:
        Exception: If an error occurs during processing, it will be printed.
    """
    
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
            signal_type='eb_MS' if params['checkbox_eb'] else 'fr'
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
            
            # dfa per lag (per horizontal line)
            dfa_corr_data = None
            try:
                dfa_data = dfa_wxcorr(corr_data, max_lag, order=1)
                dfa_alpha_per_lag = [{'lag': o['lag'], 'alpha': o['A'][0]} for o in dfa_data]
                dfa_corr_data = dfa_alpha_per_lag
            except ValueError as e:
                dfa_corr_data = None
                print("TODO: handle dfa update error in wxcorr update", e) # TODO

            # export
            export_params = {
                'selected_dyad_dir': dyad_dir,
                'input_file_a': file_path_a,
                'input_file_b': file_path_b,
                'checkbox_fr': params['checkbox_fr'],
                'window_size': params['window_size'],
                'max_lag': params['max_lag'],
                'step_size': params['step_size'],
                'checkbox_absolute_corr': params['checkbox_absolute_corr'],
                'checkbox_average_windows': params['checkbox_average_windows'],
                'checkbox_eb': params['checkbox_eb'],
                'signal_a': signal_a,
                'signal_b': signal_b,
                'wxcorr': corr_data,
                'dfa_alpha_per_lag_wxcorr': dfa_corr_data
            }
            
            # export / return data
            if export:
                output_file_name = f"wx_{os.path.basename(dyad_dir) if dyad_dir else datetime.now().strftime('%Y%m%d%H%M%S')}_wxcorr.xlsx"
                output_file_path = os.path.join(output_dir, output_file_name)
                export_wxcorr_data(output_file_path, export_params)
            return corr_data
        else:
            # Standard XCorr
            max_lag = params['max_lag_sxc']
            absolute_values = params['checkbox_absolute_corr_sxc']
            corr_data = standard_cross_correlation(signal_a, signal_b, max_lag=max_lag, absolute=absolute_values)
            # export
            export_params = {
                'selected_dyad_dir': dyad_dir,
                'input_file_a': file_path_a,
                'input_file_b': file_path_b,
                'checkbox_fr': params['checkbox_fr'],
                'max_lag': params['max_lag_sxc'],
                'checkbox_absolute_corr': params['checkbox_absolute_corr_sxc'],
                'checkbox_eb': params['checkbox_eb'],
                'signal_a': signal_a,
                'signal_b': signal_b,
                'sxcorr': corr_data
            }
            # export / return data
            if export:
                output_file_name = f"{os.path.basename(dyad_dir) if dyad_dir else datetime.now().strftime('%Y%m%d%H%M%S')}_sxcorr.xlsx"
                output_file_path = os.path.join(output_dir, output_file_name)
                export_sxcorr_data(output_file_path, export_params)
            return corr_data
    except Exception as e:
        print(f"! {os.path.basename(file_path_a)}, {os.path.basename(file_path_b)}: {e}")
        raise(e)

def random_pair_analysis(params, input_dir, random_pair_count=100): 
    """
    Perform analysis on random pairs and real dyad correlations.
    Args:
        params (dict): A dictionary of parameters, see batch_process function for details.
        input_dir (str): Path to the input directory containing dyad folders with Excel files.
        random_pair_count (int, optional): Number of random pairs to generate. Defaults to 100.
    Returns:
        tuple: A tuple containing:
            - t_stat (float): The t-statistic from Welch's t-test.
            - p_value (float): The p-value from Welch's t-test.
            - average_correlations_rp (list): List of average correlations for random pairs.
            - average_correlations_real (list): List of average correlations for real dyads.
    """

    # get input data
    dyad_folders = [f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f))]
    xlsx_file_paths = [os.path.join(input_dir, dyad_folder, f) 
                       for dyad_folder in dyad_folders 
                       for f in os.listdir(os.path.join(input_dir, dyad_folder)) 
                       if f.endswith('.xlsx')]
    # make random_pair_count random pairs of xlsx files
    random_pairs = []
    for _ in range(random_pair_count):
        pair = random.sample(xlsx_file_paths, 2)
        random_pairs.append(pair)

    # read correlation type
    is_windowed_corr = params['checkbox_windowed_xcorr']

    # process random pairs
    all_correlations_rp = []
    for pair in random_pairs:
        file_path_a, file_path_b = pair
        corr_data = _process_dyad(file_path_a, file_path_b, None, params, export=False)
        if not corr_data: continue
        if is_windowed_corr:
            all_correlations_rp.append([val for d in corr_data for val in d['correlations']])
        else:
            all_correlations_rp.append(corr_data['corr'])

    # calculate averages of all correlations
    average_correlations_rp = [np.mean(c) for c in all_correlations_rp]

    # process all real dyads
    all_correlations_real = []
    for dyad_folder in dyad_folders:
        dyad_path = os.path.join(input_dir, dyad_folder)
        xlsx_files = [f for f in os.listdir(dyad_path) if f.endswith('.xlsx')]
        if len(xlsx_files) >= 2:
            file_path_a = os.path.join(dyad_path, xlsx_files[0])
            file_path_b = os.path.join(dyad_path, xlsx_files[1])
            corr_data = _process_dyad(
                file_path_a=file_path_a, 
                file_path_b=file_path_b, 
                output_dir=None, 
                params=params, 
                export=False
            )
            if not corr_data: continue
            if is_windowed_corr:
                all_correlations_real.append([val for d in corr_data for val in d['correlations']])
            else:
                all_correlations_real.append(corr_data['corr'])

    # calculate averages of all real dyad correlations
    average_correlations_real = [np.mean(c) for c in all_correlations_real]

    # run Welch's t-test
    t_stat, p_value = ttest_ind(average_correlations_rp, average_correlations_real, equal_var=False)

    return t_stat, p_value, average_correlations_rp, average_correlations_real


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
            - checkbox_eb (bool): If True, process data as 'eb_MS', otherwise as 'fr'.
            - checkbox_windowed_xcorr (bool): If True, perform windowed cross-correlation, otherwise standard cross-correlation.
            - window_size (int): Size of the window for windowed cross-correlation.
            - step_size (int): Step size for windowed cross-correlation.
            - max_lag (int): Maximum lag for windowed cross-correlation.
            - checkbox_absolute_corr (bool): If True, use absolute values for windowed cross-correlation.
            - checkbox_average_windows (bool): If True, average the windows for windowed cross-correlation.
            - max_lag_sxc (int): Maximum lag for standard cross-correlation.
            - checkbox_absolute_corr_sxc (bool): If True, use absolute values for standard cross-correlation.
            - checkbox_fr (bool): If True, indicates that fr data is being processed.
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
        dyad_path = os.path.join(batch_input_folder, dyad_folder)
        xlsx_files = [f for f in os.listdir(dyad_path) if f.endswith('.xlsx')]
        if len(xlsx_files) >= 2:
            file_path_a = os.path.join(dyad_path, xlsx_files[0])
            file_path_b = os.path.join(dyad_path, xlsx_files[1])
            _process_dyad(file_path_a, file_path_b, output_dir, params, dyad_dir=dyad_path, export=True)