import os
import xlsx
import utils
import customtkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from plot import plot_init, update_sxcorr_plots, update_wxcorr_plots, update_preproc_plots
from cross_correlation import windowed_cross_correlation, standard_cross_correlation
from dfa import dfa, dfa_wxcorr, dfa_wxcorr_window_averages
from signal_processing import preprocess_dyad
from batch_processing import batch_process, random_pair_analysis
from export import export_sxcorr_data, export_wxcorr_data, export_random_pair_data

# ------------------
# APP INITIALIZATION
# ------------------

#init theme
tk.set_appearance_mode("Light") # options 'System', 'Light', 'Dark'
tk.set_default_color_theme("dark-blue") # options 'blue', 'green', 'dark-blue'

# init window
app = tk.CTk()  
app.title("wx")

# Get the screen width and height
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
screen_dpi = app.winfo_fpixels('1i')

# Window Scaling
RETINA = screen_dpi < 75
app_width = min(2000, screen_width)
app_height = min(1200, screen_height)
app.geometry(f"{app_width}x{app_height}")
scaling_factor = 1 if RETINA else 1.5
app.tk.call('tk', 'scaling', scaling_factor)


# ----------------------
# DEFAULTS / INIT VALUES
# ----------------------

USE_MY_PARAMS = True

INIT_WINDOW_SIZE = 250 if USE_MY_PARAMS else 150                              # 150 := 30s for 5hz signals
INIT_MAX_LAG = 25 if USE_MY_PARAMS else 15                                   # 15 := 3s
INIT_STEP_SIZE = 5 if USE_MY_PARAMS else 15                                 # 15 := 3s; =max_lag
INIT_MAX_LAG_SXC = 150

# ---------------------
# GLOBAL STATE & EVENTS
# ---------------------

# input validation trackers
val_CORRELATION_SETTINGS_VALID = tk.BooleanVar(value=True)
val_CORRELATION_SETTINGS_VALID_SXC = tk.BooleanVar(value=True)
val_WINDOW_SIZE_VALID = tk.BooleanVar(value=True)
val_STEP_SIZE_VALID = tk.BooleanVar(value=True)
val_MAX_LAG_VALID = tk.BooleanVar(value=True)
val_MAX_LAG_VALID_SXC = tk.BooleanVar(value=True)
val_INPUT_DATA_VALID = tk.BooleanVar(value=False)
val_LAG_FILTER_VALID = tk.BooleanVar(value=True)

# GUI state
val_CURRENT_TAB = tk.StringVar(value="Input Data")

# update count: changes trigger rerendering
val_UPDATE_COUNT = tk.IntVar(value=0)

# main event callback: causes rerendering
def PARAMS_CHANGED():
    val_UPDATE_COUNT.set(val_UPDATE_COUNT.get() + 1)

# ----------------
# INPUT VALIDATION
# ----------------

def on_validate_numeric_input(input):
    if input == "" or input.isdigit():
        return True
    return False
validate_numeric_input = app.register(on_validate_numeric_input)

# entry validation (windowed_xcorr)
def check_window_size():
    # window size must be at least 1
    data_length = val_data_length.get()
    window_size_is_valid = val_window_size.get() >= 1 and val_window_size.get() <= data_length
    val_WINDOW_SIZE_VALID.set(window_size_is_valid)
    return window_size_is_valid

def check_step_size():
    # step size must be at least 1 and at most window size
    window_size_is_valid = val_WINDOW_SIZE_VALID.get()
    window_size = val_window_size.get()
    step_size = val_step_size.get()
    step_size_is_valid = step_size >= 1 and (not window_size_is_valid or step_size <= window_size)
    val_STEP_SIZE_VALID.set(step_size_is_valid)
    return step_size_is_valid

def check_max_lag():
    # max lag can be at most half the window size and more than 0
    window_size_is_valid = val_WINDOW_SIZE_VALID.get()
    max_lag_is_valid = val_max_lag.get() > 0 and (not window_size_is_valid or (val_max_lag.get() <= val_window_size.get() // 2))
    val_MAX_LAG_VALID.set(max_lag_is_valid)
    return max_lag_is_valid

def check_lag_filter_in_range():
    lf_min = val_lag_filter_min.get()
    lf_max = val_lag_filter_max.get()
    max_lag = val_max_lag.get()
    return (lf_min >= -max_lag) and (lf_min <= max_lag) and (lf_max >= -max_lag) and (lf_max <= max_lag)

def check_lag_filter_sorted():
    lf_min = val_lag_filter_min.get()
    lf_max = val_lag_filter_max.get()
    return lf_max > lf_min

def check_lag_filter_exists():
    lf_min = val_lag_filter_min.get()
    lf_max = val_lag_filter_max.get()
    is_none = lf_min is None or lf_max is None
    is_empty = lf_min == '' or lf_min == ' ' or lf_max ==  '' or lf_max == ' '
    return not is_none and not is_empty

def check_lag_filter():
    # filter is valid if disabled
    if not checkbox_lag_filter.get(): 
        return True
    # otherwise it should be sorted, existing, in range
    lag_filter_is_valid = check_lag_filter_exists() and check_lag_filter_sorted() and check_lag_filter_in_range()
    # update state & return
    val_LAG_FILTER_VALID.set(lag_filter_is_valid)
    return lag_filter_is_valid

def check_wx_correlation_settings():
    window_size_is_valid = check_window_size()
    step_size_is_valid = check_step_size()
    max_lag_is_valid = check_max_lag()
    lag_filter_is_valid = check_lag_filter()
    correlation_settings_valid = window_size_is_valid and step_size_is_valid and max_lag_is_valid and lag_filter_is_valid
    val_CORRELATION_SETTINGS_VALID.set(correlation_settings_valid)
    PARAMS_CHANGED()
    return correlation_settings_valid

# entry validation (standard xcorr)
def check_max_lag_sxc():
    # max lag range [0, data_length - 1]
    data_length = val_data_length.get()
    max_lag = val_max_lag_sxc.get()
    max_lag_is_valid = max_lag >= 0 and  max_lag < data_length
    val_MAX_LAG_VALID_SXC.set(max_lag_is_valid)
    return max_lag_is_valid

def check_sx_correlation_settings():
    max_lag_is_valid = check_max_lag_sxc()
    correlation_settings_valid = max_lag_is_valid
    val_CORRELATION_SETTINGS_VALID_SXC.set(correlation_settings_valid)
    PARAMS_CHANGED()
    return correlation_settings_valid

# ------------------------------
# DATA STORAGE & STATE VARIABLES
# ------------------------------

# set up app state variables 
val_checkbox_absolute_corr = tk.BooleanVar(value=False)
val_checkbox_absolute_corr_sxc = tk.BooleanVar(value=False)
val_checkbox_eb = tk.BooleanVar(value=True)
val_checkbox_fr = tk.BooleanVar(value=False)
val_checkbox_windowed_xcorr = tk.BooleanVar(value=True)
val_window_size_input = tk.StringVar(value=INIT_WINDOW_SIZE)
val_step_size_input = tk.StringVar(value=INIT_STEP_SIZE)
val_max_lag_input = tk.StringVar(value=INIT_MAX_LAG) 
val_max_lag_input_sxc = tk.StringVar(value=INIT_MAX_LAG_SXC)   
val_window_size = tk.IntVar(value=INIT_WINDOW_SIZE)
val_step_size = tk.IntVar(value=INIT_STEP_SIZE)
val_max_lag = tk.IntVar(value=INIT_MAX_LAG)
val_max_lag_sxc = tk.IntVar(value=INIT_MAX_LAG_SXC)
val_checkbox_lag_filter = tk.BooleanVar(value=False)
val_lag_filter_min = tk.IntVar(value=-INIT_MAX_LAG)
val_lag_filter_max = tk.IntVar(value=INIT_MAX_LAG)
val_lag_filter_min_input = tk.StringVar(value=str(-INIT_MAX_LAG))
val_lag_filter_max_input = tk.StringVar(value=str(INIT_MAX_LAG))
val_checkbox_average_windows = tk.BooleanVar(value=False)
val_checkbox_show_sigmoid_correlations = tk.BooleanVar(value=False)
val_checkbox_standardise = tk.BooleanVar(value=False)
val_selected_dyad_dir = tk.StringVar(value='')
val_selected_file_a = tk.StringVar(value='')
val_selected_file_b = tk.StringVar(value='')
val_data_length = tk.IntVar(value=0)
val_selected_sheet = tk.StringVar(value='- None -')
val_selected_column_a = tk.StringVar(value='- None -')
val_selected_column_b = tk.StringVar(value='- None -')
val_checkbox_data_has_headers = tk.BooleanVar(value=True)
val_batch_input_folder = tk.StringVar(value='')
val_batch_output_folder = tk.StringVar(value='')
val_batch_processing_is_ready = tk.BooleanVar(value=False)
val_rp_n_input = tk.StringVar(value="100")  
val_rp_n = tk.IntVar(value=100)
val_random_pair_input_folder = tk.StringVar(value='')
val_random_pair_output_file = tk.StringVar(value='')
val_random_pair_is_ready = tk.BooleanVar(value=False)

# set up data containers
dat_plot_data = {
    'fig': plot_init(dpi=screen_dpi, screen_width=screen_width, screen_height=screen_height, is_retina=RETINA)
}
dat_workbook_data = {
    'workbook_a': None,
    'workbook_b': None,
    'sheet_names': [],
    'columns_a': {},
    'columns_b': {},
    'column_names_a': [],
    'column_names_b': [],
    'selected_column_a': None,
    'selected_column_b': None,
    'has_headers': True
}
dat_physiological_data = {
    'signal_a': [],
    'signal_b': [],
    'signal_a_std': [],
    'signal_b_std': [],
    'raw_signal_a': [],
    'raw_signal_b': []
}
dat_correlation_data = {
    'wxcorr': [],
    'sxcorr': [],
    'dfa_alpha_sxcorr': None,
    'dfa_alpha_per_lag_wxcorr': None,
    'dfa_alpha_window_averages_wxcorr': None,
}

# ---------
# CALLBACKS
# ---------

# gui state callbacks
def on_tab_change():
    selected_tab = group_params_tabview.get()
    val_CURRENT_TAB.set(selected_tab)
    PARAMS_CHANGED()

# entry callbacks windowed xcorr
def on_window_size_input_change(name, index, mode):
    new_str_val = val_window_size_input.get()
    if new_str_val == '':
        val_window_size.set(0)
    else:
        new_val = int(new_str_val)
        val_window_size.set(new_val)
    check_wx_correlation_settings()
val_window_size_input.trace_add("write", on_window_size_input_change)

def on_step_size_input_change(name, index, mode):
    new_str_val = val_step_size_input.get()
    if new_str_val == '':
        val_step_size.set(0)
    else:
        new_val = int(new_str_val)
        val_step_size.set(new_val)
    check_wx_correlation_settings()
val_step_size_input.trace_add("write", on_step_size_input_change)

def on_max_lag_input_change(name, index, mode):
    new_str_val = val_max_lag_input.get()
    if new_str_val == '':
        val_max_lag.set(0)
    else:
        new_val = int(new_str_val)
        val_max_lag.set(new_val)
    check_wx_correlation_settings()
val_max_lag_input.trace_add("write", on_max_lag_input_change)

# entry callbacks standard xcorr
def on_max_lag_input_change_sxc(name, index, mode):
    new_str_val = val_max_lag_input_sxc.get()
    if new_str_val == '':
        val_max_lag_sxc.set(0)
    else:
        new_val = int(new_str_val)
        val_max_lag_sxc.set(new_val)
    check_sx_correlation_settings()
val_max_lag_input_sxc.trace_add("write", on_max_lag_input_change_sxc)

# lag filter callbacks
def on_min_lag_input_change(name, index, mode):
    new_str_val = val_lag_filter_min_input.get()
    if new_str_val == '' or new_str_val == '-':
        val_lag_filter_min.set(0)
        val_lag_filter_min_input.set(0)
    else:
        val_lag_filter_min.set(int(new_str_val))
    check_wx_correlation_settings()
val_lag_filter_min_input.trace_add("write", on_min_lag_input_change)

def on_max_lag_filter_input_change(name, index, mode):
    new_str_val = val_lag_filter_max_input.get()
    if new_str_val == '':
        val_lag_filter_max.set(0)
        val_lag_filter_max_input.set(0)
    else:
        val_lag_filter_max.set(int(new_str_val))
    check_wx_correlation_settings()
val_lag_filter_max_input.trace_add("write", on_max_lag_filter_input_change)

def on_max_lag_change_update_filter(*args):
    new_max_lag = val_max_lag.get()
    val_lag_filter_min.set(-new_max_lag)
    val_lag_filter_max.set(new_max_lag)
    val_lag_filter_min_input.set(str(-new_max_lag))
    val_lag_filter_max_input.set(str(new_max_lag))
    check_wx_correlation_settings()
val_max_lag.trace_add('write', on_max_lag_change_update_filter)

# checkbox callbacks
def on_absolute_corr_change():
    new_val = val_checkbox_absolute_corr.get()
    PARAMS_CHANGED()

def on_absolute_corr_change_sxc():
    new_val = val_checkbox_absolute_corr_sxc.get()
    PARAMS_CHANGED()

def on_is_eb_change(): # eb (event-based) vs fr (fixed-rate)
    new_val = val_checkbox_eb.get()
    val_checkbox_fr.set(not new_val)
    preprocess_data()
    clear_correlation_data()
    PARAMS_CHANGED()

def on_is_fr_change(): # eb (event-based) vs fr (fixed-rate)
    new_val = val_checkbox_fr.get()
    val_checkbox_eb.set(not new_val)
    preprocess_data()
    clear_correlation_data()
    PARAMS_CHANGED()

def on_standardise_change():
    new_val = val_checkbox_standardise.get()
    clear_correlation_data()
    PARAMS_CHANGED()

def on_show_sigmoid_correlations_change():
    new_val = val_checkbox_show_sigmoid_correlations.get()
    PARAMS_CHANGED()

def on_windowed_xcorr_change():
    new_val = val_checkbox_windowed_xcorr.get()
    PARAMS_CHANGED()    

def on_average_windows_change():
    new_val = val_checkbox_average_windows.get()
    PARAMS_CHANGED()

def on_lag_filter_checkbox_change():
    new_val = val_checkbox_lag_filter.get()
    check_wx_correlation_settings()

# dropdown callbacks
def on_dropdown_select_sheet_change(value):
    selected_sheet = val_selected_sheet.get()
    update_column_names()
    preprocess_data()
    clear_correlation_data()
    PARAMS_CHANGED()  

def on_dropdown_select_column_a_change(value):
    selected_col_a = val_selected_column_a.get()
    # update data
    preprocess_data()
    clear_correlation_data()
    PARAMS_CHANGED()  

def on_dropdown_select_column_b_change(value):
    selected_col_b = val_selected_column_b.get()
    # update data
    preprocess_data()
    clear_correlation_data()
    PARAMS_CHANGED()  

def on_change_data_has_headers(*args):
    dat_workbook_data["has_headers"] = val_checkbox_data_has_headers.get()
    update_column_names()
    preprocess_data()
    clear_correlation_data()
    PARAMS_CHANGED()
val_checkbox_data_has_headers.trace_add('write', on_change_data_has_headers)

# dropdown update utility
def update_dropdown_options(dropdown, dropdown_state_var, new_options):
    dropdown.configure(values=new_options)  
    dropdown_state_var.set(new_options[0])  

# random pair N input change
def on_rp_n_input_change(name, index, mode):
    new_str_val = val_rp_n_input.get()
    if new_str_val == '':
        val_rp_n.set(0)
    else:
        new_val = int(new_str_val)
        if new_val < 0: new_val = 0
        val_rp_n.set(new_val)

# ---------------
# EXPORT HANDLERS
# ---------------
def _export_wxcorr_data(file_path):
    params = {
        'selected_dyad_dir': val_selected_dyad_dir.get(),
        'input_file_a': val_selected_file_a.get(),
        'input_file_b': val_selected_file_b.get(),
        'checkbox_EDA': val_checkbox_fr.get(),
        'window_size': val_window_size.get(),
        'max_lag': val_max_lag.get(),
        'step_size': val_step_size.get(),
        'checkbox_lag_filter': val_checkbox_lag_filter.get(),
        'lag_filter_min': val_lag_filter_min.get(),
        'lag_filter_max': val_lag_filter_max.get(),
        'checkbox_absolute_corr': val_checkbox_absolute_corr.get(),
        'checkbox_average_windows': val_checkbox_average_windows.get(),
        'checkbox_eb': val_checkbox_eb.get(),
        'checkbox_fr': val_checkbox_fr.get(),
        'signal_a': dat_physiological_data["signal_a"],
        'signal_b': dat_physiological_data["signal_b"],
        'signal_a_std': dat_physiological_data["signal_a_std"],
        'signal_b_std': dat_physiological_data["signal_b_std"],
        'is_standardised': val_checkbox_standardise.get(),
        'wxcorr': dat_correlation_data["wxcorr"],
        'dfa_alpha_window_averages_wxcorr': dat_correlation_data['dfa_alpha_window_averages_wxcorr']
    }
    export_wxcorr_data(file_path, params)

def _export_sxcorr_data(file_path):
    params = {
        'selected_dyad_dir': val_selected_dyad_dir.get(),
        'input_file_a': val_selected_file_a.get(),
        'input_file_b': val_selected_file_b.get(),
        'checkbox_fr': val_checkbox_fr.get(),
        'checkbox_eb': val_checkbox_eb.get(),
        'max_lag': val_max_lag_sxc.get(),
        'checkbox_absolute_corr': val_checkbox_absolute_corr_sxc.get(),
        'checkbox_eb': val_checkbox_eb.get(),
        'signal_a': dat_physiological_data["signal_a"],
        'signal_b': dat_physiological_data["signal_b"],
        'signal_a_std': dat_physiological_data["signal_a_std"],
        'signal_b_std': dat_physiological_data["signal_b_std"],
        'is_standardised': val_checkbox_standardise.get(),
        'sxcorr': dat_correlation_data["sxcorr"],
        'dfa_alpha': dat_correlation_data['dfa_alpha_sxcorr'],
    }
    export_sxcorr_data(file_path, params)

# export XLSX data
def export_data():
    # create initial output file name
    selected_dir = val_selected_dyad_dir.get()
    filename_init = f"wx_data_{os.path.basename(selected_dir)}" if selected_dir else "wx_data"
    # get filename using file picker
    file_path = filedialog.asksaveasfilename(
        title="Save As",
        defaultextension=".xlsx",  
        initialfile=filename_init,
        filetypes=(
            ("XLSX files", "*.xlsx"),
        )
    )
    if not file_path: return
    # call specialised export function
    is_windowed_xcorr = val_checkbox_windowed_xcorr.get()
    if is_windowed_xcorr:
        _export_wxcorr_data(file_path)
    else:
        _export_sxcorr_data(file_path)

# export plots as PNG
def export_plot():
    # get fig data
    fig = dat_plot_data["fig"]
    if not fig: return
    
    # create initial output file name
    selected_dir = val_selected_dyad_dir.get()
    filename_init = f"wx_plot_{os.path.basename(selected_dir)}" if selected_dir else "wx_plot"

    # get filename using file picker
    file_path = filedialog.asksaveasfilename(
        title="Save As",
        defaultextension=".png",  
        initialfile=filename_init,
        filetypes=(
            ("PNG files", "*.png"),
        )
    )
    if not file_path: return
    
    # export plot
    fig.savefig(file_path, dpi=300, format='png')


# ------------------
# XLSX DATA HANDLING
# ------------------

def read_xlsx_files():
    # read data from selected files into workbook objects
    file_path_a = val_selected_file_a.get()
    file_path_b = val_selected_file_b.get()
    dat_workbook_data["workbook_a"] = xlsx.read_xlsx(file_path_a)
    dat_workbook_data["workbook_b"] = xlsx.read_xlsx(file_path_b)

def update_sheet_names():
    # get common sheet names
    if not dat_workbook_data["workbook_a"] or not dat_workbook_data["workbook_b"]: return
    sheet_names_a = xlsx.get_sheet_names(dat_workbook_data["workbook_a"])
    sheet_names_b = xlsx.get_sheet_names(dat_workbook_data["workbook_b"])
    dat_workbook_data["sheet_names"] = list(set(sheet_names_a) & set(sheet_names_b))

    # update dropdown options
    update_dropdown_options(dropdown_select_sheet, val_selected_sheet, dat_workbook_data["sheet_names"])

def update_column_names():
    if not val_selected_sheet.get() or val_selected_sheet.get() == '- None -':
        return

    # get column names
    dat_workbook_data["column_names_a"] = list(xlsx.get_columns(dat_workbook_data["workbook_a"], val_selected_sheet.get(), headers=dat_workbook_data["has_headers"]).keys())
    dat_workbook_data["column_names_b"] = list(xlsx.get_columns(dat_workbook_data["workbook_b"], val_selected_sheet.get(), headers=dat_workbook_data["has_headers"]).keys())

    # update dropdown options
    update_dropdown_options(dropdown_select_column_a, val_selected_column_a, dat_workbook_data["column_names_a"])
    update_dropdown_options(dropdown_select_column_b, val_selected_column_b, dat_workbook_data["column_names_b"])
    
    # init selected column names
    dat_workbook_data["selected_column_a"] = dat_workbook_data["column_names_a"][0]
    dat_workbook_data["selected_column_b"] = dat_workbook_data["column_names_b"][0]

    # create columns object from selected sheet
    dat_workbook_data["columns_a"] = xlsx.get_columns(dat_workbook_data["workbook_a"], val_selected_sheet.get(), headers=dat_workbook_data["has_headers"])
    dat_workbook_data["columns_b"] = xlsx.get_columns(dat_workbook_data["workbook_b"], val_selected_sheet.get(), headers=dat_workbook_data["has_headers"])

# ---------------------
# DATA [PRE-]PROCESSING
# ---------------------

def preprocess_data():
    if not val_selected_sheet.get() or val_selected_sheet.get() == '- None -':
        val_INPUT_DATA_VALID.set(False)
        return
    if not val_selected_column_a.get() or val_selected_column_a.get() == '- None -':
        val_INPUT_DATA_VALID.set(False)
        return
    if not val_selected_column_b.get() or val_selected_column_b.get() == '- None -':
        val_INPUT_DATA_VALID.set(False)
        return
    # store selected columns as raw data
    dat_physiological_data["raw_signal_a"] = dat_workbook_data["columns_a"][dat_workbook_data["selected_column_a"]]
    dat_physiological_data["raw_signal_b"] = dat_workbook_data["columns_b"][dat_workbook_data["selected_column_b"]]

    # validate signals before processing
    if not (utils.is_numeric_array(dat_physiological_data["raw_signal_a"]) and utils.is_numeric_array(dat_physiological_data["raw_signal_b"])):
        val_INPUT_DATA_VALID.set(False)
        return

    # process data
    try:
        # pre process dyad: remove first and last sample & resample (IBI only), align signals
        signal_a, signal_b, signal_a_std, signal_b_std \
            = preprocess_dyad(
            dat_physiological_data["raw_signal_a"],
            dat_physiological_data["raw_signal_b"],
            signal_type='event-based' if val_checkbox_eb.get() else 'fixed-rate'
        )

        # store physiological data
        dat_physiological_data["signal_a"] = signal_a
        dat_physiological_data["signal_b"] = signal_b
        dat_physiological_data["signal_a_std"] = signal_a_std
        dat_physiological_data["signal_b_std"] = signal_b_std

        # update val data length
        val_data_length.set(len(signal_a))
        #set validation state
        val_INPUT_DATA_VALID.set(True)

    except Exception as e:
        print(f"Data is invalid [{e}]")
        # if data cant be processed: clear plots and physiological data
        # reset physiological data
        dat_physiological_data["signal_a"] = []
        dat_physiological_data["signal_b"] = []
        dat_physiological_data["signal_a_std"] = []
        dat_physiological_data["signal_b_std"] = []
        dat_physiological_data["raw_signal_a"] = []
        dat_physiological_data["raw_signal_b"] = []
        # reset plot
        dat_plot_data['fig'] = plot_init(dpi=screen_dpi, screen_width=screen_width, screen_height=screen_height, is_retina=RETINA)
        # set validation state
        val_INPUT_DATA_VALID.set(False)

# -------------------------
# MAIN DATA LOADING ROUTINE
# -------------------------

def load_xlsx_data():
    read_xlsx_files()
    update_sheet_names()
    update_column_names()
    preprocess_data()
    clear_correlation_data()


# ------------
# FILE PICKERS
# ------------

def open_dir_picker():
    dir_path = filedialog.askdirectory(
        title="Select a directory"
    )
    if not dir_path: 
        return
    
    # set selected directory and find xlsx files
    val_selected_dyad_dir.set(dir_path)

    # Get  xlsx files in the selected directory
    xlsx_files = [f for f in os.listdir(dir_path) if f.endswith('.xlsx')]
    if len(xlsx_files) < 2:
        return
    val_selected_file_a.set(os.path.join(dir_path, xlsx_files[0]))
    val_selected_file_b.set(os.path.join(dir_path, xlsx_files[1]))

    # process data from xlsx files
    load_xlsx_data()
    PARAMS_CHANGED()    

def open_batch_output_dir_picker():
    dir_path = filedialog.askdirectory(
        title="Select Output Directory"
    )
    if not dir_path:
        return
    val_batch_output_folder.set(dir_path)

def open_batch_input_folder():
    dir_path = filedialog.askdirectory(
        title="Select Batch Input Folder"
    )
    if not dir_path:
        return
    val_batch_input_folder.set(dir_path)

def open_random_pair_input_dir_picker():
    dir_path = filedialog.askdirectory(title="Select Input Folder")
    if not dir_path:
        return
    val_random_pair_input_folder.set(dir_path)

def open_random_pair_output_file_picker():
    file_path = filedialog.asksaveasfilename(
        title="Save As",
        defaultextension=".xlsx",
        filetypes=(("XLSX files", "*.xlsx"),)
    )
    if not file_path:
        return
    val_random_pair_output_file.set(file_path)

# ----------------
# BATCH PROCESSING
# ----------------

# dynamically determine ready state
def batch_processing_is_ready(*args):
    data_is_valid = val_INPUT_DATA_VALID.get() and val_CORRELATION_SETTINGS_VALID.get() and val_CORRELATION_SETTINGS_VALID_SXC.get()
    io_is_ready = val_batch_input_folder.get() != '' and val_batch_output_folder.get() != ''
    ready = data_is_valid and io_is_ready
    val_batch_processing_is_ready.set(ready)
val_INPUT_DATA_VALID.trace_add('write', batch_processing_is_ready)
val_CORRELATION_SETTINGS_VALID.trace_add('write', batch_processing_is_ready)
val_CORRELATION_SETTINGS_VALID_SXC.trace_add('write', batch_processing_is_ready)
val_batch_input_folder.trace_add('write', batch_processing_is_ready)
val_batch_output_folder.trace_add('write', batch_processing_is_ready)

# batch process data forwarding
def run_batch_process():
    # process batch
    params = {
        'batch_input_folder': val_batch_input_folder.get(),
        'output_dir': val_batch_output_folder.get(),
        'selected_sheet': val_selected_sheet.get(), 
        'workbook_data': dat_workbook_data,
        'checkbox_windowed_xcorr': val_checkbox_windowed_xcorr.get(),
        'window_size': val_window_size.get(),
        'step_size': val_step_size.get(),
        'max_lag': val_max_lag.get(),
        'max_lag_sxc': val_max_lag_sxc.get(),
        'standardised_signals': val_checkbox_standardise.get(),
        'checkbox_absolute_corr': val_checkbox_absolute_corr.get(),
        'checkbox_absolute_corr_sxc': val_checkbox_absolute_corr_sxc.get(),
        'checkbox_average_windows': val_checkbox_average_windows.get(),
        'sigmoid_correlations': val_checkbox_show_sigmoid_correlations.get(),
        'checkbox_eb': val_checkbox_eb.get(),
        'checkbox_fr': val_checkbox_fr.get(),
        'use_lag_filter': checkbox_lag_filter.get(),
        'lag_filter_min': val_lag_filter_min.get(),
        'lag_filter_max': val_lag_filter_max.get()
    }
    batch_process(params)

def handle_run_batch_button():
    val_batch_processing_is_ready.set(False)
    run_batch_process()
    val_batch_processing_is_ready.set(True)

# --------------------
# RANDOM PAIR ANALYSIS
# --------------------

# dynamically determine ready state
def random_pair_is_ready(*args):
    data_is_valid = val_INPUT_DATA_VALID.get() and val_CORRELATION_SETTINGS_VALID.get() and val_CORRELATION_SETTINGS_VALID_SXC.get()
    io_is_ready = val_random_pair_input_folder.get() != '' and val_random_pair_output_file.get() != ''
    ready = data_is_valid and io_is_ready
    val_random_pair_is_ready.set(ready)
val_INPUT_DATA_VALID.trace_add('write', random_pair_is_ready)
val_CORRELATION_SETTINGS_VALID.trace_add('write', random_pair_is_ready)
val_CORRELATION_SETTINGS_VALID_SXC.trace_add('write', random_pair_is_ready)
val_random_pair_input_folder.trace_add('write', random_pair_is_ready)
val_random_pair_output_file.trace_add('write', random_pair_is_ready)

# batch process data forwarding
def run_random_pair():
    params = {
        'batch_input_folder': val_batch_input_folder.get(),
        'output_dir': val_batch_output_folder.get(),
        'selected_sheet': val_selected_sheet.get(), 
        'workbook_data': dat_workbook_data,
        'checkbox_windowed_xcorr': val_checkbox_windowed_xcorr.get(),
        'window_size': val_window_size.get(),
        'step_size': val_step_size.get(),
        'max_lag': val_max_lag.get(),
        'max_lag_sxc': val_max_lag_sxc.get(),
        'checkbox_absolute_corr': val_checkbox_absolute_corr.get(),
        'sigmoid_correlations': val_checkbox_show_sigmoid_correlations.get(),
        'checkbox_absolute_corr_sxc': val_checkbox_absolute_corr_sxc.get(),
        'checkbox_average_windows': val_checkbox_average_windows.get(),
        'checkbox_eb': val_checkbox_eb.get(),
        'checkbox_fr': val_checkbox_fr.get(),
        'standardised_signals': val_checkbox_standardise.get(),
        'use_lag_filter': checkbox_lag_filter.get(),
        'lag_filter_min': val_lag_filter_min.get(),
        'lag_filter_max': val_lag_filter_max.get()
    }

    # run random pair analysis
    t_stat, p_value, avg_corr_rp, avg_corr_real = random_pair_analysis(
        params=params,
        random_pair_count=val_rp_n.get(),
        input_dir=val_random_pair_input_folder.get(),
    )

    # export data
    output_file = val_random_pair_output_file.get()
    export_random_pair_data(
        file_path=output_file,
        params=params,
        input_dir=val_random_pair_input_folder.get(),
        t_stat=t_stat,
        p_value=p_value,
        avg_corr_rp=avg_corr_rp,
        avg_corr_real=avg_corr_real,
    )

def handle_run_random_pair_button():
    val_random_pair_is_ready.set(False)
    run_random_pair()
    val_random_pair_is_ready.set(True)

# ---------------
# MAIN APP LAYOUT
# ---------------
# main grid
group_main = tk.CTkScrollableFrame(app, width=screen_width, height=screen_height)
group_main.pack(pady=10, padx=20)
# plot group
group_plot = tk.CTkFrame(group_main)
group_plot.grid(row=0, column=0, pady=10, padx=0, sticky='n')
# parameter group
group_params_tabview = tk.CTkTabview(group_main)
group_params_tabview.grid(row=0, column=1, padx=10, pady=20, sticky='n')


# -------------------
# GUI PARAMETER GROUP
# -------------------

# Add tabs
tab_input_data = group_params_tabview.add("Input Data")
tab_correlation = group_params_tabview.add("Correlation")
tab_export_batch = group_params_tabview.add("Export & Batch")
group_params_tabview.configure(command=on_tab_change)

# INPUT DATA & Preprocessing
subgroup_input_data = tk.CTkFrame(tab_input_data)
subgroup_input_data.grid(row=0, column=0, sticky='ew', columnspan=2, padx=0, pady=0)
# subgroup content
label_input_data = tk.CTkLabel(subgroup_input_data, text="Input Data", font=("Arial", 20, "bold"))
label_input_data.grid(row=0, column=0, columnspan=2, pady=20, padx=10, sticky='w')
button_file_picker = tk.CTkButton(subgroup_input_data, text="Choose Dyad Folder", command=open_dir_picker)
button_file_picker.grid(row=1, column=0, sticky="w", padx=10, pady=5)
label_dir_picker = tk.CTkLabel(subgroup_input_data, text="No folder selected.", font=("Arial", 14, "bold"))
label_dir_picker.grid(row=2, column=0, sticky="w", padx=10, pady=5)
label_select_sheet = tk.CTkLabel(subgroup_input_data, text="Select Sheet", font=("Arial", 14, "bold"))
label_select_sheet.grid(row=3, column=0, sticky="w", padx=10, pady=5)
dropdown_select_sheet = tk.CTkComboBox(subgroup_input_data, values=['- None -'], command=on_dropdown_select_sheet_change, variable=val_selected_sheet)
dropdown_select_sheet.grid(row=4, column=0, sticky="w", padx=10, pady=5)
checkbox_data_has_headers = tk.CTkCheckBox(subgroup_input_data, text='columns have headers', variable=val_checkbox_data_has_headers)
checkbox_data_has_headers.grid(row=5, column=0, sticky="w", padx=10, pady=5)
label_select_column_a = tk.CTkLabel(subgroup_input_data, text=f"Select Column A", font=("Arial", 14, "bold"))
label_select_column_a.grid(row=6, column=0, sticky="w", padx=10, pady=5)
dropdown_select_column_a = tk.CTkComboBox(subgroup_input_data, values=['- None -'], command=on_dropdown_select_column_a_change, variable=val_selected_column_a)
dropdown_select_column_a.grid(row=7, column=0, sticky="w", padx=10, pady=5)
label_select_column_b = tk.CTkLabel(subgroup_input_data, text=f"Select Column B", font=("Arial", 14, "bold"))
label_select_column_b.grid(row=8, column=0, sticky="w", padx=10, pady=5)
dropdown_select_column_b = tk.CTkComboBox(subgroup_input_data, values=['- None -'], command=on_dropdown_select_column_b_change, variable=val_selected_column_b)
dropdown_select_column_b.grid(row=9, column=0, sticky="w", padx=10, pady=5)
error_label_input_data = tk.CTkLabel(subgroup_input_data, text='Data is invalid.', text_color='red') # initially hidden

subgroup_data_type = tk.CTkFrame(tab_input_data)
subgroup_data_type.grid(row=1, column=0, sticky='ew', columnspan=2, padx=0, pady=0)
# subgroup content
label_data_type = tk.CTkLabel(subgroup_data_type, text="Pre-Process", font=("Arial", 20, "bold"))
label_data_type.grid(row=0, column=0, columnspan=2, pady=20, padx=10, sticky='w')
checkbox_is_eb_data = tk.CTkCheckBox(subgroup_data_type, text='event-based', variable=val_checkbox_eb, command=on_is_eb_change)
checkbox_is_eb_data.grid(row=4, column=0, sticky="w", padx=10, pady=5)
checkbox_is_fr_data = tk.CTkCheckBox(subgroup_data_type, text='fixed-rate', variable=val_checkbox_fr, command=on_is_fr_change)
checkbox_is_fr_data.grid(row=4, column=1, sticky="w", padx=10, pady=5)
label_select_data_type = tk.CTkLabel(subgroup_data_type, text=f"Event-based data will be resampled to 5hz.")
label_select_data_type.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=5)
checkbox_standardise = tk.CTkCheckBox(subgroup_data_type, text='standardise', variable=val_checkbox_standardise, command=on_standardise_change)
checkbox_standardise.grid(row=8, column=0, sticky="w", padx=10, pady=5)
label_standardise = tk.CTkLabel(subgroup_data_type, text=f"Scales to zero mean, unit variance.")
label_standardise.grid(row=9, column=0, columnspan=2, sticky="w", padx=10, pady=5)

# CORRELATION & VISUALISATION
subgroup_corr_settings = tk.CTkFrame(tab_correlation)
subgroup_corr_settings.grid(row=0, column=0, sticky='ew', columnspan=2, padx=0, pady=0)
# subgroup content
label_corr_settings = tk.CTkLabel(subgroup_corr_settings, text="Correlation Settings", font=("Arial", 20, "bold"))
label_corr_settings.grid(row=0, column=0, columnspan=2, pady=20, padx=10, sticky='w')
checkbox_windowed_xcorr = tk.CTkCheckBox(subgroup_corr_settings, text='Windowed cross-correlation', variable=val_checkbox_windowed_xcorr, command=on_windowed_xcorr_change)
checkbox_windowed_xcorr.grid(row=1, column=0, sticky="w", padx=10, pady=5)

# windowerd xcorr specialised settings
subgroup_windowed_xcorr_parameters = tk.CTkFrame(subgroup_corr_settings)
subgroup_windowed_xcorr_parameters.grid(row=2, sticky='ew', column=0, columnspan=2, padx=0, pady=0)
# subgroup content
label_subgroup_windowed_xcorr_parameters=tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Windowed cross-correlation parameters')
label_subgroup_windowed_xcorr_parameters.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky='w')
label_window_size = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Window Size')
label_window_size.grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_window_size = tk.CTkEntry(subgroup_windowed_xcorr_parameters, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_window_size_input, border_color='#777777')
entry_window_size.grid(row=1, column=1, sticky="w", padx=10, pady=5)
error_label_window_size = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Window Size must be in range [1, data_length]', text_color='red') # initially hidden
label_max_lag = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Max Lag')
label_max_lag.grid(row=3, column=0, sticky="w", padx=10, pady=5)
entry_max_lag = tk.CTkEntry(subgroup_windowed_xcorr_parameters, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_max_lag_input, border_color='#777777')
entry_max_lag.grid(row=3, column=1, sticky="w", padx=10, pady=5)
error_label_max_lag = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Max Lag must be in range [1, window_size//2]', text_color='red') # initially hidden
label_step_size = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Step Size')
label_step_size.grid(row=5, column=0, sticky="w", padx=10, pady=5)
entry_step_size = tk.CTkEntry(subgroup_windowed_xcorr_parameters, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_step_size_input, border_color='#777777')
entry_step_size.grid(row=5, column=1, sticky="w", padx=10, pady=5)
error_label_step_size = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='Step Size must be in range [1, window_size]', text_color='red') # initially hidden
checkbox_lag_filter = tk.CTkCheckBox(subgroup_windowed_xcorr_parameters, text='Filter Range of Lags', variable=val_checkbox_lag_filter)
checkbox_lag_filter.grid(row=9, column=0, sticky="w", padx=10, pady=5)
entry_lag_filter_min = tk.CTkEntry(subgroup_windowed_xcorr_parameters, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_lag_filter_min_input, border_color='#777777')
entry_lag_filter_max = tk.CTkEntry(subgroup_windowed_xcorr_parameters, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_lag_filter_max_input, border_color='#777777')
error_label_lag_filter = tk.CTkLabel(subgroup_windowed_xcorr_parameters, text='', text_color='red') # initially hidden
checkbox_absolute_corr = tk.CTkCheckBox(subgroup_windowed_xcorr_parameters, text='Absolute Correlation Values', variable=val_checkbox_absolute_corr, command=on_absolute_corr_change)
checkbox_absolute_corr.grid(row=15, column=0, sticky="w", padx=10, pady=5)
checkbox_average_windows = tk.CTkCheckBox(subgroup_windowed_xcorr_parameters, text='Average Values in Windows', variable=val_checkbox_average_windows, command=on_average_windows_change)
checkbox_average_windows.grid(row=16, column=0, sticky="w", padx=10, pady=5)
checkbox_show_sigmoid_correlations = tk.CTkCheckBox(subgroup_windowed_xcorr_parameters, text='Sigmoid-Scaled Correlation Values', variable=val_checkbox_show_sigmoid_correlations, command=on_show_sigmoid_correlations_change)
checkbox_show_sigmoid_correlations.grid(row=17, column=0, sticky="w", padx=10, pady=5)

# standard xcorr specialised settings (initially hidden)
subgroup_standard_xcorr_parameters = tk.CTkFrame(subgroup_corr_settings)
# subgroup content
label_subgroup_standard_xcorr_parameters=tk.CTkLabel(subgroup_standard_xcorr_parameters, text='Standard cross-correlation parameters')
label_subgroup_standard_xcorr_parameters.grid(row=0, column=0, sticky='ew', columnspan=2, padx=10, pady=5)
label_max_lag_sxc = tk.CTkLabel(subgroup_standard_xcorr_parameters, text='Max Lag')
label_max_lag_sxc.grid(row=1, column=0, sticky="w", padx=10, pady=5)
entry_max_lag_sxc = tk.CTkEntry(subgroup_standard_xcorr_parameters, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_max_lag_input_sxc, border_color='#777777')
entry_max_lag_sxc.grid(row=1, column=1, sticky="w", padx=10, pady=5)
error_label_max_lag_sxc = tk.CTkLabel(subgroup_standard_xcorr_parameters, text='Max Lag must be in range [0, data_length - 1]', text_color='red') # initially hidden
checkbox_absolute_corr_sxc = tk.CTkCheckBox(subgroup_standard_xcorr_parameters, text='Absolute Correlation Values', variable=val_checkbox_absolute_corr_sxc, command=on_absolute_corr_change_sxc)
checkbox_absolute_corr_sxc.grid(row=3, column=0, sticky="w", padx=10, pady=5)

# EXPORT & BATCH
# subgroup export
subgroup_export = tk.CTkFrame(tab_export_batch)
subgroup_export.grid(row=0, column=0, sticky='ew', columnspan=2, padx=0, pady=0)
label_corr_settings = tk.CTkLabel(subgroup_export, text="Export", font=("Arial", 20, "bold"))
label_corr_settings.grid(row=0, column=0, sticky='w', padx=10, columnspan=2, pady=10)
subsubgroup_export_buttons = tk.CTkFrame(subgroup_export)
subsubgroup_export_buttons.grid(row=1, column=0, columnspan=2, padx=0, pady=0)
# sub-subgroup buttons
button_export_data = tk.CTkButton(subsubgroup_export_buttons, text='Export XLSX', command=export_data)
button_export_data.grid(row=1, column=0, padx=10, pady=10)
button_export_plot = tk.CTkButton(subsubgroup_export_buttons, text='Export Plots', command=export_plot)
button_export_plot.grid(row=1, column=1, padx=10, pady=10)
# subgroup batch
subgroup_batch = tk.CTkFrame(tab_export_batch)
subgroup_batch.grid(row=1, column=0, sticky='ew', columnspan=2, padx=0, pady=0)
label_batch = tk.CTkLabel(subgroup_batch, text="Batch Processing", font=("Arial", 20, "bold"))
label_batch.grid(row=0, column=0, sticky='w', padx=10, columnspan=2, pady=10)
info_batch = tk.CTkLabel(subgroup_batch, text="Applies the same settings to multiple dyads.")
info_batch.grid(row=1, column=0, padx=10, sticky='w', columnspan=2)
button_batch_input_folder = tk.CTkButton(subgroup_batch, text='Select input folder', command=open_batch_input_folder)
button_batch_input_folder.grid(row=2, column=0, padx=10, pady=10, sticky='w')
label_batch_input_folder = tk.CTkLabel(subgroup_batch, text="No folder selected.")
label_batch_input_folder.grid(row=2, column=1, padx=10, sticky='w')
label_batch_input_num_subdirs = tk.CTkLabel(subgroup_batch, text="No folder selected.") # row=4, initially hidden
button_output_dir_picker = tk.CTkButton(subgroup_batch, text='Select output folder', command=open_batch_output_dir_picker)
button_output_dir_picker.grid(row=3, column=0, padx=10, pady=10, sticky='w')
label_output_dir = tk.CTkLabel(subgroup_batch, text="No folder selected.")
label_output_dir.grid(row=3, column=1, padx=10, sticky='w')
button_batch = tk.CTkButton(subgroup_batch, text='Run batch process', command=handle_run_batch_button, state="disabled") 
button_batch.grid(row=8, column=0, padx=10, pady=10, sticky='w')
#subgroup random pair
subgroup_random_pair = tk.CTkFrame(tab_export_batch)
subgroup_random_pair.grid(row=2, column=0, sticky='ew', columnspan=2, padx=0, pady=0)
label_random_pair = tk.CTkLabel(subgroup_random_pair, text="Random Pair Analysis", font=("Arial", 20, "bold"))
label_random_pair.grid(row=0, column=0, sticky='w', padx=10, columnspan=2, pady=10)
button_random_pair_input_folder = tk.CTkButton(subgroup_random_pair, text='Select input folder', command=open_random_pair_input_dir_picker)
button_random_pair_input_folder.grid(row=2, column=0, padx=10, pady=10, sticky='w')
label_random_pair_input_folder = tk.CTkLabel(subgroup_random_pair, text="No folder selected.")
label_random_pair_input_folder.grid(row=2, column=1, padx=10, sticky='w')
button_random_pair_output_file = tk.CTkButton(subgroup_random_pair, text='Select output file', command=open_random_pair_output_file_picker)
button_random_pair_output_file.grid(row=3, column=0, padx=10, pady=10, sticky='w')
label_random_pair_output_file = tk.CTkLabel(subgroup_random_pair, text="No file selected.")
label_random_pair_output_file.grid(row=3, column=1, padx=10, sticky='w')
label_rp_n = tk.CTkLabel(subgroup_random_pair, text="N")
label_rp_n.grid(row=4, column=0, sticky="w", padx=10, pady=5)
entry_rp_n = tk.CTkEntry(subgroup_random_pair, validate="key", validatecommand=(validate_numeric_input, "%P"), textvariable=val_rp_n_input, border_color='#777777')
entry_rp_n.grid(row=4, column=1, sticky="w", padx=10, pady=5)
button_random_pair = tk.CTkButton(subgroup_random_pair, text='Run rp analysis', command=handle_run_random_pair_button, state="disabled") 
button_random_pair.grid(row=8, column=0, padx=10, pady=10, sticky='w')





# ---------------------
# PARAMETER GUI UPDATES
# ---------------------
# input data section labels
# directory picker
def update_dir_picker_label(*args):
    dir_path = val_selected_dyad_dir.get()
    # label_dir_picker.configure(text='No folder selected.' if dir_path == '' else f"Selected: {os.path.basename(dir_path)} [{os.path.basename(val_selected_file_a.get())}, {os.path.basename(val_selected_file_b.get())}]")
    label_dir_picker.configure(text='No folder selected.' if dir_path == '' else f"Selected: {os.path.basename(dir_path)}")
val_selected_dyad_dir.trace_add('write', update_dir_picker_label)
val_selected_file_a.trace_add('write', update_dir_picker_label)
val_selected_file_b.trace_add('write', update_dir_picker_label)

# column selector dropdowns
def update_select_column_a_label(*args):
    label_select_column_a.configure(text="Select Column" if not val_selected_file_a.get() else f"Select Column for {os.path.basename(val_selected_file_a.get())}")
val_selected_file_a.trace_add('write', update_select_column_a_label)
def update_select_column_b_label(*args):
    label_select_column_b.configure(text="Select Column" if not val_selected_file_b.get() else f"Select Column for {os.path.basename(val_selected_file_b.get())}")
val_selected_file_b.trace_add('write', update_select_column_b_label)

# input data validation error message
def update_input_data_validation_error(*args):
    input_data_is_valid = (val_selected_sheet.get() == '- None -') or val_INPUT_DATA_VALID.get()
    if input_data_is_valid:
        error_label_input_data.grid_forget()
    else:
        error_label_input_data.grid(row=10, column=0, columnspan=2, sticky="w", padx=10, pady=0)
val_selected_sheet.trace_add('write', update_input_data_validation_error)
val_INPUT_DATA_VALID.trace_add('write', update_input_data_validation_error)

# windowed xcorr: win size entry
def update_window_size_entry_on_validation(*args):
    win_size_is_valid = val_WINDOW_SIZE_VALID.get()
    if win_size_is_valid:
        entry_window_size.configure(border_color='#777777')
        error_label_window_size.grid_forget()
    else:  
        entry_window_size.configure(border_color='red')  
        error_label_window_size.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=0)
val_WINDOW_SIZE_VALID.trace_add('write', update_window_size_entry_on_validation)

# windowed xcorr: max lag entry
def update_max_lag_entry_on_validation(*args):
    max_lag_is_valid = val_MAX_LAG_VALID.get()
    if max_lag_is_valid:
        entry_max_lag.configure(border_color='#777777')
        error_label_max_lag.grid_forget()
    else:  
        entry_max_lag.configure(border_color='red')  
        error_label_max_lag.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=0)
val_MAX_LAG_VALID.trace_add('write', update_max_lag_entry_on_validation)

# windowed xcorr: step size entry
def update_step_size_entry_on_validation(*args):
    step_size_is_valid = val_STEP_SIZE_VALID.get()
    if step_size_is_valid:
        entry_step_size.configure(border_color='#777777')
        error_label_step_size.grid_forget()
    else:  
        entry_step_size.configure(border_color='red')  
        error_label_step_size.grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=0)
val_STEP_SIZE_VALID.trace_add('write', update_step_size_entry_on_validation)

# lag filter min/max - hide/show based on checkbox
def update_lag_filter_visibility(*args):
    if val_checkbox_lag_filter.get():
        entry_lag_filter_min.grid(row=10, column=0, sticky="w", padx=10, pady=5)
        entry_lag_filter_max.grid(row=10, column=1, sticky="w", padx=10, pady=5)
    else:
        entry_lag_filter_min.grid_forget()
        entry_lag_filter_max.grid_forget()
        error_label_lag_filter.grid_forget()
val_checkbox_lag_filter.trace_add('write', update_lag_filter_visibility)

# lag filter errors
def update_lag_filter_entries_on_validation(*args):
    if val_LAG_FILTER_VALID.get():
        # hide error messages and remove red color if valid
        entry_lag_filter_min.configure(border_color='#777777')
        entry_lag_filter_max.configure(border_color='#777777')
        error_label_lag_filter.grid_forget()
        return
    # show error message and red borders if unsorted or out of range
    entry_lag_filter_min.configure(border_color='#777777')
    entry_lag_filter_max.configure(border_color='#777777')
    lf_sorted = check_lag_filter_sorted()
    lf_in_range = check_lag_filter_in_range()
    if not lf_sorted or not lf_in_range:
        msg = f"Filter limits must be {'sorted' if not lf_sorted else ''}{' and ' if not lf_sorted and not lf_in_range else ''} {'in [-max_lag, max_lag]' if not lf_in_range else ''}"
        error_label_lag_filter.configure(text=msg, text_color='red')
        error_label_lag_filter.grid(row=11, column=0, sticky="w", padx=10, pady=5)
val_LAG_FILTER_VALID.trace_add('write', update_lag_filter_entries_on_validation)
    

# standard xcorr entries
def update_max_lag_entry_on_validation_sxc(*args):
    max_lag_is_valid = val_MAX_LAG_VALID_SXC.get()
    if max_lag_is_valid:
        entry_max_lag_sxc.configure(border_color='#777777')
        error_label_max_lag_sxc.grid_forget()
    else:  
        entry_max_lag_sxc.configure(border_color='red')  
        error_label_max_lag_sxc.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=0)
val_MAX_LAG_VALID_SXC.trace_add('write', update_max_lag_entry_on_validation_sxc)

# export buttons
def update_active_state_export_button(*args):
    button_export_data.configure(state="normal" if val_CORRELATION_SETTINGS_VALID.get() else "disabled")
    button_export_plot.configure(state="normal" if val_CORRELATION_SETTINGS_VALID.get() else "disabled")
val_CORRELATION_SETTINGS_VALID.trace_add('write', update_active_state_export_button)

# toggle parameter xroups (wxc/sxc)
def update_xcorr_parameter_groups(*args):
    wxc_is_active = val_checkbox_windowed_xcorr.get()
    if wxc_is_active:
        subgroup_windowed_xcorr_parameters.grid(row=2, column=0, sticky='ew', columnspan=2, padx=0, pady=0)
        subgroup_standard_xcorr_parameters.grid_forget()
    else:
        subgroup_windowed_xcorr_parameters.grid_forget()
        subgroup_standard_xcorr_parameters.grid(row=2, column=0, sticky='ew', columnspan=2, padx=0, pady=0)
val_checkbox_windowed_xcorr.trace_add('write', update_xcorr_parameter_groups)


# batch file pickers: dynamic labels
val_batch_input_folder.trace_add('write', lambda *args: label_batch_input_folder.configure(text=f"Selected: {os.path.basename(val_batch_input_folder.get())}"))
val_batch_output_folder.trace_add('write', lambda *args: label_output_dir.configure(text=f"Selected: {os.path.basename(val_batch_output_folder.get())}"))

def update_batch_input_num_subdirs(*args):
    input_folder = val_batch_input_folder.get()
    if input_folder:
        label_batch_input_num_subdirs.configure(text=f"{utils.count_subdirectories(input_folder)} sub-folders / dyads")
        label_batch_input_num_subdirs.grid(row=4, column=0, padx=10, sticky='w')
    else:
        label_batch_input_num_subdirs.grid_forget()

val_batch_input_folder.trace_add('write', update_batch_input_num_subdirs)

# batch: dynamic button state 
def update_active_state_run_batch_button(*args):
    button_batch.configure(state="normal" if val_batch_processing_is_ready.get() else "disabled")
val_batch_processing_is_ready.trace_add('write', update_active_state_run_batch_button)

# random pair analysis: input chenge
val_rp_n_input.trace_add("write", on_rp_n_input_change)

# random pair file pickers: dynamic labels
val_random_pair_input_folder.trace_add('write', lambda *args: label_random_pair_input_folder.configure(text=f"Selected: {os.path.basename(val_random_pair_input_folder.get())}" if val_random_pair_input_folder.get() else "No folder selected."))
val_random_pair_output_file.trace_add('write', lambda *args: label_random_pair_output_file.configure(text=f"Selected: {os.path.basename(val_random_pair_output_file.get())}" if val_random_pair_output_file.get() else "No file selected."))

# random pair: dynamic button state 
def update_active_state_random_pair_button(*args):
    button_random_pair.configure(state="normal" if val_random_pair_is_ready.get() else "disabled")
val_random_pair_is_ready.trace_add('write', update_active_state_random_pair_button)

# -------------------------
# CORRELATION DATA HANDLING
# -------------------------
# update windowed xcorr data
def _update_wxcorr_data():
    if not val_INPUT_DATA_VALID.get() or not val_CORRELATION_SETTINGS_VALID.get():
        return
    # read data from data containers and state variables
    signal_a = dat_physiological_data["signal_a"]
    signal_b = dat_physiological_data["signal_b"]
    signal_a_std = dat_physiological_data["signal_a_std"]
    signal_b_std = dat_physiological_data["signal_b_std"]
    use_standardised_signals = val_checkbox_standardise.get()
    window_size = val_window_size.get()
    step_size = val_step_size.get()
    max_lag = val_max_lag.get()
    absolute_values = val_checkbox_absolute_corr.get()
    average_windows = val_checkbox_average_windows.get()
    use_lag_filter = val_checkbox_lag_filter.get()
    lag_filter_min = val_lag_filter_min.get()
    lag_filter_max = val_lag_filter_max.get()

    # update correlation data
    dat_correlation_data['wxcorr'] = windowed_cross_correlation(
        signal_a_std if use_standardised_signals else signal_a, 
        signal_b_std if use_standardised_signals else signal_b, 
        window_size=window_size, 
        step_size=step_size, 
        max_lag=max_lag, 
        absolute=absolute_values, 
        average_windows=average_windows,
        use_lag_filter=use_lag_filter,
        lag_filter_min=lag_filter_min,
        lag_filter_max=lag_filter_max
    )

    # update lagged dfa data
    try:
        dfa_data = dfa_wxcorr(dat_correlation_data['wxcorr'], max_lag, order=1)
        dfa_alpha_per_lag = [{'lag': o['lag'], 'alpha': o['A'][0]} for o in dfa_data]
        dat_correlation_data['dfa_alpha_per_lag_wxcorr'] = dfa_alpha_per_lag
    except ValueError as e:
        dat_correlation_data['dfa_alpha_per_lag_wxcorr'] = None
        print("TODO: handle dfa update error in wxcorr update", e) # TODO

    # update dfa of window averages
    try:
        dfa_alpha_per_window = dfa_wxcorr_window_averages(dat_correlation_data['wxcorr'], max_lag, order=1)
        dat_correlation_data['dfa_alpha_window_averages_wxcorr'] = dfa_alpha_per_window
    except ValueError as e:
        dat_correlation_data['dfa_alpha_window_averages_wxcorr'] = None

# uodate standard xcorr data
def _update_sxcorr_data():
    if not val_INPUT_DATA_VALID.get() or not val_CORRELATION_SETTINGS_VALID_SXC.get():
        return

    # read data from data containers and state variabled
    use_standardised_signals = val_checkbox_standardise.get()
    signal_a = dat_physiological_data["signal_a_std"] if use_standardised_signals else dat_physiological_data["signal_a"]
    signal_b = dat_physiological_data["signal_b_std"] if use_standardised_signals else dat_physiological_data["signal_b"]
    max_lag = val_max_lag_sxc.get()
    absolute_values = val_checkbox_absolute_corr_sxc.get()
    dat_correlation_data['sxcorr'] = standard_cross_correlation(signal_a, signal_b, max_lag=max_lag, absolute=absolute_values)

    # calculate dfa
    A, F = dfa(dat_correlation_data['sxcorr']['corr'], order=1)
    dat_correlation_data['dfa_alpha_sxcorr'] = A[0]

# update correlation data
def update_corr():
    is_windowed_xcorr = val_checkbox_windowed_xcorr.get()
    if is_windowed_xcorr:
        _update_wxcorr_data()
    else:
        _update_sxcorr_data()
    
def clear_correlation_data():
    dat_correlation_data["wxcorr"] = []
    dat_correlation_data["sxcorr"] = []

# --------
# PLOTTING
# --------

canvas = FigureCanvasTkAgg(dat_plot_data["fig"], master=group_plot)
def update_canvas():
    if not dat_plot_data["fig"]: return
    canvas.figure = dat_plot_data["fig"]
    canvas.draw()
    canvas.get_tk_widget().pack()

def update_plot(*args):
    # figure out which plot to show next
    plot_type = None
    current_tab = val_CURRENT_TAB.get()
    if current_tab == "Input Data":
        plot_type = "preprocess_preview"
    else: 
        is_windowed_xcorr = val_checkbox_windowed_xcorr.get()
        plot_type = "windowed_xcorr" if is_windowed_xcorr else "standard_xcorr"
    
    # select data based on standardisation selection
    use_standardised = val_checkbox_standardise.get()
    signal_a = dat_physiological_data['signal_a_std'] if use_standardised else dat_physiological_data['signal_a']
    signal_b = dat_physiological_data['signal_b_std'] if use_standardised else dat_physiological_data['signal_b']

    # update preprocessing preview
    if plot_type == "preprocess_preview":
        # reset plot if data is invalid
        if not val_INPUT_DATA_VALID.get(): 
            dat_plot_data["fig"] = plot_init(dpi=screen_dpi, screen_width=screen_width, screen_height=screen_height, is_retina=RETINA)
            return
        # plot data
        dat_plot_data["fig"] = update_preproc_plots({
            'signal_a': signal_a,
            'signal_b': signal_b,
            'dyad_folder': os.path.basename(val_selected_dyad_dir.get()),
            'selected_sheet': val_selected_sheet.get(),
            'filename_a': os.path.basename(val_selected_file_a.get()),
            'filename_b': os.path.basename(val_selected_file_b.get()),
            'column_a': val_selected_column_a.get(),
            'column_b': val_selected_column_b.get(),
            'is_resampled': val_checkbox_eb.get()
        })
        return
    
    # update windowed xcorr plot
    if plot_type == "windowed_xcorr":
        if not val_CORRELATION_SETTINGS_VALID.get() or not dat_correlation_data['wxcorr']: return
        dat_plot_data["fig"] = update_wxcorr_plots({
            'signal_a': signal_a,
            'signal_b': signal_b,
            'window_size': val_window_size.get(),
            'step_size': val_step_size.get(),
            'max_lag': val_max_lag.get(),
            'use_lag_filter': checkbox_lag_filter.get(),
            'lag_filter_min': val_lag_filter_min.get(),
            'lag_filter_max': val_lag_filter_max.get(),
            'windowed_xcorr_data': dat_correlation_data["wxcorr"],
            'show_sigmoid_correlations': val_checkbox_show_sigmoid_correlations.get()
        })
        return

    # update standard xcorr plot
    if plot_type == "standard_xcorr":
        if not val_CORRELATION_SETTINGS_VALID_SXC.get() or not dat_correlation_data['sxcorr']: return
        dat_plot_data["fig"] = update_sxcorr_plots({
            'signal_a': signal_a,
            'signal_b': signal_b,
            'xcorr_data': dat_correlation_data['sxcorr'],
        })
        return
    
    # don't update
    print("! warning: no plot type selected in update_plot")

# -----------
# UPDATE LOOP
# -----------

def UPDATE(*args):
    update_corr()
    update_plot()
    update_canvas()
val_UPDATE_COUNT.trace_add('write', UPDATE)
UPDATE()

# ---
# CLEANUP & SHUTDOWN
# ---

def on_window_closing():
    """Properly clean up before closing the app"""
    # Cancel all pending after callbacks
    for widget_id in list(app.after_info()):
        try:
            app.after_cancel(widget_id)
        except:
            pass
    
    # Close matplotlib figures
    try:
        import matplotlib.pyplot as plt
        plt.close('all')
    except:
        pass
    
    # Destroy the window
    app.destroy()

# Set the window close handler (Windows-specific behavior)
app.protocol("WM_DELETE_WINDOW", on_window_closing)

# ---
# RUN
# ---
app.mainloop()